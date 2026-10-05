#!/usr/bin/env python3
"""Frozen network-scale supportive analysis for Tampa four-bay prospective TNC v2.

Historical filename retained for compatibility. Paper-level decisive priority is
frozen separately in results/clonal_state_inference_hierarchy_v1.json.

This script is intended to be frozen before future meadow outcomes are opened.

Primary model:
    future_delta_frequency
      ~ baseline_frequency
      + baseline_braun_blanquet
      + z_rhizome_tnc
      + water_body

Key rules:
- complete-case node analysis only;
- stable transect node is the inferential unit;
- TNC is standardized once using the original analytic sample mean and sample SD;
- outcome remains on the raw frequency-change scale;
- Old Tampa Bay is the reference level for three water-body indicators;
- uncertainty is a 10,000-replicate node bootstrap stratified by water body;
- percentile 95% CI determines supported / contradicted / unsupported;
- no one-sided inference;
- confirmatory only with >=36 nodes total and >=6 per bay.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
REFERENCE_BAY="Old Tampa Bay"
BOOTSTRAP_REPS=10000
BOOTSTRAP_SEED=20261003
MIN_TOTAL=36
MIN_PER_BAY=6

BASELINE_REQUIRED={
    "node_id","water_body","baseline_frequency",
    "baseline_braun_blanquet","rhizome_tnc_mg_g"
}
FUTURE_REQUIRED={"node_id","future_frequency"}


def finite_numeric(s):
    return pd.to_numeric(s,errors="coerce")


def prepare(baseline:pd.DataFrame,future:pd.DataFrame):
    if m:=BASELINE_REQUIRED-set(baseline.columns):
        raise RuntimeError(f"baseline missing columns: {sorted(m)}")
    if m:=FUTURE_REQUIRED-set(future.columns):
        raise RuntimeError(f"future missing columns: {sorted(m)}")
    if baseline["node_id"].astype(str).duplicated().any():
        raise RuntimeError("baseline must contain one row per stable node")
    if future["node_id"].astype(str).duplicated().any():
        raise RuntimeError("future must contain one row per stable node")

    b=baseline[list(BASELINE_REQUIRED)].copy()
    f=future[list(FUTURE_REQUIRED)].copy()
    x=b.merge(f,on="node_id",how="inner",validate="one_to_one")
    x["water_body"]=x["water_body"].astype(str)
    x=x[x["water_body"].isin(BAYS)].copy()

    for col in ("baseline_frequency","baseline_braun_blanquet","rhizome_tnc_mg_g","future_frequency"):
        x[col]=finite_numeric(x[col])
    x=x.dropna(subset=[
        "baseline_frequency","baseline_braun_blanquet",
        "rhizome_tnc_mg_g","future_frequency","water_body"
    ]).copy()

    x["future_delta_frequency"]=x["future_frequency"]-x["baseline_frequency"]
    tnc_mean=float(x["rhizome_tnc_mg_g"].mean())
    tnc_sd=float(x["rhizome_tnc_mg_g"].std(ddof=1))
    if not np.isfinite(tnc_sd) or tnc_sd<=0:
        raise RuntimeError("rhizome TNC has zero/nonfinite sample SD")
    x["z_rhizome_tnc"]=(x["rhizome_tnc_mg_g"]-tnc_mean)/tnc_sd
    return x,tnc_mean,tnc_sd


def design_matrix(x:pd.DataFrame):
    cols=[
        np.ones(len(x),dtype=float),
        x["baseline_frequency"].to_numpy(float),
        x["baseline_braun_blanquet"].to_numpy(float),
        x["z_rhizome_tnc"].to_numpy(float),
    ]
    names=["intercept","baseline_frequency","baseline_braun_blanquet","z_rhizome_tnc"]
    for bay in BAYS:
        if bay==REFERENCE_BAY:
            continue
        cols.append((x["water_body"].to_numpy(str)==bay).astype(float))
        names.append("water_body["+bay+"]")
    X=np.column_stack(cols)
    y=x["future_delta_frequency"].to_numpy(float)
    return X,y,names


def fit_tnc_coef(x:pd.DataFrame):
    X,y,names=design_matrix(x)
    if np.linalg.matrix_rank(X)<X.shape[1]:
        return np.nan
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    return float(coef[names.index("z_rhizome_tnc")])


def bootstrap_ci(x:pd.DataFrame):
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    groups={b:x[x["water_body"]==b].reset_index(drop=True) for b in BAYS}
    vals=[]
    invalid=0
    for _ in range(BOOTSTRAP_REPS):
        parts=[]
        for bay in BAYS:
            g=groups[bay]
            idx=rng.integers(0,len(g),size=len(g))
            parts.append(g.iloc[idx])
        z=pd.concat(parts,ignore_index=True)
        coef=fit_tnc_coef(z)
        if np.isfinite(coef):
            vals.append(coef)
        else:
            invalid+=1
    if len(vals)<int(0.95*BOOTSTRAP_REPS):
        raise RuntimeError(
            f"too many rank-deficient/nonfinite bootstrap replicates: "
            f"{invalid}/{BOOTSTRAP_REPS}"
        )
    a=np.asarray(vals,float)
    return {
        "valid_replicates":int(len(a)),
        "invalid_replicates":int(invalid),
        "ci95":[float(np.quantile(a,0.025)),float(np.quantile(a,0.975))],
        "median":float(np.median(a)),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline",required=True)
    ap.add_argument("--future",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    baseline=pd.read_csv(args.baseline)
    future=pd.read_csv(args.future)
    x,tnc_mean,tnc_sd=prepare(baseline,future)

    counts={b:int((x["water_body"]==b).sum()) for b in BAYS}
    confirmatory=bool(len(x)>=MIN_TOTAL and all(counts[b]>=MIN_PER_BAY for b in BAYS))

    point=fit_tnc_coef(x)
    if not np.isfinite(point):
        raise RuntimeError("primary design matrix is rank-deficient")

    boot=bootstrap_ci(x)
    lo,hi=boot["ci95"]
    if lo>0:
        interval_classification="supported_positive"
    elif hi<0:
        interval_classification="contradicted_direction"
    else:
        interval_classification="unsupported"

    result={
        "schema":"tampa.tnc_v2_primary_analysis.v1",
        "paper_level_role":"supportive_network_generality",
        "inferential_hierarchy_contract":"results/clonal_state_inference_hierarchy_v1.json",
        "analysis_frozen":True,
        "inferential_unit":"stable transect node",
        "geography":list(BAYS),
        "reference_water_body":REFERENCE_BAY,
        "complete_case_nodes":int(len(x)),
        "nodes_by_water_body":counts,
        "confirmatory_replication_gate":{
            "minimum_total":MIN_TOTAL,
            "minimum_per_bay":MIN_PER_BAY,
            "passed":confirmatory,
        },
        "standardization":{
            "tnc":"z-score once using original analytic-sample mean and sample SD (ddof=1)",
            "tnc_mean_mg_g":tnc_mean,
            "tnc_sd_mg_g":tnc_sd,
            "outcome":"future_frequency - baseline_frequency on raw frequency scale",
        },
        "model":"future_delta_frequency ~ baseline_frequency + baseline_braun_blanquet + z_rhizome_tnc + water_body",
        "primary_coefficient":{
            "name":"z_rhizome_tnc",
            "estimate":point,
            "units":"future-frequency change per 1 analytic-sample SD higher baseline TNC",
        },
        "uncertainty":{
            "method":"water-body-stratified node bootstrap",
            "repetitions":BOOTSTRAP_REPS,
            "seed":BOOTSTRAP_SEED,
            **boot,
        },
        "support_rule":{
            "supported":"two-sided percentile 95% CI entirely above 0",
            "contradicted_direction":"two-sided percentile 95% CI entirely below 0",
            "unsupported":"CI overlaps 0",
            "one_sided_test_allowed":False,
            "interval_classification":interval_classification,
        },
        "interpretation_status":(
            interval_classification if confirmatory
            else "pilot_only_replication_gate_failed"
        ),
        "claim_boundary":[
            "A positive supported coefficient is a prospective network-scale reserve-state association, not proof of causal clonal buffering.",
            "This network-scale result cannot rescue an unsupported or non-estimable within-node decisive state-augmentation primary.",
            "If the replication gate fails, a null/overlapping interval cannot reject reserve buffering.",
            "Do not replace a null TNC primary with soluble sugar, starch, nutrient-adjusted TNC, meristem density or a selected subgroup.",
            "Binary re-recording/reappearance is not the primary outcome and is not ecological recovery."
        ],
    }
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
