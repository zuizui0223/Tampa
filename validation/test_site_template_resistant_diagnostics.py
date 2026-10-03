#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def blob_sha(path):
    data=(ROOT/path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def main():
    dfreeze=json.loads((ROOT/"field/dynamic_reserve_future_analysis_freeze.json").read_text())
    afreeze=json.loads((ROOT/"field/anchor_tnc_future_bb_analysis_freeze.json").read_text())
    assert blob_sha(dfreeze["script_path"])==dfreeze["script_blob_sha1"]
    assert blob_sha(afreeze["script_path"])==afreeze["script_blob_sha1"]
    assert dfreeze["uncertainty"]["seed"]==20261006
    assert "matched_anchor" in " ".join(dfreeze["measurement_validity_gate"]["node_level_requirements"])
    assert "perfectly confounded" in dfreeze["measurement_validity_gate"]["assay_batch_round_boundary"]
    assert "<=10%" in dfreeze["measurement_validity_gate"]["analytical_precision_boundary"]
    assert afreeze["uncertainty"]["seed"]==20261007
    event=json.loads((ROOT/"results/event_stress_debt_prospective_v1_contract.json").read_text())
    clonal=json.loads((ROOT/"results/clonal_state_prospective_v2_contract.json").read_text())
    dyn_contract=event["relationship_to_clonal_tnc_program"]["dynamic_reserve_change_future_diagnostic"]
    anc_contract=clonal["secondary_analysis"]["within_transect_anchor_diagnostic"]
    assert dyn_contract["analysis_code"]==dfreeze["script_path"]
    assert dyn_contract["analysis_freeze"]=="field/dynamic_reserve_future_analysis_freeze.json"
    assert "20261006" in dyn_contract["uncertainty"]
    assert anc_contract["analysis_code"]==afreeze["script_path"]
    assert anc_contract["analysis_freeze"]=="field/anchor_tnc_future_bb_analysis_freeze.json"
    assert "20261007" in anc_contract["uncertainty"]

    dyn=loadmod("dyn","analysis/71_dynamic_reserve_future_diagnostic.py")
    rows=[]
    rng=np.random.default_rng(10)
    for bi,b in enumerate(dyn.BAYS):
        for i in range(10):
            pre=100+rng.normal(0,4)
            delta=-5+10*(i/9)+rng.normal(0,0.2)
            post=pre+delta
            base=.45+rng.normal(0,.04)
            future=base+0.003*delta+0.001*post+rng.normal(0,.002)
            rows.append(dict(node_id=f"{bi}-{i}",water_body=b,tnc_pre=pre,tnc_post=post,
                             baseline_frequency_post=base,future_frequency=future,
                             pre_post_anchor_match_pass=True,tnc_node_qc_pass=True))
    d=pd.DataFrame(rows)
    est=dyn.fit(d)
    assert est>0,est
    dyn.BOOT=200
    boots=dyn.stratified_bootstrap(d)
    assert len(boots)>=190 and np.median(boots)>0

    anc=loadmod("anc","analysis/72_anchor_tnc_future_bb_diagnostic.py")
    rows=[]
    rng=np.random.default_rng(11)
    for bi,b in enumerate(anc.BAYS):
        for i in range(9):
            node=f"{bi}-{i}"
            node_base=rng.normal(2,0.2)
            for a in range(3):
                tnc=90+10*a+rng.normal(0,.3)
                baseline=node_base+0.05*a+rng.normal(0,.02)
                future=baseline+0.01*(tnc-(100+rng.normal(0,.1)))+rng.normal(0,.01)
                rows.append(dict(node_id=node,water_body=b,anchor_id=f"A{a}",
                                 baseline_bb_anchor=baseline,anchor_tnc=tnc,future_bb_anchor=future))
    a=anc.prepare(pd.DataFrame(rows))
    est=anc.fit(a)
    assert est>0,est
    anc.BOOT=200
    boots=anc.cluster_bootstrap(a)
    assert len(boots)>=190 and np.median(boots)>0

    print("site-template-resistant diagnostic freezes: OK")

if __name__=="__main__":
    main()
