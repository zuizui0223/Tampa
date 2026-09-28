#!/usr/bin/env python3
"""Held-out-node test of measured Tampa site-template components.

Tests whether depth and sediment summaries explain persistent node-level Thalassia
state beyond broad water-body identity and geographic coordinates.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/site_template_outcome_v1_contract.json").read_text())
MIN_YEARS=int(C["outcome_construction"]["minimum_annual_observations_per_node"])
SEED=int(C["scoring"]["support_rule"]["random_seed"])
PERM_REPS=int(C["scoring"]["support_rule"]["signflip_replicates"])

OUTCOMES={
  "detection_prevalence":{"column":"detected","clip":[0.0,1.0],"primary":True},
  "focal_frequency":{"column":"focal_frequency","clip":[0.0,1.0],"primary":True},
  "bb_cover_index":{"column":"bb_cover_mean_all_points","clip":[0.0,5.0],"primary":True},
  "blade_length":{"column":"blade_length_mean_mm","clip":[0.0,None],"primary":False},
  "shoot_density":{"column":"shoot_density_mean_m2","clip":[0.0,None],"primary":False},
}

MODELS=C["models"]

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
    p=signflip(d,seed)
    need=math.ceil(float(C["scoring"]["support_rule"]["minimum_win_fraction"])*len(d))
    return {
      "nodes":int(len(d)),
      "wins":int((d<0).sum()),
      "losses":int((d>0).sum()),
      "ties":int((d==0).sum()),
      "mean_delta":float(d.mean()),
      "median_delta":float(np.median(d)),
      "signflip_p":p,
      "supported":bool((d<0).sum()>=need and float(np.median(d))<0 and p<float(C["scoring"]["support_rule"]["one_sided_signflip_p_lt"]))
    }

def build_node_outcome(annual,target):
    g=(annual.groupby("node_id",as_index=False)
       .agg(water_body=("water_body","first"),longitude=("longitude","first"),latitude=("latitude","first"),
            outcome=(target,"mean"),n_years=(target,"count")))
    return g[g["n_years"]>=MIN_YEARS].copy()

def make_model(categorical,numeric):
    pre=ColumnTransformer([
      ("cat",OneHotEncoder(handle_unknown="ignore"),categorical),
      ("num",StandardScaler(),numeric),
    ])
    return make_pipeline(pre,Ridge(alpha=1.0))

def apply_clip(pred,clip):
    p=np.asarray(pred,dtype=float)
    if clip is None:
        return p
    lo=clip[0]; hi=clip[1]
    if lo is not None: p=np.maximum(p,float(lo))
    if hi is not None: p=np.minimum(p,float(hi))
    return p

def loon(frame,model_spec,clip):
    cats=list(model_spec["categorical"])
    nums=list(model_spec["numeric"])
    preds=np.empty(len(frame),dtype=float)
    for k in range(len(frame)):
        train=frame.drop(frame.index[k])
        test=frame.iloc[[k]]
        m=make_model(cats,nums)
        m.fit(train[cats+nums],train["outcome"].to_numpy(float))
        preds[k]=float(apply_clip(m.predict(test[cats+nums]),clip)[0])
    return preds

def analyze(annual,template,key,spec,outcome_index):
    node=build_node_outcome(annual,spec["column"])
    frame=node.merge(template,on=["node_id","water_body","longitude","latitude"],how="inner",validate="one_to_one")
    if len(frame)!=len(node):
        raise RuntimeError(f"{key}: physical template missing for eligible nodes")
    if frame[["depth_median_m","depth_iqr_m","sediment_modal","sediment_modal_fraction","sediment_entropy"]].isna().any().any():
        raise RuntimeError(f"{key}: missing physical template value")

    preds={}
    errors={}
    for name,ms in MODELS.items():
        p=loon(frame,ms,spec["clip"])
        preds[name]=p
        errors[name]=np.abs(frame["outcome"].to_numpy(float)-p)

    y=frame["outcome"].to_numpy(float)
    model_scores={}
    for name in MODELS:
        model_scores[name]={
          "mae":float(mean_absolute_error(y,preds[name])),
          "heldout_r2":float(r2_score(y,preds[name])),
        }

    comparisons={}
    for j,name in enumerate(["depth","sediment","measured_template"]):
        delta=errors[name]-errors["spatial_reference"]
        comparisons[name+"_vs_spatial"]=support(delta,SEED+outcome_index*10+j)

    out=frame[["node_id","water_body","outcome","n_years"]].copy()
    for name in MODELS:
        out[name+"_prediction"]=preds[name]
        out[name+"_abs_error"]=errors[name]

    return out,{
      "eligible_nodes":int(len(frame)),
      "minimum_years":int(frame["n_years"].min()),
      "median_years":float(frame["n_years"].median()),
      "model_scores":model_scores,
      "comparisons":comparisons,
      "template_supported":bool(comparisons["measured_template_vs_spatial"]["supported"])
    }

def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")
    template=pd.read_csv(input_dir/"site_template_node_preflight.csv")
    if len(annual)!=1480 or annual["node_id"].nunique()!=71:
        raise RuntimeError("annual panel identity drift")
    if len(template)!=71 or template["node_id"].nunique()!=71:
        raise RuntimeError("site-template preflight identity drift")
    if int((template["depth_n"]>0).sum())!=71 or int((template["sediment_point_events"]>0).sum())!=71:
        raise RuntimeError("physical template coverage drift")

    results={}
    for i,(key,spec) in enumerate(OUTCOMES.items()):
        rows,summary=analyze(annual,template,key,spec,i)
        rows.to_csv(outdir/f"site_template_{key}_loon.csv",index=False)
        results[key]=summary

    primary=[k for k,v in OUTCOMES.items() if v["primary"]]
    n_supported=sum(bool(results[k]["template_supported"]) for k in primary)
    broad=bool(n_supported>=2)
    result={
      "schema":"tampa.site_template_outcome_v1.result",
      "status":"measured_template_broadly_supported" if broad else ("measured_template_mixed" if n_supported else "measured_template_not_supported"),
      "preflight":"results/site_template_preflight_v1.json",
      "contract":"results/site_template_outcome_v1_contract.json",
      "primary_outcomes":primary,
      "primary_template_supported_count":int(n_supported),
      "primary_template_support_required":2,
      "broad_support":broad,
      "results":results,
      "interpretation":(
        "Measured depth and sediment recover held-out persistent site-state information beyond water-body identity and coordinates."
        if broad else
        "Depth and sediment alone do not provide broad held-out recovery of the persistent site effect across the primary Thalassia state dimensions; important site-template components remain unmeasured."
      ),
      "claim_boundary":C["claim_boundary"]
    }
    (outdir/"site_template_outcome_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_site_template"))
    p.add_argument("--out",type=Path,default=Path("results/generated_site_template"))
    a=p.parse_args(); main(a.input,a.out)
