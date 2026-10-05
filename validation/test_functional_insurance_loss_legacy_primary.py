#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"analysis/75_functional_insurance_loss_legacy_primary.py"

def blob_sha(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def load():
    spec=importlib.util.spec_from_file_location("fi_loss",SCRIPT)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def build():
    rows=[]
    rng=np.random.default_rng(123)
    for bay,n in (("Old Tampa Bay",8),("Middle Tampa Bay",8)):
        for i in range(n):
            node=f"{bay[:3]}-{i}"
            base=.32+rng.normal(0,.015)
            for state,delta in (("persistent_thalassia",0.0),("loss_legacy_alternative",-0.10)):
                rows.append({
                    "node_id":node,"water_body":bay,"functional_state":state,
                    "attenuation_p90":base+delta+rng.normal(0,.004),
                    "total_vegetated_cover":.75+(0.0 if state=="persistent_thalassia" else -.10)+rng.normal(0,.01),
                    "canopy_height":.30+(0.0 if state=="persistent_thalassia" else -.05)+rng.normal(0,.005),
                    "pair_distance_m":25.0,"valid_days":18,
                    "measurement_qc_pass":True,"simultaneous_pair_pass":True,"state_eligibility_pass":True,
                })
    return pd.DataFrame(rows)

def main():
    m=load()
    freeze=json.loads((ROOT/"field/functional_insurance_loss_legacy_analysis_freeze.json").read_text())
    contract=json.loads((ROOT/"results/functional_insurance_loss_legacy_primary_v1_contract.json").read_text())
    pre=json.loads((ROOT/"results/functional_insurance_loss_legacy_preflight_v1.json").read_text())
    assert freeze["status"]=="FROZEN_BEFORE_HYDRODYNAMIC_OUTCOME_COLLECTION"
    assert freeze["script_path"]=="analysis/75_functional_insurance_loss_legacy_primary.py"
    assert freeze["script_blob_sha1"]==blob_sha(SCRIPT)
    assert contract["cohort"]["planning_pairs"]==18
    assert contract["cohort"]["minimum_confirmatory_pairs"]==16
    assert pre["feasibility"]["matched_nodes"]==18
    assert pre["feasibility"]["all_pairs_within_100m"] is True
    assert pre["feasibility"]["by_water_body"]=={"Old Tampa Bay":8,"Middle Tampa Bay":10}

    d=m.prepare(build())
    p=m.pair_table(d)
    assert len(p)==16
    assert (p["paired_difference"]<0).all()
    m.BOOT=200
    boots=m.paired_bootstrap(p)
    assert len(boots)>=190
    assert np.quantile(boots,.975)<0
    adj=m.adjusted_state_coef(d)
    assert adj is not None and np.isfinite(adj)

    bad=build()
    bad.loc[(bad["node_id"]=="Old-0") & (bad["functional_state"]=="loss_legacy_alternative"),"pair_distance_m"]=125
    d2=m.prepare(bad)
    assert d2["node_id"].nunique()==15

    bad=build()
    bad.loc[bad["node_id"]=="Mid-0","simultaneous_pair_pass"]=False
    d3=m.prepare(bad)
    assert d3["node_id"].nunique()==15

    bad=build()
    bad.loc[(bad["node_id"]=="Old-1") & (bad["functional_state"]=="persistent_thalassia"),"measurement_qc_pass"]=False
    d4=m.prepare(bad)
    assert d4["node_id"].nunique()==15

    print("history-linked functional-insurance freeze/tests: OK")

if __name__=="__main__":
    main()
