#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="return_fragility_supported"
    for k in ["four_year_sequences","nodes","recovered_sequences","recovered_nodes","continuous_sequences","continuous_nodes","total_recorded_relosses"]:
        assert g["registry"][k]==c["registry"][k],k
    assert g["primary"]["supported"] is True
    assert close(g["primary"]["recovered_group_coefficient"],c["primary"]["recovered_group_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    for k in ["recovered_reloss_fraction","continuous_reloss_fraction","risk_difference_recovered_minus_continuous"]:
        assert close(g["secondary"][k],c["secondary"][k]),k
    print("return fragility canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_return_fragility/return_fragility_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/return_fragility_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
