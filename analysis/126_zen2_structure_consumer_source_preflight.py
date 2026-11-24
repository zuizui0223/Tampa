#!/usr/bin/env python3
"""Exact original-source preflight for two *different* ZEN2 seagrass studies.

ZEN2 2015 17-site experiment: eelgrass edge/interior by ambient/50/80% thinning
and tethered consumer 24-hour predation status.
ZEN2 2014 50-site survey: simultaneous biological structure and consumers.

Original-data result is exploratory and already analyzed in Hovel et al.
Ecology (2021) 10.1002/ecy.3316. This does not independently validate it.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

SOURCES={
  "ZEN2_thinning_2015":{
    "url":"https://datadocs.bco-dmo.org/dataset/724015/file/l880lRkF2gvLEO/crustacean_survival.csv",
    "doi":"10.26008/1912/bco-dmo.724015.2",
    "paper_doi":"10.1002/ecy.3316",
    "expected_minimum_headers":["Site","Patch_location","Shoot_reduction","Status"],
    "max_bytes":900000,
  },
  "ZEN2_survey_2014":{
    "url":"https://datadocs.bco-dmo.org/dataset/712069/file/1VVMOrXtMO4KM1/ZEN2_survey_sorted.csv",
    "doi":"10.26008/1912/bco-dmo.712069.1",
    "paper_doi":"10.1111/ele.12448",
    "expected_minimum_headers":[],
    "max_bytes":180000,
  },
}

def source_bytes(url,cap):
    if not url.startswith("https://datadocs.bco-dmo.org/dataset/"):
        raise ValueError("Unexpected original source hostname")
    req=Request(url,headers={"Accept-Encoding":"identity",
                             "User-Agent":"Tampa-ZEN2-source-only-2026/1.0"})
    with urlopen(req,timeout=90) as f:
        b=f.read(cap+1)
    if len(b)>cap:raise ValueError("Source exceeds fixed byte cap")
    return b

def inspect_csv(raw:bytes,kind:str):
    if len(raw)<100:raise ValueError("Unexpected source size")
    t=raw.decode("utf-8-sig")
    r=csv.DictReader(io.StringIO(t))
    head=r.fieldnames
    if not head or len(set(head))!=len(head):
        raise ValueError("CSV headers missing or duplicate")
    expected=SOURCES[kind]["expected_minimum_headers"]
    if not set(expected).issubset(set(head)):
        raise ValueError("Source does not contain required original data semantics")
    rows=list(r)
    if any(None in row for row in rows):
        raise ValueError("Malformed CSV row")
    if len(rows)<20:raise ValueError("Truncated experimental source")
    candidate={
        "site":[x for x in head if x.lower() in ("site","site_code","sitecode","site_name") or re.search("site",x,re.I)],
        "treatment":[x for x in head if re.search(r"shoot|reduct|thin|treat|patch|edge|interior|location|block",x,re.I)],
        "predation":[x for x in head if re.search(r"status|alive|consum|predat|surviv|mortality",x,re.I)],
        "plant_structure":[x for x in head if re.search(r"shoot|zoster|biomass|biom|cover|density",x,re.I)],
        "consumers":[x for x in head if re.search(r"crust|graz|epiphyt|epibiont|predator|amp|isopod",x,re.I)],
        "replication":[x for x in head if re.search(r"plot|trial|round|rep|tether|id|block|taxon",x,re.I)],
    }
    label_columns=sorted(set(candidate["site"]+candidate["treatment"]+candidate["predation"]))
    labels={}
    for k in label_columns:
        levels=Counter((str(row.get(k) or "").strip() or "<EMPTY>") for row in rows)
        labels[k]={"distinct":len(levels),"top_values":dict(levels.most_common(24))}
    missing={
        x:sum(str(row.get(x) or "").strip().lower() in ("","na","n/a","nan","null","-999") for row in rows)
        for x in head
    }
    return {
        "source_kind":kind,
        "schema":head,
        "row_count":len(rows),
        "candidate_columns":candidate,
        "factor_levels_and_counts":labels,
        "missing_counts":missing,
        "source_first_row_map":{k:rows[0][k] for k in head},
        "raw_outcome_effect_estimable_in_this_gate":False,
    }

def report():
    outputs={}
    for name,spec in SOURCES.items():
        try:
            raw=source_bytes(spec["url"],spec["max_bytes"])
            meta=inspect_csv(raw,name)
            outputs[name]={
                "status":"ORIGINAL_SOURCE_RETRIEVED_SCHEMA_PROFILED",
                "source_doi":spec["doi"],"source_url":spec["url"],
                "byte_sha256":hashlib.sha256(raw).hexdigest(),
                "source_file_bytes":len(raw),
                "profile":meta,
            }
        except (ValueError,OSError,UnicodeError,TimeoutError) as e:
            outputs[name]={
                "status":"ORIGINAL_SOURCE_OR_SCHEMA_STOP",
                "source_doi":spec["doi"],"source_url":spec["url"],
                "reason":f"{type(e).__name__}: {str(e)[:240]}",
                "new_ecological_effects":None,
            }
    return {
        "schema":"tampa.zen2_structure_consumer_source_preflight_v1",
        "evidence_class":"original_public_data_opened_for_exploratory_reanalysis",
        "separate_original_studies":outputs,
        "claim_boundaries":[
            "2014 survey and 2015 experiment are not the same plots, times or treatment.",
            "2015 tethered-predation endpoint was previously investigated in Hovel et al. 2021.",
            "Tethered consumer mortality is not autonomous prey survival nor actual grazer effect on eelgrass.",
            "2015 block/trial/organism rows are pseudoreplicates if treated as independent sites.",
            "2014 survey is observational; joint biomass and consumers do not establish reciprocity.",
            "Only a prospectively repeated partner-by-plant intervention can test feedback strength directly.",
        ],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None);a=p.parse_args()
    s=json.dumps(report(),sort_keys=True,ensure_ascii=False,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
