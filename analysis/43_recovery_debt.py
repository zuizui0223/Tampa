#!/usr/bin/env python3
"""Test quantitative recovery debt after exact-point Thalassia re-recording.

Frozen design: results/recovery_debt_v1_contract.json

The group definition is taken only from exact-point presence states:
- recovered: present at t, absent t+1, present t+2
- continuous: present at t, t+1, t+2

Numeric Braun-Blanquet values are merged only after groups are fixed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import warnings
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/recovery_debt_v1_contract.json").read_text())
H=C["primary_hypothesis"]

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
    "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
    "occurrence":{"url":f"{BASE}/occurrence.csv","size":12508487,"blob":"d34aeb5aedb72459d1e04059629cb09450df929e"},
    "emof":{"url":f"{BASE}/emof.csv","size":16449353,"blob":"e463046726080334637824555309fd89c7c447da"},
}
EVENT_HEADER=[
    "eventID","parentEventID","eventType","eventDate","year","month","day",
    "decimalLatitude","decimalLongitude","geodeticDatum","minimumDepthInMeters",
    "maximumDepthInMeters","country","countryCode","stateProvince","waterBody",
    "locality","locationID","samplingProtocol","institutionCode","datasetName",
    "datasetID","license","locationRemarks",
]
OCC_HEADER=[
    "occurrenceID","eventID","basisOfRecord","occurrenceStatus","scientificName",
    "scientificNameID","taxonRank","kingdom","phylum","class","order","family",
    "genus","collectionCode","recordedBy","identificationRemarks",
]
EMOF_HEADER=[
    "eventID","occurrenceID","measurementType","measurementTypeID",
    "measurementValue","measurementUnit","measurementUnitID","measurementRemarks",
]
FOCAL="Thalassia testudinum"
COVER_TYPE="seagrass percent cover (Braun-Blanquet scale)"
CAT=["node_id","return_year"]
NUM=["source_bb","recovered_group"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])


def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-recovery-debt/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(spec["size"]+1)
    if len(data)!=spec["size"]:
        raise RuntimeError(f"source size drift {spec['url']} {len(data)}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError(f"source blob drift {spec['url']}")
    return data


def maybe_float(x):
    try:
        y=float(str(x).strip())
    except Exception:
        return np.nan
    return y if np.isfinite(y) else np.nan


def parse_point_event_metadata(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EVENT_HEADER:
        raise RuntimeError("event header drift")
    parents={}
    points={}
    children=defaultdict(list)
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
            points[eid]={
                "parent_id":pid,
                "point_id":row["locationID"].strip(),
            }
            children[pid].append(eid)
        else:
            raise RuntimeError(f"unsupported event type {typ}")
    eligible={pid for pid in parents if len(children.get(pid,[]))>=3}
    out={}
    for eid,p in points.items():
        if p["parent_id"] not in eligible:
            continue
        parent=parents[p["parent_id"]]
        out[eid]={
            "point_id":p["point_id"],
            "node_id":parent["node_id"],
            "year":parent["year"],
            "water_body":parent["water_body"],
        }
    return out


def parse_focal_occurrences(data:bytes,point_events:set[str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    occ={}
    for row in reader:
        eid=row["eventID"].strip()
        if eid not in point_events:
            continue
        if row["occurrenceStatus"].strip()!="present":
            continue
        if row["scientificName"].strip()!=FOCAL:
            continue
        occ[row["occurrenceID"].strip()]=eid
    return occ


def parse_numeric_bb(data:bytes,focal_occ:dict[str,str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EMOF_HEADER:
        raise RuntimeError("emof header drift")
    by_event=defaultdict(list)
    nonnumeric=0
    for row in reader:
        oid=row["occurrenceID"].strip()
        eid=focal_occ.get(oid)
        if eid is None:
            continue
        if row["measurementType"]!=COVER_TYPE:
            continue
        v=maybe_float(row["measurementValue"])
        if np.isfinite(v):
            by_event[eid].append(float(v))
        else:
            nonnumeric+=1
    return by_event,nonnumeric


def point_year_bb(meta:dict,by_event:dict):
    rows=[]
    tmp=defaultdict(list)
    node={}
    wb={}
    for eid,m in meta.items():
        vals=by_event.get(eid,[])
        if not vals:
            continue
        key=(m["point_id"],m["year"])
        tmp[key].extend(vals)
        node[key]=m["node_id"]
        wb[key]=m["water_body"]
    for (point_id,year),vals in sorted(tmp.items()):
        rows.append({
            "point_id":point_id,
            "year":int(year),
            "node_id":node[(point_id,year)],
            "water_body":wb[(point_id,year)],
            "bb_numeric_mean":float(np.mean(vals)),
            "bb_numeric_n":int(len(vals)),
        })
    return pd.DataFrame(rows)


def build_groups(py:pd.DataFrame):
    rows=[]
    for point,g in py.groupby("point_id",sort=True):
        recs=g.sort_values("year").to_dict("records")
        for i in range(len(recs)-2):
            a,b,c=recs[i:i+3]
            y0,y1,y2=map(int,[a["year"],b["year"],c["year"]])
            if not (y1==y0+1 and y2==y1+1):
                continue
            if y0<2016 or y2>2025:
                continue
            states=[bool(a["thalassia_present"]),bool(b["thalassia_present"]),bool(c["thalassia_present"])]
            if states==[True,False,True]:
                recovered=1
                group="recovered"
            elif states==[True,True,True]:
                recovered=0
                group="continuous"
            else:
                continue
            rows.append({
                "point_id":str(point),
                "node_id":str(a["node_id"]),
                "water_body":str(a["water_body"]),
                "source_year":y0,
                "middle_year":y1,
                "return_year":str(y2),
                "return_year_int":y2,
                "group":group,
                "recovered_group":recovered,
            })
    return pd.DataFrame(rows)


def make_model():
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT),
        ("num",StandardScaler(),NUM),
    ])
    return make_pipeline(pre,Ridge(alpha=float(H["model"].split("alpha=")[1].split(")")[0])))


def fit_coef(d:pd.DataFrame)->float:
    if d["recovered_group"].nunique()<2:
        raise RuntimeError("insufficient groups")
    m=make_model()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(d[CAT+NUM],d["target_bb"].to_numpy(float))
    names=m.named_steps["columntransformer"].get_feature_names_out()
    coef=m.named_steps["ridge"].coef_
    idx=np.where(names=="num__recovered_group")[0]
    if len(idx)!=1:
        raise RuntimeError("recovered_group coefficient missing")
    return float(coef[int(idx[0])])


def bootstrap(d:pd.DataFrame):
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*20
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by[n] for n in chosen],ignore_index=True)
        if b["recovered_group"].nunique()<2:
            continue
        try:
            vals.append(fit_coef(b))
        except Exception:
            continue
    if len(vals)<BOOT:
        raise RuntimeError(f"only {len(vals)} valid bootstraps from {attempts}")
    return np.asarray(vals,float),attempts


def summary_group(d:pd.DataFrame,label:str):
    x=d[d["group"]==label]
    return {
        "sequences":int(len(x)),
        "nodes":int(x["node_id"].nunique()) if len(x) else 0,
        "target_bb_mean":float(x["target_bb"].mean()) if len(x) else None,
        "target_bb_median":float(x["target_bb"].median()) if len(x) else None,
        "source_bb_mean":float(x["source_bb"].mean()) if len(x) else None,
        "mean_source_to_target_change":float((x["target_bb"]-x["source_bb"]).mean()) if len(x) else None,
    }


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)

    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    if len(py)!=45494:
        raise RuntimeError(f"point-year registry drift {len(py)}")
    groups=build_groups(py)
    if len(groups)==0:
        raise RuntimeError("no recovered/continuous three-year sequences")

    raw={k:fetch(v) for k,v in FILES.items()}
    meta=parse_point_event_metadata(raw["event"])
    focal=parse_focal_occurrences(raw["occurrence"],set(meta))
    bb,nonnumeric=parse_numeric_bb(raw["emof"],focal)
    q=point_year_bb(meta,bb)

    source=q.rename(columns={
        "year":"source_year",
        "bb_numeric_mean":"source_bb",
        "bb_numeric_n":"source_bb_n",
    })[["point_id","source_year","source_bb","source_bb_n"]]
    target=q.rename(columns={
        "year":"return_year_int",
        "bb_numeric_mean":"target_bb",
        "bb_numeric_n":"target_bb_n",
    })[["point_id","return_year_int","target_bb","target_bb_n"]]

    d=(groups.merge(source,on=["point_id","source_year"],how="inner",validate="many_to_one")
             .merge(target,on=["point_id","return_year_int"],how="inner",validate="many_to_one"))

    rec=d[d["recovered_group"]==1]
    ctl=d[d["recovered_group"]==0]
    estimable=bool(
        len(rec)>=int(H["minimum_recovered_sequences"])
        and len(ctl)>=int(H["minimum_continuous_sequences"])
        and rec["node_id"].nunique()>=int(H["minimum_recovered_nodes"])
        and ctl["node_id"].nunique()>=int(H["minimum_control_nodes"])
    )

    result={
        "schema":"tampa.recovery_debt_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/recovery_debt_v1_contract.json",
        "registry":{
            "presence_defined_sequences":int(len(groups)),
            "quantitative_complete_sequences":int(len(d)),
            "nodes":int(d["node_id"].nunique()) if len(d) else 0,
            "recovered_sequences":int(len(rec)),
            "recovered_nodes":int(rec["node_id"].nunique()) if len(rec) else 0,
            "continuous_sequences":int(len(ctl)),
            "continuous_nodes":int(ctl["node_id"].nunique()) if len(ctl) else 0,
            "point_years_with_numeric_bb":int(len(q)),
            "nonnumeric_focal_bb_rows":int(nonnumeric),
        },
        "primary":{
            "recovered_group_coefficient":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "recovered":summary_group(d,"recovered"),
            "continuous":summary_group(d,"continuous"),
            "by_segment":[],
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    byseg=[]
    for wb,g in d.groupby("water_body",sort=True):
        byseg.append({
            "water_body":wb,
            "recovered_sequences":int((g["group"]=="recovered").sum()),
            "recovered_target_bb_mean":float(g.loc[g["group"]=="recovered","target_bb"].mean()) if (g["group"]=="recovered").any() else None,
            "continuous_sequences":int((g["group"]=="continuous").sum()),
            "continuous_target_bb_mean":float(g.loc[g["group"]=="continuous","target_bb"].mean()) if (g["group"]=="continuous").any() else None,
        })
    result["secondary"]["by_segment"]=byseg

    if estimable:
        point=fit_coef(d)
        vals,attempts=bootstrap(d)
        ci=np.quantile(vals,[.025,.975])
        supported=bool(ci[1]<0)
        result["status"]="recovery_debt_supported" if supported else "recovery_debt_not_supported"
        result["primary"]={
            "recovered_group_coefficient":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":int(len(vals)),
            "bootstrap_attempts":int(attempts),
            "supported":supported,
        }
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen recovered/control sequence or node minima were not met."

    d.to_csv(outdir/"recovery_debt_sequences.csv",index=False)
    q.to_csv(outdir/"recovery_debt_point_year_bb.csv",index=False)
    pd.DataFrame(byseg).to_csv(outdir/"recovery_debt_by_segment.csv",index=False)
    (outdir/"recovery_debt_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+chr(10))
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_recovery_debt"))
    p.add_argument("--out",type=Path,default=Path("results/generated_recovery_debt"))
    a=p.parse_args(); main(a.input,a.out)
