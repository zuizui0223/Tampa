#!/usr/bin/env python3
"""Fail-closed validator for the response-independent Tampa TNC-v2 method pilot."""
from __future__ import annotations
import argparse,json
from pathlib import Path

REQUIRED_SELECTED=[
  ("tissue_class","selected_horizontal_rhizome_tissue_class"),
  ("core_geometry","selected_core_diameter_cm"),
  ("core_geometry","selected_core_depth_cm"),
  ("transect_offset","selected_minimum_perpendicular_transect_offset_m"),
  ("preservation","selected_preservation_method"),
  ("preservation","selected_maximum_collection_to_preservation_minutes"),
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pilot",default="field/tnc_v2_method_pilot.json")
    ap.add_argument("--out",default="results/tnc_v2_method_pilot_validation.json")
    a=ap.parse_args()

    x=json.loads(Path(a.pilot).read_text())
    errors=[]
    pending=[]

    if x.get("outcome_response_accessed") is not False:
        errors.append("pilot must remain independent of future ecological outcome/response")

    # Candidate search order is predeclared before pilot values are inspected.
    tissue_candidates=x.get("tissue_class",{}).get("candidate_order",[])
    if len(tissue_candidates)!=2 or "3-cm" not in tissue_candidates[0] or "4-cm" not in tissue_candidates[1]:
        errors.append("tissue-class candidate order drift")

    geometry_candidates=x.get("core_geometry",{}).get("candidate_order",[])
    expected_geometry=[(9,15),(9,20),(15,15),(15,20),(15,25)]
    got_geometry=[
        (float(z.get("diameter_cm")),float(z.get("depth_cm")))
        for z in geometry_candidates
        if isinstance(z,dict) and z.get("diameter_cm") is not None and z.get("depth_cm") is not None
    ]
    if got_geometry != [(float(a),float(b)) for a,b in expected_geometry]:
        errors.append("core-geometry candidate order drift")

    preservation_candidates=x.get("preservation",{}).get("candidate_methods",[])
    if len(preservation_candidates)!=2 or "liquid-nitrogen" not in preservation_candidates[0] or "dry-ice" not in preservation_candidates[1]:
        errors.append("preservation candidate order drift")

    for sec,key in REQUIRED_SELECTED:
        if x.get(sec,{}).get(key) in (None,"","PENDING"):
            pending.append(f"{sec}.{key}")

    # Method/QC fields that are required before a PASS can be evaluated.
    for sec,keys in {
      "pilot_material":["independent_rhizome_specimens","collection_locations_or_batches","field_core_attempts"],
      "analytical_qc":[
        "calibration_identity_unambiguous",
        "standard_mix_mean_recovery_pct","matrix_spike_mean_recovery_pct",
        "matrix_spike_all_within_85_115",
        "technical_duplicate_median_cv_pct","technical_duplicate_fraction_gt15pct",
        "pilot_extract_fraction_in_calibration_range","blank_below_loq",
        "post_high_standard_carryover_below_loq"
      ],
      "tissue_class":["classification_success_fraction","sufficient_dry_mass_fraction"],
      "core_geometry":[
        "recovery_success_fraction","sufficient_dry_mass_fraction",
        "three_anchor_geometry_feasible","least_destructive_passing_geometry_selected"
      ],
      "transect_offset":[
        "monitoring_authority_boundary_documented","representative_anchor_placement_test_passed"
      ],
      "preservation":[
        "paired_specimens_at_selected_delay","median_abs_relative_tnc_difference_pct",
        "p90_abs_relative_tnc_difference_pct","monotonic_directional_drift_absent"
      ],
    }.items():
        for key in keys:
            if x.get(sec,{}).get(key) in (None,"","PENDING"):
                pending.append(f"{sec}.{key}")

    if pending and not errors:
        result={
          "schema":"tampa.tnc_v2_method_pilot_validation.v1",
          "status":"STOP_PILOT_INCOMPLETE",
          "pending_fields":sorted(set(pending)),
          "errors":[],
          "copy_to_precollection_freeze":None,
          "claim_boundary":"Incomplete pilot is a logistics/method-development state, not ecological evidence."
        }
    else:
        if pending:
            errors.append("pilot has incomplete required fields")

        p=x["pilot_material"]
        if int(p["independent_rhizome_specimens"])<8:
            errors.append("independent_rhizome_specimens < 8")
        if int(p["collection_locations_or_batches"])<2:
            errors.append("collection_locations_or_batches < 2")
        if int(p["field_core_attempts"])<10:
            errors.append("field_core_attempts < 10")

        q=x["analytical_qc"]
        if q["calibration_identity_unambiguous"] is not True:
            errors.append("primary HPLC calibration/analyte identity is not unambiguous")
        if not 95<=float(q["standard_mix_mean_recovery_pct"])<=105:
            errors.append("standard-mix mean recovery outside 95-105%")
        if not 85<=float(q["matrix_spike_mean_recovery_pct"])<=115:
            errors.append("matrix-spike mean recovery outside 85-115%")
        if q["matrix_spike_all_within_85_115"] is not True:
            errors.append("one or more individual matrix-spike recoveries fall outside 85-115%")
        if float(q["technical_duplicate_median_cv_pct"])>10:
            errors.append("technical-duplicate median CV > 10%")
        if float(q["technical_duplicate_fraction_gt15pct"])>0.10:
            errors.append(">10% of technical-duplicate pairs have CV >15%")
        if float(q["pilot_extract_fraction_in_calibration_range"])<0.90:
            errors.append("<90% pilot extracts inside frozen calibration range")
        if q["blank_below_loq"] is not True:
            errors.append("analytical blank not below LOQ")
        if q["post_high_standard_carryover_below_loq"] is not True:
            errors.append("post-high-standard carryover not below LOQ")

        t=x["tissue_class"]
        if float(t["classification_success_fraction"])<0.90:
            errors.append("tissue classification success <90%")
        if float(t["sufficient_dry_mass_fraction"])<0.90:
            errors.append("tissue sufficient-dry-mass fraction <90%")
        if t.get("selection_used_tnc_level_or_ecological_state") is not False:
            errors.append("tissue class selection used TNC level or ecological state")

        g=x["core_geometry"]
        if float(g["recovery_success_fraction"])<0.90:
            errors.append("core geometry rhizome recovery <90%")
        if float(g["sufficient_dry_mass_fraction"])<0.90:
            errors.append("core geometry dry-mass success <90%")
        if g["three_anchor_geometry_feasible"] is not True:
            errors.append("q25/q50/q75 three-anchor geometry not feasible")
        if g["least_destructive_passing_geometry_selected"] is not True:
            errors.append("selected geometry is not the least-destructive passing geometry")

        o=x["transect_offset"]
        if o["monitoring_authority_boundary_documented"] is not True:
            errors.append("monitoring-authority disturbance boundary not documented")
        if float(o["selected_minimum_perpendicular_transect_offset_m"])<=0:
            errors.append("selected transect offset must be >0")
        if o["representative_anchor_placement_test_passed"] is not True:
            errors.append("representative anchor placement test not passed")

        pr=x["preservation"]
        delays=[float(v) for v in pr.get("tested_delays_minutes",[])]
        selected=float(pr["selected_maximum_collection_to_preservation_minutes"])
        if selected not in delays:
            errors.append("selected maximum preservation delay was not directly tested")
        if int(pr["paired_specimens_at_selected_delay"])<6:
            errors.append("paired specimens at selected preservation delay <6")
        if float(pr["median_abs_relative_tnc_difference_pct"])>10:
            errors.append("median preservation-delay TNC difference >10%")
        if float(pr["p90_abs_relative_tnc_difference_pct"])>15:
            errors.append("p90 preservation-delay TNC difference >15%")
        if pr["monotonic_directional_drift_absent"] is not True:
            errors.append("monotonic TNC drift across preservation delay was not ruled out")
        if not pr.get("selected_preservation_method"):
            errors.append("preservation method is blank")

        copy={
          "horizontal_rhizome_tissue_class":t["selected_horizontal_rhizome_tissue_class"],
          "minimum_perpendicular_transect_offset_m":float(o["selected_minimum_perpendicular_transect_offset_m"]),
          "core_diameter_cm":float(g["selected_core_diameter_cm"]),
          "core_depth_cm":float(g["selected_core_depth_cm"]),
          "maximum_collection_to_preservation_minutes":selected,
          "preservation_method":pr["selected_preservation_method"],
        }

        result={
          "schema":"tampa.tnc_v2_method_pilot_validation.v1",
          "status":"PASS_METHOD_PILOT" if not errors else "STOP_PILOT_QC_FAILED",
          "pending_fields":[],
          "errors":errors,
          "copy_to_precollection_freeze":copy if not errors else None,
          "claim_boundary":"Pilot pass validates method/field feasibility only; it does not support the ecological TNC hypothesis."
        }

    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
