#!/usr/bin/env python3
"""Verify canonical microsite recovery-pathway result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=1e-8):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="habitat_continuity"
    for k,v in c["registry"].items():
        assert g["registry"][k]==v,(k,g["registry"][k],v)
    gp=g["primary"]; cp=c["primary"]
    for cls in ["other_seagrass","no_seagrass"]:
        assert gp[cls]["sequences"]==cp[cls]["sequences"]
        assert gp[cls]["nodes"]==cp[cls]["nodes"]
        assert close(gp[cls]["thalassia_return_fraction"],cp[cls]["thalassia_return_fraction"])
    assert close(gp["difference_other_minus_no_seagrass"],cp["difference_other_minus_no_seagrass"])
    assert all(close(a,b) for a,b in zip(gp["ci95"],cp["ci95"]))
    assert gp["classification"]=="habitat_continuity"
    print("microsite recovery pathway canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_microsite_recovery/microsite_recovery_pathway_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/microsite_recovery_pathway_v1.json"))
    a=p.parse_args()
    main(a.generated,a.canonical)
