#!/usr/bin/env python3
"""Strict walk-forward test of pre-survey benthic light and Thalassia condition."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/benthic_light_condition_v1_contract.json").read_text())
SEED=int(C["support_rule"]["random_seed"])
PERM_REPS=int(C["support_rule"]["signflip_replicates"])
Y0,Y1=[int(x) for x in C["validation"]["candidate_target_years"]]
TARGET_YEARS=list(range(Y0,Y1+1))
MIN_TRAIN=int(C["validation"]["minimum_train_rows"])
MIN_TRAIN_YEARS=int(C["validation"]["minimum_train_years"])
MIN_TEST=int(C["validation"]["minimum_test_rows_per_target_year"])
MIN_SCORED=int(C["validation"]["minimum_scored_target_years_per_outcome"])

OUTCOMES={
    "blade_length_mean_mm":{"clip":[0.0,None],"primary":True},
    "shoot_density_mean_m2":{"clip":[0.0,None],"primary":True},
    "focal_frequency":{"clip":[0.0,1.0],"primary":False},
    "bb_cover_mean_all_points":{"clip":[0.0,5.0],"primary":False},
}

def signflip(delta,seed):
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

def support(delta,seed):
    d=np.asarray(delta,dtype=float)
    if len(d)<MIN_SCORED:
        return {"estimable":False,"target_years":int(len(d)),"supported":False}
    p=signflip(d,seed)
    need=math.ceil(float(C["support_rule"]["minimum_win_fraction"])*len(d))
    return {
      "estimable":True,
      "target_years":int(len(d)),
      "wins":int((d<0).sum()),
      "losses":int((d>0).sum()),
      "ties":int((d==0).sum()),
      "mean_delta":float(d.mean()),
      "median_delta":float(np.median(d)),
      "signflip_p":p,
      "supported":bool((d<0).sum()>=need and float(np.median(d))<0 and p<float(C["support_rule"]["one_sided_signflip_p_lt"]))
    }

def prepare(visits, exposure):
    expcols=[
      "unit_id","depth_median_m",
      "pre_6m_benthic_fraction_mean","pre_6m_secchi_mean","pre_6m_months",
      "pre_3m_benthic_fraction_mean","pre_3m_secchi_mean","pre_3m_months",
    ]
    d=visits.merge(exposure[expcols],on="unit_id",how="inner",validate="one_to_one")
    dt=pd.to_datetime(d["date"])
    doy=dt.dt.dayofyear.to_numpy(float)
    d["sin_doy"]=np.sin(2*np.pi*doy/365.25)
    d["cos_doy"]=np.cos(2*np.pi*doy/365.25)
    d["log_points"]=np.log1p(d["child_point_count"].astype(float))
    d["year"]=d["year"].astype(int)
    return d

def make_model(numeric):
    cats=["node_id","water_body"]
    pre=ColumnTransformer([
      ("cat",OneHotEncoder(handle_unknown="ignore"),cats),
      ("num",StandardScaler(),numeric),
    ])
    return make_pipeline(pre,Ridge(alpha=1.0))

def clip_pred(p,clip):
    x=np.asarray(p,dtype=float)
    if clip[0] is not None: x=np.maximum(x,float(clip[0]))
    if clip[1] is not None: x=np.minimum(x,float(clip[1]))
    return x

def score_window(frame,target,clip,window,seed):
    secchi=f"pre_{window}_secchi_mean"
    light=f"pre_{window}_benthic_fraction_mean"
    base_num=["year","sin_doy","cos_doy","log_points","depth_median_m",secchi]
    aug_num=base_num+[light]
    required=[target,*base_num,light,"node_id","water_body"]
    d=frame.dropna(subset=required).copy()
    years=[]
    for y in TARGET_YEARS:
        train=d[d["year"]<y].copy()
        test=d[d["year"]==y].copy()
        if len(train)<MIN_TRAIN or train["year"].nunique()<MIN_TRAIN_YEARS or len(test)<MIN_TEST:
            continue
        m0=make_model(base_num); m1=make_model(aug_num)
        cats=["node_id","water_body"]
        m0.fit(train[cats+base_num],train[target].to_numpy(float))
        m1.fit(train[cats+aug_num],train[target].to_numpy(float))
        p0=clip_pred(m0.predict(test[cats+base_num]),clip)
        p1=clip_pred(m1.predict(test[cats+aug_num]),clip)
        yy=test[target].to_numpy(float)
        years.append({
          "target_year":int(y),
          "n_test":int(len(test)),
          "baseline_mae":float(mean_absolute_error(yy,p0)),
          "benthic_light_mae":float(mean_absolute_error(yy,p1)),
        })
    ys=pd.DataFrame(years)
    if len(ys):
        delta=ys["benthic_light_mae"].to_numpy(float)-ys["baseline_mae"].to_numpy(float)
        sup=support(delta,seed)
        summary={
          "window":window,
          "eligible_rows":int(len(d)),
          "eligible_nodes":int(d["node_id"].nunique()),
          "scored_target_years":int(len(ys)),
          "target_year_range":[int(ys["target_year"].min()),int(ys["target_year"].max())],
          "baseline_mean_mae":float(ys["baseline_mae"].mean()),
          "benthic_light_mean_mae":float(ys["benthic_light_mae"].mean()),
          "support":sup,
        }
    else:
        summary={"window":window,"eligible_rows":int(len(d)),"eligible_nodes":int(d["node_id"].nunique()),"scored_target_years":0,"support":{"estimable":False,"target_years":0,"supported":False}}
    return ys,summary

def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    visits=pd.read_csv(input_dir/"quant_visit_panel.csv")
    exposure=pd.read_csv(input_dir/"benthic_light_visit_exposure_preflight.csv")
    if len(exposure)!=1236:
        raise RuntimeError(f"exposure registry drift {len(exposure)}")
    d=prepare(visits,exposure)
    if len(d)!=1236:
        raise RuntimeError(f"visit-exposure join drift {len(d)}")

    results={}
    for i,(target,spec) in enumerate(OUTCOMES.items()):
        primary_scores,primary=score_window(d,target,spec["clip"],"6m",SEED+i*100)
        sens_scores,sensitivity=score_window(d,target,spec["clip"],"3m",SEED+i*100+1)
        if len(primary_scores):
            primary_scores.to_csv(outdir/f"benthic_light_{target}_6m_year_scores.csv",index=False)
        if len(sens_scores):
            sens_scores.to_csv(outdir/f"benthic_light_{target}_3m_year_scores.csv",index=False)
        results[target]={
          "primary_outcome":bool(spec["primary"]),
          "primary_6m":primary,
          "sensitivity_3m":sensitivity,
        }

    primary_names=[k for k,v in OUTCOMES.items() if v["primary"]]
    primary_estimable=sum(bool(results[k]["primary_6m"]["support"].get("estimable",False)) for k in primary_names)
    primary_supported=sum(bool(results[k]["primary_6m"]["support"].get("supported",False)) for k in primary_names)
    status=(
      "primary_nonestimable" if primary_estimable<2 else
      "benthic_light_condition_supported" if primary_supported>=1 else
      "benthic_light_condition_not_supported"
    )
    result={
      "schema":"tampa.benthic_light_condition_v1.result",
      "status":status,
      "preflight":"results/benthic_light_exposure_preflight_v1.json",
      "contract":"results/benthic_light_condition_v1_contract.json",
      "joined_visits":int(len(d)),
      "nodes":int(d["node_id"].nunique()),
      "primary_estimable_outcomes":int(primary_estimable),
      "primary_supported_outcomes":int(primary_supported),
      "results":results,
      "interpretation":(
        "Pre-survey benthic-light dose adds supported heldout information for at least one primary plant-condition outcome beyond persistent node identity, survey context, depth and bulk Secchi."
        if status=="benthic_light_condition_supported" else
        "The simplified pre-survey benthic-light proxy does not add robust heldout information for the primary plant-condition outcomes beyond persistent node identity, survey context, depth and bulk Secchi."
        if status=="benthic_light_condition_not_supported" else
        "The frozen plant-condition test was not sufficiently estimable to classify the benthic-light hypothesis."
      ),
      "claim_boundary":C["claim_boundary"]
    }
    (outdir/"benthic_light_condition_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_benthic_light"))
    p.add_argument("--out",type=Path,default=Path("results/generated_benthic_light"))
    a=p.parse_args(); main(a.input,a.out)
