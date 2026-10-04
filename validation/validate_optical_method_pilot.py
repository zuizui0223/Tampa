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
    x=json.loads(p.read_text(encoding="utf-8"))
    c=json.loads(cpath.read_text(encoding="utf-8"))
    errors=[]; pending=[]

    if x.get("outcome_response_accessed") is not False:
        errors.append("pilot must explicitly remain independent of TNC/future ecological response")

    meta=x.get("metadata",{})
    for k in (
        "par_sensor_model",
        "reference_sensor_id_and_calibration_provenance",
        "expected_field_ppfd_max_umol_m2_s",
        "mounting_geometry_and_height_tolerance_rule",
        "optical_attribution_intent",
    ):
        if meta.get(k) in (None,"","PENDING"):
            pending.append(f"metadata.{k}")

    attr_intent=meta.get("optical_attribution_intent")
    if attr_intent not in (None,"","PENDING"):
        allowed=c["optional_above_canopy_attribution"]["allowed_values"]
        if attr_intent not in allowed:
            errors.append(f"optical_attribution_intent must be one of {allowed}")
        if attr_intent=="confirmatory" and meta.get("above_canopy_clearance_tolerance_rule") in (None,"","PENDING"):
            pending.append("metadata.above_canopy_clearance_tolerance_rule")

    declared=x.get("calibration",{}).get("declared_outcome_bearing_sensor_ids",[])
    if not declared:
        pending.append("metadata.outcome_bearing_sensor_ids")
    if len(declared)!=len(set(declared)):
        errors.append("outcome_bearing_sensor_ids contains duplicates")

    # Calibration.
    cal=c["calibration_gate"]
    ac=cal["post_correction_acceptance"]
    darkdef=cal["dark_reference_definition"]
    sm=x.get("calibration",{}).get("sensor_metrics",{})
    manifest={}
    all_channels_pass=True

    for sid in declared:
        m=sm.get(sid)
        if not isinstance(m,dict):
            pending.append(f"calibration.sensor_metrics.{sid}")
            all_channels_pass=False
            continue
        required=(
            "paired_n","irradiance_levels","dark_observations",
            "maximum_reference_ppfd_umol_m2_s","intercept","slope","r_squared",
            "median_absolute_relative_error","p95_absolute_relative_error",
            "dark_offset_abs_umol_m2_s","saturated"
        )
        if any(m.get(k) is None for k in required):
            pending.append(f"calibration.sensor_metrics.{sid}")
            all_channels_pass=False
            continue
        fail=[]
        if int(m["paired_n"])<cal["minimum_paired_observations_per_sensor"]:
            fail.append("paired_n")
        if int(m["irradiance_levels"])<cal["minimum_irradiance_levels"]:
            fail.append("irradiance_levels")
        if int(m["dark_observations"])<darkdef["minimum_dark_observations_per_sensor"]:
            fail.append("dark_observations")
        try:
            expected_max=float(meta["expected_field_ppfd_max_umol_m2_s"])
            if float(m["maximum_reference_ppfd_umol_m2_s"])<expected_max:
                fail.append("expected_field_range")
        except Exception:
            pending.append("metadata.expected_field_ppfd_max_umol_m2_s")
        if float(m["r_squared"])<ac["r_squared_min"]:
            fail.append("r_squared")
        if float(m["median_absolute_relative_error"])>ac["median_absolute_relative_error_max"]:
            fail.append("median_absolute_relative_error")
        if float(m["p95_absolute_relative_error"])>ac["p95_absolute_relative_error_max"]:
            fail.append("p95_absolute_relative_error")
        if float(m["dark_offset_abs_umol_m2_s"])>ac["dark_offset_abs_umol_m2_s_max"]:
            fail.append("dark_offset")
        if bool(m["saturated"]) is not ac["saturation_allowed"]:
            fail.append("saturation")
        if fail:
            all_channels_pass=False
            errors.append(f"sensor {sid} fails calibration gate: {fail}")
        manifest[sid]={
            "reference_from_raw_to_ppfd":{
                "intercept":float(m["intercept"]),
                "slope":float(m["slope"]),
            },
            "r_squared":float(m["r_squared"]),
            "median_absolute_relative_error":float(m["median_absolute_relative_error"]),
            "p95_absolute_relative_error":float(m["p95_absolute_relative_error"]),
            "dark_offset_abs_umol_m2_s":float(m["dark_offset_abs_umol_m2_s"]),
            "paired_n":int(m["paired_n"]),
            "irradiance_levels":int(m["irradiance_levels"]),
            "dark_observations":int(m["dark_observations"]),
            "maximum_reference_ppfd_umol_m2_s":float(m["maximum_reference_ppfd_umol_m2_s"]),
        }

    # Side-by-side DLI.
    side=x.get("calibration",{})
    eligible_checks=side.get("eligible_checks",[])
    if not eligible_checks:
        pending.append("calibration.eligible_side_by_side_check")
    maxcv=side.get("max_between_sensor_cv")
    minhours=side.get("minimum_underwater_hours")
    if maxcv is None:
        pending.append("calibration.max_between_sensor_cv")
    elif float(maxcv)>cal["side_by_side_dli_check"]["maximum_between_sensor_cv"]:
        errors.append("between-sensor side-by-side DLI CV exceeds gate")
    if minhours is None:
        pending.append("calibration.minimum_underwater_hours")
    elif float(minhours)<cal["side_by_side_dli_check"]["minimum_underwater_hours"]:
        errors.append("side-by-side underwater duration below gate")

    # Vertical profile.
    vp=x.get("vertical_profile",{})
    vpc=c["vertical_representativeness_gate"]
    try:
        if int(vp.get("pilot_nodes"))<vpc["pilot_nodes_min"]:
            pending.append("vertical_profile.pilot_nodes_minimum")
    except Exception:
        pending.append("vertical_profile.pilot_nodes")
    by=vp.get("nodes_by_bay")
    if not isinstance(by,dict):
        pending.append("vertical_profile.nodes_by_bay")
        by={}
    else:
        for b in BAYS:
            if int(by.get(b,0))<vpc["pilot_nodes_min_per_bay"]:
                pending.append(f"vertical_profile.nodes_by_bay.{b}")
    try:
        if int(vp.get("minimum_valid_daylight_days_per_node"))<vpc["minimum_valid_daylight_days_per_node"]:
            pending.append("vertical_profile.minimum_valid_daylight_days_per_node")
    except Exception:
        pending.append("vertical_profile.minimum_valid_daylight_days_per_node")

    classes=vp.get("nodes_by_canopy_height_class")
    cg=vpc["canopy_height_class_gate"]
    if not isinstance(classes,dict):
        pending.append("vertical_profile.nodes_by_canopy_height_class")
    else:
        for cls in cg["classes"]:
            if int(classes.get(cls,0))<cg["minimum_pilot_nodes_per_class"]:
                pending.append(f"vertical_profile.canopy_height_class.{cls}")

    selected=vp.get("selected_within_canopy_height_fraction")
    if selected is None:
        pending.append("vertical_profile.selected_within_canopy_height_fraction")
        selected_num=None
    else:
        selected_num=float(selected)
        if selected_num not in [float(z) for z in vpc["candidate_levels"]]:
            errors.append("selected canopy-height fraction not in frozen candidate levels")

    metrics=vp.get("candidate_level_metrics",{})
    complete=[]
    for lev in vpc["candidate_levels"]:
        key=str(float(lev))
        m=metrics.get(key) or metrics.get(f"{float(lev):g}")
        if isinstance(m,dict) and m.get("median_absolute_relative_error") is not None:
            complete.append((float(lev),float(m["median_absolute_relative_error"])))
    if complete and selected_num is not None:
        tie={0.5:0,0.25:1,0.75:2}
        expected=min(complete,key=lambda z:(z[1],tie.get(z[0],99)))[0]
        if abs(selected_num-expected)>1e-12:
            errors.append(f"selected canopy height {selected_num} does not match frozen selection rule {expected}")

    chosen=None
    if selected_num is not None:
        chosen=metrics.get(str(selected_num)) or metrics.get(f"{selected_num:g}")
    if not isinstance(chosen,dict):
        pending.append("vertical_profile.selected_level_metrics")
    else:
        acc=vpc["acceptance"]
        if float(chosen["median_absolute_relative_error"])>acc["median_absolute_relative_error_max"]:
            errors.append("selected height median absolute relative error exceeds gate")
        if float(chosen["fraction_node_days_with_absolute_relative_error_lte_0_25"])<acc["fraction_node_days_with_absolute_relative_error_lte_0_25_min"]:
            errors.append("selected height node-day agreement fraction below gate")
        if float(chosen["max_absolute_bay_median_relative_bias"])>acc["absolute_bay_median_relative_bias_max"]:
            errors.append("selected height bay median relative bias exceeds gate")

    # Placement repeatability.
    placement=x.get("placement",{})
    try:
        if int(placement.get("pilot_nodes"))<c["placement_repeatability_gate"]["pilot_nodes_min"]:
            pending.append("placement.pilot_nodes")
    except Exception:
        pending.append("placement.pilot_nodes")
    if placement.get("covers_vertical_profile_nodes") is not True:
        pending.append("placement.same_vertical_profile_nodes")
    try:
        if int(placement.get("minimum_mock_deployments_per_node"))<c["placement_repeatability_gate"]["repeat_mock_deployments_per_node_min"]:
            pending.append("placement.minimum_mock_deployments_per_node")
    except Exception:
        pending.append("placement.minimum_mock_deployments_per_node")
    pf=placement.get("fraction_within_tolerance")
    if pf is None:
        pending.append("placement.fraction_within_tolerance")
    elif float(pf)<c["placement_repeatability_gate"]["fraction_placements_within_tolerance_min"]:
        errors.append("placement repeatability below gate")

    # Fouling / maintenance.
    fouling=x.get("fouling",{})
    mode=fouling.get("selected_maintenance_mode")
    interval=fouling.get("selected_manual_service_interval_days")
    selected_metrics=fouling.get("selected_metrics")
    if mode is None:
        pending.append("fouling.selected_maintenance_mode")
    elif mode not in ("manual","active_antifouling"):
        errors.append("maintenance mode must be manual or active_antifouling")
    if not isinstance(selected_metrics,dict):
        pending.append("fouling.selected_metrics")
    elif selected_metrics.get("pass") is not True:
        errors.append("selected maintenance configuration fails fouling gate")
    if mode=="manual":
        if interval not in c["fouling_maintenance_gate"]["candidate_service_intervals_days"]:
            errors.append("selected manual service interval outside frozen candidate set")
        passing=[
            int(k.split("_",1)[1])
            for k,v in fouling.get("candidate_metrics",{}).items()
            if k.startswith("manual_") and isinstance(v,dict) and v.get("pass") is True
        ]
        expected=next(
            (z for z in c["fouling_maintenance_gate"]["candidate_service_intervals_days"] if z in passing),
            None
        )
        if expected is not None and int(interval)!=int(expected):
            errors.append("selected manual interval is not the longest passing frozen candidate")
    elif mode=="active_antifouling":
        if interval!="NOT_APPLICABLE_ACTIVE_ANTIFOULING":
            errors.append("active antifouling must use explicit non-applicable manual interval token")

    pending=sorted(set(pending))
    if pending and not errors:
        status="STOP_PILOT_INCOMPLETE"
        copy=None
    elif errors:
        status="STOP_PILOT_QC_FAILED"
        copy=None
    else:
        status="PASS_OPTICAL_PILOT"
        if attr_intent=="confirmatory":
            clearance=meta["above_canopy_clearance_tolerance_rule"]
        else:
            clearance="NOT_APPLICABLE_ATTRIBUTION_DISABLED"
        if mode=="manual":
            manual_interval=int(interval)
        else:
            manual_interval="NOT_APPLICABLE_ACTIVE_ANTIFOULING"
        copy={
            "par_sensor_model":meta["par_sensor_model"],
            "reference_sensor_id_and_calibration_provenance":meta["reference_sensor_id_and_calibration_provenance"],
            "sensor_specific_calibration_manifest":manifest,
            "all_outcome_bearing_channels_pass_calibration_gate":all_channels_pass,
            "selected_within_canopy_height_fraction":selected_num,
            "vertical_profile_pilot_nodes":int(vp["pilot_nodes"]),
            "vertical_profile_nodes_by_bay":by,
            "vertical_profile_median_absolute_relative_error":float(chosen["median_absolute_relative_error"]),
            "vertical_profile_fraction_node_days_within_25pct":float(chosen["fraction_node_days_with_absolute_relative_error_lte_0_25"]),
            "vertical_profile_max_absolute_bay_median_relative_bias":float(chosen["max_absolute_bay_median_relative_bias"]),
            "placement_repeatability_fraction_within_tolerance":float(pf),
            "mounting_geometry_and_height_tolerance_rule":meta["mounting_geometry_and_height_tolerance_rule"],
            "maintenance_mode":mode,
            "manual_service_interval_days":manual_interval,
            "fouling_median_absolute_relative_change":float(selected_metrics["median_absolute_relative_change"]),
            "fouling_p90_absolute_relative_change":float(selected_metrics["p90_absolute_relative_change"]),
            "above_canopy_clearance_tolerance_rule":clearance,
            "pilot_artifact_or_manifest_digest":sha256(p),
        }

    result={
        "schema":"tampa.optical_method_pilot_validation.v2",
        "status":status,
        "pending_fields":pending,
        "errors":errors,
        "copy_to_optical_pilot_freeze":copy,
        "pilot_source":str(p),
        "pilot_candidate_sha256":sha256(p),
        "raw_pilot_provenance":x.get("raw_pilot_provenance"),
        "source_artifact_manifest":x.get("source_artifact_manifest"),
        "claim_boundary":"Pilot validation is measurement-method evidence only; it does not support the ecological optical mechanism.",
    }
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
