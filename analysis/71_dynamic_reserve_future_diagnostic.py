#!/usr/bin/env python3
"""Frozen secondary diagnostic: paired-anchor reserve trajectory -> future meadow change.

Input is anchor-level, exactly one row per frozen q25/q50/q75 anchor.
The node-level trajectory is the median of matched anchor-specific changes:
    delta_tnc_42d = median_j(tnc_post_j - tnc_pre_j)
This prevents spatial differences among anchor neighborhoods from being silently
relabelled as temporal reserve change.

Secondary only: cannot replace or rescue the authoritative four-bay static TNC primary.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
MIN_TOTAL=30
MIN_PER_BAY=8
ANCHORS_PER_NODE=3
BOOT=10000
SEED=20261006
MIN_INTERVAL=39
MAX_INTERVAL=45

REQ={
 "node_id","water_body","anchor_id",
 "tnc_pre_anchor","tnc_post_anchor","pre_tnc_date","post_tnc_date",
 "baseline_frequency_post","future_frequency",
 "pre_anchor_tnc_qc_pass","post_anchor_tnc_qc_pass"
}

def _boolify(s):
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().map({"true":True,"false":False,"1":True,"0":False})

def prepare(anchor_df:pd.DataFrame):
    z=anchor_df.copy()
    z["pre_tnc_date"]=pd.to_datetime(z["pre_tnc_date"],errors="coerce")
    z["post_tnc_date"]=pd.to_datetime(z["post_tnc_date"],errors="coerce")
    z["interval_days"]=(z["post_tnc_date"]-z["pre_tnc_date"]).dt.days
    for c in ["tnc_pre_anchor","tnc_post_anchor","baseline_frequency_post","future_frequency"]:
        z[c]=pd.to_numeric(z[c],errors="coerce")
    z["pre_anchor_tnc_qc_pass"]=_boolify(z["pre_anchor_tnc_qc_pass"])
    z["post_anchor_tnc_qc_pass"]=_boolify(z["post_anchor_tnc_qc_pass"])

    z=z[
      z["water_body"].isin(BAYS)
      & z["node_id"].notna()
      & z["anchor_id"].notna()
      & z["interval_days"].between(MIN_INTERVAL,MAX_INTERVAL,inclusive="both")
      & (z["pre_anchor_tnc_qc_pass"]==True)
      & (z["post_anchor_tnc_qc_pass"]==True)
      & z[["tnc_pre_anchor","tnc_post_anchor","baseline_frequency_post","future_frequency"]].notna().all(axis=1)
    ].copy()

    node_rows=[]
    for node,g in z.groupby("node_id",sort=False):
        if g["water_body"].nunique()!=1:
            continue
        if len(g)!=ANCHORS_PER_NODE or g["anchor_id"].nunique()!=ANCHORS_PER_NODE:
            continue
        # The repeated node-level outcome/context values must actually be identical.
        if g["baseline_frequency_post"].nunique()!=1 or g["future_frequency"].nunique()!=1:
            continue
        if g["pre_tnc_date"].nunique()!=1 or g["post_tnc_date"].nunique()!=1:
            continue

        paired_delta=(g["tnc_post_anchor"]-g["tnc_pre_anchor"]).to_numpy(float)
        pre=g["tnc_pre_anchor"].to_numpy(float)
        post=g["tnc_post_anchor"].to_numpy(float)
        node_rows.append({
          "node_id":str(node),
          "water_body":str(g["water_body"].iloc[0]),
          "tnc_pre":float(np.median(pre)),
          "tnc_post":float(np.median(post)),
          "delta_tnc_42d":float(np.median(paired_delta)),
          "paired_anchor_delta_min":float(np.min(paired_delta)),
          "paired_anchor_delta_max":float(np.max(paired_delta)),
          "paired_anchor_delta_sign_concordance":float(max(
              np.mean(paired_delta>0),np.mean(paired_delta<0),np.mean(paired_delta==0)
          )),
          "pre_tnc_date":g["pre_tnc_date"].iloc[0],
          "post_tnc_date":g["post_tnc_date"].iloc[0],
          "interval_days":int(g["interval_days"].iloc[0]),
          "baseline_frequency_post":float(g["baseline_frequency_post"].iloc[0]),
          "future_frequency":float(g["future_frequency"].iloc[0]),
        })
    return pd.DataFrame(node_rows)

def design(df:pd.DataFrame):
    y=(df["future_frequency"]-df["baseline_frequency_post"]).to_numpy(float)
    cols=[
      np.ones(len(df)),
      df["baseline_frequency_post"].to_numpy(float),
      df["tnc_post"].to_numpy(float),
      df["delta_tnc_42d"].to_numpy(float),
    ]
    for b in BAYS[1:]:
        cols.append((df["water_body"].astype(str)==b).astype(float).to_numpy())
    X=np.column_stack(cols)
    return X,y,3

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
    raw=pd.read_csv(a.input)
    miss=REQ-set(raw.columns)
    if miss: raise SystemExit(f"missing columns: {sorted(miss)}")
    forbidden=[c for c in raw.columns if c.lower() in {"binary_reappearance","recovery"}]
    if forbidden: raise SystemExit(f"prohibited outcome columns: {forbidden}")

    d=prepare(raw)
    if d.empty:
        counts=pd.Series(0,index=BAYS,dtype=int)
    else:
        counts=d.groupby("water_body")["node_id"].nunique().reindex(BAYS,fill_value=0).astype(int)
    gate=(len(d)>=MIN_TOTAL and bool((counts>=MIN_PER_BAY).all()))

    result={
      "schema":"tampa.dynamic_reserve_future_diagnostic_v2_paired_anchor",
      "status":"NONESTIMABLE_REPLICATION_GATE" if not gate else None,
      "secondary":True,
      "model":"future_delta_frequency ~ baseline_frequency_post + tnc_post + paired_anchor_delta_tnc_42d + water_body",
      "focal_coefficient":"paired_anchor_delta_tnc_42d",
      "delta_definition":"node median of the three matched q25/q50/q75 anchor-specific changes (tnc_post_anchor - tnc_pre_anchor); not difference of independently summarized node medians",
      "current_state_definition":"tnc_post = median of the same three post-exposure anchor TNC values",
      "eligible_nodes":int(len(d)),
      "nodes_by_water_body":{b:int(counts[b]) for b in BAYS},
      "required_complete_paired_anchors_per_node":ANCHORS_PER_NODE,
      "temporal_pairing_days":[MIN_INTERVAL,MAX_INTERVAL],
      "anchor_change_diagnostic":{
        "sign_concordance_role":"descriptive measurement-heterogeneity diagnostic only; no post-hoc concordance threshold is used to select nodes",
        "median_sign_concordance":None if d.empty else float(d["paired_anchor_delta_sign_concordance"].median())
      },
      "bootstrap":{"method":"water-body-stratified stable-node bootstrap","repetitions":BOOT,"seed":SEED},
      "estimate":None,"ci95":None,
      "classification":"nonestimable" if not gate else None,
      "claim_boundary":[
        "Secondary temporal site-template-resistant diagnostic; cannot replace or rescue the authoritative four-bay static TNC primary.",
        "Paired q25/q50/q75 anchor changes reduce spatial-core confounding relative to subtracting independently summarized node medians.",
        "Support weakens a purely time-invariant node-quality explanation but does not remove time-varying common causes or residual TNC measurement error.",
        "Every retained anchor must pass authoritative TNC sample/assay QC in both rounds; failed anchors make the entire three-anchor node ineligible rather than being imputed or replaced after future outcome access.",
        "If assay batch is perfectly confounded with pre/post round at the study level, this diagnostic must be declared non-estimable upstream rather than interpreted as temporal reserve change.",
        "Because current tnc_post and paired change share post measurements, correlated measurement error can still affect the state-versus-trajectory coefficient; analytical/spatial precision diagnostics must remain visible.",
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
            result.update({"status":"ESTIMATED","estimate":est,"ci95":[float(lo),float(hi)],"classification":cls})
            result["bootstrap"]["valid_replicates"]=int(len(boots))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
