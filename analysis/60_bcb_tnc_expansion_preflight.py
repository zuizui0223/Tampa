#!/usr/bin/env python3
"""Response-open baseline design audit for adding Boca Ciega Bay to future TNC sampling.

This does NOT test a mechanism and opens no future response.
It asks whether Boca Ciega Bay contributes enough contemporaneously relevant
Thalassia-positive fixed nodes, with adequate meter-mark spatial replication,
to improve the prospective below-ground reserve design.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from collections import defaultdict,Counter
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np
from scipy.stats import nct,t

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
 "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
 "occurrence":{"url":f"{BASE}/occurrence.csv","size":12508487,"blob":"d34aeb5aedb72459d1e04059629cb09450df929e"},
}
CURRENT=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
EXPANDED=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
YEARS=(2023,2024,2025)
FOCAL="Thalassia testudinum"

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-BCB-expansion-preflight/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(spec["size"]+1)
    if len(data)!=spec["size"] or git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError("pinned source identity drift")
    return data

def parse_site(location_id:str):
    try:
        return float(location_id.rsplit(":",1)[-1])
    except Exception:
        return None

def detectable_partial_r(n:int,controls:int,alpha=.05,power=.80):
    df=n-controls-2
    crit=t.ppf(1-alpha/2,df)
    lo,hi=1e-6,.999
    for _ in range(100):
        r=(lo+hi)/2
        delta=math.sqrt(df*r*r/(1-r*r))
        p=nct.sf(crit,df,delta)+nct.cdf(-crit,df,delta)
        if p<power: lo=r
        else: hi=r
    return (lo+hi)/2

def main(out:Path):
    er=csv.DictReader(io.StringIO(fetch(FILES["event"]).decode("utf-8"),newline=""))
    parents={}; children=defaultdict(list); point_meta={}
    for row in er:
        typ=row["eventType"].strip()
        if typ=="Transect":
            year=int(row["year"] or row["eventDate"][:4])
            wb=row["waterBody"].strip()
            if year in YEARS and wb in EXPANDED:
                parents[row["eventID"].strip()]={
                    "node_id":row["locationID"].strip(),
                    "year":year,"water_body":wb
                }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            if pid in parents:
                eid=row["eventID"].strip()
                children[pid].append(eid)
                point_meta[eid]={"pid":pid,"site_m":parse_site(row["locationID"].strip())}

    eligible={p for p in parents if len(children.get(p,[]))>=3}
    focal=set()
    rd=csv.DictReader(io.StringIO(fetch(FILES["occurrence"]).decode("utf-8"),newline=""))
    for row in rd:
        eid=row["eventID"].strip()
        meta=point_meta.get(eid)
        if not meta or meta["pid"] not in eligible:
            continue
        if row["scientificName"].strip()==FOCAL and row["occurrenceStatus"].strip()=="present":
            focal.add(eid)

    visits=[]
    for pid in eligible:
        p=parents[pid]; pts=children[pid]
        visits.append({
            **p,"pid":pid,
            "focal_frequency":sum(e in focal for e in pts)/len(pts)
        })

    ny=defaultdict(lambda:{"n":0,"freq":0.0,"water_body":None,"pids":[]})
    for v in visits:
        k=(v["node_id"],v["year"])
        z=ny[k];z["n"]+=1;z["freq"]+=v["focal_frequency"];z["water_body"]=v["water_body"];z["pids"].append(v["pid"])
    annual=[]
    for (node,year),z in ny.items():
        annual.append({
            "node_id":node,"year":year,"water_body":z["water_body"],
            "focal_frequency":z["freq"]/z["n"],"pids":z["pids"]
        })
    latest={}
    for x in annual:
        if x["node_id"] not in latest or x["year"]>latest[x["node_id"]]["year"]:
            latest[x["node_id"]]=x
    latest=list(latest.values())

    rows=[]
    for x in latest:
        if x["focal_frequency"]<=0:
            continue
        sites=set()
        for pid in x["pids"]:
            for eid in children[pid]:
                if eid in focal and point_meta[eid]["site_m"] is not None:
                    sites.add(float(point_meta[eid]["site_m"]))
        rows.append({
            "node_id":x["node_id"],"water_body":x["water_body"],"year":x["year"],
            "focal_frequency":x["focal_frequency"],
            "positive_meter_marks":len(sites),
            "positive_site_m":sorted(sites)
        })

    by={}
    for wb in EXPANDED:
        d=[x for x in rows if x["water_body"]==wb]
        by[wb]={
            "thalassia_positive_nodes":len(d),
            "nodes_with_ge3_positive_marks":sum(x["positive_meter_marks"]>=3 for x in d),
            "nodes_with_lt3_positive_marks":sum(x["positive_meter_marks"]<3 for x in d),
            "positive_mark_min":min((x["positive_meter_marks"] for x in d),default=None),
            "positive_mark_median":float(np.median([x["positive_meter_marks"] for x in d])) if d else None,
            "positive_mark_max":max((x["positive_meter_marks"] for x in d),default=None)
        }

    current_n=sum(by[x]["thalassia_positive_nodes"] for x in CURRENT)
    expanded_n=sum(by[x]["thalassia_positive_nodes"] for x in EXPANDED)

    # Current model: TNC + baseline frequency + baseline BB + 2 bay indicators => 4 controls around focal TNC.
    # Expanded model adds one extra bay indicator => 5 controls.
    r33=detectable_partial_r(current_n,4)
    r41=detectable_partial_r(expanded_n,5)

    bcb=by["Boca Ciega Bay"]
    feasible=(
        bcb["thalassia_positive_nodes"]>=8 and
        bcb["nodes_with_lt3_positive_marks"]==0 and
        expanded_n>=40
    )

    result={
        "schema":"tampa.bcb_tnc_expansion_preflight_v1",
        "status":"four_bay_tnc_expansion_feasible" if feasible else "four_bay_tnc_expansion_not_supported",
        "evidence_class":"response-open baseline field-design feasibility only; no future outcome",
        "source":{"commit":COMMIT,"years":list(YEARS)},
        "current_three_bay":{
            "bays":list(CURRENT),
            "recent_thalassia_positive_nodes":current_n,
            "approximate_80pct_detectable_partial_r":r33
        },
        "candidate_four_bay":{
            "bays":list(EXPANDED),
            "recent_thalassia_positive_nodes":expanded_n,
            "minimum_nodes_per_bay":min(by[x]["thalassia_positive_nodes"] for x in EXPANDED),
            "approximate_80pct_detectable_partial_r":r41,
            "by_water_body":by
        },
        "boca_ciega_design_value":{
            "additional_nodes":bcb["thalassia_positive_nodes"],
            "all_nodes_have_ge3_positive_marks":bcb["nodes_with_lt3_positive_marks"]==0,
            "role":"additional independent Thalassia meadow context / prospective generality; not selected using a future response"
        },
        "decision":"If field permission/logistics are comparable, Boca Ciega Bay is eligible for a separately frozen four-bay TNC expansion before future response access. Do not add it later only because the three-bay TNC result is null.",
        "boundary":[
            "This preflight does not modify the already frozen three-bay contract by itself.",
            "Opened 2023-2025 state is used only for future field feasibility.",
            "Boca Ciega Bay inclusion must be decided before TNC collection and future outcome access.",
            "Event-scale hot-fresh and hydrodynamic designs may retain different geographies; mechanism programs need not share an identical sampling frame.",
            "Do not treat increased n as permission to weaken seasonal, assay, or spatial-core rules."
        ],
        "nodes":sorted(rows,key=lambda x:(x["water_body"],x["node_id"]))
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","current_three_bay","candidate_four_bay","boca_ciega_design_value","decision")},indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_bcb_expansion/bcb_tnc_expansion_preflight_v1.json"))
    a=ap.parse_args(); main(a.out)
