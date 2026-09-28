#!/usr/bin/env python3
"""Bare-state subgroup audit of the pre-loss exact-point Thalassia legacy signal.

Frozen design: results/preloss_legacy_bare_audit_v1_contract.json

The primary population is restricted to the already-defined three-year recovery
sequences whose focal-loss year became completely seagrass-bare. This removes
immediate alternative-seagrass continuity from the tested pathway.
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
C=json.loads((ROOT/"results/preloss_legacy_bare_audit_v1_contract.json").read_text())
P=C["primary_population"]
BOOT=int(C["uncertainty"]["bootstrap_replicates"])
SEED=int(C["uncertainty"]["random_seed"])

CAT=["node_id"]
NUM=["loss_year","source_mixed","pre_loss_run_length_centered"]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_bare_history(py:pd.DataFrame, seq:pd.DataFrame)->pd.DataFrame:
    required_py={
        "point_id","node_id","year","thalassia_present","alternative_species"
    }
    required_seq={
        "point_id","node_id","source_year","loss_year","recovery_year",
        "intermediate_state","thalassia_return"
    }
    if m:=required_py.difference(py.columns):
        raise RuntimeError(f"point-year columns missing: {sorted(m)}")
    if m:=required_seq.difference(seq.columns):
        raise RuntimeError(f"recovery columns missing: {sorted(m)}")

    history={}
    for point,g in py.groupby("point_id",sort=False):
        history[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    rows=[]
    bare=seq[seq["intermediate_state"].astype(str)=="no_seagrass"].copy()
    for r in bare.itertuples(index=False):
        point=str(r.point_id)
        source=int(r.source_year)
        h=history.get(point,{})
        if source not in h:
            raise RuntimeError(f"source point-year missing: {point} {source}")
        src=h[source]
        if not bool(src.thalassia_present):
            raise RuntimeError(f"source not Thalassia-positive: {point} {source}")

        run=0
        y=source
        while y in h and bool(h[y].thalassia_present):
            run+=1
            y-=1

        rows.append({
            "point_id":point,
            "node_id":str(r.node_id),
            "source_year":source,
            "loss_year":int(r.loss_year),
            "recovery_year":int(r.recovery_year),
            "thalassia_return":int(r.thalassia_return),
            "source_mixed":int(bool(species_set(src.alternative_species))),
            "pre_loss_run_length":int(run),
        })

    d=pd.DataFrame(rows)
    if len(d):
        means=d.groupby("node_id")["pre_loss_run_length"].transform("mean")
        d["pre_loss_run_length_centered"]=d["pre_loss_run_length"].astype(float)-means.astype(float)
    return d


def make_model():
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),NUM),
    ])
    return make_pipeline(
        pre,
        LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000)
    )


def fit_coef(d:pd.DataFrame)->float:
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("one-class target")
    if np.isclose(d["pre_loss_run_length_centered"].std(ddof=0),0):
        raise RuntimeError("no centered run-length variation")
    m=make_model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["thalassia_return"].astype(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    target="num__pre_loss_run_length_centered"
    idx=np.where(names==target)[0]
    if len(idx)!=1:
        raise RuntimeError(f"legacy coefficient missing from features: {names}")
    return float(m.named_steps["logisticregression"].coef_[0][int(idx[0])])


def fit_uncentered(d:pd.DataFrame)->float|None:
    if len(d)==0:
        return None
    z=d.copy()
    z["pre_loss_run_length_centered"]=z["pre_loss_run_length"].astype(float)
    try:
        return fit_coef(z)
    except Exception:
        return None


def estimable(d:pd.DataFrame)->tuple[bool,dict]:
    nodes=int(d["node_id"].nunique()) if len(d) else 0
    returns=int(d["thalassia_return"].sum()) if len(d) else 0
    nonreturns=int(len(d)-returns)
    varying=int((d.groupby("node_id")["pre_loss_run_length"].nunique()>1).sum()) if len(d) else 0
    ok=bool(
        len(d)>=int(P["minimum_sequences"])
        and nodes>=int(P["minimum_nodes"])
        and returns>=int(P["minimum_return_events"])
        and nonreturns>=int(P["minimum_nonreturn_events"])
        and varying>=int(P["minimum_nodes_with_run_length_variation"])
    )
    return ok,{
        "bare_sequences":int(len(d)),
        "nodes":nodes,
        "return_events":returns,
        "nonreturn_events":nonreturns,
        "nodes_with_run_length_variation":varying,
    }


def bootstrap(d:pd.DataFrame)->tuple[np.ndarray,int]:
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*40
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        pieces=[]
        for j,n in enumerate(chosen):
            x=by[n].copy()
            x["node_id"]=f"boot_{j}_{n}"
            pieces.append(x)
        z=pd.concat(pieces,ignore_index=True)
        try:
            vals.append(fit_coef(z))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"insufficient valid bootstrap fits: {len(vals)} from {attempts}")
    return np.asarray(vals,float),attempts


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    if len(seq)!=259:
        raise RuntimeError(f"recovery sequence registry drift: {len(seq)}")

    d=build_bare_history(py,seq)
    ok,registry=estimable(d)
    result={
        "schema":"tampa.preloss_legacy_bare_audit_v1.result",
        "status":"non_estimable" if not ok else None,
        "contract":"results/preloss_legacy_bare_audit_v1_contract.json",
        "registry":registry,
        "primary":{
            "standardized_centered_run_length_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "return_run_length_median":(
                float(d.loc[d["thalassia_return"]==1,"pre_loss_run_length"].median())
                if (d["thalassia_return"]==1).any() else None
            ),
            "nonreturn_run_length_median":(
                float(d.loc[d["thalassia_return"]==0,"pre_loss_run_length"].median())
                if (d["thalassia_return"]==0).any() else None
            ),
            "uncentered_run_length_coefficient":None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if ok:
        point=fit_coef(d)
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="bare_state_legacy_supported" if supported else "bare_state_legacy_not_supported"
        result["primary"]={
            "standardized_centered_run_length_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]["uncentered_run_length_coefficient"]=fit_uncentered(d)
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen bare-state sequence/outcome/node-variation minima were not met."

    d.to_csv(outdir/"preloss_legacy_bare_sequences.csv",index=False)
    (outdir/"preloss_legacy_bare_audit_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_bare_legacy"))
    p.add_argument("--out",type=Path,default=Path("results/generated_bare_legacy"))
    a=p.parse_args()
    main(a.input,a.out)
