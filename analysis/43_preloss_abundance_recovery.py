#!/usr/bin/env python3
"""Test whether exact-point pre-loss Thalassia abundance predicts re-recording.

Frozen design: results/preloss_abundance_recovery_v1_contract.json
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
C=json.loads((ROOT/"results/preloss_abundance_recovery_v1_contract.json").read_text())
H=C["primary_hypothesis"]

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
    "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
    "occurrence":{"url":f"{BASE}/occurrence.csv","size":12508487,"blob":"d34aeb5aedb72459d1e04059629cb09450df929e"},
    "emof":{"url":f"{BASE}/emof.csv","size":16449353,"blob":"e463046726080334637824555309fd89c7c447da"},
}
FOCAL="Thalassia testudinum"
MEASURE="seagrass percent cover (Braun-Blanquet scale)"
EVENT_HEADER=["eventID","parentEventID","eventType","eventDate","year","month","day","decimalLatitude","decimalLongitude","geodeticDatum","minimumDepthInMeters","maximumDepthInMeters","country","countryCode","stateProvince","waterBody","locality","locationID","samplingProtocol","institutionCode","datasetName","datasetID","license","locationRemarks"]
OCC_HEADER=["occurrenceID","eventID","basisOfRecord","occurrenceStatus","scientificName","scientificNameID","taxonRank","kingdom","phylum","class","order","family","genus","collectionCode","recordedBy","identificationRemarks"]
EMOF_HEADER=["eventID","occurrenceID","measurementType","measurementTypeID","measurementValue","measurementUnit","measurementUnitID","measurementRemarks"]

BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
CAT=["node_id"]
NUM=["loss_year","loss_year_vegetated","source_mixed","pre_loss_run_centered","source_bb_centered"]


def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-point-bb-recovery/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(int(spec["size"])+1)
    if len(data)!=int(spec["size"]):
        raise RuntimeError(f"source size drift {spec['url']} {len(data)}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError(f"source blob drift {spec['url']}")
    return data


def maybe_float(x):
    try:
        v=float(str(x).strip())
    except Exception:
        return math.nan
    return v if math.isfinite(v) else math.nan


def parse_event(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EVENT_HEADER:
        raise RuntimeError("event header drift")
    parents={}
    children=defaultdict(list)
    point={}
    for row in reader:
        typ=row["eventType"].strip()
        eid=row["eventID"].strip()
        if typ=="Transect":
            dt=datetime.strptime(row["eventDate"],"%Y-%m-%d")
            parents[eid]={
                "node_id":row["locationID"].strip(),
                "year":int(dt.year),
                "water_body":row["waterBody"].strip(),
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            children[pid].append(eid)
            point[eid]={
                "parent_id":pid,
                "point_id":row["locationID"].strip(),
            }
        else:
            raise RuntimeError(f"unsupported event type {typ}")
    eligible={pid for pid in parents if len(children.get(pid,[]))>=3}
    point={eid:x for eid,x in point.items() if x["parent_id"] in eligible}
    return parents,point


def parse_occ(data:bytes,point_events:set[str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    occ={}
    by_event=defaultdict(list)
    for row in reader:
        eid=row["eventID"].strip()
        if eid not in point_events:
            continue
        if row["occurrenceStatus"].strip()!="present":
            continue
        if row["scientificName"].strip()!=FOCAL:
            continue
        oid=row["occurrenceID"].strip()
        occ[oid]=eid
        by_event[eid].append(oid)
    return occ,by_event


def parse_emof(data:bytes,occurrence_to_event:dict[str,str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EMOF_HEADER:
        raise RuntimeError("emof header drift")
    vals=defaultdict(list)
    nonnumeric=0
    for row in reader:
        oid=row["occurrenceID"].strip()
        if oid not in occurrence_to_event:
            continue
        if row["measurementType"]!=MEASURE:
            continue
        v=maybe_float(row["measurementValue"])
        if math.isfinite(v):
            vals[oid].append(v)
        else:
            nonnumeric+=1
    return vals,nonnumeric


def build_point_year_bb(raw_event,raw_occ,raw_emof):
    parents,points=parse_event(raw_event)
    occ,by_event=parse_occ(raw_occ,set(points))
    meas,nonnumeric=parse_emof(raw_emof,occ)
    rows=[]
    for eid,p in points.items():
        pid=p["parent_id"]
        if pid not in parents:
            continue
        local=[]
        for oid in by_event.get(eid,[]):
            local.extend(meas.get(oid,[]))
        if not local:
            continue
        rows.append({
            "point_id":p["point_id"],
            "node_id":parents[pid]["node_id"],
            "year":parents[pid]["year"],
            "bb":float(np.mean(local)),
        })
    pv=pd.DataFrame(rows)
    py=(pv.groupby(["point_id","node_id","year"],as_index=False)
        .agg(source_point_bb=("bb","mean"),numeric_point_visits=("bb","size")))
    return py,nonnumeric


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v.strip() for v in str(x).split(";") if v.strip()}


def build_frame(consensus:pd.DataFrame,seq:pd.DataFrame,bb:pd.DataFrame):
    by_point={}
    for point,g in consensus.groupby("point_id",sort=False):
        by_point[str(point)]={int(r.year):r for r in g.itertuples(index=False)}
    bb_lookup={(str(r.point_id),int(r.year)):float(r.source_point_bb) for r in bb.itertuples(index=False)}
    rows=[]
    for r in seq.itertuples(index=False):
        point=str(r.point_id)
        source=int(r.source_year)
        key=(point,source)
        if key not in bb_lookup:
            continue
        hist=by_point.get(point,{})
        if source not in hist or not bool(hist[source].thalassia_present):
            raise RuntimeError(f"source consensus mismatch {point} {source}")
        run=0
        y=source
        while y in hist and bool(hist[y].thalassia_present):
            run+=1; y-=1
        src=hist[source]
        rows.append({
            "point_id":point,
            "node_id":str(r.node_id),
            "source_year":source,
            "loss_year":int(r.loss_year),
            "recovery_year":int(r.recovery_year),
            "loss_year_vegetated":int(str(r.intermediate_state)=="other_seagrass"),
            "source_mixed":int(bool(species_set(src.alternative_species))),
            "pre_loss_run":int(run),
            "source_point_bb":bb_lookup[key],
            "thalassia_return":int(r.thalassia_return),
        })
    d=pd.DataFrame(rows)
    if len(d):
        d["pre_loss_run_centered"]=d["pre_loss_run"]-d.groupby("node_id")["pre_loss_run"].transform("mean")
        d["source_bb_centered"]=d["source_point_bb"]-d.groupby("node_id")["source_point_bb"].transform("mean")
    return d


def make_model(num_cols):
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),num_cols),
    ])
    clf=LogisticRegression(
        C=float(H["logistic_C"]),solver=str(H["solver"]),max_iter=int(H["max_iter"])
    )
    return make_pipeline(pre,clf)


def fit_coef(d:pd.DataFrame,num_cols,target:str):
    if d["thalassia_return"].nunique()<2:
        raise RuntimeError("single outcome class")
    m=make_model(num_cols)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+num_cols],d["thalassia_return"].to_numpy(int))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["logisticregression"].coef_[0]
    idx=np.where(names=="num__"+target)[0]
    if len(idx)!=1:
        raise RuntimeError(f"coefficient missing {target}")
    return float(coef[int(idx[0])])


def bootstrap(d:pd.DataFrame):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*10
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by[n] for n in chosen],ignore_index=True)
        if b["thalassia_return"].nunique()<2:
            continue
        try:
            vals.append(fit_coef(b,NUM,"source_bb_centered"))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstraps from {attempts}")
    return np.asarray(vals,float),attempts


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    consensus=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    if len(seq)!=259:
        raise RuntimeError(f"recovery sequence registry drift {len(seq)}")

    raw={k:fetch(v) for k,v in FILES.items()}
    bb,nonnumeric=build_point_year_bb(raw["event"],raw["occurrence"],raw["emof"])
    d=build_frame(consensus,seq,bb)

    nodes=int(d["node_id"].nunique()) if len(d) else 0
    variation=int((d.groupby("node_id")["source_point_bb"].nunique()>1).sum()) if len(d) else 0
    returns=int(d["thalassia_return"].sum()) if len(d) else 0
    nonreturns=int(len(d)-returns)
    estimable=bool(
        len(d)>=int(H["minimum_eligible_sequences"])
        and nodes>=int(H["minimum_nodes"])
        and variation>=int(H["minimum_nodes_with_bb_variation"])
        and returns>=int(H["minimum_returns"])
        and nonreturns>=int(H["minimum_nonreturns"])
    )

    result={
        "schema":"tampa.preloss_abundance_recovery_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/preloss_abundance_recovery_v1_contract.json",
        "registry":{
            "frozen_recovery_sequences":int(len(seq)),
            "bb_eligible_sequences":int(len(d)),
            "eligible_fraction":float(len(d)/len(seq)),
            "nodes":nodes,
            "nodes_with_bb_variation":variation,
            "returns":returns,
            "nonreturns":nonreturns,
            "nonnumeric_focal_bb_rows_in_source":int(nonnumeric),
        },
        "primary":{
            "centered_source_bb_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "return_bb_median":float(d.loc[d["thalassia_return"]==1,"source_point_bb"].median()) if returns else None,
            "nonreturn_bb_median":float(d.loc[d["thalassia_return"]==0,"source_point_bb"].median()) if nonreturns else None,
            "coefficient_without_history_control":None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        point=fit_coef(d,NUM,"source_bb_centered")
        nohist=[x for x in NUM if x!="pre_loss_run_centered"]
        nohist_coef=fit_coef(d,nohist,"source_bb_centered")
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]="preloss_abundance_recovery_supported" if supported else "preloss_abundance_recovery_not_supported"
        result["primary"]={
            "centered_source_bb_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["secondary"]["coefficient_without_history_control"]=nohist_coef
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen abundance-coverage/node/outcome minima were not met."

    bb.to_csv(outdir/"point_year_braun_blanquet.csv",index=False)
    d.to_csv(outdir/"preloss_abundance_recovery_sequences.csv",index=False)
    (outdir/"preloss_abundance_recovery_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_preloss_abundance"))
    p.add_argument("--out",type=Path,default=Path("results/generated_preloss_abundance"))
    a=p.parse_args(); main(a.input,a.out)
