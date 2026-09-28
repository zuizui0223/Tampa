#!/usr/bin/env python3
"""Test pre-loss local legacy among exact points that become seagrass-bare.

Frozen design: results/bare_loss_local_legacy_v1_contract.json
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/bare_loss_local_legacy_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
MIN_SEQ=int(H["minimum_sequences"])
MIN_NODES=int(H["minimum_nodes"])
MIN_VAR=int(H["minimum_nodes_with_run_length_variation"])
MIN_RETURN=int(H["minimum_returns"])
MIN_NONRETURN=int(H["minimum_nonreturns"])

CAT=["node_id"]
NUM=["loss_year","source_mixed","pre_loss_run_length_centered"]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_frame(py:pd.DataFrame, seq:pd.DataFrame)->pd.DataFrame:
    by_point={}
    for point,g in py.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    bare=seq[seq["intermediate_state"]=="no_seagrass"].copy()
    rows=[]
    for r in bare.itertuples(index=False):
        point=str(r.point_id)
        source=int(r.source_year)
        hist=by_point.get(point,{})
        if source not in hist:
            raise RuntimeError(f"source point-year missing: {point} {source}")
        src=hist[source]
        if not bool(src.thalassia_present):
            raise RuntimeError(f"source not Thalassia-positive: {point} {source}")
        run=0
        y=source
        while y in hist and bool(hist[y].thalassia_present):
            run+=1
            y-=1
        rows.append({
            "point_id":point,
            "node_id":str(r.node_id),
            "source_year":source,
            "loss_year":int(r.loss_year),
            "recovery_year":int(r.recovery_year),
            "source_mixed":int(bool(species_set(src.alternative_species))),
            "pre_loss_run_length":int(run),
            "thalassia_return":int(r.thalassia_return),
        })
    d=pd.DataFrame(rows)
    if len(d):
        d["pre_loss_run_length_centered"]=(
            d["pre_loss_run_length"]-
            d.groupby("node_id")["pre_loss_run_length"].transform("mean")
        )
    return d


def model():
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),NUM),
    ])
    clf=LogisticRegression(
        C=float(H["logistic_C"]),
        solver=str(H["solver"]),
        max_iter=int(H["max_iter"]),
    )
    return make_pipeline(pre,clf)


def fit_coef(d:pd.DataFrame)->float:
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("single outcome class")
    m=model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["thalassia_return"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    target="num__pre_loss_run_length_centered"
    idx=np.where(names==target)[0]
    if len(idx)!=1:
        raise RuntimeError(f"legacy coefficient missing: {names}")
    return float(coef[int(idx[0])])


def bootstrap(d:pd.DataFrame):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*20
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by[n] for n in chosen],ignore_index=True)
        if b["thalassia_return"].nunique()<2:
            continue
        try:
            vals.append(fit_coef(b))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstraps from {attempts}")
    return np.asarray(vals,float),attempts


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    if len(seq)!=259:
        raise RuntimeError(f"recovery sequence registry drift: {len(seq)}")

    d=build_frame(py,seq)
    nodes=int(d["node_id"].nunique()) if len(d) else 0
    varying=int((d.groupby("node_id")["pre_loss_run_length"].nunique()>1).sum()) if len(d) else 0
    returns=int(d["thalassia_return"].sum()) if len(d) else 0
    nonreturns=int(len(d)-returns)

    estimable=bool(
        len(d)>=MIN_SEQ and nodes>=MIN_NODES and varying>=MIN_VAR
        and returns>=MIN_RETURN and nonreturns>=MIN_NONRETURN
    )

    result={
        "schema":"tampa.bare_loss_local_legacy_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/bare_loss_local_legacy_v1_contract.json",
        "registry":{
            "bare_loss_sequences":int(len(d)),
            "nodes":nodes,
            "nodes_with_run_length_variation":varying,
            "returns":returns,
            "nonreturns":nonreturns,
            "run_length_min":int(d["pre_loss_run_length"].min()) if len(d) else None,
            "run_length_median":float(d["pre_loss_run_length"].median()) if len(d) else None,
            "run_length_max":int(d["pre_loss_run_length"].max()) if len(d) else None,
        },
        "primary":{
            "centered_run_length_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "return_run_length_median":float(d.loc[d["thalassia_return"]==1,"pre_loss_run_length"].median()) if returns else None,
            "nonreturn_run_length_median":float(d.loc[d["thalassia_return"]==0,"pre_loss_run_length"].median()) if nonreturns else None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        point=fit_coef(d)
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="bare_loss_local_legacy_supported" if supported else "bare_loss_local_legacy_not_supported"
        result["primary"]={
            "centered_run_length_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen bare-state sequence/node/outcome-class minima were not met."

    d.to_csv(outdir/"bare_loss_local_legacy_sequences.csv",index=False)
    (outdir/"bare_loss_local_legacy_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_bare_loss_legacy"))
    p.add_argument("--out",type=Path,default=Path("results/generated_bare_loss_legacy"))
    a=p.parse_args()
    main(a.input,a.out)
