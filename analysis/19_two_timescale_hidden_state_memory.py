#!/usr/bin/env python3
"""Known-truth sufficiency test for a two-timescale hidden-state memory mechanism.

Coarse and quantitative observations come from the same sampled count. Unlike the
failed threshold-only model, the sampling probability is the product of:
1) a slowly varying latent annual persistence/suitability state; and
2) a faster conditional meadow-condition state.

The analysis uses the same Ridge learner, MSE, rows, walk-forward target years,
and tau=10 exponential memory for both observed state dimensions.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "results/two_timescale_hidden_state_memory_v1_contract.json").read_text()
)

G = CONTRACT["simulation_grid"]
P = CONTRACT["prediction_design"]
SITES = int(G["sites"])
YEARS = int(G["years"])
REPS = int(G["replicates_per_cell"])
PHI_SLOW = [float(x) for x in G["phi_slow"]]
PHI_FAST = [float(x) for x in G["phi_fast"]]
SLOW_MEANS = [float(x) for x in G["slow_mean_logit"]]
POINT_COUNTS = [int(x) for x in G["point_count"]]
SLOW_SD = float(G["slow_stationary_sd"])
FAST_SD = float(G["fast_stationary_sd"])
SLOW_SITE_SD = float(G["slow_site_intercept_sd"])
FAST_SITE_SD = float(G["fast_site_intercept_sd"])
FAST_MEAN = float(G["fast_mean_logit"])
SEED = int(G["random_seed"])
TAU = float(P["exponential_tau_years"])
FIRST_SCORE = int(P["first_scored_target_year"])
LAST_SCORE = int(P["last_scored_target_year"])
ALPHA = 1.0


def logistic(x: np.ndarray) -> np.ndarray:
    out = np.empty_like(x, dtype=float)
    pos = x >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-x[pos]))
    ex = np.exp(x[~pos])
    out[~pos] = ex / (1.0 + ex)
    return out


def ar1(
    rng: np.random.Generator,
    site_mean: np.ndarray,
    phi: float,
    stationary_sd: float,
) -> np.ndarray:
    z = np.empty((SITES, YEARS), dtype=float)
    z[:, 0] = site_mean + rng.normal(0.0, stationary_sd, size=SITES)
    innovation_sd = stationary_sd * math.sqrt(max(0.0, 1.0 - phi * phi))
    for t in range(1, YEARS):
        z[:, t] = (
            site_mean
            + phi * (z[:, t - 1] - site_mean)
            + rng.normal(0.0, innovation_sd, size=SITES)
        )
    return z


def simulate(
    rng: np.random.Generator,
    phi_slow: float,
    phi_fast: float,
    slow_mean: float,
    point_count: int,
):
    slow_mu = slow_mean + rng.normal(0.0, SLOW_SITE_SD, size=SITES)
    fast_mu = FAST_MEAN + rng.normal(0.0, FAST_SITE_SD, size=SITES)
    h = ar1(rng, slow_mu, phi_slow, SLOW_SD)
    c = ar1(rng, fast_mu, phi_fast, FAST_SD)

    occupancy_propensity = logistic(h)
    occupied = rng.binomial(1, occupancy_propensity).astype(float)
    conditional_frequency = logistic(c)
    point_probability = occupied * conditional_frequency
    k = rng.binomial(point_count, point_probability)
    frequency = k.astype(float) / float(point_count)
    binary = (k > 0).astype(float)
    return occupancy_propensity, conditional_frequency, occupied, frequency, binary


def exponential_history(obs: np.ndarray) -> np.ndarray:
    out = np.full_like(obs, np.nan, dtype=float)
    for t in range(1, obs.shape[1]):
        ages = np.arange(t, 0, -1, dtype=float)
        w = np.exp(-ages / TAU)
        w /= w.sum()
        out[:, t] = obs[:, :t] @ w
    return out


def rows_for(obs: np.ndarray):
    hist = exponential_history(obs)
    site=[]; year=[]; target=[]; lag1=[]; history=[]
    for t in range(2, YEARS):
        for i in range(SITES):
            site.append(i); year.append(t); target.append(float(obs[i,t]))
            lag1.append(float(obs[i,t-1])); history.append(float(hist[i,t]))
    return {
        "site": np.asarray(site,dtype=int),
        "year": np.asarray(year,dtype=int),
        "target": np.asarray(target,dtype=float),
        "lag1": np.asarray(lag1,dtype=float),
        "history": np.asarray(history,dtype=float),
    }


def site_matrix(site: np.ndarray):
    x=np.zeros((len(site),SITES-1),dtype=float)
    m=site>0
    x[np.nonzero(m)[0],site[m]-1]=1.0
    return x


def design(rows, train_mask, arm: str):
    sx=site_matrix(rows["site"])
    year=rows["year"].astype(float)
    mu=float(year[train_mask].mean()); sd=float(year[train_mask].std(ddof=0))
    if sd<=0: raise RuntimeError("nonpositive training year sd")
    parts=[sx, ((year-mu)/sd)[:,None]]
    if arm in ("lag1","long"):
        parts.append(rows["lag1"][:,None])
    if arm=="long":
        parts.append(rows["history"][:,None])
    return np.hstack(parts)


def yearly_scores(obs: np.ndarray):
    rows=rows_for(obs)
    year=rows["year"]
    y=rows["target"]
    scores={"baseline":[],"lag1":[],"long":[]}
    target_years=[]
    for target_year in range(FIRST_SCORE,LAST_SCORE+1):
        train=year<target_year
        test=year==target_year
        if train.sum()==0 or test.sum()==0:
            raise RuntimeError("empty walk-forward partition")
        target_years.append(target_year)
        for arm in ("baseline","lag1","long"):
            x=design(rows,train,arm)
            model=Ridge(alpha=ALPHA)
            model.fit(x[train],y[train])
            pred=np.clip(model.predict(x[test]),0.0,1.0)
            scores[arm].append(float(mean_squared_error(y[test],pred)))
    return np.asarray(target_years), {k:np.asarray(v) for k,v in scores.items()}


def exact_signflip_p(delta: np.ndarray) -> float:
    delta=np.asarray(delta,dtype=float)
    observed=float(delta.mean())
    n=len(delta)
    count=0; total=1<<n
    for bits in range(total):
        signs=np.ones(n,dtype=float)
        for j in range(n):
            if (bits>>j)&1: signs[j]=-1.0
        if float((delta*signs).mean()) <= observed + 1e-15:
            count+=1
    return count/total


def support(candidate: np.ndarray, reference: np.ndarray):
    delta=candidate-reference
    wins=int((delta<0).sum())
    n=len(delta)
    p=exact_signflip_p(delta)
    passed=bool(
        wins >= math.ceil(0.60*n)
        and float(np.median(delta)) < 0.0
        and p < 0.05
    )
    return {
        "wins":wins, "years":n, "median_delta":float(np.median(delta)),
        "mean_delta":float(delta.mean()), "signflip_p":float(p), "supported":passed,
    }


def state_result(obs: np.ndarray):
    years,s=yearly_scores(obs)
    lag=support(s["lag1"],s["baseline"])
    older=support(s["long"],s["lag1"])
    lag_mean=float(s["lag1"].mean()); long_mean=float(s["long"].mean())
    rel=(lag_mean-long_mean)/lag_mean if lag_mean>0 else 0.0
    return {
        "target_years":years.tolist(),
        "baseline_mean_mse":float(s["baseline"].mean()),
        "lag1_mean_mse":lag_mean,
        "long_mean_mse":long_mean,
        "older_relative_gain":rel,
        "lag1_support":lag,
        "older_support":older,
    }


def cell_key(ps,pf,mean,n):
    return f"phi_slow={ps:g}|phi_fast={pf:g}|slow_mean={mean:g}|points={n}"


def main(outdir: Path):
    outdir.mkdir(parents=True,exist_ok=True)
    rows=[]
    cell_index=0
    for ps,pf,sm,npoints in itertools.product(PHI_SLOW,PHI_FAST,SLOW_MEANS,POINT_COUNTS):
        key=cell_key(ps,pf,sm,npoints)
        for rep in range(REPS):
            rng=np.random.default_rng(SEED + cell_index*10000 + rep)
            q,c,z,freq,binary=simulate(rng,ps,pf,sm,npoints)
            fr=state_result(freq); br=state_result(binary)
            pattern=bool(
                fr["lag1_support"]["supported"]
                and br["lag1_support"]["supported"]
                and br["older_support"]["supported"]
                and not fr["older_support"]["supported"]
            )
            amp=br["older_relative_gain"]-fr["older_relative_gain"]
            rows.append({
                "cell":key,"cell_index":cell_index,"replicate":rep,
                "phi_slow":ps,"phi_fast":pf,"slow_mean_logit":sm,"point_count":npoints,
                "latent_occupancy_propensity_mean":float(q.mean()),
                "realized_occupancy_mean":float(z.mean()),
                "conditional_frequency_mean":float(c.mean()),
                "observed_frequency_mean":float(freq.mean()),
                "binary_prevalence":float(binary.mean()),
                "frequency_lag1_supported":fr["lag1_support"]["supported"],
                "binary_lag1_supported":br["lag1_support"]["supported"],
                "frequency_older_supported":fr["older_support"]["supported"],
                "binary_older_supported":br["older_support"]["supported"],
                "frequency_older_relative_gain":fr["older_relative_gain"],
                "binary_older_relative_gain":br["older_relative_gain"],
                "older_history_amplification":amp,
                "target_pattern":pattern,
            })
        cell_index+=1
    repdf=pd.DataFrame(rows)
    if len(repdf)!=24*REPS:
        raise RuntimeError(f"unexpected replicate count {len(repdf)}")

    cells=(repdf.groupby(
        ["cell","cell_index","phi_slow","phi_fast","slow_mean_logit","point_count"],as_index=False
    ).agg(
        replicates=("replicate","size"),
        mean_binary_prevalence=("binary_prevalence","mean"),
        mean_frequency=("observed_frequency_mean","mean"),
        target_pattern_fraction=("target_pattern","mean"),
        binary_lag1_support_fraction=("binary_lag1_supported","mean"),
        frequency_lag1_support_fraction=("frequency_lag1_supported","mean"),
        binary_older_support_fraction=("binary_older_supported","mean"),
        frequency_older_support_fraction=("frequency_older_supported","mean"),
        median_binary_older_gain=("binary_older_relative_gain","median"),
        median_frequency_older_gain=("frequency_older_relative_gain","median"),
        median_amplification=("older_history_amplification","median"),
    ))
    cells["cell_support"]=(
        (cells["target_pattern_fraction"]>=0.50)
        & (cells["median_amplification"]>0)
    )

    byslow=(cells.groupby("phi_slow",as_index=False).agg(
        cells=("cell","size"),
        supporting_cells=("cell_support","sum"),
        median_pattern_fraction=("target_pattern_fraction","median"),
        median_amplification=("median_amplification","median"),
    ))
    byslow["phi_slow_robust"]=byslow["supporting_cells"]>=6

    rule=CONTRACT["global_support_rule"]
    supporting=int(cells["cell_support"].sum())
    global_pattern=float(repdf["target_pattern"].mean())
    robust=int(byslow["phi_slow_robust"].sum())
    passed=bool(
        supporting>=int(rule["minimum_supporting_cells"])
        and global_pattern>=float(rule["minimum_global_target_pattern_fraction"])
        and robust>=2
    )
    summary={
        "schema":"tampa.two_timescale_hidden_state_memory_v1.result",
        "status":"mechanism_supported" if passed else "mechanism_not_supported",
        "known_truth":{
            "slow_latent_persistence_state":True,
            "fast_conditional_condition_state":True,
            "binary_and_frequency_share_same_sampled_count":True,
            "common_learner":"Ridge(alpha=1.0)",
            "common_loss":"MSE on [0,1]",
            "tau_years":TAU,
        },
        "design":{
            "cells":int(len(cells)),"replicates_per_cell":REPS,
            "total_replicates":int(len(repdf)),"sites":SITES,"years":YEARS,
            "phi_slow":PHI_SLOW,"phi_fast":PHI_FAST,
            "slow_mean_logit":SLOW_MEANS,"point_count":POINT_COUNTS,
        },
        "primary":{
            "supporting_cells":supporting,
            "required_supporting_cells":int(rule["minimum_supporting_cells"]),
            "global_target_pattern_fraction":global_pattern,
            "required_global_target_pattern_fraction":float(rule["minimum_global_target_pattern_fraction"]),
            "robust_phi_slow_levels":robust,
            "required_robust_phi_slow_levels":2,
            "global_median_amplification":float(repdf["older_history_amplification"].median()),
            "support_rule_passed":passed,
        },
        "by_phi_slow":byslow.to_dict("records"),
        "interpretation":(
            "A distinct slow latent persistence/suitability process combined with faster conditional meadow-condition dynamics is sufficient across the frozen grid to reproduce the target state-dimension memory pattern under shared point sampling."
            if passed else
            "The frozen two-timescale latent-state model did not robustly reproduce the full target pattern. This weakens this specific slow-persistence/fast-condition sufficiency explanation."
        ),
        "claim_boundary":CONTRACT["interpretation_boundary"],
    }
    repdf.to_csv(outdir/"two_timescale_replicates.csv",index=False)
    cells.to_csv(outdir/"two_timescale_cells.csv",index=False)
    byslow.to_csv(outdir/"two_timescale_phi_slow_summary.csv",index=False)
    (outdir/"two_timescale_hidden_state_memory_v1.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_two_timescale"))
    args=ap.parse_args()
    main(args.out)
