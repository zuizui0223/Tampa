#!/usr/bin/env python3
"""Exploratory global seagrass below/above biomass state coupling.

The estimands are frozen by this code before viewing the source outcomes. One
source row is not an independent study; first-level summaries are separately
reported within original publication reference strings. Any claim that
background carbon storage or rhizome TNC was measured is strictly forbidden.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "macro_source_reader",ROOT/"analysis"/"114_global_seagrass_929968_feasibility.py"
)
SOURCE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE)

MIN_GENUS_ROWS=30
MIN_GENUS_REFS=5
MIN_REGION_ROWS=30
MIN_REGION_REFS=5
MIN_MIDDLE_ROWS=15
MIN_MIDDLE_REFS=4


def variance(values):
    return statistics.variance(values) if len(values)>1 else None


def quantile(values,q):
    return SOURCE.quantile(values,q)


def grouped_summary(records,group_key,min_rows,min_refs):
    groups=defaultdict(list)
    for r in records:
        groups[r[group_key]].append(r)
    out=[]
    for group, members in groups.items():
        ref_groups=defaultdict(list)
        for x in members:
            ref_groups[x["ref"]].append(x["log_ratio"])
        study_medians=[statistics.median(vals) for vals in ref_groups.values()]
        support=len(members)>=min_rows and len(ref_groups)>=min_refs
        out.append({
            "group":group,"paired_observation_rows":len(members),
            "raw_reference_string_clusters_not_verified_unique_papers":len(ref_groups),
            "supported_descriptive_coverage_gate":support,
            "median_row_below_above_ratio":statistics.median([x["ratio"] for x in members]),
            "median_reference_equal_below_above_ratio":(
                math.exp(statistics.median(study_medians))
                if support else None
            ),
            "reference_equal_log_ratio_iqr":[
                quantile(study_medians,.25),quantile(study_medians,.75)
            ] if support else None,
        })
    return sorted(out,key=lambda x:(-x["paired_observation_rows"],x["group"]))


def records_from_source(rows, keys):
    records=[]
    excluded={"missing_or_nonpositive_above":0,
              "missing_or_nonpositive_below":0,
              "invalid_reference_genus_or_bioregion":0}
    for row in rows:
        ref=str(row[keys["ref"]] or "").strip()
        genus=str(row[keys["genus"]] or "").strip()
        region=str(row[keys["region"]] or "").strip()
        habitat=str(row[keys["habitat"]] or "").strip()
        a=SOURCE.parse_num(row[keys["ag"]])
        b=SOURCE.parse_num(row[keys["bg"]])
        if not ref or not genus or not region:
            excluded["invalid_reference_genus_or_bioregion"]+=1
            continue
        if a is None or a<=0:
            excluded["missing_or_nonpositive_above"]+=1
            continue
        if b is None or b<=0:
            excluded["missing_or_nonpositive_below"]+=1
            continue
        # Negative raw values cannot be made positive by transformation.
        ratio=b/a
        if ratio<=0 or not math.isfinite(ratio):
            raise ValueError("Impossible finite positive biomass allocation ratio")
        records.append({
            "ref":ref,"genus":genus,"region":region,"habitat":habitat,
            "above":a,"below":b,"ratio":ratio,"log_ratio":math.log(ratio)
        })
    return records,excluded


def reference_central_aboveground_spread(records):
    """40th-60th percent AG per genus, then BG range within same genus.

    This fixed central-band diagnostic is descriptive conditional heterogeneity
    rather than a physiological reserve test. Clusters are reference strings.
    """
    groups=defaultdict(list)
    for r in records: groups[r["genus"]].append(r)
    out=[]
    for genus,rs in groups.items():
        aboves=[r["above"] for r in rs]
        lo,hi=quantile(aboves,.4),quantile(aboves,.6)
        middle=[r for r in rs if lo<=r["above"]<=hi]
        refs={r["ref"] for r in middle}
        support=len(middle)>=MIN_MIDDLE_ROWS and len(refs)>=MIN_MIDDLE_REFS
        bgs=[r["below"] for r in middle]
        q25,q75=quantile(bgs,.25),quantile(bgs,.75)
        out.append({
            "genus":genus,
            "all_paired_rows":len(rs),
            "central_above_quantiles_g_m2":[lo,hi],
            "central_band_same_row_records":len(middle),
            "central_band_raw_reference_strings":len(refs),
            "coverage_gate":support,
            "central_band_bg_q25_g_m2":q25 if support else None,
            "central_band_bg_median_g_m2":statistics.median(bgs) if support else None,
            "central_band_bg_q75_g_m2":q75 if support else None,
            "central_band_bg_q75_to_q25":q75/q25 if support and q25>0 else None,
        })
    return sorted(out,key=lambda x:(-x["all_paired_rows"],x["genus"]))


def execute(raw):
    rows,keys,source_header=SOURCE.tabular(raw)
    records,exclusions=records_from_source(rows,keys)
    refs=defaultdict(list)
    for r in records: refs[r["ref"]].append(r["log_ratio"])
    ref_medians=[statistics.median(x) for x in refs.values()]
    paired_ratios=[r["ratio"] for r in records]
    overall={
        "same_row_positive_above_below_records":len(records),
        "raw_reference_string_clusters":len(refs),
        "median_paired_below_above_ratio":statistics.median(paired_ratios) if paired_ratios else None,
        "reference_equal_median_ratio":math.exp(statistics.median(ref_medians)) if ref_medians else None,
        "reference_equal_q25_q75_log_ratio":[quantile(ref_medians,.25),quantile(ref_medians,.75)]
            if ref_medians else None,
        "excluded_row_flags_not_disjoint":exclusions,
    }
    return {
        "schema":"tampa.global_seagrass_allocation_conditioned_spread_v1",
        "evidence_class":"exploratory_global_cross_sectional_literature_compilation",
        "source":{"doi":SOURCE.DOI,"byte_sha256":SOURCE.hashlib.sha256(raw).hexdigest(),
                  "header":source_header},
        "overall":overall,
        "genus":grouped_summary(records,"genus",MIN_GENUS_ROWS,MIN_GENUS_REFS),
        "bioregion":grouped_summary(records,"region",MIN_REGION_ROWS,MIN_REGION_REFS),
        "within_genus_central_aboveground_conditioned_bg_spread":
            reference_central_aboveground_spread(records),
        "hard_interpretation_stops":[
            "Positive AG and BG biomass must be co-reported in exactly one source row.",
            "A raw reference string is a provisional publication cluster; bibliographic corruption may split studies.",
            "Unequal measurement coverage can induce selection bias: no missing-as-zero.",
            "The source is a literature compilation; neither simultaneous quadrat identity nor matched season is independently audited.",
            "Measured belowground biomass is NOT rhizome carbohydrates or physiological TNC.",
            "Study-equal medians and central-bin spreads are descriptive, not a causal macroecological coefficient.",
            "No sampled true species absences, dynamic site persistence, longitudinal cover thinning or ecosystem functions are inferred.",
            "Do not treat a 2025 published global genus/bioregion analysis as unreported prior work.",
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=None)
    args=p.parse_args()
    raw=SOURCE.download()
    data=execute(raw)
    s=json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(s,encoding="utf-8")
    else:
        print(s,end="")


if __name__=="__main__":
    main()
