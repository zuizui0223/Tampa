#!/usr/bin/env python3
"""Verify frozen response-independent optical pilot acceptance contract."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/"results/optical_pilot_acceptance_v1_contract.json").read_text())

assert c["status"]=="response_independent_method_pilot_not_yet_run"
assert c["calibration_gate"]["minimum_irradiance_levels"]==5
assert c["calibration_gate"]["minimum_paired_observations_per_sensor"]==50
a=c["calibration_gate"]["post_correction_acceptance"]
assert a["r_squared_min"]==0.995
assert a["median_absolute_relative_error_max"]==0.05
assert a["p95_absolute_relative_error_max"]==0.10

v=c["vertical_representativeness_gate"]
assert v["pilot_nodes_min"]==12
assert v["pilot_nodes_min_per_bay"]==3
assert v["candidate_levels"]==[0.25,0.5,0.75]
assert v["acceptance"]["median_absolute_relative_error_max"]==0.15
assert v["acceptance"]["fraction_node_days_with_absolute_relative_error_lte_0_25_min"]==0.80

p=c["placement_repeatability_gate"]
assert p["repeat_mock_deployments_per_node_min"]==3
assert p["fraction_placements_within_tolerance_min"]==0.90

f=c["fouling_maintenance_gate"]
assert f["minimum_submerged_pilot_days"]==14
assert f["candidate_service_intervals_days"]==[14,7,3]

d=c["daily_dli_qc"]
assert d["minimum_scheduled_daylight_observation_fraction"]==0.90
assert d["maximum_continuous_daylight_gap_minutes"]==30
assert d["node_primary_minimum_valid_days"]==30

opt=json.loads((ROOT/"results/optical_microenvironment_prospective_v1_contract.json").read_text())
assert opt["primary_exposure"]["name"]=="mean_daily_within_canopy_dli"
assert opt["deployment"]["within_canopy_sensor"]["vertical_representativeness_pilot"]["purpose"].startswith("Verify")
print("Tampa optical pilot acceptance contract: OK")
