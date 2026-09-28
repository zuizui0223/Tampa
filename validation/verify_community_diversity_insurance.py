#!/usr/bin/env python3
"""Verify canonical community diversity-insurance result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["schema"]=="tampa.community_diversity_insurance_v1.result"
    assert g["registry"]["transitions"]==c["registry"]["transitions"]
    assert g["registry"]["nodes"]==c["registry"]["nodes"]
    gp=g["primary"]; cp=c["primary"]
    assert gp["estimable"] is True and gp["supported"] is True
    assert gp["bootstrap_replicates_used"]==cp["bootstrap_replicates"]
    assert close(gp["standardized_richness_log_odds_coefficient"],cp["standardized_richness_log_odds_coefficient"],tol=1e-8)
    assert close(gp["bootstrap_ci95"][0],cp["bootstrap_ci95"][0])
    assert close(gp["bootstrap_ci95"][1],cp["bootstrap_ci95"][1])
    print("community diversity-insurance canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_diversity_insurance/community_diversity_insurance_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/community_diversity_insurance_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
