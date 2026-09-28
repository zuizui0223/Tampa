#!/usr/bin/env python3
"""Verify canonical exact-point return-fragility result."""
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
    gp=g["primary"]; cp=c["primary"]
    assert gp["supported"] is True
    assert close(gp["recovered_group_coefficient"],cp["recovered_group_coefficient"])
    assert close(gp["ci95"][0],cp["ci95"][0])
    assert close(gp["ci95"][1],cp["ci95"][1])
    gs=g["secondary"]; cs=c["secondary"]
    assert close(gs["recovered_reloss_fraction"],cs["recovered_reloss_fraction"])
    assert close(gs["continuous_reloss_fraction"],cs["continuous_reloss_fraction"])
    assert close(gs["risk_difference_recovered_minus_continuous"],cs["risk_difference_recovered_minus_continuous"])
    print("return fragility canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_return_fragility/return_fragility_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/return_fragility_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
