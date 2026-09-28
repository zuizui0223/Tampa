#!/usr/bin/env python3
"""Verify canonical local-legacy recovery-quality result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="legacy_recovery_quality_not_supported"
    for k in ["recovered_quantitative_sequences","nodes","nodes_with_thalassia_run_variation",
              "positive_habitat_headstart_events","thalassia_run_min","thalassia_run_max"]:
        assert g["registry"][k]==c["registry"][k], k
    assert g["primary"]["supported"] is False
    assert close(g["primary"]["thalassia_run_coefficient"],c["primary"]["thalassia_run_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    assert close(g["secondary"]["coefficients"]["habitat_headstart_centered"],c["secondary"]["habitat_headstart_coefficient"])
    assert close(g["secondary"]["habitat_headstart_ci95"][0],c["secondary"]["habitat_headstart_ci95"][0])
    assert close(g["secondary"]["habitat_headstart_ci95"][1],c["secondary"]["habitat_headstart_ci95"][1])
    print("legacy-recovery-quality canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_legacy_recovery_quality/legacy_recovery_quality_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/legacy_recovery_quality_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
