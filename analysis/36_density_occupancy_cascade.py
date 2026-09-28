#!/usr/bin/env python3
"""Strict walk-forward test of a density-to-occupancy state cascade in Tampa Thalassia."""
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
C=json.loads((ROOT/"results/density_occupancy_cascade_v1_contract.json").read_text())
P=C["primary_model"]; S=C["support_rule"]

TARGET_YEARS=list(range(int(P["candidate_target_years"][0]),int(P["candidate_target_years"][1])+1))
MIN_TRAIN=int(P["minimum_train_rows"])
MIN_TRAIN_YEARS=int(P["minimum_train_years"])
MIN_TEST=int(P["minimum_test_rows_per_target_year"])
MIN_SCORED=int(P["minimum_scored_target_years"])
PERM_REPS=int(S["signflip_replicates"])
SEED=int(S["random_seed"])

CONDITIONS={
    "shoot_density":{
        "column":"shoot_density_mean_m2",
        "measurements":"shoot_measurements",
        "primary":True,
    },
    "blade_length":{
        "column":"blade_length_mean_mm",
        "measurements":"blade_measurements",
        "primary":False,
    },
}


def build_transitions(annual:pd.DataFrame,condition_col:str,measurement_col:str)->pd.DataFrame:
    rows=[]
    for node,g in annual.sort_values(["node_id","year"]).groupby("node_id"):
        recs=g.to_dict("records")
        for a,b in zip(recs[:-1],recs[1:]):
            sy=int(a["year"]); ty=int(b["year"])
            if ty!=sy+1:
                continue
            vals=[
                a.get("focal_frequency"),a.get("bb_cover_mean_all_points"),
                a.get(condition_col),b.get("focal_frequency"),
                a.get("visits"),a.get(measurement_col),
            ]
            if any(pd.isna(v) for v in vals):
                continue
            if str(a["water_body"])!=str(b["water_body"]):
                raise RuntimeError(f"water-body drift within stable node {node} {sy}->{ty}")
            rows.append({
                "node_id":str(node),
                "water_body":str(a["water_body"]),
                "source_year":sy,
                "target_year":ty,
                "source_frequency":float(a["focal_frequency"]),
                "source_bb":float(a["bb_cover_mean_all_points"]),
                "source_condition":float(a[condition_col]),
                "log_source_visits":float(np.log1p(float(a["visits"]))),
                "log_source_condition_measurements":float(np.log1p(float(a[measurement_col]))),
                "target_frequency":float(b["focal_frequency"]),
            })
    return pd.DataFrame(rows).sort_values(["target_year","node_id"]).reset_index(drop=True)


def make_model(numeric:list[str]):
    cats=["water_body","node_id"]
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),cats),
        ("num",StandardScaler(),numeric),
    ])
    return make_pipeline(pre,Ridge(alpha=1.0))


def fit_predict(train:pd.DataFrame,test:pd.DataFrame,numeric:list[str],with_condition:bool):
    cats=["water_body","node_id"]
    model=make_model(numeric)
    model.fit(train[cats+numeric],train["target_frequency"].to_numpy(float))
    pred=np.clip(np.asarray(model.predict(test[cats+numeric]),dtype=float),0.0,1.0)
    coef=None
    if with_condition:
        pre=model.named_steps["columntransformer"]
        ridge=model.named_steps["ridge"]
        names=list(pre.get_feature_names_out())
        key="num__source_condition"
        if key not in names:
            raise RuntimeError(f"source_condition coefficient not found: {names[-8:]}")
        coef=float(np.asarray(ridge.coef_,dtype=float)[names.index(key)])
    return pred,coef


def signflip(delta:np.ndarray,seed:int)->float:
    d=np.asarray(delta,dtype=float)
    obs=float(d.mean())
    rng=np.random.default_rng(seed)
    count=0
    remaining=PERM_REPS
    while remaining:
        n=min(5000,remaining)
        signs=rng.choice(np.asarray([-1.0,1.0]),size=(n,len(d)),replace=True)
        vals=(signs*d[None,:]).mean(axis=1)
        count+=int(np.sum(vals<=obs+1e-15))
        remaining-=n
    return float((count+1)/(PERM_REPS+1))


def support(years:pd.DataFrame,seed:int)->dict:
    if len(years)<MIN_SCORED:
        return {
            "estimable":False,
            "scored_target_years":int(len(years)),
            "supported":False,
        }
    delta=years["augmented_mae"].to_numpy(float)-years["baseline_mae"].to_numpy(float)
    p=signflip(delta,seed)
    need=math.ceil(float(S["minimum_win_fraction"])*len(delta))
    wins=int((delta<0).sum())
    coeff=years["condition_coefficient"].to_numpy(float)
    positive=int((coeff>0).sum())
    coef_need=math.ceil(0.60*len(coeff))
    supported=bool(
        wins>=need
        and float(np.median(delta))<0
        and p<float(S["one_sided_signflip_p_lt"])
        and positive>=coef_need
        and float(np.median(coeff))>0
    )
    return {
        "estimable":True,
        "scored_target_years":int(len(years)),
        "wins":wins,
        "losses":int((delta>0).sum()),
        "ties":int((delta==0).sum()),
        "mean_delta_augmented_minus_baseline":float(delta.mean()),
        "median_delta_augmented_minus_baseline":float(np.median(delta)),
        "signflip_p":p,
        "positive_condition_coefficient_years":positive,
        "coefficient_positive_fraction":float(positive/len(coeff)),
        "median_standardized_condition_coefficient":float(np.median(coeff)),
        "supported":supported,
    }


def evaluate(frame:pd.DataFrame,seed:int):
    base_num=[
        "target_year","source_frequency","source_bb",
        "log_source_visits","log_source_condition_measurements",
    ]
    aug_num=base_num+["source_condition"]
    yearly=[]
    for y in TARGET_YEARS:
        train=frame[frame["target_year"]<y].copy()
        test=frame[frame["target_year"]==y].copy()
        if len(train)<MIN_TRAIN or train["target_year"].nunique()<MIN_TRAIN_YEARS or len(test)<MIN_TEST:
            continue
        p0,_=fit_predict(train,test,base_num,False)
        p1,coef=fit_predict(train,test,aug_num,True)
        yy=test["target_frequency"].to_numpy(float)
        yearly.append({
            "target_year":int(y),
            "n_test":int(len(test)),
            "baseline_mae":float(mean_absolute_error(yy,p0)),
            "augmented_mae":float(mean_absolute_error(yy,p1)),
            "condition_coefficient":float(coef),
        })
    ys=pd.DataFrame(yearly)
    summary={
        "transition_rows":int(len(frame)),
        "nodes":int(frame["node_id"].nunique()) if len(frame) else 0,
        "target_year_range":(
            [int(ys["target_year"].min()),int(ys["target_year"].max())] if len(ys) else None
        ),
        "baseline_mean_mae":float(ys["baseline_mae"].mean()) if len(ys) else None,
        "augmented_mean_mae":float(ys["augmented_mae"].mean()) if len(ys) else None,
        "support":support(ys,seed),
    }
    return ys,summary


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")
    required={
        "node_id","year","water_body","visits",
        "focal_frequency","bb_cover_mean_all_points",
        "shoot_density_mean_m2","shoot_measurements",
        "blade_length_mean_mm","blade_measurements",
    }
    missing=required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"annual panel missing columns: {sorted(missing)}")
    if len(annual)!=1480 or annual["node_id"].nunique()!=71:
        raise RuntimeError("Tampa annual panel identity drift")

    results={}
    for i,(name,spec) in enumerate(CONDITIONS.items()):
        frame=build_transitions(annual,spec["column"],spec["measurements"])
        ys,summary=evaluate(frame,SEED+i)
        frame.to_csv(outdir/f"density_cascade_{name}_transitions.csv",index=False)
        ys.to_csv(outdir/f"density_cascade_{name}_year_scores.csv",index=False)
        results[name]={
            "primary":bool(spec["primary"]),
            **summary,
        }

    primary=results["shoot_density"]["support"]
    status=(
        "shoot_density_leads_frequency"
        if primary.get("supported",False)
        else "density_occupancy_cascade_not_supported"
        if primary.get("estimable",False)
        else "density_occupancy_cascade_nonestimable"
    )

    result={
        "schema":"tampa.density_occupancy_cascade_v1.result",
        "status":status,
        "contract":"results/density_occupancy_cascade_v1_contract.json",
        "target":"next-year focal_frequency",
        "results":results,
        "interpretation":(
            C["interpretation_map"]["supported"]
            if status=="shoot_density_leads_frequency"
            else C["interpretation_map"]["unsupported"]
        ),
        "claim_boundary":C["claim_boundary"],
    }
    (outdir/"density_occupancy_cascade_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_density_cascade"))
    p.add_argument("--out",type=Path,default=Path("results/generated_density_cascade"))
    a=p.parse_args()
    main(a.input,a.out)
