#!/usr/bin/env python3
"""Response-free exact triplet-completeness fragility of the frozen TNC design.

Illustrative anchor completeness rates are NOT observed Tampa QC or future
biological-response data. Nothing here adjusts frozen sampling/analysis rules.
"""
from __future__ import annotations
import argparse
import json
from math import comb
from pathlib import Path

CONTRACT=Path("results/clonal_state_augmentation_primary_v1_contract.json")
OUTPUT=Path("results/tnc_anchor_triplet_fragility_v1.json")
PROBABILITIES=(0.90,0.95,0.97,0.98,0.985,0.99,0.995)

def tail(n:int, minimum:int, q:float)->float:
    if not (0<=q<=1 and 0<=minimum<=n):
        raise ValueError("invalid gate or probability")
    return sum(comb(n,k)*q**k*(1-q)**(n-k) for k in range(minimum,n+1))

def needed_p(n:int,minimum:int,target:float,anchors:int)->float:
    lo,hi=0.,1.
    for _ in range(80):
        mid=(lo+hi)/2
        if tail(n,minimum,mid**anchors)<target: lo=mid
        else: hi=mid
    return hi

def build(contract:dict)->dict:
    gate=contract["gate"]
    counts=gate["preflight_by_bay"]
    n=gate["preflight_complete_nodes"]
    minimum=gate["min_complete_nodes"]
    min_bay=gate["min_nodes_per_bay"]
    assert counts=={"Old Tampa Bay":8,"Middle Tampa Bay":10,"Lower Tampa Bay":12,"Boca Ciega Bay":8}
    assert sum(counts.values())==n==38
    assert minimum==36 and min_bay==6
    anchors=3
    # With only two lost nodes, every bay's frozen six-node minimum still passes.
    assert min(counts.values())-(n-minimum)>=min_bay
    scenarios=[]
    for p in PROBABILITIES:
        q=p**anchors
        scenarios.append({
            "hypothetical_single_anchor_completeness":p,
            "complete_node_probability_if_anchors_independent":round(q,9),
            "expected_complete_nodes_if_fully_independent":round(n*q,6),
            "probability_to_pass_original_replication_gate_if_fully_independent":round(tail(n,minimum,q),9),
        })
    return {
      "schema":"tampa.tnc_anchor_triplet_fragility_v1",
      "status":"ILLUSTRATIVE_RESPONSE_FREE_SCENARIOS_NOT_EMPIRICAL_YIELD_OR_POWER",
      "source":"results/clonal_state_augmentation_primary_v1_contract.json",
      "planning_frame":{"three_anchor_nodes":n,"by_water_body":counts,
        "minimum_complete_nodes":minimum,"minimum_per_bay":min_bay,
        "anchors_per_node":anchors,"candidate_anchor_rows":n*anchors,
        "minimum_complete_anchor_rows":minimum*anchors,
        "allowed_whole_node_losses":n-minimum},
      "deterministic_example":{
        "candidate_anchor_rows":114,"passing_anchor_rows":111,
        "anchor_success_fraction":round(111/114,9),
        "three_failed_anchors_at_three_distinct_nodes":{"complete_nodes":35,"gate_pass":False},
        "three_failed_anchors_at_one_node":{"complete_nodes":37,"gate_pass":True}
      },
      "scenarios":scenarios,
      "hypothetical_minimum_independent_anchor_completeness_to_reach_gate_probability":{
        str(x):round(needed_p(n,minimum,x,anchors),9)
        for x in (0.5,0.8,0.9,0.95)
      },
      "boundary":[
        "These numerical probabilities assume independent anchor outcomes and independent nodes; correlated/bay-level failures or changing eligibility invalidate them.",
        "A complete anchor includes TNC QC, quantitative current BB, matching future BB and undisturbed spatial correspondence; p is not merely chemical recovery.",
        "Method-pilot 9/10 tissue or core yield is not evidence of sufficient complete triplet yield in the later four-bay study.",
        "Do not alter original anchor IDs, rescue with supportive network-scale TNC, relax 36/6 gates, or impute/reassign anchors after future response access.",
        "No ecological outcome, HPLC concentration, observed attrition probability or change in frozen inference is used."
      ]
    }

def self_test()->None:
    assert tail(38,36,1)==1 and tail(38,36,0)==0
    assert abs(tail(3,2,.5)-.5)<1e-12
    assert abs(tail(38,36,.95**3)-.07730774280667545)<1e-12
    assert .986<needed_p(38,36,.8,3)<.987
    print("PASS: frozen 38/36 gate, exact binomial tail, and triplet design")

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,default=CONTRACT)
    ap.add_argument("--out",type=Path,default=OUTPUT)
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        self_test()
        return
    result=build(json.loads(args.contract.read_text()))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],
                      "thresholds":result["hypothetical_minimum_independent_anchor_completeness_to_reach_gate_probability"]}))

if __name__=="__main__":
    main()
