#!/usr/bin/env python3
"""Response-independent spatial preflight for bare-bed canopy controls.

Uses:
- pinned 2023-2025 TBISMP Event/Occurrence state only for field-sampling feasibility;
- the directly downloadable FWC/FWRI Seagrass Florida polygon archive;
- no future biological response.

FWC metadata documents SWFWMD Seagrass in 2024 as the current southwest-Florida
source within the statewide compilation. This script is a spatial feasibility
audit only, not a Tampa seagrass time-series analysis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

import geopandas as gpd
import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, box
from shapely.ops import unary_union

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
    "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
    "occurrence":{"url":f"{BASE}/occurrence.csv","size":12508487,"blob":"d34aeb5aedb72459d1e04059629cb09450df929e"},
}
CORE=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
YEARS=(2023,2024,2025)
THALASSIA="Thalassia testudinum"
ORDER="Alismatales"

FWC_ZIP_URL="https://atoll.floridamarine.org/Data/Zips/SDE/seagrass_fl_poly.zip"
EDGE_MAX_M=100.0
TARGET=18
MINIMUM=12
MIN_PER_BAY=3

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def get_bytes(url:str,timeout:int=300)->bytes:
    req=Request(url,headers={
        "Accept-Encoding":"identity",
        "User-Agent":"Tampa-bare-control-preflight/1.1",
    })
    with urlopen(req,timeout=timeout) as r:
        return r.read()

def fetch(spec):
    data=get_bytes(spec["url"],180)
    if len(data)!=spec["size"]:
        raise RuntimeError(f"source size drift {len(data)} != {spec['size']}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError("source blob drift")
    return data

def reconstruct_recent_nodes(event:bytes,occ:bytes):
    rd=csv.DictReader(io.StringIO(event.decode("utf-8"),newline=""))
    parents={}; children=defaultdict(list)
    for row in rd:
        typ=row["eventType"].strip()
        if typ=="Transect":
            year=int(row["year"] or row["eventDate"][:4])
            wb=row["waterBody"].strip()
            if year in YEARS and wb in CORE:
                parents[row["eventID"].strip()]={
                    "node_id":row["locationID"].strip(),
                    "year":year,
                    "water_body":wb,
                    "longitude":float(row["decimalLongitude"]),
                    "latitude":float(row["decimalLatitude"]),
                }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            if pid in parents:
                children[pid].append(row["eventID"].strip())

    eligible={p for p in parents if len(children.get(p,[]))>=3}
    point_to_parent={eid:p for p in eligible for eid in children[p]}

    state=defaultdict(lambda:{"thalassia":False,"species":set()})
    rd=csv.DictReader(io.StringIO(occ.decode("utf-8"),newline=""))
    for row in rd:
        eid=row["eventID"].strip()
        if eid not in point_to_parent:
            continue
        if row["occurrenceStatus"].strip()!="present" or row["order"].strip()!=ORDER:
            continue
        sci=row["scientificName"].strip()
        if not sci:
            continue
        state[eid]["species"].add(sci)
        if sci==THALASSIA:
            state[eid]["thalassia"]=True

    visit=[]
    for pid in eligible:
        p=parents[pid]; eids=children[pid]; n=len(eids)
        th=sum(bool(state.get(eid) and state[eid]["thalassia"]) for eid in eids)
        anysg=sum(bool(state.get(eid) and state[eid]["species"]) for eid in eids)
        visit.append({**p,"tf":th/n,"af":anysg/n})

    ny=defaultdict(lambda:{"n":0,"tf":0.0,"af":0.0,"meta":None})
    for v in visit:
        k=(v["node_id"],v["year"])
        x=ny[k]
        x["n"]+=1; x["tf"]+=v["tf"]; x["af"]+=v["af"]; x["meta"]=v

    latest={}
    for (node,year),x in ny.items():
        m=x["meta"]
        a={
            "node_id":node,
            "year":year,
            "water_body":m["water_body"],
            "longitude":m["longitude"],
            "latitude":m["latitude"],
            "thalassia_frequency":x["tf"]/x["n"],
            "any_seagrass_frequency":x["af"]/x["n"],
        }
        if node not in latest or year>latest[node]["year"]:
            latest[node]=a

    out=sorted(latest.values(),key=lambda z:(z["water_body"],z["node_id"]))
    if len(out)!=40:
        raise RuntimeError(f"recent node registry drift: {len(out)} != 40")
    if sum(x["any_seagrass_frequency"]>0 for x in out)!=40:
        raise RuntimeError("recent vegetated-node registry drift")
    if sum(x["thalassia_frequency"]>0 for x in out)!=33:
        raise RuntimeError("recent Thalassia-positive registry drift")
    return out

def fetch_fwc_seagrass_union(outdir:Path,nodes):
    raw=get_bytes(FWC_ZIP_URL,300)
    archive=outdir/"seagrass_fl_poly.zip"
    archive.write_bytes(raw)

    extract=outdir/"seagrass_fwc"
    extract.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        z.extractall(extract)

    shp=sorted(extract.rglob("*.shp"))
    if not shp:
        raise RuntimeError("FWC archive contained no shapefile")

    gdf=gpd.read_file(shp[0])
    if gdf.crs is None:
        raise RuntimeError("FWC seagrass shapefile has no CRS")
    source_crs=str(gdf.crs)
    source_columns=[str(x) for x in gdf.columns if x!="geometry"]

    gdf=gdf.to_crs("EPSG:26917")
    tr=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True)
    xy=[tr.transform(n["longitude"],n["latitude"]) for n in nodes]

    # Three-km buffer only reduces the statewide file to the Tampa analysis region.
    # It does not alter the frozen 100-m bare-control candidate threshold.
    local_box=box(
        min(x for x,y in xy)-3000,
        min(y for x,y in xy)-3000,
        max(x for x,y in xy)+3000,
        max(y for x,y in xy)+3000,
    )
    local=gdf[gdf.geometry.intersects(local_box)].copy()
    local=local[local.geometry.notna() & ~local.geometry.is_empty].copy()
    if local.empty:
        raise RuntimeError("FWC archive has no seagrass polygons near Tampa nodes")

    # Repair only invalid topology before unioning.
    bad=~local.geometry.is_valid
    if bad.any():
        local.loc[bad,"geometry"]=local.loc[bad,"geometry"].buffer(0)
    local=local[local.geometry.notna() & ~local.geometry.is_empty].copy()

    union=unary_union(list(local.geometry))
    audit={
        "archive_bytes":len(raw),
        "archive_sha256":hashlib.sha256(raw).hexdigest(),
        "source_features_total":int(len(gdf)),
        "tampa_nearby_features":int(len(local)),
        "source_columns":source_columns,
        "source_crs":source_crs,
        "working_crs":"EPSG:26917",
    }

    archive.unlink(missing_ok=True)
    return union,audit

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    nodes=reconstruct_recent_nodes(fetch(FILES["event"]),fetch(FILES["occurrence"]))
    union,source_audit=fetch_fwc_seagrass_union(outdir,nodes)

    transformer=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True)
    boundary=union.boundary

    rows=[]
    for n in nodes:
        p=Point(*transformer.transform(n["longitude"],n["latitude"]))
        inside=bool(union.covers(p))
        if inside:
            edge=float(p.distance(boundary))
            nearest_seagrass=0.0
        else:
            edge=None
            nearest_seagrass=float(p.distance(union))
        candidate=bool(inside and edge is not None and edge<=EDGE_MAX_M)
        rows.append({
            **n,
            "inside_current_mapped_seagrass":inside,
            "edge_distance_m":edge,
            "nearest_mapped_seagrass_distance_m":nearest_seagrass,
            "bare_edge_candidate_100m":candidate,
            "primary_thalassia_positive":bool(n["thalassia_frequency"]>0),
        })

    by={}
    for wb in CORE:
        d=[x for x in rows if x["water_body"]==wb]
        cand=[x for x in d if x["bare_edge_candidate_100m"]]
        cand_primary=[x for x in cand if x["primary_thalassia_positive"]]
        by[wb]={
            "recent_vegetated_nodes":len(d),
            "inside_current_mapped_seagrass":sum(x["inside_current_mapped_seagrass"] for x in d),
            "bare_edge_candidates_100m":len(cand),
            "thalassia_positive_bare_edge_candidates_100m":len(cand_primary),
            "map_state_mismatches":sum(not x["inside_current_mapped_seagrass"] for x in d),
        }

    total=sum(x["bare_edge_candidate_100m"] for x in rows)
    minbay=min(by[wb]["bare_edge_candidates_100m"] for wb in CORE)
    passed=bool(total>=MINIMUM and minbay>=MIN_PER_BAY)
    edgevals=[x["edge_distance_m"] for x in rows if x["edge_distance_m"] is not None]

    result={
        "schema":"tampa.bare_control_spatial_preflight_v1",
        "status":"geographic_edge_feasibility_pass" if passed else "geographic_edge_feasibility_not_supported",
        "response_independent":True,
        "source":{
            "tbismp_commit":COMMIT,
            "recent_years":list(YEARS),
            "seagrass_source":"FWC/FWRI Seagrass Florida current statewide compilation",
            "seagrass_archive":FWC_ZIP_URL,
            "tampa_component_provenance":"SWFWMD Seagrass in 2024 per FWC metadata",
            "archive_audit":source_audit,
        },
        "registry":{
            "recent_vegetated_nodes":len(rows),
            "recent_thalassia_positive_nodes":sum(x["primary_thalassia_positive"] for x in rows),
            "inside_current_mapped_seagrass_nodes":sum(x["inside_current_mapped_seagrass"] for x in rows),
            "map_state_mismatches":sum(not x["inside_current_mapped_seagrass"] for x in rows),
        },
        "edge_distance_m":{
            "n_inside":len(edgevals),
            "median":float(np.median(edgevals)) if edgevals else None,
            "p25":float(np.quantile(edgevals,0.25)) if edgevals else None,
            "p75":float(np.quantile(edgevals,0.75)) if edgevals else None,
            "max":float(np.max(edgevals)) if edgevals else None,
        },
        "candidate_gate":{
            "maximum_edge_distance_m":EDGE_MAX_M,
            "target_nodes":TARGET,
            "minimum_nodes":MINIMUM,
            "minimum_nodes_per_bay":MIN_PER_BAY,
            "candidate_nodes":int(total),
            "minimum_candidates_in_any_bay":int(minbay),
            "by_water_body":by,
            "passed":passed,
        },
        "nodes":rows,
        "claim_boundary":[
            "A mapped meadow edge within 100 m is only a geographic reconnaissance candidate, not a validated bare control.",
            "Field validation must still satisfy frozen separation, depth matching, comparable forcing, substrate/context and simultaneous sensor geometry.",
            "The source mapping can omit small bare gaps inside patchy beds; a negative GIS gate is conservative.",
            "Do not relax the 100-m threshold after inspection to create a pass.",
            "The FWC compilation is used for spatial feasibility, not Tampa time-series inference.",
            "No future biological response is used.",
        ],
    }

    (outdir/"bare_control_spatial_preflight_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    with (outdir/"bare_control_spatial_candidates_v1.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    print(json.dumps({
        "status":result["status"],
        "registry":result["registry"],
        "edge_distance_m":result["edge_distance_m"],
        "candidate_gate":result["candidate_gate"],
    },indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_bare_control_preflight"))
    a=ap.parse_args()
    main(a.out)
