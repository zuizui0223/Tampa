#!/usr/bin/env python3
"""Test whether return-year quantitative quality predicts subsequent re-loss.

Frozen design: results/return_quality_fragility_v1_contract.json
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
C=json.loads((ROOT/"results/return_quality_fragility_v1_contract.json").read_text())
H=C["primary_hypothesis"]

CAT=["node_id","return_year"]
NUM=["pre_loss_run_length_centered","loss_year_vegetated","source_bb","return_bb"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])


def build_point_lookup(py:pd.DataFrame):
    out={}
    for point,g in py.groupby("point_id",sort=False):
        out[str(point)]={int(r.year):r for r in g.itertuples(index=False)}
    return out


def pre_loss_run(year_map:dict[int,object],source_year:int)->int:
    run=0
    y=int(source_year)
    while y in year_map and bool(year_map[y].thalassia_present):
        run+=1
        y-=1
    return run


def build_sequences(py:pd.DataFrame, q:pd.DataFrame)->pd.DataFrame:
    qmap={(str(r.point_id),int(r.year)):float(r.bb_numeric_mean)
          for r in q.itertuples(index=False)}
    by_point=build_point_lookup(py)
    rows=[]
    for point,ymap in by_point.items():
        years=sorted(ymap)
        for y0 in years:
            y1,y2,y3=y0+1,y0+2,y0+3
            if y1 not in ymap or y2 not in ymap or y3 not in ymap:
                continue
            if y0<2016 or y3>2025:
                continue
            a,b,c,d=ymap[y0],ymap[y1],ymap[y2],ymap[y3]
            if not (bool(a.thalassia_present) and not bool(b.thalassia_present) and bool(c.thalassia_present)):
                continue
            source_bb=qmap.get((point,y0))
            return_bb=qmap.get((point,y2))
            if source_bb is None or return_bb is None:
                continue
            rows.append({
                "point_id":point,
                "node_id":str(a.node_id),
                "water_body":str(a.water_body),
                "source_year":int(y0),
                "loss_year":int(y1),
                "return_year":str(y2),
                "return_year_int":int(y2),
                "outcome_year":int(y3),
                "pre_loss_run_length":int(pre_loss_run(ymap,y0)),
                "loss_year_vegetated":int(bool(b.any_seagrass_present)),
                "source_bb":float(source_bb),
                "return_bb":float(return_bb),
                "recorded_reloss":int(not bool(d.thalassia_present)),
            })
    d=pd.DataFrame(rows)
    if len(d):
        d["pre_loss_run_length_centered"]=(
            d["pre_loss_run_length"].astype(float)
            - d.groupby("node_id")["pre_loss_run_length"].transform("mean").astype(float)
        )
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


def fit_coefficients(d:pd.DataFrame)->dict[str,float]:
    if d["recorded_reloss"].nunique()<2:
        raise RuntimeError("insufficient outcome classes")
    m=make_model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["recorded_reloss"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    out={}
    for key in NUM:
        idx=np.where(names==f"num__{key}")[0]
        if len(idx)!=1:
            raise RuntimeError(f"coefficient missing {key}")
        out[key]=float(coef[int(idx[0])])
    return out


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
        if b["recorded_reloss"].nunique()<2:
            continue
        try:
            vals.append(fit_coefficients(b)["return_bb"])
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstraps from {attempts}")
    return np.asarray(vals,float),attempts


def quartile_summary(d:pd.DataFrame):
    try:
        q=pd.qcut(d["return_bb"],4,labels=False,duplicates="drop")
    except Exception:
        return []
    x=d.assign(return_bb_quartile=q)
    rows=[]
    for k,g in x.dropna(subset=["return_bb_quartile"]).groupby("return_bb_quartile"):
        if len(g)<10:
            continue
        rows.append({
            "quartile":int(k)+1,
            "sequences":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "return_bb_mean":float(g["return_bb"].mean()),
            "recorded_reloss_fraction":float(g["recorded_reloss"].mean()),
        })
    return rows


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    q=pd.read_csv(input_dir/"recovery_debt_point_year_bb.csv")
    if len(py)!=45494:
        raise RuntimeError(f"point-year registry drift {len(py)}")

    d=build_sequences(py,q)
    reloss=int(d["recorded_reloss"].sum()) if len(d) else 0
    estimable=bool(
        len(d)>=int(H["minimum_sequences"])
        and d["node_id"].nunique()>=int(H["minimum_nodes"])
        and reloss>=int(H["minimum_reloss_events"])
    )

    result={
        "schema":"tampa.return_quality_fragility_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/return_quality_fragility_v1_contract.json",
        "registry":{
            "complete_recovered_four_year_sequences":int(len(d)),
            "nodes":int(d["node_id"].nunique()) if len(d) else 0,
            "recorded_relosses":reloss,
            "stable_returns":int(len(d)-reloss),
            "pre_loss_run_min":int(d["pre_loss_run_length"].min()) if len(d) else None,
            "pre_loss_run_max":int(d["pre_loss_run_length"].max()) if len(d) else None,
        },
        "primary":{
            "return_bb_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "coefficients":None,
            "stable_return_bb_mean":float(d.loc[d["recorded_reloss"]==0,"return_bb"].mean()) if len(d) else None,
            "relost_return_bb_mean":float(d.loc[d["recorded_reloss"]==1,"return_bb"].mean()) if len(d) else None,
            "quartiles":quartile_summary(d) if len(d) else [],
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        coef=fit_coefficients(d)
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[1]<0)
        result["status"]="return_quality_fragility_supported" if supported else "return_quality_fragility_not_supported"
        result["primary"]={
            "return_bb_coefficient":coef["return_bb"],
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]["coefficients"]=coef
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen recovered-sequence/node/re-loss minima were not met."

    d.to_csv(outdir/"return_quality_fragility_sequences.csv",index=False)
    pd.DataFrame(result["secondary"]["quartiles"]).to_csv(
        outdir/"return_quality_fragility_quartiles.csv",index=False
    )
    (outdir/"return_quality_fragility_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_return_quality_fragility"))
    p.add_argument("--out",type=Path,default=Path("results/generated_return_quality_fragility"))
    a=p.parse_args(); main(a.input,a.out)
