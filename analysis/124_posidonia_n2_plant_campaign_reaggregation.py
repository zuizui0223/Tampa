#!/usr/bin/env python3
"""Plant-level reaggregation of Nature 2021 Posidonia root N2-fixation data.

Mohr et al. Nature (2021) DOI: 10.1038/s41586-021-04063-4, original
Source Data Figure 2 Panel a. Each figure point is a ROOT PIECE; each
Excel column identifies a separately labelled PLANT. We aggregate root-piece
measurements within the same plant before calculating seasonal contrasts.

This is OPENED and already published data. Campaigns span 2014–2018 and
cannot be interpreted as randomized N, light or temperature treatments.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
import re
import statistics
from collections import defaultdict
from pathlib import Path

from importlib.util import spec_from_file_location, module_from_spec

HERE=Path(__file__).resolve().parents[1]
SPEC=spec_from_file_location("n2_source_gate",HERE/"analysis/123_posidonia_nfix_original_source_factor_gate.py")
SOURCE=module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE)

SOURCE_KEY="figure2"
SHA=SOURCE.FILES[SOURCE_KEY]["sha256"]
PATTERN=re.compile(r"^(April|May|June|August|September)(20\d{2})_Plant(\d+)$")
CAMPAIGN_EXPECTED={"April2016":5,"May2015":8,"May2017":3,"June2014":6,"August2016":6,"September2018":3}
METRIC="root_piece_N2_fixation_umol_N_gDW_per_day"
REPEAT=5000
SEED=2026112402

def calculate_from_raw(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Source Data Fig2 XLSX sha256 mismatch")
    titles,sheets=SOURCE.unpack(raw)
    if titles!=["Figure 2"] or len(sheets)!=1:
        raise ValueError("Unexpected original Nature Figure 2 source sheets")
    rows=next(iter(sheets.values()))
    indexed={int(x["row"]):x["cells"] for x in rows}
    if 3 not in indexed or 4 not in indexed:
        raise ValueError("Original source does not include plant label/accession rows")
    def letter(cell_ref):
        m=re.fullmatch(r"([A-Z]+)\d+",cell_ref)
        if not m:raise ValueError(f"Malformed Excel cell address: {cell_ref}")
        return m.group(1)
    columns={}
    for key,label in indexed[3].items():
        col=letter(key)
        if col=="A":
            if label!="Sample name":raise ValueError("Original row3 sample label drift")
            continue
        m=PATTERN.fullmatch(label)
        if not m:raise ValueError(f"Unrecognized campaign/plant: {label}")
        campaign=m.group(1)+m.group(2)
        columns[col]={"plant":label,"campaign":campaign,"year":int(m.group(2)),"month":m.group(1),
                      "original_root_pieces":[],"accession":indexed[4].get(col+"4")}
    if len(columns)!=31:
        raise ValueError(f"Expected original 31 separately labelled plants; got {len(columns)}")
    count=defaultdict(int)
    for plant in columns.values():count[plant["campaign"]]+=1
    if dict(count)!=CAMPAIGN_EXPECTED:
        raise ValueError("Original campaign composition changed")
    for row_num,cells in sorted(indexed.items()):
        if row_num<=4:continue
        for cell,value in cells.items():
            col=letter(cell)
            if col not in columns:continue
            try:z=float(value)
            except ValueError as exc:
                raise ValueError("Nonnumeric root-piece N2 fixation in source") from exc
            if not math.isfinite(z) or z<0:raise ValueError("Impossible negative/nonfinite fixation")
            columns[col]["original_root_pieces"].append(z)
    plant_rows=[]
    for col,rec in sorted(columns.items()):
        pieces=rec["original_root_pieces"]
        if len(pieces)==0:raise ValueError("Plant label with no measured root pieces")
        plant_rows.append({
          "plant":rec["plant"],"campaign":rec["campaign"],"root_piece_readings":len(pieces),
          "plant_mean_fixation":statistics.mean(pieces),
          "plant_median_fixation":statistics.median(pieces),
          "root_piece_fraction_positive":sum(x>0 for x in pieces)/len(pieces),
          "root_piece_zero_count":sum(x==0 for x in pieces),
          "root_piece_max_fixation":max(pieces),
          "accession":rec["accession"],
        })
    campaigns=defaultdict(list)
    for rec in plant_rows:campaigns[rec["campaign"]].append(rec)
    summary=[]
    for name in CAMPAIGN_EXPECTED:
        plants=campaigns[name]
        means=[p["plant_mean_fixation"] for p in plants]
        summary.append({
          "campaign":name,
          "plants_distinct":len(plants),
          "root_piece_readings_total":sum(p["root_piece_readings"] for p in plants),
          "plant_mean_fixation_group_mean":statistics.mean(means),
          "plant_mean_fixation_group_median":statistics.median(means),
          "plant_means_positive_count":sum(x>0 for x in means),
          "plant_median_fixation_group_median":statistics.median([p["plant_median_fixation"] for p in plants]),
          "all_root_piece_zero_counts":sum(p["root_piece_zero_count"] for p in plants),
          "plant_mean_min":min(means),"plant_mean_max":max(means),
        })
    april=[p["plant_mean_fixation"] for p in campaigns["April2016"]]
    august=[p["plant_mean_fixation"] for p in campaigns["August2016"]]
    observed=statistics.mean(august)-statistics.mean(april)
    rng=random.Random(SEED)
    sample=[]
    for i in range(REPEAT):
        am=statistics.mean(april[rng.randrange(len(april))] for j in range(len(april)))
        um=statistics.mean(august[rng.randrange(len(august))] for j in range(len(august)))
        sample.append(um-am)
    sample.sort()
    return {
        "schema":"tampa.posidonia_n2_original_plant_vs_root_piece_v1",
        "source_paper":"10.1038/s41586-021-04063-4",
        "source_fig":"Figure 2 panel a",
        "source_sha256":hashlib.sha256(raw).hexdigest(),
        "unit":METRIC,
        "plant_count":len(plant_rows),
        "root_piece_measurement_count":sum(p["root_piece_readings"] for p in plant_rows),
        "campaigns":summary,
        "plant_level_details":plant_rows,
        "same_year_2016_nonmatched_plants_apr_vs_aug":{
          "n_april_plants":len(april),
          "n_august_plants":len(august),
          "difference_aug_minus_apr_of_plant_mean_fixation":observed,
          "within_campaign_plant_bootstrap_95pct_percentile":[sample[math.floor((REPEAT-1)*.025)],sample[math.ceil((REPEAT-1)*.975)]],
          "status":"POSTHOC_UNMATCHED_PLANT_SEASONAL_ASSOCIATION_NOT_N_LIGHT_FACTORIAL",
        },
        "hard_limits":[
          "Plant-labelled columns are primary biological replicates; rows 5 onward are root-piece subsamples and not independent plants.",
          "Zero source values are retained; zeros may include nondetection and should not be interpreted as symbiont absence.",
          "Samples from different months use different plants; April and August 2016 are not longitudinal measurements of the same individual.",
          "Campaigns belong to different years (2014, 2015, 2016, 2017, 2018), confounded with season, history and method.",
          "Published study already reported summer enhancement of N2 fixation; this reaggregation is not independent replication.",
          "No experimental manipulation of light, nutrient supplementation, or loss of symbiont in these two groups.",
          "No causal carbon-cost balance or host survival, Thalassia or global cross-species interaction inferred.",
        ]
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None);a=p.parse_args()
    data=calculate_from_raw(SOURCE.fetch(SOURCE.FILES[SOURCE_KEY]["url"]))
    payload=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(payload,encoding="utf-8")
    else:print(payload,end="")

if __name__=="__main__":main()
