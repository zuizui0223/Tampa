#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="bare_loss_local_legacy_not_supported"
    for k in ["bare_loss_sequences","nodes","nodes_with_run_length_variation","returns","nonreturns"]:
        assert g["registry"][k]==c["registry"][k],k
    assert g["primary"]["supported"] is False
    assert close(g["primary"]["centered_run_length_coefficient"],c["primary"]["centered_run_length_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    assert g["secondary"]["return_run_length_median"]==c["secondary"]["return_run_length_median"]
    assert g["secondary"]["nonreturn_run_length_median"]==c["secondary"]["nonreturn_run_length_median"]
    print("bare-loss local legacy canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_bare_loss_legacy/bare_loss_local_legacy_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/bare_loss_local_legacy_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
