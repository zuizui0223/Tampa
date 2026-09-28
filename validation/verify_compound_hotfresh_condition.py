#!/usr/bin/env python3
"""Verify canonical compound hot-fresh result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="compound_hotfresh_condition_not_supported"
    assert g["primary_estimable_outcomes"]==2
    assert g["primary_supported_outcomes"]==0
    for name in ["blade_length_mean_mm","shoot_density_mean_m2"]:
        gr=g["results"][name]
        cr=c["primary"][name]
        assert gr["transition_rows"]==cr["transition_rows"]
        assert gr["nodes"]==cr["nodes"]
        assert gr["scored_target_years"]==cr["target_years"]
        assert close(gr["baseline_mean_mae"],cr["baseline_mae"])
        assert close(gr["compound_mean_mae"],cr["compound_mae"])
        gs=gr["support"]
        assert gs["wins"]==cr["wins"]
        assert gs["losses"]==cr["losses"]
        assert gs["supported"] is False
        assert close(gs["mean_delta"],cr["mean_delta"])
        assert close(gs["median_delta"],cr["median_delta"])
        assert close(gs["signflip_p"],cr["signflip_p"],tol=0.005)
    print("compound hot-fresh canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_compound_hotfresh/compound_hotfresh_condition_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/compound_hotfresh_condition_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
