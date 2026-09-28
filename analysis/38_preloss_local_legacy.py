#!/usr/bin/env python3
"""Test whether pre-loss local Thalassia history predicts exact-point re-recording.

Frozen design: results/preloss_local_legacy_v1_contract.json

Consumes the exact same point-year consensus states and three-year recovery sequences
used by the community-insurance / microsite-recovery analyses. The primary predictor
is consecutive pre-loss Thalassia run length centered within stable transect node.
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
C=json.loads((ROOT/"results/preloss_local_legacy_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
MIN_SEQ=int(H["minimum_sequences"])
MIN_NODES=int(H["minimum_nodes"])
MIN_VAR_NODES=int(H["minimum_nodes_with_run_length_variation"])

CAT=["node_id"]
NUM=["loss_year","loss_year_vegetated","source_mixed","pre_loss_run_length_centered"]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_history_frame(py:pd.DataFrame, seq:pd.DataFrame)->pd.DataFrame:
    required_py={
        "point_id","node_id","year","thalassia_present",
        "any_seagrass_present","alternative_species"
    }
    required_seq={
        "point_id","node_id","source_year","loss_year","recovery_year",
        "intermediate_state","thalassia_return"
    }
    if m:=required_py.difference(py.columns):
        raise RuntimeError(f"point-year columns missing: {sorted(m)}")
    if m:=required_seq.difference(seq.columns):
        raise RuntimeError(f"recovery columns missing: {sorted(m)}")

    by_point={}
    for point,g in py.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    rows=[]
    for r in seq.itertuples(index=False):
        point=str(r.point_id)
        source=int(r.source_year)
        history=by_point.get(point,{})
        if source not in history:
            raise RuntimeError(f"source point-year absent from consensus panel: {point} {source}")
        src=history[source]
        if not bool(src.thalassia_present):
            raise RuntimeError(f"recovery sequence source not Thalassia-positive: {point} {source}")

        run=0
        y=source
        while y in history and bool(history[y].thalassia_present):
            run+=1
            y-=1

        rows.append({
            "point_id":point,
            "node_id":str(r.node_id),
            "source_year":source,
            "loss_year":int(r.loss_year),
            "recovery_year":int(r.recovery_year),
            "thalassia_return":int(r.thalassia_return),
            "loss_year_vegetated":int(str(r.intermediate_state)=="other_seagrass"),
            "source_mixed":int(bool(species_set(src.alternative_species))),
            "pre_loss_run_length":int(run),
        })

    d=pd.DataFrame(rows)
    if len(d)==0:
        raise RuntimeError("no legacy-eligible recovery sequences")
    if (d["pre_loss_run_length"]<1).any():
        raise RuntimeError("pre-loss run length below one")

    node_mean=d.groupby("node_id")["pre_loss_run_length"].transform("mean")
    d["pre_loss_run_length_centered"]=d["pre_loss_run_length"]-node_mean
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


def fit_coef(d:pd.DataFrame)->float:
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("bootstrap sample has one outcome class")
    m=make_model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["thalassia_return"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    target="num__pre_loss_run_length_centered"
    idx=np.where(names==target)[0]
    if len(idx)!=1:
        raise RuntimeError(f"could not locate legacy coefficient: {names}")
    return float(coef[int(idx[0])])


def fit_uncentered_descriptive(d:pd.DataFrame)->float:
    tmp=d.copy()
    tmp["pre_loss_run_length_centered"]=tmp["pre_loss_run_length"].astype(float)
    return fit_coef(tmp)


def bootstrap_nodes(d:pd.DataFrame)->tuple[np.ndarray,int]:
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*5
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by[n] for n in chosen],ignore_index=True)
        try:
            vals.append(fit_coef(b))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstrap fits from {attempts} attempts")
    return np.asarray(vals,float),attempts


def run_length_summary(d:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for run,g in d.groupby("pre_loss_run_length",sort=True):
        if len(g)<10:
            continue
        rows.append({
            "pre_loss_run_length":int(run),
            "sequences":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "thalassia_return_fraction":float(g["thalassia_return"].mean()),
        })
    return pd.DataFrame(rows)


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    if len(seq)!=259:
        raise RuntimeError(f"frozen recovery sequence registry drift: {len(seq)}")

    d=build_history_frame(py,seq)
    nodes=int(d["node_id"].nunique())
    varying=int((d.groupby("node_id")["pre_loss_run_length"].nunique()>1).sum())
    estimable=bool(len(d)>=MIN_SEQ and nodes>=MIN_NODES and varying>=MIN_VAR_NODES)

    result={
        "schema":"tampa.preloss_local_legacy_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/preloss_local_legacy_v1_contract.json",
        "registry":{
            "recovery_sequences":int(len(d)),
            "nodes":nodes,
            "nodes_with_run_length_variation":varying,
            "run_length_min":int(d["pre_loss_run_length"].min()),
            "run_length_max":int(d["pre_loss_run_length"].max()),
            "run_length_median":float(d["pre_loss_run_length"].median()),
        },
        "primary":{
            "centered_run_length_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "uncentered_run_length_coefficient":None,
            "return_run_length_median":float(d.loc[d["thalassia_return"]==1,"pre_loss_run_length"].median()) if (d["thalassia_return"]==1).any() else None,
            "nonreturn_run_length_median":float(d.loc[d["thalassia_return"]==0,"pre_loss_run_length"].median()) if (d["thalassia_return"]==0).any() else None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        point=fit_coef(d)
        uncentered=fit_uncentered_descriptive(d)
        boot,attempts=bootstrap_nodes(d)
        ci=np.quantile(boot,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="preloss_local_legacy_supported" if supported else "preloss_local_legacy_not_supported"
        result["primary"]={
            "centered_run_length_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(boot)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]["uncentered_run_length_coefficient"]=uncentered
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen sequence/node/within-node variation minima were not met."

    d.to_csv(outdir/"preloss_local_legacy_sequences.csv",index=False)
    run_length_summary(d).to_csv(outdir/"preloss_local_legacy_by_run_length.csv",index=False)
    (outdir/"preloss_local_legacy_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_preloss_legacy"))
    p.add_argument("--out",type=Path,default=Path("results/generated_preloss_legacy"))
    a=p.parse_args()
    main(a.input,a.out)
