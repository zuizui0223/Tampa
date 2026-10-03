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
    assert afreeze["uncertainty"]["seed"]==20261007

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
                             baseline_frequency_post=base,future_frequency=future))
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
