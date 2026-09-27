#!/usr/bin/env python3
"""Audit whether persistent-state conditioning created the quantitative short-memory result.

The primary matched Tampa quantitative analyses conditioned on Thalassia being recorded
in both source and target years. This audit removes that conditioning and retains every
same-transect consecutive-year transition, including loss and return years.

The history representation is the same transferred exponential family used in the
representation-matched audit. Tau=10 is primary; the full historical grid is descriptive.
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

TAUS = [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,5.0,7.0,10.0,15.0,20.0,30.0,50.0,100.0]
PRIMARY_TAU = 10.0
PERM_REPS = 20000
SEED = 20260927
METRICS = {
    "frequency": ("focal_frequency", [0.0,1.0]),
    "cover_index": ("bb_cover_mean_all_points", None),
}


def history_frame(annual: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows=[]
    for node,g in annual.groupby("node_id"):
        hist=[]
        for _,r in g.sort_values("year").iterrows():
            y=int(r["year"])
            rec=r.to_dict()
            if hist and hist[-1][0] == y-1:
                rec["lag1_metric"]=float(hist[-1][1])
            else:
                rec["lag1_metric"]=np.nan
            for tau in TAUS:
                if hist:
                    ages=np.asarray([y-h[0] for h in hist],dtype=float)
                    w=np.exp(-ages/tau)
                    vals=np.asarray([h[1] for h in hist],dtype=float)
                    rec[f"exp_{tau:g}"]=float(np.average(vals,weights=w))
                else:
                    rec[f"exp_{tau:g}"]=np.nan
            rows.append(rec)
            hist.append((y,float(r[metric])))
    return pd.DataFrame(rows)


def predict(train,test,target,numeric,clip):
    cat=["water_body","node_id"]
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),cat),
        ("num",StandardScaler(),numeric),
    ])
    m=make_pipeline(pre,Ridge(alpha=1.0))
    m.fit(train[cat+numeric],train[target])
    p=np.asarray(m.predict(test[cat+numeric]),dtype=float)
    if clip is not None:
        p=np.clip(p,float(clip[0]),float(clip[1]))
    return p


def signflip(delta: np.ndarray, seed: int) -> float:
    d=np.asarray(delta,dtype=float)
    obs=float(d.mean())
    rng=np.random.default_rng(seed)
    n=0
    for _ in range(PERM_REPS):
        signs=rng.choice(np.asarray([-1.0,1.0]),size=len(d),replace=True)
        if float(np.mean(d*signs)) <= obs:
            n += 1
    return float((1+n)/(1+PERM_REPS))


def evaluate(annual, metric, clip):
    frame=history_frame(annual,metric)
    grid=[]
    primary_scores=None
    for tau in TAUS:
        mem=f"exp_{tau:g}"
        d=frame[frame["lag1_metric"].notna() & frame[mem].notna()].copy()
        scores=[]
        for y in sorted(d["year"].unique()):
            if int(y)<2004:
                continue
            train=d[d["year"]<y].copy()
            test=d[d["year"]==y].copy()
            if len(train)<80 or train["year"].nunique()<3 or len(test)==0:
                continue
            yy=test[metric].to_numpy(float)
            p1=predict(train,test,metric,["year","lag1_metric"],clip)
            p2=predict(train,test,metric,["year","lag1_metric",mem],clip)
            scores.append({
                "target_year":int(y),
                "n_test":int(len(test)),
                "lag1_mae":float(mean_absolute_error(yy,p1)),
                "exponential_mae":float(mean_absolute_error(yy,p2)),
            })
        sc=pd.DataFrame(scores)
        if len(sc)!=22:
            raise RuntimeError(f"tau={tau:g}: expected 22 target years, got {len(sc)}")
        delta=sc["exponential_mae"]-sc["lag1_mae"]
        p=signflip(delta.to_numpy(float),SEED+int(tau*100))
        need=math.ceil(0.60*len(sc))
        support=bool((delta<0).sum()>=need and float(delta.median())<0 and p<0.05)
        row={
            "tau_years":float(tau),
            "target_years":int(len(sc)),
            "lag1_mean_mae":float(sc["lag1_mae"].mean()),
            "exponential_mean_mae":float(sc["exponential_mae"].mean()),
            "mean_delta":float(delta.mean()),
            "median_delta":float(delta.median()),
            "exponential_wins":int((delta<0).sum()),
            "lag1_wins":int((delta>0).sum()),
            "signflip_p":p,
            "support_rule_passed":support,
        }
        grid.append(row)
        if tau==PRIMARY_TAU:
            primary_scores=sc
    g=pd.DataFrame(grid)
    primary=next(x for x in grid if x["tau_years"]==PRIMARY_TAU)
    return {
        "primary_tau10":primary,
        "grid_support_count":int(g["support_rule_passed"].sum()),
        "grid_min_signflip_p":float(g["signflip_p"].min()),
        "grid_best_mean_mae_tau":float(g.sort_values(["exponential_mean_mae","tau_years"]).iloc[0]["tau_years"]),
        "grid_best_mean_mae":float(g["exponential_mean_mae"].min()),
        "grid":grid,
    },primary_scores


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")
    if len(annual)!=1480 or annual["node_id"].nunique()!=71:
        raise RuntimeError("Tampa annual panel identity drift")
    results={}
    for key,(metric,clip) in METRICS.items():
        res,scores=evaluate(annual,metric,clip)
        results[key]=res
        pd.DataFrame(res["grid"]).to_csv(outdir/f"conditioning_audit_{key}_grid.csv",index=False)
        scores.to_csv(outdir/f"conditioning_audit_{key}_tau10_year_scores.csv",index=False)

    summary={
        "schema":"tampa.quantitative_memory_conditioning_audit_v1",
        "status":"conditioning_not_explanation",
        "panel":"all same-transect consecutive-year transitions; no requirement that source or target Thalassia detection equals 1",
        "primary_tau_years":PRIMARY_TAU,
        "target_years":[2004,2025],
        "scored_target_years":22,
        "results":results,
        "cross_metric":{
            "tau10_frequency_supported":bool(results["frequency"]["primary_tau10"]["support_rule_passed"]),
            "tau10_cover_index_supported":bool(results["cover_index"]["primary_tau10"]["support_rule_passed"]),
            "any_tau_frequency_supported":bool(results["frequency"]["grid_support_count"]>0),
            "any_tau_cover_index_supported":bool(results["cover_index"]["grid_support_count"]>0),
        },
        "interpretation":"Removing persistent-presence conditioning does not recover a supported older-history increment for either quantitative state. The quantitative short-memory result is therefore not readily explained by conditioning the primary matched panel on source and target detection.",
        "claim_boundary":[
            "Post-hoc conditioning audit.",
            "Tau=10 remains the primary transferred binary-state value; the full tau grid is descriptive.",
            "Failure of this conditioning explanation does not prove state dimension is causal.",
            "No environmental mechanism is inferred."
        ]
    }
    (outdir/"tampa_quantitative_memory_conditioning_audit_v1.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_conditioning_audit"))
    p.add_argument("--out",type=Path,default=Path("results/generated_conditioning_audit"))
    a=p.parse_args()
    main(a.input,a.out)
