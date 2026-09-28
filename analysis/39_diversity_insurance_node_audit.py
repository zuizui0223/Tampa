#!/usr/bin/env python3
"""Within-node audit of the exact-point seagrass diversity-insurance gradient.

Frozen design: results/diversity_insurance_node_audit_v1_contract.json

Consumes the exact same Thalassia-loss transition population produced by
analysis/34_community_insurance.py. The primary predictor is alternative-seagrass
richness centered within stable transect node, and node_id is included as a fixed
categorical reference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/diversity_insurance_node_audit_v1_contract.json").read_text())
BOOT=int(C["uncertainty"]["bootstrap_replicates"])
SEED=int(C["uncertainty"]["random_seed"])
MIN_NODES=int(C["primary_population"]["minimum_informative_nodes"])
MIN_TRANS=int(C["primary_population"]["minimum_transitions"])


def richness(x)->int:
    if pd.isna(x):
        return 0
    return len({v for v in str(x).split(";") if v and v!="nan"})


def prepare(trans:pd.DataFrame):
    required={
        "node_id","target_year","source_alternative_species",
        "target_any_seagrass_present"
    }
    missing=required.difference(trans.columns)
    if missing:
        raise RuntimeError(f"missing transition columns: {sorted(missing)}")
    d=trans.copy()
    d["source_alternative_richness"]=d["source_alternative_species"].fillna("").map(richness).astype(int)
    d["target_any_seagrass_present"]=d["target_any_seagrass_present"].astype(bool)
    variation=d.groupby("node_id")["source_alternative_richness"].nunique()
    informative=sorted(variation[variation>=2].index.astype(str).tolist())
    d["node_id"]=d["node_id"].astype(str)
    d=d[d["node_id"].isin(informative)].copy()
    means=d.groupby("node_id")["source_alternative_richness"].transform("mean")
    d["within_node_centered_richness"]=d["source_alternative_richness"].astype(float)-means.astype(float)
    return d,informative,variation


def make_model():
    numeric=["target_year","within_node_centered_richness"]
    categorical=["node_id"]
    pre=ColumnTransformer([
        ("num",StandardScaler(),numeric),
        ("cat",OneHotEncoder(handle_unknown="ignore"),categorical),
    ])
    return make_pipeline(
        pre,
        LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000)
    )


def fit_centered_coef(d:pd.DataFrame)->float:
    if d["target_any_seagrass_present"].nunique()<2:
        raise RuntimeError("one-class target")
    if np.isclose(d["within_node_centered_richness"].std(ddof=0),0):
        raise RuntimeError("no centered-richness variation")
    m=make_model()
    cols=["target_year","within_node_centered_richness","node_id"]
    m.fit(d[cols],d["target_any_seagrass_present"].astype(int))
    # ColumnTransformer emits numeric columns first: target_year, centered richness.
    return float(m.named_steps["logisticregression"].coef_[0][1])


def fit_uncentered_orientation(d:pd.DataFrame)->float|None:
    z=d.copy()
    if z["target_any_seagrass_present"].nunique()<2 or z["source_alternative_richness"].nunique()<2:
        return None
    pre=ColumnTransformer([
        ("num",StandardScaler(),["target_year","source_alternative_richness"]),
        ("cat",OneHotEncoder(handle_unknown="ignore"),["node_id"]),
    ])
    m=make_pipeline(pre,LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000))
    m.fit(z[["target_year","source_alternative_richness","node_id"]],
          z["target_any_seagrass_present"].astype(int))
    return float(m.named_steps["logisticregression"].coef_[0][1])


def bootstrap(d:pd.DataFrame,informative:list[str]):
    estimable=bool(
        len(informative)>=MIN_NODES
        and len(d)>=MIN_TRANS
        and d["target_any_seagrass_present"].nunique()>=2
        and d["within_node_centered_richness"].nunique()>=2
    )
    out={
        "informative_nodes":int(len(informative)),
        "transitions":int(len(d)),
        "standardized_centered_richness_log_odds_coefficient":None,
        "ci95":None,
        "bootstrap_replicates_used":0,
        "estimable":estimable,
        "supported":False,
    }
    if not estimable:
        return out

    full=fit_centered_coef(d)
    by={n:d[d["node_id"]==n] for n in informative}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*30
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(informative,size=len(informative),replace=True)
        # Re-label duplicated sampled clusters so bootstrap copies get independent
        # node fixed effects while preserving all within-node rows.
        pieces=[]
        for j,n in enumerate(chosen):
            x=by[n].copy()
            x["node_id"]=f"boot_{j}_{n}"
            pieces.append(x)
        z=pd.concat(pieces,ignore_index=True)
        if z["target_any_seagrass_present"].nunique()<2:
            continue
        try:
            vals.append(fit_centered_coef(z))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"insufficient valid bootstrap fits: {len(vals)}")
    arr=np.asarray(vals,float)
    ci=np.quantile(arr,[.025,.975])
    out.update({
        "standardized_centered_richness_log_odds_coefficient":float(full),
        "ci95":[float(ci[0]),float(ci[1])],
        "bootstrap_replicates_used":int(len(arr)),
        "bootstrap_attempts":int(attempts),
        "supported":bool(ci[0]>0),
    })
    return out


def descriptives(d:pd.DataFrame):
    rows=[]
    for n,g in d.groupby("node_id",sort=True):
        rows.append({
            "node_id":n,
            "transitions":int(len(g)),
            "raw_richness_levels":int(g["source_alternative_richness"].nunique()),
            "raw_richness_min":int(g["source_alternative_richness"].min()),
            "raw_richness_max":int(g["source_alternative_richness"].max()),
            "centered_richness_sd":float(g["within_node_centered_richness"].std(ddof=0)),
            "target_occupancy_fraction":float(g["target_any_seagrass_present"].mean()),
        })
    return pd.DataFrame(rows)


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    trans=pd.read_csv(input_dir/"community_insurance_transitions.csv")
    if len(trans)!=370:
        raise RuntimeError(f"community-insurance transition registry drift: {len(trans)}")

    d,informative,variation=prepare(trans)
    primary=bootstrap(d,informative)
    node_desc=descriptives(d)
    orientation=fit_uncentered_orientation(d) if len(d) else None

    result={
        "schema":"tampa.diversity_insurance_node_audit_v1.result",
        "status":(
            "within_node_diversity_insurance_supported"
            if primary.get("supported",False)
            else "within_node_diversity_insurance_not_supported"
            if primary.get("estimable",False)
            else "non_estimable"
        ),
        "contract":"results/diversity_insurance_node_audit_v1_contract.json",
        "registry":{
            "all_transitions":int(len(trans)),
            "all_nodes":int(trans["node_id"].nunique()),
            "informative_nodes":int(len(informative)),
            "informative_transitions":int(len(d)),
            "observed_raw_richness_values":sorted(int(v) for v in trans["source_alternative_species"].fillna("").map(richness).unique()),
        },
        "primary":primary,
        "secondary":{
            "median_centered_richness_sd":float(node_desc["centered_richness_sd"].median()) if len(node_desc) else None,
            "uncentered_with_node_effect_orientation_coefficient":orientation,
        },
        "interpretation":(
            C["interpretation"]["supported"]
            if primary.get("supported",False)
            else C["interpretation"]["unsupported"]
        ),
        "claim_boundary":C["claim_boundary"],
    }

    d.to_csv(outdir/"diversity_insurance_node_audit_transitions.csv",index=False)
    node_desc.to_csv(outdir/"diversity_insurance_node_audit_nodes.csv",index=False)
    (outdir/"diversity_insurance_node_audit_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_diversity_node_audit"))
    p.add_argument("--out",type=Path,default=Path("results/generated_diversity_node_audit"))
    a=p.parse_args()
    main(a.input,a.out)
