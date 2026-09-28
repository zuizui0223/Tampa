#!/usr/bin/env python3
"""Test whether exact-point Thalassia returns are more fragile than continuous occupancy.

Frozen design: results/return_fragility_v1_contract.json
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
C=json.loads((ROOT/"results/return_fragility_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
CAT=["node_id","return_year"]
NUM=["recovered_group"]


def build_sequences(py:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for point,g in py.groupby("point_id",sort=True):
        recs=g.sort_values("year").to_dict("records")
        for i in range(len(recs)-3):
            a,b,c,d=recs[i:i+4]
            y0,y1,y2,y3=map(int,[a["year"],b["year"],c["year"],d["year"]])
            if not (y1==y0+1 and y2==y1+1 and y3==y2+1):
                continue
            if y0<2016 or y3>2025:
                continue
            states=[bool(a["thalassia_present"]),bool(b["thalassia_present"]),bool(c["thalassia_present"])]
            if states==[True,False,True]:
                group="recovered"
                recovered=1
            elif states==[True,True,True]:
                group="continuous"
                recovered=0
            else:
                continue
            rows.append({
                "point_id":str(point),
                "node_id":str(a["node_id"]),
                "water_body":str(a["water_body"]),
                "source_year":y0,
                "loss_or_middle_year":y1,
                "return_year":str(y2),
                "outcome_year":y3,
                "group":group,
                "recovered_group":recovered,
                "recorded_reloss":int(not bool(d["thalassia_present"])),
            })
    return pd.DataFrame(rows)


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
    if d["recorded_reloss"].nunique()<2 or d["recovered_group"].nunique()<2:
        raise RuntimeError("insufficient classes")
    m=make_model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["recorded_reloss"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    idx=np.where(names=="num__recovered_group")[0]
    if len(idx)!=1:
        raise RuntimeError("recovered_group coefficient missing")
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
        if b["recorded_reloss"].nunique()<2 or b["recovered_group"].nunique()<2:
            continue
        try:
            vals.append(fit_coef(b))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstraps from {attempts}")
    return np.asarray(vals,float),attempts


def frac(d:pd.DataFrame)->float:
    return float(d["recorded_reloss"].mean()) if len(d) else float("nan")


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    d=build_sequences(py)
    rec=d[d["recovered_group"]==1].copy()
    ctl=d[d["recovered_group"]==0].copy()
    total_reloss=int(d["recorded_reloss"].sum()) if len(d) else 0

    estimable=bool(
        len(rec)>=int(H["minimum_recovered_sequences"])
        and len(ctl)>=int(H["minimum_continuous_sequences"])
        and rec["node_id"].nunique()>=int(H["minimum_recovered_nodes"])
        and ctl["node_id"].nunique()>=int(H["minimum_control_nodes"])
        and total_reloss>=int(H["minimum_reloss_events_total"])
    )

    byseg=[]
    for wb,g in d.groupby("water_body",sort=True):
        r=g[g["recovered_group"]==1]
        c=g[g["recovered_group"]==0]
        byseg.append({
            "water_body":wb,
            "recovered_sequences":int(len(r)),
            "recovered_reloss_fraction":frac(r) if len(r) else None,
            "continuous_sequences":int(len(c)),
            "continuous_reloss_fraction":frac(c) if len(c) else None,
        })

    result={
        "schema":"tampa.return_fragility_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/return_fragility_v1_contract.json",
        "registry":{
            "four_year_sequences":int(len(d)),
            "nodes":int(d["node_id"].nunique()) if len(d) else 0,
            "recovered_sequences":int(len(rec)),
            "recovered_nodes":int(rec["node_id"].nunique()) if len(rec) else 0,
            "continuous_sequences":int(len(ctl)),
            "continuous_nodes":int(ctl["node_id"].nunique()) if len(ctl) else 0,
            "total_recorded_relosses":total_reloss,
        },
        "primary":{
            "recovered_group_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "recovered_reloss_fraction":frac(rec) if len(rec) else None,
            "continuous_reloss_fraction":frac(ctl) if len(ctl) else None,
            "risk_difference_recovered_minus_continuous":(
                float(frac(rec)-frac(ctl)) if len(rec) and len(ctl) else None
            ),
            "by_segment":byseg,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        point=fit_coef(d)
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="return_fragility_supported" if supported else "return_fragility_not_supported"
        result["primary"]={
            "recovered_group_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen recovered/control/node/re-loss minima were not met."

    d.to_csv(outdir/"return_fragility_sequences.csv",index=False)
    pd.DataFrame(byseg).to_csv(outdir/"return_fragility_by_segment.csv",index=False)
    (outdir/"return_fragility_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_return_fragility"))
    p.add_argument("--out",type=Path,default=Path("results/generated_return_fragility"))
    a=p.parse_args(); main(a.input,a.out)
