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
assert "binary reappearance" in direct["future_outcome"]["prohibited_primary"]
assert (ROOT/"docs/DIRECT_HYDRODYNAMIC_SAMPLING_PROTOCOL_V1.md").exists()

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
