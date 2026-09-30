#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/"results/optical_microenvironment_prospective_v1_contract.json").read_text())

assert c["status"]=="future_new_measurement_design_not_yet_deployed"
assert c["sampling_frame"]["planning_nodes"]==33
assert c["sampling_frame"]["minimum_confirmatory_nodes"]==30
assert c["sampling_frame"]["minimum_confirmatory_nodes_per_bay"]==8
sel=c["sampling_frame"]["sensor_meter_mark_selection"]
assert sel["primary_thalassia_rule"].startswith("Among contemporaneously Thalassia-positive meter marks")
assert "Do not move" in sel["prohibited_rescue"]

d=c["deployment"]
assert d["target_duration_days"]==42
assert d["minimum_valid_common_overlap_days"]==35
assert d["maximum_nominal_sampling_interval_minutes"]==15
assert ">=85%" in d["coverage_rule"]
assert d["within_canopy_sensor"]["placement"].startswith("One fixed response-independent")

e=c["primary_exposure"]
assert e["name"]=="mean_daily_within_canopy_dli"
assert e["unit"]=="mol photons m-2 d-1"
assert "No low-light threshold" in e["no_threshold_search"]
assert e["minimum_variation_gate"]["minimum_distinct_node_exposure_values"]==10
assert e["minimum_variation_gate"]["minimum_bays_with_node_scale_variation"]==2

p=c["primary_analysis"]
assert p["model"]=="tnc_post ~ tnc_pre + mean_daily_within_canopy_dli + water_body"
assert p["expected_direction"]=="positive"
assert p["support_rule"]["supported"]=="two-sided 95% interval entirely above 0"
assert p["support_rule"]["contradicted_direction"]=="two-sided 95% interval entirely below 0"
assert "one-sided" in p["support_rule"]["boundary"]

assert c["reserve_response"]["temporal_pairing"].startswith("Confirmatory pre/post TNC interval remains 39-45 days")
assert c["secondary_optical_decomposition"]["epiphyte_biomass"]["role"].startswith("Secondary explanation")
assert c["competing_epiphyte_interpretations"]["decision_boundary"].startswith("Do not infer epiphyte stress")
assert c["relationship_to_event_stress"]["separate_primary_tests"] is True
assert "cannot be rescued" in c["relationship_to_event_stress"]["no_rescue_rule"]
assert "binary" in c["relationship_to_future_meadow_state"]["boundary"].lower()
assert "purely static site-template" in c["site_template_boundary"]["statement"]

protocol=(ROOT/"docs/OPTICAL_MICROENVIRONMENT_PROTOCOL_V1.md").read_text()
assert "mean_daily_within_canopy_dli" in protocol
assert "No primary light threshold" in protocol
assert "mature-canopy marker" in protocol
assert "paired leaf-optics" in protocol
assert "Site-template boundary" in protocol

print("Tampa optical microenvironment design: OK")
