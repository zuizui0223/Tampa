#!/usr/bin/env python3
"""Exact-point test of pre-existing seagrass community insurance.

Consumes point-year consensus states from analysis/33_community_buffering.py.
No endpoint or grouping is selected here; all choices are frozen in
results/community_insurance_v1_contract.json.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/community_insurance_v1_contract.json").read_text())
SEED=2026092807
BOOT=5000


def species_set(x)->set[str]:
    if pd.isna(x):
        return set()
    return {v for v in str(x).split(";") if v}


def build_transitions(py:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for point,g in py.groupby("point_id"):
        recs=g.sort_values("year").to_dict("records")
        for a,b in zip(recs[:-1],recs[1:]):
            sy=int(a["year"]); ty=int(b["year"])
            if ty!=sy+1 or not (2016<=ty<=2025):
                continue
            if not bool(a["thalassia_present"]) or bool(b["thalassia_present"]):
                continue
            source_alt=species_set(a.get("alternative_species",""))
            target_alt=species_set(b.get("alternative_species",""))
            target_any=bool(b["any_seagrass_present"])
            retained=source_alt & target_alt
            novel=target_alt - source_alt
            rows.append({
                "point_id":point,
                "node_id":a["node_id"],
                "water_body":a["water_body"],
                "source_year":sy,
                "target_year":ty,
                "source_mixed":bool(source_alt),
                "source_alternative_species":";".join(sorted(source_alt)),
                "target_any_seagrass_present":target_any,
                "target_alternative_species":";".join(sorted(target_alt)),
                "retained_alternative_species":";".join(sorted(retained)),
                "new_alternative_species":";".join(sorted(novel)),
                "retained_species_any":bool(retained),
                "new_species_any":bool(novel),
                "target_fate_class":(
                    "bare" if not target_any else
                    "retained_only" if retained and not novel else
                    "retained_plus_new" if retained and novel else
                    "new_only"
                ),
            })
    return pd.DataFrame(rows)


def frac(d:pd.DataFrame,col:str)->float:
    return float(d[col].astype(bool).mean()) if len(d) else math.nan


def h3a(trans:pd.DataFrame)->dict:
    mixed=trans[trans["source_mixed"]].copy()
    alone=trans[~trans["source_mixed"]].copy()
    mixed_nodes=set(mixed["node_id"]); alone_nodes=set(alone["node_id"])
    cfg=C["hypotheses"]["H3a_source_mixture_insurance"]
    min_events=int(cfg["minimum_events_per_group"]); min_nodes=int(cfg["minimum_nodes_per_group"])
    estimable=bool(
        len(mixed)>=min_events and len(alone)>=min_events
        and len(mixed_nodes)>=min_nodes and len(alone_nodes)>=min_nodes
    )
    out={
        "source_mixed_events":int(len(mixed)),
        "source_thalassia_only_events":int(len(alone)),
        "source_mixed_nodes":int(len(mixed_nodes)),
        "source_thalassia_only_nodes":int(len(alone_nodes)),
        "mixed_target_occupancy_fraction":frac(mixed,"target_any_seagrass_present"),
        "thalassia_only_target_occupancy_fraction":frac(alone,"target_any_seagrass_present"),
        "estimable":estimable,
        "supported":False,
        "difference_mixed_minus_thalassia_only":None,
        "ci95":None,
    }
    if not estimable:
        return out
    obs=out["mixed_target_occupancy_fraction"]-out["thalassia_only_target_occupancy_fraction"]
    nodes=sorted(trans["node_id"].unique())
    by_node={n:trans[trans["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    for _ in range(BOOT):
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        d=pd.concat([by_node[n] for n in chosen],ignore_index=True)
        m=d[d["source_mixed"]]; a=d[~d["source_mixed"]]
        if len(m)==0 or len(a)==0:
            continue
        vals.append(frac(m,"target_any_seagrass_present")-frac(a,"target_any_seagrass_present"))
    arr=np.asarray(vals,float)
    ci=np.quantile(arr,[.025,.975])
    out.update({
        "difference_mixed_minus_thalassia_only":float(obs),
        "ci95":[float(ci[0]),float(ci[1])],
        "bootstrap_replicates_used":int(len(arr)),
        "supported":bool(ci[0]>0),
    })
    return out


def h3b(trans:pd.DataFrame)->dict:
    d=trans[trans["target_any_seagrass_present"]].copy()
    nodes=set(d["node_id"])
    cfg=C["hypotheses"]["H3b_persistence_not_colonization"]
    estimable=bool(len(d)>=int(cfg["minimum_events"]) and len(nodes)>=int(cfg["minimum_nodes"]))
    out={
        "target_occupied_events":int(len(d)),
        "nodes":int(len(nodes)),
        "retained_species_fraction":frac(d,"retained_species_any"),
        "new_only_fraction":float((d["target_fate_class"]=="new_only").mean()) if len(d) else math.nan,
        "retained_only_fraction":float((d["target_fate_class"]=="retained_only").mean()) if len(d) else math.nan,
        "retained_plus_new_fraction":float((d["target_fate_class"]=="retained_plus_new").mean()) if len(d) else math.nan,
        "estimable":estimable,
        "supported":False,
        "ci95":None,
    }
    if not estimable:
        return out
    nodes=sorted(nodes)
    by_node={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED+1)
    vals=np.empty(BOOT,float)
    for i in range(BOOT):
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        x=pd.concat([by_node[n] for n in chosen],ignore_index=True)
        vals[i]=frac(x,"retained_species_any")
    ci=np.quantile(vals,[.025,.975])
    out.update({
        "ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[0]>0.5),
    })
    return out


def descriptives(trans:pd.DataFrame):
    rows=[]
    for wb,g in trans.groupby("water_body"):
        occ=g[g["target_any_seagrass_present"]]
        rows.append({
            "water_body":wb,
            "events":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "source_mixed_fraction":frac(g,"source_mixed"),
            "target_occupancy_fraction":frac(g,"target_any_seagrass_present"),
            "retained_species_fraction_given_target_occupied":frac(occ,"retained_species_any"),
            "new_only_fraction_given_target_occupied":float((occ["target_fate_class"]=="new_only").mean()) if len(occ) else math.nan,
        })
    return pd.DataFrame(rows)


def species_fates(trans:pd.DataFrame):
    counts=Counter()
    for r in trans.itertuples():
        src=species_set(r.source_alternative_species)
        tgt=species_set(r.target_alternative_species)
        for sp in tgt:
            status="retained" if sp in src else "new"
            counts[(r.water_body,sp,status)]+=1
    rows=[
        {"water_body":wb,"species":sp,"status":status,"events":n}
        for (wb,sp,status),n in sorted(counts.items())
    ]
    return pd.DataFrame(rows)


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    required={
        "point_id","node_id","year","water_body","thalassia_present",
        "any_seagrass_present","alternative_species"
    }
    missing=required.difference(py.columns)
    if missing:
        raise RuntimeError(f"missing point-year columns: {sorted(missing)}")
    if py["point_id"].nunique()<1000:
        raise RuntimeError("stable-point registry unexpectedly small")

    trans=build_transitions(py)
    if len(trans)==0:
        raise RuntimeError("no eligible exact-point Thalassia-loss transitions")

    a=h3a(trans)
    b=h3b(trans)
    bay=descriptives(trans)
    species=species_fates(trans)

    status=(
        "both_insurance_hypotheses_supported" if a["supported"] and b["supported"] else
        "source_mixture_insurance_supported" if a["supported"] else
        "preexisting_species_persistence_supported" if b["supported"] else
        "community_insurance_not_supported"
    )
    result={
        "schema":"tampa.community_insurance_v1.result",
        "status":status,
        "contract":"results/community_insurance_v1_contract.json",
        "registry":{
            "point_years":int(len(py)),
            "stable_points":int(py["point_id"].nunique()),
            "eligible_thalassia_loss_transitions":int(len(trans)),
            "nodes_with_loss":int(trans["node_id"].nunique()),
        },
        "H3a_source_mixture_insurance":a,
        "H3b_persistence_not_colonization":b,
        "interpretation":(
            "The analysis distinguishes two forms of community insurance: whether pre-existing mixed-species points are less likely to become seagrass-bare after focal loss, and whether target alternative occupancy mainly retains species already present before focal loss rather than appearing only afterward."
        ),
        "claim_boundary":C["claim_boundary"],
    }
    trans.to_csv(outdir/"community_insurance_transitions.csv",index=False)
    bay.to_csv(outdir/"community_insurance_by_segment.csv",index=False)
    species.to_csv(outdir/"community_insurance_species_fates.csv",index=False)
    (outdir/"community_insurance_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_community_insurance"))
    p.add_argument("--out",type=Path,default=Path("results/generated_community_insurance"))
    a=p.parse_args()
    main(a.input,a.out)
