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
    print("PASS: collinear TNC vs baseline fails closed; full-rank TNC effect remains estimable")

if __name__=="__main__":
    main()
