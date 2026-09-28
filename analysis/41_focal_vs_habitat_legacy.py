#!/usr/bin/env python3
"""Decompose local history into focal Thalassia run and generic habitat headstart.

Frozen design: results/focal_vs_habitat_legacy_v1_contract.json
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
C=json.loads((ROOT/"results/focal_vs_habitat_legacy_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])

CAT=["node_id"]
NUM=[
    "loss_year","loss_year_vegetated","source_mixed",
    "thalassia_run_centered","habitat_headstart_centered"
]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def consecutive_run(hist:dict[int,object],source:int,field:str)->int:
    run=0
    y=source
    while y in hist and bool(getattr(hist[y],field)):
        run+=1
        y-=1
    return run


def build_frame(py:pd.DataFrame,seq:pd.DataFrame)->pd.DataFrame:
    by_point={}
    for point,g in py.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    rows=[]
    for r in seq.itertuples(index=False):
        point=str(r.point_id)
        source=int(r.source_year)
        hist=by_point.get(point,{})
        if source not in hist:
            raise RuntimeError(f"missing source point-year: {point} {source}")
        src=hist[source]
        if not bool(src.thalassia_present):
            raise RuntimeError(f"source not Thalassia positive: {point} {source}")
        th=consecutive_run(hist,source,"thalassia_present")
        anyrun=consecutive_run(hist,source,"any_seagrass_present")
        if anyrun<th:
            raise RuntimeError("any-seagrass run shorter than Thalassia run")
        head=anyrun-th
        rows.append({
            "point_id":point,
            "node_id":str(r.node_id),
            "source_year":source,
            "loss_year":int(r.loss_year),
            "recovery_year":int(r.recovery_year),
            "loss_year_vegetated":int(str(r.intermediate_state)=="other_seagrass"),
            "source_mixed":int(bool(species_set(src.alternative_species))),
            "thalassia_run":int(th),
            "any_seagrass_run":int(anyrun),
            "habitat_headstart":int(head),
            "thalassia_return":int(r.thalassia_return),
        })
    d=pd.DataFrame(rows)
    d["thalassia_run_centered"]=d["thalassia_run"]-d.groupby("node_id")["thalassia_run"].transform("mean")
    d["habitat_headstart_centered"]=d["habitat_headstart"]-d.groupby("node_id")["habitat_headstart"].transform("mean")
    return d


def make_model():
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


def fit_coefs(d:pd.DataFrame)->tuple[float,float]:
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("single outcome class")
    m=make_model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["thalassia_return"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    out=[]
    for target in ["num__thalassia_run_centered","num__habitat_headstart_centered"]:
        idx=np.where(names==target)[0]
        if len(idx)!=1:
            raise RuntimeError(f"coefficient not found: {target}")
        out.append(float(coef[int(idx[0])]))
    return out[0],out[1]


def bootstrap(d:pd.DataFrame):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    focal=[]; habitat=[]
    attempts=0
    max_attempts=BOOT*10
    while len(focal)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by[n] for n in chosen],ignore_index=True)
        if b["thalassia_return"].nunique()<2:
            continue
        try:
            f,h=fit_coefs(b)
        except Exception:
            continue
        focal.append(f); habitat.append(h)
    if len(focal)<BOOT:
        raise RuntimeError(f"only {len(focal)} valid bootstrap fits from {attempts}")
    return np.asarray(focal,float),np.asarray(habitat,float),attempts


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    if len(seq)!=259:
        raise RuntimeError(f"recovery sequence registry drift: {len(seq)}")
    d=build_frame(py,seq)

    nodes=int(d["node_id"].nunique())
    th_var=int((d.groupby("node_id")["thalassia_run"].nunique()>1).sum())
    head_pos=int((d["habitat_headstart"]>0).sum())
    head_nodes=int(d.loc[d["habitat_headstart"]>0,"node_id"].nunique())
    estimable=bool(
        len(d)>=int(H["minimum_sequences"])
        and nodes>=int(H["minimum_nodes"])
        and th_var>=int(H["minimum_nodes_with_thalassia_run_variation"])
        and head_pos>=int(H["minimum_headstart_positive_events"])
        and head_nodes>=int(H["minimum_nodes_with_positive_headstart"])
    )

    result={
        "schema":"tampa.focal_vs_habitat_legacy_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/focal_vs_habitat_legacy_v1_contract.json",
        "registry":{
            "recovery_sequences":int(len(d)),
            "nodes":nodes,
            "nodes_with_thalassia_run_variation":th_var,
            "headstart_positive_events":head_pos,
            "nodes_with_positive_headstart":head_nodes,
            "thalassia_run_median":float(d["thalassia_run"].median()),
            "any_seagrass_run_median":float(d["any_seagrass_run"].median()),
            "habitat_headstart_median":float(d["habitat_headstart"].median()),
            "habitat_headstart_max":int(d["habitat_headstart"].max()),
        },
        "primary":{
            "centered_thalassia_run_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "centered_habitat_headstart_coefficient":None,
            "habitat_headstart_ci95":None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        focal,habitat=fit_coefs(d)
        fb,hb,attempts=bootstrap(d)
        fci=np.quantile(fb,[.025,.975])
        hci=np.quantile(hb,[.025,.975])
        supported=bool(fci[0]>0)
        result["status"]="focal_specific_legacy_supported" if supported else "focal_specific_legacy_not_supported"
        result["primary"]={
            "centered_thalassia_run_coefficient":focal,
            "ci95":[float(fci[0]),float(fci[1])],
            "bootstrap_replicates":int(len(fb)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]={
            "centered_habitat_headstart_coefficient":habitat,
            "habitat_headstart_ci95":[float(hci[0]),float(hci[1])],
        }
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen predictor-structure or sequence/node minima were not met."

    d.to_csv(outdir/"focal_vs_habitat_legacy_sequences.csv",index=False)
    (outdir/"focal_vs_habitat_legacy_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_focal_vs_habitat"))
    p.add_argument("--out",type=Path,default=Path("results/generated_focal_vs_habitat"))
    a=p.parse_args(); main(a.input,a.out)
