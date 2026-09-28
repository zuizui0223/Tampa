#!/usr/bin/env python3
"""Three-year exact-point test of a community recovery-scaffold hypothesis.

Frozen design: results/community_recovery_scaffold_v1_contract.json

Sequence:
t-1 Thalassia present -> t Thalassia absent -> t+1 same point observed.
Compare t+1 recorded Thalassia return when t retains another seagrass versus
when t is seagrass-bare. Loss year 2016 is excluded from the primary endpoint.
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
C=json.loads((ROOT/"results/community_recovery_scaffold_v1_contract.json").read_text())

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
LOSS0,LOSS1=[int(x) for x in C["three_year_sequence"]["primary_loss_years"]]
BOOT=int(C["implementation_freeze"]["bootstrap_replicates"])
SEED=int(C["implementation_freeze"]["random_seed"])
MIN_EVENTS=int(C["hypothesis"]["minimum_events_per_group"])
MIN_NODES=int(C["hypothesis"]["minimum_nodes_per_group"])


def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def fetch(spec:dict)->bytes:
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-recovery-scaffold/1.0"})
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
            points[eid]={"parent_id":pid,"point_id":row["locationID"].strip()}
        else:
            raise RuntimeError(f"unsupported event type: {typ}")
    eligible={pid for pid in parents if len(children.get(pid,[]))>=3}
    points={eid:x for eid,x in points.items() if x["parent_id"] in eligible}
    return {pid:parents[pid] for pid in eligible},children,points


def parse_taxa(data:bytes,point_ids:set[str]):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    taxa=defaultdict(set)
    source_counts=defaultdict(int)
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
        source_counts[sci]+=1
    return taxa,dict(sorted(source_counts.items()))


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
        names=set(x for x in sets[0].split(";") if x)
        rows.append({
            "point_id":str(point),
            "node_id":nodes[0],
            "water_body":wb[0],
            "year":int(year),
            "taxon_set":sets[0],
            "thalassia_present":THALASSIA in names,
            "any_seagrass_present":bool(names),
            "alternative_taxa":";".join(sorted(x for x in names if x!=THALASSIA)),
            "visits_in_year":int(g["unit_id"].nunique()),
        })
    return pd.DataFrame(rows).sort_values(["point_id","year"]).reset_index(drop=True),ambiguous


def build_three_year_sequences(py:pd.DataFrame,loss_year0:int,loss_year1:int):
    rows=[]
    d=py[py["water_body"].isin(SEGMENTS)].copy()
    by={(str(r.point_id),int(r.year)):r for r in d.itertuples(index=False)}
    for (point,year),mid in sorted(by.items(),key=lambda kv:(kv[0][0],kv[0][1])):
        if not (loss_year0<=year<=loss_year1):
            continue
        left=by.get((point,year-1))
        right=by.get((point,year+1))
        if left is None or right is None:
            continue
        if not bool(left.thalassia_present) or bool(mid.thalassia_present):
            continue
        group="other_seagrass" if bool(mid.any_seagrass_present) else "bare"
        rows.append({
            "point_id":point,
            "node_id":str(mid.node_id),
            "water_body":str(mid.water_body),
            "source_year":int(year-1),
            "loss_year":int(year),
            "followup_year":int(year+1),
            "loss_year_group":group,
            "loss_year_alternative_taxa":str(mid.alternative_taxa),
            "thalassia_return":bool(right.thalassia_present),
            "followup_taxon_set":str(right.taxon_set),
        })
    return pd.DataFrame(rows)


def summarize_group(d:pd.DataFrame,label:str):
    g=d[d["loss_year_group"]==label].copy()
    return {
        "events":int(len(g)),
        "nodes":int(g["node_id"].nunique()),
        "thalassia_returns":int(g["thalassia_return"].sum()),
        "return_fraction":float(g["thalassia_return"].mean()) if len(g) else None,
    }


def bootstrap_primary(seq:pd.DataFrame):
    occ=summarize_group(seq,"other_seagrass")
    bare=summarize_group(seq,"bare")
    estimable=bool(
        occ["events"]>=MIN_EVENTS and bare["events"]>=MIN_EVENTS
        and occ["nodes"]>=MIN_NODES and bare["nodes"]>=MIN_NODES
    )
    diff=(
        float(occ["return_fraction"]-bare["return_fraction"])
        if occ["return_fraction"] is not None and bare["return_fraction"] is not None
        else None
    )
    out={
        "loss_year_other_seagrass":occ,
        "loss_year_bare":bare,
        "risk_difference_other_minus_bare":diff,
        "estimable":estimable,
    }
    if not estimable:
        out.update({"bootstrap_ci95":None,"supported":False})
        return out

    nodes=sorted(seq["node_id"].unique())
    by={n:seq[seq["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    while len(vals)<BOOT and attempts<BOOT*20:
        attempts+=1
        sampled=rng.choice(nodes,size=len(nodes),replace=True)
        dd=pd.concat([by[n] for n in sampled],ignore_index=True)
        o=dd[dd["loss_year_group"]=="other_seagrass"]
        b=dd[dd["loss_year_group"]=="bare"]
        if len(o)==0 or len(b)==0:
            continue
        vals.append(float(o["thalassia_return"].mean()-b["thalassia_return"].mean()))
    if len(vals)<BOOT:
        raise RuntimeError(f"insufficient valid bootstrap replicates: {len(vals)}")
    ci=np.quantile(np.asarray(vals,float),[0.025,0.975])
    out.update({
        "bootstrap_ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[0]>0),
    })
    return out


def segment_summary(seq:pd.DataFrame):
    rows=[]
    for wb,g in seq.groupby("water_body"):
        for group in ["other_seagrass","bare"]:
            z=g[g["loss_year_group"]==group]
            rows.append({
                "water_body":wb,
                "loss_year_group":group,
                "events":int(len(z)),
                "nodes":int(z["node_id"].nunique()),
                "returns":int(z["thalassia_return"].sum()),
                "return_fraction":float(z["thalassia_return"].mean()) if len(z) else None,
            })
    return pd.DataFrame(rows)


def taxon_summary(seq:pd.DataFrame):
    rows=[]
    occ=seq[seq["loss_year_group"]=="other_seagrass"].copy()
    taxa=defaultdict(lambda:{"events":0,"returns":0})
    for r in occ.to_dict("records"):
        names=set(x for x in str(r["loss_year_alternative_taxa"]).split(";") if x)
        for taxon in names:
            taxa[taxon]["events"]+=1
            taxa[taxon]["returns"]+=int(bool(r["thalassia_return"]))
    for taxon,z in sorted(taxa.items(),key=lambda kv:(-kv[1]["events"],kv[0])):
        rows.append({
            "loss_year_taxon":taxon,
            "events":int(z["events"]),
            "returns":int(z["returns"]),
            "return_fraction":float(z["returns"]/z["events"]),
        })
    return pd.DataFrame(rows)


def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    raw={k:fetch(v) for k,v in FILES.items()}
    parents,children,points=parse_event(raw["event"])
    taxa,source_taxa=parse_taxa(raw["occurrence"],set(points))
    pv=build_point_visits(parents,children,points,taxa)
    py,ambiguous=consensus_point_year(pv)

    primary=build_three_year_sequences(py,LOSS0,LOSS1)
    sensitivity_2016=build_three_year_sequences(py,2016,2016)
    result_primary=bootstrap_primary(primary)
    seg=segment_summary(primary)
    tax=taxon_summary(primary)

    result={
        "schema":"tampa.community_recovery_scaffold_v1.result",
        "status":"completed_posthoc_exploratory",
        "contract":"results/community_recovery_scaffold_v1_contract.json",
        "registry":{
            "eligible_visits":int(len(parents)),
            "stable_nodes":int(pv["node_id"].nunique()),
            "point_visit_rows":int(len(pv)),
            "consensus_point_years":int(len(py)),
            "ambiguous_complete_taxon_set_point_years_excluded":int(ambiguous),
            "primary_three_year_sequences":int(len(primary)),
            "primary_nodes":int(primary["node_id"].nunique()) if len(primary) else 0,
            "sensitivity_2016_sequences":int(len(sensitivity_2016)),
        },
        "source_present_alismatales_taxa":source_taxa,
        "primary":result_primary,
        "by_segment":seg.to_dict("records"),
        "by_loss_year_taxon":tax.to_dict("records"),
        "sensitivity_2016":{
            "other_seagrass":summarize_group(sensitivity_2016,"other_seagrass"),
            "bare":summarize_group(sensitivity_2016,"bare"),
        },
        "interpretation":(
            "Support indicates that retaining another seagrass during an exact-point Thalassia non-detection predicts greater one-year recorded Thalassia return than becoming seagrass-bare, consistent with a recovery-scaffold candidate state."
        ),
        "claim_boundary":C["claim_boundary"],
    }

    pv.to_csv(outdir/"recovery_scaffold_point_visits.csv",index=False)
    py.to_csv(outdir/"recovery_scaffold_point_year_consensus.csv",index=False)
    primary.to_csv(outdir/"recovery_scaffold_three_year_sequences.csv",index=False)
    sensitivity_2016.to_csv(outdir/"recovery_scaffold_2016_sensitivity.csv",index=False)
    seg.to_csv(outdir/"recovery_scaffold_by_segment.csv",index=False)
    tax.to_csv(outdir/"recovery_scaffold_by_loss_year_taxon.csv",index=False)
    (outdir/"community_recovery_scaffold_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_recovery_scaffold"))
    a=p.parse_args()
    main(a.out)
