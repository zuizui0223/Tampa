#!/usr/bin/env python3
"""Verify the prospective event-scale hot-fresh stress-debt design."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/"results/event_stress_debt_prospective_v1_contract.json").read_text())

assert c["status"]=="future_new_measurement_design_not_yet_deployed"
assert c["sampling_frame"]["planning_nodes"]==33
assert c["sampling_frame"]["minimum_confirmatory_nodes"]==30
assert c["sampling_frame"]["minimum_confirmatory_nodes_per_bay"]==8

d=c["deployment"]
assert d["target_duration_days"]==42
assert d["minimum_valid_common_overlap_days"]==35
assert d["maximum_nominal_sampling_interval_minutes"]==15
assert d["valid_coverage_rule"].startswith("Each confirmatory node must retain >=85%")

r=c["reserve_sampling"]
assert ">=3" in r["pre_exposure"]
assert ">=3" in r["post_exposure"]
assert r["inferential_unit"].startswith("stable transect node")
pair=r["temporal_pairing"]
assert pair["target_pre_post_interval_days"]==42
assert pair["confirmatory_min_interval_days"]==39
assert pair["confirmatory_max_interval_days"]==45
assert "descriptive-only" in pair["rule"]
guard=r["combined_destructive_sampling_guardrail"]
assert "Exactly two" in guard["total_rounds"]
assert "3 valid pre-exposure + 3 valid post-exposure" in guard["total_core_count"]
assert "permanent monitoring transect" in guard["permanent_transect_buffer"]
assert "maximum cumulative disturbed area" in guard["cumulative_footprint"]
assert "measurement-intervention concern" in guard["interpretation_boundary"]

e=c["primary_exposure"]
assert e["name"]=="joint_hot_fresh_hours_30_25"
assert "temperature >=30 C AND salinity <=25 ppt" in e["definition"]
assert e["nonestimable_variation_gate"]["minimum_nodes_with_nonzero_joint_exposure"]==10
assert e["nonestimable_variation_gate"]["minimum_bays_with_nonzero_joint_exposure"]==2
wb=e["nonestimable_variation_gate"]["within_bay_identifiability"]
assert wb["minimum_bays_with_node_scale_variation"]==2
assert wb["minimum_analyzable_nodes_in_each_counted_bay"]==6
assert wb["minimum_distinct_exposure_values_in_each_counted_bay"]==3
assert "Do not remove water_body" in wb["failure_rule"]
assert "Do not lower/raise either threshold" in e["nonestimable_variation_gate"]["rule"]

p=c["primary_analysis"]
assert p["model"]=="tnc_post ~ tnc_pre + joint_hot_fresh_hours_30_25 + water_body"
assert p["expected_direction"]=="negative"
assert p["support_rule"]["supported"]=="two-sided 95% interval entirely below 0"
assert p["support_rule"]["contradicted_direction"]=="two-sided 95% interval entirely above 0"
assert "one-sided" in p["support_rule"]["boundary"]

assert c["design_precision_gate"]["approximate_detectable_partial_r"]["n_33"]==0.45
assert c["secondary_future_ecology"]["boundary"].startswith("Cannot rescue")
assert c["relationship_to_otb_temperature_pilot"]["pr"]==38
assert "extreme-effect" in c["relationship_to_otb_temperature_pilot"]["role"]

chain=c["relationship_to_clonal_tnc_program"]["two_gate_chain"]
assert "event-stress" in chain["gate_A_event_to_reserve"]
assert "clonal contract" in chain["gate_B_reserve_to_future_state"]
assert "not formal mediation" in chain["both_supported"]

dyn=c["relationship_to_clonal_tnc_program"]["dynamic_reserve_change_future_diagnostic"]
assert dyn["model"]=="future_delta_frequency ~ baseline_frequency_post + tnc_post + delta_tnc_42d + water_body"
assert dyn["focal_coefficient"]=="delta_tnc_42d"
assert dyn["support_rule"]["supported"]=="two-sided 95% interval entirely above 0"
assert "current post-exposure reserve level" in dyn["purpose"]
assert "cannot rescue" in dyn["no_rescue_rule"].lower()

protocol=(ROOT/"docs/EVENT_SCALE_STRESS_DEBT_PROTOCOL_V1.md").read_text()
assert "same Tampa definition" in protocol
assert "common calendar overlap" in protocol
assert "Pre-exposure" in protocol and "Post-exposure" in protocol
assert "Do not alter thresholds" in protocol
assert "Separate optical mechanism" in protocol

hyp=(ROOT/"docs/MECHANISM_COMPETING_HYPOTHESES_V1.md").read_text()
assert "## H3. Event-scale hot-fresh stress debt" in hyp
assert "tnc_post" in hyp
assert "PAR is not added here" in hyp


cal=json.loads((ROOT/"results/event_stress_calendar_preflight_v1.json").read_text())
assert cal["status"]=="calendar_selected_from_response_independent_exposure_climatology"
assert cal["response_independent"] is True
assert cal["selected_window"]["start_md"]=="07-24"
assert cal["selected_window"]["end_md"]=="09-03"
assert cal["selected_window"]["OTB_nonzero_fraction"]==0.632
assert cal["selected_window"]["MTB_nonzero_fraction"]==0.3633333333
assert cal["selected_window"]["LTB_nonzero_fraction"]==0.0
assert cal["selected_window"]["historical_year_fraction_with_events_in_at_least_2_bays"]==0.64
assert c["deployment"]["calendar_preflight"]["frozen_start_month_day"]=="07-24"
assert c["deployment"]["calendar_preflight"]["frozen_end_month_day"]=="09-03"
assert c["deployment"]["calendar_preflight"]["historical_nonzero_station_year_fraction"]["Lower Tampa Bay"]==0.0
assert "July 24" in c["deployment"]["primary_exposure_window"]
assert "non-estimable" in c["primary_exposure"]["nonestimable_variation_gate"]["rule"]

print("Tampa event-scale stress-debt design: OK")
