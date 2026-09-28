#!/usr/bin/env python3
"""Verify canonical density-to-occupancy cascade result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=1e-8):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="density_occupancy_cascade_not_supported"
    for gname,cname in [("shoot_density","primary_shoot_density"),("blade_length","secondary_blade_length")]:
        gr=g["results"][gname]
        cr=c[cname]
        assert gr["transition_rows"]==cr["transition_rows"]
        assert gr["nodes"]==cr["nodes"]
        assert gr["support"]["scored_target_years"]==cr["scored_target_years"]
        assert close(gr["baseline_mean_mae"],cr["baseline_mean_mae"])
        assert close(gr["augmented_mean_mae"],cr["augmented_mean_mae"])
        assert gr["support"]["wins"]==cr["wins"]
        assert gr["support"]["losses"]==cr["losses"]
        assert close(gr["support"]["mean_delta_augmented_minus_baseline"],cr["mean_delta"])
        assert close(gr["support"]["median_delta_augmented_minus_baseline"],cr["median_delta"])
        assert close(gr["support"]["signflip_p"],cr["signflip_p"],tol=0.005)
        assert gr["support"]["positive_condition_coefficient_years"]==cr["positive_coefficient_years"]
        assert close(gr["support"]["coefficient_positive_fraction"],cr["coefficient_positive_fraction"])
        assert close(gr["support"]["median_standardized_condition_coefficient"],cr["median_standardized_coefficient"])
        assert gr["support"]["supported"] is False
    print("density-to-occupancy cascade canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_density_cascade/density_occupancy_cascade_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/density_occupancy_cascade_v1.json"))
    a=p.parse_args()
    main(a.generated,a.canonical)
