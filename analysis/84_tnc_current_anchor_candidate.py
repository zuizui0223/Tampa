#!/usr/bin/env python3
"""Response-blind prospective field-point to TNC anchor candidate crosswalk.

Consumes externally supplied contemporaneous baseline point records and the
existing four-bay node/date manifest. Uses the same nearest-unique quartile
selection as analysis/62; DOES NOT freeze locations, permit coring, read TNC
values or future meadow response, or replace the authoritative field gates.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
CLASSES=("q25","q50","q75")
NODE_COLUMNS={"node_id","water_body","thalassia_positive","tnc_date","baseline_survey_date"}
MARK_COLUMNS={"node_id","water_body","baseline_survey_date","point_location_id",
              "site_m","thalassia_present","baseline_bb_anchor"}
MIN_TOTAL=36
MIN_BAY=6

def read_csv(path:Path,columns:set[str])->list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        header=reader.fieldnames or []
        if len(header)!=len(set(header)) or set(header)!=columns:
            raise ValueError(f"{path}: exact response-blind header required; "
                             f"missing={sorted(columns-set(header))}; "
                             f"extra={sorted(set(header)-columns)}")
        return list(reader)

def flag(x:object,where:str)->bool:
    if isinstance(x,bool): return x
    val=str(x).strip().lower()
    if val in {"true","1","yes"}: return True
    if val in {"false","0","no"}: return False
    raise ValueError(f"{where}: invalid boolean {x!r}")

def date(x:object,where:str)->dt.date:
    try:
        d=dt.date.fromisoformat(str(x).strip())
        if d.isoformat()!=str(x).strip():
            raise ValueError("noncanonical date")
        return d
    except Exception as e:
        raise ValueError(f"{where}: require ISO YYYY-MM-DD") from e

def number(x:object,where:str)->float:
    try:
        v=float(x)
        if not math.isfinite(v): raise ValueError("non-finite")
        return v
    except Exception as e:
        raise ValueError(f"{where}: invalid numeric value {x!r}") from e

def quantile(vals:list[float],p:float)->float:
    s=sorted(vals)
    if not s: raise ValueError("empty quantile source")
    pos=(len(s)-1)*p
    lo=math.floor(pos)
    hi=math.ceil(pos)
    return s[lo]+(s[hi]-s[lo])*(pos-lo)

def quartile_sites(sites:list[float])->list[float]:
    """Replicate np.quantile(...,[.25,.50,.75]) + nearest_unique lower-site tie."""
    if len(sites)<3 or len(set(sites))!=len(sites):
        raise ValueError("need at least three distinct positive site_m values")
    ordered=sorted(sites)
    result=[]
    used=set()
    for p in (.25,.5,.75):
        target=quantile(ordered,p)
        remaining=[s for s in ordered if s not in used]
        hit=min(remaining,key=lambda s:(abs(s-target),s))
        result.append(hit)
        used.add(hit)
    return result

def build(node_rows:list[dict],mark_rows:list[dict])->dict:
    if not node_rows or not mark_rows:
        raise ValueError("full contemporaneous node and point census required")
    nodes={}
    date_vals=[]
    for row in node_rows:
        if set(row)!=NODE_COLUMNS:
            raise ValueError("node manifest contains extra, missing, or forbidden response columns")
        nid=str(row["node_id"]).strip()
        bay=str(row["water_body"]).strip()
        if not nid or nid in nodes or bay not in BAYS:
            raise ValueError("duplicate/blank node ID or invalid water body")
        positive=flag(row["thalassia_positive"],nid)
        when=date(row["baseline_survey_date"],f"{nid}.baseline_survey_date")
        planned=date(row["tnc_date"],f"{nid}.tnc_date") if positive else None
        if positive:
            if abs((planned-when).days)>14:
                raise ValueError(f"{nid}: baseline-to-planned-TNC exceeds frozen +/-14 days")
            date_vals.append(planned)
        nodes[nid]=(bay,positive,when,planned)
    if not date_vals or (max(date_vals)-min(date_vals)).days>28:
        raise ValueError("missing positive TNC dates or frozen 28-day span exceeded")

    bynode=defaultdict(list)
    all_point_ids=set()
    bynode_sites=defaultdict(set)
    for row in mark_rows:
        if set(row)!=MARK_COLUMNS:
            raise ValueError("point census has extra/missing/forbidden outcome columns")
        nid=str(row["node_id"]).strip()
        bay=str(row["water_body"]).strip()
        pid=str(row["point_location_id"]).strip()
        if nid not in nodes or nodes[nid][0]!=bay:
            raise ValueError(f"point for unregistered or misassigned node: {nid}")
        when=date(row["baseline_survey_date"],f"{nid}.point_date")
        if when!=nodes[nid][2]:
            raise ValueError(f"{nid}: point survey date disagrees with node manifest")
        site=number(row["site_m"],f"{nid}.site_m")
        if site<0 or not pid or pid in all_point_ids or site in bynode_sites[nid]:
            raise ValueError(f"{nid}: duplicate/missing point identity or site_m")
        all_point_ids.add(pid)
        bynode_sites[nid].add(site)
        bynode[nid].append({
            "point_location_id":pid,
            "site_m":site,
            "focal":flag(row["thalassia_present"],f"{nid}.{pid}.thalassia_present"),
            "bb_raw":str(row["baseline_bb_anchor"]).strip()
        })

    anchors=[]
    excluded=[]
    positive_nodes=0
    complete=Counter()
    for nid,(bay,expected_positive,when,planned) in nodes.items():
        if nid not in bynode:
            raise ValueError(f"{nid}: missing full baseline point survey roster")
        visit=bynode[nid]
        positives=[m for m in visit if m["focal"]]
        if bool(positives)!=expected_positive:
            raise ValueError(f"{nid}: node positive status contradicts point census")
        if not expected_positive: continue
        positive_nodes+=1
        if len(visit)<3 or len(positives)<3:
            excluded.append({"node_id":nid,"water_body":bay,
                             "reason":"fewer_than_three_current_live_marks"})
            continue
        selected=quartile_sites([m["site_m"] for m in positives])
        rows=[]
        invalid=None
        for cls,site in zip(CLASSES,selected):
            point=next(m for m in positives if m["site_m"]==site)
            try:
                bb=number(point["bb_raw"],f"{nid}.{cls}.baseline_bb_anchor")
                if not (0<bb<=5):
                    raise ValueError("numeric current focal BB must be positive and <=5")
            except ValueError:
                invalid=f"selected {cls} lacks valid numeric current BB (no alternative mark allowed)"
                break
            rows.append({
                "node_id":nid,"water_body":bay,"anchor_id":cls,
                "point_location_id":point["point_location_id"],
                "site_m":site,"baseline_bb_anchor":bb,
                "baseline_survey_date":when.isoformat(),
                "planned_tnc_date":planned.isoformat(),
                "current_eligibility_evidence":"CURRENT_BASELINE_INPUT_ONLY",
                "sampling_authority_status":"NOT_AUTHORIZED",
            })
        if invalid:
            excluded.append({"node_id":nid,"water_body":bay,"reason":invalid})
            continue
        anchors.extend(rows)
        complete[bay]+=1

    count=sum(complete.values())
    status=("PASS_ANCHOR_CANDIDATE_GEOMETRY_ONLY" if count>=MIN_TOTAL
            and all(complete[b]>=MIN_BAY for b in BAYS)
            else "STOP_COMPLETE_TRIPLET_GATE")
    return {
        "schema":"tampa.contemporaneous_tnc_anchor_candidate_v1",
        "status":status,
        "historical_frame_reference":"NOT_USED_FOR_SELECTION",
        "source_state":"EXTERNALLY_SUPPLIED_CONTEMPORANEOUS_BASELINE_NOT_INDEPENDENTLY_VERIFIED",
        "positive_nodes":positive_nodes,
        "complete_triplet_nodes":count,
        "bay_complete_triplet_counts":{b:complete[b] for b in BAYS},
        "original_gate":{"min_complete_nodes":MIN_TOTAL,"min_per_bay":MIN_BAY},
        "anchor_candidates":anchors,
        "excluded_nodes":excluded,
        "scientific_boundary":[
            "Candidate positions are computed from all supplied current-positive meter marks; completeness of the externally supplied point census must be independently verified by the monitoring authority.",
            "Do not treat this output as a frozen final core location, permission, destructive field approval, or eligibility beyond the recorded baseline.",
            "Exactly the predeclared nearest-unique q25/q50/q75 algorithm is used; missing selected numeric BB excludes the full node, with no outcome-dependent mark replacement.",
            "Both TNC method pilot and integrated resources/permit/site-protection freezes must pass independently before any outcome-bearing sample.",
            "No HPLC reserve values, future ecological outcome, clonal buffering mechanism or management effect is tested."
        ],
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--nodes",type=Path,required=True,
                   help="authoritative response-independent node/date manifest")
    p.add_argument("--points",type=Path,required=True,
                   help="complete contemporaneous sampled meter-mark roster for listed nodes")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--candidate-csv",type=Path,default=None)
    args=p.parse_args()
    result=build(read_csv(args.nodes,NODE_COLUMNS),read_csv(args.points,MARK_COLUMNS))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if args.candidate_csv is not None:
        args.candidate_csv.parent.mkdir(parents=True,exist_ok=True)
        names=("node_id","water_body","anchor_id","point_location_id","site_m",
               "baseline_bb_anchor","baseline_survey_date","planned_tnc_date",
               "current_eligibility_evidence","sampling_authority_status")
        with args.candidate_csv.open("w",newline="",encoding="utf-8") as h:
            w=csv.DictWriter(h,fieldnames=names,lineterminator="\n")
            w.writeheader()
            w.writerows(result["anchor_candidates"])
    print(json.dumps({k:result[k] for k in (
        "status","positive_nodes","complete_triplet_nodes","bay_complete_triplet_counts")},indent=2))
    if result["status"]!="PASS_ANCHOR_CANDIDATE_GEOMETRY_ONLY":
        raise SystemExit(2)

if __name__=="__main__":
    main()
