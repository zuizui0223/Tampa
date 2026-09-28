#!/usr/bin/env python3
"""Post-hoc audit: does older history proxy persistent site-specific quality?

The Tampa binary memory analysis originally used longitude, latitude, year and
water-body but not stable node identity. Later quantitative analyses included
node identity. This creates a reference-saturation confound.

This audit toggles exactly one reference component: stable node_id. Within each
response type, learner, loss, row set, lag-1 feature, exponential-memory family,
and target-year split remain fixed.

Responses:
- detected: LogisticRegression, binary log loss (reproduces the frozen binary line);
- focal_frequency: Ridge, MAE;
- Braun-Blanquet all-point index: Ridge, MAE.

Tau=10 is primary because it is frozen by the binary result. The historical tau
grid is descriptive and used to count how many memory scales survive node-ID
reference saturation.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TAUS = [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,5.0,7.0,10.0,15.0,20.0,30.0,50.0,100.0]
PRIMARY_TAU = 10.0
PERM_REPS = 20000
SEED = 20260927
TARGET_YEARS = list(range(2004, 2026))

OUTCOMES = {
    "binary_detected": {
        "column": "detected",
        "learner": "logistic",
        "loss": "log_loss",
        "clip": [0.0,1.0],
    },
    "frequency": {
        "column": "focal_frequency",
        "learner": "ridge",
        "loss": "mae",
        "clip": [0.0,1.0],
    },
    "cover_index": {
        "column": "bb_cover_mean_all_points",
        "learner": "ridge",
        "loss": "mae",
        "clip": None,
    },
}


def history_frame(annual: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows=[]
    for node,g in annual.groupby("node_id"):
        hist=[]
        for _,r in g.sort_values("year").iterrows():
            year=int(r["year"])
            rec=r.to_dict()
            if hist and hist[-1][0] == year-1:
                rec["lag1_metric"]=float(hist[-1][1])
            else:
                rec["lag1_metric"]=np.nan
            for tau in TAUS:
                if hist:
                    ages=np.asarray([year-old_year for old_year,_ in hist],dtype=float)
                    weights=np.exp(-ages/tau)
                    vals=np.asarray([value for _,value in hist],dtype=float)
                    rec[f"exp_{tau:g}"]=float(np.average(vals,weights=weights))
                else:
                    rec[f"exp_{tau:g}"]=np.nan
            rows.append(rec)
            hist.append((year,float(r[metric])))
    return pd.DataFrame(rows)


def predictor(train, test, target, numeric, use_node_id, learner, clip):
    cats=["water_body"] + (["node_id"] if use_node_id else [])
    pre=ColumnTransformer([
        ("num",StandardScaler(),numeric),
        ("cat",OneHotEncoder(handle_unknown="ignore"),cats),
    ])
    if learner=="logistic":
        model=make_pipeline(pre,LogisticRegression(max_iter=1500,C=1.0))
        model.fit(train[numeric+cats],train[target].astype(int))
        pred=model.predict_proba(test[numeric+cats])[:,1]
    elif learner=="ridge":
        model=make_pipeline(pre,Ridge(alpha=1.0))
        model.fit(train[numeric+cats],train[target].astype(float))
        pred=np.asarray(model.predict(test[numeric+cats]),dtype=float)
    else:
        raise RuntimeError(f"unknown learner {learner}")
    if clip is not None:
        pred=np.clip(pred,float(clip[0]),float(clip[1]))
    return np.asarray(pred,dtype=float)


def score(y, pred, loss):
    if loss=="log_loss":
        return float(log_loss(y.astype(int),pred,labels=[0,1]))
    if loss=="mae":
        return float(mean_absolute_error(y.astype(float),pred))
    raise RuntimeError(f"unknown loss {loss}")


def signflip(delta: np.ndarray, seed: int) -> float:
    d=np.asarray(delta,dtype=float)
    obs=float(d.mean())
    rng=np.random.default_rng(seed)
    count=0
    for _ in range(PERM_REPS):
        signs=rng.choice(np.asarray([-1.0,1.0]),size=len(d),replace=True)
        if float(np.mean(d*signs)) <= obs:
            count += 1
    return float((1+count)/(1+PERM_REPS))


def evaluate_reference(frame, spec, use_node_id, outcome_index):
    target=spec["column"]
    learner=spec["learner"]
    loss=spec["loss"]
    clip=spec["clip"]
    rows=[]
    for tau_index,tau in enumerate(TAUS):
        mem=f"exp_{tau:g}"
        d=frame[frame["lag1_metric"].notna() & frame[mem].notna()].copy()
        yearly=[]
        for y in TARGET_YEARS:
            train=d[d["year"]<y].copy()
            test=d[d["year"]==y].copy()
            if len(test)==0:
                raise RuntimeError(f"{target}: no test rows in {y}")
            if learner=="logistic" and train[target].nunique()<2:
                raise RuntimeError(f"{target}: one-class training in {y}")
            base_numeric=["longitude","latitude","year","lag1_metric"]
            p1=predictor(train,test,target,base_numeric,use_node_id,learner,clip)
            p2=predictor(train,test,target,base_numeric+[mem],use_node_id,learner,clip)
            yy=test[target].to_numpy()
            yearly.append({
                "target_year":int(y),
                "lag1_score":score(yy,p1,loss),
                "history_score":score(yy,p2,loss),
            })
        ys=pd.DataFrame(yearly)
        delta=ys["history_score"]-ys["lag1_score"]
        p=signflip(
            delta.to_numpy(float),
            SEED + outcome_index*100000 + (10000 if use_node_id else 0) + tau_index
        )
        need=math.ceil(0.60*len(ys))
        support=bool(
            int((delta<0).sum())>=need
            and float(delta.median())<0
            and p<0.05
        )
        rows.append({
            "tau_years":float(tau),
            "target_years":int(len(ys)),
            "lag1_mean_score":float(ys["lag1_score"].mean()),
            "history_mean_score":float(ys["history_score"].mean()),
            "mean_history_minus_lag1":float(delta.mean()),
            "median_history_minus_lag1":float(delta.median()),
            "history_wins":int((delta<0).sum()),
            "lag1_wins":int((delta>0).sum()),
            "ties":int((delta==0).sum()),
            "signflip_p":p,
            "support_rule_passed":support,
        })
    grid=pd.DataFrame(rows)
    primary=next(r for r in rows if r["tau_years"]==PRIMARY_TAU)
    return {
        "reference":"with_node_id" if use_node_id else "without_node_id",
        "primary_tau10":primary,
        "grid_support_count":int(grid["support_rule_passed"].sum()),
        "grid_best_score_tau":float(
            grid.sort_values(["history_mean_score","tau_years"]).iloc[0]["tau_years"]
        ),
        "grid_best_history_mean_score":float(grid["history_mean_score"].min()),
        "grid_min_signflip_p":float(grid["signflip_p"].min()),
        "grid":rows,
    }


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")
    required={
        "node_id","year","water_body","longitude","latitude",
        "detected","focal_frequency","bb_cover_mean_all_points"
    }
    missing=required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing annual columns {sorted(missing)}")
    if len(annual)!=1480 or annual["node_id"].nunique()!=71:
        raise RuntimeError("Tampa annual panel identity drift")

    results={}
    for outcome_index,(name,spec) in enumerate(OUTCOMES.items()):
        metric=spec["column"]
        if annual[metric].isna().any():
            raise RuntimeError(f"unexpected missing values in {metric}")
        frame=history_frame(annual,metric)
        no_node=evaluate_reference(frame,spec,False,outcome_index)
        with_node=evaluate_reference(frame,spec,True,outcome_index)
        results[name]={
            "learner":spec["learner"],
            "loss":spec["loss"],
            "without_node_id":no_node,
            "with_node_id":with_node,
            "tau10_support_removed_by_node_id":bool(
                no_node["primary_tau10"]["support_rule_passed"]
                and not with_node["primary_tau10"]["support_rule_passed"]
            ),
            "grid_support_reduction":int(
                no_node["grid_support_count"]-with_node["grid_support_count"]
            ),
        }
        pd.DataFrame(no_node["grid"]).to_csv(
            outdir/f"site_identity_{name}_without_node_grid.csv",index=False
        )
        pd.DataFrame(with_node["grid"]).to_csv(
            outdir/f"site_identity_{name}_with_node_grid.csv",index=False
        )

    binary=results["binary_detected"]
    frequency=results["frequency"]
    cover=results["cover_index"]

    proxy_pattern=bool(
        binary["tau10_support_removed_by_node_id"]
        and frequency["tau10_support_removed_by_node_id"]
        and binary["with_node_id"]["grid_support_count"]==0
        and frequency["with_node_id"]["grid_support_count"]==0
        and cover["with_node_id"]["grid_support_count"]==0
    )

    summary={
        "schema":"tampa.site_identity_memory_audit_v1",
        "status":"stable_site_reference_absorbs_older_history" if proxy_pattern else "mixed_site_identity_moderation",
        "panel":"all same-transect consecutive-year annual states; identical target years 2004-2025",
        "reference_contrast":{
            "without_node_id":"longitude + latitude + water_body + year + lag1",
            "with_node_id":"same reference plus stable categorical node_id",
            "only_reference_difference":"node_id"
        },
        "primary_tau_years":PRIMARY_TAU,
        "results":results,
        "primary_proxy_pattern_passed":proxy_pattern,
        "interpretation":(
            "Older-history value is strongly reference dependent. In both binary recorded state "
            "and focal frequency, tau=10 history is supported when the reference lacks stable node "
            "identity but loses support when node identity is added; no outcome has any supported "
            "tau once node identity is present. This is consistent with historical state acting "
            "partly as a proxy for persistent site-specific ecological quality that is not captured "
            "by coordinates and bay segment, rather than uniquely measuring long temporal memory."
            if proxy_pattern else
            "Stable node identity moderates older-history value, but the frozen proxy pattern is mixed."
        ),
        "claim_boundary":[
            "Post-hoc reference-saturation audit.",
            "Node identity is a saturated repeated-site reference, not an identified habitat mechanism.",
            "The result does not tell which persistent ecological attributes differ among sites.",
            "History may still contain temporal information even when its formal support rule fails after node identity is added.",
            "Do not reinterpret node identity as a causal site effect."
        ]
    }
    (outdir/"tampa_site_identity_memory_audit_v1.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_site_identity"))
    p.add_argument("--out",type=Path,default=Path("results/generated_site_identity"))
    a=p.parse_args()
    main(a.input,a.out)
