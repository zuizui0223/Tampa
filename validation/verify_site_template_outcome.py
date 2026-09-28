#!/usr/bin/env python3
"""Verify canonical site-template result against a fresh rerun."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def close(a,b,tol=0.005):
    return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)

def main(generated:Path, canonical:Path):
    g=json.loads(generated.read_text())
    c=json.loads(canonical.read_text())
    assert g["status"]=="measured_template_not_supported"
    assert g["primary_template_supported_count"]==0
    assert g["broad_support"] is False
    for gname,cname in [
        ("detection_prevalence","detection_prevalence"),
        ("focal_frequency","focal_frequency"),
        ("bb_cover_index","bb_cover_index"),
    ]:
        gr=g["results"][gname]
        cr=c["primary"][cname]
        assert gr["eligible_nodes"]==cr["eligible_nodes"]
        assert gr["template_supported"] is False
        assert close(gr["model_scores"]["spatial_reference"]["mae"],cr["spatial_reference"]["mae"])
        assert close(gr["model_scores"]["spatial_reference"]["heldout_r2"],cr["spatial_reference"]["heldout_r2"])
        assert close(gr["model_scores"]["measured_template"]["mae"],cr["measured_template"]["mae"])
        assert close(gr["model_scores"]["measured_template"]["heldout_r2"],cr["measured_template"]["heldout_r2"])
        gi=gr["comparisons"]["measured_template_vs_spatial"]
        ci=cr["increment"]
        assert gi["wins"]==ci["wins"]
        assert gi["losses"]==ci["losses"]
        assert gi["ties"]==ci["ties"]
        assert gi["supported"] is False
        assert close(gi["mean_delta"],ci["mean_delta"])
        assert close(gi["median_delta"],ci["median_delta"])
        assert close(gi["signflip_p"],ci["signflip_p"],tol=0.005)
    print("site-template canonical result: OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--generated",type=Path,default=Path("results/generated_site_template/site_template_outcome_v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("results/site_template_outcome_v1.json"))
    a=p.parse_args(); main(a.generated,a.canonical)
