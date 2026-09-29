#!/usr/bin/env python3
"""Verify the prospective Tampa clonal-reserve design before future response access."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

c=json.loads((ROOT/"results/clonal_state_prospective_v1_contract.json").read_text())
assert c["status"]=="future_new_measurement_design_not_yet_opened"
assert c["baseline_new_measurements"]["primary_predictor"]["name"]=="rhizome_total_nonstructural_carbohydrate"
assert c["eligibility"]["planning_target_nodes"]==33
assert c["eligibility"]["minimum_primary_analyzable_nodes"]==30
assert c["eligibility"]["minimum_primary_nodes_per_bay"]==8
ctx=c["eligibility"]["recent_2023_2025_feasibility_context"]
assert ctx["recent_thalassia_positive_nodes"]==33
assert ctx["by_water_body"]=={
    "Old Tampa Bay":8,
    "Middle Tampa Bay":11,
    "Lower Tampa Bay":14,
}
assert c["primary_analysis"]["primary_coefficient"]=="standardized_rhizome_TNC"
assert "30 analyzable" in c["primary_analysis"]["confirmatory_gate"]
assert c["design_precision_gate"]["approximate_detectable_partial_r"]["n_24"]==0.57
assert c["design_precision_gate"]["approximate_detectable_partial_r"]["n_33"]==0.49
std=c["baseline_new_measurements"]["standardization"]
for k in (
    "campaign_seasonality","baseline_alignment","tissue_fraction",
    "preservation","assay_batch","time_of_day"
):
    assert k in std
assert "42 consecutive days" in std["campaign_seasonality"]
assert "14 days" in std["baseline_alignment"]
assert "binary reappearance" in c["future_outcome"]["prohibited_primary"]
assert any("season" in x.lower() and "tissue" in x.lower() for x in c["claim_boundary"])

p=(ROOT/"docs/CLONAL_STATE_SAMPLING_PROTOCOL_V1.md").read_text()
assert "Use a census-oriented baseline frame" in p
assert "at least 30 analyzable nodes" in p
assert "at least 8 analyzable" in p
assert "## Seasonal and tissue standardization" in p
assert "## Precision gate" in p
assert "n = 33: about 0.49" in p
assert "future_delta_frequency ~ standardized_rhizome_TNC" in p


sp=json.loads((ROOT/"results/clonal_core_spatial_preflight_v1.json").read_text())
assert sp["status"]=="baseline_spatial_core_design_feasible"
assert sp["registry"]["thalassia_positive_nodes"]==33
assert sp["registry"]["positive_meter_mark_count"]["nodes_with_ge3"]==30
assert sp["registry"]["positive_meter_mark_count"]["nodes_with_lt3"]==3
assert sp["registry"]["by_water_body"]["Old Tampa Bay"]["three_or_more_positive_marks"]==8
assert sp["registry"]["by_water_body"]["Middle Tampa Bay"]["one_positive_mark"]==1
assert sp["registry"]["by_water_body"]["Lower Tampa Bay"]["two_positive_marks"]==1
assert sp["registry"]["by_water_body"]["Lower Tampa Bay"]["one_positive_mark"]==1
assert c["baseline_new_measurements"]["core_spatial_design"]["recent_nodes_with_three_or_more_positive_marks"]==30
assert "inferential unit remains the stable transect node" in p
assert "destructive_sampling_guardrail" in c["eligibility"]
assert "destructive_sampling_sensitivity" in c["future_outcome"]
assert "## Destructive-sampling guardrail" in p

print("Tampa clonal reserve prospective design: OK")
