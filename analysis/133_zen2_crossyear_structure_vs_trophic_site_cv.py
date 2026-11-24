#!/usr/bin/env python3
"""Leave-one-geographic-site-out ZEN2 structural vs trophic transport benchmark.

Dataset is response-OPEN: 2014 nearest source-verified vegetation summary +
2015 ZEN2 original site experiment, 14 coordinates/code-gated localities.
Only one predictor (2014 shoot density) for three separate 2015 outcomes:
2015 shoot density, 2015 edge risk difference and 2015 80%-thinning risk
difference. Four baseline comparisons add 2014 periphyton as an exploratory
alternative, but are not new confirmatory ecological tests.

This design avoids pseudo-replication, test-site response leakage and 
re-optimization to the left-out outcome. Its LOOCV is resampling *within
one response-open study program*, not a prospective prediction.
"""
from __future__ import annotations
import argparse
import json
import math
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/zen2_2014_prior_state_2015_trophic_risk_verified_20261124.json"
MIN_SITES=10
PAIRINGS=(
    ("year2014_shoot_density","year2015_ambient_shoot_density","log1p_response"),
    ("year2014_shoot_density","year2015_edge_minus_interior_risk","risk_difference"),
    ("year2014_shoot_density","year2015_eighty_minus_ambient_risk","risk_difference"),
    ("year2014_epiphyton","year2015_edge_minus_interior_risk","risk_difference"),
    ("year2014_epiphyton","year2015_eighty_minus_ambient_risk","risk_difference"),
)

def transformed(value, kind):
    if value is None:raise ValueError("Unexpected missing numeric value")
    v=float(value)
    if not math.isfinite(v):raise ValueError("Nonfinite")
    if kind=="log1p_predictor" or kind=="log1p_response":
        if v<0:raise ValueError("Negative abundance or biomass")
        return math.log1p(v)
    if kind=="risk_difference":return v
    raise ValueError("Unexpected transform")

def fit_ols(x,y):
    if len(x)!=len(y) or len(x)<5:raise ValueError("Too few training sites")
    a=statistics.mean(x);b=statistics.mean(y)
    xx=sum((v-a)**2 for v in x)
    if xx<=1e-14:
        return {"intercept":b,"slope":0.0,"reason":"constant_training_predictor"}
    coef=sum((p-a)*(q-b) for p,q in zip(x,y))/xx
    return {"intercept":b-coef*a,"slope":coef,"reason":"valid_ordinary_least_squares"}

def cv(rows,pred,response,kind):
    subset=[
        row for row in rows
        if row.get(pred) is not None and row.get(response) is not None
    ]
    if len(subset)<MIN_SITES or len({r["site_code"] for r in subset})!=len(subset):
        raise ValueError("Wrong geographic replication or missingness")
    xs=[transformed(r[pred],"log1p_predictor") for r in subset]
    ys=[transformed(r[response],kind) for r in subset]
    held=[]
    for i,row in enumerate(subset):
        x_train=xs[:i]+xs[i+1:]
        y_train=ys[:i]+ys[i+1:]
        model=fit_ols(x_train,y_train)
        predicted=model["intercept"]+model["slope"]*xs[i]
        baseline=statistics.mean(y_train)
        held.append({
            "site":row["site_code"],
            "observed":ys[i],"predicted":predicted,"baseline_prediction":baseline,
            "residual_model":ys[i]-predicted,
            "residual_baseline":ys[i]-baseline,
            "training_slope":model["slope"],
            "distance_km":row["nearest_distance_km"],
        })
    numer=sum(h["residual_model"]**2 for h in held)
    denom=sum(h["residual_baseline"]**2 for h in held)
    if denom<=1e-14:raise ValueError("Near-constant outcome with no benchmark")
    return {
        "prior_predictor":pred,
        "later_outcome":response,
        "response_scale":kind,
        "cross_validation":"each of n site-level records left out once, OLS fit to remaining n-1",
        "n_site_codes":len(subset),
        "site_codes":[x["site_code"] for x in subset],
        "training_only_reference_mean_rmse":math.sqrt(denom/len(held)),
        "prior_state_model_rmse":math.sqrt(numer/len(held)),
        "site_equal_cv_r2_against_fold_training_mean":1-numer/denom,
        "n_sites_model_absolute_error_better_than_fold_reference":sum(
            abs(h["residual_model"])<abs(h["residual_baseline"]) for h in held
        ),
        "slope_min_across_folds":min(h["training_slope"] for h in held),
        "slope_max_across_folds":max(h["training_slope"] for h in held),
        "held_out_site_predictions":held,
    }

def report(source):
    if source.get("schema")!="tampa.zen2_nearest_subsite_2014_prior_state_2015_interaction_exploratory_v1":
        raise ValueError("Incorrect original source-backed crossyear schema")
    if source.get("n_match")!=14 or len(source.get("candidate_sites",[]))!=14:
        raise ValueError("Unexpected frozen site-matched cohort")
    sites=source["candidate_sites"]
    result=[
        cv(sites,pred,response,kind)
        for pred,response,kind in PAIRINGS
    ]
    short=[s for s in sites if s["nearest_distance_km"]<=5]
    if len(short)!=13:raise ValueError("Geographic eligibility 5km drift")
    strict=[
        cv(short,"year2014_shoot_density","year2015_ambient_shoot_density","log1p_response"),
        cv(short,"year2014_shoot_density","year2015_eighty_minus_ambient_risk","risk_difference"),
    ]
    return {
        "schema":"tampa.zen2_crossyear_site_cv_predictive_skill_v1",
        "evidence_class":"response_exposed_exploratory_leave_site_out_model_comparison",
        "original_sources":source["source_shas"],
        "original_geographic_cohort_site_count":14,
        "one_geography_one_cv_unit":True,
        "baseline":"mean of the n-1 training sites on the same outcome scale, recomputed inside each fold",
        "model":"one predictor + intercept ordinary least squares, both fitted only within n-1 site labels",
        "original_14_site_models":result,
        "stricter_5km_sensitivity":strict,
        "interpretation_stops":[
            "Models, endpoints and transformations were chosen after prior ZEN2 outcomes had already been seen.",
            "This within-program leave-one-site-out fit is NOT a prospective or untouched independent external validation.",
            "The original Hovel et al. 2021 already modeled same-year vegetation and predation relationships.",
            "CV R2 measures prediction error relative to a simple baseline, not the absence/presence of causal ecological interactions.",
            "Shoot density is from nearby sites in two years, not repeated fixed quadrats or plant-specific survival.",
            "Risk outcome is a site-level binary tether-assay contrast heavily affected by predation ceiling.",
            "Reported CV scores are posthoc descriptive; do not claim accepted models or generality without new independent sampled years/sites.",
            "Only 14 source-matched localities, some sharing research network and physical regimes.",
        ]
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=None)
    args=parser.parse_args()
    result=report(json.loads(SOURCE.read_text()))
    content=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(content,encoding="utf-8")
    else:print(content,end="")

if __name__=="__main__":
    main()
