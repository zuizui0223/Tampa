#!/usr/bin/env python3
"""Test whether alternative seagrass after Thalassia loss was already present.

Frozen design: results/preexisting_mixed_patch_v1_contract.json

The test follows exact stable meter marks across consecutive years. Point-years are
eligible only when repeated visits agree on the complete set of present Alismatales
scientificName values.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/preexisting_mixed_patch_v1_contract.json").read_text())

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
SEGMENTS=set(str(x) for x in C["primary_segments"])
Y0,Y1=[int(x) for x in C["primary_period"]]
BOOT=int(C["implementation_freeze"]["bootstrap_replicates"])
SEED=int(C["implementation_freeze"]["random_seed"])
MIN_EVENTS=int(C["hypothesis"]["minimum_events"])
MIN_NODES=int(C["hypothesis"]["minimum_nodes"])


def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def fetch(spec:dict)->bytes:
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-mixed-patch/1.0"})
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
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            children[pid].append(eid)
            points[eid]={
                "parent_id":pid,
                "point_id":row["locationID"].strip(),
            }
        else:
            raise RuntimeError(f"unsupported event type {typ}")
    eligible={pid for pid in parents if len(children.get(pid,[]))>=3}
    points={eid:x for eid,x in points.items() if x["parent_id"] in eligible}
    return {pid:parents[pid] for pid in eligible},children,points


def parse_taxa(data:bytes,point_ids:set[str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    taxa=defaultdict(set)
    names=defaultdict(int)
    for row in reader:
        eid=row["eventID"].strip()
        if eid not in point_ids:
            continue
        if row["occurrenceStatus"].strip()!="present":
            continue
        if row["order"].strip()!=ORDER:
            continue
        sci=row["scientificName"].strip()
        if not sci:
            continue
        taxa[eid].add(sci)
        names[sci]+=1
    return taxa,dict(sorted(names.items()))


def build_point_visits(parents,children,points,taxa):
    rows=[]
    for pid,p in sorted(parents.items()):
        for eid in children[pid]:
            if eid not in points:
                continue
            names=tuple(sorted(taxa.get(eid,set())))
            rows.append({
                **p,
                "point_id":points[eid]["point_id"],
                "taxon_set":";".join(names),
                "thalassia_present":THALASSIA in names,
                "any_seagrass_present":bool(names),
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
        sets=sorted(set(g["taxon_set"].astype(str)))
        if len(sets)!=1:
            ambiguous+=1
            continue
        taxa=sets[0]
        names=set(x for x in taxa.split(";") if x)
        rows.append({
            "point_id":str(point),
            "node_id":nodes[0],
            "water_body":wb[0],
            "year":int(year),
            "taxon_set":taxa,
            "thalassia_present":THALASSIA in names,
            "visits_in_year":int(g["unit_id"].nunique()),
        })
    return pd.DataFrame(rows).sort_values(["point_id","year"]).reset_index(drop=True),ambiguous


def alt_set(taxon_set:str)->set[str]:
    return {x for x in str(taxon_set).split(";") if x and x!=THALASSIA}


def replacement_events(py:pd.DataFrame):
    rows=[]
    d=py[py["water_body"].isin(SEGMENTS)].copy()
    for point,g in d.groupby("point_id"):
        recs=g.sort_values("year").to_dict("records")
        for a,b in zip(recs[:-1],recs[1:]):
            if int(b["year"])!=int(a["year"])+1:
                continue
            if not (Y0<=int(b["year"])<=Y1):
                continue
            if not bool(a["thalassia_present"]) or bool(b["thalassia_present"]):
                continue
            source_alt=alt_set(a["taxon_set"])
            target_alt=alt_set(b["taxon_set"])
            if not target_alt:
                continue
            persisted=sorted(source_alt & target_alt)
            new_only=sorted(target_alt-source_alt)
            rows.append({
                "point_id":point,
                "node_id":a["node_id"],
                "water_body":a["water_body"],
                "source_year":int(a["year"]),
                "target_year":int(b["year"]),
                "source_alternative_taxa":";".join(sorted(source_alt)),
                "target_alternative_taxa":";".join(sorted(target_alt)),
                "persisted_alternative_taxa":";".join(persisted),
                "new_target_only_taxa":";".join(new_only),
                "preexisting_persistence":bool(persisted),
                "de_novo_only":bool(not persisted),
            })
    return pd.DataFrame(rows)


def bootstrap_primary(events:pd.DataFrame):
    nodes=sorted(events["node_id"].unique()) if len(events) else []
    estimable=bool(len(events)>=MIN_EVENTS and len(nodes)>=MIN_NODES)
    frac=float(events["preexisting_persistence"].mean()) if len(events) else None
    out={
        "events":int(len(events)),
        "nodes":int(len(nodes)),
        "preexisting_persistence_events":int(events["preexisting_persistence"].sum()) if len(events) else 0,
        "de_novo_only_events":int(events["de_novo_only"].sum()) if len(events) else 0,
        "preexisting_persistence_fraction":frac,
        "estimable":estimable,
    }
    if not estimable:
        out.update({"bootstrap_ci95":None,"supported":False})
        return out

    by={n:events[events["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=np.empty(BOOT,dtype=float)
    for i in range(BOOT):
        sampled=rng.choice(nodes,size=len(nodes),replace=True)
        dd=pd.concat([by[n] for n in sampled],ignore_index=True)
        vals[i]=float(dd["preexisting_persistence"].mean())
    ci=np.quantile(vals,[0.025,0.975])
    out.update({
        "bootstrap_ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[0]>0.5),
    })
    return out


def by_segment(events:pd.DataFrame):
    rows=[]
    for wb,g in events.groupby("water_body"):
        rows.append({
            "water_body":wb,
            "events":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "preexisting_persistence_events":int(g["preexisting_persistence"].sum()),
            "de_novo_only_events":int(g["de_novo_only"].sum()),
            "preexisting_persistence_fraction":float(g["preexisting_persistence"].mean()),
        })
    return pd.DataFrame(rows)


def by_taxon(events:pd.DataFrame):
    counts=defaultdict(lambda:{"target_events":0,"persisted_events":0,"new_only_events":0})
    for r in events.to_dict("records"):
        source=alt_set(r["source_alternative_taxa"])
        target=alt_set(r["target_alternative_taxa"])
        for taxon in target:
            counts[taxon]["target_events"]+=1
            if taxon in source:
                counts[taxon]["persisted_events"]+=1
            else:
                counts[taxon]["new_only_events"]+=1
    rows=[]
    for taxon,z in sorted(counts.items(),key=lambda kv:(-kv[1]["target_events"],kv[0])):
        rows.append({
            "taxon":taxon,
            **z,
            "persisted_fraction_of_target_events":float(z["persisted_events"]/z["target_events"]),
        })
    return pd.DataFrame(rows)


def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    raw={k:fetch(v) for k,v in FILES.items()}
    parents,children,points=parse_event(raw["event"])
    taxa,source_taxa=parse_taxa(raw["occurrence"],set(points))
    pv=build_point_visits(parents,children,points,taxa)
    py,ambiguous=consensus_point_year(pv)
    events=replacement_events(py)
    primary=bootstrap_primary(events)
    seg=by_segment(events)
    tax=by_taxon(events)

    result={
        "schema":"tampa.preexisting_mixed_patch_v1.result",
        "status":"completed_posthoc_exploratory",
        "contract":"results/preexisting_mixed_patch_v1_contract.json",
        "registry":{
            "eligible_visits":int(len(parents)),
            "stable_nodes":int(pv["node_id"].nunique()),
            "point_visit_rows":int(len(pv)),
            "consensus_point_years":int(len(py)),
            "ambiguous_complete_taxon_set_point_years_excluded":int(ambiguous),
            "primary_replacement_events":int(len(events)),
            "primary_nodes":int(events["node_id"].nunique()) if len(events) else 0,
        },
        "source_present_alismatales_taxa":source_taxa,
        "primary":primary,
        "by_segment":seg.to_dict("records"),
        "by_target_taxon":tax.to_dict("records"),
        "interpretation":(
            "Support indicates that most alternative-seagrass occupancy observed one year after exact-point Thalassia loss was persistence of at least one alternative species already co-occurring at that meter mark, consistent with species-specific dropout from mixed patches rather than entirely de novo replacement."
        ),
        "claim_boundary":C["claim_boundary"],
    }

    pv.to_csv(outdir/"mixed_patch_point_visits.csv",index=False)
    py.to_csv(outdir/"mixed_patch_point_year_consensus.csv",index=False)
    events.to_csv(outdir/"mixed_patch_replacement_events.csv",index=False)
    seg.to_csv(outdir/"mixed_patch_by_segment.csv",index=False)
    tax.to_csv(outdir/"mixed_patch_by_target_taxon.csv",index=False)
    (outdir/"preexisting_mixed_patch_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_preexisting_mixed_patch"))
    a=p.parse_args()
    main(a.out)
