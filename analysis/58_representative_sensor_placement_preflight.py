#!/usr/bin/env python3
"""Response-independent audit of representative hydrodynamic sensor placement.

The earlier GIS gate allowed any recent vegetated meter mark within a node to
supply a <=100 m mapped-edge candidate. This audit asks whether that feasibility
persists when the vegetated sensor location is chosen *without* using edge
distance.

No future biological response is opened.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

import numpy as np
from pyproj import Transformer
from shapely.geometry import Point

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"analysis/55_bare_control_spatial_preflight.py"
spec=importlib.util.spec_from_file_location("tampa_bare_preflight",SRC)
m=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

EDGE_MAX_M=100.0
CORE=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
MINIMUM=12
MIN_PER_BAY=3
TARGET=18

def pick_rep(marks,thalassia_only=False):
    veg=sorted(marks,key=lambda x:x["site_m"])
    if not veg:
        return None
    med=float(np.median([x["site_m"] for x in veg]))
    pool=[x for x in veg if (x["thalassia_present"] if thalassia_only else True)]
    if not pool:
        return None
    chosen=min(pool,key=lambda x:(abs(x["site_m"]-med),x["site_m"]))
    return {**chosen,"node_vegetated_site_median":med}

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    recent,node_meta,marks=m.reconstruct_recent_meter_marks(
        m.fetch(m.FILES["event"]),m.fetch(m.FILES["occurrence"])
    )
    (union,source_audit),source_errors=m.obtain_seagrass_union(outdir,node_meta)
    boundary=union.boundary
    tr=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True)

    rows=[]
    for n in node_meta:
        mm=[x for x in marks if x["node_id"]==n["node_id"]]
        rep=pick_rep(mm,False)
        trep=pick_rep(mm,True)
        if rep is None:
            raise RuntimeError(f"no representative vegetated mark for {n['node_id']}")

        def assess(x):
            if x is None:
                return None
            p=Point(*tr.transform(x["longitude"],x["latitude"]))
            inside=bool(union.covers(p))
            edge=float(p.distance(boundary)) if inside else None
            return {
                "site_m":x["site_m"],
                "node_vegetated_site_median":x["node_vegetated_site_median"],
                "longitude":x["longitude"],
                "latitude":x["latitude"],
                "inside_mapped_seagrass":inside,
                "edge_distance_m":edge,
                "edge_candidate_100m":bool(inside and edge is not None and edge<=EDGE_MAX_M)
            }

        rows.append({
            "node_id":n["node_id"],
            "water_body":n["water_body"],
            "year":n["year"],
            "thalassia_frequency":n["thalassia_frequency"],
            "vegetated_meter_marks":n["vegetated_meter_marks"],
            "thalassia_positive_meter_marks":n["thalassia_positive_meter_marks"],
            "vegetated_representative":assess(rep),
            "thalassia_representative":assess(trep)
        })

    by={}
    for wb in CORE:
        d=[x for x in rows if x["water_body"]==wb]
        v=sum(bool(x["vegetated_representative"]["edge_candidate_100m"]) for x in d)
        td=[x for x in d if x["thalassia_representative"] is not None]
        t=sum(bool(x["thalassia_representative"]["edge_candidate_100m"]) for x in td)
        by[wb]={
            "recent_vegetated_nodes":len(d),
            "vegetated_representative_candidates_100m":v,
            "recent_thalassia_positive_nodes":len(td),
            "thalassia_representative_candidates_100m":t
        }

    veg_n=sum(bool(x["vegetated_representative"]["edge_candidate_100m"]) for x in rows)
    th_rows=[x for x in rows if x["thalassia_representative"] is not None]
    th_n=sum(bool(x["thalassia_representative"]["edge_candidate_100m"]) for x in th_rows)

    veg_pass=bool(veg_n>=MINIMUM and min(by[w]["vegetated_representative_candidates_100m"] for w in CORE)>=MIN_PER_BAY)
    th_pass=bool(th_n>=MINIMUM and min(by[w]["thalassia_representative_candidates_100m"] for w in CORE)>=MIN_PER_BAY)

    result={
        "schema":"tampa.representative_sensor_placement_preflight_v1",
        "status":"representative_placement_both_gates_pass" if veg_pass and th_pass else (
            "representative_placement_general_only_pass" if veg_pass else "representative_placement_gate_not_supported"
        ),
        "response_independent":True,
        "selection":{
            "vegetated":"closest vegetated mark to node median vegetated site_m; tie -> lower site_m",
            "thalassia":"closest Thalassia-positive mark to node median vegetated site_m; tie -> lower site_m",
            "edge_distance_used_for_selection":False
        },
        "source":{"seagrass_map":source_audit,"failed_source_attempts":source_errors},
        "registry":{
            "recent_vegetated_nodes":len(rows),
            "recent_thalassia_positive_nodes":len(th_rows)
        },
        "gate":{
            "maximum_edge_distance_m":EDGE_MAX_M,
            "minimum_nodes":MINIMUM,
            "minimum_nodes_per_bay":MIN_PER_BAY,
            "target_nodes":TARGET,
            "vegetated_representative_candidate_nodes":veg_n,
            "vegetated_gate_pass":veg_pass,
            "thalassia_representative_candidate_nodes":th_n,
            "thalassia_gate_pass":th_pass,
            "by_water_body":by
        },
        "nodes":rows,
        "claim_boundary":[
            "No future biological response is used.",
            "Sensor-position selection is independent of mapped edge distance.",
            "GIS feasibility does not replace field control qualification.",
            "Do not switch to edge-nearest meter marks to rescue a failed representative-placement gate."
        ]
    }
    (outdir/"representative_sensor_placement_preflight_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","registry","gate")},indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_representative_sensor_placement"))
    a=ap.parse_args(); main(a.out)
