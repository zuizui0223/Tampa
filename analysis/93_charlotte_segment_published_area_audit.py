#!/usr/bin/env python3
"""Audit published Charlotte Harbor 2022/2024 eight-segment acreage (not GIS).

Source: SWFWMD March 11 2026 CHFI/SWIM presentation. Numeric labels are
rounded; source displayed deltas can differ from displayed differences by 1 acre.
"""
import argparse
import csv
import json
from pathlib import Path

SOURCE="https://chnep.wateratlas.usf.edu/upload/documents/CHFI_presentation_SWIM_20260311.pdf"
ORDER=("East Wall North","East Wall South","Myakka River","Peace River",
       "Placida","Southern Charlotte","Turtle / Bull Bay","West Wall")
TOTAL22=14913
TOTAL24=14020
REPORTED_DELTA=-893

def audit(text):
    rows=list(csv.DictReader(text.splitlines()))
    if len(rows)!=8 or tuple(r["segment"] for r in rows)!=ORDER:
        raise ValueError("SOURCE_SEGMENT_REGISTRY_DRIFT")
    d={}
    for r in rows:
        if r.get("source_id")!="SWFWMD_CHFI_20260311":
            raise ValueError("SOURCE_ID_DRIFT")
        a=int(r["acres_2022"]);b=int(r["acres_2024"])
        report=int(r["source_reported_delta_acres"])
        p=int(r["source_reported_percent"])
        if a<=0 or b<0 or abs(report-(b-a))>1:
            raise ValueError("EXCESSIVE_ROUNDING_DISCREPANCY")
        if abs(p-100*(b-a)/a)>1.1:
            raise ValueError("PERCENT_CHANGE_SOURCE_DRIFT")
        d[r["segment"]]={"2022":a,"2024":b,
            "delta_from_displayed_acres":b-a,"reported_delta_acres":report,
            "displayed_percentage":p}
    sum22=sum(q["2022"] for q in d.values())
    sum24=sum(q["2024"] for q in d.values())
    reported_sum=sum(q["reported_delta_acres"] for q in d.values())
    if abs(sum22-TOTAL22)>1 or abs(sum24-TOTAL24)>1:
        raise ValueError("BAYWIDE_SOURCE_TOTAL_DRIFT")
    if abs(reported_sum-REPORTED_DELTA)>1:
        raise ValueError("SOURCE_DELTA_TOTAL_DRIFT")
    declines=sorted(((k,-v["reported_delta_acres"]) for k,v in d.items()
                     if v["reported_delta_acres"]<0),key=lambda v:-v[1])
    contributors=declines[:3]
    return {"schema":"tampa.charlotte_2022_2024_published_segment_audit_v1",
        "evidence":"EXTERNAL_AGENCY_REPORTED_DESCRIPTIVE_AREAS_NOT_LOCAL_MEADOW_MEASUREMENTS",
        "source":SOURCE,
        "source_rounded_total":{"2022":TOTAL22,"2024":TOTAL24,
            "reported_net_delta":REPORTED_DELTA},
        "sum_of_displayed_segment_2022":sum22,
        "sum_of_displayed_segment_2024":sum24,
        "sum_of_reported_segment_deltas":reported_sum,
        "one_acre_rounding_inconsistency_disclosed":True,
        "segments":d,"top_three_reported_absolute_decline_segments":contributors,
        "share_of_reported_bay_net_loss_attributable_to_top_three_negative_deltas_percent":
           round(100*sum(v for k,v in contributors)/abs(REPORTED_DELTA),2),
        "east_wall_north_decline_acres":d["East Wall North"]["reported_delta_acres"],
        "myakka_river_reported_gain_acres":d["Myakka River"]["reported_delta_acres"],
        "limitations":"Published mapped acreages, coarse rounded labels, only eight fixed named regions; cannot infer rhizome buffering, algae-driven competition, physiological change or independent polygon replication."}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    root=Path(__file__).resolve().parents[1]
    parser.add_argument("--csv",default=str(root/"results/charlotte_segments_2022_2024_official_v1.csv"))
    parser.add_argument("--out",default=str(root/"results/generated_charlotte_segments_audit_v1.json"))
    args=parser.parse_args()
    report=audit(Path(args.csv).read_text(encoding="utf-8"))
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
