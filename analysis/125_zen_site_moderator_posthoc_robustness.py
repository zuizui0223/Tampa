#!/usr/bin/env python3
"""Post-hoc site-level moderator sensitivity for the source-frozen 15-site ZEN experiment.

Data: published 2011 ZEN grazer deterrent x nutrient experiment, original CSV
previously verified and reaggregated in the pinned result JSON. 15 sites are
the only independent geographic replicates. This tests a *screen* of the
temperature, salinity, grazer-richness moderators already inspected.

The screen was selected AFTER seeing the site contrasts, so even a small
permutation p-value is NOT preregistered confirmation. No mediation/causality.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/zen_15site_mesograzer_exploratory_verified_20261124.json"
PREDICTORS=("temp_avg","sal","grazer_richness_site")
PERM=20000
SEED=2026112418

def corr(x,y):
    if len(x)!=len(y) or len(x)<5 or any(not math.isfinite(z) for z in x+y):
        return None
    mu=sum(x)/len(x); mv=sum(y)/len(y)
    xx=sum((z-mu)**2 for z in x);yy=sum((z-mv)**2 for z in y)
    if xx==0 or yy==0:return None
    return sum((a-mu)*(b-mv) for a,b in zip(x,y))/math.sqrt(xx*yy)

def ranks(x):
    order=sorted(range(len(x)),key=lambda i:x[i])
    out=[0.]*len(x)
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]:j+=1
        midrank=((i+1)+j)/2
        for k in order[i:j]:out[k]=midrank
        i=j
    return out

def calculate(pinned):
    if pinned.get("schema")!="tampa.zen_global_mesograzer_15site_exploratory_v1":
        raise ValueError("Unrecognized source schema")
    if pinned.get("status")!="response_open_exploratory_comparative_experiment":
        raise ValueError("Unexpected source evidence type")
    if pinned["source"].get("sha256")!="5a97763735a22076eac25a86736c50cb12611a529c5e233941fbc3a73ad4c6ae":
        raise ValueError("ZEN original source digest changed")
    sites=pinned["analysis"]["per_site_exploratory_contrasts"]
    if len(sites)!=15 or len({s["site"] for s in sites})!=15:
        raise ValueError("Expected 15 independent site records")
    ys=[s["endpoints"]["chla_per_Zostera"]["posthoc_log_arm_mean_contrasts"]["grazer_deterrent_main_difference"] for s in sites]
    obs={}
    xs={}
    for var in PREDICTORS:
        x=[s["cross_site_predictors"][var] for s in sites]
        if any(v is None for v in x):raise ValueError("Missing site-level measured predictor")
        xs[var]=x
        obs[var]={"pearson_r":corr(x,ys),"spearman_r":corr(ranks(x),ranks(ys)),
                  "n_sites":len(ys)}
        loo=[]
        for i,site in enumerate(sites):
            xx=[z for k,z in enumerate(x) if k!=i]
            yy=[z for k,z in enumerate(ys) if k!=i]
            loo.append({"omit":site["site"],"r":corr(xx,yy)})
        obs[var]["leave_one_site_out_pearson_min"]=min(z["r"] for z in loo)
        obs[var]["leave_one_site_out_pearson_max"]=max(z["r"] for z in loo)
        obs[var]["leave_one_site_out_extremes"]=(
            min(loo,key=lambda z:z["r"]),max(loo,key=lambda z:z["r"]))
    rng=random.Random(SEED)
    null_exceed={v:0 for v in PREDICTORS}
    max_exceed={v:0 for v in PREDICTORS}
    max_abs_observed={v:abs(obs[v]["pearson_r"]) for v in PREDICTORS}
    for i in range(PERM):
        shuffled=ys.copy()
        rng.shuffle(shuffled)
        null={v:abs(corr(xs[v],shuffled)) for v in PREDICTORS}
        m=max(null.values())
        for v in PREDICTORS:
            null_exceed[v]+=int(null[v]>=max_abs_observed[v])
            max_exceed[v]+=int(m>=max_abs_observed[v])
    for var in PREDICTORS:
        obs[var]["two_sided_unadjusted_site_label_permutation_p"]=(1+null_exceed[var])/(1+PERM)
        obs[var]["three_predictor_familywise_maxT_permutation_p"]=(1+max_exceed[var])/(1+PERM)
    return {
        "schema":"tampa.zen_site_moderator_posthoc_robustness_v1",
        "evidence_class":"response_exposed_hypothesis_generation_not_new_global_confirmation",
        "source":"results/zen_15site_mesograzer_exploratory_verified_20261124.json",
        "source_raw_data_sha256":pinned["source"]["sha256"],
        "global_differences_are_site_specific_log_ratios_not_seagrass_biomass":True,
        "outcome":"15-site grazer-deterrent effect on epiphytic chlorophyll-a (log ratio)",
        "predictor_results":obs,
        "permutation": {"draws":PERM,"seed":SEED,"familywise_three_previously_screened_predictors":True,
                        "randomization_unit":"whole_site_effects_permuted_against_fixed_site_covariates_not_original_2011_experimental_randomization"},
        "limitations":[
            "Temperature and salinity were observed environmental contexts, not manipulated factors.",
            "Original Duffy et al. 2015 study already tested the importance of grazer diversity vs environmental gradients.",
            "Selection of moderators and log effect occurred after seeing outcomes: permutation thresholds cannot undo researcher degrees of freedom.",
            "15 site labels, not 600 plot observations, form the geographic replication.",
            "No broad climatic generalization or temperature-causal grazer mechanism is supported by this retrospective screen.",
            "Three-predictor maxT handles this declared family only; it does not correct for every tested hypothesis in the existing literature.",
        ]
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None);a=p.parse_args()
    j=json.loads(SOURCE.read_text())
    result=calculate(j)
    payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(payload,encoding="utf-8")
    else:print(payload,end="")

if __name__=="__main__":
    main()
