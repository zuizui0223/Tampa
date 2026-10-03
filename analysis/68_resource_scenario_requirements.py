#!/usr/bin/env python3
"""Derive response-independent resource envelopes from frozen Tampa field contracts.

No biological predictor/outcome values are read. This is a logistics calculator
for deciding which optional modules are physically supportable before sampling.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def cores(n_tnc:int, n_prepost:int)->int:
    if n_prepost>n_tnc:
        raise ValueError("pre/post nodes cannot exceed authoritative TNC nodes")
    return 6*n_prepost + 3*(n_tnc-n_prepost)

def main():
    campaign=json.loads((ROOT/"results/integrated_field_campaign_v1_contract.json").read_text())
    tnc=json.loads((ROOT/"results/clonal_state_prospective_v2_contract.json").read_text())
    event=json.loads((ROOT/"results/event_stress_debt_prospective_v1_contract.json").read_text())
    optical=json.loads((ROOT/"results/optical_microenvironment_prospective_v1_contract.json").read_text())

    tnc_plan=campaign["mechanism_execution_gates"]["tnc_v2"]["planning_nodes"]
    tnc_min=campaign["mechanism_execution_gates"]["tnc_v2"]["confirmatory_minimum_total"]
    event_plan=campaign["mechanism_execution_gates"]["event_stress"]["planning_nodes"]
    event_min=campaign["mechanism_execution_gates"]["event_stress"]["confirmatory_minimum_total"]
    optical_plan=campaign["mechanism_execution_gates"]["optical"]["planning_nodes"]
    optical_min=campaign["mechanism_execution_gates"]["optical"]["confirmatory_minimum_total"]
    ref_target=campaign["mechanism_execution_gates"]["optical"]["paired_reference_subset"]["target_nodes"]
    ref_min=campaign["mechanism_execution_gates"]["optical"]["paired_reference_subset"]["minimum_total"]

    result={
      "schema":"tampa.field_resource_scenario_requirements_v1",
      "status":"response_independent_resource_envelope",
      "protected_primary":{
        "tnc_v2_planning_nodes":tnc_plan,
        "tnc_v2_confirmatory_minimum_nodes":tnc_min,
        "minimum_cores_full_planning_frame_tnc_only":cores(tnc_plan,0),
        "minimum_cores_at_exact_tnc_confirmatory_floor_tnc_only":cores(tnc_min,0),
      },
      "scenario_examples":{
        "tnc_only_full_planning_frame":{
          "tnc_nodes":tnc_plan,
          "prepost_nodes":0,
          "minimum_outcome_bearing_cores_before_replacements":cores(tnc_plan,0),
          "temperature_salinity_node_systems":0,
          "within_canopy_par_node_systems":0,
          "above_canopy_reference_systems":0,
        },
        "one_forcing_module_at_confirmatory_floor_with_full_tnc_frame":{
          "tnc_nodes":tnc_plan,
          "prepost_nodes":event_min,
          "minimum_outcome_bearing_cores_before_replacements":cores(tnc_plan,event_min),
          "note":"Applies to either event or optical when exactly 30 core-three nodes receive pre/post TNC."
        },
        "one_or_both_forcing_modules_full_core_three_frame":{
          "tnc_nodes":tnc_plan,
          "prepost_union_nodes":event_plan,
          "minimum_outcome_bearing_cores_before_replacements":cores(tnc_plan,event_plan),
          "note":"If event and optical use the same full 33 core-three nodes, shared TNC means both together still require 222 rather than two separate pre/post core programmes."
        }
      },
      "module_capacity_gates":{
        "event_stress":{
          "planning_complete_temperature_salinity_node_systems":event_plan,
          "confirmatory_minimum_complete_temperature_salinity_node_systems":event_min,
          "minimum_per_core_bay":campaign["mechanism_execution_gates"]["event_stress"]["confirmatory_minimum_per_bay"],
          "simultaneous":True,
          "rotation_across_weather_windows_allowed":False
        },
        "optical_primary":{
          "planning_within_canopy_par_node_systems":optical_plan,
          "confirmatory_minimum_within_canopy_par_node_systems":optical_min,
          "minimum_per_core_bay":campaign["mechanism_execution_gates"]["optical"]["confirmatory_minimum_per_bay"],
          "simultaneous":True,
          "rotation_across_weather_windows_allowed":False
        },
        "optical_attribution":{
          "target_above_canopy_reference_systems":ref_target,
          "confirmatory_minimum_above_canopy_reference_systems":ref_min,
          "minimum_per_core_bay":campaign["mechanism_execution_gates"]["optical"]["paired_reference_subset"]["minimum_per_bay"],
          "requires_optical_primary_confirmatory":True,
          "role":"secondary attribution; may be disabled without invalidating optical primary"
        }
      },
      "decision_tree":[
        "Protect TNC-v2 first. If the final authoritative TNC node set, preservation capacity, HPLC capacity, method pilot or baseline calendar cannot satisfy v2, no outcome-bearing campaign is ready.",
        "If event-stress lacks its full simultaneous 30-node / 8-per-bay sensor and pilot/calendar gates, freeze event_module_intent=disabled before outcome-bearing pre-TNC sampling.",
        "If optical lacks its full simultaneous 30-node / 8-per-bay within-canopy PAR and pilot/calendar gates, freeze optical_module_intent=disabled before outcome-bearing pre-TNC sampling.",
        "If optical primary is confirmatory but the paired above-canopy subset cannot reach 12 total / 3 per bay, set optical_attribution_intent=disabled; do not downgrade the optical primary.",
        "If both event and optical are confirmatory, they may share the same pre/post TNC rounds; resource planning uses the union of their node sets, never the sum.",
      ],
      "exact_core_formula":"6 * n(unique confirmatory event OR optical nodes) + 3 * n(authoritative TNC nodes outside that union)",
      "capacity_boundary":[
        "Core counts above exclude replacement attempts; replacement-core policy and total attempted-core ceiling are separate frozen fields.",
        "HPLC and preservation capacity must be checked against the exact final-node core count, not merely against these planning examples.",
        "Multi-channel PAR hardware may satisfy more than one sampling volume only when the frozen calibration/synchronization/geometry rules are met.",
        "These resource envelopes contain no ecological result and cannot be used to select nodes by future TNC or meadow response."
      ]
    }
    out=ROOT/"results/field_resource_scenario_requirements_v1.json"
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
