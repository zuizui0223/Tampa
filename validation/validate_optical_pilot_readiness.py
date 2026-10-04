#!/usr/bin/env python3
"""Fail-closed audit of the optical response-independent method pilot freeze."""
from __future__ import annotations
import argparse,json
from pathlib import Path

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--freeze",default="field/optical_pilot_freeze.json")
    ap.add_argument("--contract",default="results/optical_pilot_acceptance_v1_contract.json")
    ap.add_argument("--strict",action="store_true")
    a=ap.parse_args()
    x=json.loads(Path(a.freeze).read_text())
    c=json.loads(Path(a.contract).read_text())
    f=x["fields_to_freeze_before_optical_confirmatory_deployment"]
    errors=[]

    assert x["contract"]=="results/optical_pilot_acceptance_v1_contract.json"
    assert x["fixed_dli_qc"]["minimum_scheduled_daylight_observation_fraction"]==c["daily_dli_qc"]["minimum_scheduled_daylight_observation_fraction"]
    assert x["fixed_dli_qc"]["maximum_continuous_daylight_gap_minutes"]==c["daily_dli_qc"]["maximum_continuous_daylight_gap_minutes"]
    assert x["fixed_dli_qc"]["node_primary_minimum_valid_days"]==c["daily_dli_qc"]["node_primary_minimum_valid_days"]

    pending=[k for k,v in f.items() if v in (None,"","PENDING")]
    if x["status"]!="READY":
        result={
          "schema":"tampa.optical_pilot_readiness.v1",
          "status":"STOP_OPTICAL_PILOT_INCOMPLETE",
          "pending_fields":pending,
          "errors":[],
          "claim_boundary":["Method readiness is not ecological evidence.","Do not begin confirmatory optical deployment while this freeze is incomplete."]
        }
        print(json.dumps(result,indent=2,sort_keys=True))
        if a.strict: raise SystemExit(2)
        return

    if pending:
        errors.append(f"READY status with pending fields: {pending}")

    if f.get("all_outcome_bearing_channels_pass_calibration_gate") is not True:
        errors.append("not all outcome-bearing PAR channels passed calibration gate")

    level=f.get("selected_within_canopy_height_fraction")
    if level not in (0.25,0.5,0.75):
        errors.append("selected height must be one of 0.25, 0.50, 0.75")

    try:
        n=int(f["vertical_profile_pilot_nodes"])
        if n<c["vertical_representativeness_gate"]["pilot_nodes_min"]:
            errors.append(f"vertical profile nodes {n} below minimum")
        by=f["vertical_profile_nodes_by_bay"]
        for b in BAYS:
            if int(by.get(b,0))<c["vertical_representativeness_gate"]["pilot_nodes_min_per_bay"]:
                errors.append(f"vertical profile {b} below per-bay minimum")
        if float(f["vertical_profile_median_absolute_relative_error"])>c["vertical_representativeness_gate"]["acceptance"]["median_absolute_relative_error_max"]:
            errors.append("vertical profile median error exceeds gate")
        if float(f["vertical_profile_fraction_node_days_within_25pct"])<c["vertical_representativeness_gate"]["acceptance"]["fraction_node_days_with_absolute_relative_error_lte_0_25_min"]:
            errors.append("vertical profile node-day agreement fraction below gate")
        if abs(float(f["vertical_profile_max_absolute_bay_median_relative_bias"]))>c["vertical_representativeness_gate"]["acceptance"]["absolute_bay_median_relative_bias_max"]:
            errors.append("vertical profile bay bias exceeds gate")
        if float(f["placement_repeatability_fraction_within_tolerance"])<c["placement_repeatability_gate"]["fraction_placements_within_tolerance_min"]:
            errors.append("placement repeatability below gate")
    except Exception as e:
        errors.append(f"invalid vertical-profile/placement fields: {e}")

    mode=str(f.get("maintenance_mode"))
    if mode=="manual":
        try:
            interval=int(f["manual_service_interval_days"])
            if interval not in c["fouling_maintenance_gate"]["candidate_service_intervals_days"]:
                errors.append("manual service interval not in frozen candidate set")
        except Exception:
            errors.append("manual service interval invalid")
    elif mode=="active_antifouling":
        if f.get("manual_service_interval_days")!="NOT_APPLICABLE_ACTIVE_ANTIFOULING":
            errors.append("active antifouling requires explicit non-applicable manual interval token")
    else:
        errors.append("maintenance_mode must be manual or active_antifouling")

    clearance=f.get("above_canopy_clearance_tolerance_rule")
    if clearance in (None,"","PENDING"):
        errors.append("above_canopy clearance must be frozen or explicitly marked not applicable")
    elif clearance=="NOT_APPLICABLE_ATTRIBUTION_DISABLED":
        pass

    try:
        if float(f["fouling_median_absolute_relative_change"])>c["fouling_maintenance_gate"]["acceptance"]["median_absolute_relative_change_max"]:
            errors.append("fouling median response change exceeds gate")
        if float(f["fouling_p90_absolute_relative_change"])>c["fouling_maintenance_gate"]["acceptance"]["p90_absolute_relative_change_max"]:
            errors.append("fouling p90 response change exceeds gate")
    except Exception as e:
        errors.append(f"invalid fouling fields: {e}")

    result={
      "schema":"tampa.optical_pilot_readiness.v1",
      "status":"READY" if not errors else "STOP_OPTICAL_PILOT_FAILED",
      "pending_fields":[],
      "errors":errors,
      "claim_boundary":["READY means measurement method/geometry passed; it is not evidence for an ecological optical mechanism."]
    }
    print(json.dumps(result,indent=2,sort_keys=True))
    if errors and a.strict: raise SystemExit(2)

if __name__=="__main__":
    main()
