#!/usr/bin/env python3
"""Pre-outcome local-depth sensitivity for the decisive Tampa anchor-TNC test.

Primary inference remains analysis/72_anchor_tnc_future_bb_diagnostic.py.

This sensitivity asks whether the within-node centered anchor-TNC coefficient
survives adjustment for contemporaneous same-meter water depth, a plausible
persistent meter-mark microhabitat confounder.

Required extra input:
    baseline_depth_m

Model:
    future_BB_anchor
      ~ baseline_BB_anchor
      + within_node_centered_anchor_TNC
      + within_node_centered_baseline_depth
      + node_fixed_effect

The sensitivity cannot rescue an unsupported primary result.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"analysis"/"72_anchor_tnc_future_bb_diagnostic.py"
spec=importlib.util.spec_from_file_location("anchor_primary",BASE)
m=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

REQ_EXTRA={"baseline_depth_m"}
BOOT=10000
SEED=20261010


def prepare_depth(df):
    miss=REQ_EXTRA-set(df.columns)
    if miss:
        raise SystemExit(f"missing depth-sensitivity columns: {sorted(miss)}")
    z=m.prepare(df)
    z["baseline_depth_m"]=pd.to_numeric(z["baseline_depth_m"],errors="coerce")
    keep=[]
    for node,g in z.groupby("node_id",sort=False):
        if len(g)!=m.ANCHORS_PER_NODE or g["anchor_id"].nunique()!=m.ANCHORS_PER_NODE:
            continue
        if g["baseline_depth_m"].notna().all():
            keep.append(g)
    if not keep:
        return z.iloc[0:0].copy()
    z=pd.concat(keep,ignore_index=True)
    z["within_node_centered_baseline_depth"]=(
        z["baseline_depth_m"]
        - z.groupby("node_id")["baseline_depth_m"].transform("mean")
    )
    return z


def design(df,node_col="node_id"):
    y=df["future_bb_anchor"].to_numpy(float)
    nodes=pd.Categorical(df[node_col].astype(str))
    dummies=pd.get_dummies(nodes,drop_first=True,dtype=float)
    X=np.column_stack([
        np.ones(len(df)),
        df["baseline_bb_anchor"].to_numpy(float),
        df["within_node_centered_anchor_TNC"].to_numpy(float),
        df["within_node_centered_baseline_depth"].to_numpy(float),
        dummies.to_numpy(float),
    ])
    return X,y,2,3


def fit(df,node_col="node_id"):
    X,y,k_tnc,k_depth=design(df,node_col)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return {
        "beta_tnc":float(beta[k_tnc]),
        "beta_depth":float(beta[k_depth]),
    }


def cluster_bootstrap(df):
    rng=np.random.default_rng(SEED)
    node_meta=df[["node_id","water_body"]].drop_duplicates()
    by={b:node_meta[node_meta["water_body"]==b]["node_id"].tolist() for b in m.BAYS}
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
            if np.isfinite(v["beta_tnc"]):
                vals.append(v["beta_tnc"])
        except np.linalg.LinAlgError:
            pass
    return np.asarray(vals,float)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    df=pd.read_csv(a.input)
    miss=m.REQ-set(df.columns)
    if miss:
        raise SystemExit(f"missing primary columns: {sorted(miss)}")
    d=prepare_depth(df)

    meta=d[["node_id","water_body"]].drop_duplicates()
    counts=meta.groupby("water_body")["node_id"].nunique().reindex(m.BAYS,fill_value=0).astype(int)
    n=int(meta["node_id"].nunique())
    gate=(n>=m.MIN_TOTAL and bool((counts>=m.MIN_PER_BAY).all()))

    result={
        "schema":"tampa.anchor_tnc_depth_sensitivity_v1",
        "status":"NONESTIMABLE_DEPTH_COVERAGE_GATE" if not gate else None,
        "primary":False,
        "inferential_role":"predeclared_local_microhabitat_confounder_sensitivity",
        "parent_primary":"analysis/72_anchor_tnc_future_bb_diagnostic.py",
        "contract":"results/clonal_state_anchor_depth_sensitivity_v1_contract.json",
        "model":"future_BB_anchor ~ baseline_BB_anchor + within_node_centered_anchor_TNC + within_node_centered_baseline_depth + node_fixed_effect",
        "focal_coefficient":"within_node_centered_anchor_TNC",
        "depth_coefficient":"within_node_centered_baseline_depth",
        "eligible_nodes":n,
        "eligible_anchor_rows":int(len(d)),
        "nodes_by_water_body":{b:int(counts[b]) for b in m.BAYS},
        "bootstrap":{"method":"water-body-stratified stable-node cluster bootstrap","repetitions":BOOT,"seed":SEED},
        "estimate_tnc":None,
        "estimate_depth":None,
        "ci95_tnc":None,
        "classification":"nonestimable" if not gate else None,
        "claim_boundary":[
            "This sensitivity cannot replace or rescue the decisive primary anchor-TNC result.",
            "Depth is measured contemporaneously at the same permanent meter mark as baseline quantitative state.",
            "Adjustment for depth reduces one persistent meter-mark microhabitat alternative but does not eliminate unmeasured substrate, light, hydrodynamic or time-varying common causes.",
            "If the depth coverage gate fails, report non-estimable; do not relax node or per-bay thresholds after future outcomes."
        ]
    }

    if gate:
        est=fit(d)
        boots=cluster_bootstrap(d)
        result["estimate_tnc"]=est["beta_tnc"]
        result["estimate_depth"]=est["beta_depth"]
        result["bootstrap"]["valid_replicates"]=int(len(boots))
        if len(boots)<0.95*BOOT:
            result["status"]="NONESTIMABLE_BOOTSTRAP_FAILURE"
            result["classification"]="nonestimable"
        else:
            lo,hi=np.quantile(boots,[0.025,0.975])
            result["ci95_tnc"]=[float(lo),float(hi)]
            result["status"]="ESTIMATED"
            result["classification"]="supported_after_depth_adjustment" if lo>0 else "contradicted_direction" if hi<0 else "unsupported_after_depth_adjustment"

    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
