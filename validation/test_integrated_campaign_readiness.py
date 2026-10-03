#!/usr/bin/env python3
"""Synthetic branch tests for integrated campaign readiness logic."""
from __future__ import annotations
import copy, json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/"validation/validate_integrated_campaign_readiness.py"
CONTRACT=ROOT/"results/integrated_field_campaign_v1_contract.json"
BASE_FREEZE=json.loads((ROOT/"field/integrated_campaign_resource_freeze.json").read_text())
BASE_TNC=json.loads((ROOT/"field/tnc_v2_precollection_freeze.json").read_text())

BAYS3=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
BAYS4=BAYS3+("Boca Ciega Bay",)

def nodes():
    by={
      "Old Tampa Bay":[f"O{i}" for i in range(1,9)],
      "Middle Tampa Bay":[f"M{i}" for i in range(1,12)],
      "Lower Tampa Bay":[f"L{i}" for i in range(1,15)],
      "Boca Ciega Bay":[f"B{i}" for i in range(1,9)],
    }
    return by

def flat(by,bays):
    return [n for b in bays for n in by[b]]

def dates(ns,value):
    return {n:value for n in ns}

def complete_tnc_freeze():
    x=copy.deepcopy(BASE_TNC)
    f=x["fields_to_freeze_before_first_outcome_bearing_core"]
    f.update({
      "campaign_start_date":"2027-09-01",
      "campaign_end_date":"2027-09-10",
      "horizontal_rhizome_tissue_class":"horizontal_rhizome_standard_v1",
      "minimum_perpendicular_transect_offset_m":1.0,
      "core_diameter_cm":10.0,
      "core_depth_cm":20.0,
      "maximum_collection_to_preservation_minutes":30,
      "preservation_method":"frozen_v1",
      "assay_batch_randomization_rule":"blocked_random_v1",
    })
    return x

def base_resource(event_intent, optical_intent, attr_intent):
    x=copy.deepcopy(BASE_FREEZE)
    f=x["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]
    by=nodes(); tnc=flat(by,BAYS4)
    f.update({
      "event_module_intent":event_intent,
      "optical_module_intent":optical_intent,
      "optical_attribution_intent":attr_intent,
      "final_four_bay_tnc_nodes_by_bay":by,
      "tnc_v2_primary_analysis_code_frozen":True,
      "node_level_uncertainty_code_frozen":True,
      "preservation_capacity_for_planned_core_samples":300,
      "four_bay_authoritative_tnc_baseline_calendar":dates(flat(by,BAYS3),"2027-09-03") | dates(by["Boca Ciega Bay"],"2027-09-04"),
      "four_bay_baseline_transect_calendar":dates(flat(by,BAYS3),"2027-09-03") | dates(by["Boca Ciega Bay"],"2027-09-04"),
    })
    return x

def add_forcing(x,event=True,optical=True,attr=False,temp_systems=33):
    f=x["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]
    by=nodes(); core={b:by[b] for b in BAYS3}; ns=flat(by,BAYS3)
    if event:
        f.update({
          "final_core_three_event_nodes_by_bay":core,
          "complete_temperature_salinity_node_systems_available":temp_systems,
          "temperature_salinity_sensor_model_and_calibration_rule":"event_sensor_rule_v1",
          "event_sensor_geometry_pilot_complete":True,
          "event_primary_analysis_code_frozen":True,
        })
    if optical:
        f.update({
          "final_core_three_optical_nodes_by_bay":core,
          "within_canopy_par_node_systems_available":33,
          "par_sensor_model_and_calibration_rule":"par_rule_v1",
          "optical_vertical_profile_pilot_complete":True,
          "optical_primary_analysis_code_frozen":True,
        })
    if event or optical:
        f.update({
          "pre_post_core_offset_geometry_frozen":True,
          "maximum_attempted_cores_per_node_across_pre_post_rounds":8,
          "core_three_pre_visit_route_calendar":dates(ns,"2027-07-23"),
          "core_three_post_visit_route_calendar":dates(ns,"2027-09-03"),
          "core_three_logger_deployment_calendar":dates(ns,"2027-07-24"),
          "core_three_logger_retrieval_calendar":dates(ns,"2027-09-03"),
        })
    if event and optical:
        f["forcing_family_analysis_code_frozen"]=True
    if attr:
        refs={
          "Old Tampa Bay":by["Old Tampa Bay"][:4],
          "Middle Tampa Bay":by["Middle Tampa Bay"][:4],
          "Lower Tampa Bay":by["Lower Tampa Bay"][:4],
        }
        f.update({
          "optical_reference_nodes_by_bay":refs,
          "above_canopy_par_reference_systems_available":12,
          "optical_attribution_analysis_code_frozen":True,
        })
    return x

def run_case(name,resource,expected):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        rf=td/"resource.json"; tf=td/"tnc.json"; out=td/"out.json"
        rf.write_text(json.dumps(resource))
        tf.write_text(json.dumps(complete_tnc_freeze()))
        cp=subprocess.run([
          sys.executable,str(VALIDATOR),
          "--freeze",str(rf),"--tnc-freeze",str(tf),
          "--contract",str(CONTRACT),"--out",str(out)
        ],cwd=ROOT,text=True,capture_output=True)
        if cp.returncode!=0:
            raise RuntimeError(f"{name}: validator crashed\nSTDOUT={cp.stdout}\nSTDERR={cp.stderr}")
        res=json.loads(out.read_text())
        if res["status"]!=expected:
            raise AssertionError(f"{name}: {res['status']} != {expected}\n{json.dumps(res,indent=2)}")
        print(name,res["status"],res.get("module_status"))

def main():
    # TNC-only decisive campaign: optional forcing modules disabled.
    run_case(
      "tnc_only_ready",
      base_resource("disabled","disabled","disabled"),
      "READY_TNC_CONFIRMATORY_CAMPAIGN",
    )

    # Both forcing primaries confirmatory, secondary above-canopy attribution disabled.
    run_case(
      "event_optical_ready_attribution_disabled",
      add_forcing(base_resource("confirmatory","confirmatory","disabled"),True,True,False,33),
      "READY_TNC_CONFIRMATORY_CAMPAIGN",
    )

    # Complete freeze but declared confirmatory event module lacks one simultaneous system.
    run_case(
      "event_capacity_failure",
      add_forcing(base_resource("confirmatory","disabled","disabled"),True,False,False,32),
      "STOP_MODULE_INTENT_MISMATCH",
    )

if __name__=="__main__":
    main()
