#!/usr/bin/env python3
"""Audit pre-loss local legacy after saturating current quantitative meadow state.

Frozen design:
results/local_legacy_current_state_audit_v1_contract.json

The primary question is whether the already-supported exact-point pre-loss run-length
effect remains after adding source-year transect-level focal frequency and
Braun-Blanquet state, stable node identity, loss year, loss-year vegetation state,
and source mixed-species state.
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
C=json.loads((ROOT/"results/local_legacy_current_state_audit_v1_contract.json").read_text())
H=C["primary_hypothesis"]
M=C["model"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
MIN_SEQ=int(H["minimum_sequences"])
MIN_NODES=int(H["minimum_nodes"])
MIN_VAR_NODES=int(H["minimum_nodes_with_run_length_variation"])

CAT=["node_id"]
BASE_NUM=["loss_year","loss_year_vegetated","source_mixed"]
STATE_NUM=["source_focal_frequency","source_bb_cover_mean_all_points"]
HIST="pre_loss_run_length_centered"
NUM=BASE_NUM+STATE_NUM+[HIST]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_history_frame(py:pd.DataFrame,seq:pd.DataFrame,annual:pd.DataFrame)->pd.DataFrame:
    required_py={
        "point_id","node_id","year","thalassia_present",
        "any_seagrass_present","alternative_species"
    }
    required_seq={
        "point_id","node_id","source_year","loss_year","recovery_year",
        "intermediate_state","thalassia_return"
    }
    required_ann={
        "node_id","year","focal_frequency","bb_cover_mean_all_points"
    }
    if m:=required_py.difference(py.columns):
        raise RuntimeError(f"point-year columns missing: {sorted(m)}")
    if m:=required_seq.difference(seq.columns):
        raise RuntimeError(f"recovery columns missing: {sorted(m)}")
    if m:=required_ann.difference(annual.columns):
        raise RuntimeError(f"annual columns missing: {sorted(m)}")

    by_point={}
    for point,g in py.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    ann=annual[list(required_ann)].copy()
    ann["node_id"]=ann["node_id"].astype(str)
    ann["year"]=ann["year"].astype(int)
    ann=ann.rename(columns={
        "year":"source_year",
        "focal_frequency":"source_focal_frequency",
        "bb_cover_mean_all_points":"source_bb_cover_mean_all_points",
    })

    rows=[]
    for r in seq.itertuples(index=False):
        point=str(r.point_id)
        source=int(r.source_year)
        hist=by_point.get(point,{})
        if source not in hist:
            raise RuntimeError(f"source point-year absent: {point} {source}")
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
            "thalassia_return":int(r.thalassia_return),
            "loss_year_vegetated":int(str(r.intermediate_state)=="other_seagrass"),
            "source_mixed":int(bool(species_set(src.alternative_species))),
            "pre_loss_run_length":int(run),
        })

    d=pd.DataFrame(rows)
    if len(d)!=259:
        raise RuntimeError(f"frozen recovery registry drift: {len(d)}")
    d=d.merge(ann,on=["node_id","source_year"],how="left",validate="many_to_one")
    d=d.dropna(subset=STATE_NUM).copy()
    if len(d)==0:
        raise RuntimeError("no current-state-complete recovery sequences")
    node_mean=d.groupby("node_id")["pre_loss_run_length"].transform("mean")
    d[HIST]=d["pre_loss_run_length"].astype(float)-node_mean.astype(float)
    return d


def make_model(include_state:bool=True):
    nums=BASE_NUM+([*STATE_NUM] if include_state else [])+[HIST]
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),nums),
    ])
    return make_pipeline(
        pre,
        LogisticRegression(
            C=float(M["logistic_C"]),
            solver=str(M["solver"]),
            max_iter=int(M["max_iter"]),
        )
    ), nums


def fit_coef(d:pd.DataFrame,include_state:bool=True)->float:
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("one-class outcome")
    model,nums=make_model(include_state)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(d[CAT+nums],d["thalassia_return"].to_numpy(int))
    names=model.named_steps["columntransformer"].get_feature_names_out()
    coef=model.named_steps["logisticregression"].coef_[0]
    target=f"num__{HIST}"
    idx=np.where(names==target)[0]
    if len(idx)!=1:
        raise RuntimeError(f"legacy coefficient not found: {names}")
    return float(coef[int(idx[0])])


def bootstrap(d:pd.DataFrame):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    while len(vals)<BOOT and attempts<BOOT*8:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        pieces=[]
        for j,n in enumerate(chosen):
            z=by[n].copy()
            z["node_id"]=f"boot_{j}_{n}"
            pieces.append(z)
        b=pd.concat(pieces,ignore_index=True)
        try:
            vals.append(fit_coef(b,True))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstrap fits")
    return np.asarray(vals,float),attempts


def safe_corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if len(a)<3 or np.isclose(a.std(ddof=0),0) or np.isclose(b.std(ddof=0),0):
        return None
    return float(np.corrcoef(a,b)[0,1])


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")

    d=build_history_frame(py,seq,annual)
    nodes=int(d["node_id"].nunique())
    varying=int((d.groupby("node_id")["pre_loss_run_length"].nunique()>1).sum())
    estimable=bool(len(d)>=MIN_SEQ and nodes>=MIN_NODES and varying>=MIN_VAR_NODES)

    result={
        "schema":"tampa.local_legacy_current_state_audit_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/local_legacy_current_state_audit_v1_contract.json",
        "registry":{
            "complete_sequences":int(len(d)),
            "nodes":nodes,
            "nodes_with_run_length_variation":varying,
            "run_length_min":int(d["pre_loss_run_length"].min()),
            "run_length_median":float(d["pre_loss_run_length"].median()),
            "run_length_max":int(d["pre_loss_run_length"].max()),
        },
        "primary":{
            "current_state_saturated_run_length_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "without_current_state_run_length_coefficient":None,
            "corr_run_length_source_frequency":safe_corr(d["pre_loss_run_length"],d["source_focal_frequency"]),
            "corr_run_length_source_bb":safe_corr(d["pre_loss_run_length"],d["source_bb_cover_mean_all_points"]),
            "return_source_frequency_median":float(d.loc[d["thalassia_return"]==1,"source_focal_frequency"].median()) if (d["thalassia_return"]==1).any() else None,
            "nonreturn_source_frequency_median":float(d.loc[d["thalassia_return"]==0,"source_focal_frequency"].median()) if (d["thalassia_return"]==0).any() else None,
            "return_source_bb_median":float(d.loc[d["thalassia_return"]==1,"source_bb_cover_mean_all_points"].median()) if (d["thalassia_return"]==1).any() else None,
            "nonreturn_source_bb_median":float(d.loc[d["thalassia_return"]==0,"source_bb_cover_mean_all_points"].median()) if (d["thalassia_return"]==0).any() else None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        point=fit_coef(d,True)
        orient=fit_coef(d,False)
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="legacy_beyond_current_state_supported" if supported else "legacy_beyond_current_state_not_supported"
        result["primary"]={
            "current_state_saturated_run_length_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]["without_current_state_run_length_coefficient"]=orient
        result["interpretation"]=C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
    else:
        result["interpretation"]="Frozen current-state-complete sequence/node/variation minima were not met."

    d.to_csv(outdir/"local_legacy_current_state_audit_sequences.csv",index=False)
    (outdir/"local_legacy_current_state_audit_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_local_legacy_current_state"))
    p.add_argument("--out",type=Path,default=Path("results/generated_local_legacy_current_state"))
    a=p.parse_args()
    main(a.input,a.out)
