#!/usr/bin/env python3
"""Metadata-only, fail-closed eligibility gate for SEACAR CHAP Program 570.

DOES NOT READ BIOLOGICAL WORKBOOKS. PASS means only curator-asserted metadata
completeness; it is neither independent authentication nor empirical replication.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SCHEMA="tampa.chap_external_state_axes_v1.metadata_manifest"
EXCLUDE={"CR01","CR02","CR02A","CR02B","CR03","CR04A","CR04B","CR05","PI10","PI11","SC04","SC05"}
ROLES={"program_id","aquatic_preserve","transect_id","survey_date","quadrat_id",
       "quadrat_role","surveyed_quadrat_roster","species_code","braun_blanquet",
       "blade_length_cm","shoot_count"}
DOCS={"source_workbook_metadata","longitudinal_identifier_protocol",
      "sampling_zero_missing_protocol","bb_scale_protocol","measurement_area_protocol",
      "annual_survey_season_protocol","program_570_filter_protocol",
      "healthy_blade_selection_protocol","shoot_subquadrat_extrapolation_protocol"}
FLAGS={"stable_transect_id_documented","stable_repeat_quadrat_id_documented",
       "repeat_quadrats_only","exclude_variable_bed_edges",
       "complete_surveyed_quadrat_roster_documented",
       "explicit_surveyed_absence_distinct_from_missing",
       "repeated_season_comparability_documented",
       "shoot_count_per_area_documented","blade_length_unit_cm_documented",
       "healthy_thalassia_blade_selection_documented",
       "shoot_subquadrat_extrapolation_documented",
       "multiple_surveys_per_year_rule_documented","protocol_changes_identified",
       "separate_570_from_5721_and_571","exclude_documented_noncore_stations"}
BB_OPTIONS={"confirmed_0.5","confirmed_0.05","different_documented_raw_scale"}

def good_text(v):
    return isinstance(v,str) and bool(v.strip())

def good_url(v):
    if not good_text(v): return False
    p=urlparse(v)
    return p.scheme=="https" and bool(p.netloc)

def gate(manifest):
    errors=[]
    def demand(condition,code):
        if not condition: errors.append(code)
    if not isinstance(manifest,dict):
        return {"status":"STOP_METADATA_GATE","errors":["INVALID_MANIFEST"],
                "response_rows_read":0,"model_fits":0,"external_replication_observed":False}
    demand(manifest.get("schema")==SCHEMA,"SCHEMA_MISMATCH")
    demand(manifest.get("program_id")==570,"PROGRAM_NOT_570")
    demand(manifest.get("response_values_opened") is False,"RESPONSES_ALREADY_OPENED")
    # Public mapped-area and species-trend aggregate responses have been reviewed.
    # Raw workbook not opened != untouched hypothesis-independent confirmation.
    demand(manifest.get("published_aggregate_outcomes_seen") is True,
           "PUBLISHED_OUTCOME_EXPOSURE_NOT_ACKNOWLEDGED")
    demand(manifest.get("external_predictive_validation_eligible") is False,
           "UNTOUCHED_PREDICTION_CLAIM_FORBIDDEN")
    demand(manifest.get("authorization")=="confirmed_by_data_requester","DATA_ACCESS_UNCONFIRMED")
    url=manifest.get("official_program_url")
    p=urlparse(url) if good_url(url) else None
    demand(bool(p and p.netloc=="data.florida-seacar.org" and
                p.path.rstrip("/")=="/programs/details/570"),"PROGRAM_URL_UNVERIFIED")

    source=manifest.get("source")
    if not isinstance(source,dict): source={}
    demand(good_text(source.get("original_workbook_filename")),"WORKBOOK_FILENAME_MISSING")
    demand(bool(re.fullmatch(r"[a-fA-F0-9]{64}",str(source.get("original_workbook_sha256","")))),
           "WORKBOOK_SHA256_MISSING")
    demand(good_text(source.get("provenance_method")),"SOURCE_PROVENANCE_MISSING")
    demand(source.get("raw_response_opened") is False,"SOURCE_RESPONSE_ALREADY_OPENED")
    documents=manifest.get("documentation")
    if not isinstance(documents,dict): documents={}
    for field in sorted(DOCS):
        d=documents.get(field)
        demand(isinstance(d,dict) and good_url(d.get("url")) and good_text(d.get("locator")),
               "DOCUMENTATION_MISSING:"+field)
    columns=manifest.get("column_roles")
    if not isinstance(columns,dict): columns={}
    for field in sorted(ROLES):
        demand(good_text(columns.get(field)),"COLUMN_ROLE_UNRESOLVED:"+field)
    mapped=[columns.get(k) for k in sorted(ROLES) if good_text(columns.get(k))]
    demand(len(mapped)==len(set(mapped)),"COLUMN_ROLE_AMBIGUOUS_DUPLICATE")

    rules=manifest.get("identity_and_observation")
    if not isinstance(rules,dict): rules={}
    for field in sorted(FLAGS):
        demand(rules.get(field) is True,"IDENTITY_RULE_UNRESOLVED:"+field)
    demand(rules.get("raw_bb_few_category_resolution") in BB_OPTIONS,
           "BB_FEW_CATEGORY_UNRESOLVED_0.05_VS_0.5")
    demand(rules.get("zero_assignment")=="sampled_complete_focal_negative_only",
           "ZERO_MISSING_POLICY_UNSAFE")
    demand(rules.get("primary_start_year")==2016 and rules.get("primary_end_year")==2025,
           "PRIMARY_WINDOW_DRIFT")
    exclusion=manifest.get("excluded_station_codes")
    demand(isinstance(exclusion,list) and {str(x).strip().upper() for x in exclusion}==EXCLUDE,
           "STATION_EXCLUSION_LIST_INCOMPLETE_OR_CHANGED")

    return {"schema":"tampa.chap_external_state_axes_v1.metadata_gate_result",
            "status":"STOP_METADATA_GATE" if errors else "PASS_METADATA_DOCUMENTATION_ONLY",
            "errors":sorted(set(errors)), "response_rows_read":0,
            "source_workbook_opened_by_gate":False,"model_fits":0,
            "external_replication_observed":False,
            "published_aggregate_outcomes_seen":True,
            "untouched_external_prediction_eligible":False,
            "meaning_of_pass":"Curator assertions and locators only; no independent source audit or empirical estimability"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True,help="JSON metadata manifest only, not response data")
    parser.add_argument("--out",help="optional output JSON")
    args=parser.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result=gate(manifest)
    payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True,exist_ok=True)
        Path(args.out).write_text(payload,encoding="utf-8")
    print(payload,end="")
    return 0 if result["status"]=="PASS_METADATA_DOCUMENTATION_ONLY" else 2

if __name__=="__main__":
    sys.exit(main())
