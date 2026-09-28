#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="legacy_continuity_interaction_not_supported"
    for k in ["recovery_sequences","nodes","vegetated_loss_sequences","bare_loss_sequences","nodes_with_both_loss_states"]:
        assert g["registry"][k]==c["registry"][k],k
    assert g["primary"]["supported"] is False
    assert close(g["primary"]["interaction_coefficient"],c["primary"]["interaction_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    for k in ["vegetated_only_history_coefficient","bare_only_history_coefficient","vegetated_return_fraction","bare_return_fraction"]:
        assert close(g["secondary"][k],c["secondary"][k]),k
    print("legacy-continuity interaction canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_legacy_continuity/legacy_continuity_interaction_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/legacy_continuity_interaction_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
