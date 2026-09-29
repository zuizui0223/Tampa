#!/usr/bin/env python3
"""Response-independent spatial feasibility audit for matched bare-bed controls.

Important coordinate semantics
------------------------------
Darwin Core Point rows repeat the transect-start coordinate for every meter mark.
They are NOT literal meter-mark coordinates. The pinned Event locationRemarks
stores the signed transect bearing that obis-example derived from the original
TBEP transect LINESTRING. Meter-mark positions are therefore reconstructed as:

    pinned transect-start coordinate + signed bearing + meter-mark distance

This corrects the earlier start-point-only GIS audit without changing the frozen
scientific gate: <=100 m mapped meadow-edge distance, >=12 candidate nodes, and
>=3 candidates in each of Old/Middle/Lower Tampa Bay.

This is field-feasibility only. It opens no future biological response.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import geopandas as gpd
import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, box, shape
from shapely.ops import transform as shp_transform, unary_union

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
    "event":{
        "url":f"{BASE}/event.csv",
        "size":24654717,
        "blob":"583b4d4e328290ab065346579eb4f29f03ea0f99",
    },
    "occurrence":{
        "url":f"{BASE}/occurrence.csv",
        "size":12508487,
        "blob":"d34aeb5aedb72459d1e04059629cb09450df929e",
    },
}
CORE=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
YEARS=(2023,2024,2025)
THALASSIA="Thalassia testudinum"
ORDER="Alismatales"

# Primary public source may be inaccessible from CI; the USF mirror is accepted
# only if returned DATESTAMP values pass the frozen >=2024 validation gate.
SWFWMD_FEATURE_URL=(
    "https://www25.swfwmd.state.fl.us/arcgis12/rest/services/"
    "OpenData/Environmental_Seagrass2018_sql/FeatureServer/3"
)
USF_MIRROR_URL=(
    "https://gis.waterinstitute.usf.edu/arcgis/rest/services/"
    "Maps/Seagrass2024/MapServer/0"
)
FWC_ZIP_URL="https://atoll.floridamarine.org/Data/Zips/SDE/seagrass_fl_poly.zip"

EDGE_MAX_M=100.0
TARGET=18
MINIMUM=12
MIN_PER_BAY=3
EARTH_RADIUS_M=6371008.8
BEARING_RE=re.compile(r"bearing of\s+(-?\d+(?:\.\d+)?)\s+degrees",re.I)


def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def get_bytes(url:str,timeout:int=300)->bytes:
    req=Request(url,headers={
        "Accept-Encoding":"identity",
        "User-Agent":"Tampa-bare-control-meter-mark-preflight/2.0",
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


def parse_bearing(remark:str)->float:
    m=BEARING_RE.search(str(remark or ""))
    if not m:
        raise RuntimeError(f"bearing missing from locationRemarks: {remark!r}")
    b=float(m.group(1))
    if not (-180.0 <= b <= 180.0):
        raise RuntimeError(f"bearing outside pinned convention: {b}")
    return b


def parse_site_m(location_id:str)->float:
    s=str(location_id or "").rsplit(":",1)[-1].strip()
    try:
        x=float(s)
    except Exception as exc:
        raise RuntimeError(f"non-numeric meter-mark locationID {location_id!r}") from exc
    if not math.isfinite(x):
        raise RuntimeError(f"non-finite meter mark {x}")
    # The pinned source contains signed offsets (negative values lie on the
    # opposite side of mark 0) and transects extending beyond 1 km. Preserve
    # the observed signed meter-mark distance rather than clipping it.
    return x


def dest_point(lon_deg:float,lat_deg:float,bearing_deg:float,distance_m:float):
    """Spherical forward geodesic; sub-km Tampa use makes error negligible."""
    phi1=math.radians(lat_deg)
    lam1=math.radians(lon_deg)
    theta=math.radians(bearing_deg)
    delta=distance_m/EARTH_RADIUS_M
    sin_phi2=math.sin(phi1)*math.cos(delta)+math.cos(phi1)*math.sin(delta)*math.cos(theta)
    phi2=math.asin(max(-1.0,min(1.0,sin_phi2)))
    lam2=lam1+math.atan2(
        math.sin(theta)*math.sin(delta)*math.cos(phi1),
        math.cos(delta)-math.sin(phi1)*math.sin(phi2),
    )
    lon=((math.degrees(lam2)+540.0)%360.0)-180.0
    lat=math.degrees(phi2)
    return lon,lat


def reconstruct_recent_meter_marks(event:bytes,occ:bytes):
    er=csv.DictReader(io.StringIO(event.decode("utf-8"),newline=""))
    parents={}
    children=defaultdict(list)

    for row in er:
        typ=row["eventType"].strip()
        if typ=="Transect":
            year=int(row["year"] or row["eventDate"][:4])
            wb=row["waterBody"].strip()
            if year not in YEARS or wb not in CORE:
                continue
            eid=row["eventID"].strip()
            parents[eid]={
                "event_id":eid,
                "node_id":row["locationID"].strip(),
                "node_short":row["locationID"].strip().rsplit(":",1)[-1],
                "year":year,
                "date":row["eventDate"].strip(),
                "water_body":wb,
                "start_longitude":float(row["decimalLongitude"]),
                "start_latitude":float(row["decimalLatitude"]),
                "bearing_deg":parse_bearing(row["locationRemarks"]),
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            if pid in parents:
                children[pid].append({
                    "event_id":row["eventID"].strip(),
                    "location_id":row["locationID"].strip(),
                    "site_m":parse_site_m(row["locationID"]),
                })

    eligible={p for p in parents if len(children.get(p,[]))>=3}
    point_meta={
        x["event_id"]:(pid,x)
        for pid in eligible
        for x in children[pid]
    }

    state=defaultdict(lambda:{"any_seagrass":False,"thalassia":False})
    rd=csv.DictReader(io.StringIO(occ.decode("utf-8"),newline=""))
    for row in rd:
        eid=row["eventID"].strip()
        if eid not in point_meta:
            continue
        if row["occurrenceStatus"].strip()!="present" or row["order"].strip()!=ORDER:
            continue
        state[eid]["any_seagrass"]=True
        if row["scientificName"].strip()==THALASSIA:
            state[eid]["thalassia"]=True

    visits=[]
    for pid in sorted(eligible):
        p=parents[pid]
        pts=children[pid]
        visits.append({
            **p,
            "sampled_points":len(pts),
            "thalassia_frequency":sum(state[x["event_id"]]["thalassia"] for x in pts)/len(pts),
            "any_seagrass_frequency":sum(state[x["event_id"]]["any_seagrass"] for x in pts)/len(pts),
        })

    # Reproduce the existing recent-node frame: annualize visit frequencies and
    # select the latest eligible node-year.
    ny=defaultdict(lambda:{
        "visits":0,"tf":0.0,"af":0.0,"water_body":None,
        "parents":[],
    })
    for v in visits:
        k=(v["node_id"],v["year"])
        z=ny[k]
        z["visits"]+=1
        z["tf"]+=v["thalassia_frequency"]
        z["af"]+=v["any_seagrass_frequency"]
        z["water_body"]=v["water_body"]
        z["parents"].append(v["event_id"])

    annual=[]
    for (node,year),z in ny.items():
        annual.append({
            "node_id":node,
            "year":year,
            "water_body":z["water_body"],
            "thalassia_frequency":z["tf"]/z["visits"],
            "any_seagrass_frequency":z["af"]/z["visits"],
            "parents":z["parents"],
        })

    latest={}
    for a in annual:
        if a["node_id"] not in latest or a["year"]>latest[a["node_id"]]["year"]:
            latest[a["node_id"]]=a

    recent=sorted(latest.values(),key=lambda x:(x["water_body"],x["node_id"]))
    if len(recent)!=40:
        raise RuntimeError(f"recent core-node registry drift: {len(recent)} != 40")
    if sum(x["any_seagrass_frequency"]>0 for x in recent)!=40:
        raise RuntimeError("recent vegetated-node registry drift")
    if sum(x["thalassia_frequency"]>0 for x in recent)!=33:
        raise RuntimeError("recent Thalassia-positive registry drift")

    marks=[]
    node_meta=[]
    for a in recent:
        # All eligible visits in the latest node-year should use one fixed start
        # and one signed line-derived bearing. Check rather than silently choose.
        ps=[parents[pid] for pid in a["parents"]]
        starts={(round(p["start_longitude"],8),round(p["start_latitude"],8)) for p in ps}
        bearings={round(p["bearing_deg"],1) for p in ps}
        if len(starts)!=1 or len(bearings)!=1:
            raise RuntimeError(
                f"latest-year geometry not stable for {a['node_id']}: starts={starts} bearings={bearings}"
            )
        p=ps[0]
        by_site=defaultdict(lambda:{"sampled":0,"any":False,"thalassia":False})
        for pid in a["parents"]:
            for x in children[pid]:
                z=by_site[x["site_m"]]
                z["sampled"]+=1
                z["any"] = z["any"] or state[x["event_id"]]["any_seagrass"]
                z["thalassia"] = z["thalassia"] or state[x["event_id"]]["thalassia"]

        veg_sites=0
        th_sites=0
        for site_m,z in sorted(by_site.items()):
            if not z["any"]:
                continue
            lon,lat=dest_point(
                p["start_longitude"],p["start_latitude"],p["bearing_deg"],site_m
            )
            veg_sites+=1
            th_sites+=int(z["thalassia"])
            marks.append({
                "node_id":a["node_id"],
                "node_short":p["node_short"],
                "water_body":a["water_body"],
                "year":a["year"],
                "site_m":float(site_m),
                "longitude":float(lon),
                "latitude":float(lat),
                "thalassia_present":bool(z["thalassia"]),
                "sampled_visits_at_mark":int(z["sampled"]),
                "start_longitude":p["start_longitude"],
                "start_latitude":p["start_latitude"],
                "bearing_deg":p["bearing_deg"],
            })
        if veg_sites==0:
            raise RuntimeError(f"latest vegetated node has no vegetated meter mark: {a['node_id']}")
        node_meta.append({
            **{k:a[k] for k in (
                "node_id","year","water_body","thalassia_frequency","any_seagrass_frequency"
            )},
            "start_longitude":p["start_longitude"],
            "start_latitude":p["start_latitude"],
            "bearing_deg":p["bearing_deg"],
            "vegetated_meter_marks":veg_sites,
            "thalassia_positive_meter_marks":th_sites,
        })

    return recent,node_meta,marks


def arcgis_json(url:str,params:dict):
    raw=get_bytes(url+"/query?"+urlencode(params),240)
    return json.loads(raw.decode("utf-8"))


def tampa_envelope(nodes,pad=0.08):
    lons=[x["start_longitude"] for x in nodes]
    lats=[x["start_latitude"] for x in nodes]
    return f"{min(lons)-pad},{min(lats)-pad},{max(lons)+pad},{max(lats)+pad}"


def fetch_swfwmd_2024_union(nodes):
    envelope=tampa_envelope(nodes)
    geoms=[]; offset=0; page_size=1000
    while True:
        data=arcgis_json(SWFWMD_FEATURE_URL,{
            "where":"1=1",
            "geometry":envelope,
            "geometryType":"esriGeometryEnvelope",
            "inSR":"4326",
            "spatialRel":"esriSpatialRelIntersects",
            "outFields":"OBJECTID,FLUCCSCODE,FLUCCSDESC,DATESTAMP",
            "returnGeometry":"true",
            "outSR":"4326",
            "orderByFields":"OBJECTID",
            "resultOffset":str(offset),
            "resultRecordCount":str(page_size),
            "f":"geojson",
        })
        if "error" in data:
            raise RuntimeError(f"SWFWMD FeatureServer error: {data['error']}")
        feats=data.get("features",[])
        for ft in feats:
            if ft.get("geometry"):
                geoms.append(shape(ft["geometry"]))
        if len(feats)<page_size:
            break
        offset+=len(feats)
        if offset>20000:
            raise RuntimeError("SWFWMD pagination runaway guard")
    if not geoms:
        raise RuntimeError("SWFWMD 2024 FeatureServer returned no Tampa-area polygons")
    tr=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True)
    return shp_transform(tr.transform,unary_union(geoms)),{
        "source":"SWFWMD Seagrass in 2024 FeatureServer",
        "feature_url":SWFWMD_FEATURE_URL,
        "features_returned":len(geoms),
        "working_crs":"EPSG:26917",
        "query_envelope_wgs84":envelope,
    }


def fetch_usf_2024_mirror_union(nodes):
    """Fallback mirror accepted only with independent >=2024 DATESTAMP gate."""
    from datetime import datetime, timezone
    envelope=tampa_envelope(nodes)
    geoms=[]; dates=[]; offset=0; page_size=1000
    while True:
        data=arcgis_json(USF_MIRROR_URL,{
            "where":"1=1",
            "geometry":envelope,
            "geometryType":"esriGeometryEnvelope",
            "inSR":"4326",
            "spatialRel":"esriSpatialRelIntersects",
            "outFields":"OBJECTID,OBJECTID_1,FLUCCSCODE,FLUCCSDESC,DATESTAMP",
            "returnGeometry":"true",
            "outSR":"4326",
            "resultOffset":str(offset),
            "resultRecordCount":str(page_size),
            "f":"geojson",
        })
        if "error" in data:
            raise RuntimeError(f"USF mirror query error: {data['error']}")
        feats=data.get("features",[])
        for ft in feats:
            if ft.get("geometry"):
                geoms.append(shape(ft["geometry"]))
            val=(ft.get("properties") or {}).get("DATESTAMP")
            if val is not None:
                try:
                    if isinstance(val,(int,float)):
                        yr=datetime.fromtimestamp(float(val)/1000.0,tz=timezone.utc).year
                    else:
                        yr=int(str(val)[:4])
                    dates.append(yr)
                except Exception:
                    pass
        if len(feats)<page_size:
            break
        offset+=len(feats)
        if offset>20000:
            raise RuntimeError("USF mirror pagination runaway guard")
    if not geoms:
        raise RuntimeError("USF mirror returned no Tampa-area polygons")
    if not dates or float(np.median(np.asarray(dates,float)))<2024:
        raise RuntimeError(f"USF mirror failed >=2024 DATESTAMP gate: {Counter(dates)}")
    tr=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True)
    return shp_transform(tr.transform,unary_union(geoms)),{
        "source":"USF Water Institute Seagrass2024 mirror",
        "feature_url":USF_MIRROR_URL,
        "features_returned":len(geoms),
        "datestamp_year_counts":dict(Counter(dates)),
        "date_gate":"median DATESTAMP year >= 2024",
        "working_crs":"EPSG:26917",
        "fallback_used":True,
    }


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
    gdf=gdf.to_crs("EPSG:26917")
    tr=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True)
    xy=[tr.transform(x["start_longitude"],x["start_latitude"]) for x in nodes]
    local_box=box(
        min(x for x,y in xy)-5000,min(y for x,y in xy)-5000,
        max(x for x,y in xy)+5000,max(y for x,y in xy)+5000,
    )
    local=gdf[gdf.geometry.intersects(local_box)].copy()
    local=local[local.geometry.notna() & ~local.geometry.is_empty].copy()
    if local.empty:
        raise RuntimeError("FWC archive has no polygons near Tampa core nodes")
    bad=~local.geometry.is_valid
    if bad.any():
        local.loc[bad,"geometry"]=local.loc[bad,"geometry"].buffer(0)
    union=unary_union(list(local.geometry))
    audit={
        "source":"FWC/FWRI statewide seagrass archive",
        "archive_bytes":len(raw),
        "archive_sha256":hashlib.sha256(raw).hexdigest(),
        "source_features_total":int(len(gdf)),
        "tampa_nearby_features":int(len(local)),
        "source_crs":source_crs,
        "working_crs":"EPSG:26917",
        "fallback_used":True,
    }
    archive.unlink(missing_ok=True)
    return union,audit


def obtain_seagrass_union(outdir:Path,nodes):
    errors=[]
    try:
        return fetch_swfwmd_2024_union(nodes),errors
    except Exception as exc:
        errors.append({"source":"SWFWMD official","error":f"{type(exc).__name__}: {exc}"})
    try:
        return fetch_usf_2024_mirror_union(nodes),errors
    except Exception as exc:
        errors.append({"source":"USF 2024 mirror","error":f"{type(exc).__name__}: {exc}"})
    try:
        return fetch_fwc_seagrass_union(outdir,nodes),errors
    except Exception as exc:
        errors.append({"source":"FWC statewide archive","error":f"{type(exc).__name__}: {exc}"})
    raise RuntimeError(json.dumps(errors))


def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    recent,node_meta,marks=reconstruct_recent_meter_marks(
        fetch(FILES["event"]),fetch(FILES["occurrence"])
    )

    try:
        (union,source_audit),source_errors=obtain_seagrass_union(outdir,node_meta)
    except Exception as exc:
        unresolved={
            "schema":"tampa.bare_control_spatial_preflight_v1",
            "status":"source_delivery_unavailable_spatial_feasibility_unresolved",
            "response_independent":True,
            "coordinate_semantics":"meter marks reconstructed from pinned start coordinate + signed line-derived bearing + meter-mark distance",
            "registry":{
                "recent_vegetated_nodes":40,
                "recent_thalassia_positive_nodes":33,
                "vegetated_meter_marks":len(marks),
            },
            "frozen_gate":{
                "maximum_edge_distance_m":EDGE_MAX_M,
                "target_nodes":TARGET,
                "minimum_nodes":MINIMUM,
                "minimum_nodes_per_bay":MIN_PER_BAY,
                "passed":None,
            },
            "delivery_error":str(exc),
            "decision":"No scientific pass/fail assigned; preserve all frozen thresholds.",
            "claim_boundary":[
                "Source delivery failure is not ecological evidence.",
                "No future biological response is used.",
            ],
        }
        (outdir/"bare_control_spatial_preflight_v1.json").write_text(
            json.dumps(unresolved,indent=2,sort_keys=True)+"\n"
        )
        (outdir/"bare_control_spatial_candidates_v1.csv").write_text(
            "node_id,water_body,year,site_m,longitude,latitude,status\n"+
            "\n".join(
                f'{x["node_id"]},{x["water_body"]},{x["year"]},{x["site_m"]},'
                f'{x["longitude"]},{x["latitude"]},UNRESOLVED'
                for x in marks
            )+"\n"
        )
        print(json.dumps(unresolved,indent=2,sort_keys=True))
        return

    tr=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True)
    boundary=union.boundary

    assessed=[]
    for m in marks:
        p=Point(*tr.transform(m["longitude"],m["latitude"]))
        inside=bool(union.covers(p))
        edge=float(p.distance(boundary)) if inside else None
        near=float(p.distance(union)) if not inside else 0.0
        assessed.append({
            **m,
            "inside_mapped_seagrass":inside,
            "edge_distance_m":edge,
            "nearest_mapped_seagrass_distance_m":near,
            "bare_edge_candidate_100m":bool(inside and edge is not None and edge<=EDGE_MAX_M),
        })

    nodes=[]
    for n in node_meta:
        mm=[x for x in assessed if x["node_id"]==n["node_id"]]
        inside=[x for x in mm if x["inside_mapped_seagrass"]]
        cand=[x for x in mm if x["bare_edge_candidate_100m"]]
        tcand=[x for x in cand if x["thalassia_present"]]
        best=min(cand,key=lambda x:x["edge_distance_m"]) if cand else None
        bestt=min(tcand,key=lambda x:x["edge_distance_m"]) if tcand else None
        nodes.append({
            **n,
            "vegetated_marks_inside_map":len(inside),
            "mapped_state_compatible":bool(inside),
            "bare_edge_candidate_100m":bool(cand),
            "thalassia_mark_bare_edge_candidate_100m":bool(tcand),
            "best_candidate_site_m":best["site_m"] if best else None,
            "best_candidate_edge_distance_m":best["edge_distance_m"] if best else None,
            "best_thalassia_site_m":bestt["site_m"] if bestt else None,
            "best_thalassia_edge_distance_m":bestt["edge_distance_m"] if bestt else None,
        })

    by={}
    for wb in CORE:
        d=[x for x in nodes if x["water_body"]==wb]
        by[wb]={
            "recent_vegetated_nodes":len(d),
            "mapped_state_compatible_nodes":sum(x["mapped_state_compatible"] for x in d),
            "bare_edge_candidate_nodes_100m":sum(x["bare_edge_candidate_100m"] for x in d),
            "thalassia_mark_candidate_nodes_100m":sum(
                x["thalassia_mark_bare_edge_candidate_100m"] for x in d
            ),
            "map_state_mismatches":sum(not x["mapped_state_compatible"] for x in d),
        }

    total=sum(x["bare_edge_candidate_100m"] for x in nodes)
    minbay=min(by[wb]["bare_edge_candidate_nodes_100m"] for wb in CORE)
    passed=bool(total>=MINIMUM and minbay>=MIN_PER_BAY)
    mark_edge=[x["edge_distance_m"] for x in assessed if x["edge_distance_m"] is not None]

    result={
        "schema":"tampa.bare_control_spatial_preflight_v1",
        "status":"geographic_edge_feasibility_pass" if passed else "geographic_edge_feasibility_not_supported",
        "response_independent":True,
        "coordinate_semantics":{
            "start_coordinate":"pinned Darwin Core transect meter mark 0",
            "bearing":"signed bearing parsed from pinned locationRemarks; generated from original TBEP transect LINESTRING",
            "meter_mark_distance":"numeric suffix of child Point locationID",
            "important_correction":"Point-row coordinates repeat the start coordinate and are not literal meter-mark coordinates.",
        },
        "source":{
            "tbismp_commit":COMMIT,
            "recent_years":list(YEARS),
            "seagrass_source":source_audit,
            "failed_source_attempts":source_errors,
        },
        "registry":{
            "recent_vegetated_nodes":len(nodes),
            "recent_thalassia_positive_nodes":sum(x["thalassia_frequency"]>0 for x in nodes),
            "vegetated_meter_marks":len(assessed),
            "mapped_state_compatible_nodes":sum(x["mapped_state_compatible"] for x in nodes),
            "map_state_mismatches":sum(not x["mapped_state_compatible"] for x in nodes),
        },
        "meter_mark_edge_distance_m":{
            "n_inside":len(mark_edge),
            "median":float(np.median(mark_edge)) if mark_edge else None,
            "p25":float(np.quantile(mark_edge,0.25)) if mark_edge else None,
            "p75":float(np.quantile(mark_edge,0.75)) if mark_edge else None,
            "max":float(np.max(mark_edge)) if mark_edge else None,
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
        "nodes":nodes,
        "claim_boundary":[
            "A reconstructed vegetated meter mark within 100 m of mapped meadow edge is only a reconnaissance candidate, not a validated bare control.",
            "Field validation must still satisfy depth matching, comparable forcing, substrate/context, wake screening and simultaneous sensor geometry.",
            "The external map can omit small bare gaps and differs in survey timing from recent transect observations; GIS failure is conservative.",
            "Do not relax the frozen 100-m / 12-node / 3-per-bay thresholds after inspection.",
            "No future biological response is used.",
        ],
    }

    (outdir/"bare_control_spatial_preflight_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    with (outdir/"bare_control_spatial_candidates_v1.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(assessed[0].keys()))
        w.writeheader()
        w.writerows(assessed)

    print(json.dumps({
        "status":result["status"],
        "registry":result["registry"],
        "meter_mark_edge_distance_m":result["meter_mark_edge_distance_m"],
        "candidate_gate":result["candidate_gate"],
    },indent=2,sort_keys=True))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument(
        "--out",type=Path,
        default=Path("results/generated_bare_control_preflight")
    )
    args=ap.parse_args()
    main(args.out)
