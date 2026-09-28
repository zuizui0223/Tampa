#!/usr/bin/env python3
"""Verify canonical within-node microsite-continuity audit against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="within_node_microsite_continuity_not_supported"
    assert g["registry"]["all_recovery_sequences"]==c["registry"]["all_recovery_sequences"]
    assert g["registry"]["all_nodes"]==c["registry"]["all_nodes"]
    assert g["registry"]["informative_nodes"]==c["registry"]["informative_nodes"]
    assert g["primary"]["supported"] is False
    assert close(g["primary"]["equal_node_mean_difference"],c["primary"]["equal_node_mean_difference"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    for k in [
        "positive_nodes","zero_nodes","negative_nodes",
        "informative_vegetated_sequences","informative_bare_sequences"
    ]:
        assert g["secondary"][k]==c["secondary"][k], k
    assert close(
        g["secondary"]["event_weighted_difference_in_informative_nodes"],
        c["secondary"]["event_weighted_difference_in_informative_nodes"]
    )
    print("microsite-continuity within-node canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_microsite_continuity/microsite_continuity_node_audit_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/microsite_continuity_node_audit_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
