#!/usr/bin/env python3
"""Verify canonical pre-existing mixed-patch result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["schema"]=="tampa.preexisting_mixed_patch_v1.result"
    assert g["registry"]["eligible_visits"]==c["registry"]["eligible_visits"]
    assert g["registry"]["stable_nodes"]==c["registry"]["stable_nodes"]
    assert g["registry"]["primary_replacement_events"]==c["registry"]["primary_replacement_events"]
    assert g["registry"]["primary_nodes"]==c["registry"]["primary_nodes"]
    gp=g["primary"]; cp=c["primary"]
    assert gp["estimable"] is True
    assert gp["supported"] is True
    assert gp["events"]==cp["preexisting_persistence_events"]+cp["de_novo_only_events"]
    assert gp["preexisting_persistence_events"]==cp["preexisting_persistence_events"]
    assert gp["de_novo_only_events"]==cp["de_novo_only_events"]
    assert close(gp["preexisting_persistence_fraction"],cp["preexisting_persistence_fraction"],tol=1e-10)
    assert close(gp["bootstrap_ci95"][0],cp["bootstrap_ci95"][0])
    assert close(gp["bootstrap_ci95"][1],cp["bootstrap_ci95"][1])
    print("pre-existing mixed-patch canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_preexisting_mixed_patch/preexisting_mixed_patch_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/preexisting_mixed_patch_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
