#!/usr/bin/env python3
"""Recent community-state preflight for the direct hydrodynamic sampling frame.

This is a design-feasibility audit, not an ecological endpoint test. It opens no
future biological response. From the pinned 2023-2025 source record it asks:
1) how many recent Old/Middle/Lower Tampa nodes are Thalassia-positive and can
   enter the future Thalassia-persistence primary cohort;
2) how many are vegetated across a broad Thalassia share gradient and can enter
   the secondary community functional-insurance physical test.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
import numpy as np

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

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-functional-insurance-preflight/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(spec["size"]+1)
    if len(data)!=spec["size"]:
        raise RuntimeError(f"source size drift {len(data)} != {spec['size']}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError("source blob drift")
    return data

def parse_event(data:bytes):
    rd=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
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
                }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            if pid in parents:
                children[pid].append(row["eventID"].strip())
    eligible={p for p in parents if len(children.get(p,[]))>=3}
    point_to_parent={
        eid:p for p in eligible for eid in children[p]
    }
    return {p:parents[p] for p in eligible},children,point_to_parent

def parse_occurrence(data:bytes,point_ids:set[str]):
    rd=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    state=defaultdict(lambda:{"thalassia":False,"species":set()})
    for row in rd:
        eid=row["eventID"].strip()
        if eid not in point_ids:
            continue
        if row["occurrenceStatus"].strip()!="present" or row["order"].strip()!=ORDER:
            continue
        sci=row["scientificName"].strip()
        if not sci:
            continue
        state[eid]["species"].add(sci)
        if sci==THALASSIA:
            state[eid]["thalassia"]=True
    return state

def visit_states(parents,children,state):
    rows=[]
    for pid,p in parents.items():
        eids=children[pid]
        n=len(eids); th=0; anysg=0
        for eid in eids:
            s=state.get(eid)
            if s and s["species"]:
                anysg+=1
                th+=int(s["thalassia"])
        rows.append({
            **p,
            "sampled_points":n,
            "thalassia_frequency":th/n,
            "any_seagrass_frequency":anysg/n,
        })
    return rows

def annual_latest(visits):
    ny=defaultdict(lambda:{"n":0,"tf":0.0,"af":0.0,"water_body":None})
    for v in visits:
        key=(v["node_id"],v["year"])
        x=ny[key]; x["n"]+=1; x["tf"]+=v["thalassia_frequency"]; x["af"]+=v["any_seagrass_frequency"]; x["water_body"]=v["water_body"]
    annual=[]
    for (node,year),x in ny.items():
        annual.append({
            "node_id":node,"year":year,"water_body":x["water_body"],
            "thalassia_frequency":x["tf"]/x["n"],
            "any_seagrass_frequency":x["af"]/x["n"],
        })
    latest={}
    for x in annual:
        if x["node_id"] not in latest or x["year"]>latest[x["node_id"]]["year"]:
            latest[x["node_id"]]=x
    out=[]
    for x in latest.values():
        af=x["any_seagrass_frequency"]; tf=x["thalassia_frequency"]
        share=(tf/af) if af>0 else None
        if af<=0:
            cat="bare"
        elif tf<=0:
            cat="alternative_only"
        elif share>=0.8:
            cat="thalassia_dominant"
        elif share<=0.2:
            cat="low_thalassia_mixed"
        else:
            cat="intermediate_mixed"
        out.append({**x,"thalassia_share_of_seagrass_points":share,"category":cat})
    return sorted(out,key=lambda z:(z["water_body"],z["node_id"]))

def q(arr,p):
    return float(np.quantile(np.asarray(arr,float),p)) if arr else None

def main(out:Path):
    raw={k:fetch(v) for k,v in FILES.items()}
    parents,children,point_to_parent=parse_event(raw["event"])
    state=parse_occurrence(raw["occurrence"],set(point_to_parent))
    latest=annual_latest(visit_states(parents,children,state))

    by={}
    for wb in CORE:
        d=[x for x in latest if x["water_body"]==wb]
        by[wb]={
            "recent_nodes":len(d),
            "thalassia_positive_nodes":sum(x["thalassia_frequency"]>0 for x in d),
            "vegetated_nodes":sum(x["any_seagrass_frequency"]>0 for x in d),
            "alternative_only_nodes":sum(x["category"]=="alternative_only" for x in d),
            "categories":dict(Counter(x["category"] for x in d)),
            "latest_years":dict(Counter(str(x["year"]) for x in d)),
        }

    shares=[x["thalassia_share_of_seagrass_points"] for x in latest if x["thalassia_share_of_seagrass_points"] is not None]
    primary_n=sum(x["thalassia_frequency"]>0 for x in latest)
    vegetated_n=sum(x["any_seagrass_frequency"]>0 for x in latest)
    min_primary_bay=min(by[wb]["thalassia_positive_nodes"] for wb in CORE)

    result={
        "schema":"tampa.functional_insurance_sampling_preflight_v1",
        "status":"recent_sampling_frame_supports_split_primary_and_functional_cohorts",
        "evidence_class":"response-open historical design feasibility only; not an ecological mechanism test",
        "source":{"commit":COMMIT,"years":list(YEARS),"geography":list(CORE)},
        "registry":{
            "stable_core_nodes_total":47,
            "nodes_with_recent_eligible_state":len(latest),
            "nodes_without_recent_eligible_state":47-len(latest),
            "recent_thalassia_positive_nodes":primary_n,
            "recent_vegetated_nodes":vegetated_n,
            "recent_alternative_only_nodes":sum(x["category"]=="alternative_only" for x in latest),
        },
        "by_water_body":by,
        "thalassia_share_of_seagrass_points":{
            "definition":"latest eligible annual Thalassia point frequency / latest eligible annual any-seagrass point frequency",
            "n_vegetated_nodes":len(shares),
            "min":min(shares) if shares else None,
            "q25":q(shares,0.25),
            "median":q(shares,0.5),
            "q75":q(shares,0.75),
            "max":max(shares) if shares else None,
        },
        "design_consequence":{
            "primary_future_persistence_cohort":"baseline Thalassia-positive Old/Middle/Lower nodes only",
            "recent_primary_cohort_size":primary_n,
            "recent_minimum_per_bay":min_primary_bay,
            "confirmatory_gate_30_nodes_and_8_per_bay_would_pass_on_recent_frame":bool(primary_n>=30 and min_primary_bay>=8),
            "secondary_functional_insurance_cohort":"all baseline-vegetated core nodes, including alternative-only nodes",
            "recent_secondary_cohort_size":vegetated_n,
            "reason":"Alternative-only meadows are informative for physical functional insurance but should not be used to inflate the primary future Thalassia-persistence cohort."
        },
        "nodes":latest,
        "claim_boundary":[
            "This audit uses already-open historical community composition only to assess prospective sampling feasibility.",
            "The 2023-2025 frame is not a future endpoint and does not prove functional insurance.",
            "Deployment eligibility must be re-evaluated using the contemporaneous baseline survey before sensors are placed.",
            "Do not add alternative-only nodes to the primary Thalassia-persistence analysis to rescue sample size.",
            "Alternative-only nodes may enter the separately declared physical community-functional-insurance analysis."
        ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","registry","by_water_body","thalassia_share_of_seagrass_points","design_consequence")},indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_functional_insurance_preflight/functional_insurance_sampling_preflight_v1.json"))
    a=ap.parse_args(); main(a.out)
