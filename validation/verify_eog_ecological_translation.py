#!/usr/bin/env python3
"""Verify the canonical EOG ecological translation against a fresh rerun."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def close(a, b, tol=1e-8):
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def main(generated: Path, canonical: Path) -> None:
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())

    assert g["status"]=="posthoc_ecological_translation"
    for key in ["detected","focal_frequency","bb_cover_mean_all_points","blade_length_mean_mm","shoot_density_mean_m2"]:
        assert close(g["state_structure"][key]["stable_node_r2"], c["state_structure"][key]["stable_node_r2"])

    gb=g["dynamic_neighborhood"]["binary_detected"]
    cb=c["dynamic_neighborhood"]["binary_detected"]
    assert close(gb["baseline_mean_score"],cb["baseline_log_loss"])
    assert close(gb["dynamic_neighborhood_mean_score"],cb["dynamic_neighborhood_log_loss"])
    assert gb["dynamic_neighborhood_wins"]==cb["dynamic_neighborhood_wins"]
    assert close(gb["signflip_mc_one_sided_p"],cb["signflip_mc_one_sided_p"],tol=0.005)

    gf=g["dynamic_neighborhood"]["focal_frequency"]
    cf=c["dynamic_neighborhood"]["focal_frequency"]
    assert close(gf["baseline_mean_score"],cf["baseline_mae"])
    assert close(gf["dynamic_neighborhood_mean_score"],cf["dynamic_neighborhood_mae"])
    assert gf["dynamic_neighborhood_wins"]==cf["dynamic_neighborhood_wins"]
    assert close(gf["signflip_mc_one_sided_p"],cf["signflip_mc_one_sided_p"],tol=0.005)

    print("EOG ecological translation canonical summary: OK")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_eog_ecology/eog_ecological_translation_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/eog_ecological_translation_v1.json"))
    a=p.parse_args()
    main(a.generated,a.canonical)
