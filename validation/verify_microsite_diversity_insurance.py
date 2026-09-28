#!/usr/bin/env python3
"""Verify canonical microsite-diversity insurance result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=1e-8):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="both_supported"
    for k,v in c["registry"].items():
        assert g["registry"][k]==v,(k,g["registry"][k],v)

    gh1=g["H1_microsite_insurance"]; ch1=c["H1_microsite_insurance"]
    assert gh1["supported"] is True
    for cls in ["mixed_source","pure_thalassia_source"]:
        for k in ["events","nodes"]:
            assert gh1[cls][k]==ch1[cls][k],(cls,k)
        assert close(gh1[cls]["replacement_fraction"],ch1[cls]["replacement_fraction"])
    assert close(gh1["difference_mixed_minus_pure"],ch1["difference_mixed_minus_pure"])
    assert all(close(a,b) for a,b in zip(gh1["ci95"],ch1["ci95"]))

    gh2=g["H2_persistence_component"]; ch2=c["H2_persistence_component"]
    assert gh2["supported"] is True
    assert gh2["replacement_events"]==ch2["replacement_events"]
    assert gh2["nodes"]==ch2["nodes"]
    assert close(gh2["persistent_component_fraction"],ch2["persistent_component_fraction"])
    assert close(gh2["novel_only_fraction"],ch2["novel_only_fraction"])
    assert all(close(a,b) for a,b in zip(gh2["ci95"],ch2["ci95"]))
    print("microsite diversity insurance canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_microsite_insurance/microsite_diversity_insurance_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/microsite_diversity_insurance_v1.json"))
    a=p.parse_args()
    main(a.generated,a.canonical)
