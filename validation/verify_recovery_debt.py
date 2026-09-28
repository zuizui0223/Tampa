#!/usr/bin/env python3
"""Verify canonical recovery-debt result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="recovery_debt_supported"
    for k in [
        "presence_defined_sequences","quantitative_complete_sequences","nodes",
        "recovered_sequences","recovered_nodes","continuous_sequences","continuous_nodes",
        "point_years_with_numeric_bb","nonnumeric_focal_bb_rows"
    ]:
        assert g["registry"][k]==c["registry"][k], k
    assert g["primary"]["supported"] is True
    assert close(g["primary"]["recovered_group_coefficient"],c["primary"]["recovered_group_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    for group in ["recovered","continuous"]:
        gg=g["secondary"][group]; cc=c["secondary"][group]
        for k in ["target_bb_mean","target_bb_median","source_bb_mean","mean_source_to_target_change"]:
            assert close(gg[k],cc[k]), (group,k)
    print("recovery-debt canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_recovery_debt/recovery_debt_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/recovery_debt_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
