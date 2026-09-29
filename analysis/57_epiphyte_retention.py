#!/usr/bin/env python3
"""Frozen post-hoc epiphyte -> next-year exact-point retention analysis.

Contract: results/epiphyte_retention_v1_contract.json

The response-blind coverage preflight preceded association work. During registry
inspection an unadjusted retention gradient was then seen, so this script is
explicitly a post-hoc adjusted follow-up, not untouched confirmation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import warnings
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/epiphyte_retention_v1_contract.json").read_text())
P=C["primary_analysis"]

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/data/trnsct.csv"
SIZE=17186023
BLOB="2a9ac04c300d4e209b1359656de6b581ad7ae138"
FOCAL={"Thalassia","Thalassia testudinum"}
EPI={"Clean":0.0,"Light":1.0,"Moderate":2.0,"Heavy":3.0}
PRIMARY_EXCLUDE_TARGET=int(C["transition_population"]["primary_target_year_exclusion"])
BOOT=int(P["bootstrap"]["replicates"])
SEED=int(P["bootstrap"]["seed"])

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch()->bytes:
    req=Request(URL,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-epiphyte-retention/1.0"})
    with urlopen(req,timeout=180) as resp:
        data=resp.read(SIZE+1)
    if len(data)!=SIZE or git_blob_sha1(data)!=BLOB:
        raise RuntimeError("pinned raw source identity drift")
    return data

def maybe_float(x):
    try:
        y=float(str(x).strip())
    except Exception:
        return math.nan
    return y if math.isfinite(y) else math.nan

def parse_bb(x):
    s=str(x or "").strip()
    if not s:
        return math.nan
    left=s.split("=",1)[0].strip()
    v=maybe_float(left)
    return v if math.isfinite(v) and 0<=v<=5 else math.nan

def parse_dt(x):
    s=str(x or "").strip()
    if not s:
        return None
    # Source is ISO-like; retain date only.
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception:
        try:
            return datetime.strptime(s[:10],"%Y-%m-%d")
        except Exception:
            return None

def build_point_year():
    reader=csv.DictReader(io.StringIO(fetch().decode("utf-8"),newline=""))
    req={"AssessmentYear","Transect","BaySegment","Site","Species","SpeciesAbundance",
         "EpiphyteDensity","Depth","ObservationDate"}
    if not req.issubset(set(reader.fieldnames or [])):
        raise RuntimeError("source schema drift")
    d={}
    for row in reader:
        node=(row["Transect"] or "").strip()
        site=(row["Site"] or "").strip()
        ys=(row["AssessmentYear"] or "").strip()
        if not node or not site or not ys:
            continue
        try: year=int(float(ys))
        except Exception: continue
        key=(node,site,year)
        z=d.setdefault(key,{
            "node_id":node,"site":site,"year":year,
            "water_body":(row["BaySegment"] or "").strip(),
            "sampled":True,"thalassia_present":False,
            "epi":[],"bb":[],"depth":[],"sin_doy":[],"cos_doy":[]
        })
        dep=maybe_float(row["Depth"])
        if math.isfinite(dep) and dep!=0:
            z["depth"].append(abs(dep)/100.0)
        dt=parse_dt(row["ObservationDate"])
        if dt is not None:
            doy=dt.timetuple().tm_yday
            ang=2*math.pi*(doy-1)/365.25
            z["sin_doy"].append(math.sin(ang)); z["cos_doy"].append(math.cos(ang))

        sp=(row["Species"] or "").strip()
        if sp not in FOCAL:
            continue
        z["thalassia_present"]=True
        ev=(row["EpiphyteDensity"] or "").strip()
        if ev in EPI:
            z["epi"].append(EPI[ev])
        bb=parse_bb(row["SpeciesAbundance"])
        if math.isfinite(bb):
            z["bb"].append(bb)

    rows=[]
    for z in d.values():
        rows.append({
            "node_id":z["node_id"],"site":z["site"],"year":z["year"],
            "water_body":z["water_body"],
            "sampled":True,
            "thalassia_present":bool(z["thalassia_present"]),
            "epi_score":float(np.mean(z["epi"])) if z["epi"] else np.nan,
            "source_bb":float(np.mean(z["bb"])) if z["bb"] else np.nan,
            "source_depth_m":float(np.median(z["depth"])) if z["depth"] else np.nan,
            "sin_doy":float(np.mean(z["sin_doy"])) if z["sin_doy"] else np.nan,
            "cos_doy":float(np.mean(z["cos_doy"])) if z["cos_doy"] else np.nan,
        })
    return pd.DataFrame(rows)

def transitions(py:pd.DataFrame):
    lookup={(r.node_id,str(r.site),int(r.year)):r for r in py.itertuples(index=False)}
    rows=[]
    for r in py.itertuples(index=False):
        if not bool(r.thalassia_present) or not np.isfinite(r.epi_score) or int(r.year)>=2025:
            continue
        t=lookup.get((r.node_id,str(r.site),int(r.year)+1))
        if t is None:
            continue
        rows.append({
            "node_id":str(r.node_id),
            "site":str(r.site),
            "water_body":str(r.water_body),
            "source_year":str(int(r.year)),
            "source_year_int":int(r.year),
            "target_year":int(r.year)+1,
            "retained_next_year":int(bool(t.thalassia_present)),
            "epi_score":float(r.epi_score),
            "source_bb":float(r.source_bb) if np.isfinite(r.source_bb) else np.nan,
            "source_depth_m":float(r.source_depth_m) if np.isfinite(r.source_depth_m) else np.nan,
            "sin_doy":float(r.sin_doy) if np.isfinite(r.sin_doy) else np.nan,
            "cos_doy":float(r.cos_doy) if np.isfinite(r.cos_doy) else np.nan,
        })
    d=pd.DataFrame(rows)
    if len(d):
        d["epi_node_mean"]=d.groupby("node_id")["epi_score"].transform("mean")
        d["epi_within_node"]=d["epi_score"]-d["epi_node_mean"]
    return d

PRIMARY_CAT=["node_id","source_year"]
PRIMARY_NUM=["epi_within_node","source_bb","source_depth_m","sin_doy","cos_doy"]
POOLED_CAT=["water_body","source_year"]
POOLED_NUM=["epi_score","source_bb","source_depth_m","sin_doy","cos_doy"]

def model(cat,num):
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),cat),
        ("num",StandardScaler(),num),
    ])
    clf=LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000)
    return make_pipeline(pre,clf)

def fit_coef(d,cat,num,key):
    if d["retained_next_year"].nunique()<2:
        raise RuntimeError("outcome has <2 classes")
    m=model(cat,num)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[cat+num],d["retained_next_year"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    co=m.named_steps["logisticregression"].coef_[0]
    hit=np.where(names==f"num__{key}")[0]
    if len(hit)!=1:
        raise RuntimeError(f"coefficient not found: {key}")
    return float(co[int(hit[0])])

def bootstrap(d,cat,num,key):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]; attempts=0
    while len(vals)<BOOT and attempts<BOOT*20:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        parts=[]
        for k,n in enumerate(chosen):
            x=by[n].copy()
            # Make duplicate sampled clusters distinct fixed-effect labels while
            # preserving the within-cluster observations.
            if "node_id" in cat:
                x["node_id"]=f"{n}__boot{k}"
            parts.append(x)
        b=pd.concat(parts,ignore_index=True)
        if b["retained_next_year"].nunique()<2:
            continue
        try: vals.append(fit_coef(b,cat,num,key))
        except Exception: continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstrap fits")
    return np.asarray(vals,float),attempts

def unadjusted_by_round(d):
    x=d.copy()
    x["epi_rounded"]=x["epi_score"].round().clip(0,3).astype(int)
    out=[]
    for k,g in x.groupby("epi_rounded",sort=True):
        out.append({
            "epiphyte_ordinal":int(k),
            "transitions":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "retention_fraction":float(g["retained_next_year"].mean())
        })
    return out

def run_one(d,label):
    complete=d.dropna(subset=PRIMARY_NUM).copy()
    mins=C["transition_population"]
    losses=int((complete["retained_next_year"]==0).sum())
    estimable=(
        len(complete)>=int(mins["minimum_complete_transitions"])
        and complete["node_id"].nunique()>=int(mins["minimum_nodes"])
        and losses>=int(mins["minimum_recorded_losses"])
    )
    res={
        "label":label,
        "registry":{
            "candidate_transitions":int(len(d)),
            "complete_transitions":int(len(complete)),
            "nodes":int(complete["node_id"].nunique()),
            "retained":int(complete["retained_next_year"].sum()),
            "recorded_losses":losses,
            "source_year_min":int(complete["source_year_int"].min()) if len(complete) else None,
            "source_year_max":int(complete["source_year_int"].max()) if len(complete) else None,
        },
        "unadjusted_by_rounded_epiphyte":unadjusted_by_round(complete) if len(complete) else [],
        "primary":{"coefficient":None,"ci95":None,"classification":"non_estimable"},
        "secondary_pooled":{"coefficient":None},
    }
    if not estimable:
        return res
    p=fit_coef(complete,PRIMARY_CAT,PRIMARY_NUM,"epi_within_node")
    vals,attempts=bootstrap(complete,PRIMARY_CAT,PRIMARY_NUM,"epi_within_node")
    ci=np.quantile(vals,[.025,.975])
    if ci[1]<0: cls="within_node_negative_epiphyte_signal"
    elif ci[0]>0: cls="within_node_positive_epiphyte_signal"
    else: cls="within_node_epiphyte_signal_not_supported"
    pooled=fit_coef(complete,POOLED_CAT,POOLED_NUM,"epi_score")
    res["primary"]={
        "coefficient":p,
        "ci95":[float(ci[0]),float(ci[1])],
        "bootstrap_replicates":int(len(vals)),
        "bootstrap_attempts":int(attempts),
        "classification":cls,
    }
    res["secondary_pooled"]={"coefficient":pooled}
    return res

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=build_point_year()
    d=transitions(py)
    primary=d[d["target_year"]!=PRIMARY_EXCLUDE_TARGET].copy()
    sensitivity=d.copy()

    pri=run_one(primary,"primary_exclude_target_2016")
    sen=run_one(sensitivity,"sensitivity_include_target_2016")
    cls=pri["primary"]["classification"]
    interpretations=P["interpretation"]
    if cls=="within_node_negative_epiphyte_signal":
        interpretation=interpretations["ci_below_zero"]
    elif cls=="within_node_positive_epiphyte_signal":
        interpretation=interpretations["ci_above_zero"]
    elif cls=="within_node_epiphyte_signal_not_supported":
        interpretation=interpretations["ci_overlaps_zero"]
    else:
        interpretation="Frozen sample minima were not met."

    result={
        "schema":"tampa.epiphyte_retention_v1.result",
        "status":cls,
        "contract":"results/epiphyte_retention_v1_contract.json",
        "primary":pri,
        "sensitivity":sen,
        "interpretation":interpretation,
        "sensitivity_agreement":(
            pri["primary"]["classification"]==sen["primary"]["classification"]
        ),
        "claim_boundary":C["claim_boundary"]
    }
    d.to_csv(outdir/"epiphyte_retention_transitions.csv",index=False)
    (outdir/"epiphyte_retention_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_epiphyte_retention"))
    a=p.parse_args(); main(a.out)
