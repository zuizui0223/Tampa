#!/usr/bin/env python3
"""Static consistency checks for Tampa integrated campaign design."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

x=json.loads((ROOT/"results/integrated_field_campaign_v1_contract.json").read_text())
freeze=json.loads((ROOT/"field/integrated_campaign_resource_freeze.json").read_text())
tnc=json.loads((ROOT/"results/clonal_state_prospective_v2_contract.json").read_text())
evt=json.loads((ROOT/"results/event_stress_debt_prospective_v1_contract.json").read_text())
opt=json.loads((ROOT/"results/optical_microenvironment_prospective_v1_contract.json").read_text())
hyd=json.loads((ROOT/"results/direct_hydrodynamic_prospective_v1_contract.json").read_text())

assert x["status"]=="resource_inventory_and_response_independent_pilots_pending"
assert x["source_contracts"]["authoritative_tnc"]=="results/clonal_state_prospective_v2_contract.json"
assert x["shared_calendar"]["event_optical_window"]["start_month_day"]=="07-24"
assert x["shared_calendar"]["event_optical_window"]["end_month_day"]=="09-03"
assert x["shared_calendar"]["event_optical_window"]["target_days"]==42
assert "third redundant TNC round" in x["shared_calendar"]["authoritative_tnc_baseline_reuse"]
assert x["shared_tnc_sampling"]["core_three_rounds"]==2
assert x["shared_tnc_sampling"]["boca_ciega_rounds"]==1
assert "Do not add" in x["shared_tnc_sampling"]["no_sham_coring"]
assert "222" in x["shared_tnc_sampling"]["round_assignment"]["planned_full_frame_example"]

assert x["mechanism_execution_gates"]["tnc_v2"]["confirmatory_minimum_total"]==tnc["eligibility"]["minimum_confirmatory_analyzable_nodes"]==36
assert x["mechanism_execution_gates"]["tnc_v2"]["confirmatory_minimum_per_bay"]==tnc["eligibility"]["minimum_confirmatory_nodes_per_bay"]==6
assert x["mechanism_execution_gates"]["event_stress"]["confirmatory_minimum_total"]==evt["sampling_frame"]["minimum_confirmatory_nodes"]==30
assert x["mechanism_execution_gates"]["event_stress"]["confirmatory_minimum_per_bay"]==evt["sampling_frame"]["minimum_confirmatory_nodes_per_bay"]==8
assert x["mechanism_execution_gates"]["optical"]["confirmatory_minimum_total"]==opt["sampling_frame"]["minimum_confirmatory_nodes"]==30
assert x["mechanism_execution_gates"]["optical"]["confirmatory_minimum_per_bay"]==opt["sampling_frame"]["minimum_confirmatory_nodes_per_bay"]==8
ref=opt["secondary_optical_decomposition"]["paired_above_canopy_reference"]
assert x["mechanism_execution_gates"]["optical"]["paired_reference_subset"]["minimum_total"]==ref["minimum_analyzable_nodes"]==12
assert x["mechanism_execution_gates"]["optical"]["paired_reference_subset"]["minimum_per_bay"]==ref["minimum_nodes_per_bay"]==3
assert x["mechanism_execution_gates"]["hydrodynamic"]["role"].startswith("Separate module")
assert x["module_priority_and_failure_policy"]["priority_order"][0]=="authoritative four-bay TNC v2 primary"
assert x["module_priority_and_failure_policy"]["priority_order"][1]=="core-three optical primary if full confirmatory capacity exists"
assert x["module_priority_and_failure_policy"]["priority_order"][2]=="core-three event-stress primary if full confirmatory capacity exists"
assert "optical has the frozen scientific priority over event-stress" in x["module_priority_and_failure_policy"]["priority_consistency_note"]
assert "disabled" in x["module_priority_and_failure_policy"]["optional_module_rule"]
assert x["mechanism_execution_gates"]["optical"]["paired_reference_subset"]["role"].startswith("secondary attribution")
assert "97.5%" in x["paper_level_forcing_family"]["integrated_family_rule"]
assert "Do not compare" in x["paper_level_forcing_family"]["no_ranking"]

assert freeze["contract"]=="results/integrated_field_campaign_v1_contract.json"
assert freeze["status"]=="PENDING_RESPONSE_INDEPENDENT_RESOURCE_AUDIT"
assert freeze["fixed_rules"]["tnc_v2_minimum_total"]==36
assert freeze["fixed_rules"]["tnc_v2_minimum_per_bay"]==6
assert freeze["fixed_rules"]["event_minimum_total"]==30
assert freeze["fixed_rules"]["event_minimum_per_bay"]==8
assert freeze["fixed_rules"]["optical_minimum_total"]==30
assert freeze["fixed_rules"]["optical_minimum_per_bay"]==8
assert freeze["fixed_rules"]["optical_reference_minimum_total"]==12
assert freeze["fixed_rules"]["optical_reference_minimum_per_bay"]==3
assert freeze["fixed_rules"]["third_redundant_tnc_round_allowed"] is False
assert freeze["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]["optical_reference_nodes_by_bay"] is None
ff=freeze["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]
assert ff["event_module_intent"] is None
assert ff["optical_module_intent"] is None
assert ff["optical_attribution_intent"] is None
assert ff["tnc_v2_primary_analysis_code_frozen"] is True
assert ff["node_level_uncertainty_code_frozen"] is True
assert (ROOT/"field/tnc_v2_primary_analysis_freeze.json").exists()
assert ff["forcing_family_analysis_code_frozen"] is True
assert "confirmatory" in freeze["fixed_rules"]["module_intent_allowed_values"]
assert "disabled" in freeze["fixed_rules"]["module_intent_allowed_values"]

doc=(ROOT/"docs/INTEGRATED_FIELD_CAMPAIGN_V1.md").read_text()
assert "33 * 6 + 8 * 3 = 222" in doc
assert "A third redundant TNC round is prohibited" in doc
assert "Sequentially rotating a smaller logger pool" in doc
assert "Hydrodynamic measurement is not a prerequisite" in doc
assert "four-bay TNC v2" in doc

# The readiness audit must be able to represent the deliberately pending state.
assert (ROOT/"validation/validate_integrated_campaign_readiness.py").exists()
print("Tampa integrated campaign design: OK")
