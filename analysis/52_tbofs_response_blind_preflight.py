#!/usr/bin/env python3
"""Response-blind TBOFS grid/depth preflight for Tampa stable transects.

This script is intentionally forbidden from reading any Tampa biological response.
It reconstructs only node_id, water_body, longitude and latitude from the pinned
Darwin Core Event table, then asks whether a fixed NOAA TBOFS 3-D field supplies
a reproducible near-bed current grid close enough to the 71 stable nodes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import xarray as xr

SOURCE_COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
EVENT_URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{SOURCE_COMMIT}/dwc/event.csv"
EVENT_SIZE=24654717
EVENT_BLOB="583b4d4e328290ab065346579eb4f29f03ea0f99"

# Fixed before inspecting any hydrodynamic/seagrass association.
TBOFS_URL=(
    "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nosofs/prod/"
    "tbofs.20260928/tbofs.t00z.20260928.fields.f001.nc"
)
TBOFS_SAMPLE_DATE="2026-09-28"
TBOFS_CYCLE="t00z"
TBOFS_LEAD="f001"

ALLOWED_NODE_COLUMNS=("node_id","water_body","longitude","latitude")
PROHIBITED_BIOLOGICAL_TERMS=(
    "detected","focal_frequency","bb_cover","blade","shoot_density",
    "loss","re_record","reappear","recovery"
)

GATE={
    "minimum_valid_nodes":30,
    "required_water_bodies":["Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay"],
    "maximum_median_mapping_distance_km":1.0,
    "maximum_primary_node_mapping_distance_km":2.0,
}

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def download(url:str, timeout:int=180)->bytes:
    req=Request(url,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-TBOFS-preflight/1.0"})
    with urlopen(req,timeout=timeout) as resp:
        return resp.read()

def reconstruct_nodes(event_bytes:bytes):
    if len(event_bytes)!=EVENT_SIZE:
        raise RuntimeError(f"event size drift: {len(event_bytes)} != {EVENT_SIZE}")
    if git_blob_sha1(event_bytes)!=EVENT_BLOB:
        raise RuntimeError("event git-blob identity drift")
    reader=csv.DictReader(io.StringIO(event_bytes.decode("utf-8"),newline=""))
    parents={}
    child_count=defaultdict(int)
    for row in reader:
        typ=row["eventType"].strip()
        if typ=="Transect":
            parents[row["eventID"].strip()]={
                "node_id":row["locationID"].strip(),
                "water_body":row["waterBody"].strip(),
                "longitude":float(row["decimalLongitude"]),
                "latitude":float(row["decimalLatitude"]),
            }
        elif typ=="Point":
            child_count[row["parentEventID"].strip()]+=1
    nodes={}
    for eid,p in parents.items():
        if child_count.get(eid,0)<3:
            continue
        nid=p["node_id"]
        if nid in nodes:
            old=nodes[nid]
            # Coordinates should be effectively stable; retain first exactly as annual reconstruction does.
            if old["water_body"]!=p["water_body"]:
                raise RuntimeError(f"water-body drift within node {nid}")
        else:
            nodes[nid]=p
    out=sorted(nodes.values(),key=lambda x:x["node_id"])
    if len(out)!=71:
        raise RuntimeError(f"stable-node registry drift: {len(out)} != 71")
    if set(out[0])!=set(ALLOWED_NODE_COLUMNS):
        raise RuntimeError("response-blind node schema drift")
    return out

def pick_name(ds, choices):
    for x in choices:
        if x in ds.variables:
            return x
    return None

def haversine_grid_km(lat0,lon0,lat,lon):
    r=6371.0088
    p0=np.deg2rad(lat0); p=np.deg2rad(lat)
    dp=p-p0; dl=np.deg2rad(lon-lon0)
    a=np.sin(dp/2.0)**2 + np.cos(p0)*np.cos(p)*np.sin(dl/2.0)**2
    return 2*r*np.arcsin(np.sqrt(np.clip(a,0,1)))

def finite_nearbed_support(ds,u_name,v_name,s_dim,nearbed_index,shape):
    """Return a conservative rho-grid mask supported by adjacent finite u and v."""
    u=ds[u_name]
    v=ds[v_name]
    usel={s_dim:nearbed_index}
    vsel={s_dim:nearbed_index}
    # Select first time-like dimension only for a source-usability audit.
    for d in u.dims:
        if d not in usel and d not in ("eta_u","xi_u") and u.sizes[d]==1:
            usel[d]=0
    for d in v.dims:
        if d not in vsel and d not in ("eta_v","xi_v") and v.sizes[d]==1:
            vsel[d]=0
    ua=np.asarray(u.isel(**usel).values)
    va=np.asarray(v.isel(**vsel).values)
    ua=np.squeeze(ua); va=np.squeeze(va)
    if ua.ndim!=2 or va.ndim!=2:
        raise RuntimeError(f"unexpected u/v dimensionality after slicing: {ua.shape}, {va.shape}")

    ny,nx=shape
    us=np.isfinite(ua) & (np.abs(ua)<1e20)
    vs=np.isfinite(va) & (np.abs(va)<1e20)
    rho_u=np.zeros((ny,nx),dtype=bool)
    rho_v=np.zeros((ny,nx),dtype=bool)

    # ROMS u is staggered in xi; v in eta.
    if us.shape==(ny,nx-1):
        rho_u[:,0] |= us[:,0]
        rho_u[:,-1] |= us[:,-1]
        if nx>2:
            rho_u[:,1:-1] |= us[:,:-1] | us[:,1:]
    else:
        raise RuntimeError(f"u grid {us.shape} incompatible with rho grid {shape}")

    if vs.shape==(ny-1,nx):
        rho_v[0,:] |= vs[0,:]
        rho_v[-1,:] |= vs[-1,:]
        if ny>2:
            rho_v[1:-1,:] |= vs[:-1,:] | vs[1:,:]
    else:
        raise RuntimeError(f"v grid {vs.shape} incompatible with rho grid {shape}")
    return rho_u & rho_v

def inspect_and_map(nc_path:Path,nodes):
    with xr.open_dataset(nc_path,decode_times=False,mask_and_scale=True) as ds:
        lon_name=pick_name(ds,["lon_rho","longitude","Longitude"])
        lat_name=pick_name(ds,["lat_rho","latitude","Latitude"])
        mask_name=pick_name(ds,["mask_rho","mask"])
        s_name=pick_name(ds,["s_rho","Depth","depth"])
        u_name=pick_name(ds,["u","u_eastward"])
        v_name=pick_name(ds,["v","v_northward"])
        h_name=pick_name(ds,["h","depth","Depth"])

        required={"lon":lon_name,"lat":lat_name,"vertical":s_name,"u":u_name,"v":v_name}
        if any(v is None for v in required.values()):
            raise RuntimeError(f"missing required TBOFS variables: {required}")

        lon=np.asarray(ds[lon_name].values)
        lat=np.asarray(ds[lat_name].values)
        if lon.ndim!=2 or lat.shape!=lon.shape:
            raise RuntimeError(f"unexpected coordinate shapes lon={lon.shape} lat={lat.shape}")
        ny,nx=lon.shape

        s=np.asarray(ds[s_name].values).reshape(-1)
        if s.size<2:
            raise RuntimeError("vertical coordinate has <2 levels")
        # ROMS sigma coordinate: most negative layer is closest to the bed.
        nearbed_index=int(np.nanargmin(s))
        nearbed_value=float(s[nearbed_index])
        surface_index=int(np.nanargmax(s))
        vertical_ok=bool(nearbed_value<0 and nearbed_value<float(s[surface_index]))

        support=finite_nearbed_support(ds,u_name,v_name,s_name,nearbed_index,(ny,nx))
        base=np.isfinite(lon)&np.isfinite(lat)&support
        if mask_name:
            mask=np.asarray(ds[mask_name].values)
            mask=np.squeeze(mask)
            if mask.shape==base.shape:
                base &= np.isfinite(mask)&(mask>0)
        valid_count=int(base.sum())
        if valid_count==0:
            raise RuntimeError("no valid near-bed current-support rho cells")
        flat=np.flatnonzero(base)
        vlat=lat.ravel()[flat]
        vlon=lon.ravel()[flat]

        mapped=[]
        for node in nodes:
            d=haversine_grid_km(node["latitude"],node["longitude"],vlat,vlon)
            k=int(np.nanargmin(d))
            fi=int(flat[k])
            jj,ii=np.unravel_index(fi,(ny,nx))
            mapped.append({
                **node,
                "rho_j":int(jj),
                "rho_i":int(ii),
                "grid_longitude":float(lon[jj,ii]),
                "grid_latitude":float(lat[jj,ii]),
                "distance_km":float(d[k]),
            })

        dist=np.array([x["distance_km"] for x in mapped],dtype=float)
        by_water={}
        for wb in sorted({x["water_body"] for x in mapped}):
            dd=np.array([x["distance_km"] for x in mapped if x["water_body"]==wb])
            by_water[wb]={
                "nodes":int(dd.size),
                "median_distance_km":float(np.median(dd)),
                "max_distance_km":float(np.max(dd)),
                "within_2km":int((dd<=2.0).sum()),
            }

        meta={
            "dimensions":{k:int(v) for k,v in ds.sizes.items()},
            "variables":{
                "longitude":lon_name,
                "latitude":lat_name,
                "mask":mask_name,
                "vertical":s_name,
                "u":u_name,
                "v":v_name,
                "bathymetry":h_name,
            },
            "u_dims":list(ds[u_name].dims),
            "v_dims":list(ds[v_name].dims),
            "u_units":str(ds[u_name].attrs.get("units","")),
            "v_units":str(ds[v_name].attrs.get("units","")),
            "u_long_name":str(ds[u_name].attrs.get("long_name","")),
            "v_long_name":str(ds[v_name].attrs.get("long_name","")),
            "vertical_values":[float(x) for x in s.tolist()],
            "nearbed_index":nearbed_index,
            "nearbed_coordinate_value":nearbed_value,
            "surface_index":surface_index,
            "vertical_nearbed_interpretation_ok":vertical_ok,
            "rho_grid_shape":[ny,nx],
            "nearbed_current_supported_rho_cells":valid_count,
        }

    required_water_ok=all(any(x["water_body"]==wb for x in mapped) for wb in GATE["required_water_bodies"])
    gate_checks={
        "valid_nodes_gte_30":len(mapped)>=GATE["minimum_valid_nodes"],
        "required_water_bodies_present":required_water_ok,
        "median_distance_lte_1km":float(np.median(dist))<=GATE["maximum_median_mapping_distance_km"],
        "max_distance_lte_2km":float(np.max(dist))<=GATE["maximum_primary_node_mapping_distance_km"],
        "vertical_nearbed_interpretation":bool(meta["vertical_nearbed_interpretation_ok"]),
    }
    return {
        "schema":"tampa.tbofs_hydrodynamic_preflight_v1",
        "status":"source_gate_passed" if all(gate_checks.values()) else "source_gate_failed",
        "response_blind":True,
        "source":{
            "biological_registry_commit":SOURCE_COMMIT,
            "tbofs_url":TBOFS_URL,
            "tbofs_sample_date":TBOFS_SAMPLE_DATE,
            "tbofs_cycle":TBOFS_CYCLE,
            "tbofs_lead":TBOFS_LEAD,
        },
        "registry":{
            "stable_nodes":len(nodes),
            "by_water_body":dict(Counter(x["water_body"] for x in nodes)),
            "allowed_columns":list(ALLOWED_NODE_COLUMNS),
        },
        "tbofs":meta,
        "mapping":{
            "mapped_nodes":len(mapped),
            "median_distance_km":float(np.median(dist)),
            "p90_distance_km":float(np.quantile(dist,0.9)),
            "max_distance_km":float(np.max(dist)),
            "within_1km":int((dist<=1.0).sum()),
            "within_2km":int((dist<=2.0).sum()),
            "by_water_body":by_water,
            "nodes":mapped,
        },
        "gate":{
            "frozen_thresholds":GATE,
            "checks":gate_checks,
            "passed":bool(all(gate_checks.values())),
        },
        "claim_boundary":[
            "This audit uses node coordinates only and contains no Tampa biological response.",
            "Passing the source gate establishes physical-layer usability, not ecological mechanism support.",
            "No interpolation radius, vertical level, exposure percentile or biological model is tuned here."
        ],
    }

def main(outdir:Path,keep_nc:bool=False):
    outdir.mkdir(parents=True,exist_ok=True)
    event=download(EVENT_URL,timeout=180)
    nodes=reconstruct_nodes(event)
    nc_path=outdir/"tbofs_sample.nc"
    nc_path.write_bytes(download(TBOFS_URL,timeout=240))
    result=inspect_and_map(nc_path,nodes)
    (outdir/"tbofs_hydrodynamic_preflight_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    (outdir/"tbofs_nodes_response_blind.csv").write_text(
        "node_id,water_body,longitude,latitude\n"+
        "\n".join(f'{x["node_id"]},{x["water_body"]},{x["longitude"]},{x["latitude"]}' for x in nodes)+"\n"
    )
    if not keep_nc:
        nc_path.unlink(missing_ok=True)
    print(json.dumps({
        "status":result["status"],
        "stable_nodes":result["registry"]["stable_nodes"],
        "median_distance_km":result["mapping"]["median_distance_km"],
        "max_distance_km":result["mapping"]["max_distance_km"],
        "gate":result["gate"]["checks"],
    },indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_tbofs_preflight"))
    p.add_argument("--keep-nc",action="store_true")
    a=p.parse_args()
    main(a.out,a.keep_nc)
