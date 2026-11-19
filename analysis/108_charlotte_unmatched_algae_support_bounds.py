#!/usr/bin/env python3
"""Transparent worst-case support bounds for mapped sea/algae retention contrasts.

Input is the prior, successful source-verified patch-size and spatial support
table. No live biology/GIS access; no refitting, p-values or bootstrap CIs.

The hypothetical target is algae-area-weighted (seagrass same broad 2024 map
class retention minus attached-algae same class retention) over every 2022
algae size/grid stratum. Sea retention in unsupported strata is NOT identified;
let its feasible fraction range [0,1]. Actual algae retention is observed.
The resulting bounds are *deterministic missing-reference sensitivity bounds*,
not a CI or a causal partially identified treatment effect.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"results/charlotte_patch_size_spatial_support_verified_20261119.json"
EXPECTED_SCHEMA="tampa.charlotte_patch_size_space_support_verified_release_v1"
EXPECTED_DIGEST="sha256:fff3f0961ca079576e59940d5777186949bfb80a6ee9e2308ad56db91baa8bc0"
EXPECTED_ARCHIVE="sha256:fb22443b6d0b8bf1a86cf82670342adf18c6d76971074b65f7cbafbfe9db1bea"
KEYS={
 "size_stratification":"2022 source patch-size bins",
 "five_kilometre_representative_point_grid":"5km source representative-point geography",
 "size_by_grid_stratification":"joint patch-size and 5km geography",
}
TOL_AC=0.025

class Stop(ValueError):pass

def valid_number(x,field):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):
        raise Stop("INVALID_NUMERIC_FIELD:"+field)
    return float(x)

def summarize_frozen(release):
    if release.get("schema")!=EXPECTED_SCHEMA:
        raise Stop("SOURCE_RELEASE_SCHEMA_MISMATCH")
    audit=release.get("audited_ci",{})
    if (audit.get("run_id")!=44455648817 or
        audit.get("artifact_zip_sha256")!=EXPECTED_DIGEST or
        audit.get("source_original_zip_digest")!=EXPECTED_ARCHIVE or
        audit.get("completed_success") is not True):
        raise Stop("SOURCE_ARCHIVE_PROVENANCE_NOT_VERIFIED")
    data=release.get("report",{})
    if data.get("status")!="SOURCE_ARCHIVE_VERIFIED_POSTHOC_DESCRIPTIVE_SIZE_AND_GRID_SUPPORT":
        raise Stop("NON_FINAL_SOURCE_REPORT")
    original=data.get("unmatched_original",{}).get("by_2022_class",{})
    algae=original.get("attached_macroalgae",{})
    total=valid_number(algae.get("source_area_acres"),"source_total")
    total_ret=valid_number(algae.get("retained_area_acres"),"source_retained")
    if total<=0 or not (0<=total_ret<=total):
        raise Stop("IMPOSSIBLE_ALGAE_SOURCE_AREA")
    if abs(total-674.188)>.003 or abs(total_ret-245.158)>.003:
        raise Stop("FROZEN_ORIGINAL_CLASS_TOTALS_CHANGED")
    return data,total,total_ret

def bounds(section,total,total_ret):
    cells=section.get("cell_data")
    if not isinstance(cells,dict) or not cells:
        raise Stop("MISSING_SOURCE_STRATA")
    supported=[]
    unsupported=[]
    all_algae_area=all_algae_retained=0.
    for key,c in cells.items():
        try:
            algae=c["attached_macroalgae"]
            sea=c["seagrass"]
            A=valid_number(algae["source_area_acres"],key+":algae_area")
            R=valid_number(algae["retained_area_acres"],key+":algae_retained")
            n=algae["patches"]
            if A<0 or R<-.002 or R>A+TOL_AC or not isinstance(n,int) or n<0:
                raise Stop("UNPHYSICAL_SOURCE_CELL:"+key)
            all_algae_area+=A
            all_algae_retained+=R
            if c.get("in_common_support") is True:
                sea_rate=valid_number(sea["same_class_rate_percent"],key+":sea_rate")
                algae_rate=valid_number(algae["same_class_rate_percent"],key+":algae_rate")
                if not (0<=sea_rate<=100 and 0<=algae_rate<=100) or A<=0:
                    raise Stop("SUPPORTED_RATE_OUTSIDE_UNIT_INTERVAL:"+key)
                supported.append({"stratum":str(key),"algae_area":A,"algae_retained":R,
                                  "sea_rate":sea_rate,"algae_rate":algae_rate,
                                  "class_difference_points":sea_rate-algae_rate})
            elif c.get("in_common_support") is False:
                unsupported.append({"stratum":str(key),"algae_area":A,
                                    "algae_retained":R,"algae_patch_count":n,
                                    "seagrass_patch_count":sea.get("patches")})
            else:
                raise Stop("UNDEFINED_COMMON_SUPPORT_FLAG:"+key)
        except (TypeError,KeyError) as e:
            raise Stop("BAD_SOURCE_STRATUM:"+str(key)) from e
    if abs(all_algae_area-total)>TOL_AC or abs(all_algae_retained-total_ret)>TOL_AC:
        raise Stop("MAP_ALGAE_AREA_OR_RETENTION_MASS_BALANCE_FAILED")
    matched_area=sum(r["algae_area"] for r in supported)
    matched_ret=sum(r["algae_retained"] for r in supported)
    outside_area=max(0.,total-matched_area)
    outside_ret=max(0.,total_ret-matched_ret)
    if outside_ret>outside_area+TOL_AC:
        raise Stop("UNSUPPORTED_ALGAE_RETENTION_EXCEEDS_AREA")
    if abs(matched_area-valid_number(section.get("matched_algae_area_acres"),"matched_algae_area"))>TOL_AC:
        raise Stop("PREVIOUS_MATCHED_ALGAE_AREA_CHANGED")

    matched_gap_weighted_area=sum(r["algae_area"]*r["class_difference_points"]/100 for r in supported)
    if matched_area>0:
        matched_contrast=100*matched_gap_weighted_area/matched_area
        original_conditional=section.get("weighted_seagrass_minus_algae_points")
        if original_conditional is None or abs(matched_contrast-float(original_conditional))>.035:
            raise Stop("FROZEN_MATCHED_CONTRAST_NOT_REPRODUCED")
        weights=[r["algae_area"]/matched_area for r in supported]
        effective_n=1/sum(x*x for x in weights)
        leave=[]
        if len(supported)>1:
            for r in supported:
                remainder=matched_area-r["algae_area"]
                if remainder<=0:continue
                revised=100*(matched_gap_weighted_area-
                        r["algae_area"]*r["class_difference_points"]/100)/remainder
                leave.append({"stratum":r["stratum"],
                              "omitted_source_algae_acres":round(r["algae_area"],3),
                              "recomputed_conditional_contrast_points":round(revised,3)})
        neg_cells=[r for r in supported if r["class_difference_points"]<0]
    else:
        matched_contrast=None
        effective_n=None
        leave=[]
        neg_cells=[]

    # An explicitly geographical *leave-one-entire-5km-cell-out* audit for
    # size-by-grid strata. Removing only one size-cell can understate spatial
    # leverage because multiple strata may belong to the same 5km grid.
    geographical_leave=[]
    if supported and all("|" in r["stratum"] for r in supported):
        grid_names=sorted({r["stratum"].split("|",1)[1] for r in supported})
        for grid in grid_names:
            excluded=[r for r in supported if r["stratum"].split("|",1)[1]==grid]
            omitted_area=sum(r["algae_area"] for r in excluded)
            omitted_gap_area=sum(r["algae_area"]*r["class_difference_points"]/100 for r in excluded)
            remain_area=matched_area-omitted_area
            if remain_area<=0:continue
            geographical_leave.append({
              "grid_id":grid,"omitted_strata":len(excluded),
              "omitted_matched_algae_area_acres":round(omitted_area,3),
              "omitted_matched_algae_area_percent":round(100*omitted_area/matched_area,3),
              "remaining_matched_algae_gap_points":round(
                  100*(matched_gap_weighted_area-omitted_gap_area)/remain_area,3)
            })
    # Sharp algebraic envelope under ONLY the 0-100% unknown seagrass
    # same-map-class retention in unsupported strata. Observed algae same-class
    # retention there is known and never replaced by guessed values.
    #
    # matched contribution + unsupported area*(unobserved sea rate - observed
    # algae rate), all divided by TOTAL ORIGINAL 2022 ALGAE SOURCE AREA.
    lo=100*(matched_gap_weighted_area-outside_ret)/total
    hi=100*(matched_gap_weighted_area+outside_area-outside_ret)/total
    if lo>hi+.002:
        raise Stop("PARTIAL_IDENTIFICATION_BOUNDS_REVERSED")
    if not(-100.001<=lo<=100.001 and -100.001<=hi<=100.001):
        raise Stop("IMPOSSIBLE_EFFECTIVE_BOUNDS")
    covered=100*matched_area/total
    if abs(covered-valid_number(section.get("algae_source_area_with_comparable_seagrass_percent"),"matched_percent"))>.05:
        raise Stop("COMMON_SUPPORT_FRACTION_MISMATCH")
    return {
        "source_area_acres":round(total,3),
        "source_retained_area_acres":round(total_ret,3),
        "matched_algae_acres":round(matched_area,3),
        "unsupported_algae_acres":round(outside_area,3),
        "unsupported_observed_algae_retained_acres":round(outside_ret,3),
        "matched_algae_area_percent":round(covered,3),
        "matched_n_strata":len(supported),
        "nonmatched_n_strata":len(unsupported),
        "conditional_original_matched_class_gap_points":None if matched_contrast is None else round(matched_contrast,3),
        "full_algae_area_hypothetical_comparator_gap_lower_points":round(lo,3),
        "full_algae_area_hypothetical_comparator_gap_upper_points":round(hi,3),
        "zero_inside_feasible_envelope":lo<=0<=hi,
        "algebra":"matched algae-area-weighted class gap + unsupported algae-area*(unknown seagrass retention in [0,1] - observed algae retention) over total algae area",
        "not_a_confidence_interval":True,
        "not_a_causal_identification_set":True,
        "whole_area_adjusted_effect_is_estimable":bool(section.get("can_generalize_to_full_algae_area")),
        "weighted_effective_n_matched_strata":None if effective_n is None else round(effective_n,3),
        "reverse_direction_matched_strata_count":len(neg_cells),
        "reverse_direction_algae_area_percent_of_matched":round(100*sum(x["algae_area"] for x in neg_cells)/matched_area,3) if matched_area else None,
        "leave_one_entire_5km_grid_out_results":geographical_leave,
        "leave_one_entire_5km_grid_out_gap_range_points":[
            round(min(x["remaining_matched_algae_gap_points"] for x in geographical_leave),3),
            round(max(x["remaining_matched_algae_gap_points"] for x in geographical_leave),3)
        ] if geographical_leave else None,
        "leave_one_5km_grid_out_can_reverse_conditional_sign":(
            any(x["remaining_matched_algae_gap_points"]<0 for x in geographical_leave)
            and matched_contrast is not None and matched_contrast>0),
        "leave_one_matched_stratum_out_conditional_gap_range_points":
           [round(min(x["recomputed_conditional_contrast_points"] for x in leave),3),
            round(max(x["recomputed_conditional_contrast_points"] for x in leave),3)] if leave else None,
        "largest_matched_algae_weight_strata":[
            {"stratum":r["stratum"],"algae_area_acres":round(r["algae_area"],3),
             "share_of_matched_algae_area_percent":round(100*r["algae_area"]/matched_area,3),
             "class_gap_points":round(r["class_difference_points"],3)}
            for r in sorted(supported,key=lambda x:-x["algae_area"])[:5]],
        "largest_unsupported_algae_strata":[
            {"stratum":r["stratum"],"algae_area_acres":round(r["algae_area"],3),
             "observed_algae_retained_acres":round(r["algae_retained"],3),
             "comparable_seagrass_patch_count":r["seagrass_patch_count"]}
            for r in sorted(unsupported,key=lambda x:-x["algae_area"])[:5]],
        "scientific_scope":"The class contrast is a map-category area sensitivity, not measured biological persistence. Unmatched cells lack same-stratum source-class support, not necessarily a coherent physically manipulable seagrass potential outcome."
    }

def evaluate(release):
    data,total,ret=summarize_frozen(release)
    result={KEYS[k]:bounds(data[k],total,ret) for k in KEYS}
    return {
      "schema":"tampa.charlotte_unmatched_algae_reference_bounds_v1",
      "status":"SOURCE_PINNED_PARTIAL_INFORMATION_SENSITIVITY_ONLY",
      "source_artifact_sha256":EXPECTED_DIGEST,
      "algae_area_target":"algae-area-weighted hypothetical mapped class persistence comparison, fixed year 2022 source extent",
      "source_original_2022_algae_acres":round(total,3),
      "results":result,
      "independent_sites_or_biological_followup_observed":False,
      "no_pvalue_or_confidence_interval":True,
      "summary":"The size+space contrast sign is not identified for the original full 2022 algae footprint because more than half of algae area is outside joint support; a sensitivity envelope crossing zero is not a test of the sign of a biological effect."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",default=str(REPORT))
    p.add_argument("--out",required=True)
    x=p.parse_args()
    original_bytes=Path(x.source).read_bytes()
    release=json.loads(original_bytes)
    report=evaluate(release)
    report["input_release_file_sha256"]=hashlib.sha256(original_bytes).hexdigest()
    target=Path(x.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
