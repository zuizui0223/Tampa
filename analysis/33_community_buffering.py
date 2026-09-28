#!/usr/bin/env python3
"""Community buffering and exact-point turnover in Tampa Bay seagrass.

Post-hoc exploratory ecological test frozen in results/community_buffering_v1_contract.json.

Two questions:
1. Does occupancy by non-Thalassia seagrasses buffer total seagrass point occupancy
   while Thalassia frequency declines in Lower Tampa Bay?
2. When an exact stable meter mark loses Thalassia between consecutive years, is
   it more often occupied by another seagrass in Lower Tampa Bay than in Old +
   Middle Tampa Bay?

All seagrass occupancy is defined taxonomically as present Alismatales rows in the
pinned Darwin Core occurrence table, rather than by summing species frequencies.
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
C=json.loads((ROOT/"results/community_buffering_v1_contract.json").read_text())

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
ORDER="Alismatales"
PRIMARY_SEGMENT="Lower Tampa Bay"
COMPARISON={"Old Tampa Bay","Middle Tampa Bay"}
H1_BOOT=int(C["implementation_freeze"]["H1_bootstrap_replicates"])
H2_BOOT=int(C["implementation_freeze"]["H2_bootstrap_replicates"])
SEED=int(C["implementation_freeze"]["random_seed"])


def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-community-buffering/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(spec["size"]+1)
    if len(data)!=spec["size"]:
        raise RuntimeError(f"source size drift {spec['url']} {len(data)}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError(f"source blob drift {spec['url']}")
    return data


def parse_event(data:bytes):
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
                "unit_id":eid,
                "node_id":row["locationID"].strip(),
                "year":int(dt.year),
                "date":dt.date().isoformat(),
                "water_body":row["waterBody"].strip(),
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            point_id=row["locationID"].strip()
            points[eid]={
                "event_id":eid,
                "parent_id":pid,
                "point_id":point_id,
            }
            children[pid].append(eid)
        else:
            raise RuntimeError(f"unsupported event type {typ}")
    eligible={pid for pid,p in parents.items() if len(children.get(pid,[]))>=3}
    points={eid:x for eid,x in points.items() if x["parent_id"] in eligible}
    child_to_parent={eid:x["parent_id"] for eid,x in points.items()}
    return {pid:parents[pid] for pid in eligible},points,children,child_to_parent


def parse_occurrence(data:bytes, point_events:set[str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    state=defaultdict(lambda:{"thalassia":False,"seagrass_names":set()})
    for row in reader:
        eid=row["eventID"].strip()
        if eid not in point_events:
            continue
        if row["occurrenceStatus"].strip()!="present":
            continue
        if row["order"].strip()!=ORDER:
            continue
        sci=row["scientificName"].strip()
        if not sci:
            continue
        state[eid]["seagrass_names"].add(sci)
        if sci==THALASSIA:
            state[eid]["thalassia"]=True
    return state


def build_visit_panel(parents,points,children,occ):
    rows=[]
    point_rows=[]
    for pid,parent in sorted(parents.items()):
        eids=[eid for eid in children[pid] if eid in points]
        if len(eids)<3:
            continue
        t=0; anysg=0; alt_only=0
        for eid in eids:
            st=occ.get(eid,{"thalassia":False,"seagrass_names":set()})
            th=bool(st["thalassia"])
            names=set(st["seagrass_names"])
            any_present=bool(names)
            alt_names=sorted(x for x in names if x!=THALASSIA)
            non_thal_only=bool(any_present and not th)
            t+=int(th); anysg+=int(any_present); alt_only+=int(non_thal_only)
            point_rows.append({
                **parent,
                "point_id":points[eid]["point_id"],
                "thalassia_present":th,
                "any_seagrass_present":any_present,
                "non_thalassia_only_present":non_thal_only,
                "alternative_species":";".join(alt_names),
            })
        n=len(eids)
        rows.append({
            **parent,
            "child_point_count":n,
            "thalassia_frequency":t/n,
            "any_seagrass_frequency":anysg/n,
            "non_thalassia_only_frequency":alt_only/n,
        })
    return pd.DataFrame(rows),pd.DataFrame(point_rows)


def annualize_visit(visit:pd.DataFrame):
    annual=(visit.groupby(["node_id","year"],as_index=False)
      .agg(
        water_body=("water_body","first"),
        date=("date","first"),
        visits=("unit_id","size"),
        child_point_count=("child_point_count","mean"),
        thalassia_frequency=("thalassia_frequency","mean"),
        any_seagrass_frequency=("any_seagrass_frequency","mean"),
        non_thalassia_only_frequency=("non_thalassia_only_frequency","mean"),
      )
      .sort_values(["node_id","year"]))
    dt=pd.to_datetime(annual["date"])
    doy=dt.dt.dayofyear.to_numpy(float)
    annual["sin_doy"]=np.sin(2*np.pi*(doy-1)/365.2425)
    annual["cos_doy"]=np.cos(2*np.pi*(doy-1)/365.2425)
    annual["log_points"]=np.log(annual["child_point_count"].astype(float))
    return annual


def slope(frame:pd.DataFrame,metric:str,min_years=5):
    cols=["node_id","year","sin_doy","cos_doy","log_points",metric]
    d=frame[cols].dropna().copy()
    counts=d.groupby("node_id").size()
    nodes=sorted(counts[counts>=min_years].index.tolist())
    d=d[d["node_id"].isin(nodes)].copy()
    if len(nodes)<3:
        return None
    vars_=["year","sin_doy","cos_doy","log_points"]
    cross={}
    for node,g in d.groupby("node_id"):
        x=g[vars_].to_numpy(float); y=g[metric].to_numpy(float)
        x=x-x.mean(axis=0); y=y-y.mean()
        cross[node]=(x.T@x,x.T@y)
    def est(sel):
        xtx=np.sum([cross[n][0] for n in sel],axis=0)
        xty=np.sum([cross[n][1] for n in sel],axis=0)
        return np.linalg.pinv(xtx)@xty
    beta=est(nodes)
    rng=np.random.default_rng(SEED)
    vals=np.empty(H1_BOOT,float)
    for i in range(H1_BOOT):
        vals[i]=est(rng.choice(nodes,size=len(nodes),replace=True).tolist())[0]
    ci=np.quantile(vals,[.025,.975])
    return {
        "nodes":len(nodes),"rows":int(len(d)),
        "year_slope":float(beta[0]),
        "ci95":[float(ci[0]),float(ci[1])],
    }


def consensus_point_year(points:pd.DataFrame):
    rows=[]
    excluded=0
    for (point_id,year),g in points.groupby(["point_id","year"]):
        vals=g[["thalassia_present","any_seagrass_present","non_thalassia_only_present"]].drop_duplicates()
        if len(vals)!=1:
            excluded+=1
            continue
        wb=g["water_body"].iloc[0]
        node=g["node_id"].iloc[0]
        alt=set()
        for x in g["alternative_species"].fillna(""):
            alt.update(v for v in str(x).split(";") if v)
        r=vals.iloc[0]
        rows.append({
            "point_id":point_id,"node_id":node,"year":int(year),"water_body":wb,
            "thalassia_present":bool(r["thalassia_present"]),
            "any_seagrass_present":bool(r["any_seagrass_present"]),
            "non_thalassia_only_present":bool(r["non_thalassia_only_present"]),
            "alternative_species":";".join(sorted(alt)),
            "visits_in_year":int(g["unit_id"].nunique()),
        })
    return pd.DataFrame(rows),excluded


def point_loss_transitions(py:pd.DataFrame):
    rows=[]
    for point,g in py.groupby("point_id"):
        recs=g.sort_values("year").to_dict("records")
        for a,b in zip(recs[:-1],recs[1:]):
            if int(b["year"])!=int(a["year"])+1:
                continue
            if not (2016<=int(b["year"])<=2025):
                continue
            if not bool(a["thalassia_present"]) or bool(b["thalassia_present"]):
                continue
            rows.append({
                "point_id":point,
                "node_id":a["node_id"],
                "water_body":a["water_body"],
                "source_year":int(a["year"]),
                "target_year":int(b["year"]),
                "replacement_by_other_seagrass":bool(b["any_seagrass_present"]),
                "target_alternative_species":b["alternative_species"],
            })
    return pd.DataFrame(rows)


def replacement_fraction(d:pd.DataFrame):
    if len(d)==0:
        return math.nan
    return float(d["replacement_by_other_seagrass"].mean())


def bootstrap_difference(losses:pd.DataFrame):
    lower=losses[losses["water_body"]==PRIMARY_SEGMENT].copy()
    comp=losses[losses["water_body"].isin(COMPARISON)].copy()
    ln=sorted(lower["node_id"].unique()); cn=sorted(comp["node_id"].unique())
    min_events=int(C["hypotheses"]["H2_exact_point_turnover"]["minimum_loss_events_per_group"])
    min_nodes=int(C["hypotheses"]["H2_exact_point_turnover"]["minimum_nodes_with_loss_per_group"])
    estimable=bool(len(lower)>=min_events and len(comp)>=min_events and len(ln)>=min_nodes and len(cn)>=min_nodes)
    base={
        "lower_events":int(len(lower)),"comparison_events":int(len(comp)),
        "lower_nodes":int(len(ln)),"comparison_nodes":int(len(cn)),
        "lower_replacement_fraction":replacement_fraction(lower),
        "comparison_replacement_fraction":replacement_fraction(comp),
        "estimable":estimable,
    }
    if not estimable:
        base.update({"difference":None,"ci95":None,"supported":False})
        return base
    diff=base["lower_replacement_fraction"]-base["comparison_replacement_fraction"]
    rng=np.random.default_rng(SEED+1)
    boots=np.empty(H2_BOOT,float)
    by_l={n:lower[lower["node_id"]==n] for n in ln}
    by_c={n:comp[comp["node_id"]==n] for n in cn}
    for i in range(H2_BOOT):
        ls=rng.choice(ln,size=len(ln),replace=True)
        cs=rng.choice(cn,size=len(cn),replace=True)
        lv=pd.concat([by_l[n] for n in ls],ignore_index=True)
        cv=pd.concat([by_c[n] for n in cs],ignore_index=True)
        boots[i]=replacement_fraction(lv)-replacement_fraction(cv)
    ci=np.quantile(boots,[.025,.975])
    base.update({
        "difference_lower_minus_comparison":float(diff),
        "ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[0]>0),
    })
    return base


def species_fates(losses:pd.DataFrame):
    rows=[]
    for wb,g in losses.groupby("water_body"):
        counts=defaultdict(int)
        for x in g["target_alternative_species"].fillna(""):
            vals=[v for v in str(x).split(";") if v]
            if not vals:
                counts["no_other_seagrass"]+=1
            else:
                for v in set(vals):
                    counts[v]+=1
        for name,n in sorted(counts.items()):
            rows.append({"water_body":wb,"target_fate":name,"events":int(n)})
    return pd.DataFrame(rows)


def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    raw={k:fetch(v) for k,v in FILES.items()}
    parents,points,children,child_to_parent=parse_event(raw["event"])
    occ=parse_occurrence(raw["occurrence"],set(points))
    visit,point_visit=build_visit_panel(parents,points,children,occ)
    annual=annualize_visit(visit)

    post=annual[annual["year"].between(2016,2025)].copy()
    slope_results={}
    for wb in sorted(post["water_body"].unique()):
        g=post[post["water_body"]==wb]
        slope_results[wb]={m:slope(g,m) for m in [
            "thalassia_frequency","any_seagrass_frequency","non_thalassia_only_frequency"
        ]}

    lower=slope_results.get(PRIMARY_SEGMENT,{})
    t=lower.get("thalassia_frequency")
    any_=lower.get("any_seagrass_frequency")
    alt=lower.get("non_thalassia_only_frequency")
    h1_estimable=all(x is not None for x in [t,any_,alt])
    h1_support=False
    buffering_fraction=None
    if h1_estimable:
        if abs(t["year_slope"])>0:
            buffering_fraction=float(1-abs(any_["year_slope"])/abs(t["year_slope"]))
        h1_support=bool(
            t["ci95"][1]<0
            and alt["ci95"][0]>0
            and abs(any_["year_slope"])<abs(t["year_slope"])
        )

    py,ambiguous=consensus_point_year(point_visit)
    repeated_points=int((py.groupby("point_id")["year"].nunique()>=2).sum())
    losses=point_loss_transitions(py)
    h2=bootstrap_difference(losses)
    fates=species_fates(losses)

    result={
        "schema":"tampa.community_buffering_v1.result",
        "status":"completed_posthoc_exploratory",
        "contract":"results/community_buffering_v1_contract.json",
        "registry":{
            "eligible_visits":int(len(visit)),
            "stable_nodes":int(annual["node_id"].nunique()),
            "point_visit_rows":int(len(point_visit)),
            "consensus_point_years":int(len(py)),
            "ambiguous_point_years_excluded":int(ambiguous),
            "repeated_stable_points":repeated_points,
            "thalassia_loss_point_transitions_post2016":int(len(losses)),
        },
        "H1_transect_occupancy_buffering":{
            "primary_segment":PRIMARY_SEGMENT,
            "slopes":lower,
            "buffering_fraction_abs_slope_reduction":buffering_fraction,
            "supported":h1_support,
            "all_segments":slope_results,
        },
        "H2_exact_point_turnover":h2,
        "interpretation":(
            "Community buffering is supported only if focal Thalassia declines while non-Thalassia-only occupancy rises and total seagrass occupancy changes less, with exact-point Thalassia losses in Lower Tampa Bay also more likely to remain occupied by another seagrass than comparable losses in Old and Middle Tampa Bay."
        ),
        "claim_boundary":C["claim_boundary"],
    }

    visit.to_csv(outdir/"community_buffering_visit.csv",index=False)
    annual.to_csv(outdir/"community_buffering_annual.csv",index=False)
    py.to_csv(outdir/"community_buffering_point_year_consensus.csv",index=False)
    losses.to_csv(outdir/"community_buffering_thalassia_point_losses.csv",index=False)
    fates.to_csv(outdir/"community_buffering_target_species_fates.csv",index=False)
    (outdir/"community_buffering_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_community_buffering"))
    a=p.parse_args()
    main(a.out)
