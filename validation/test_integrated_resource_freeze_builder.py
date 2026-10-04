#!/usr/bin/env python3
"""Synthetic end-to-end tests for integrated resource-freeze raw pipeline."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable
BUILD=ROOT/"analysis/73_build_integrated_resource_freeze.py"
READY=ROOT/"validation/validate_integrated_campaign_readiness.py"
BASE_RESOURCE=json.loads((ROOT/"field/integrated_campaign_resource_freeze.json").read_text())
BASE_TNC=json.loads((ROOT/"field/tnc_v2_precollection_freeze.json").read_text())
OPTICAL=ROOT/"field/optical_pilot_freeze.json"
BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")

def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")

def nodes():
    out={}; k=0
    for b in BAYS:
        out[b]=[]
        for _ in range(9):
            k+=1
            out[b].append(f"SYN{k:02d}")
    return out

def execution():
    by=nodes()
    flat=[n for b in BAYS for n in by[b]]
    tnc={n:"2027-09-03" for n in flat}
    base={n:"2027-09-03" for n in flat}
    return {
      "schema":"tampa.tnc_v2_contemporaneous_execution_manifest_v1",
      "status":"PASS_EXECUTION_MANIFEST",
      "response_independent":True,
      "errors":[],
      "resource_freeze_payload":{
        "final_four_bay_tnc_nodes_by_bay":by,
        "four_bay_authoritative_tnc_baseline_calendar":tnc,
        "four_bay_baseline_transect_calendar":base,
        "tnc_v2_precollection_campaign_start_date":"2027-09-03",
        "tnc_v2_precollection_campaign_end_date":"2027-09-03",
      }
    }

def resource_inputs():
    return {
      "schema":"tampa.integrated_resource_inputs.v1",
      "status":"FROZEN_RESPONSE_INDEPENDENT_INPUT",
      "response_independent":True,
      "module_intent":{"event_stress":"disabled","optical":"disabled","optical_attribution":"disabled"},
      "inventory":{
        "complete_temperature_salinity_node_systems_available":None,
        "within_canopy_par_node_systems_available":None,
        "above_canopy_par_reference_systems_available":None,
        "preservation_capacity_for_planned_core_samples":108,
        "hplc_primary_assay_capacity_for_planned_core_samples":108,
      },
      "event_method":{
        "temperature_salinity_sensor_model_and_calibration_rule":None,
        "event_sensor_geometry_pilot_complete":None,
      },
      "coring":{
        "pre_post_core_offset_geometry_frozen":None,
        "maximum_attempted_cores_per_node_across_pre_post_rounds":None,
        "minimum_pre_post_core_center_separation_cm":None,
        "maximum_cumulative_disturbed_area_cm2_per_node":None,
      },
      "secondary_optical_attribution":{"optical_attribution_analysis_code_frozen":None},
      "provenance":{
        "inventory_date":"2027-06-01",
        "prepared_by":"synthetic-test",
        "equipment_inventory_source":"synthetic",
        "field_access_or_permission_note":"synthetic"
      }
    }

def filled_tnc_base():
    x=deepcopy(BASE_TNC)
    f=x["fields_to_freeze_before_first_outcome_bearing_core"]
    f.update({
      "horizontal_rhizome_tissue_class":"synthetic horizontal segment class",
      "minimum_perpendicular_transect_offset_m":1.0,
      "core_diameter_cm":5.0,
      "core_depth_cm":20.0,
      "maximum_collection_to_preservation_minutes":30,
      "preservation_method":"synthetic frozen method",
    })
    # The assay batch rule is already frozen in the repository. Campaign dates
    # are deliberately left for the builder to import from the execution manifest.
    return x

def write_forcing(path,extra_future=False,event=False):
    cols=[
      "node_id","water_body","event_selected","optical_selected","optical_reference",
      "pre_visit_date","post_visit_date","logger_deployment_date","logger_retrieval_date"
    ]
    if extra_future: cols.append("future_frequency")
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        if event:
            row={
              "node_id":"SYN01","water_body":"Old Tampa Bay",
              "event_selected":"true","optical_selected":"false","optical_reference":"false",
              "pre_visit_date":"2027-07-24","post_visit_date":"2027-09-04",
              "logger_deployment_date":"2027-07-24","logger_retrieval_date":"2027-09-03",
            }
            if extra_future: row["future_frequency"]="0.5"
            w.writerow(row)

def run_builder(td:Path,inputs,forcing_event=False,future_col=False,expect_ok=True):
    inp=td/"inputs.json"; force=td/"forcing.csv"; exe=td/"exec.json"
    rbase=td/"resource_base.json"; tbase=td/"tnc_base.json"
    rout=td/"resource_candidate.json"; tout=td/"tnc_candidate.json"
    write_json(inp,inputs); write_forcing(force,extra_future=future_col,event=forcing_event)
    write_json(exe,execution()); write_json(rbase,BASE_RESOURCE); write_json(tbase,filled_tnc_base())
    cmd=[
      PY,str(BUILD),
      "--resource-inputs",str(inp),
      "--forcing-manifest",str(force),
      "--tnc-execution",str(exe),
      "--resource-base",str(rbase),
      "--tnc-base",str(tbase),
      "--optical-freeze",str(OPTICAL),
      "--resource-out",str(rout),
      "--tnc-out",str(tout),
    ]
    cp=subprocess.run(cmd,capture_output=True,text=True)
    if expect_ok and cp.returncode!=0:
        raise AssertionError(cp.stderr+cp.stdout)
    if not expect_ok and cp.returncode==0:
        raise AssertionError("builder unexpectedly passed")
    return cp,rout,tout

def main():
    with tempfile.TemporaryDirectory() as d:
        td=Path(d)

        # Positive: protected four-bay TNC-only design reaches READY.
        cp,rout,tout=run_builder(td,resource_inputs(),expect_ok=True)
        r=json.loads(rout.read_text())
        t=json.loads(tout.read_text())
        assert r["build_provenance"]["selected_counts"]["tnc_v2"]==36
        assert r["build_provenance"]["selected_counts"]["prepost_union"]==0
        assert t["fields_to_freeze_before_first_outcome_bearing_core"]["campaign_start_date"]=="2027-09-03"
        assert t["fields_to_freeze_before_first_outcome_bearing_core"]["campaign_end_date"]=="2027-09-03"

        ready=td/"ready.json"
        vp=subprocess.run([
          PY,str(READY),
          "--freeze",str(rout),
          "--tnc-freeze",str(tout),
          "--optical-pilot-freeze",str(OPTICAL),
          "--out",str(ready),
          "--strict",
        ],capture_output=True,text=True)
        if vp.returncode!=0:
            raise AssertionError(vp.stderr+vp.stdout)
        rr=json.loads(ready.read_text())
        assert rr["status"]=="READY_TNC_CONFIRMATORY_CAMPAIGN"
        assert rr["module_status"]["event_stress"]=="DISABLED"
        assert rr["module_status"]["optical"]=="DISABLED"
        assert rr["calculated"]["minimum_outcome_bearing_tnc_cores_before_replacements"]==108

        # Negative: a disabled event module cannot silently carry selected nodes.
        bad=resource_inputs()
        run_builder(td,bad,forcing_event=True,expect_ok=False)

        # Negative: future/outcome columns are forbidden in the raw forcing manifest.
        run_builder(td,resource_inputs(),forcing_event=True,future_col=True,expect_ok=False)

    print("Integrated resource-freeze raw pipeline: OK")

if __name__=="__main__":
    main()
