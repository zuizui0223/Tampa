#!/usr/bin/env python3
"""Verify canonical community-buffering result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=1e-8):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path,canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["schema"]=="tampa.community_buffering_v1.result"
    assert g["registry"]["eligible_visits"]==c["registry"]["eligible_visits"]
    assert g["registry"]["stable_nodes"]==c["registry"]["stable_nodes"]
    assert g["registry"]["repeated_stable_points"]==c["registry"]["repeated_stable_points"]
    assert g["registry"]["thalassia_loss_point_transitions_post2016"]==c["registry"]["thalassia_loss_point_transitions_post2016"]

    h1=g["H1_transect_occupancy_buffering"]
    assert h1["supported"] is False
    for key,ckey in [
        ("thalassia_frequency","thalassia_frequency_slope"),
        ("any_seagrass_frequency","any_seagrass_frequency_slope"),
        ("non_thalassia_only_frequency","non_thalassia_only_frequency_slope"),
    ]:
        assert close(h1["slopes"][key]["year_slope"],c["H1_lower_tampa"][ckey])
    assert close(h1["buffering_fraction_abs_slope_reduction"],c["H1_lower_tampa"]["absolute_slope_attenuation_fraction"])

    h2=g["H2_exact_point_turnover"]
    assert h2["estimable"] is False and h2["supported"] is False
    for k in ["lower_events","lower_nodes","comparison_events","comparison_nodes"]:
        assert int(h2[k])==int(c["H2_exact_point"][k])
    assert close(h2["lower_replacement_fraction"],c["H2_exact_point"]["lower_replacement_fraction"])
    assert close(h2["comparison_replacement_fraction"],c["H2_exact_point"]["comparison_replacement_fraction"])
    print("community-buffering canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_community_buffering/community_buffering_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/community_buffering_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
