#!/usr/bin/env python3
"""Verify canonical condition-to-thinning result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="condition_leading_information_not_supported"
    assert g["registry"]["condition_eligible_consecutive_transitions"]==c["registry"]["condition_eligible_consecutive_transitions"]
    assert g["registry"]["nodes"]==c["registry"]["nodes"]

    gp=g["primary_frequency"]; cp=c["primary_frequency"]
    assert gp["scored_target_years"]==cp["scored_target_years"]
    assert gp["support"]["wins"]==cp["wins"]
    assert gp["support"]["losses"]==cp["losses"]
    assert gp["support"]["supported"] is False
    assert close(gp["baseline_mean_mae"],cp["baseline_mean_mae"])
    assert close(gp["condition_mean_mae"],cp["condition_mean_mae"])
    assert close(gp["support"]["mean_delta"],cp["mean_delta"])
    assert close(gp["support"]["median_delta"],cp["median_delta"])
    assert close(gp["support"]["signflip_p"],cp["signflip_p"],tol=0.005)

    gs=g["sensitivity_include_2016"]; cs=c["sensitivity_include_2016"]
    assert gs["scored_target_years"]==cs["scored_target_years"]
    assert gs["support"]["wins"]==cs["wins"]
    assert gs["support"]["losses"]==cs["losses"]
    assert gs["support"]["supported"] is False
    assert close(gs["baseline_mean_mae"],cs["baseline_mean_mae"])
    assert close(gs["condition_mean_mae"],cs["condition_mean_mae"])
    assert close(gs["support"]["signflip_p"],cs["signflip_p"],tol=0.005)

    gb=g["secondary_braun_blanquet"]; cb=c["secondary_braun_blanquet"]
    assert gb["scored_target_years"]==cb["scored_target_years"]
    assert gb["support"]["wins"]==cb["wins"]
    assert gb["support"]["losses"]==cb["losses"]
    assert gb["support"]["supported"] is False
    assert close(gb["baseline_mean_mae"],cb["baseline_mean_mae"])
    assert close(gb["condition_mean_mae"],cb["condition_mean_mae"])
    assert close(gb["support"]["signflip_p"],cb["signflip_p"],tol=0.005)

    print("condition-to-thinning canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_condition_leads_thinning/condition_leads_thinning_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/condition_leads_thinning_v1.json"))
    a=p.parse_args()
    main(a.generated,a.canonical)
