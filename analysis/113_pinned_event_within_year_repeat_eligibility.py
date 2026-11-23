#!/usr/bin/env python3
"""Response-blind repeat-survey eligibility audit for the pinned TBEP Event table.

Uses ONLY Event rows (Transect/Point metadata). No Occurrence or eMoF,
no Thalassia responses, no model refitting, and no detection estimates.
The 1497 eligible visits / 1480 node-years must be reconstructed exactly.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
SOURCE_URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc/event.csv"
SOURCE_BYTES=24654717
SOURCE_BLOB="583b4d4e328290ab065346579eb4f29f03ea0f99"
HEADER=[
    "eventID","parentEventID","eventType","eventDate","year","month","day",
    "decimalLatitude","decimalLongitude","geodeticDatum","minimumDepthInMeters",
    "maximumDepthInMeters","country","countryCode","stateProvince","waterBody",
    "locality","locationID","samplingProtocol","institutionCode","datasetName",
    "datasetID","license","locationRemarks",
]


def sha_blob(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def download()->bytes:
    req=Request(SOURCE_URL,headers={
        "Accept-Encoding":"identity",
        "User-Agent":"Tampa-source-only-repeat-eligibility/1.0"
    })
    with urlopen(req,timeout=180) as r:
        data=r.read(SOURCE_BYTES+1)
    if len(data)!=SOURCE_BYTES or sha_blob(data)!=SOURCE_BLOB:
        raise RuntimeError("Pinned Event byte size or Git blob identity has changed")
    return data


def source_index(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames != HEADER:
        raise RuntimeError("Event schema changed")
    parents={}
    pointmarks=defaultdict(set)
    point_events=defaultdict(int)
    raw_child_count=0
    for row in reader:
        kind=row["eventType"].strip()
        eid=row["eventID"].strip()
        if not eid:
            raise RuntimeError("blank eventID")
        if kind=="Transect":
            if eid in parents:
                raise RuntimeError("duplicate transect eventID")
            dt=date.fromisoformat(row["eventDate"].strip()[:10])
            if row["year"].strip() and int(row["year"]) != dt.year:
                raise RuntimeError("Event year/date mismatch")
            node=row["locationID"].strip()
            if not node:
                raise RuntimeError("transect without stable locationID")
            parents[eid]={
                "node_id":node,"year":dt.year,"date":dt.isoformat(),
                "water_body":row["waterBody"].strip(),
                "protocol":row["samplingProtocol"].strip(),
                "institution":row["institutionCode"].strip(),
                "eventID":eid,
            }
        elif kind=="Point":
            raw_child_count+=1
            pid=row["parentEventID"].strip()
            if not pid:
                raise RuntimeError("point without transect parentEventID")
            mark=row["locationID"].strip()
            if not mark:
                raise RuntimeError("point without locationID")
            point_events[pid]+=1
            pointmarks[pid].add(mark)
        else:
            raise RuntimeError(f"unexpected eventType {kind}")
    if not set(point_events).issubset(parents):
        raise RuntimeError("orphan point parents")
    eligible={
        k:dict(v,child_count=point_events[k],unique_marks=len(pointmarks[k]))
        for k,v in parents.items() if point_events[k]>=3
    }
    return eligible, pointmarks, {
        "all_transect_events":len(parents),
        "all_point_events":raw_child_count,
        "eligible_transect_visits":len(eligible),
        "eligible_unique_nodes":len({v["node_id"] for v in eligible.values()}),
        "eligible_node_years":len({(v["node_id"],v["year"]) for v in eligible.values()}),
    }


def audit(eligible:dict, marksets:dict)->dict:
    by=defaultdict(list)
    for k,v in eligible.items():
        by[(v["node_id"],v["year"])].append(v)
    groups=[]
    sum_extra=0
    for (node,year),g in sorted(by.items()):
        if len(g)<2:
            continue
        sum_extra+=len(g)-1
        dates=sorted({date.fromisoformat(v["date"]) for v in g})
        by_date=defaultdict(set)
        for v in g:
            by_date[v["date"]].update(marksets[v["eventID"]])
        overlaps=[]
        for a,b in itertools.combinations(g,2):
            ma=marksets[a["eventID"]]
            mb=marksets[b["eventID"]]
            shared=len(ma & mb)
            day_gap=abs((date.fromisoformat(a["date"])-date.fromisoformat(b["date"])).days)
            overlaps.append({
                "date_a":a["date"],"date_b":b["date"],"day_gap":day_gap,
                "shared_mark_ids":shared,
                "marks_a":len(ma),"marks_b":len(mb),
                "jaccard_mark_roster":shared/len(ma|mb) if (ma|mb) else 0,
                "distinct_dates":day_gap>0,
                "candidate_mark_revisits_on_different_dates":bool(day_gap>0 and shared>0),
            })
        all_marks=set().union(*[marksets[x["eventID"]] for x in g])
        mark_dates={m:{v["date"] for v in g if m in marksets[v["eventID"]]}
                    for m in all_marks}
        distinct_date_marks=sum(len(d)>=2 for d in mark_dates.values())
        candidate_gap=[p["day_gap"] for p in overlaps if p["candidate_mark_revisits_on_different_dates"]]
        protocols=sorted({x["protocol"] for x in g})
        institutions=sorted({x["institution"] for x in g})
        bodies=sorted({x["water_body"] for x in g})
        groups.append({
            "node_id":node,"year":year,"visits":len(g),"extra_visits":len(g)-1,
            "distinct_parent_event_dates":len(dates),
            "all_parent_dates":[d.isoformat() for d in dates],
            "event_ids":[x["eventID"] for x in sorted(g,key=lambda x:(x["date"],x["eventID"]))],
            "water_bodies":bodies,"sampling_protocols":protocols,
            "institution_codes":institutions,
            "all_unique_sampled_mark_ids":len(all_marks),
            "marks_repeated_across_distinct_parent_dates":distinct_date_marks,
            "pair_count":len(overlaps),
            "candidate_distinct_date_pair_count":len(candidate_gap),
            "candidate_pairs_with_7_day_gap_or_less":sum(x<=7 for x in candidate_gap),
            "candidate_pairs_with_14_day_gap_or_less":sum(x<=14 for x in candidate_gap),
            "candidate_pairs_with_30_day_gap_or_less":sum(x<=30 for x in candidate_gap),
            "pair_metadata":overlaps,
            "valid_independent_detection_replicates_verified":False,
        })
    n_meta=sum(x["pair_count"] for x in groups)
    summary={
        "eligible_visits":len(eligible),
        "eligible_node_years":len(by),
        "eligible_nodes":len({x["node_id"] for x in eligible.values()}),
        "extra_visits_beyond_first_node_year":sum_extra,
        "node_year_groups_with_multiple_eligible_visits":len(groups),
        "node_year_groups_with_multiple_parent_dates":sum(x["distinct_parent_event_dates"]>=2 for x in groups),
        "node_year_groups_with_repeated_marks_across_distinct_dates":sum(x["marks_repeated_across_distinct_parent_dates"]>0 for x in groups),
        "total_marks_repeated_across_distinct_dates_sum_across_node_years":sum(x["marks_repeated_across_distinct_parent_dates"] for x in groups),
        "parent_event_visit_pairs_same_node_year":n_meta,
        "distinct_date_pairs_sharing_mark_ids":sum(x["candidate_distinct_date_pair_count"] for x in groups),
        "within_7_days_pairs":sum(x["candidate_pairs_with_7_day_gap_or_less"] for x in groups),
        "within_14_days_pairs":sum(x["candidate_pairs_with_14_day_gap_or_less"] for x in groups),
        "within_30_days_pairs":sum(x["candidate_pairs_with_30_day_gap_or_less"] for x in groups),
    }
    if sum_extra!=len(eligible)-len(by):
        raise AssertionError("Annualization identity mismatch")
    return {"summary":summary,"repeated_node_year_details":groups}


def run_metadata_only(data:bytes)->dict:
    eligible, marks, registry=source_index(data)
    if registry["eligible_transect_visits"]!=1497 or registry["eligible_node_years"]!=1480 or registry["eligible_unique_nodes"]!=71:
        raise RuntimeError(f"Source eligibility drift: {registry}")
    out=audit(eligible,marks)
    if out["summary"]["extra_visits_beyond_first_node_year"]!=17:
        raise RuntimeError("Expected frozen surplus of exactly 17 eligible visits")
    return {
        "schema":"tampa.pinned_source_within_year_repeat_eligibility_audit_v1",
        "evidence_class":"response_blind_source_metadata_audit_not_detection_estimation",
        "source":{"url":SOURCE_URL,"commit":COMMIT,"size":SOURCE_BYTES,"blob":SOURCE_BLOB,
                  "sha256":hashlib.sha256(data).hexdigest()},
        "registry":registry,
        **out,
        "hard_boundaries":[
            "No Occurrence or eMoF observations are read; no species recorded/non-recorded outcomes inferred.",
            "Distinct parent event dates can be administrative/default dates; real survey timestamps are not verified.",
            "Overlapping Point locationIDs are candidate sampled-mark roster repeats, not identical photographed quadrat footprints.",
            "Same-day multiple parent events cannot be counted as independent temporal field revisits.",
            "Metadata-only dates and marks do not establish closure, conditional independence, observer identity, or sampling comparability.",
            "An eligible node-year with two visits provides at most one additional visit, not automatically independent detections.",
            "No detection probability, demographic loss, true recovery, TNC mechanism or posterior absence is estimated.",
            "This is a historical feasibility audit only, not permission or redefinition of prospective TNC-v2 protocol.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=None)
    args=p.parse_args()
    output=run_metadata_only(download())
    text=json.dumps(output,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding="utf-8")
    else:
        print(text,end="")


if __name__=="__main__":
    main()
