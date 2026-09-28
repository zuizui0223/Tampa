#!/usr/bin/env python3
"""Test whether pre-loss focal history predicts quantitative recovery depth.

Frozen design: results/legacy_recovery_quality_v1_contract.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/legacy_recovery_quality_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
CAT=["node_id","return_year"]
NUM=["source_bb","thalassia_run_centered","habitat_headstart_centered","loss_year_vegetated","source_mixed"]


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def by_point_year(py:pd.DataFrame):
    out={}
    for point,g in py.groupby("point_id",sort=False):
        out[str(point)]={int(r.year):r for r in g.itertuples(index=False)}
    return out


def consecutive_run(ymap:dict[int,object],year:int,field:str)->int:
    run=0
    y=int(year)
    while y in ymap and bool(getattr(ymap[y],field)):
        run+=1
        y-=1
    return run


def build_sequences(py:pd.DataFrame,q:pd.DataFrame)->pd.DataFrame:
    qmap={(str(r.point_id),int(r.year)):float(r.bb_numeric_mean)
          for r in q.itertuples(index=False)}
    by=by_point_year(py)
    rows=[]
    for point,ymap in by.items():
        for y0 in sorted(ymap):
            y1,y2=y0+1,y0+2
            if y1 not in ymap or y2 not in ymap:
                continue
            if y0<2016 or y2>2025:
                continue
            a,b,c=ymap[y0],ymap[y1],ymap[y2]
            if not (bool(a.thalassia_present) and not bool(b.thalassia_present) and bool(c.thalassia_present)):
                continue
            source_bb=qmap.get((point,y0))
            return_bb=qmap.get((point,y2))
            if source_bb is None or return_bb is None:
                continue
            tr=consecutive_run(ymap,y0,"thalassia_present")
            ar=consecutive_run(ymap,y0,"any_seagrass_present")
            head=max(0,ar-tr)
            rows.append({
                "point_id":point,
                "node_id":str(a.node_id),
                "water_body":str(a.water_body),
                "source_year":int(y0),
                "loss_year":int(y1),
                "return_year":str(y2),
                "return_year_int":int(y2),
                "source_bb":float(source_bb),
                "return_bb":float(return_bb),
                "thalassia_run":int(tr),
                "any_seagrass_run":int(ar),
                "habitat_headstart":int(head),
                "loss_year_vegetated":int(bool(b.any_seagrass_present)),
                "source_mixed":int(bool(species_set(a.alternative_species))),
            })
    d=pd.DataFrame(rows)
    if len(d):
        d["thalassia_run_centered"]=(
            d["thalassia_run"].astype(float)
            - d.groupby("node_id")["thalassia_run"].transform("mean").astype(float)
        )
        d["habitat_headstart_centered"]=(
            d["habitat_headstart"].astype(float)
            - d.groupby("node_id")["habitat_headstart"].transform("mean").astype(float)
        )
    return d


def make_model():
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),NUM),
    ])
    return make_pipeline(pre,Ridge(alpha=1.0))


def fit_coefficients(d:pd.DataFrame)->dict[str,float]:
    m=make_model()
    m.fit(d[CAT+NUM],d["return_bb"].to_numpy(float))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["ridge"].coef_
    out={}
    for key in NUM:
        idx=np.where(names==f"num__{key}")[0]
        if len(idx)!=1:
            raise RuntimeError(f"coefficient missing {key}")
        out[key]=float(coef[int(idx[0])])
    return out


def bootstrap(d:pd.DataFrame,key:str):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    while len(vals)<BOOT and attempts<BOOT*20:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by[n] for n in chosen],ignore_index=True)
        try:
            vals.append(fit_coefficients(b)[key])
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstrap fits from {attempts}")
    return np.asarray(vals,float),attempts


def run_classes(d:pd.DataFrame):
    rows=[]
    for run,g in d.groupby("thalassia_run",sort=True):
        if len(g)<10:
            continue
        rows.append({
            "thalassia_run":int(run),
            "sequences":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "return_bb_mean":float(g["return_bb"].mean()),
            "return_bb_median":float(g["return_bb"].median()),
            "mean_source_to_return_change":float((g["return_bb"]-g["source_bb"]).mean()),
        })
    return rows


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    q=pd.read_csv(input_dir/"recovery_debt_point_year_bb.csv")
    if len(py)!=45494:
        raise RuntimeError(f"point-year registry drift {len(py)}")
    d=build_sequences(py,q)

    node_var=(d.groupby("node_id")["thalassia_run"].nunique()>1) if len(d) else pd.Series(dtype=bool)
    positive_head=int((d["habitat_headstart"]>0).sum()) if len(d) else 0
    estimable=bool(
        len(d)>=int(H["minimum_sequences"])
        and d["node_id"].nunique()>=int(H["minimum_nodes"])
        and int(node_var.sum())>=int(H["minimum_nodes_with_thalassia_run_variation"])
        and positive_head>=int(H["minimum_positive_headstart_events"])
    )

    result={
        "schema":"tampa.legacy_recovery_quality_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/legacy_recovery_quality_v1_contract.json",
        "registry":{
            "recovered_quantitative_sequences":int(len(d)),
            "nodes":int(d["node_id"].nunique()) if len(d) else 0,
            "nodes_with_thalassia_run_variation":int(node_var.sum()) if len(d) else 0,
            "positive_habitat_headstart_events":positive_head,
            "thalassia_run_min":int(d["thalassia_run"].min()) if len(d) else None,
            "thalassia_run_max":int(d["thalassia_run"].max()) if len(d) else None,
        },
        "primary":{
            "thalassia_run_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "coefficients":None,
            "habitat_headstart_ci95":None,
            "run_classes":run_classes(d) if len(d) else [],
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        coef=fit_coefficients(d)
        vals,attempts=bootstrap(d,"thalassia_run_centered")
        ci=np.quantile(vals,[.025,.975])
        headvals,_=bootstrap(d,"habitat_headstart_centered")
        hci=np.quantile(headvals,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="legacy_recovery_quality_supported" if supported else "legacy_recovery_quality_not_supported"
        result["primary"]={
            "thalassia_run_coefficient":coef["thalassia_run_centered"],
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]={
            "coefficients":coef,
            "habitat_headstart_ci95":[float(hci[0]),float(hci[1])],
            "run_classes":run_classes(d),
        }
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen sequence/node/history-variation/headstart minima were not met."

    d.to_csv(outdir/"legacy_recovery_quality_sequences.csv",index=False)
    pd.DataFrame(result["secondary"]["run_classes"]).to_csv(
        outdir/"legacy_recovery_quality_run_classes.csv",index=False
    )
    (outdir/"legacy_recovery_quality_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_legacy_recovery_quality"))
    p.add_argument("--out",type=Path,default=Path("results/generated_legacy_recovery_quality"))
    a=p.parse_args(); main(a.input,a.out)
