#!/usr/bin/env python3
"""Fail-closed validator for the response-independent Tampa optical method pilot."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pilot",default="field/optical_pilot_candidate.json")
    ap.add_argument("--contract",default="results/optical_pilot_acceptance_v1_contract.json")
    ap.add_argument("--out",default="results/optical_method_pilot_validation.json")
    a=ap.parse_args()

    p=Path(a.pilot); cpath=Path(a.contract)
    x=json.loads(p.read_text())
    c=json.loads(cpath.read_text())
    errors=[]; pending=[]

    if x.get("outcome_response_accessed") is not False:
        errors.append("pilot must explicitly remain independent of TNC/future ecological response")

    meta=x.get("metadata",{})
    for k in (
      "par_sensor_model","reference_sensor_id_and_calibration_provenance",
      "side_by_side_underwater_hours","fouling_pilot_submerged_days",
      "mounting_geometry_and_height_tolerance_rule","above_canopy_clearance_tolerance_rule"
    ):
        if meta.get(k) in (None,"","PENDING"):
            pending.append(f"metadata.{k}")

    # Calibration: every declared candidate channel in the raw summary must pass.
    sm=x.get("calibration",{}).get("sensor_metrics",{})
    if not sm:
        pending.append("calibration.sensor_metrics")
    cal=c["calibration_gate"]
    ac=cal["post_correction_acceptance"]
    all_channels_pass=True
    calibration_manifest={}
    for sid,m in sm.items():
        required=("paired_n","irradiance_levels","intercept","slope","r_squared",
                  "median_absolute_relative_error","p95_absolute_relative_error",
                  "dark_offset_abs_umol_m2_s","saturated")
        if any(m.get(k) is None for k in required):
            pending.append(f"calibration.sensor_metrics.{sid}")
            all_channels_pass=False
            continue
        fail=[]
        if int(m["paired_n"])<cal["minimum_paired_observations_per_sensor"]: fail.append("paired_n")
        if int(m["irradiance_levels"])<cal["minimum_irradiance_levels"]: fail.append("irradiance_levels")
        if float(m["r_squared"])<ac["r_squared_min"]: fail.append("r_squared")
        if float(m["median_absolute_relative_error"])>ac["median_absolute_relative_error_max"]: fail.append("median_absolute_relative_error")
        if float(m["p95_absolute_relative_error"])>ac["p95_absolute_relative_error_max"]: fail.append("p95_absolute_relative_error")
        if float(m["dark_offset_abs_umol_m2_s"])>ac["dark_offset_abs_umol_m2_s_max"]: fail.append("dark_offset")
        if bool(m["saturated"]) is not ac["saturation_allowed"]: fail.append("saturation")
        if fail:
            all_channels_pass=False
            errors.append(f"sensor {sid} fails calibration gate: {fail}")
        calibration_manifest[sid]={
          "reference_from_raw_to_ppfd":{"intercept":float(m["intercept"]),"slope":float(m["slope"])},
          "r_squared":float(m["r_squared"]),
          "median_absolute_relative_error":float(m["median_absolute_relative_error"]),
          "p95_absolute_relative_error":float(m["p95_absolute_relative_error"]),
          "dark_offset_abs_umol_m2_s":float(m["dark_offset_abs_umol_m2_s"])
        }

    try:
        hours=float(meta["side_by_side_underwater_hours"])
        if hours<cal["side_by_side_dli_check"]["minimum_underwater_hours"]:
            errors.append("side-by-side underwater duration below calibration gate")
        sidecv=x.get("calibration",{}).get("max_between_sensor_cv")
        if sidecv is None:
            pending.append("calibration.max_between_sensor_cv")
        elif float(sidecv)>cal["side_by_side_dli_check"]["maximum_between_sensor_cv"]:
            errors.append("between-sensor side-by-side DLI CV exceeds gate")
    except (TypeError,ValueError,KeyError):
        if "metadata.side_by_side_underwater_hours" not in pending:
            pending.append("metadata.side_by_side_underwater_hours")

    # Vertical profile and one-height selection.
    vp=x.get("vertical_profile",{})
    selected=vp.get("selected_within_canopy_height_fraction")
    if selected is None:
        pending.append("vertical_profile.selected_within_canopy_height_fraction")
    else:
        selected=float(selected)
        if selected not in c["vertical_representativeness_gate"]["candidate_levels"]:
            errors.append("selected canopy-height fraction not in frozen candidate levels")
    try:
        n=int(vp.get("pilot_nodes"))
        if n<c["vertical_representativeness_gate"]["pilot_nodes_min"]:
            errors.append("vertical-profile pilot node count below gate")
    except Exception:
        pending.append("vertical_profile.pilot_nodes")
        n=None
    by=vp.get("nodes_by_bay")
    if not isinstance(by,dict) or not by:
        pending.append("vertical_profile.nodes_by_bay")
        by={}
    else:
        for b in BAYS:
            if int(by.get(b,0))<c["vertical_representativeness_gate"]["pilot_nodes_min_per_bay"]:
                errors.append(f"vertical-profile {b} node count below gate")
    try:
        mindays=int(vp.get("minimum_valid_daylight_days_per_node"))
        if mindays<c["vertical_representativeness_gate"]["minimum_valid_daylight_days_per_node"]:
            errors.append("minimum valid profile daylight days/node below gate")
    except Exception:
        pending.append("vertical_profile.minimum_valid_daylight_days_per_node")

    chosen_metric=None
    if selected is not None:
        chosen_metric=vp.get("candidate_level_metrics",{}).get(str(selected))
        if chosen_metric is None:
            # JSON may stringify 0.5 as "0.5"; defensive alternate.
            chosen_metric=vp.get("candidate_level_metrics",{}).get(f"{selected:g}")
        if not isinstance(chosen_metric,dict):
            pending.append("vertical_profile.selected_level_metrics")
        else:
            a=c["vertical_representativeness_gate"]["acceptance"]
            if float(chosen_metric["median_absolute_relative_error"])>a["median_absolute_relative_error_max"]:
                errors.append("selected height median absolute relative error exceeds gate")
            if float(chosen_metric["fraction_node_days_with_absolute_relative_error_lte_0_25"])<a["fraction_node_days_with_absolute_relative_error_lte_0_25_min"]:
                errors.append("selected height node-day agreement fraction below gate")
            if float(chosen_metric["max_absolute_bay_median_relative_bias"])>a["absolute_bay_median_relative_bias_max"]:
                errors.append("selected height bay median relative bias exceeds gate")

    # Placement.
    placement=x.get("placement",{})
    pf=placement.get("fraction_within_tolerance")
    if pf is None:
        pending.append("placement.fraction_within_tolerance")
    elif float(pf)<c["placement_repeatability_gate"]["fraction_placements_within_tolerance_min"]:
        errors.append("placement repeatability below gate")

    # Fouling.
    try:
        days=int(meta["fouling_pilot_submerged_days"])
        if days<c["fouling_maintenance_gate"]["minimum_submerged_pilot_days"]:
            errors.append("fouling pilot duration below gate")
    except Exception:
        if "metadata.fouling_pilot_submerged_days" not in pending:
            pending.append("metadata.fouling_pilot_submerged_days")
    fouling=x.get("fouling",{})
    interval=fouling.get("selected_manual_service_interval_days")
    if interval is None:
        pending.append("fouling.selected_manual_service_interval_days")
        selected_fouling=None
    else:
        interval=int(interval)
        if interval not in c["fouling_maintenance_gate"]["candidate_service_intervals_days"]:
            errors.append("selected fouling interval outside frozen candidate set")
        selected_fouling=fouling.get("candidate_interval_metrics",{}).get(str(interval))
        if not isinstance(selected_fouling,dict):
            pending.append("fouling.selected_interval_metrics")
        elif selected_fouling.get("pass") is not True:
            errors.append("selected fouling interval does not pass frozen response gate")

    # Candidate output can be incomplete before actual pilot; that is not an error.
    pending=sorted(set(pending))
    if pending and not errors:
        status="STOP_PILOT_INCOMPLETE"
        copy=None
    elif errors:
        status="STOP_PILOT_QC_FAILED"
        copy=None
    else:
        status="PASS_OPTICAL_PILOT"
        rawprov=x.get("raw_pilot_provenance",{})
        copy={
          "par_sensor_model":meta["par_sensor_model"],
          "reference_sensor_id_and_calibration_provenance":meta["reference_sensor_id_and_calibration_provenance"],
          "sensor_specific_calibration_manifest":calibration_manifest,
          "all_outcome_bearing_channels_pass_calibration_gate":all_channels_pass,
          "selected_within_canopy_height_fraction":selected,
          "vertical_profile_pilot_nodes":int(vp["pilot_nodes"]),
          "vertical_profile_nodes_by_bay":by,
          "vertical_profile_median_absolute_relative_error":float(chosen_metric["median_absolute_relative_error"]),
          "vertical_profile_fraction_node_days_within_25pct":float(chosen_metric["fraction_node_days_with_absolute_relative_error_lte_0_25"]),
          "vertical_profile_max_absolute_bay_median_relative_bias":float(chosen_metric["max_absolute_bay_median_relative_bias"]),
          "placement_repeatability_fraction_within_tolerance":float(pf),
          "mounting_geometry_and_height_tolerance_rule":meta["mounting_geometry_and_height_tolerance_rule"],
          "maintenance_mode":"manual",
          "manual_service_interval_days":interval,
          "fouling_median_absolute_relative_change":float(selected_fouling["median_absolute_relative_change"]),
          "fouling_p90_absolute_relative_change":float(selected_fouling["p90_absolute_relative_change"]),
          "above_canopy_clearance_tolerance_rule":meta["above_canopy_clearance_tolerance_rule"],
          "pilot_artifact_or_manifest_digest":sha256(p)
        }

    result={
      "schema":"tampa.optical_method_pilot_validation.v1",
      "status":status,
      "pending_fields":pending,
      "errors":errors,
      "copy_to_optical_pilot_freeze":copy,
      "pilot_source":str(p),
      "pilot_candidate_sha256":sha256(p),
      "raw_pilot_provenance":x.get("raw_pilot_provenance"),
      "claim_boundary":"Pilot validation is measurement-method evidence only; it does not support the ecological optical mechanism."
    }
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()
