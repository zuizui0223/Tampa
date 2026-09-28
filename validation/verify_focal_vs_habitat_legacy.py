#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="focal_specific_legacy_supported"
    for k in ["recovery_sequences","nodes","nodes_with_thalassia_run_variation","headstart_positive_events","nodes_with_positive_headstart"]:
        assert g["registry"][k]==c["registry"][k],k
    assert g["primary"]["supported"] is True
    assert close(g["primary"]["centered_thalassia_run_coefficient"],c["primary"]["centered_thalassia_run_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    assert close(g["secondary"]["centered_habitat_headstart_coefficient"],c["secondary"]["centered_habitat_headstart_coefficient"])
    assert close(g["secondary"]["habitat_headstart_ci95"][0],c["secondary"]["habitat_headstart_ci95"][0])
    assert close(g["secondary"]["habitat_headstart_ci95"][1],c["secondary"]["habitat_headstart_ci95"][1])
    print("focal-vs-habitat legacy canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_focal_vs_habitat/focal_vs_habitat_legacy_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/focal_vs_habitat_legacy_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
