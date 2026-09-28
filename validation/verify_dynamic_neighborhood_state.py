#!/usr/bin/env python3
"""Verify canonical dynamic-neighborhood summary against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="posthoc_exploratory_completed"
    assert close(g["primary_radius_km"],c["primary_radius_km"],tol=1e-12)
    for gname,cname in [("frequency","frequency"),("cover_index","cover_index")]:
        gp=g["results"][gname]["primary"]
        cp=c[cname]
        assert gp["rows"]==c["rows"]
        assert gp["nodes"]==c["nodes"]
        assert gp["target_years"]==c["target_years"]
        assert close(gp["mean_mae"]["own"],cp["own_mae"])
        assert close(gp["mean_mae"]["segment"],cp["segment_mae"])
        assert close(gp["mean_mae"]["local"],cp["local_mae"])
        for inc in ["segment_increment","local_increment"]:
            gi=gp[inc]; ci=cp[inc]
            assert gi["wins"]==ci["wins"]
            assert gi["supported"]==ci["supported"]
            assert close(gi["mean_delta"],ci["mean_delta"])
            assert close(gi["median_delta"],ci["median_delta"])
            assert close(gi["signflip_p"],ci["signflip_p"],tol=0.005)
        sens=g["results"][gname]["sensitivity"]
        assert sens["segment_supported_radii"]==cp["segment_supported_radii"]
        assert sens["local_supported_radii"]==cp["local_supported_radii"]
    assert not g["cross_metric"]["segment_supported_both_metrics"]
    assert not g["cross_metric"]["local_supported_both_metrics"]
    print("dynamic-neighborhood canonical summary: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_dynamic_neighborhood/dynamic_neighborhood_state_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/dynamic_neighborhood_state_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
