#!/usr/bin/env python3
"""Test whether exact-point Thalassia return probability decays with time since loss.

Frozen design:
results/recovery_window_v1_contract.json

Builds discrete-time risk rows for years 1-3 after exact-point Thalassia loss,
conditional on the point remaining absent and continuously observed. The primary
coefficient is years_since_loss in a node-fixed-effect logistic model.
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
C=json.loads((ROOT/"results/recovery_window_v1_contract.json").read_text())
H=C["primary_hypothesis"]
M=C["model"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
MIN_ROWS=int(H["minimum_risk_rows"])
MIN_NODES=int(H["minimum_nodes"])
MIN_PER_D=int(H["minimum_rows_per_duration"])
MIN_RET=int(H["minimum_returns"])
LOSS_Y0,LOSS_Y1=[int(v) for v in C["episode_population"]["loss_year_range"]]
MAX_D=int(C["episode_population"]["maximum_absence_duration_years"])

CAT=["node_id"]
NUM=[
    "loss_year",
    "years_since_loss",
    "pre_loss_run_length_centered",
    "source_mixed",
    "previous_other_seagrass",
]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_episodes(py:pd.DataFrame)->pd.DataFrame:
    req={
        "point_id","node_id","water_body","year","thalassia_present",
        "any_seagrass_present","alternative_species"
    }
    if m:=req.difference(py.columns):
        raise RuntimeError(f"missing point-year columns: {sorted(m)}")

    by_point={}
    for point,g in py.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    episodes=[]
    for point,hist in by_point.items():
        years=sorted(hist)
        for loss_year in years:
            if not (LOSS_Y0<=loss_year<=LOSS_Y1):
                continue
            source_year=loss_year-1
            if source_year not in hist:
                continue
            src=hist[source_year]
            loss=hist[loss_year]
            if not bool(src.thalassia_present) or bool(loss.thalassia_present):
                continue

            run=0
            y=source_year
            while y in hist and bool(hist[y].thalassia_present):
                run+=1
                y-=1

            episodes.append({
                "episode_id":f"{point}|{loss_year}",
                "point_id":point,
                "node_id":str(src.node_id),
                "water_body":str(src.water_body),
                "source_year":source_year,
                "loss_year":loss_year,
                "pre_loss_run_length":int(run),
                "source_mixed":int(bool(species_set(src.alternative_species))),
            })

    e=pd.DataFrame(episodes)
    if len(e)==0:
        raise RuntimeError("no eligible loss episodes")
    node_mean=e.groupby("node_id")["pre_loss_run_length"].transform("mean")
    e["pre_loss_run_length_centered"]=e["pre_loss_run_length"].astype(float)-node_mean.astype(float)
    return e,by_point


def expand_risk_rows(episodes:pd.DataFrame, by_point:dict[str,dict[int,object]])->pd.DataFrame:
    rows=[]
    for ep in episodes.itertuples(index=False):
        hist=by_point[str(ep.point_id)]
        loss_year=int(ep.loss_year)
        # Prior state for duration 1 is the loss year, which is focal-absent by construction.
        prior_year=loss_year
        for d in range(1,MAX_D+1):
            current_year=loss_year+d
            if prior_year not in hist or current_year not in hist:
                break
            prior=hist[prior_year]
            cur=hist[current_year]
            if bool(prior.thalassia_present):
                # Should only occur after a prior return, at which point the episode must already have stopped.
                break

            ret=int(bool(cur.thalassia_present))
            rows.append({
                "episode_id":ep.episode_id,
                "point_id":ep.point_id,
                "node_id":ep.node_id,
                "water_body":ep.water_body,
                "loss_year":loss_year,
                "risk_year":current_year,
                "years_since_loss":int(d),
                "pre_loss_run_length":int(ep.pre_loss_run_length),
                "pre_loss_run_length_centered":float(ep.pre_loss_run_length_centered),
                "source_mixed":int(ep.source_mixed),
                "previous_other_seagrass":int(bool(prior.any_seagrass_present)),
                "thalassia_return":ret,
            })
            if ret:
                break
            prior_year=current_year
    d=pd.DataFrame(rows)
    if len(d)==0:
        raise RuntimeError("no recovery risk rows")
    return d


def make_model(include_history:bool=True):
    nums=[
        "loss_year",
        "years_since_loss",
        "source_mixed",
        "previous_other_seagrass",
    ] + (["pre_loss_run_length_centered"] if include_history else [])
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),nums),
    ])
    clf=LogisticRegression(
        C=float(M["logistic_C"]),
        solver=str(M["solver"]),
        max_iter=int(M["max_iter"]),
    )
    return make_pipeline(pre,clf),nums


def fit_duration_coef(d:pd.DataFrame,include_history:bool=True)->float:
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("one-class outcome")
    model,nums=make_model(include_history)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(d[CAT+nums],d["thalassia_return"].to_numpy(int))
    names=model.named_steps["columntransformer"].get_feature_names_out()
    coef=model.named_steps["logisticregression"].coef_[0]
    target="num__years_since_loss"
    idx=np.where(names==target)[0]
    if len(idx)!=1:
        raise RuntimeError(f"duration coefficient not found: {names}")
    return float(coef[int(idx[0])])


def bootstrap_nodes(d:pd.DataFrame)->tuple[np.ndarray,int]:
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    while len(vals)<BOOT and attempts<BOOT*10:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        pieces=[]
        for j,n in enumerate(chosen):
            z=by[n].copy()
            z["node_id"]=f"boot_{j}_{n}"
            pieces.append(z)
        b=pd.concat(pieces,ignore_index=True)
        try:
            vals.append(fit_duration_coef(b,True))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstrap fits")
    return np.asarray(vals,float),attempts


def duration_summary(d:pd.DataFrame)->pd.DataFrame:
    return (d.groupby("years_since_loss",as_index=False)
        .agg(
            risk_rows=("episode_id","size"),
            nodes=("node_id","nunique"),
            returns=("thalassia_return","sum"),
            return_hazard=("thalassia_return","mean"),
        )
        .sort_values("years_since_loss"))


def continuity_summary(d:pd.DataFrame)->pd.DataFrame:
    return (d.groupby("previous_other_seagrass",as_index=False)
        .agg(
            risk_rows=("episode_id","size"),
            nodes=("node_id","nunique"),
            returns=("thalassia_return","sum"),
            return_hazard=("thalassia_return","mean"),
        )
        .sort_values("previous_other_seagrass"))


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")

    episodes,by_point=build_episodes(py)
    risk=expand_risk_rows(episodes,by_point)
    ds=duration_summary(risk)

    per_duration={int(r.years_since_loss):int(r.risk_rows) for r in ds.itertuples()}
    estimable=bool(
        len(risk)>=MIN_ROWS
        and risk["node_id"].nunique()>=MIN_NODES
        and int(risk["thalassia_return"].sum())>=MIN_RET
        and all(per_duration.get(d,0)>=MIN_PER_D for d in range(1,MAX_D+1))
    )

    result={
        "schema":"tampa.recovery_window_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/recovery_window_v1_contract.json",
        "registry":{
            "loss_episodes":int(len(episodes)),
            "risk_rows":int(len(risk)),
            "nodes":int(risk["node_id"].nunique()),
            "returns":int(risk["thalassia_return"].sum()),
            "risk_rows_by_duration":{str(k):v for k,v in per_duration.items()},
        },
        "primary":{
            "duration_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "duration_hazards":ds.to_dict("records"),
            "without_history_duration_coefficient":None,
            "previous_other_seagrass_hazards":continuity_summary(risk).to_dict("records"),
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        point=fit_duration_coef(risk,True)
        orient=fit_duration_coef(risk,False)
        vals,attempts=bootstrap_nodes(risk)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[1]<0)
        result["status"]="finite_recovery_window_supported" if supported else "recovery_window_not_supported"
        result["primary"]={
            "duration_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]["without_history_duration_coefficient"]=orient
        result["interpretation"]=C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
    else:
        result["interpretation"]="Frozen risk-row/node/duration/return minima were not met."

    episodes.to_csv(outdir/"recovery_window_episodes.csv",index=False)
    risk.to_csv(outdir/"recovery_window_risk_rows.csv",index=False)
    ds.to_csv(outdir/"recovery_window_hazards_by_duration.csv",index=False)
    continuity_summary(risk).to_csv(outdir/"recovery_window_hazards_by_previous_vegetation.csv",index=False)
    (outdir/"recovery_window_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_recovery_window"))
    p.add_argument("--out",type=Path,default=Path("results/generated_recovery_window"))
    a=p.parse_args()
    main(a.input,a.out)
