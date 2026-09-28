#!/usr/bin/env python3
"""Known-truth test of latent occupancy persistence + imperfect detection.

The latent patch state is a first-order Markov chain. Conditional meadow condition
is a faster first-order AR(1). Coarse and quantitative observations are derived
from the same finite point count. Prediction uses the same learner, loss, split
and tau=10 exponential history for both state dimensions.
"""
from __future__ import annotations
import argparse, itertools, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/latent_occupancy_detection_memory_v1_contract.json").read_text())
G=C["simulation_grid"]; P=C["prediction_design"]
SITES=int(G["sites"]); YEARS=int(G["years"]); REPS=int(G["replicates_per_cell"])
P11=[float(x) for x in G["p11"]]; P01=[float(x) for x in G["p01"]]
PHI_FAST=[float(x) for x in G["phi_fast"]]; FAST_MEANS=[float(x) for x in G["fast_mean_logit"]]
POINTS=[int(x) for x in G["point_count"]]
FAST_SD=float(G["fast_stationary_sd"]); FAST_SITE_SD=float(G["fast_site_intercept_sd"])
MASTER=int(G["random_seed"]); TAU=float(P["exponential_tau_years"])
TR0,TR1=[int(x) for x in P["calibration_target_years"]]
TE0,TE1=[int(x) for x in P["heldout_target_years"]]

# Static row geometry and exact sign-flip matrix.
ROW_SITE=np.tile(np.arange(SITES),YEARS-2)
ROW_YEAR=np.repeat(np.arange(2,YEARS),SITES)
SITE_X=np.zeros((len(ROW_SITE),SITES-1),dtype=float)
_mask=ROW_SITE>0
SITE_X[np.nonzero(_mask)[0],ROW_SITE[_mask]-1]=1.0
TRAIN=(ROW_YEAR>=TR0)&(ROW_YEAR<=TR1)
TEST=(ROW_YEAR>=TE0)&(ROW_YEAR<=TE1)
YR_M=float(ROW_YEAR[TRAIN].mean()); YR_SD=float(ROW_YEAR[TRAIN].std(ddof=0))
YEAR_Z=((ROW_YEAR-YR_M)/YR_SD)[:,None]
TEST_YEARS=np.arange(TE0,TE1+1,dtype=int)
HELD_YEAR=ROW_YEAR[TEST]
_codes=np.arange(1<<len(TEST_YEARS),dtype=np.uint16)[:,None]
_bits=(_codes>>np.arange(len(TEST_YEARS),dtype=np.uint16)[None,:])&1
SIGNS=np.where(_bits==1,-1.0,1.0)


def logistic(x):
    return 1.0/(1.0+np.exp(-x))


def simulate_occupancy(rng,p11,p01):
    z=np.empty((SITES,YEARS),dtype=float)
    stationary=p01/(1.0-p11+p01)
    z[:,0]=rng.binomial(1,stationary,size=SITES)
    for t in range(1,YEARS):
        prob=np.where(z[:,t-1]>0.5,p11,p01)
        z[:,t]=rng.binomial(1,prob)
    return z,stationary


def simulate_fast(rng,phi,mean_logit):
    mu=mean_logit+rng.normal(0.0,FAST_SITE_SD,size=SITES)
    x=np.empty((SITES,YEARS),dtype=float)
    x[:,0]=mu+rng.normal(0.0,FAST_SD,size=SITES)
    innov=FAST_SD*math.sqrt(max(0.0,1.0-phi*phi))
    for t in range(1,YEARS):
        x[:,t]=mu+phi*(x[:,t-1]-mu)+rng.normal(0.0,innov,size=SITES)
    return logistic(x)


def exponential_history(obs):
    out=np.full_like(obs,np.nan,dtype=float)
    for t in range(1,YEARS):
        age=np.arange(t,0,-1,dtype=float)
        w=np.exp(-age/TAU); w/=w.sum()
        out[:,t]=obs[:,:t]@w
    return out


def flatten(obs):
    h=exponential_history(obs)
    y=np.concatenate([obs[:,t] for t in range(2,YEARS)])
    lag=np.concatenate([obs[:,t-1] for t in range(2,YEARS)])
    hist=np.concatenate([h[:,t] for t in range(2,YEARS)])
    return y,lag,hist


def yearly_scores(obs):
    y,lag,hist=flatten(obs)
    matrices={
        "baseline":np.hstack([SITE_X,YEAR_Z]),
        "lag1":np.hstack([SITE_X,YEAR_Z,lag[:,None]]),
        "long":np.hstack([SITE_X,YEAR_Z,lag[:,None],hist[:,None]]),
    }
    scores={k:[] for k in matrices}
    ytest=y[TEST]
    for arm,X in matrices.items():
        model=Ridge(alpha=1.0)
        model.fit(X[TRAIN],y[TRAIN])
        pred=np.clip(model.predict(X[TEST]),0.0,1.0)
        for ty in TEST_YEARS:
            m=HELD_YEAR==ty
            scores[arm].append(float(mean_squared_error(ytest[m],pred[m])))
    return {k:np.asarray(v,dtype=float) for k,v in scores.items()}


def exact_signflip_p(delta):
    delta=np.asarray(delta,dtype=float)
    observed=float(delta.mean())
    perm=(SIGNS@delta)/float(len(delta))
    return float(np.mean(perm<=observed+1e-15))


def support(candidate,reference):
    d=candidate-reference
    p=exact_signflip_p(d)
    passed=bool((d<0).sum()>=math.ceil(0.60*len(d)) and float(np.median(d))<0.0 and p<0.05)
    return {
        "wins":int((d<0).sum()),"years":int(len(d)),
        "median_delta":float(np.median(d)),"mean_delta":float(d.mean()),
        "signflip_p":p,"supported":passed,
    }


def state_result(obs):
    s=yearly_scores(obs)
    lag=support(s["lag1"],s["baseline"])
    older=support(s["long"],s["lag1"])
    lm=float(s["lag1"].mean()); hm=float(s["long"].mean())
    gain=(lm-hm)/lm if lm>0 else 0.0
    return lag,older,gain


def key(p11,p01,phi,mean,n):
    return f"p11={p11:g}|p01={p01:g}|phi_fast={phi:g}|fast_mean={mean:g}|points={n}"


def main(outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    rows=[]; ci=0
    for p11,p01,phi,mean,n in itertools.product(P11,P01,PHI_FAST,FAST_MEANS,POINTS):
        cell=key(p11,p01,phi,mean,n)
        for rep in range(REPS):
            rng=np.random.default_rng(MASTER+ci*10000+rep)
            occ,stationary=simulate_occupancy(rng,p11,p01)
            cond=simulate_fast(rng,phi,mean)
            k=rng.binomial(n,occ*cond)
            freq=k.astype(float)/float(n)
            binary=(k>0).astype(float)
            fl,fo,fg=state_result(freq)
            bl,bo,bg=state_result(binary)
            occupied=occ>0.5
            false_neg=float(((binary==0)&occupied).sum()/occupied.sum()) if occupied.sum()>0 else np.nan
            pattern=bool(fl["supported"] and bl["supported"] and bo["supported"] and not fo["supported"])
            rows.append({
                "cell":cell,"cell_index":ci,"replicate":rep,
                "p11":p11,"p01":p01,"phi_fast":phi,"fast_mean_logit":mean,"point_count":n,
                "stationary_occupancy_probability":stationary,
                "realized_occupancy_prevalence":float(occ.mean()),
                "binary_prevalence":float(binary.mean()),
                "frequency_mean":float(freq.mean()),
                "false_negative_rate_given_occupied":false_neg,
                "binary_lag1_supported":bl["supported"],
                "frequency_lag1_supported":fl["supported"],
                "binary_older_supported":bo["supported"],
                "frequency_older_supported":fo["supported"],
                "binary_older_relative_gain":bg,
                "frequency_older_relative_gain":fg,
                "older_history_amplification":bg-fg,
                "target_pattern":pattern
            })
        ci+=1
    rep=pd.DataFrame(rows)
    if len(rep)!=32*REPS: raise RuntimeError(f"unexpected replicate count {len(rep)}")
    cells=(rep.groupby(["cell","cell_index","p11","p01","phi_fast","fast_mean_logit","point_count"],as_index=False)
        .agg(
            replicates=("replicate","size"),
            target_pattern_fraction=("target_pattern","mean"),
            binary_lag1_support_fraction=("binary_lag1_supported","mean"),
            frequency_lag1_support_fraction=("frequency_lag1_supported","mean"),
            binary_older_support_fraction=("binary_older_supported","mean"),
            frequency_older_support_fraction=("frequency_older_supported","mean"),
            median_amplification=("older_history_amplification","median"),
            median_binary_older_gain=("binary_older_relative_gain","median"),
            median_frequency_older_gain=("frequency_older_relative_gain","median"),
            mean_false_negative_rate=("false_negative_rate_given_occupied","mean"),
            mean_binary_prevalence=("binary_prevalence","mean"),
            mean_frequency=("frequency_mean","mean")
        ))
    cells["cell_support"]=(cells["target_pattern_fraction"]>=0.50)&(cells["median_amplification"]>0)
    byp=(cells.groupby("p11",as_index=False).agg(
        cells=("cell","size"),supporting_cells=("cell_support","sum"),
        median_pattern_fraction=("target_pattern_fraction","median"),
        median_amplification=("median_amplification","median"),
        median_false_negative_rate=("mean_false_negative_rate","median")
    ))
    byp["p11_robust"]=byp["supporting_cells"]>=12
    supporting=int(cells["cell_support"].sum())
    global_pattern=float(rep["target_pattern"].mean())
    robust=int(byp["p11_robust"].sum())
    passed=bool(supporting>=24 and global_pattern>=0.50 and robust==2)
    summary={
        "schema":"tampa.latent_occupancy_detection_memory_v1.result",
        "status":"mechanism_supported" if passed else "mechanism_not_supported",
        "known_truth":{
            "latent_occupancy_markov_order":1,
            "fast_condition_markov_order":1,
            "binary_and_frequency_share_same_sampled_count":True,
            "common_learner":"Ridge(alpha=1.0)","common_loss":"MSE on [0,1]","tau_years":TAU
        },
        "design":{
            "cells":int(len(cells)),"replicates_per_cell":REPS,"total_replicates":int(len(rep)),
            "sites":SITES,"years":YEARS,"p11":P11,"p01":P01,"phi_fast":PHI_FAST,
            "fast_mean_logit":FAST_MEANS,"point_count":POINTS
        },
        "primary":{
            "supporting_cells":supporting,"required_supporting_cells":24,
            "global_target_pattern_fraction":global_pattern,"required_global_target_pattern_fraction":0.50,
            "robust_p11_levels":robust,"required_robust_p11_levels":2,
            "global_median_amplification":float(rep["older_history_amplification"].median()),
            "support_rule_passed":passed
        },
        "diagnostic":{
            "binary_lag1_support_fraction":float(rep["binary_lag1_supported"].mean()),
            "frequency_lag1_support_fraction":float(rep["frequency_lag1_supported"].mean()),
            "binary_older_support_fraction":float(rep["binary_older_supported"].mean()),
            "frequency_older_support_fraction":float(rep["frequency_older_supported"].mean()),
            "median_false_negative_rate_given_occupied":float(rep["false_negative_rate_given_occupied"].median()),
            "median_binary_prevalence":float(rep["binary_prevalence"].median())
        },
        "by_p11":byp.to_dict("records"),
        "interpretation":(
            "Explicit first-order latent patch persistence plus imperfect detection is sufficient across the frozen grid to reproduce immediate memory in both states with older-history support concentrated in coarse recorded state."
            if passed else
            "The frozen latent-occupancy/detection model did not robustly reproduce the complete Tampa state-dimension memory pattern."
        ),
        "hard_stop":C["hard_stop"],
        "claim_boundary":C["interpretation_boundary"]
    }
    rep.to_csv(outdir/"latent_occupancy_replicates.csv",index=False)
    cells.to_csv(outdir/"latent_occupancy_cells.csv",index=False)
    byp.to_csv(outdir/"latent_occupancy_p11_summary.csv",index=False)
    (outdir/"latent_occupancy_detection_memory_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,default=Path("results/generated_latent_occupancy"))
    args=ap.parse_args(); main(args.out)
