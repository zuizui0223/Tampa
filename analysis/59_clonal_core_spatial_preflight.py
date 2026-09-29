#!/usr/bin/env python3
"""Baseline-only spatial feasibility for the prospective rhizome-TNC cores."""
from __future__ import annotations
import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"analysis/55_bare_control_spatial_preflight.py"
spec=importlib.util.spec_from_file_location("tampa_meter_marks",SRC)
m=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

CORE=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")

def nearest_unique(vals,target,used):
    cand=sorted((abs(x-target),x) for x in vals if x not in used)
    if not cand:
        return None
    return cand[0][1]

def main(out:Path):
    _,node_meta,marks=m.reconstruct_recent_meter_marks(
        m.fetch(m.FILES["event"]),m.fetch(m.FILES["occurrence"])
    )
    rows=[]
    for n in node_meta:
        if n["water_body"] not in CORE or n["thalassia_frequency"]<=0:
            continue
        vals=sorted({float(x["site_m"]) for x in marks if x["node_id"]==n["node_id"] and x["thalassia_present"]})
        if not vals:
            raise RuntimeError(f"positive node has no positive meter marks: {n['node_id']}")
        if len(vals)>=3:
            q=np.quantile(np.asarray(vals,float),[.25,.5,.75])
            used=set(); anchors=[]
            for target in q:
                hit=nearest_unique(vals,float(target),used)
                if hit is None:
                    raise RuntimeError("unique anchor assignment failed")
                anchors.append(hit); used.add(hit)
            design_class="three_spatial_anchors"
        elif len(vals)==2:
            mid=float(np.mean(vals))
            third=min(vals,key=lambda x:(abs(x-mid),x))
            anchors=[vals[0],vals[1],third]
            design_class="two_marks_one_replicated_anchor"
        else:
            anchors=[vals[0],vals[0],vals[0]]
            design_class="single_mark_three_offsets"
        rows.append({
            "node_id":n["node_id"],
            "water_body":n["water_body"],
            "year":n["year"],
            "thalassia_frequency":n["thalassia_frequency"],
            "positive_meter_marks":len(vals),
            "design_class":design_class,
            "anchor_site_m":anchors
        })

    by={}
    for wb in CORE:
        d=[x for x in rows if x["water_body"]==wb]
        by[wb]={
            "nodes":len(d),
            "three_or_more_positive_marks":sum(x["positive_meter_marks"]>=3 for x in d),
            "two_positive_marks":sum(x["positive_meter_marks"]==2 for x in d),
            "one_positive_mark":sum(x["positive_meter_marks"]==1 for x in d),
            "design_classes":dict(Counter(x["design_class"] for x in d))
        }
    counts=[x["positive_meter_marks"] for x in rows]
    result={
        "schema":"tampa.clonal_core_spatial_preflight_v1",
        "status":"baseline_spatial_core_design_feasible",
        "evidence_class":"response-open baseline design feasibility only; no future outcome",
        "registry":{
            "thalassia_positive_nodes":len(rows),
            "by_water_body":by,
            "positive_meter_mark_count":{
                "min":int(min(counts)),
                "median":float(np.median(counts)),
                "max":int(max(counts)),
                "nodes_with_ge3":sum(x>=3 for x in counts),
                "nodes_with_lt3":sum(x<3 for x in counts)
            }
        },
        "anchor_rule":{
            "ge3":"observed positive marks nearest q25/q50/q75 site_m, unique where possible",
            "eq2":"one core anchor per mark plus third independent lateral-offset core at midpoint-nearest positive mark",
            "eq1":"three independent offset cores adjacent to the single positive mark"
        },
        "nodes":rows,
        "claim_boundary":[
            "Recent vegetation state is used only to preflight sampling geometry.",
            "No TNC values or future biological responses are available or used.",
            "Nodes with fewer than three positive marks have reduced spatial representation and retain that design-class label.",
            "Do not move core anchors after TNC assay results."
        ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","registry","anchor_rule")},indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_clonal_core_preflight/clonal_core_spatial_preflight_v1.json"))
    a=ap.parse_args(); main(a.out)
