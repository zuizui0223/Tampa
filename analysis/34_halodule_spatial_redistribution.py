#!/usr/bin/env python3
"""Exact-point test of Halodule spatial redistribution versus direct Thalassia takeover.

Frozen design: results/halodule_spatial_redistribution_v1_contract.json

The endpoint is built directly from pinned Darwin Core Event + Occurrence tables.
Point-years are eligible only when repeated visits agree separately on Thalassia
and Halodule presence/absence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/halodule_spatial_redistribution_v1_contract.json").read_text())

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
    "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
    "occurrence":{"url":f"{BASE}/occurrence.csv","size":12508487,"blob":"d34aeb5aedb72459d1e04059629cb09450df929e"},
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
THALASSIA="Thalassia testudinum"
HALODULE="Halodule wrightii"
SEGMENT=str(C["primary_segment"])
Y0,Y1=[int(x) for x in C["primary_period"]]
BOOT=int(C["implementation_freeze"]["bootstrap_replicates"])
SEED=int(C["implementation_freeze"]["random_seed"])


def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def fetch(spec:dict)->bytes:
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-halodule-redistribution/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(int(spec["size"])+1)
    if len(data)!=int(spec["size"]):
        raise RuntimeError(f"source size drift: {spec['url']} -> {len(data)}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError(f"source blob drift: {spec['url']}")
    return data


def parse_event(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EVENT_HEADER:
        raise RuntimeError("event header drift")
    parents={}
    children=defaultdict(list)
    points={}
    for row in reader:
        typ=row["eventType"].strip()
        eid=row["eventID"].strip()
        if typ=="Transect":
            dt=datetime.strptime(row["eventDate"],"%Y-%m-%d")
            parents[eid]={
                "unit_id":eid,
                "node_id":row["locationID"].strip(),
                "water_body":row["waterBody"].strip(),
                "year":int(dt.year),
                "date":dt.date().isoformat(),
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            children[pid].append(eid)
            points[eid]={
                "parent_id":pid,
                "point_id":row["locationID"].strip(),
            }
        else:
            raise RuntimeError(f"unsupported event type: {typ}")
    eligible={pid for pid in parents if len(children.get(pid,[]))>=3}
    points={eid:x for eid,x in points.items() if x["parent_id"] in eligible}
    return {pid:parents[pid] for pid in eligible},children,points


def parse_occurrence(data:bytes,point_ids:set[str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    state=defaultdict(lambda:{"thalassia":False,"halodule":False})
    focal_rows=0
    for row in reader:
        eid=row["eventID"].strip()
        if eid not in point_ids:
            continue
        if row["occurrenceStatus"].strip()!="present":
            continue
        sci=row["scientificName"].strip()
        if sci==THALASSIA:
            state[eid]["thalassia"]=True
            focal_rows+=1
        elif sci==HALODULE:
            state[eid]["halodule"]=True
            focal_rows+=1
    if focal_rows==0:
        raise RuntimeError("no Thalassia/Halodule present rows")
    return state


def point_visits(parents,children,points,state):
    rows=[]
    for pid,p in sorted(parents.items()):
        for eid in children[pid]:
            if eid not in points:
                continue
            st=state.get(eid,{"thalassia":False,"halodule":False})
            rows.append({
                **p,
                "point_id":points[eid]["point_id"],
                "thalassia_present":bool(st["thalassia"]),
                "halodule_present":bool(st["halodule"]),
            })
    return pd.DataFrame(rows)


def consensus_point_year(pv:pd.DataFrame):
    rows=[]
    ambiguous=0
    for (point,year),g in pv.groupby(["point_id","year"],sort=True):
        wb=sorted(set(g["water_body"].astype(str)))
        nodes=sorted(set(g["node_id"].astype(str)))
        if len(wb)!=1 or len(nodes)!=1:
            raise RuntimeError(f"point-year parent drift: {point} {year}")
        states=g[["thalassia_present","halodule_present"]].drop_duplicates()
        if len(states)!=1:
            ambiguous+=1
            continue
        st=states.iloc[0]
        rows.append({
            "point_id":str(point),
            "node_id":nodes[0],
            "water_body":wb[0],
            "year":int(year),
            "thalassia_present":bool(st["thalassia_present"]),
            "halodule_present":bool(st["halodule_present"]),
            "visits_in_year":int(g["unit_id"].nunique()),
        })
    return pd.DataFrame(rows).sort_values(["point_id","year"]).reset_index(drop=True),ambiguous


def transitions(py:pd.DataFrame):
    rows=[]
    d=py[py["water_body"]==SEGMENT].copy()
    for point,g in d.groupby("point_id"):
        recs=g.sort_values("year").to_dict("records")
        for a,b in zip(recs[:-1],recs[1:]):
            if int(b["year"])!=int(a["year"])+1:
                continue
            if not (Y0<=int(b["year"])<=Y1):
                continue
            if bool(a["halodule_present"]):
                continue
            gained=bool(b["halodule_present"])
            direct=bool(
                gained and bool(a["thalassia_present"]) and not bool(b["thalassia_present"])
            )
            if not bool(a["thalassia_present"]) and not bool(b["thalassia_present"]):
                fate="gain_from_thalassia_absent_space" if gained else "no_gain_from_thalassia_absent_space"
            elif bool(a["thalassia_present"]) and bool(b["thalassia_present"]):
                fate="gain_with_thalassia_persistence" if gained else "no_gain_with_thalassia_persistence"
            elif bool(a["thalassia_present"]) and not bool(b["thalassia_present"]):
                fate="direct_takeover_candidate" if gained else "thalassia_loss_without_halodule_gain"
            else:
                fate="simultaneous_thalassia_gain" if gained else "thalassia_gain_without_halodule_gain"
            rows.append({
                "point_id":point,
                "node_id":a["node_id"],
                "source_year":int(a["year"]),
                "target_year":int(b["year"]),
                "source_thalassia_present":bool(a["thalassia_present"]),
                "target_thalassia_present":bool(b["thalassia_present"]),
                "halodule_gain":gained,
                "direct_takeover_candidate":direct,
                "fate":fate,
            })
    return pd.DataFrame(rows)


def bootstrap_direct_fraction(gain:pd.DataFrame):
    min_events=int(C["hypotheses"]["H1_direct_takeover_not_dominant"]["minimum_gain_events"])
    min_nodes=int(C["hypotheses"]["H1_direct_takeover_not_dominant"]["minimum_nodes_with_gain"])
    nodes=sorted(gain["node_id"].unique()) if len(gain) else []
    estimable=bool(len(gain)>=min_events and len(nodes)>=min_nodes)
    out={
        "gain_events":int(len(gain)),
        "nodes_with_gain":int(len(nodes)),
        "direct_takeover_events":int(gain["direct_takeover_candidate"].sum()) if len(gain) else 0,
        "direct_takeover_fraction":float(gain["direct_takeover_candidate"].mean()) if len(gain) else None,
        "estimable":estimable,
    }
    if not estimable:
        out.update({"bootstrap_ci95":None,"supported":False})
        return out
    by={n:gain[gain["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=np.empty(BOOT,dtype=float)
    for i in range(BOOT):
        sampled=rng.choice(nodes,size=len(nodes),replace=True)
        dd=pd.concat([by[n] for n in sampled],ignore_index=True)
        vals[i]=float(dd["direct_takeover_candidate"].mean())
    ci=np.quantile(vals,[0.025,0.975])
    out.update({
        "bootstrap_ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[1]<0.5),
    })
    return out


def bootstrap_gain_risk(trans:pd.DataFrame):
    absent=trans[~trans["source_thalassia_present"]].copy()
    present=trans[trans["source_thalassia_present"]].copy()
    min_t=int(C["hypotheses"]["H2_gain_prefers_non_thalassia_space"]["minimum_transitions_per_group"])
    min_n=int(C["hypotheses"]["H2_gain_prefers_non_thalassia_space"]["minimum_nodes_per_group"])
    an=sorted(absent["node_id"].unique())
    pn=sorted(present["node_id"].unique())
    estimable=bool(len(absent)>=min_t and len(present)>=min_t and len(an)>=min_n and len(pn)>=min_n)
    p_abs=float(absent["halodule_gain"].mean()) if len(absent) else None
    p_pre=float(present["halodule_gain"].mean()) if len(present) else None
    out={
        "source_thalassia_absent_transitions":int(len(absent)),
        "source_thalassia_absent_nodes":int(len(an)),
        "gain_probability_source_thalassia_absent":p_abs,
        "source_thalassia_present_transitions":int(len(present)),
        "source_thalassia_present_nodes":int(len(pn)),
        "gain_probability_source_thalassia_present":p_pre,
        "risk_difference_absent_minus_present":float(p_abs-p_pre) if p_abs is not None and p_pre is not None else None,
        "estimable":estimable,
    }
    if not estimable:
        out.update({"bootstrap_ci95":None,"supported":False})
        return out

    all_nodes=sorted(trans["node_id"].unique())
    by={n:trans[trans["node_id"]==n] for n in all_nodes}
    rng=np.random.default_rng(SEED+1)
    vals=[]
    attempts=0
    while len(vals)<BOOT and attempts<BOOT*20:
        attempts+=1
        sampled=rng.choice(all_nodes,size=len(all_nodes),replace=True)
        dd=pd.concat([by[n] for n in sampled],ignore_index=True)
        a=dd[~dd["source_thalassia_present"]]
        p=dd[dd["source_thalassia_present"]]
        if len(a)==0 or len(p)==0:
            continue
        vals.append(float(a["halodule_gain"].mean()-p["halodule_gain"].mean()))
    if len(vals)<BOOT:
        raise RuntimeError(f"insufficient valid node-bootstrap replicates: {len(vals)}")
    ci=np.quantile(np.asarray(vals,float),[0.025,0.975])
    out.update({
        "bootstrap_ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[0]>0),
    })
    return out


def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    raw={k:fetch(v) for k,v in FILES.items()}
    parents,children,points=parse_event(raw["event"])
    state=parse_occurrence(raw["occurrence"],set(points))
    pv=point_visits(parents,children,points,state)
    py,ambiguous=consensus_point_year(pv)
    tr=transitions(py)
    gain=tr[tr["halodule_gain"]].copy()

    h1=bootstrap_direct_fraction(gain)
    h2=bootstrap_gain_risk(tr)
    fate=gain.groupby("fate",as_index=False).agg(
        events=("point_id","size"),
        nodes=("node_id","nunique"),
    ).sort_values(["events","fate"],ascending=[False,True])
    if len(gain):
        fate["fraction_of_halodule_gains"]=fate["events"]/len(gain)
    else:
        fate["fraction_of_halodule_gains"]=0.0

    result={
        "schema":"tampa.halodule_spatial_redistribution_v1.result",
        "status":"completed_posthoc_exploratory",
        "contract":"results/halodule_spatial_redistribution_v1_contract.json",
        "registry":{
            "eligible_visits":int(len(parents)),
            "stable_nodes":int(pv["node_id"].nunique()),
            "point_visit_rows":int(len(pv)),
            "consensus_point_years":int(len(py)),
            "ambiguous_taxon_specific_point_years_excluded":int(ambiguous),
            "lower_eligible_source_halodule_absent_transitions":int(len(tr)),
            "lower_halodule_gain_events":int(len(gain)),
        },
        "H1_direct_takeover_not_dominant":h1,
        "H2_gain_prefers_non_thalassia_space":h2,
        "gain_fates":fate.to_dict("records"),
        "interpretation":(
            "If supported, the two frozen endpoints indicate that Lower Tampa Bay Halodule expansion is dominated by spatial redistribution into non-Thalassia space rather than point-for-point takeover of Thalassia meter marks."
        ),
        "claim_boundary":C["claim_boundary"],
    }

    pv.to_csv(outdir/"halodule_point_visits.csv",index=False)
    py.to_csv(outdir/"halodule_point_year_consensus.csv",index=False)
    tr.to_csv(outdir/"halodule_source_absent_transitions.csv",index=False)
    gain.to_csv(outdir/"halodule_gain_events.csv",index=False)
    fate.to_csv(outdir/"halodule_gain_fates.csv",index=False)
    (outdir/"halodule_spatial_redistribution_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_halodule_redistribution"))
    a=p.parse_args()
    main(a.out)
