#!/usr/bin/env python3
"""Verify canonical benthic-light result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="benthic_light_condition_not_supported"
    assert g["primary_estimable_outcomes"]==2
    assert g["primary_supported_outcomes"]==0
    for name in ["blade_length_mean_mm","shoot_density_mean_m2"]:
        gr=g["results"][name]["primary_6m"]
        cr=c["primary_6m"][name]
        assert gr["eligible_rows"]==cr["eligible_rows"]
        assert gr["eligible_nodes"]==cr["eligible_nodes"]
        assert gr["scored_target_years"]==cr["scored_target_years"]
        assert close(gr["baseline_mean_mae"],cr["baseline_mae"])
        assert close(gr["benthic_light_mean_mae"],cr["light_mae"])
        gs=gr["support"]
        assert gs["wins"]==cr["wins"]
        assert gs["losses"]==cr["losses"]
        assert gs["supported"] is False
        assert close(gs["mean_delta"],cr["mean_delta"])
        assert close(gs["median_delta"],cr["median_delta"])
        assert close(gs["signflip_p"],cr["signflip_p"],tol=0.005)
    print("benthic-light canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_benthic_light/benthic_light_condition_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/benthic_light_condition_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
