#!/usr/bin/env python3
"""Frozen secondary diagnostic: within-transect centered anchor TNC -> future same-mark BB.

Input has exactly one row per frozen anchor. Nodes enter only with three complete
quantitative anchors. Stable-node identity is absorbed by fixed effects and
uncertainty resamples whole nodes within water body.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
MIN_TOTAL=36
MIN_PER_BAY=6
ANCHORS_PER_NODE=3
BOOT=10000
SEED=20261007
REQ={"node_id","water_body","anchor_id","baseline_bb_anchor","anchor_tnc","future_bb_anchor","anchor_tnc_qc_pass"}

def prepare(df):
    z=df.copy()
    for c in ["baseline_bb_anchor","anchor_tnc","future_bb_anchor"]:
        z[c]=pd.to_numeric(z[c],errors="coerce")
    if z["anchor_tnc_qc_pass"].dtype != bool:
        z["anchor_tnc_qc_pass"]=z["anchor_tnc_qc_pass"].astype(str).str.lower().map({"true":True,"false":False,"1":True,"0":False})
    z=z[z["water_body"].isin(BAYS) & (z["anchor_tnc_qc_pass"]==True)].dropna(
        subset=["node_id","water_body","anchor_id","baseline_bb_anchor","anchor_tnc","future_bb_anchor"]
    ).copy()
    keep=[]
    for node,g in z.groupby("node_id",sort=False):
        if g["water_body"].nunique()!=1: continue
        if g["anchor_id"].nunique()!=ANCHORS_PER_NODE or len(g)!=ANCHORS_PER_NODE: continue
        keep.append(g)
    if not keep:
        return z.iloc[0:0].copy()
    z=pd.concat(keep,ignore_index=True)
    z["within_node_centered_anchor_TNC"]=z["anchor_tnc"]-z.groupby("node_id")["anchor_tnc"].transform("mean")
    return z

def design(df,node_col="node_id"):
    y=df["future_bb_anchor"].to_numpy(float)
    nodes=pd.Categorical(df[node_col].astype(str))
    dummies=pd.get_dummies(nodes,drop_first=True,dtype=float)
    X=np.column_stack([
      np.ones(len(df)),
      df["baseline_bb_anchor"].to_numpy(float),
      df["within_node_centered_anchor_TNC"].to_numpy(float),
      dummies.to_numpy(float)
    ])
    return X,y,2

def fit(df,node_col="node_id"):
    X,y,k=design(df,node_col)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return float(beta[k])

def cluster_bootstrap(df):
    rng=np.random.default_rng(SEED)
    node_meta=df[["node_id","water_body"]].drop_duplicates()
    by={b:node_meta[node_meta["water_body"]==b]["node_id"].tolist() for b in BAYS}
    vals=[]
    for rep in range(BOOT):
        pieces=[]; draw=0
        for b,nodes in by.items():
            chosen=rng.choice(nodes,size=len(nodes),replace=True)
            for node in chosen:
                g=df[df["node_id"]==node].copy()
                g["boot_node"]=f"{b}|{rep}|{draw}"
                pieces.append(g); draw+=1
        z=pd.concat(pieces,ignore_index=True)
        try:
            v=fit(z,"boot_node")
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
    d=prepare(df)
    meta=d[["node_id","water_body"]].drop_duplicates()
    counts=meta.groupby("water_body")["node_id"].nunique().reindex(BAYS,fill_value=0).astype(int)
    n=int(meta["node_id"].nunique())
    gate=(n>=MIN_TOTAL and bool((counts>=MIN_PER_BAY).all()))

    result={
      "schema":"tampa.within_transect_anchor_tnc_future_bb_v1",
      "status":"NONESTIMABLE_REPLICATION_GATE" if not gate else None,
      "secondary":True,
      "model":"future_BB_anchor ~ baseline_BB_anchor + within_node_centered_anchor_TNC + node_fixed_effect",
      "focal_coefficient":"within_node_centered_anchor_TNC",
      "eligible_nodes":n,
      "eligible_anchor_rows":int(len(d)),
      "nodes_by_water_body":{b:int(counts[b]) for b in BAYS},
      "required_complete_anchors_per_node":ANCHORS_PER_NODE,
      "bootstrap":{"method":"water-body-stratified stable-node cluster bootstrap","repetitions":BOOT,"seed":SEED},
      "estimate":None,"ci95":None,"ci97_5_family":None,
      "classification":"nonestimable" if not gate else None,
      "claim_boundary":[
        "Secondary spatial site-template-resistant diagnostic; cannot replace or rescue the authoritative four-bay node-level TNC primary.",
        "Node fixed effects remove stable transect-level differences, not persistent meter-mark microhabitat or time-varying local common causes.",
        "Braun-Blanquet is analyzed on the frozen quantitative score scale.",
        "Every retained anchor must pass the authoritative TNC sample/assay QC; failed anchor chemistry makes the entire three-anchor node ineligible rather than being imputed or replaced after future outcome access."
      ]
    }
    if gate:
        est=fit(d)
        boots=cluster_bootstrap(d)
        if len(boots)<0.95*BOOT:
            result["status"]="NONESTIMABLE_BOOTSTRAP_FAILURE"
            result["classification"]="nonestimable"
            result["bootstrap"]["valid_replicates"]=int(len(boots))
        else:
            lo,hi=np.quantile(boots,[0.025,0.975])
            flo,fhi=np.quantile(boots,[0.0125,0.9875])
            cls="supported" if lo>0 else "contradicted_direction" if hi<0 else "unsupported"
            fcls="supported" if flo>0 else "contradicted_direction" if fhi<0 else "unsupported"
            result.update({
              "status":"ESTIMATED","estimate":est,
              "ci95":[float(lo),float(hi)],"classification":cls,
              "ci97_5_family":[float(flo),float(fhi)],"family_classification":fcls
            })
            result["bootstrap"]["valid_replicates"]=int(len(boots))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
