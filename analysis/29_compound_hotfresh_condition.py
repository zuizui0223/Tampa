#!/usr/bin/env python3
"""Walk-forward test of joint hot-fresh stress beyond marginal hot/fresh runs."""
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
C=json.loads((ROOT/"results/compound_hotfresh_condition_v1_contract.json").read_text())
Y0,Y1=[int(x) for x in C["transition_design"]["candidate_target_years"]]
YEARS=list(range(Y0,Y1+1))
SEED=int(C["support_rule"]["random_seed"])
PERM=int(C["support_rule"]["signflip_replicates"])
MIN_TRAIN=int(C["validation"]["minimum_train_rows"])
MIN_TRAIN_YEARS=int(C["validation"]["minimum_train_years"])
MIN_TEST=int(C["validation"]["minimum_test_rows"])
MIN_SCORED=int(C["validation"]["minimum_scored_target_years"])
PRIMARY=set(C["primary_outcomes"])
SEGMENT_MAP={str(k):str(v) for k,v in C["exposure_mapping"]["segment_map"].items()}

OUTCOMES={
  "blade_length_mean_mm":{"clip":[0.0,None]},
  "shoot_density_mean_m2":{"clip":[0.0,None]},
  "focal_frequency":{"clip":[0.0,1.0]},
  "bb_cover_mean_all_points":{"clip":[0.0,5.0]},
}

def signflip(delta,seed):
    d=np.asarray(delta,dtype=float)
    obs=float(d.mean())
    rng=np.random.default_rng(seed)
    count=0
    rem=PERM
    while rem:
        n=min(5000,rem)
        signs=rng.choice(np.asarray([-1.0,1.0]),size=(n,len(d)),replace=True)
        vals=(signs*d[None,:]).mean(axis=1)
        count+=int(np.sum(vals<=obs+1e-15))
        rem-=n
    return float((count+1)/(PERM+1))

def support(delta,seed,p_threshold):
    d=np.asarray(delta,dtype=float)
    if len(d)<MIN_SCORED:
        return {"estimable":False,"target_years":int(len(d)),"supported":False}
    p=signflip(d,seed)
    need=math.ceil(float(C["support_rule"]["minimum_win_fraction"])*len(d))
    return {
      "estimable":True,"target_years":int(len(d)),
      "wins":int((d<0).sum()),"losses":int((d>0).sum()),"ties":int((d==0).sum()),
      "mean_delta":float(d.mean()),"median_delta":float(np.median(d)),
      "signflip_p":p,"p_threshold":float(p_threshold),
      "supported":bool((d<0).sum()>=need and float(np.median(d))<0 and p<float(p_threshold))
    }

def exposure_wide(seg):
    req={"bay_segment","trnyr","stress_type","mean_max_run_days"}
    missing=req.difference(seg.columns)
    if missing:
        raise RuntimeError(f"exposure columns missing {sorted(missing)}")
    p=seg.pivot_table(index=["bay_segment","trnyr"],columns="stress_type",values="mean_max_run_days",aggfunc="first").reset_index()
    need={"tempcnt","salicnt","bothcnt"}
    missing=need.difference(p.columns)
    if missing:
        raise RuntimeError(f"stress types missing {sorted(missing)}")
    return p.rename(columns={"tempcnt":"hot_run_days","salicnt":"fresh_run_days","bothcnt":"hotfresh_run_days"})

def transitions(annual,target,expo):
    rows=[]
    a=annual[annual["water_body"].isin(SEGMENT_MAP)].copy()
    a["bay_segment"]=a["water_body"].map(SEGMENT_MAP)
    for node,g in a.sort_values(["node_id","year"]).groupby("node_id"):
        recs=g.to_dict("records")
        for src,tgt in zip(recs[:-1],recs[1:]):
            if int(tgt["year"])!=int(src["year"])+1:
                continue
            if pd.isna(src[target]) or pd.isna(tgt[target]):
                continue
            rows.append({
              "node_id":str(node),"water_body":str(tgt["water_body"]),
              "bay_segment":str(tgt["bay_segment"]),"target_year":int(tgt["year"]),
              "target":float(tgt[target]),"lag1_state":float(src[target])
            })
    d=pd.DataFrame(rows)
    d=d.merge(expo,left_on=["bay_segment","target_year"],right_on=["bay_segment","trnyr"],how="inner",validate="many_to_one")
    return d.drop(columns=["trnyr"]).sort_values(["target_year","node_id"]).reset_index(drop=True)

def model_predict(train,test,numeric,clip):
    cats=["node_id","water_body"]
    pre=ColumnTransformer([
      ("cat",OneHotEncoder(handle_unknown="ignore"),cats),
      ("num",StandardScaler(),numeric)
    ])
    m=make_pipeline(pre,Ridge(alpha=1.0))
    m.fit(train[cats+numeric],train["target"].to_numpy(float))
    p=np.asarray(m.predict(test[cats+numeric]),dtype=float)
    if clip[0] is not None:
        p=np.maximum(p,float(clip[0]))
    if clip[1] is not None:
        p=np.minimum(p,float(clip[1]))
    return p

def analyze(d,clip,seed,p_threshold):
    base=["target_year","lag1_state","hot_run_days","fresh_run_days"]
    aug=base+["hotfresh_run_days"]
    yr=[]
    for y in YEARS:
        tr=d[d["target_year"]<y].copy()
        te=d[d["target_year"]==y].copy()
        if len(tr)<MIN_TRAIN or tr["target_year"].nunique()<MIN_TRAIN_YEARS or len(te)<MIN_TEST:
            continue
        yv=te["target"].to_numpy(float)
        p0=model_predict(tr,te,base,clip)
        p1=model_predict(tr,te,aug,clip)
        yr.append({
          "target_year":int(y),"n_test":int(len(te)),
          "baseline_mae":float(mean_absolute_error(yv,p0)),
          "compound_mae":float(mean_absolute_error(yv,p1))
        })
    ys=pd.DataFrame(yr)
    delta=ys["compound_mae"].to_numpy(float)-ys["baseline_mae"].to_numpy(float) if len(ys) else np.asarray([])
    return ys,{
      "transition_rows":int(len(d)),
      "nodes":int(d["node_id"].nunique()) if len(d) else 0,
      "scored_target_years":int(len(ys)),
      "target_year_range":[int(ys["target_year"].min()),int(ys["target_year"].max())] if len(ys) else None,
      "baseline_mean_mae":float(ys["baseline_mae"].mean()) if len(ys) else None,
      "compound_mean_mae":float(ys["compound_mae"].mean()) if len(ys) else None,
      "support":support(delta,seed,p_threshold) if len(delta) else {"estimable":False,"target_years":0,"supported":False}
    }

def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")
    seg=pd.read_csv(input_dir/"compound_hotfresh_segment_year.csv")
    if len(annual)!=1480 or annual["node_id"].nunique()!=71:
        raise RuntimeError("annual panel identity drift")
    expo=exposure_wide(seg)

    results={}
    for i,(name,spec) in enumerate(OUTCOMES.items()):
        d=transitions(annual,name,expo)
        pthr=float(C["support_rule"]["primary_familywise_p_lt"] if name in PRIMARY else C["support_rule"]["secondary_nominal_p_lt"])
        ys,summ=analyze(d,spec["clip"],SEED+i,pthr)
        if len(ys):
            ys.to_csv(outdir/f"compound_hotfresh_{name}_year_scores.csv",index=False)
        results[name]={"primary":bool(name in PRIMARY),**summ}

    primary_estimable=sum(bool(results[x]["support"]["estimable"]) for x in PRIMARY)
    primary_supported=sum(bool(results[x]["support"]["supported"]) for x in PRIMARY)
    status=("primary_nonestimable" if primary_estimable<2 else
            "compound_hotfresh_condition_supported" if primary_supported>=1 else
            "compound_hotfresh_condition_not_supported")
    result={
      "schema":"tampa.compound_hotfresh_condition_v1.result",
      "status":status,
      "contract":"results/compound_hotfresh_condition_v1_contract.json",
      "exposure_source":"published Beck et al. 2024 daily GAM threshold reconstruction",
      "primary_estimable_outcomes":int(primary_estimable),
      "primary_supported_outcomes":int(primary_supported),
      "results":results,
      "interpretation":(
        "Joint hot-fresh run duration adds outcome-specific heldout information beyond marginal hot and fresh run duration for at least one primary Thalassia plant-condition state."
        if status=="compound_hotfresh_condition_supported" else
        "Joint hot-fresh run duration does not add supported heldout information beyond marginal hot and fresh run duration plus local plant-condition legacy for the primary Thalassia condition states."
        if status=="compound_hotfresh_condition_not_supported" else
        "The primary plant-condition test is not sufficiently estimable."
      ),
      "claim_boundary":C["claim_boundary"]
    }
    (outdir/"compound_hotfresh_condition_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_compound_hotfresh"))
    p.add_argument("--out",type=Path,default=Path("results/generated_compound_hotfresh"))
    a=p.parse_args()
    main(a.input,a.out)
