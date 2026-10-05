#!/usr/bin/env python3
"""Frozen primary analysis for Tampa history-linked functional insurance.

Question
--------
Within the same stable meadow, does a point where Thalassia was historically
lost but another seagrass retained occupancy show different present-day
hydrodynamic attenuation than a nearby point with >=3 years of continuous
Thalassia occupancy?

The analysis is frozen before any hydrodynamic outcome is collected.

Primary estimand
----------------
Equal-node mean paired difference in attenuation_p90:

    loss-legacy alternative state - persistent-Thalassia state

A 10,000-replicate stable-node paired bootstrap is stratified by Old versus
Middle Tampa Bay. An interval overlapping zero is unresolved, NOT evidence of
functional equivalence.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

BAYS=("Old Tampa Bay","Middle Tampa Bay")
STATES=("loss_legacy_alternative","persistent_thalassia")
BOOT=10000
SEED=20261008
MIN_PAIRS=16
MIN_PER_BAY=6
MAX_PAIR_DISTANCE_M=100.0
MIN_VALID_DAYS=15

REQ={
    "node_id","water_body","functional_state","attenuation_p90",
    "total_vegetated_cover","canopy_height","pair_distance_m","valid_days",
    "measurement_qc_pass","simultaneous_pair_pass","state_eligibility_pass",
}

def as_bool(s:pd.Series)->pd.Series:
    if s.dtype==bool:
        return s
    return s.astype(str).str.strip().str.lower().map({
        "true":True,"false":False,"1":True,"0":False
    })

def prepare(df:pd.DataFrame)->pd.DataFrame:
    miss=REQ-set(df.columns)
    if miss:
        raise RuntimeError(f"missing columns: {sorted(miss)}")
    z=df.copy()
    for c in ("attenuation_p90","total_vegetated_cover","canopy_height","pair_distance_m","valid_days"):
        z[c]=pd.to_numeric(z[c],errors="coerce")
    for c in ("measurement_qc_pass","simultaneous_pair_pass","state_eligibility_pass"):
        z[c]=as_bool(z[c])
    z=z[
        z["water_body"].isin(BAYS)
        & z["functional_state"].isin(STATES)
        & (z["measurement_qc_pass"]==True)
        & (z["simultaneous_pair_pass"]==True)
        & (z["state_eligibility_pass"]==True)
        & (z["valid_days"]>=MIN_VALID_DAYS)
        & (z["pair_distance_m"]<=MAX_PAIR_DISTANCE_M)
    ].dropna(subset=[
        "node_id","water_body","functional_state","attenuation_p90",
        "total_vegetated_cover","canopy_height","pair_distance_m","valid_days"
    ]).copy()

    keep=[]
    for node,g in z.groupby("node_id",sort=False):
        if len(g)!=2 or g["functional_state"].nunique()!=2 or g["water_body"].nunique()!=1:
            continue
        if set(g["functional_state"])!=set(STATES):
            continue
        if g["pair_distance_m"].nunique()!=1:
            continue
        keep.append(g)
    if not keep:
        return z.iloc[0:0].copy()
    return pd.concat(keep,ignore_index=True)

def pair_table(d:pd.DataFrame)->pd.DataFrame:
    p=d.pivot(index=["node_id","water_body"],columns="functional_state",values="attenuation_p90").reset_index()
    p["paired_difference"]=p["loss_legacy_alternative"]-p["persistent_thalassia"]
    return p

def paired_bootstrap(p:pd.DataFrame)->np.ndarray:
    rng=np.random.default_rng(SEED)
    vals=[]
    by={b:p[p["water_body"]==b].reset_index(drop=True) for b in BAYS}
    for _ in range(BOOT):
        pieces=[]
        for b in BAYS:
            g=by[b]
            if len(g)==0:
                pieces=[]
                break
            idx=rng.integers(0,len(g),size=len(g))
            pieces.append(g.iloc[idx])
        if not pieces:
            continue
        x=pd.concat(pieces,ignore_index=True)
        v=float(x["paired_difference"].mean())
        if np.isfinite(v):
            vals.append(v)
    return np.asarray(vals,float)

def adjusted_state_coef(d:pd.DataFrame)->float|None:
    x=d.copy()
    nodes=pd.Categorical(x["node_id"].astype(str))
    nd=pd.get_dummies(nodes,drop_first=True,dtype=float)
    state=(x["functional_state"]=="loss_legacy_alternative").astype(float).to_numpy()
    X=np.column_stack([
        np.ones(len(x)),
        state,
        x["total_vegetated_cover"].to_numpy(float),
        x["canopy_height"].to_numpy(float),
        nd.to_numpy(float),
    ])
    y=x["attenuation_p90"].to_numpy(float)
    if np.linalg.matrix_rank(X)<X.shape[1]:
        return None
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return float(beta[1])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    d=prepare(pd.read_csv(a.input))
    p=pair_table(d) if len(d) else pd.DataFrame()
    counts={b:int((p["water_body"]==b).sum()) if len(p) else 0 for b in BAYS}
    n=int(len(p))
    gate=bool(n>=MIN_PAIRS and all(counts[b]>=MIN_PER_BAY for b in BAYS))

    result={
        "schema":"tampa.functional_insurance_loss_legacy_primary_v1",
        "analysis_frozen":True,
        "contract":"results/functional_insurance_loss_legacy_primary_v1_contract.json",
        "inferential_unit":"stable transect node / matched state pair",
        "confirmatory_geography":list(BAYS),
        "complete_pairs":n,
        "pairs_by_water_body":counts,
        "replication_gate":{
            "minimum_total":MIN_PAIRS,
            "minimum_per_bay":MIN_PER_BAY,
            "passed":gate,
        },
        "primary":{
            "estimand":"mean attenuation_p90(loss-legacy alternative) - attenuation_p90(persistent Thalassia)",
            "estimate":None,
            "ci95":None,
            "classification":"nonestimable" if n==0 else None,
        },
        "secondary_structure_adjusted":{
            "model":"attenuation_p90 ~ loss_legacy_alternative_indicator + total_vegetated_cover + canopy_height + node_fixed_effect",
            "state_coefficient":None,
            "role":"mechanism decomposition only; cannot replace or rescue the primary paired contrast",
        },
        "bootstrap":{
            "method":"Old/Middle-stratified stable-node paired bootstrap",
            "repetitions":BOOT,
            "seed":SEED,
            "valid_replicates":0,
        },
        "claim_boundary":[
            "An interval overlapping zero is unresolved and is not evidence of functional equivalence.",
            "If the replication gate fails, the estimate is pilot-only and an unresolved interval cannot support functional redundancy.",
            "The structure-adjusted secondary asks whether a primary physical difference remains beyond present cover and canopy height; it cannot rescue a null primary.",
            "Use canopy ecosystem-engineering language only if the separately frozen bare-bed physical-attribution gate passes.",
        ],
    }

    if n:
        est=float(p["paired_difference"].mean())
        boots=paired_bootstrap(p)
        result["primary"]["estimate"]=est
        result["bootstrap"]["valid_replicates"]=int(len(boots))
        if len(boots)<int(.95*BOOT):
            result["primary"]["classification"]="nonestimable_bootstrap_failure"
        else:
            lo,hi=np.quantile(boots,[.025,.975])
            result["primary"]["ci95"]=[float(lo),float(hi)]
            if not gate:
                cls="pilot_only_replication_gate_failed"
            elif hi<0:
                cls="resolved_lower_function_after_turnover"
            elif lo>0:
                cls="resolved_higher_attenuation_after_turnover"
            else:
                cls="unresolved_difference"
            result["primary"]["classification"]=cls
        result["secondary_structure_adjusted"]["state_coefficient"]=adjusted_state_coef(d)

    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
