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
assert clonal["eligibility"]["planning_target_nodes"]==33
assert clonal["eligibility"]["minimum_confirmatory_analyzable_nodes"]==30
assert clonal["eligibility"]["minimum_confirmatory_nodes_per_bay"]==8
assert clonal["eligibility"]["recent_2023_2025_feasibility_context"]["recent_thalassia_positive_nodes"]==33
assert clonal["baseline_new_measurements"]["temporal_standardization"]["campaign_window"].startswith("Collect all primary TNC samples within one predeclared <=28-day")
assert "14 days" in clonal["baseline_new_measurements"]["temporal_standardization"]["baseline_alignment"]
assert clonal["baseline_new_measurements"]["analytical_standardization"]["preferred_assay"].startswith("HPLC")
assert "leaf %N" in clonal["baseline_new_measurements"]["nutrient_state_diagnostic"]["measurements"]
assert clonal["design_precision_gate"]["approximate_detectable_partial_r"]["n_33"]==0.49
assert clonal["primary_analysis"]["confirmatory_gate"].startswith(">=30 analyzable nodes")
assert clonal["primary_analysis"]["support_rule"]["supported"]=="interval entirely above 0"
assert clonal["primary_analysis"]["support_rule"]["contradicted_direction"]=="interval entirely below 0"
assert clonal["baseline_new_measurements"]["genet_identity_diagnostic"]["role"].startswith("secondary interpretation diagnostic")
assert "multilocus genotypes" in " ".join(clonal["baseline_new_measurements"]["genet_identity_diagnostic"]["node_summary"])
assert "does not prove" in clonal["baseline_new_measurements"]["genet_identity_diagnostic"]["interpretation"]["repeated_genotype"]
assert any("not proof of resource translocation" in x for x in clonal["claim_boundary"])
assert clonal["baseline_new_measurements"]["core_spatial_design"]["status"]=="baseline_spatial_core_design_feasible"
assert clonal["baseline_new_measurements"]["core_spatial_design"]["recent_nodes_with_three_or_more_positive_marks"]==30
assert clonal["baseline_new_measurements"]["core_spatial_design"]["recent_nodes_requiring_sparse_fallback"]==3
assert "destructive_sampling_guardrail" in clonal["eligibility"]
assert "destructive_sampling_sensitivity" in clonal["future_outcome"]
assert (ROOT/"results/clonal_core_spatial_preflight_v1.json").exists()
sp=json.loads((ROOT/"results/clonal_core_spatial_preflight_v1.json").read_text())
assert sp["status"]=="baseline_spatial_core_design_feasible"
assert sp["registry"]["thalassia_positive_nodes"]==33
assert sp["registry"]["positive_meter_mark_count"]["nodes_with_ge3"]==30
assert sp["registry"]["positive_meter_mark_count"]["nodes_with_lt3"]==3
assert sp["registry"]["by_water_body"]["Old Tampa Bay"]["three_or_more_positive_marks"]==8
assert sp["registry"]["by_water_body"]["Middle Tampa Bay"]["one_positive_mark"]==1
assert sp["registry"]["by_water_body"]["Lower Tampa Bay"]["two_positive_marks"]==1
assert sp["registry"]["by_water_body"]["Lower Tampa Bay"]["one_positive_mark"]==1
assert "one-sided" in clonal["primary_analysis"]["support_rule"]["note"]
assert clonal["baseline_new_measurements"]["temporal_standardization"]["historical_feasibility"]["observed_2025_survey_span_days"]==71
assert clonal["baseline_new_measurements"]["temporal_standardization"]["historical_feasibility"]["densest_historical_28_day_window_nodes"]==19
assert clonal["baseline_new_measurements"]["temporal_standardization"]["baseline_survey_plan"]["preferred"].startswith("Perform the fixed-transect baseline survey and TNC coring on the same day")
assert "dedicated additional baseline" in clonal["baseline_new_measurements"]["temporal_standardization"]["baseline_survey_plan"]["routine_schedule_boundary"]

ct=json.loads((ROOT/"results/clonal_tnc_timing_feasibility_v1.json").read_text())
assert ct["status"]=="historical_routine_timing_too_dispersed_for_confirmatory_tnc_baseline"
assert ct["registry"]["recent_thalassia_positive_nodes"]==33
assert ct["latest_positive_by_year"]["2025"]["span_days"]==71
assert ct["densest_historical_28_day_window"]["nodes"]==19
assert ct["prospective_decision"]["campaign_window_days"]==28
assert ct["prospective_decision"]["baseline_alignment_days_each_side"]==14
assert clonal["baseline_new_measurements"]["core_replication_boundary"]["inferential_unit"]=="stable transect node"
assert "independent genets" in clonal["baseline_new_measurements"]["core_replication_boundary"]["genetic_boundary"]
assert clonal["secondary_analysis"]["meristem_bank_hypothesis"]["predictor"].startswith("predeclared node-level rhizome meristem")
assert "not a rescue" in clonal["secondary_analysis"]["meristem_bank_hypothesis"]["role"]

# Independent physical-layer gate: TBOFS was tested response-blind and rejected
# as the primary meadow-scale near-bed exposure layer.
tbofs=json.loads((ROOT/"results/tbofs_hydrodynamic_preflight_v1.json").read_text())
assert tbofs["status"]=="all_network_source_gate_failed"
assert tbofs["response_blind"] is True
assert tbofs["all_71_nodes"]["mapped_nodes"]==71
assert tbofs["original_gate"]["passed"] is False
assert tbofs["original_gate"]["max_distance_lte_2km"] is False

depth=json.loads((ROOT/"results/tbofs_depth_relevance_audit_v1.json").read_text())
assert depth["status"]=="nearbed_meadow_interpretation_not_supported"
assert depth["response_blind"] is True
assert depth["tri_bay_core"]["nodes"]==47
assert depth["tri_bay_core"]["model_deeper_than_observed_nodes"]==47
assert depth["tri_bay_core"]["model_bathymetry_median_across_nodes_m"] > depth["tri_bay_core"]["observed_depth_median_across_nodes_m"]

direct=json.loads((ROOT/"results/direct_hydrodynamic_prospective_v1_contract.json").read_text())
assert direct["status"]=="future_new_measurement_design_not_yet_deployed"
assert direct["primary_analysis"]["primary_coefficient"]=="attenuation_p90"
assert direct["eligibility"]["planning_target_nodes"]==40
assert direct["eligibility"]["minimum_primary_analyzable_nodes"]==30
assert direct["eligibility"]["minimum_primary_nodes_per_bay"]==8
assert direct["eligibility"]["recent_2023_2025_feasibility_context"]["recent_thalassia_positive_nodes"]==33
assert direct["design_precision_gate"]["approximate_detectable_partial_r"]["n_33"]==0.49
assert "wave_current_resolution_gate" in direct["new_measurements"]["deployment"]
assert any("oscillatory horizontal RMS speed" in x for x in direct["secondary_mechanism_support"]["wave_current_decomposition"]["metrics"])
assert "binary reappearance" in direct["future_outcome"]["prohibited_primary"]
assert (ROOT/"docs/DIRECT_HYDRODYNAMIC_SAMPLING_PROTOCOL_V1.md").exists()
assert direct["new_measurements"]["canopy_counterfactual_control"]["target_nodes"]==18
assert direct["new_measurements"]["canopy_counterfactual_control"]["minimum_analyzable_nodes"]==12
assert direct["new_measurements"]["canopy_counterfactual_control"]["minimum_nodes_per_bay"]==3
assert direct["new_measurements"]["canopy_counterfactual_control"]["spatial_preflight"]["status"]=="geographic_edge_feasibility_pass"
assert direct["new_measurements"]["canopy_counterfactual_control"]["spatial_preflight"]["candidate_nodes_with_mapped_edge_within_100m"]==39
assert "excess_canopy_attenuation_p90" in direct["new_measurements"]["canopy_counterfactual_control"]["metrics"]
assert "gate_A_physical" in direct["ecosystem_engineering_feedback_gate"]
assert "gate_B_future_ecology" in direct["ecosystem_engineering_feedback_gate"]
assert any("boundary-layer shear" in x for x in direct["claim_boundary"])

bare=json.loads((ROOT/"results/bare_control_spatial_preflight_v1.json").read_text())
assert bare["status"]=="geographic_edge_feasibility_pass"
assert bare["response_independent"] is True
assert bare["registry"]["vegetated_meter_marks"]==762
assert bare["registry"]["mapped_state_compatible_nodes"]==39
assert bare["candidate_gate"]["candidate_nodes"]==39
assert bare["candidate_gate"]["minimum_candidates_in_any_bay"]==12
assert bare["candidate_gate"]["passed"] is True
assert bare["candidate_gate"]["maximum_edge_distance_m"]==100.0
assert bare["candidate_gate"]["minimum_nodes"]==12
assert bare["candidate_gate"]["minimum_nodes_per_bay"]==3
assert (ROOT/"docs/BARE_CONTROL_FIELD_RECONNAISSANCE_V1.md").exists()
assert bare["candidate_gate"]["by_water_body"]["Old Tampa Bay"]["bare_edge_candidate_nodes_100m"]==12
assert bare["candidate_gate"]["by_water_body"]["Middle Tampa Bay"]["bare_edge_candidate_nodes_100m"]==12
assert bare["candidate_gate"]["by_water_body"]["Lower Tampa Bay"]["bare_edge_candidate_nodes_100m"]==15
assert bare["primary_thalassia_counterfactual_feasibility"]["thalassia_positive_nodes_with_100m_candidate"]==31
assert bare["coordinate_semantics"]["correction"].startswith("Darwin Core Point coordinates repeat meter mark 0")

rep=json.loads((ROOT/"results/representative_sensor_placement_preflight_v1.json").read_text())
assert rep["status"]=="representative_placement_both_gates_pass"
assert rep["response_independent"] is True
assert rep["selection"]["edge_distance_used_for_selection"] is False
assert rep["gate"]["vegetated_representative_candidate_nodes"]==21
assert rep["gate"]["thalassia_representative_candidate_nodes"]==19
assert rep["gate"]["by_water_body"]["Old Tampa Bay"]["thalassia_representative_candidates_100m"]==3
assert rep["gate"]["by_water_body"]["Middle Tampa Bay"]["thalassia_representative_candidates_100m"]==7
assert rep["gate"]["by_water_body"]["Lower Tampa Bay"]["thalassia_representative_candidates_100m"]==9
assert direct["new_measurements"]["canopy_counterfactual_control"]["representative_placement_preflight"]["status"]=="representative_placement_both_gates_pass"
assert direct["eligibility"]["vegetated_sensor_placement"]["prohibited_rescue"].startswith("Do not move")

frame=json.loads((ROOT/"results/functional_insurance_sampling_preflight_v1.json").read_text())
assert frame["status"]=="recent_sampling_frame_supports_split_primary_and_functional_cohorts"
assert frame["registry"]["recent_thalassia_positive_nodes"]==33
assert frame["registry"]["recent_vegetated_nodes"]==40
assert frame["registry"]["recent_alternative_only_nodes"]==7
assert frame["decision"]["recent_frame_passes_30_node_8_per_bay_primary_precision_gate"] is True

boundary=(ROOT/"docs/ECOLOGICAL_MECHANISM_BOUNDARY_V1.md").read_text()
assert "Observation-state reappearance is not ecological recovery." in boundary
assert "Do **not** add another retrospective decomposition" in boundary
assert "Below-ground reserve / clonal state" in boundary
assert "Canopy hydrodynamic self-buffering" in boundary
assert "TBOFS near-bottom current as meadow exposure" in boundary

program=(ROOT/"docs/NEXT_MEASUREMENT_LAYER_PROGRAM_V1.md").read_text()
assert "Annual/exact-point retrospective mechanism decomposition: **HARD STOP**" in program
assert "results/clonal_state_prospective_v1_contract.json" in program
assert "docs/CLONAL_STATE_SAMPLING_PROTOCOL_V1.md" in program
assert "NOAA TBOFS near-bottom current: **not accepted as meadow-scale exposure" in program
assert "Direct paired canopy/ambient velocity layer" in program

cons=(ROOT/"manuscript/TAMPA_CONSERVATION_TRANSLATION_V1.md").read_text()
assert "buffer-then-threshold meadow model" not in cons
assert "multiple partially independent degradation axes" in cons
assert "re-recorded / reappearing in the observation record" in cons

disc=(ROOT/"manuscript/TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md").read_text()
assert "Further decomposition of the same annual loss/re-recording table is not treated as a new mechanism test." in disc
assert "plant-condition decline is a one-year precursor" not in disc

print("Tampa new-measurement mechanism boundary: OK")
