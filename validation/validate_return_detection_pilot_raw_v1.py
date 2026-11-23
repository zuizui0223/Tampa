#!/usr/bin/env python3
"""Fail-closed raw-record audit for OPTIONAL non-invasive Tampa detection pilot.

No historical outcome or TNC protocol is fitted/altered. A PASS means only
machine-readable field provenance, never biological closure/independence.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

FIELDS = [
    "campaign_id","node_id","water_body","mark_id","visit_id",
    "visit_local_iso","observer_id","mode","footprint_id","offset_id",
    "photo_id","was_sampled","thalassia_recorded","bb_ordinal",
    "mark_identity_verified","notes",
]
MODES={"registered_revisit","blind_photo_recheck","offset_subquadrat"}
BAYS={"Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay"}

def validate_rows(rows):
    seen=set()
    registered_photos={}
    registered=defaultdict(set)
    counters=defaultdict(int)
    for line, raw in enumerate(rows,start=2):
        if set(raw) != set(FIELDS):
            raise ValueError(f"Line {line}: schema drift")
        r={k:str(v or "").strip() for k,v in raw.items()}
        for k in ("campaign_id","node_id","water_body","mark_id","visit_id",
                  "visit_local_iso","observer_id","mode","footprint_id"):
            if not r[k]:
                raise ValueError(f"Line {line}: missing {k}")
        if r["water_body"] not in BAYS:
            raise ValueError(f"Line {line}: unknown bay")
        if r["mode"] not in MODES:
            raise ValueError(f"Line {line}: unknown mode")
        try:
            dt=datetime.fromisoformat(r["visit_local_iso"])
        except ValueError as ex:
            raise ValueError(f"Line {line}: invalid timestamp") from ex
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError(f"Line {line}: timestamp must have offset")
        for k in ("was_sampled","mark_identity_verified"):
            if r[k] not in {"0","1"}:
                raise ValueError(f"Line {line}: {k} must be 0 or 1")
        key=tuple(r[k] for k in ("campaign_id","node_id","mark_id",
                                 "visit_id","observer_id","mode",
                                 "footprint_id","offset_id"))
        if key in seen:
            raise ValueError(f"Line {line}: duplicate observer/mark/visit/mode")
        seen.add(key)
        if r["mode"]=="offset_subquadrat" and not r["offset_id"]:
            raise ValueError(f"Line {line}: offset observation lacks offset ID")
        if r["mode"]!="offset_subquadrat" and r["offset_id"]:
            raise ValueError(f"Line {line}: offset ID supplied for non-offset mode")
        if r["mode"]=="blind_photo_recheck" and not r["photo_id"]:
            raise ValueError(f"Line {line}: blind photo recheck lacks photo ID")
        if r["was_sampled"]=="0":
            if r["thalassia_recorded"] or r["bb_ordinal"] or r["photo_id"]:
                raise ValueError(f"Line {line}: unvisited/unread cannot be a zero or photo observation")
            counters["unvisited_or_unread"]+=1
            continue
        if r["thalassia_recorded"] not in {"0","1"}:
            raise ValueError(f"Line {line}: sampled record needs explicit Thalassia 0/1")
        if not r["photo_id"]:
            raise ValueError(f"Line {line}: sampled observation needs audit photo ID")
        if r["bb_ordinal"]:
            try:
                bb=float(r["bb_ordinal"])
            except ValueError as ex:
                raise ValueError(f"Line {line}: nonnumeric BB") from ex
            if not 0<=bb<=5 or (bb==0 and r["thalassia_recorded"]=="1") or (bb>0 and r["thalassia_recorded"]=="0"):
                raise ValueError(f"Line {line}: contradictory BB and focal recorded state")
        counters["sampled_photo_or_field_records"]+=1
        counters["mode_"+r["mode"]]+=1
        counters["thalassia_positive"]+=int(r["thalassia_recorded"])
        counters["thalassia_negative"]+=1-int(r["thalassia_recorded"])
        if r["mark_identity_verified"]!="1":
            counters["sampled_but_mark_unverified"]+=1
        if r["mode"]=="registered_revisit":
            visit_key=tuple(r[k] for k in ("campaign_id","node_id","mark_id",
                                             "footprint_id","visit_id"))
            photo_key=(r["campaign_id"],r["photo_id"])
            if photo_key in registered_photos and registered_photos[photo_key] != visit_key:
                raise ValueError(f"Line {line}: same field photo reused as independent field visit")
            registered_photos[photo_key]=visit_key
            if r["mark_identity_verified"]=="1":
                base=tuple(r[k] for k in ("campaign_id","node_id","mark_id","footprint_id"))
                registered[base].add(r["visit_id"])
    counters["raw_rows"]=len(rows)
    counters["verified_registered_footprints_with_two_or_more_distinct_visit_ids"]=sum(
        len(v)>=2 for v in registered.values()
    )
    return {
        "schema":"tampa.optional_detection_pilot_raw_qc_v1",
        "status":"EMPTY_TEMPLATE_NOT_READY" if not rows else "RAW_SYNTAX_QC_ONLY_NOT_FIELD_READY",
        "counts":dict(sorted(counters.items())),
        "independence_certified":False,
        "closure_certified":False,
        "biological_mechanism_identified":False,
        "notes":[
            "Same-photo blind observer reads are classification repeats, not independent field visits.",
            "Offset subquadrats are spatial subunits, not repeated detection at an identical footprint.",
            "Two different visit IDs are only candidate repeats; real independence and closure require human verification.",
            "Absent recorded Thalassia (0) is permitted only for a sampled/reviewed row; an unvisited row has blank response.",
            "No connection to frozen TNC field readiness or permission to collect outcome-bearing cores.",
        ],
    }

def validate_csv(path:Path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError("Unexpected CSV header/order")
        return validate_rows(list(reader))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("field/return_detection_pilot_raw_v1_template.csv"))
    p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    report=validate_csv(a.input)
    s=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:
        print(s,end="")

if __name__=="__main__":
    main()
