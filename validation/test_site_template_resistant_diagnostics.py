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
    assert "exactly three frozen q25/q50/q75 anchor IDs per node" in " ".join(dfreeze["measurement_validity_gate"]["node_level_requirements"])
    assert "perfectly confounded" in dfreeze["measurement_validity_gate"]["assay_batch_round_boundary"]
    assert "<=10%" in dfreeze["measurement_validity_gate"]["analytical_precision_boundary"]
    assert afreeze["uncertainty"]["seed"]==20261007
    assert afreeze["role"].startswith("paper-level decisive within-meadow state-augmentation primary")
    assert afreeze["inferential_hierarchy_contract"]=="results/clonal_state_inference_hierarchy_v1.json"
    assert "anchor_tnc_qc_pass" in afreeze["measurement_validity_gate"]["anchor_requirement"]
    assert "Do not impute" in afreeze["measurement_validity_gate"]["no_imputation"]
    event=json.loads((ROOT/"results/event_stress_debt_prospective_v1_contract.json").read_text())
    clonal=json.loads((ROOT/"results/clonal_state_prospective_v2_contract.json").read_text())
    dyn_contract=event["relationship_to_clonal_tnc_program"]["dynamic_reserve_change_future_diagnostic"]
    anc_contract=clonal["secondary_analysis"]["within_transect_anchor_diagnostic"]
    assert dyn_contract["analysis_code"]==dfreeze["script_path"]
    assert dyn_contract["analysis_freeze"]=="field/dynamic_reserve_future_analysis_freeze.json"
    assert "20261006" in dyn_contract["uncertainty"]
    assert "share the same post-exposure anchor measurements" in dyn_contract["measurement_error_boundary"]["issue"]
    assert "measurement-sensitive" in dyn_contract["measurement_error_boundary"]["discrepancy_rule"]
    assert anc_contract["analysis_code"]==afreeze["script_path"]
    assert anc_contract["analysis_freeze"]=="field/anchor_tnc_future_bb_analysis_freeze.json"
    assert "20261007" in anc_contract["uncertainty"]

    dyn=loadmod("dyn","analysis/71_dynamic_reserve_future_diagnostic.py")
    # Guard the key estimand: matched-anchor median change is not allowed to
    # collapse back to difference of independently summarized node medians.
    toy=pd.DataFrame([
      dict(node_id="toy",water_body=dyn.BAYS[0],anchor_id="q25",tnc_pre_anchor=0,tnc_post_anchor=99,
           pre_tnc_date="2027-07-24",post_tnc_date="2027-09-03",baseline_frequency_post=.5,future_frequency=.5,
           pre_anchor_tnc_qc_pass=True,post_anchor_tnc_qc_pass=True),
      dict(node_id="toy",water_body=dyn.BAYS[0],anchor_id="q50",tnc_pre_anchor=100,tnc_post_anchor=100,
           pre_tnc_date="2027-07-24",post_tnc_date="2027-09-03",baseline_frequency_post=.5,future_frequency=.5,
           pre_anchor_tnc_qc_pass=True,post_anchor_tnc_qc_pass=True),
      dict(node_id="toy",water_body=dyn.BAYS[0],anchor_id="q75",tnc_pre_anchor=101,tnc_post_anchor=102,
           pre_tnc_date="2027-07-24",post_tnc_date="2027-09-03",baseline_frequency_post=.5,future_frequency=.5,
           pre_anchor_tnc_qc_pass=True,post_anchor_tnc_qc_pass=True),
    ])
    toy_node=dyn.prepare(toy)
    assert len(toy_node)==1
    assert toy_node.iloc[0]["delta_tnc_42d"]==1.0
    assert (np.median([99,100,102])-np.median([0,100,101]))==0.0
    rows=[]
    rng=np.random.default_rng(10)
    for bi,b in enumerate(dyn.BAYS):
        for i in range(10):
            node=f"{bi}-{i}"
            base=.45+rng.normal(0,.04)
            latent_delta=-5+10*(i/9)+rng.normal(0,0.2)
            post_vals=[]
            for a,anchor in enumerate(("q25","q50","q75")):
                pre=100+6*a+rng.normal(0,1.0)
                delta=latent_delta+rng.normal(0,0.15)
                post=pre+delta
                post_vals.append(post)
                rows.append(dict(
                    node_id=node,water_body=b,anchor_id=anchor,
                    tnc_pre_anchor=pre,tnc_post_anchor=post,
                    pre_tnc_date="2027-07-24",post_tnc_date="2027-09-03",
                    baseline_frequency_post=base,future_frequency=np.nan,
                    pre_anchor_tnc_qc_pass=True,post_anchor_tnc_qc_pass=True
                ))
            future=base+0.003*latent_delta+0.001*np.median(post_vals)+rng.normal(0,.002)
            for r in rows[-3:]:
                r["future_frequency"]=future
    d=dyn.prepare(pd.DataFrame(rows))
    assert len(d)==30
    assert np.allclose(
        d["delta_tnc_42d"].to_numpy(),
        [np.median([
            rows[k]["tnc_post_anchor"]-rows[k]["tnc_pre_anchor"]
            for k in range(i*3,(i+1)*3)
        ]) for i in range(30)]
    )
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
                                 baseline_bb_anchor=baseline,anchor_tnc=tnc,future_bb_anchor=future,
                                 anchor_tnc_qc_pass=True))
    a=anc.prepare(pd.DataFrame(rows))
    est=anc.fit(a)
    assert est>0,est
    anc.BOOT=200
    boots=anc.cluster_bootstrap(a)
    assert len(boots)>=190 and np.median(boots)>0

    print("site-template-resistant diagnostic freezes: OK")

if __name__=="__main__":
    main()
