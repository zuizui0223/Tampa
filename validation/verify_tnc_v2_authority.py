#!/usr/bin/env python3
"""Verify that Tampa TNC v2 is the sole outcome-bearing primary before field collection."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
v1=json.loads((ROOT/"results/clonal_state_prospective_v1_contract.json").read_text())
v2=json.loads((ROOT/"results/clonal_state_prospective_v2_contract.json").read_text())
freeze=json.loads((ROOT/"field/tnc_v2_precollection_freeze.json").read_text())

assert v1["supersession_notice"]["status"]=="superseded_for_outcome_bearing_primary_inference"
assert v1["supersession_notice"]["superseded_by"]=="results/clonal_state_prospective_v2_contract.json"

assert v2["version_authority"]["status"]=="authoritative_outcome_bearing_tnc_primary"
assert v2["version_authority"]["supersedes"]=="results/clonal_state_prospective_v1_contract.json"
assert "Do not revert" in v2["version_authority"]["no_reversion"]
assert v2["eligibility"]["geography"]==[
    "Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay"
]
assert v2["eligibility"]["planning_target_nodes"]==41
assert v2["eligibility"]["minimum_confirmatory_analyzable_nodes"]==36
assert v2["eligibility"]["minimum_confirmatory_nodes_per_bay"]==6
assert v2["primary_analysis"]["confirmatory_gate"].startswith(">=36 analyzable nodes")
assert "four-level factor" in v2["primary_analysis"]["required_controls"][-1]
assert "three water-body indicators" in v2["design_precision_gate"]["planning_model_terms"]
assert v2["design_precision_gate"]["approximate_detectable_partial_r"]["n_36"]==0.4739779676
assert v2["design_precision_gate"]["approximate_detectable_partial_r"]["n_41"]==0.4433248073
assert "prespecified_context_extension" not in v2

ad=v2["secondary_analysis"]["within_transect_anchor_diagnostic"]
assert ad["status"]=="anchor_level_quantitative_diagnostic_feasible"
assert ad["feasibility"]["eligible_nodes"]==38
assert ad["feasibility"]["by_water_body"]["Old Tampa Bay"]==8
assert ad["feasibility"]["by_water_body"]["Middle Tampa Bay"]==10
assert ad["feasibility"]["by_water_body"]["Lower Tampa Bay"]==12
assert ad["feasibility"]["by_water_body"]["Boca Ciega Bay"]==8
assert ad["feasibility"]["passed"] is True
assert (ROOT/"results/tnc_anchor_bb_four_bay_preflight_v1.json").exists()
assert ad["frozen_feasibility_gate"]["minimum_nodes_with_three_distinct_quantitative_anchors"]==36
assert ad["frozen_feasibility_gate"]["minimum_nodes_per_bay"]==6

assert freeze["contract"]=="results/clonal_state_prospective_v2_contract.json"
assert freeze["geography"]==v2["eligibility"]["geography"]
assert freeze["fixed_rules"]["minimum_primary_nodes_total"]==36
assert freeze["fixed_rules"]["minimum_primary_nodes_per_bay"]==6
assert freeze["fixed_rules"]["assay_method"]=="HPLC"
assert freeze["status"]=="PENDING_RESPONSE_INDEPENDENT_PILOT"
assert any(v is None for v in freeze["fields_to_freeze_before_first_outcome_bearing_core"].values())

assert (ROOT/"docs/CLONAL_STATE_SAMPLING_PROTOCOL_V2.md").exists()
p=(ROOT/"docs/CLONAL_STATE_SAMPLING_PROTOCOL_V2.md").read_text()
assert "authoritative outcome-bearing TNC field protocol" in p
assert ">=36 analyzable nodes total" in p
assert ">=6 analyzable nodes in **each** of the four bays" in p
assert "Boca Ciega Bay" in p
assert "Do not choose between v1 and v2 after outcomes are known." in p

readme=(ROOT/"README.md").read_text()
assert "Primary confirmation requires >=36 analyzable nodes and >=6 per bay." in readme

cons=(ROOT/"manuscript/TAMPA_CONSERVATION_TRANSLATION_V1.md").read_text()
assert "The authoritative prospective TNC primary now spans Old, Middle, Lower and Boca Ciega Bay." in cons
assert ">=36 analyzable nodes total with >=6 in each bay" in cons
assert "The confirmatory core remains Old, Middle and Lower Tampa Bay" not in cons

priority=(ROOT/"docs/TAMPA_DECISIVE_TEST_PRIORITY_V1.md").read_text()
assert ">=6 analyzable nodes in each bay" in priority
assert "six-node per-bay floor is a representation guardrail" in priority

status=(ROOT/"docs/THREE_ECOLOGY_PROGRAMS_STATUS_V1.md").read_text()
assert "- >=36 analyzable nodes;" in status
assert "- >=6 per bay;" in status

print("Tampa TNC v2 authority boundary: OK")
