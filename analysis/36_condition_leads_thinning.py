#!/usr/bin/env python3
"""Test whether plant condition carries leading information about next-year thinning.

Frozen design: results/condition_leads_thinning_v1_contract.json

Primary question:
Does source-year blade length + shoot density improve strict walk-forward prediction
of next-year focal Thalassia frequency beyond stable site identity and current
frequency/Braun-Blanquet state?

This is a post-hoc temporal-ordering test. It is not causal.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/condition_leads_thinning_v1_contract.json").read_text())

SEED=int(C["support_rule"]["random_seed"])
PERM_REPS=int(C["support_rule"]["signflip_replicates"])
MIN_TRAIN=int(C["validation"]["minimum_training_rows"])
MIN_TRAIN_YEARS=int(C["validation"]["minimum_training_target_years"])
MIN_TEST=int(C["validation"]["minimum_test_rows_per_target_year"])
MIN_SCORED=int(C["validation"]["minimum_scored_target_years"])
Y0,Y1=[int(x) for x in C["transition_population"]["candidate_target_years"]]
EXCLUDED={int(x) for x in C["transition_population"]["primary_excluded_target_years"]}

CAT=["water_body","node_id"]
BASE_NUM=["target_year","source_focal_frequency","source_bb_cover_mean_all_points"]
COND_NUM=["source_blade_length_mean_mm","source_log1p_shoot_density"]


def build_transitions(annual:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for node,g in annual.sort_values(["node_id","year"]).groupby("node_id"):
        recs=g.to_dict("records")
        for a,b in zip(recs[:-1],recs[1:]):
            if int(b["year"])!=int(a["year"])+1:
                continue
            if not (Y0<=int(b["year"])<=Y1):
                continue
            vals=[
                a.get("focal_frequency"),
                a.get("bb_cover_mean_all_points"),
                a.get("blade_length_mean_mm"),
                a.get("shoot_density_mean_m2"),
                b.get("focal_frequency"),
                b.get("bb_cover_mean_all_points"),
            ]
            if any(pd.isna(v) for v in vals):
                continue
            shoot=float(a["shoot_density_mean_m2"])
            if shoot<0:
                raise RuntimeError("negative shoot density")
            rows.append({
                "node_id":str(node),
                "water_body":str(a["water_body"]),
                "source_year":int(a["year"]),
                "target_year":int(b["year"]),
                "source_focal_frequency":float(a["focal_frequency"]),
                "source_bb_cover_mean_all_points":float(a["bb_cover_mean_all_points"]),
                "source_blade_length_mean_mm":float(a["blade_length_mean_mm"]),
                "source_shoot_density_mean_m2":shoot,
                "source_log1p_shoot_density":float(np.log1p(shoot)),
                "target_focal_frequency":float(b["focal_frequency"]),
                "target_bb_cover_mean_all_points":float(b["bb_cover_mean_all_points"]),
            })
    return pd.DataFrame(rows).sort_values(["target_year","node_id"]).reset_index(drop=True)


def model(numeric):
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),numeric),
    ])
    return make_pipeline(pre,Ridge(alpha=float(C["implementation_freeze"]["ridge_alpha"])))


def clip_pred(pred,clip):
    p=np.asarray(pred,dtype=float)
    if clip is not None:
        lo,hi=clip
        if lo is not None: p=np.maximum(p,float(lo))
        if hi is not None: p=np.minimum(p,float(hi))
    return p


def signflip(delta,seed):
    d=np.asarray(delta,dtype=float)
    obs=float(d.mean())
    rng=np.random.default_rng(seed)
    count=0
    remaining=PERM_REPS
    while remaining:
        n=min(5000,remaining)
        signs=rng.choice(np.asarray([-1.0,1.0]),size=(n,len(d)),replace=True)
        null=(signs*d[None,:]).mean(axis=1)
        count+=int(np.sum(null<=obs+1e-15))
        remaining-=n
    return float((count+1)/(PERM_REPS+1))


def support(delta,seed):
    d=np.asarray(delta,dtype=float)
    if len(d)<MIN_SCORED:
        return {
            "estimable":False,
            "target_years":int(len(d)),
            "supported":False,
        }
    p=signflip(d,seed)
    wins=int((d<0).sum())
    need=math.ceil(float(C["support_rule"]["minimum_win_fraction"])*len(d))
    med=float(np.median(d))
    return {
        "estimable":True,
        "target_years":int(len(d)),
        "wins":wins,
        "losses":int((d>0).sum()),
        "ties":int((d==0).sum()),
        "mean_delta":float(d.mean()),
        "median_delta":med,
        "signflip_p":p,
        "supported":bool(
            wins>=need
            and med<0
            and p<float(C["support_rule"]["one_sided_signflip_p_lt"])
        ),
    }


def score(frame:pd.DataFrame,target:str,clip,exclude_2016:bool,seed:int):
    d=frame.copy()
    if exclude_2016:
        d=d[~d["target_year"].isin(EXCLUDED)].copy()
    yearly=[]
    for year in range(Y0,Y1+1):
        if exclude_2016 and year in EXCLUDED:
            continue
        train=d[d["target_year"]<year].copy()
        test=d[d["target_year"]==year].copy()
        if len(test)<MIN_TEST:
            continue
        if len(train)<MIN_TRAIN or train["target_year"].nunique()<MIN_TRAIN_YEARS:
            continue
        m0=model(BASE_NUM)
        m1=model(BASE_NUM+COND_NUM)
        m0.fit(train[CAT+BASE_NUM],train[target].to_numpy(float))
        m1.fit(train[CAT+BASE_NUM+COND_NUM],train[target].to_numpy(float))
        p0=clip_pred(m0.predict(test[CAT+BASE_NUM]),clip)
        p1=clip_pred(m1.predict(test[CAT+BASE_NUM+COND_NUM]),clip)
        y=test[target].to_numpy(float)
        yearly.append({
            "target_year":int(year),
            "n_test":int(len(test)),
            "baseline_mae":float(mean_absolute_error(y,p0)),
            "condition_mae":float(mean_absolute_error(y,p1)),
        })
    ys=pd.DataFrame(yearly)
    if len(ys):
        delta=ys["condition_mae"].to_numpy(float)-ys["baseline_mae"].to_numpy(float)
        sup=support(delta,seed)
        summary={
            "eligible_rows":int(len(d)),
            "nodes":int(d["node_id"].nunique()),
            "scored_target_years":int(len(ys)),
            "target_year_range":[int(ys["target_year"].min()),int(ys["target_year"].max())],
            "baseline_mean_mae":float(ys["baseline_mae"].mean()),
            "condition_mean_mae":float(ys["condition_mae"].mean()),
            "support":sup,
        }
    else:
        summary={
            "eligible_rows":int(len(d)),
            "nodes":int(d["node_id"].nunique()),
            "scored_target_years":0,
            "support":{"estimable":False,"target_years":0,"supported":False},
        }
    return ys,summary


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")
    required={
        "node_id","year","water_body",
        "focal_frequency","bb_cover_mean_all_points",
        "blade_length_mean_mm","shoot_density_mean_m2",
    }
    missing=required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing annual columns {sorted(missing)}")
    if len(annual)!=1480 or annual["node_id"].nunique()!=71:
        raise RuntimeError("Tampa annual panel identity drift")

    trans=build_transitions(annual)
    if len(trans)==0:
        raise RuntimeError("no condition-eligible consecutive transitions")

    p_freq,primary=score(
        trans,
        "target_focal_frequency",
        C["primary_outcome"]["clip"],
        True,
        SEED,
    )
    s_freq,sens2016=score(
        trans,
        "target_focal_frequency",
        C["primary_outcome"]["clip"],
        False,
        SEED+1,
    )
    p_bb,secondary=score(
        trans,
        "target_bb_cover_mean_all_points",
        C["secondary_outcome"]["clip"],
        True,
        SEED+2,
    )

    status=(
        "condition_leading_information_supported"
        if primary["support"].get("supported",False)
        else "condition_leading_information_not_supported"
        if primary["support"].get("estimable",False)
        else "condition_leading_information_nonestimable"
    )

    result={
        "schema":"tampa.condition_leads_thinning_v1.result",
        "status":status,
        "contract":"results/condition_leads_thinning_v1_contract.json",
        "registry":{
            "condition_eligible_consecutive_transitions":int(len(trans)),
            "nodes":int(trans["node_id"].nunique()),
            "target_year_range":[int(trans["target_year"].min()),int(trans["target_year"].max())],
        },
        "primary_frequency":primary,
        "sensitivity_include_2016":sens2016,
        "secondary_braun_blanquet":secondary,
        "interpretation":(
            C["interpretation"]["supported"]
            if status=="condition_leading_information_supported"
            else C["interpretation"]["unsupported"]
        ),
        "claim_boundary":C["claim_boundary"],
    }

    trans.to_csv(outdir/"condition_leads_thinning_transitions.csv",index=False)
    p_freq.to_csv(outdir/"condition_leads_thinning_frequency_primary_year_scores.csv",index=False)
    s_freq.to_csv(outdir/"condition_leads_thinning_frequency_with2016_year_scores.csv",index=False)
    p_bb.to_csv(outdir/"condition_leads_thinning_bb_primary_year_scores.csv",index=False)
    (outdir/"condition_leads_thinning_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"
"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_condition_leads_thinning"))
    p.add_argument("--out",type=Path,default=Path("results/generated_condition_leads_thinning"))
    a=p.parse_args()
    main(a.input,a.out)
