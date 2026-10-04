#!/usr/bin/env python3
"""Synthetic end-to-end test for the optical raw-pilot pipeline."""
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
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=header); w.writeheader(); w.writerows(rows)

def run(cmd):
    cp=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    if cp.returncode!=0:
        raise RuntimeError("command failed\n"+" ".join(map(str,cmd))+"\nSTDOUT="+cp.stdout+"\nSTDERR="+cp.stderr)
    return cp

def main():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        meta=td/"meta.json"
        meta.write_text(json.dumps({
          "schema":"synthetic",
          "outcome_response_accessed":False,
          "par_sensor_model":"synthetic_PAR_v1",
          "reference_sensor_id_and_calibration_provenance":"REF1 synthetic",
          "side_by_side_underwater_hours":6,
          "fouling_pilot_submerged_days":14,
          "mounting_geometry_and_height_tolerance_rule":"50pct canopy target; max(2cm,10pct canopy) tolerance",
          "above_canopy_clearance_tolerance_rule":"0.10m target +/-0.02m"
        }))

        cal=td/"cal.csv"; rows=[]
        for sid,scale in (("P1",1.02),("P2",0.98)):
            for li,ref in enumerate((50,100,300,600,1000),start=1):
                for rep in range(10):
                    rows.append({
                      "sensor_id":sid,"irradiance_level_id":f"L{li}",
                      "reference_ppfd_umol_m2_s":ref,
                      "sensor_raw_ppfd_umol_m2_s":ref/scale,
                      "dark":"false","saturated":"false"
                    })
            rows.append({"sensor_id":sid,"irradiance_level_id":"D","reference_ppfd_umol_m2_s":0,
                         "sensor_raw_ppfd_umol_m2_s":0,"dark":"true","saturated":"false"})
        write_csv(cal,["sensor_id","irradiance_level_id","reference_ppfd_umol_m2_s","sensor_raw_ppfd_umol_m2_s","dark","saturated"],rows)

        side=td/"side.csv"
        write_csv(side,["check_id","sensor_id","dli_mol_m2","underwater_hours"],[
          {"check_id":"C1","sensor_id":"P1","dli_mol_m2":10.0,"underwater_hours":6},
          {"check_id":"C1","sensor_id":"P2","dli_mol_m2":10.2,"underwater_hours":6},
        ])

        prof=td/"profile.csv"; rows=[]
        for bi,b in enumerate(BAYS):
            for i in range(4):
                node=f"{b[:1]}{i+1}"
                for day in (1,2):
                    rows.append({"node_id":node,"water_body":b,"date":f"2027-06-{day:02d}",
                                 "dli_25":8.0,"dli_50":10.0,"dli_75":12.0,"dli_above":15.0})
        write_csv(prof,["node_id","water_body","date","dli_25","dli_50","dli_75","dli_above"],rows)

        place=td/"place.csv"; rows=[]
        for bi,b in enumerate(BAYS):
            for i in range(4):
                node=f"{b[:1]}{i+1}"
                for rep in range(3):
                    rows.append({"node_id":node,"water_body":b,"replicate_id":rep+1,
                                 "canopy_height_m":0.40,"achieved_height_m":0.20})
        write_csv(place,["node_id","water_body","replicate_id","canopy_height_m","achieved_height_m"],rows)

        foul=td/"foul.csv"; rows=[]
        for b in BAYS:
            for i in range(2):
                rows.append({"location_id":f"{b[:1]}F{i+1}","water_body":b,"service_interval_days":14,
                             "pre_clean_ppfd_umol_m2_s":98.0,"post_clean_ppfd_umol_m2_s":100.0})
        write_csv(foul,["location_id","water_body","service_interval_days","pre_clean_ppfd_umol_m2_s","post_clean_ppfd_umol_m2_s"],rows)

        cand=td/"candidate.json"; audit=td/"audit.json"; val=td/"validation.json"; applied=td/"freeze.json"
        run([sys.executable,str(BUILD),"--contract",str(CONTRACT),"--metadata",str(meta),
             "--calibration",str(cal),"--sideby",str(side),"--profile",str(prof),
             "--placement",str(place),"--fouling",str(foul),"--out",str(cand),"--audit-out",str(audit)])
        run([sys.executable,str(VALIDATE),"--pilot",str(cand),"--contract",str(CONTRACT),"--out",str(val)])
        v=json.loads(val.read_text())
        assert v["status"]=="PASS_OPTICAL_PILOT",json.dumps(v,indent=2)
        assert v["copy_to_optical_pilot_freeze"]["selected_within_canopy_height_fraction"]==0.5
        assert v["copy_to_optical_pilot_freeze"]["manual_service_interval_days"]==14

        run([sys.executable,str(APPLY),"--validation",str(val),"--freeze",str(BASE_FREEZE),"--out",str(applied)])
        x=json.loads(applied.read_text())
        assert x["status"]=="READY"
        cp=run([sys.executable,str(READINESS),"--freeze",str(applied),"--contract",str(CONTRACT),"--strict"])
        assert '"status": "READY"' in cp.stdout
        print("Tampa optical raw-pilot pipeline synthetic PASS")

if __name__=="__main__": main()
