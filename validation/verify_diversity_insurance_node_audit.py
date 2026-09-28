#!/usr/bin/env python3
"""Verify canonical within-node diversity-insurance audit."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="within_node_diversity_insurance_not_supported"
    for k in ["all_transitions","all_nodes","informative_nodes","informative_transitions"]:
        assert g["registry"][k]==c["registry"][k],k
    gp=g["primary"]; cp=c["primary"]
    assert gp["estimable"] is True and gp["supported"] is False
    assert gp["bootstrap_replicates_used"]==cp["bootstrap_replicates"]
    assert close(gp["standardized_centered_richness_log_odds_coefficient"],
                 cp["standardized_centered_richness_log_odds_coefficient"])
    assert close(gp["ci95"][0],cp["ci95"][0])
    assert close(gp["ci95"][1],cp["ci95"][1])
    print("within-node diversity-insurance canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_diversity_node_audit/diversity_insurance_node_audit_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/diversity_insurance_node_audit_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
