#!/usr/bin/env python3
"""Synthetic end-to-end tests for the Tampa optical raw-pilot pipeline.

Tests:
1. repository blank templates remain fail-closed;
2. a fully passing response-independent pilot validates, mechanically copies,
   and yields READY optical method freeze;
3. a declared outcome-bearing sensor omitted from side-by-side DLI fails;
4. an otherwise good fouling dataset that never reaches 14 submerged days fails.

No TNC or future ecological response is used.
"""
from __future__ import annotations
import csv,json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/"validation/build_optical_pilot_summary.py"
VALIDATE=ROOT/"validation/validate_optical_method_pilot.py"
APPLY=ROOT/"analysis/72_apply_optical_method_pilot.py"
READINESS=ROOT/"validation/validate_optical_pilot_readiness.py"
CONTRACT=ROOT/"results/optical_pilot_acceptance_v1_contract.json"
BASE_FREEZE=ROOT/"field/optical_pilot_freeze.json"
BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")


def write_csv(path,header,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=header)
        w.writeheader(); w.writerows(rows)


def run(cmd,allow_fail=False):
    cp=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    if cp.returncode!=0 and not allow_fail:
        raise AssertionError(
            "command failed\n"+" ".join(map(str,cmd))+
            "\nSTDOUT="+cp.stdout+"\nSTDERR="+cp.stderr
        )
    return cp


def make_inputs(tmp,missing_side_sensor=False,fouling_day=14,primary_class="2pi_cosine_ppfd",reference_class="2pi_cosine_ppfd"):
    meta=tmp/"meta.json"
    meta.write_text(json.dumps({
      "schema":"synthetic",
      "outcome_response_accessed":False,
      "par_sensor_model":"synthetic_PAR_v1",
      "reference_sensor_id_and_calibration_provenance":"REF1 synthetic calibrated reference",
      "primary_angular_response_class":primary_class,
      "reference_angular_response_class":reference_class,
      "outcome_bearing_sensor_ids":["P1","P2"],
      "expected_field_photon_rate_max_umol_m2_s":1000,
      "mounting_geometry_and_height_tolerance_rule":"selected fraction of measured canopy height; max(2 cm,10% canopy) tolerance",
      "optical_attribution_intent":"disabled",
      "above_canopy_clearance_tolerance_rule":None,
      "source_artifact_manifest":[{"artifact":"synthetic","sha256":"synthetic"}]
    },indent=2))

    cal=tmp/"cal.csv"; rows=[]
    for sid,scale in (("P1",1.02),("P2",0.98)):
        # 50 non-dark observations over five levels.
        for li,ref in enumerate((50,100,300,600,1000),start=1):
            for rep in range(10):
                rows.append({
                  "sensor_id":sid,"irradiance_level_id":f"L{li}",
                  "reference_photon_rate_umol_m2_s":ref,
                  "sensor_raw_photon_rate_umol_m2_s":ref/scale,
                  "dark":"false","saturated":"false"
                })
        # Separate dark-offset gate: >=5 observations.
        for rep in range(5):
            rows.append({
              "sensor_id":sid,"irradiance_level_id":"D",
              "reference_photon_rate_umol_m2_s":0,
              "sensor_raw_photon_rate_umol_m2_s":0,
              "dark":"true","saturated":"false"
            })
    write_csv(cal,[
      "sensor_id","irradiance_level_id","reference_photon_rate_umol_m2_s",
      "sensor_raw_photon_rate_umol_m2_s","dark","saturated"
    ],rows)

    side=tmp/"side.csv"
    side_rows=[
      {"check_id":"C1","sensor_id":"P1","dli_mol_m2":10.0,"underwater_hours":6.5},
    ]
    if not missing_side_sensor:
        side_rows.append(
          {"check_id":"C1","sensor_id":"P2","dli_mol_m2":10.2,"underwater_hours":6.5}
        )
    write_csv(side,["check_id","sensor_id","dli_mol_m2","underwater_hours"],side_rows)

    prof=tmp/"profile.csv"; rows=[]
    for bi,b in enumerate(BAYS):
        for i in range(4):
            node=f"{bi+1}P{i+1}"
            for day in (1,2):
                rows.append({
                  "node_id":node,"water_body":b,"date":f"2027-08-{day:02d}",
                  "canopy_height_m":0.30+0.05*(i%3),
                  "canopy_height_class":("low","middle","high")[i%3],
                  "dli_25":8.0,"dli_50":10.0,"dli_75":12.0,"dli_above":15.0,
                  "daylight_coverage_fraction":1.0,
                  "max_daylight_gap_minutes":15
                })
    write_csv(prof,[
      "node_id","water_body","date","canopy_height_m","canopy_height_class",
      "dli_25","dli_50","dli_75","dli_above",
      "daylight_coverage_fraction","max_daylight_gap_minutes"
    ],rows)

    place=tmp/"place.csv"; rows=[]
    for bi,b in enumerate(BAYS):
        for i in range(4):
            node=f"{bi+1}P{i+1}"
            for rep in range(3):
                rows.append({
                  "node_id":node,"water_body":b,"replicate_id":rep+1,
                  "canopy_height_m":0.40,"achieved_height_m":0.20
                })
    write_csv(place,[
      "node_id","water_body","replicate_id","canopy_height_m","achieved_height_m"
    ],rows)

    foul=tmp/"foul.csv"; rows=[]
    for bi,b in enumerate(BAYS):
        for i in range(2):
            rows.append({
              "location_id":f"{bi+1}F{i+1}","water_body":b,
              "maintenance_mode":"manual","service_interval_days":14,
              "pilot_day":fouling_day,"check_id":"end",
              "pre_clean_photon_rate_umol_m2_s":98.0,
              "post_clean_photon_rate_umol_m2_s":100.0
            })
    write_csv(foul,[
      "location_id","water_body","maintenance_mode","service_interval_days",
      "pilot_day","check_id","pre_clean_photon_rate_umol_m2_s",
      "post_clean_photon_rate_umol_m2_s"
    ],rows)
    return meta,cal,side,prof,place,foul


def build_validate(tmp,prefix,**kwargs):
    meta,cal,side,prof,place,foul=make_inputs(tmp,**kwargs)
    cand=tmp/f"{prefix}_candidate.json"
    audit=tmp/f"{prefix}_audit.json"
    val=tmp/f"{prefix}_validation.json"
    run([
      sys.executable,str(BUILD),"--contract",str(CONTRACT),
      "--metadata",str(meta),"--calibration",str(cal),"--sideby",str(side),
      "--profile",str(prof),"--placement",str(place),"--fouling",str(foul),
      "--out",str(cand),"--audit-out",str(audit)
    ])
    run([sys.executable,str(VALIDATE),"--pilot",str(cand),"--contract",str(CONTRACT),"--out",str(val)])
    return cand,val,json.loads(val.read_text())


def test_blank_templates(tmp):
    cand=tmp/"blank_candidate.json"; audit=tmp/"blank_audit.json"; val=tmp/"blank_val.json"
    run([
      sys.executable,str(BUILD),"--contract",str(CONTRACT),
      "--metadata",str(ROOT/"field/optical_raw_pilot_metadata.json"),
      "--calibration",str(ROOT/"field/optical_calibration_pilot.csv"),
      "--sideby",str(ROOT/"field/optical_side_by_side_dli_pilot.csv"),
      "--profile",str(ROOT/"field/optical_vertical_profile_pilot.csv"),
      "--placement",str(ROOT/"field/optical_placement_pilot.csv"),
      "--fouling",str(ROOT/"field/optical_fouling_pilot.csv"),
      "--out",str(cand),"--audit-out",str(audit)
    ])
    run([sys.executable,str(VALIDATE),"--pilot",str(cand),"--contract",str(CONTRACT),"--out",str(val)])
    x=json.loads(val.read_text())
    assert x["status"]=="STOP_PILOT_INCOMPLETE",x


def test_pass_and_handoff(tmp):
    cand,val,v=build_validate(tmp,"pass")
    assert v["status"]=="PASS_OPTICAL_PILOT",json.dumps(v,indent=2)
    copy=v["copy_to_optical_pilot_freeze"]
    assert copy["selected_within_canopy_height_fraction"]==0.5
    assert copy["manual_service_interval_days"]==14
    assert copy["above_canopy_clearance_tolerance_rule"]=="NOT_APPLICABLE_ATTRIBUTION_DISABLED"

    applied=tmp/"freeze.json"
    run([
      sys.executable,str(APPLY),"--validation",str(val),
      "--freeze",str(BASE_FREEZE),"--out",str(applied)
    ])
    freeze=json.loads(applied.read_text())
    assert freeze["status"]=="READY",freeze
    cp=run([
      sys.executable,str(READINESS),"--freeze",str(applied),
      "--contract",str(CONTRACT),"--strict"
    ])
    assert '"status": "READY"' in cp.stdout


def test_missing_declared_side_sensor_fails(tmp):
    _,_,v=build_validate(tmp,"missing_side",missing_side_sensor=True)
    assert v["status"]!="PASS_OPTICAL_PILOT",v
    assert any("side_by_side" in x or "side-by-side" in x for x in v["pending_fields"]+v["errors"]),v


def test_short_fouling_fails(tmp):
    _,_,v=build_validate(tmp,"short_fouling",fouling_day=10)
    assert v["status"]!="PASS_OPTICAL_PILOT",v
    assert any("fouling" in x for x in v["pending_fields"]+v["errors"]),v



def test_angular_class_mismatch_fails(tmp):
    _,_,v=build_validate(
        tmp,"angular_mismatch",
        primary_class="2pi_cosine_ppfd",
        reference_class="4pi_scalar_ppffr"
    )
    assert v["status"]=="STOP_PILOT_QC_FAILED",v
    assert any("angular-response" in x or "cross-class" in x for x in v["errors"]),v


def test_scalar_matched_class_passes(tmp):
    _,_,v=build_validate(
        tmp,"scalar_pass",
        primary_class="4pi_scalar_ppffr",
        reference_class="4pi_scalar_ppffr"
    )
    assert v["status"]=="PASS_OPTICAL_PILOT",v
    copy=v["copy_to_optical_pilot_freeze"]
    assert copy["primary_angular_response_class"]=="4pi_scalar_ppffr"
    assert copy["reference_angular_response_class"]=="4pi_scalar_ppffr"
    assert "scalar" in copy["primary_light_quantity_reporting_label"]


def main():
    with tempfile.TemporaryDirectory(prefix="optical_pilot_pipeline_") as td:
        tmp=Path(td)
        test_blank_templates(tmp)
        test_pass_and_handoff(tmp)
        test_missing_declared_side_sensor_fails(tmp)
        test_short_fouling_fails(tmp)
        test_angular_class_mismatch_fails(tmp)
        test_scalar_matched_class_passes(tmp)
    print("Tampa optical raw-pilot pipeline synthetic tests: OK")


if __name__=="__main__":
    main()
