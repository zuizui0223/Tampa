#!/usr/bin/env python3
"""Verify TNC v2 primary analysis freeze metadata."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
freeze=json.loads((ROOT/"field/tnc_v2_primary_analysis_freeze.json").read_text())
contract=json.loads((ROOT/"results/clonal_state_prospective_v2_contract.json").read_text())
hierarchy=json.loads((ROOT/"results/clonal_state_inference_hierarchy_v1.json").read_text())
anchor_freeze=json.loads((ROOT/"field/anchor_tnc_future_bb_analysis_freeze.json").read_text())
resource=json.loads((ROOT/"field/integrated_campaign_resource_freeze.json").read_text())
tnc_pre=json.loads((ROOT/"field/tnc_v2_precollection_freeze.json").read_text())

assert freeze["status"]=="FROZEN_BEFORE_FUTURE_OUTCOME_ACCESS"
assert freeze["paper_level_role"].startswith("supportive network-scale")
assert freeze["inferential_hierarchy_contract"]=="results/clonal_state_inference_hierarchy_v1.json"
assert hierarchy["decisive_primary"]["analysis_code"]=="analysis/72_anchor_tnc_future_bb_diagnostic.py"
assert hierarchy["supportive_network_test"]["analysis_code"]=="analysis/64_tnc_v2_primary_analysis.py"
assert anchor_freeze["role"].startswith("paper-level decisive within-meadow state-augmentation primary")
assert freeze["script_path"]=="analysis/64_tnc_v2_primary_analysis.py"
assert freeze["uncertainty"]["repetitions"]==10000
assert freeze["uncertainty"]["seed"]==20261003
assert freeze["replication_gate"]["minimum_total"]==36
assert freeze["replication_gate"]["minimum_per_bay"]==6
assert freeze["support_rule"]["one_sided_test_allowed"] is False
assert contract["primary_analysis"]["analysis_freeze"]=="field/tnc_v2_primary_analysis_freeze.json"
assert "10,000-replicate water-body-stratified" in contract["primary_analysis"]["uncertainty"]
assert resource["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]["tnc_v2_primary_analysis_code_frozen"] is True
assert resource["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]["node_level_uncertainty_code_frozen"] is True
assert tnc_pre["fields_to_freeze_before_first_outcome_bearing_core"]["assay_batch_randomization_rule"]

print("Tampa TNC v2 primary analysis freeze: OK")
