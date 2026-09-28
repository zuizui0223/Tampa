#!/usr/bin/env python3
"""Verify canonical return-quality fragility result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="return_quality_fragility_not_supported"
    for k in ["complete_recovered_four_year_sequences","nodes","recorded_relosses","stable_returns","pre_loss_run_min","pre_loss_run_max"]:
        assert g["registry"][k]==c["registry"][k], k
    assert g["primary"]["supported"] is False
    assert close(g["primary"]["return_bb_coefficient"],c["primary"]["return_bb_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    assert close(g["secondary"]["stable_return_bb_mean"],c["secondary"]["stable_return_bb_mean"])
    assert close(g["secondary"]["relost_return_bb_mean"],c["secondary"]["relost_return_bb_mean"])
    print("return-quality fragility canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_return_quality_fragility/return_quality_fragility_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/return_quality_fragility_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
