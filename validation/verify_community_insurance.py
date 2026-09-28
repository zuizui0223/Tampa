#!/usr/bin/env python3
"""Verify canonical pre-existing community-insurance result."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=1e-8):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text()); c=json.loads(canonical.read_text())
    assert g["status"]=="both_insurance_hypotheses_supported"
    assert g["registry"]["eligible_thalassia_loss_transitions"]==c["registry"]["exact_point_thalassia_loss_transitions"]
    assert g["registry"]["nodes_with_loss"]==c["registry"]["nodes_with_loss"]

    a=g["H3a_source_mixture_insurance"]; ca=c["H3a_source_mixture_insurance"]
    assert a["supported"] is True and a["estimable"] is True
    for k in ["source_mixed_events","source_mixed_nodes","source_thalassia_only_events","source_thalassia_only_nodes"]:
        assert int(a[k])==int(ca[k])
    assert close(a["mixed_target_occupancy_fraction"],ca["mixed_target_occupancy_fraction"])
    assert close(a["thalassia_only_target_occupancy_fraction"],ca["thalassia_only_target_occupancy_fraction"])
    assert close(a["difference_mixed_minus_thalassia_only"]*100,ca["difference_percentage_points"])
    assert close(a["ci95"][0]*100,ca["difference_ci95_percentage_points"][0])
    assert close(a["ci95"][1]*100,ca["difference_ci95_percentage_points"][1])

    b=g["H3b_persistence_not_colonization"]; cb=c["H3b_preexisting_species_persistence"]
    assert b["supported"] is True and b["estimable"] is True
    assert int(b["target_occupied_events"])==int(cb["target_occupied_events"])
    assert int(b["nodes"])==int(cb["nodes"])
    assert close(b["retained_species_fraction"],cb["retained_species_fraction"])
    assert close(b["ci95"][0],cb["retained_species_ci95"][0])
    assert close(b["ci95"][1],cb["retained_species_ci95"][1])
    assert close(b["new_only_fraction"],cb["new_only_fraction"])
    print("community-insurance canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_community_insurance/community_insurance_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/community_insurance_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
