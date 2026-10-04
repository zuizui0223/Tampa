#!/usr/bin/env python3
"""Frozen primary analysis for Tampa within-canopy optical microenvironment."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
REFERENCE_BAY="Old Tampa Bay"
BOOTSTRAP_REPS=10000
BOOTSTRAP_SEED=20261005
MIN_TOTAL=30
MIN_PER_BAY=8
MIN_DISTINCT_OVERALL=10
MIN_VARIATION_BAYS=2
MIN_NODES_VARIATION_BAY=6
MIN_DISTINCT_EXPOSURES_BAY=3
REQ={
 "node_id","water_body","tnc_pre_mg_g","tnc_post_mg_g",
 "mean_daily_within_canopy_dli","par_coverage_fraction",
 "valid_daily_dli_count","common_overlap_days","pre_post_tnc_interval_days",
 "daily_dli_qc_pass","primary_qc_pass"
}

def truth(v):
    return str(v).strip().lower() in {"1","true","yes","y","pass","passed"}

def prep(df):
    if m:=REQ-set(df.columns): raise RuntimeError(f"missing columns: {sorted(m)}")
    if df["node_id"].astype(str).duplicated().any(): raise RuntimeError("one row per node required")
    x=df.copy();x["water_body"]=x["water_body"].astype(str)
    x=x[x["water_body"].isin(BAYS)].copy()
    for col in ["tnc_pre_mg_g","tnc_post_mg_g","mean_daily_within_canopy_dli",
                "par_coverage_fraction","valid_daily_dli_count","common_overlap_days",
                "pre_post_tnc_interval_days"]:
        x[col]=pd.to_numeric(x[col],errors="coerce")
    x=x[x["primary_qc_pass"].map(truth)&x["daily_dli_qc_pass"].map(truth)].copy()
    x=x.dropna(subset=[
      "tnc_pre_mg_g","tnc_post_mg_g","mean_daily_within_canopy_dli",
      "par_coverage_fraction","valid_daily_dli_count","common_overlap_days",
      "pre_post_tnc_interval_days"
    ])
    x=x[x["par_coverage_fraction"]>=.85]
    x=x[x["valid_daily_dli_count"]>=30]
    x=x[x["common_overlap_days"]>=35]
    x=x[x["pre_post_tnc_interval_days"].between(39,45)]
    return x.reset_index(drop=True)

def design(x):
    cols=[np.ones(len(x)),x["tnc_pre_mg_g"].to_numpy(float),x["mean_daily_within_canopy_dli"].to_numpy(float)]
    names=["intercept","tnc_pre_mg_g","mean_daily_within_canopy_dli"]
    for b in BAYS:
        if b==REFERENCE_BAY: continue
        cols.append((x["water_body"].to_numpy(str)==b).astype(float));names.append("water_body["+b+"]")
    return np.column_stack(cols),x["tnc_post_mg_g"].to_numpy(float),names

def coef(x):
    X,y,names=design(x)
    if np.linalg.matrix_rank(X)<X.shape[1]: return np.nan
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    return float(b[names.index("mean_daily_within_canopy_dli")])

def gates(x):
    counts={b:int((x["water_body"]==b).sum()) for b in BAYS}
    sample=bool(len(x)>=MIN_TOTAL and all(counts[b]>=MIN_PER_BAY for b in BAYS))
    overall=bool(x["mean_daily_within_canopy_dli"].nunique()>=MIN_DISTINCT_OVERALL)
    varying=[];distinct={}
    for b in BAYS:
        z=x.loc[x["water_body"]==b,"mean_daily_within_canopy_dli"]
        distinct[b]=int(z.nunique())
        if len(z)>=MIN_NODES_VARIATION_BAY and z.nunique()>=MIN_DISTINCT_EXPOSURES_BAY:
            varying.append(b)
    within=bool(len(varying)>=MIN_VARIATION_BAYS)
    return counts,sample,overall,within,varying,distinct

def boot(x):
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    groups={b:x[x["water_body"]==b].reset_index(drop=True) for b in BAYS}
    vals=[];invalid=0
    for _ in range(BOOTSTRAP_REPS):
        parts=[]
        for b in BAYS:
            g=groups[b];idx=rng.integers(0,len(g),size=len(g));parts.append(g.iloc[idx])
        z=pd.concat(parts,ignore_index=True);v=coef(z)
        if np.isfinite(v):vals.append(v)
        else:invalid+=1
    if len(vals)<.95*BOOTSTRAP_REPS: raise RuntimeError(f"valid bootstrap replicates {len(vals)} <95%")
    a=np.asarray(vals,float)
    return {
      "valid_replicates":len(a),"invalid_replicates":invalid,
      "ci95":[float(np.quantile(a,.025)),float(np.quantile(a,.975))],
      "ci97_5":[float(np.quantile(a,.0125)),float(np.quantile(a,.9875))],
      "median":float(np.median(a))
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--optical-freeze",default="field/optical_pilot_freeze.json")
    a=ap.parse_args()

    method=json.loads(Path(a.optical_freeze).read_text())
    if method.get("status")!="READY":
        raise RuntimeError("optical method freeze must be READY before primary analysis")
    mf=method.get("fields_to_freeze_before_optical_confirmatory_deployment",{})
    angular_class=mf.get("primary_angular_response_class")
    reference_class=mf.get("reference_angular_response_class")
    quantity_label=mf.get("primary_light_quantity_reporting_label")
    if angular_class not in {"2pi_cosine_ppfd","4pi_scalar_ppffr"}:
        raise RuntimeError("primary optical angular-response class is not valid/frozen")
    if reference_class!=angular_class:
        raise RuntimeError("primary/reference optical angular-response classes mismatch")
    if not quantity_label:
        raise RuntimeError("primary optical light-quantity reporting label is missing")

    x=prep(pd.read_csv(a.input));counts,sample,overall,within,var_bays,distinct=gates(x)
    point=coef(x)
    if not np.isfinite(point): raise RuntimeError("primary design matrix rank-deficient")
    b=boot(x);lo,hi=b["ci95"]
    interval="supported_positive" if lo>0 else "contradicted_direction" if hi<0 else "unsupported"
    estimable=sample and overall and within
    res={
      "schema":"tampa.optical_primary_analysis.v1",
      "model":"tnc_post ~ tnc_pre + mean_daily_within_canopy_dli + water_body",
      "optical_measurement_semantics":{
        "angular_response_class":angular_class,
        "reference_angular_response_class":reference_class,
        "reporting_label":quantity_label,
        "method_freeze":str(a.optical_freeze)
      },
      "primary_coefficient":{"name":"mean_daily_within_canopy_dli","estimate":point,"units":"mg g-1 post-TNC per mol photons m-2 d-1 of the frozen optical quantity"},
      "analytic_nodes":len(x),"nodes_by_water_body":counts,
      "gates":{
        "sample_gate_passed":sample,"overall_distinct_exposure_gate_passed":overall,
        "within_bay_identifiability_passed":within,
        "within_bay_variation_bays":var_bays,"distinct_exposure_values_by_bay":distinct
      },
      "uncertainty":{"method":"water-body-stratified stable-node bootstrap","repetitions":BOOTSTRAP_REPS,"seed":BOOTSTRAP_SEED,**b},
      "standalone_interval_classification":interval,
      "interpretation_status":interval if estimable else "nonestimable_or_pilot_gate_failed",
      "family_level_ci97_5":b["ci97_5"],
      "claim_boundary":[
        "Support is a prospective actual-light/reserve association, not proof that epiphytes or light alone are causal.",
        "Do not introduce a low-light threshold, change PAR aggregation, drop water_body, shift season, or select a favorable node subset after TNC inspection.",
        "A positive canopy attenuation diagnostic cannot rescue a null within-canopy DLI primary.",
        "Interpret the DLI coefficient only for the angular-response quantity frozen before deployment; cosine PPFD and scalar PPFFR are not interchangeable."
      ]
    }
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n");print(json.dumps(res,indent=2,sort_keys=True))
if __name__=="__main__":main()
