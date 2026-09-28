#!/usr/bin/env python3
"""Verify canonical current-state-saturated local-legacy result."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="legacy_beyond_current_state_supported"
    assert g["registry"]["complete_sequences"]==c["registry"]["complete_sequences"]
    assert g["registry"]["nodes"]==c["registry"]["nodes"]
    assert g["registry"]["nodes_with_run_length_variation"]==c["registry"]["nodes_with_run_length_variation"]
    assert g["primary"]["supported"] is True
    assert close(
        g["primary"]["current_state_saturated_run_length_coefficient"],
        c["primary"]["current_state_saturated_run_length_coefficient"]
    )
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    for k in [
        "without_current_state_run_length_coefficient",
        "corr_run_length_source_frequency",
        "corr_run_length_source_bb"
    ]:
        assert close(g["secondary"][k],c["secondary"][k])
    print("current-state-saturated local legacy canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_local_legacy_current_state/local_legacy_current_state_audit_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/local_legacy_current_state_audit_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
