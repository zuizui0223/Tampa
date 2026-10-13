#!/usr/bin/env python3
"""Known-truth identifiability regression for frozen within-node anchor-TNC primary.

No measured HPLC, source ecological response or future Tampa outcomes are opened.
A completely collinear source TNC/baseline design must be NONESTIMABLE, not
misinterpreted as a biological positive or null coefficient.
"""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"analysis/72_anchor_tnc_future_bb_diagnostic.py"

def load_module():
    spec=importlib.util.spec_from_file_location("anchor_tnc_frozen",SCRIPT)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def synthetic(identifiable:bool):
    rng=np.random.default_rng(20261013)
    rows=[]
    for b in ("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay"):
        for n in range(9):
            node=f"{b}-{n}"
            for a in range(3):
                baseline=float(a+1)
                tnc=(100+baseline) if not identifiable else 100+3*a+rng.normal(0,1.25)
                future=0.65*baseline+0.01*n if not identifiable else (
                    0.65*baseline+0.08*(tnc-100)+0.01*n
                )
                rows.append({
                    "node_id":node,"water_body":b,"anchor_id":f"q{(25,50,75)[a]}",
                    "baseline_bb_anchor":baseline,"anchor_tnc":tnc,
                    "future_bb_anchor":future,"anchor_tnc_qc_pass":True
                })
    return pd.DataFrame(rows)

def main():
    m=load_module()
    singular=m.prepare(synthetic(identifiable=False))
    X,_,_=m.design(singular)
    assert singular.node_id.nunique()==36 and len(singular)==108
    assert np.linalg.matrix_rank(X)<X.shape[1],"toy construction did not create rank deficit"
    try:
        m.fit(singular)
    except np.linalg.LinAlgError:
        pass
    else:
        raise AssertionError(
            "FROZEN PRIMARY BUG: rank-deficient TNC coefficient was returned "
            "instead of refusing to estimate it"
        )

    with tempfile.TemporaryDirectory() as td:
        csv=Path(td)/"frozen_anchor_synthetic_input.csv"
        output=Path(td)/"result.json"
        synthetic(identifiable=False).to_csv(csv,index=False)
        run=subprocess.run(
            [sys.executable,str(SCRIPT),"--input",str(csv),"--out",str(output)],
            cwd=ROOT,capture_output=True,text=True,timeout=60
        )
        assert run.returncode==0,(run.stdout,run.stderr)
        result=json.loads(output.read_text())
        assert result["status"]=="NONESTIMABLE_DESIGN_RANK",result
        assert result["classification"]=="nonestimable",result
        assert result["estimate"] is None and result["ci95"] is None
        assert result["eligible_nodes"]==36 and result["eligible_anchor_rows"]==108

    valid=m.prepare(synthetic(identifiable=True))
    X,_,_=m.design(valid)
    assert np.linalg.matrix_rank(X)==X.shape[1],"positive-control design unexpectedly singular"
    beta=m.fit(valid)
    assert np.isfinite(beta) and abs(beta-0.08)<1e-7,beta
    # The companion predeclared depth sensitivity is just as vulnerable:
    # a local TNC difference can be exactly aliased with within-node depth.
    dp_spec=importlib.util.spec_from_file_location(
        "anchor_depth_frozen",ROOT/"analysis/76_anchor_tnc_future_bb_depth_sensitivity.py")
    assert dp_spec and dp_spec.loader
    depth=importlib.util.module_from_spec(dp_spec);dp_spec.loader.exec_module(depth)
    dx=synthetic(identifiable=True)
    dx["baseline_depth_m"]=0.5+dx["anchor_tnc"]/1000.0
    dx["future_bb_anchor"]=0.65*dx["baseline_bb_anchor"]+8.0*dx["baseline_depth_m"]
    dz=depth.prepare_depth(dx)
    DX,_,_,_=depth.design(dz)
    assert np.linalg.matrix_rank(DX)<DX.shape[1],"depth collinearity toy invalid"
    try:
        depth.fit(dz)
    except np.linalg.LinAlgError:
        pass
    else:
        raise AssertionError("DEPTH SENSITIVITY BUG: aliased TNC/depth returned pseudo-coefficient")

    # Node-scale reserve-trajectory diagnostic can likewise alias
    # delta TNC and current TNC when baseline reserve is constant.
    dyn_spec=importlib.util.spec_from_file_location(
        "dynamic_tnc_frozen",ROOT/"analysis/71_dynamic_reserve_future_diagnostic.py")
    assert dyn_spec and dyn_spec.loader
    dyn=importlib.util.module_from_spec(dyn_spec);dyn_spec.loader.exec_module(dyn)
    dynrows=[]
    for bay in dyn.BAYS:
        for ni in range(10):
            node=f"{bay}-{ni}"
            delta=ni*0.4+0.1
            for ai,anchor in enumerate(("q25","q50","q75")):
                dynrows.append({
                    "node_id":node,"water_body":bay,"anchor_id":anchor,
                    "tnc_pre_anchor":100.0,"tnc_post_anchor":100.0+delta,
                    "pre_tnc_date":"2027-07-24","post_tnc_date":"2027-09-03",
                    "baseline_frequency_post":0.15+ni*0.01,
                    "future_frequency":0.15+ni*0.01+0.01*delta,
                    "pre_anchor_tnc_qc_pass":True,"post_anchor_tnc_qc_pass":True
                })
    dy=dyn.prepare(pd.DataFrame(dynrows))
    assert len(dy)==30
    Xd,_,_=dyn.design(dy)
    assert np.linalg.matrix_rank(Xd)<Xd.shape[1],"dynamic alias toy invalid"
    try:
        dyn.fit(dy)
    except np.linalg.LinAlgError:
        pass
    else:
        raise AssertionError("RESERVE TRAJECTORY BUG: aliased stock/trajectory returned pseudo-coefficient")

    print("PASS: decisive, depth, dynamic collinear models fail closed; identifiable TNC works")

if __name__=="__main__":
    main()
