#!/usr/bin/env python3
"""Frozen Appearance -> next-year exact-point retention follow-up.

Contract was created before this association script:
results/appearance_retention_v1_contract.json
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,warnings
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/appearance_retention_v1_contract.json").read_text())
P=C["primary_analysis"]
COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/data/trnsct.csv"
SIZE=17186023
BLOB="2a9ac04c300d4e209b1359656de6b581ad7ae138"
FOCAL={"Thalassia","Thalassia testudinum"}
APP={"Poor":0.0,"Fair":1.0,"Good":2.0,"Very Good":3.0,"Excellent":3.0}
EXCLUDE=int(C["transition_population"]["primary_target_year_exclusion"])
BOOT=int(P["bootstrap"]["replicates"]); SEED=int(P["bootstrap"]["seed"])

def sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch():
    req=Request(URL,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-appearance-retention/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(SIZE+1)
    if len(data)!=SIZE or sha(data)!=BLOB:
        raise RuntimeError("pinned raw source identity drift")
    return data

def fnum(x):
    try:
        v=float(str(x).strip())
    except Exception:
        return math.nan
    return v if math.isfinite(v) else math.nan

def parse_bb(x):
    s=str(x or "").strip()
    if not s: return math.nan
    v=fnum(s.split("=",1)[0].strip())
    return v if math.isfinite(v) and 0<=v<=5 else math.nan

def parse_dt(x):
    s=str(x or "").strip()
    if not s: return None
    try: return datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception:
        try: return datetime.strptime(s[:10],"%Y-%m-%d")
        except Exception: return None

def build_point_year():
    rd=csv.DictReader(io.StringIO(fetch().decode("utf-8"),newline=""))
    req={"AssessmentYear","Transect","BaySegment","Site","Species","SpeciesAbundance",
         "Appearance","Depth","ObservationDate","MonitoringAgency"}
    if not req.issubset(set(rd.fieldnames or [])):
        raise RuntimeError("source schema drift")
    d={}
    for row in rd:
        node=(row["Transect"] or "").strip()
        site=(row["Site"] or "").strip()
        ys=(row["AssessmentYear"] or "").strip()
        if not node or not site or not ys: continue
        try: year=int(float(ys))
        except Exception: continue
        key=(node,site,year)
        z=d.setdefault(key,{
            "node_id":node,"site":site,"year":year,
            "water_body":(row["BaySegment"] or "").strip(),
            "monitoring_agency":((row["MonitoringAgency"] or "").strip() or "UNKNOWN"),
            "thalassia_present":False,"appearance":[],"bb":[],"depth":[],
            "sin_doy":[],"cos_doy":[]
        })
        ag=((row["MonitoringAgency"] or "").strip() or "UNKNOWN")
        if z["monitoring_agency"]=="UNKNOWN" and ag!="UNKNOWN":
            z["monitoring_agency"]=ag
        dep=fnum(row["Depth"])
        if math.isfinite(dep) and dep!=0:
            z["depth"].append(abs(dep)/100.0)
        dt=parse_dt(row["ObservationDate"])
        if dt is not None:
            doy=dt.timetuple().tm_yday; ang=2*math.pi*(doy-1)/365.25
            z["sin_doy"].append(math.sin(ang)); z["cos_doy"].append(math.cos(ang))

        if (row["Species"] or "").strip() not in FOCAL:
            continue
        z["thalassia_present"]=True
        av=(row["Appearance"] or "").strip()
        if av in APP: z["appearance"].append(APP[av])
        bb=parse_bb(row["SpeciesAbundance"])
        if math.isfinite(bb): z["bb"].append(bb)

    out=[]
    for z in d.values():
        site_m=fnum(z["site"])
        out.append({
            "node_id":z["node_id"],"site":z["site"],"year":z["year"],
            "water_body":z["water_body"],"monitoring_agency":z["monitoring_agency"],
            "sampled":True,"thalassia_present":bool(z["thalassia_present"]),
            "appearance_score":float(np.mean(z["appearance"])) if z["appearance"] else np.nan,
            "source_bb":float(np.mean(z["bb"])) if z["bb"] else np.nan,
            "source_depth_m":float(np.median(z["depth"])) if z["depth"] else np.nan,
            "site_m":float(site_m) if math.isfinite(site_m) else np.nan,
            "sin_doy":float(np.mean(z["sin_doy"])) if z["sin_doy"] else np.nan,
            "cos_doy":float(np.mean(z["cos_doy"])) if z["cos_doy"] else np.nan
        })
    return pd.DataFrame(out)

def transitions(py):
    lookup={(r.node_id,str(r.site),int(r.year)):r for r in py.itertuples(index=False)}
    rows=[]
    for r in py.itertuples(index=False):
        if not bool(r.thalassia_present) or not np.isfinite(r.appearance_score) or int(r.year)>=2025:
            continue
        t=lookup.get((r.node_id,str(r.site),int(r.year)+1))
        if t is None: continue
        rows.append({
            "node_id":str(r.node_id),"site":str(r.site),
            "monitoring_agency":str(r.monitoring_agency or "UNKNOWN"),
            "source_year":str(int(r.year)),"source_year_int":int(r.year),"target_year":int(r.year)+1,
            "retained_next_year":int(bool(t.thalassia_present)),
            "appearance_score":float(r.appearance_score),
            "source_bb":float(r.source_bb) if np.isfinite(r.source_bb) else np.nan,
            "source_depth_m":float(r.source_depth_m) if np.isfinite(r.source_depth_m) else np.nan,
            "site_m":float(r.site_m) if np.isfinite(r.site_m) else np.nan,
            "sin_doy":float(r.sin_doy) if np.isfinite(r.sin_doy) else np.nan,
            "cos_doy":float(r.cos_doy) if np.isfinite(r.cos_doy) else np.nan
        })
    return pd.DataFrame(rows)

CAT=["node_id","source_year","monitoring_agency"]
NUM=["appearance_within_node","source_bb","source_depth_m","site_m","sin_doy","cos_doy"]

def model():
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),NUM)
    ])
    return make_pipeline(pre,LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000))

def fit_coef(d):
    m=model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["retained_next_year"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    co=m.named_steps["logisticregression"].coef_[0]
    hit=np.where(names=="num__appearance_within_node")[0]
    if len(hit)!=1: raise RuntimeError("appearance coefficient missing")
    return float(co[int(hit[0])])

def bootstrap(d):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED); vals=[]; attempts=0
    while len(vals)<BOOT and attempts<BOOT*20:
        attempts+=1; chosen=rng.choice(nodes,size=len(nodes),replace=True); parts=[]
        for k,n in enumerate(chosen):
            x=by[n].copy()
            x["node_id"]=f"{n}__boot{k}"
            parts.append(x)
        b=pd.concat(parts,ignore_index=True)
        if b["retained_next_year"].nunique()<2: continue
        try: vals.append(fit_coef(b))
        except Exception: continue
    if len(vals)<BOOT: raise RuntimeError(f"only {len(vals)} valid bootstrap fits")
    return np.asarray(vals,float),attempts

def run(d,label):
    x=d.copy()
    x["appearance_node_mean"]=x.groupby("node_id")["appearance_score"].transform("mean")
    x["appearance_within_node"]=x["appearance_score"]-x["appearance_node_mean"]
    complete=x.dropna(subset=NUM).copy()
    mins=C["transition_population"]
    losses=int((complete["retained_next_year"]==0).sum())
    reg={
        "candidate_transitions":int(len(d)),
        "complete_transitions":int(len(complete)),
        "nodes":int(complete["node_id"].nunique()),
        "recorded_losses":losses,
        "retained":int(complete["retained_next_year"].sum())
    }
    estimable=(len(complete)>=mins["minimum_complete_transitions"] and
               reg["nodes"]>=mins["minimum_nodes"] and
               losses>=mins["minimum_recorded_losses"] and
               complete["retained_next_year"].nunique()==2)
    if not estimable:
        return {"label":label,"registry":reg,"primary":{"classification":"non_estimable","coefficient":None,"ci95":None}}
    coef=fit_coef(complete); vals,attempts=bootstrap(complete); ci=np.quantile(vals,[.025,.975])
    if ci[0]>0: cls="within_node_positive_appearance_signal"
    elif ci[1]<0: cls="within_node_negative_appearance_signal"
    else: cls="within_node_appearance_signal_not_supported"
    return {
        "label":label,"registry":reg,
        "primary":{"coefficient":coef,"ci95":[float(ci[0]),float(ci[1])],
                   "bootstrap_replicates":int(len(vals)),"bootstrap_attempts":int(attempts),
                   "classification":cls}
    }

def main(out:Path):
    out.mkdir(parents=True,exist_ok=True)
    py=build_point_year(); d=transitions(py)
    pri=run(d[d["target_year"]!=EXCLUDE].copy(),"primary_exclude_target_2016")
    sen=run(d.copy(),"sensitivity_include_target_2016")
    cls=pri["primary"]["classification"]
    interp=P["interpretation"]
    interpretation=(interp["ci_above_zero"] if cls=="within_node_positive_appearance_signal"
                    else interp["ci_below_zero"] if cls=="within_node_negative_appearance_signal"
                    else interp["ci_overlaps_zero"] if cls=="within_node_appearance_signal_not_supported"
                    else "Frozen sample minima were not met.")
    result={
        "schema":"tampa.appearance_retention_v1.result",
        "status":cls,
        "contract":"results/appearance_retention_v1_contract.json",
        "primary":pri,"sensitivity":sen,
        "sensitivity_agreement":pri["primary"]["classification"]==sen["primary"]["classification"],
        "interpretation":interpretation,
        "claim_boundary":C["claim_boundary"]
    }
    d.to_csv(out/"appearance_retention_transitions.csv",index=False)
    (out/"appearance_retention_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--out",type=Path,default=Path("results/generated_appearance_retention"))
    a=p.parse_args(); main(a.out)
