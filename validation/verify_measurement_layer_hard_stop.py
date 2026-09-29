#!/usr/bin/env python3
"""Verify Tampa new-measurement mechanism boundary."""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

cv=json.loads((ROOT/"results/current_validation_v2.json").read_text())
stop=cv["measurement_layer_hard_stop"]
assert stop["status"]=="same_annual_exact_point_mechanism_mining_closed"
assert stop["next_mechanism_priority"][0]=="below-ground reserve / clonal state"
assert "new biological measurement state" in stop["allowed_new_mechanism_gate"]
assert "additional annual/exact-point reappearance/loss/reloss subgroups" in stop["stopped_lines"]

clonal=json.loads((ROOT/"results/clonal_state_prospective_v1_contract.json").read_text())
assert clonal["status"]=="future_new_measurement_design_not_yet_opened"
assert clonal["future_outcome"]["primary"].startswith("next fixed-transect survey focal_frequency")
assert "binary reappearance" in clonal["future_outcome"]["prohibited_primary"]
assert clonal["baseline_new_measurements"]["primary_predictor"]["name"]=="rhizome_total_nonstructural_carbohydrate"
assert clonal["eligibility"]["target_sample_size_nodes"]==36
assert clonal["eligibility"]["minimum_analyzable_nodes"]==30


epi=json.loads((ROOT/"results/epiphyte_retention_v1.json").read_text())
assert epi["status"]=="primary_positive_but_2016_sensitivity_not_supported"
assert epi["primary_exclude_target_2016"]["coefficient_epi_within_node"]>0
assert epi["sensitivity_include_target_2016"]["ci95"][0]<0<epi["sensitivity_include_target_2016"]["ci95"][1]

tbofs=json.loads((ROOT/"results/tbofs_hydrodynamic_preflight_v1.json").read_text())
assert tbofs["status"]=="all_network_source_gate_failed"
assert tbofs["original_gate"]["passed"] is False
assert tbofs["tri_bay_core_geometric_summary"]["same_distance_thresholds_pass"] is True

tbofs_depth=json.loads((ROOT/"results/tbofs_depth_relevance_audit_v1.json").read_text())
assert tbofs_depth["status"]=="nearbed_meadow_interpretation_not_supported"
assert tbofs_depth["tri_bay_core"]["model_deeper_than_observed_nodes"]==47
assert tbofs_depth["tri_bay_core"]["model_at_2m_floor_nodes"]==40

hydro=json.loads((ROOT/"results/direct_hydrodynamic_prospective_v1_contract.json").read_text())
assert hydro["status"]=="future_new_measurement_design_not_yet_deployed"
assert hydro["primary_physical_metrics"]["attenuation_p90"].startswith("1 - p90(U_inside)")
assert hydro["primary_analysis"]["primary_coefficient"]=="attenuation_p90"
assert hydro["eligibility"]["target_nodes"]==36
assert hydro["eligibility"]["minimum_analyzable_nodes"]==30
assert hydro["mechanism_gate_logic"]["combined_claim_rule"].startswith("Use")
assert "binary reappearance" in hydro["future_outcome"]["prohibited_primary"]

hydro_protocol=(ROOT/"docs/DIRECT_HYDRODYNAMIC_SAMPLING_PROTOCOL_V1.md").read_text()
assert "Canopy hydrodynamic buffering hypothesis" in hydro_protocol
assert "TBOFS near-bottom velocity" in hydro_protocol
assert "attenuation_p90" in hydro_protocol

dual=json.loads((ROOT/"results/dual_buffer_prospective_v1_contract.json").read_text())
assert dual["status"]=="future_joint_new_measurement_design_not_yet_deployed"
assert dual["sampling"]["target_complete_nodes"]==36
assert dual["joint_primary_model"]["focal_coefficients"]==["TNC_z","attenuation_p90_z"]
assert "Holm" in dual["joint_primary_model"]["familywise_error"]
assert "No TNC x attenuation interaction" in dual["interaction_rule"]

boundary=(ROOT/"docs/ECOLOGICAL_MECHANISM_BOUNDARY_V1.md").read_text()
assert "Observation-state reappearance is not ecological recovery." in boundary
assert "Do **not** add another retrospective decomposition" in boundary
assert "Below-ground reserve / clonal state" in boundary
assert "model bottom-sigma velocity is not accepted" in boundary
assert "DIRECT_HYDRODYNAMIC_SAMPLING_PROTOCOL_V1.md" in boundary
assert "dual_buffer_prospective_v1_contract.json" in boundary

program=(ROOT/"docs/NEXT_MEASUREMENT_LAYER_PROGRAM_V1.md").read_text()
assert "Annual/exact-point retrospective mechanism decomposition: **HARD STOP**" in program
assert "results/clonal_state_prospective_v1_contract.json" in program
assert "docs/CLONAL_STATE_SAMPLING_PROTOCOL_V1.md" in program
assert "TBOFS near-bottom current: **not accepted as meadow-scale exposure" in program
assert "DIRECT_HYDRODYNAMIC_SAMPLING_PROTOCOL_V1.md" in program
assert "dual_buffer_prospective_v1_contract.json" in program

cons=(ROOT/"manuscript/TAMPA_CONSERVATION_TRANSLATION_V1.md").read_text()
assert "buffer-then-threshold meadow model" not in cons
assert "multiple partially independent degradation axes" in cons
assert "re-recorded / reappearing in the observation record" in cons

disc=(ROOT/"manuscript/TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md").read_text()
assert "Further decomposition of the same annual loss/re-recording table is not treated as a new mechanism test." in disc
assert "plant-condition decline is a one-year precursor" not in disc

print("Tampa new-measurement mechanism boundary: OK")
