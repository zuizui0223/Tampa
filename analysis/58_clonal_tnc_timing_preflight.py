#!/usr/bin/env python3
"""Historical design-feasibility audit for prospective clonal/TNC timing.

Uses already-open 2023-2025 Tampa monitoring data only to ask whether recent
Thalassia-positive core-bay nodes were surveyed in a compact enough seasonal
window to support the prospective <=28-day TNC campaign / +/-14-day baseline
alignment design.

This is not a mechanism test and opens no future response.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from collections import defaultdict,Counter
from datetime import datetime
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
 "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
 "occurrence":{"url":f"{BASE}/occurrence.csv","size":12508487,"blob":"d34aeb5aedb72459d1e04059629cb09450df929e"},
}
CORE=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
YEARS=(2023,2024,2025)
FOCAL="Thalassia testudinum"

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-clonal-timing-preflight/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(spec["size"]+1)
    if len(data)!=spec["size"] or git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError("pinned source identity drift")
    return data

def main(out:Path):
    er=csv.DictReader(io.StringIO(fetch(FILES["event"]).decode("utf-8"),newline=""))
    parents={}; children=defaultdict(list)
    for row in er:
        typ=row["eventType"].strip()
        if typ=="Transect":
            year=int(row["year"] or row["eventDate"][:4])
            wb=row["waterBody"].strip()
            if year in YEARS and wb in CORE:
                parents[row["eventID"].strip()]={
                    "node_id":row["locationID"].strip(),
                    "year":year,
                    "water_body":wb,
                    "date":datetime.strptime(row["eventDate"][:10],"%Y-%m-%d").date()
                }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            if pid in parents:
                children[pid].append(row["eventID"].strip())
    eligible={p for p in parents if len(children.get(p,[]))>=3}
    point_to_parent={eid:p for p in eligible for eid in children[p]}

    focal=set()
    rd=csv.DictReader(io.StringIO(fetch(FILES["occurrence"]).decode("utf-8"),newline=""))
    for row in rd:
        eid=row["eventID"].strip()
        if eid in point_to_parent and row["scientificName"].strip()==FOCAL and row["occurrenceStatus"].strip()=="present":
            focal.add(eid)

    visits=[]
    for pid in eligible:
        p=parents[pid]; pts=children[pid]
        freq=sum(eid in focal for eid in pts)/len(pts)
        visits.append({**p,"focal_frequency":freq})

    # annualize frequency; representative survey date = median ordinal date among visits
    ny=defaultdict(lambda:{"freq":[],"dates":[],"water_body":None})
    for v in visits:
        k=(v["node_id"],v["year"])
        z=ny[k]; z["freq"].append(v["focal_frequency"]); z["dates"].append(v["date"]); z["water_body"]=v["water_body"]
    annual=[]
    for (node,year),z in ny.items():
        ords=np.array([d.toordinal() for d in z["dates"]],dtype=float)
        med=int(np.median(ords))
        annual.append({
            "node_id":node,"year":year,"water_body":z["water_body"],
            "focal_frequency":float(np.mean(z["freq"])),
            "survey_date":datetime.fromordinal(med).date()
        })

    latest_all={}
    for x in annual:
        if x["node_id"] not in latest_all or x["year"]>latest_all[x["node_id"]]["year"]:
            latest_all[x["node_id"]]=x
    rows=sorted(
        [x for x in latest_all.values() if x["focal_frequency"]>0],
        key=lambda x:(x["water_body"],x["node_id"])
    )
    if len(rows)!=33:
        raise RuntimeError(f"recent latest-state Thalassia-positive node drift: {len(rows)} != 33")

    # For each year, quantify survey span among nodes whose latest positive state is that year.
    by_year={}
    for y in YEARS:
        d=[x for x in rows if x["year"]==y]
        if not d: continue
        dates=[x["survey_date"] for x in d]
        by_year[str(y)]={
            "nodes":len(d),
            "min_date":min(dates).isoformat(),
            "max_date":max(dates).isoformat(),
            "span_days":(max(dates)-min(dates)).days,
            "by_water_body":dict(Counter(x["water_body"] for x in d))
        }

    # Overall recent latest-state dates are not a proposed campaign; report only as historical context.
    dates=[x["survey_date"] for x in rows]
    months=Counter(d.strftime("%m") for d in dates)

    # Find densest 28-day historical window among the 33 latest-positive survey dates.
    ordered=sorted(rows,key=lambda x:x["survey_date"])
    best=[]
    for i,a in enumerate(ordered):
        b=[x for x in ordered if 0 <= (x["survey_date"]-a["survey_date"]).days <= 27]
        if len(b)>len(best): best=b
    best_by=Counter(x["water_body"] for x in best)

    result={
        "schema":"tampa.clonal_tnc_timing_feasibility_v1",
        "status":"historical_timing_feasibility_only",
        "evidence_class":"response-open historical field-design audit; not a mechanism test",
        "source":{"commit":COMMIT,"years":list(YEARS),"geography":list(CORE)},
        "registry":{
            "recent_thalassia_positive_nodes":len(rows),
            "by_water_body":dict(Counter(x["water_body"] for x in rows)),
            "latest_positive_years":dict(Counter(str(x["year"]) for x in rows)),
            "survey_month_counts":dict(sorted(months.items()))
        },
        "latest_positive_by_year":by_year,
        "densest_historical_28_day_window":{
            "nodes":len(best),
            "by_water_body":dict(best_by),
            "start":best[0]["survey_date"].isoformat() if best else None,
            "end":max(x["survey_date"] for x in best).isoformat() if best else None,
            "note":"Historical concentration only; not a license to select these nodes prospectively."
        },
        "prospective_decision":{
            "campaign_window_days":28,
            "baseline_alignment_days_each_side":14,
            "rule":"Do not rely on historical routine survey timing to create the prospective window. Coordinate the future baseline fixed-transect survey and TNC campaign as one planned field campaign.",
            "failure_boundary":"If baseline surveys cannot be paired within +/-14 days under one <=28-day TNC campaign, affected nodes are descriptive-only rather than widening the frozen seasonal window."
        },
        "nodes":[{**x,"survey_date":x["survey_date"].isoformat()} for x in rows],
        "claim_boundary":[
            "Historical survey timing is used only to assess logistics.",
            "No future biological response is opened.",
            "Do not select a convenient historical season after seeing future outcomes.",
            "The prospective seasonal window remains frozen regardless of this audit."
        ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("registry","latest_positive_by_year","densest_historical_28_day_window","prospective_decision")},indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_clonal_timing_preflight/clonal_tnc_timing_feasibility_v1.json"))
    a=ap.parse_args(); main(a.out)
