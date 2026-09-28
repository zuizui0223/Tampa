#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="preloss_local_legacy_supported"
    assert g["registry"]["recovery_sequences"]==c["registry"]["recovery_sequences"]
    assert g["registry"]["nodes"]==c["registry"]["nodes"]
    assert g["registry"]["nodes_with_run_length_variation"]==c["registry"]["nodes_with_run_length_variation"]
    assert g["primary"]["supported"] is True
    assert close(g["primary"]["centered_run_length_coefficient"],c["primary"]["centered_run_length_coefficient"])
    assert close(g["primary"]["ci95"][0],c["primary"]["ci95"][0])
    assert close(g["primary"]["ci95"][1],c["primary"]["ci95"][1])
    assert g["secondary"]["return_run_length_median"]==c["secondary"]["return_run_length_median"]
    assert g["secondary"]["nonreturn_run_length_median"]==c["secondary"]["nonreturn_run_length_median"]
    print("preloss local legacy canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_preloss_legacy/preloss_local_legacy_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/preloss_local_legacy_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
