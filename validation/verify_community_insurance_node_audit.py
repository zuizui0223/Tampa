#!/usr/bin/env python3
"""Verify canonical within-node binary community-insurance audit."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())

    assert g["schema"]=="tampa.community_insurance_node_audit_v1.result"
    assert g["status"]=="within_node_binary_community_insurance_not_supported"

    gr=g["registry"]; cr=c["registry"]
    for k in [
        "all_transitions","all_nodes","informative_nodes",
        "informative_transitions","mixed_events_informative",
        "thalassia_only_events_informative",
    ]:
        assert int(gr[k])==int(cr[k]), (k,gr[k],cr[k])

    gp=g["primary"]; cp=c["primary"]
    assert gp["supported"] is False
    assert int(gp["bootstrap_replicates_used"])==int(cp["bootstrap_replicates"])
    assert close(
        gp["standardized_centered_source_mixed_log_odds_coefficient"],
        cp["standardized_centered_source_mixed_log_odds_coefficient"],
        tol=1e-8,
    )
    assert close(gp["ci95"][0],cp["bootstrap_ci95"][0])
    assert close(gp["ci95"][1],cp["bootstrap_ci95"][1])

    gs=g["secondary"]; cs=c["secondary"]
    assert int(gs["positive_node_differences"])==int(cs["positive_node_differences"])
    assert int(gs["zero_node_differences"])==int(cs["zero_node_differences"])
    assert int(gs["negative_node_differences"])==int(cs["negative_node_differences"])
    assert close(
        gs["median_node_difference"],
        cs["median_node_mixed_minus_alone_occupancy_difference"],
        tol=1e-8,
    )
    print("within-node binary community-insurance audit: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument(
        "--generated", type=Path,
        default=Path("results/generated_community_insurance_node_audit/community_insurance_node_audit_v1.json")
    )
    p.add_argument(
        "--canonical", type=Path,
        default=Path("results/community_insurance_node_audit_v1.json")
    )
    a=p.parse_args()
    main(a.generated,a.canonical)
