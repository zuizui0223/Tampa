#!/usr/bin/env python3
"""Frozen primary analysis for Tampa event-scale hot-fresh stress debt."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
REFERENCE_BAY="Old Tampa Bay"
BOOTSTRAP_REPS=10000
BOOTSTRAP_SEED=20261004
MIN_TOTAL=30
MIN_PER_BAY=8
MIN_NONZERO_NODES=10
MIN_NONZERO_BAYS=2
MIN_VARIATION_BAYS=2
MIN_NODES_VARIATION_BAY=6
MIN_DISTINCT_EXPOSURES=3

REQ={
 "node_id","water_body","tnc_pre_mg_g","tnc_post_mg_g",
 "joint_hot_fresh_hours_30_25","paired_coverage_fraction",
 "common_overlap_days","pre_post_tnc_interval_days","primary_qc_pass"
}

def truth(v):
    return str(v).strip().lower() in {"1","true","yes","y","pass","passed"}

def prep(df):
    if m:=REQ-set(df.columns): raise RuntimeError(f"missing columns: {sorted(m)}")
    if df["node_id"].astype(str).duplicated().any(): raise RuntimeError("one row per node required")
    x=df.copy()
    x["water_body"]=x["water_body"].astype(str)
    x=x[x["water_body"].isin(BAYS)].copy()
    for col in ["tnc_pre_mg_g","tnc_post_mg_g","joint_hot_fresh_hours_30_25",
                "paired_coverage_fraction","common_overlap_days","pre_post_tnc_interval_days"]:
        x[col]=pd.to_numeric(x[col],errors="coerce")
    x=x[x["primary_qc_pass"].map(truth)].copy()
    x=x.dropna(subset=[
      "tnc_pre_mg_g","tnc_post_mg_g","joint_hot_fresh_hours_30_25",
      "paired_coverage_fraction","common_overlap_days","pre_post_tnc_interval_days"
    ])
    x=x[x["paired_coverage_fraction"]>=0.85]
    x=x[x["common_overlap_days"]>=35]
    x=x[x["pre_post_tnc_interval_days"].between(39,45)]
    return x.reset_index(drop=True)

def design(x):
    cols=[
      np.ones(len(x)),
      x["tnc_pre_mg_g"].to_numpy(float),
      x["joint_hot_fresh_hours_30_25"].to_numpy(float)
    ]
    names=["intercept","tnc_pre_mg_g","joint_hot_fresh_hours_30_25"]
    for bay in BAYS:
        if bay==REFERENCE_BAY: continue
        cols.append((x["water_body"].to_numpy(str)==bay).astype(float))
        names.append("water_body["+bay+"]")
    return np.column_stack(cols),x["tnc_post_mg_g"].to_numpy(float),names

def coef(x):
    X,y,names=design(x)
    if np.linalg.matrix_rank(X)<X.shape[1]: return np.nan
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    return float(b[names.index("joint_hot_fresh_hours_30_25")])

def gates(x):
    counts={b:int((x["water_body"]==b).sum()) for b in BAYS}
    sample=bool(len(x)>=MIN_TOTAL and all(counts[b]>=MIN_PER_BAY for b in BAYS))
    nonzero=x["joint_hot_fresh_hours_30_25"]>0
    nz_bays=[b for b in BAYS if ((x["water_body"]==b)&nonzero).any()]
    nonzero_gate=bool(int(nonzero.sum())>=MIN_NONZERO_NODES and len(nz_bays)>=MIN_NONZERO_BAYS)
    varying=[]
    distinct={}
    for b in BAYS:
        z=x.loc[x["water_body"]==b,"joint_hot_fresh_hours_30_25"]
        distinct[b]=int(z.nunique())
        if len(z)>=MIN_NODES_VARIATION_BAY and z.nunique()>=MIN_DISTINCT_EXPOSURES:
            varying.append(b)
    within=bool(len(varying)>=MIN_VARIATION_BAYS)
    return counts,sample,nonzero_gate,within,nz_bays,varying,distinct

def boot(x):
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    groups={b:x[x["water_body"]==b].reset_index(drop=True) for b in BAYS}
    vals=[]; invalid=0
    for _ in range(BOOTSTRAP_REPS):
        parts=[]
        for b in BAYS:
            g=groups[b]
            idx=rng.integers(0,len(g),size=len(g))
            parts.append(g.iloc[idx])
        z=pd.concat(parts,ignore_index=True)
        v=coef(z)
        if np.isfinite(v): vals.append(v)
        else: invalid+=1
    if len(vals)<0.95*BOOTSTRAP_REPS:
        raise RuntimeError(f"valid bootstrap replicates {len(vals)} <95%")
    a=np.asarray(vals,float)
    return {
      "valid_replicates":len(a),"invalid_replicates":invalid,
      "ci95":[float(np.quantile(a,.025)),float(np.quantile(a,.975))],
      "ci97_5":[float(np.quantile(a,.0125)),float(np.quantile(a,.9875))],
      "median":float(np.median(a))
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    x=prep(pd.read_csv(a.input))
    counts,sample,nz,within,nz_bays,var_bays,distinct=gates(x)
    point=coef(x)
    if not np.isfinite(point): raise RuntimeError("primary design matrix rank-deficient")
    b=boot(x)
    lo,hi=b["ci95"]
    interval="supported_negative" if hi<0 else "contradicted_direction" if lo>0 else "unsupported"
    estimable=sample and nz and within
    status=interval if estimable else "nonestimable_or_pilot_gate_failed"
    res={
      "schema":"tampa.event_stress_primary_analysis.v1",
      "model":"tnc_post ~ tnc_pre + joint_hot_fresh_hours_30_25 + water_body",
      "primary_coefficient":{"name":"joint_hot_fresh_hours_30_25","estimate":point,"units":"mg g-1 post-TNC per joint hot-fresh hour"},
      "analytic_nodes":len(x),"nodes_by_water_body":counts,
      "gates":{
        "sample_gate_passed":sample,"nonzero_exposure_gate_passed":nz,
        "within_bay_identifiability_passed":within,
        "nonzero_exposure_bays":nz_bays,"within_bay_variation_bays":var_bays,
        "distinct_exposure_values_by_bay":distinct
      },
      "uncertainty":{"method":"water-body-stratified stable-node bootstrap","repetitions":BOOTSTRAP_REPS,"seed":BOOTSTRAP_SEED,**b},
      "standalone_interval_classification":interval,
      "interpretation_status":status,
      "family_level_ci97_5":b["ci97_5"],
      "claim_boundary":[
        "If sample or exposure-identifiability gates fail, do not interpret the primary coefficient as network-scale event stress.",
        "Do not remove water_body, retune 30 C / 25 ppt, move the July 24-September 3 window, or select nodes after TNC inspection.",
        "Support is a hot-fresh event-complex association with reserve depletion, not proof that 30 C itself causes heat injury."
      ]
    }
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps(res,indent=2,sort_keys=True))
if __name__=="__main__": main()
