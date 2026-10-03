#!/usr/bin/env python3
"""Synthetic checks for frozen Tampa event, optical and forcing-family analyses."""
from __future__ import annotations
import importlib.util,json,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m

ev=loadmod("event_primary","analysis/65_event_stress_primary_analysis.py")
op=loadmod("optical_primary","analysis/66_optical_primary_analysis.py")
ev.BOOTSTRAP_REPS=800
op.BOOTSTRAP_REPS=800

# Event: 30 nodes, OTB/MTB vary, LTB near-zero; strong negative true effect.
erows=[]
k=0
for bi,b in enumerate(ev.BAYS):
    for i in range(10):
        k+=1
        expo=(i+1)*2.0 if b=="Old Tampa Bay" else (i+1)*1.2 if b=="Middle Tampa Bay" else 0.0
        pre=100+1.5*i+3*bi
        post=pre-0.45*expo+0.08*np.sin(k)
        erows.append({
          "node_id":f"E{k:02d}","water_body":b,
          "tnc_pre_mg_g":pre,"tnc_post_mg_g":post,
          "joint_hot_fresh_hours_30_25":expo,
          "paired_coverage_fraction":0.97,"common_overlap_days":39,
          "pre_post_tnc_interval_days":42,"primary_qc_pass":True
        })
ex=ev.prep(pd.DataFrame(erows))
counts,sample,nz,within,nzb,varb,distinct=ev.gates(ex)
assert sample and nz and within
assert len(varb)>=2
assert ev.coef(ex)<0
eb=ev.boot(ex)
assert eb["ci95"][1]<0, eb

# Event identifiability fail: exposure is a pure bay-level contrast.
bad=pd.DataFrame(erows)
bad["joint_hot_fresh_hours_30_25"]=bad["water_body"].map({
 "Old Tampa Bay":10.0,"Middle Tampa Bay":3.0,"Lower Tampa Bay":0.0
})
bx=ev.prep(bad)
_,sample,nz,within,_,_,_=ev.gates(bx)
assert sample and nz and not within

# Optical: 30 nodes, within-bay DLI variation, strong positive effect.
orows=[]
k=0
for bi,b in enumerate(op.BAYS):
    for i in range(10):
        k+=1
        dli=2.0+0.7*i+0.5*bi
        pre=95+1.2*i+2*bi
        post=pre+0.8*dli+0.08*np.cos(k)
        orows.append({
          "node_id":f"O{k:02d}","water_body":b,
          "tnc_pre_mg_g":pre,"tnc_post_mg_g":post,
          "mean_daily_within_canopy_dli":dli,
          "par_coverage_fraction":0.96,"valid_daily_dli_count":37,
          "common_overlap_days":39,"pre_post_tnc_interval_days":42,
          "daily_dli_qc_pass":True,"primary_qc_pass":True
        })
ox=op.prep(pd.DataFrame(orows))
counts,sample,overall,within,varb,distinct=op.gates(ox)
assert sample and overall and within
assert op.coef(ox)>0
ob=op.boot(ox)
assert ob["ci95"][0]>0, ob

# Optical variation fail.
obad=pd.DataFrame(orows)
obad["mean_daily_within_canopy_dli"]=obad["water_body"].map({
 "Old Tampa Bay":3.0,"Middle Tampa Bay":5.0,"Lower Tampa Bay":7.0
})
ox=op.prep(obad)
_,sample,overall,within,_,_=op.gates(ox)
assert sample and not overall and not within

# Family-level summarizer: corrected directional intervals.
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    ep=td/"event.json";opp=td/"optical.json";out=td/"family.json"
    ep.write_text(json.dumps({
      "schema":"tampa.event_stress_primary_analysis.v1",
      "interpretation_status":"supported_negative",
      "family_level_ci97_5":[-0.8,-0.1]
    }))
    opp.write_text(json.dumps({
      "schema":"tampa.optical_primary_analysis.v1",
      "interpretation_status":"supported_positive",
      "family_level_ci97_5":[0.2,0.7]
    }))
    cp=subprocess.run([
      sys.executable,str(ROOT/"analysis/67_forcing_family_analysis.py"),
      "--event",str(ep),"--optical",str(opp),"--out",str(out)
    ],cwd=ROOT,text=True,capture_output=True)
    assert cp.returncode==0,(cp.stdout,cp.stderr)
    fam=json.loads(out.read_text())
    assert fam["status"]=="FAMILY_CORRECTED_SUPPORT_PRESENT"
    assert fam["members"]["event_stress"]["family_corrected_supported"] is True
    assert fam["members"]["optical"]["family_corrected_supported"] is True

    # A non-estimable member blocks the joint confirmatory family claim.
    z=json.loads(ep.read_text())
    z["interpretation_status"]="nonestimable_or_pilot_gate_failed"
    ep.write_text(json.dumps(z))
    cp=subprocess.run([
      sys.executable,str(ROOT/"analysis/67_forcing_family_analysis.py"),
      "--event",str(ep),"--optical",str(opp),"--out",str(out)
    ],cwd=ROOT,text=True,capture_output=True)
    assert cp.returncode==0
    fam=json.loads(out.read_text())
    assert fam["status"]=="FAMILY_NOT_JOINTLY_ESTIMABLE"

print("Tampa frozen event/optical/forcing-family synthetic checks: OK")
