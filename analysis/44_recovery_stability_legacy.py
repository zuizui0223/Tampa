#!/usr/bin/env python3
"""Test whether pre-loss focal history predicts stability of exact-point returns.

Frozen design: results/recovery_stability_legacy_v1_contract.json
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
C=json.loads((ROOT/"results/recovery_stability_legacy_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
CAT=["node_id","return_year"]
NUM=["loss_year_vegetated","source_mixed","pre_loss_run_centered"]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_sequences(py:pd.DataFrame)->pd.DataFrame:
    by_point={}
    for point,g in py.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}

    rows=[]
    for point,hist in by_point.items():
        years=sorted(hist)
        for y0 in years:
            y1,y2,y3=y0+1,y0+2,y0+3
            if y0<2016 or y3>2025:
                continue
            if not all(y in hist for y in [y0,y1,y2,y3]):
                continue
            a,b,c,d=[hist[y] for y in [y0,y1,y2,y3]]
            if not (bool(a.thalassia_present) and not bool(b.thalassia_present) and bool(c.thalassia_present)):
                continue
            run=0
            y=y0
            while y in hist and bool(hist[y].thalassia_present):
                run+=1; y-=1
            rows.append({
                "point_id":point,
                "node_id":str(a.node_id),
                "water_body":str(a.water_body),
                "source_year":y0,
                "loss_year":y1,
                "return_year":str(y2),
                "outcome_year":y3,
                "loss_year_vegetated":int(bool(b.any_seagrass_present)),
                "source_mixed":int(bool(species_set(a.alternative_species))),
                "pre_loss_run_length":int(run),
                "recorded_reloss":int(not bool(d.thalassia_present)),
            })
    x=pd.DataFrame(rows)
    if len(x):
        x["pre_loss_run_centered"]=(
            x["pre_loss_run_length"]-
            x.groupby("node_id")["pre_loss_run_length"].transform("mean")
        )
    return x


def make_model():
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),NUM),
    ])
    clf=LogisticRegression(
        C=float(H["logistic_C"]),solver=str(H["solver"]),max_iter=int(H["max_iter"])
    )
    return make_pipeline(pre,clf)


def fit_coefs(d:pd.DataFrame):
    if d["recorded_reloss"].nunique()<2:
        raise RuntimeError("single outcome class")
    m=make_model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["recorded_reloss"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    out={}
    for target in ["pre_loss_run_centered","loss_year_vegetated"]:
        idx=np.where(names=="num__"+target)[0]
        if len(idx)!=1:
            raise RuntimeError(f"coefficient missing {target}")
        out[target]=float(coef[int(idx[0])])
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
            vals.append(fit_coefs(b)["pre_loss_run_centered"])
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstrap fits from {attempts}")
    return np.asarray(vals,float),attempts


def by_run(d:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for run,g in d.groupby("pre_loss_run_length",sort=True):
        if len(g)<5:
            continue
        rows.append({
            "pre_loss_run_length":int(run),
            "sequences":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "recorded_reloss_fraction":float(g["recorded_reloss"].mean()),
        })
    return pd.DataFrame(rows)


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    d=build_sequences(py)

    nodes=int(d["node_id"].nunique()) if len(d) else 0
    varying=int((d.groupby("node_id")["pre_loss_run_length"].nunique()>1).sum()) if len(d) else 0
    reloss=int(d["recorded_reloss"].sum()) if len(d) else 0
    stable=int(len(d)-reloss)
    estimable=bool(
        len(d)>=int(H["minimum_sequences"])
        and nodes>=int(H["minimum_nodes"])
        and varying>=int(H["minimum_nodes_with_run_length_variation"])
        and reloss>=int(H["minimum_reloss_events"])
        and stable>=int(H["minimum_stable_events"])
    )

    result={
        "schema":"tampa.recovery_stability_legacy_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/recovery_stability_legacy_v1_contract.json",
        "registry":{
            "recovered_four_year_sequences":int(len(d)),
            "nodes":nodes,
            "nodes_with_run_length_variation":varying,
            "recorded_relosses":reloss,
            "stable_returns":stable,
        },
        "primary":{
            "centered_pre_loss_run_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "loss_year_vegetated_coefficient":None,
            "recovered_reloss_fraction":float(d["recorded_reloss"].mean()) if len(d) else None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        coefs=fit_coefs(d)
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[1]<0)
        result["status"]="recovery_stability_legacy_supported" if supported else "recovery_stability_legacy_not_supported"
        result["primary"]={
            "centered_pre_loss_run_coefficient":coefs["pre_loss_run_centered"],
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]["loss_year_vegetated_coefficient"]=coefs["loss_year_vegetated"]
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen recovered-sequence/node/outcome minima were not met."

    d.to_csv(outdir/"recovery_stability_legacy_sequences.csv",index=False)
    by_run(d).to_csv(outdir/"recovery_stability_by_run_length.csv",index=False)
    (outdir/"recovery_stability_legacy_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_recovery_stability"))
    p.add_argument("--out",type=Path,default=Path("results/generated_recovery_stability"))
    a=p.parse_args(); main(a.input,a.out)
