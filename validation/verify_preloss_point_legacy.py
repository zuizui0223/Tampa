#!/usr/bin/env python3
"""Verify canonical pre-loss exact-point legacy result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="preloss_local_legacy_supported"
    for k in ["recovery_sequences","nodes","informative_strata","informative_nodes","maximum_observed_streak_years"]:
        assert g["registry"][k]==c["registry"][k],k
    assert g["primary"]["supported"] is True
    assert close(g["primary"]["equal_node_mean_streak_difference_years"],c["primary"]["equal_node_mean_streak_difference_years"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    for k in ["positive_nodes","zero_nodes","negative_nodes"]:
        assert g["secondary"][k]==c["secondary"][k],k
    assert close(g["secondary"]["median_node_effect"],c["secondary"]["median_node_effect"])
    print("pre-loss exact-point legacy canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_preloss_legacy/preloss_point_legacy_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/preloss_point_legacy_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
