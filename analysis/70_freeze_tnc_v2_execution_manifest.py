#!/usr/bin/env python3
"""Validate/freeze a contemporaneous four-bay TNC node registry and baseline calendars.

This utility does not discover or choose nodes. It validates a human-supplied,
response-independent manifest created from the contemporaneous baseline survey
and writes the exact structures consumed by the integrated resource freeze.

Future outcome columns are forbidden.
"""
from __future__ import annotations
import argparse,csv,json,datetime as dt
from collections import defaultdict
from pathlib import Path

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
FORBIDDEN=("future","outcome","future_frequency","delta_frequency","next_year","response")
MIN_TOTAL=36
MIN_PER_BAY=6
MAX_TNC_CAMPAIGN_SPAN=28
MAX_BASELINE_OFFSET=14

def parse_date(x:str)->dt.date:
    return dt.date.fromisoformat(x)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,required=True,
      help="CSV: node_id,water_body,thalassia_positive,tnc_date,baseline_survey_date")
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    with a.manifest.open(newline="") as f:
        r=csv.DictReader(f)
        cols=[c.strip() for c in (r.fieldnames or [])]
        lower=[c.lower() for c in cols]
        bad=[c for c in cols if any(tok in c.lower() for tok in FORBIDDEN)]
        if bad:
            raise SystemExit(f"forbidden future/outcome columns present: {bad}")
        req={"node_id","water_body","thalassia_positive","tnc_date","baseline_survey_date"}
        miss=req-set(cols)
        if miss: raise SystemExit(f"missing columns: {sorted(miss)}")
        rows=list(r)

    seen=set(); eligible=[]; errors=[]
    for i,row in enumerate(rows,2):
        node=row["node_id"].strip()
        bay=row["water_body"].strip()
        if not node: errors.append(f"row {i}: blank node_id"); continue
        if node in seen: errors.append(f"duplicate node_id {node}")
        seen.add(node)
        if bay not in BAYS: errors.append(f"{node}: unsupported water_body={bay}")
        pos=str(row["thalassia_positive"]).strip().lower()
        if pos not in {"true","1","yes","false","0","no"}:
            errors.append(f"{node}: thalassia_positive must be boolean")
            continue
        if pos not in {"true","1","yes"}:
            continue
        try:
            td=parse_date(row["tnc_date"].strip())
            bd=parse_date(row["baseline_survey_date"].strip())
        except Exception:
            errors.append(f"{node}: invalid ISO date")
            continue
        if abs((td-bd).days)>MAX_BASELINE_OFFSET:
            errors.append(f"{node}: baseline survey {bd} is >{MAX_BASELINE_OFFSET} d from TNC {td}")
        eligible.append({"node_id":node,"water_body":bay,"tnc_date":td,"baseline_survey_date":bd})

    by=defaultdict(list)
    for x in eligible: by[x["water_body"]].append(x)
    counts={b:len(by[b]) for b in BAYS}
    if len(eligible)<MIN_TOTAL:
        errors.append(f"eligible total {len(eligible)} < {MIN_TOTAL}")
    for b in BAYS:
        if counts[b]<MIN_PER_BAY:
            errors.append(f"{b}: eligible nodes {counts[b]} < {MIN_PER_BAY}")

    dates=[x["tnc_date"] for x in eligible]
    if dates:
        start=min(dates); end=max(dates); span=(end-start).days
        if span>MAX_TNC_CAMPAIGN_SPAN:
            errors.append(f"TNC campaign span {span} d > {MAX_TNC_CAMPAIGN_SPAN}")
    else:
        start=end=None;span=None

    result={
      "schema":"tampa.tnc_v2_contemporaneous_execution_manifest_v1",
      "status":"PASS_EXECUTION_MANIFEST" if not errors else "STOP_EXECUTION_MANIFEST",
      "response_independent":True,
      "errors":errors,
      "counts_by_bay":counts,
      "total_eligible_nodes":len(eligible),
      "tnc_campaign":{
        "start_date":start.isoformat() if start else None,
        "end_date":end.isoformat() if end else None,
        "span_days":span,
        "maximum_allowed_span_days":MAX_TNC_CAMPAIGN_SPAN
      },
      "baseline_alignment_days_each_side":MAX_BASELINE_OFFSET,
      "resource_freeze_payload":None,
      "claim_boundary":[
        "This utility validates a supplied contemporaneous execution manifest; it does not choose nodes.",
        "Only baseline Thalassia status and logistics dates are allowed. Future response fields are forbidden.",
        "Passing the manifest is execution readiness, not ecological evidence."
      ]
    }
    if not errors:
        result["resource_freeze_payload"]={
          "final_four_bay_tnc_nodes_by_bay":{
            b:[x["node_id"] for x in by[b]] for b in BAYS
          },
          "four_bay_authoritative_tnc_baseline_calendar":{
            x["node_id"]:x["tnc_date"].isoformat() for x in eligible
          },
          "four_bay_baseline_transect_calendar":{
            x["node_id"]:x["baseline_survey_date"].isoformat() for x in eligible
          },
          "tnc_v2_precollection_campaign_start_date":start.isoformat(),
          "tnc_v2_precollection_campaign_end_date":end.isoformat()
        }

    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if errors: raise SystemExit(2)

if __name__=="__main__":
    main()
