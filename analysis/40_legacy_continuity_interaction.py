#!/usr/bin/env python3
"""Test interaction between pre-loss focal history and loss-year community continuity.

Frozen design: results/legacy_continuity_interaction_v1_contract.json
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
C=json.loads((ROOT/"results/legacy_continuity_interaction_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])

CAT=["node_id"]
NUM=["loss_year","source_mixed","loss_year_vegetated","pre_loss_run_length_centered","legacy_x_continuity"]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_frame(py:pd.DataFrame, seq:pd.DataFrame)->pd.DataFrame:
    by_point={}
    for point,g in py.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    rows=[]
    for r in seq.itertuples(index=False):
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
            "loss_year_vegetated":int(str(r.intermediate_state)=="other_seagrass"),
            "pre_loss_run_length":int(run),
            "thalassia_return":int(r.thalassia_return),
        })

    d=pd.DataFrame(rows)
    d["pre_loss_run_length_centered"]=(
        d["pre_loss_run_length"]-
        d.groupby("node_id")["pre_loss_run_length"].transform("mean")
    )
    d["legacy_x_continuity"]=d["pre_loss_run_length_centered"]*d["loss_year_vegetated"]
    return d


def make_model(num_cols):
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),num_cols),
    ])
    clf=LogisticRegression(
        C=float(C["model"]["logistic_C"]),
        solver=str(C["model"]["solver"]),
        max_iter=int(C["model"]["max_iter"]),
    )
    return make_pipeline(pre,clf)


def fit_coef(d:pd.DataFrame,num_cols,target_name:str)->float:
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("single outcome class")
    m=make_model(num_cols)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+num_cols],d["thalassia_return"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    target="num__"+target_name
    idx=np.where(names==target)[0]
    if len(idx)!=1:
        raise RuntimeError(f"coefficient not found: {target}")
    return float(coef[int(idx[0])])


def bootstrap(d:pd.DataFrame):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*10
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by[n] for n in chosen],ignore_index=True)
        if b["thalassia_return"].nunique()<2 or b["loss_year_vegetated"].nunique()<2:
            continue
        try:
            vals.append(fit_coef(b,NUM,"legacy_x_continuity"))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstrap fits from {attempts}")
    return np.asarray(vals,float),attempts


def subset_history_coef(d:pd.DataFrame,vegetated:int):
    x=d[d["loss_year_vegetated"]==vegetated].copy()
    if len(x)<10 or x["thalassia_return"].nunique()<2:
        return None
    cols=["loss_year","source_mixed","pre_loss_run_length_centered"]
    try:
        return fit_coef(x,cols,"pre_loss_run_length_centered")
    except Exception:
        return None


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    if len(seq)!=259:
        raise RuntimeError(f"recovery sequence registry drift: {len(seq)}")

    d=build_frame(py,seq)
    nodes=int(d["node_id"].nunique())
    veg=int(d["loss_year_vegetated"].sum())
    bare=int(len(d)-veg)
    both=int((d.groupby("node_id")["loss_year_vegetated"].nunique()>=2).sum())

    estimable=bool(
        len(d)>=int(H["minimum_sequences"])
        and nodes>=int(H["minimum_nodes"])
        and veg>=int(H["minimum_vegetated_sequences"])
        and bare>=int(H["minimum_bare_sequences"])
        and both>=int(H["minimum_nodes_with_both_loss_states"])
    )

    result={
        "schema":"tampa.legacy_continuity_interaction_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/legacy_continuity_interaction_v1_contract.json",
        "registry":{
            "recovery_sequences":int(len(d)),
            "nodes":nodes,
            "vegetated_loss_sequences":veg,
            "bare_loss_sequences":bare,
            "nodes_with_both_loss_states":both,
        },
        "primary":{
            "interaction_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "vegetated_only_history_coefficient":subset_history_coef(d,1),
            "bare_only_history_coefficient":subset_history_coef(d,0),
            "vegetated_return_fraction":float(d.loc[d["loss_year_vegetated"]==1,"thalassia_return"].mean()),
            "bare_return_fraction":float(d.loc[d["loss_year_vegetated"]==0,"thalassia_return"].mean()),
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        point=fit_coef(d,NUM,"legacy_x_continuity")
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="legacy_continuity_interaction_supported" if supported else "legacy_continuity_interaction_not_supported"
        result["primary"]={
            "interaction_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen sequence/state/node minima were not met."

    d.to_csv(outdir/"legacy_continuity_interaction_sequences.csv",index=False)
    (outdir/"legacy_continuity_interaction_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_legacy_continuity"))
    p.add_argument("--out",type=Path,default=Path("results/generated_legacy_continuity"))
    a=p.parse_args(); main(a.input,a.out)
