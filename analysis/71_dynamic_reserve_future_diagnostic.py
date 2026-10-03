#!/usr/bin/env python3
"""Frozen secondary diagnostic: recent reserve trajectory -> future meadow change.

Input is node-level, one row per stable core-three node.
This analysis is secondary and cannot rescue the authoritative four-bay static TNC primary.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
MIN_TOTAL=30
MIN_PER_BAY=8
BOOT=10000
SEED=20261006
MIN_INTERVAL=39
MAX_INTERVAL=45

REQ={
 "node_id","water_body","tnc_pre","tnc_post","pre_tnc_date","post_tnc_date",
 "baseline_frequency_post","future_frequency"
}

def design(df:pd.DataFrame):
    y=(df["future_frequency"]-df["baseline_frequency_post"]).to_numpy(float)
    delta=(df["tnc_post"]-df["tnc_pre"]).to_numpy(float)
    cols=[
      np.ones(len(df)),
      df["baseline_frequency_post"].to_numpy(float),
      df["tnc_post"].to_numpy(float),
      delta,
    ]
    for b in BAYS[1:]:
        cols.append((df["water_body"].astype(str)==b).astype(float).to_numpy())
    X=np.column_stack(cols)
    return X,y,3  # focal delta-TNC column

def fit(df):
    X,y,k=design(df)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return float(beta[k])

def stratified_bootstrap(df):
    rng=np.random.default_rng(SEED)
    groups={b:df[df["water_body"]==b].reset_index(drop=True) for b in BAYS}
    vals=[]
    for _ in range(BOOT):
        parts=[]
        for b,g in groups.items():
            ix=rng.integers(0,len(g),size=len(g))
            parts.append(g.iloc[ix].copy())
        z=pd.concat(parts,ignore_index=True)
        try:
            v=fit(z)
            if np.isfinite(v): vals.append(v)
        except np.linalg.LinAlgError:
            pass
    return np.asarray(vals,float)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    df=pd.read_csv(a.input)
    miss=REQ-set(df.columns)
    if miss: raise SystemExit(f"missing columns: {sorted(miss)}")
    forbidden=[c for c in df.columns if c.lower() in {"binary_reappearance","recovery"}]
    if forbidden: raise SystemExit(f"prohibited outcome columns: {forbidden}")

    df=df.copy()
    df["pre_tnc_date"]=pd.to_datetime(df["pre_tnc_date"],errors="coerce")
    df["post_tnc_date"]=pd.to_datetime(df["post_tnc_date"],errors="coerce")
    df["interval_days"]=(df["post_tnc_date"]-df["pre_tnc_date"]).dt.days
    for c in ["tnc_pre","tnc_post","baseline_frequency_post","future_frequency"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")

    valid=(
      df["water_body"].isin(BAYS)
      & df["node_id"].notna()
      & df["interval_days"].between(MIN_INTERVAL,MAX_INTERVAL,inclusive="both")
      & df[["tnc_pre","tnc_post","baseline_frequency_post","future_frequency"]].notna().all(axis=1)
    )
    d=df.loc[valid].copy()
    if d["node_id"].duplicated().any():
        raise SystemExit("duplicate node_id in analytic input")

    counts=d.groupby("water_body")["node_id"].nunique().reindex(BAYS,fill_value=0).astype(int)
    gate=(len(d)>=MIN_TOTAL and bool((counts>=MIN_PER_BAY).all()))
    result={
      "schema":"tampa.dynamic_reserve_future_diagnostic_v1",
      "status":"NONESTIMABLE_REPLICATION_GATE" if not gate else None,
      "secondary":True,
      "model":"future_delta_frequency ~ baseline_frequency_post + tnc_post + delta_tnc_42d + water_body",
      "focal_coefficient":"delta_tnc_42d",
      "delta_definition":"tnc_post - tnc_pre",
      "eligible_nodes":int(len(d)),
      "nodes_by_water_body":{b:int(counts[b]) for b in BAYS},
      "temporal_pairing_days":[MIN_INTERVAL,MAX_INTERVAL],
      "bootstrap":{"method":"water-body-stratified stable-node bootstrap","repetitions":BOOT,"seed":SEED},
      "estimate":None,"ci95":None,
      "classification":"nonestimable" if not gate else None,
      "claim_boundary":[
        "Secondary temporal site-template-resistant diagnostic; cannot replace or rescue the authoritative four-bay static TNC primary.",
        "Support weakens a purely time-invariant node-quality explanation but does not remove time-varying common causes or TNC measurement error.",
        "Binary reappearance is not an outcome."
      ]
    }
    if gate:
        est=fit(d)
        boots=stratified_bootstrap(d)
        if len(boots)<0.95*BOOT:
            result["status"]="NONESTIMABLE_BOOTSTRAP_FAILURE"
            result["classification"]="nonestimable"
            result["bootstrap"]["valid_replicates"]=int(len(boots))
        else:
            lo,hi=np.quantile(boots,[0.025,0.975])
            cls="supported" if lo>0 else "contradicted_direction" if hi<0 else "unsupported"
            result.update({
              "status":"ESTIMATED",
              "estimate":est,
              "ci95":[float(lo),float(hi)],
              "classification":cls,
            })
            result["bootstrap"]["valid_replicates"]=int(len(boots))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
