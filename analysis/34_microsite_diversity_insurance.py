#!/usr/bin/env python3
"""Test microsite diversity insurance after exact-point Thalassia loss.

Consumes the consensus stable-point annual states produced by
analysis/33_community_buffering.py. No new environmental variable or endpoint
selection occurs here; the post-hoc ecological hypotheses are frozen in
results/microsite_diversity_insurance_v1_contract.json.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/microsite_diversity_insurance_v1_contract.json").read_text())

START,END=[int(x) for x in C["primary_period"]]
H1=C["hypotheses"]["H1_microsite_insurance"]
H2=C["hypotheses"]["H2_persistence_component"]

H1_BOOT=int(H1["bootstrap_replicates"])
H2_BOOT=int(H2["bootstrap_replicates"])
H1_SEED=int(H1["random_seed"])
H2_SEED=int(H2["random_seed"])


def taxa_set(x)->set[str]:
    s="" if pd.isna(x) else str(x).strip()
    if not s:
        return set()
    return {v.strip() for v in s.split(";") if v.strip()}


def build_transitions(py:pd.DataFrame)->pd.DataFrame:
    required={
        "point_id","node_id","water_body","year",
        "thalassia_present","any_seagrass_present","alternative_species"
    }
    missing=required.difference(py.columns)
    if missing:
        raise RuntimeError(f"missing point-year columns: {sorted(missing)}")

    rows=[]
    for point_id,g in py.groupby("point_id",sort=True):
        recs=g.sort_values("year").to_dict("records")
        for a,b in zip(recs[:-1],recs[1:]):
            sy=int(a["year"]); ty=int(b["year"])
            if ty != sy+1:
                continue
            if sy < START or ty > END:
                continue
            if not bool(a["thalassia_present"]) or bool(b["thalassia_present"]):
                continue

            src=taxa_set(a["alternative_species"])
            tgt=taxa_set(b["alternative_species"])
            replacement=bool(b["any_seagrass_present"])
            if replacement != bool(tgt):
                raise RuntimeError(
                    f"target replacement/taxon-set disagreement: {point_id} {ty}"
                )

            source_class="mixed_source" if src else "pure_thalassia_source"
            inter=src & tgt
            novel=tgt-src
            persistent_component=bool(inter)
            novel_only_component=bool(tgt and not inter)

            rows.append({
                "point_id":point_id,
                "node_id":a["node_id"],
                "water_body":a["water_body"],
                "source_year":sy,
                "target_year":ty,
                "source_class":source_class,
                "source_alternative_species":";".join(sorted(src)),
                "target_alternative_species":";".join(sorted(tgt)),
                "target_replacement":int(replacement),
                "persistent_component":int(persistent_component),
                "novel_only_component":int(novel_only_component),
                "persistent_taxa":";".join(sorted(inter)),
                "novel_taxa":";".join(sorted(novel)),
            })
    return pd.DataFrame(rows)


def class_summary(d:pd.DataFrame,source_class:str)->dict:
    x=d[d["source_class"]==source_class]
    if len(x)==0:
        return {
            "events":0,"nodes":0,"replacement_fraction":None
        }
    return {
        "events":int(len(x)),
        "nodes":int(x["node_id"].nunique()),
        "replacement_fraction":float(x["target_replacement"].mean()),
    }


def bootstrap_h1(d:pd.DataFrame)->dict:
    mixed=class_summary(d,"mixed_source")
    pure=class_summary(d,"pure_thalassia_source")
    min_events=int(H1["minimum_events_per_source_class"])
    min_nodes=int(H1["minimum_nodes_per_source_class"])
    estimable=bool(
        mixed["events"]>=min_events and pure["events"]>=min_events
        and mixed["nodes"]>=min_nodes and pure["nodes"]>=min_nodes
    )
    out={
        "mixed_source":mixed,
        "pure_thalassia_source":pure,
        "estimable":estimable,
        "difference_mixed_minus_pure":None,
        "ci95":None,
        "supported":False,
    }
    if not estimable:
        return out

    point=float(mixed["replacement_fraction"]-pure["replacement_fraction"])
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by_node={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(H1_SEED)
    vals=[]
    attempts=0
    max_attempts=H1_BOOT*20
    while len(vals)<H1_BOOT and attempts<max_attempts:
        attempts+=1
        sample=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by_node[n] for n in sample],ignore_index=True)
        bm=class_summary(b,"mixed_source")
        bp=class_summary(b,"pure_thalassia_source")
        if bm["events"]==0 or bp["events"]==0:
            continue
        vals.append(float(bm["replacement_fraction"]-bp["replacement_fraction"]))
    if len(vals)!=H1_BOOT:
        raise RuntimeError(f"H1 bootstrap could not obtain {H1_BOOT} estimable replicates")
    ci=np.quantile(np.asarray(vals,float),[.025,.975])
    out.update({
        "difference_mixed_minus_pure":point,
        "ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[0]>0),
        "bootstrap_attempts":int(attempts),
    })
    return out


def bootstrap_h2(d:pd.DataFrame)->dict:
    x=d[d["target_replacement"]==1].copy()
    n=int(len(x)); nodes_n=int(x["node_id"].nunique()) if n else 0
    min_events=int(H2["minimum_replacement_events"])
    min_nodes=int(H2["minimum_nodes"])
    estimable=bool(n>=min_events and nodes_n>=min_nodes)
    out={
        "replacement_events":n,
        "nodes":nodes_n,
        "persistent_component_fraction":None,
        "novel_only_fraction":None,
        "estimable":estimable,
        "ci95":None,
        "supported":False,
    }
    if not estimable:
        return out

    point=float(x["persistent_component"].mean())
    novel=float(x["novel_only_component"].mean())
    nodes=np.asarray(sorted(x["node_id"].unique()),dtype=object)
    by_node={n:x[x["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(H2_SEED)
    vals=np.empty(H2_BOOT,float)
    for i in range(H2_BOOT):
        sample=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by_node[n] for n in sample],ignore_index=True)
        vals[i]=float(b["persistent_component"].mean())
    ci=np.quantile(vals,[.025,.975])
    out.update({
        "persistent_component_fraction":point,
        "novel_only_fraction":novel,
        "ci95":[float(ci[0]),float(ci[1])],
        "supported":bool(ci[0]>0.5),
    })
    return out


def bay_descriptive(d:pd.DataFrame)->list[dict]:
    rows=[]
    for bay,g in d.groupby("water_body",sort=True):
        m=class_summary(g,"mixed_source")
        p=class_summary(g,"pure_thalassia_source")
        rep=g[g["target_replacement"]==1]
        rows.append({
            "water_body":bay,
            "events":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "mixed_events":m["events"],
            "mixed_replacement_fraction":m["replacement_fraction"],
            "pure_events":p["events"],
            "pure_replacement_fraction":p["replacement_fraction"],
            "replacement_events":int(len(rep)),
            "persistent_component_fraction":(
                float(rep["persistent_component"].mean()) if len(rep) else None
            ),
        })
    return rows


def taxon_fates(d:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for _,r in d[d["target_replacement"]==1].iterrows():
        src=taxa_set(r["source_alternative_species"])
        tgt=taxa_set(r["target_alternative_species"])
        for taxon in sorted(tgt):
            rows.append({
                "water_body":r["water_body"],
                "node_id":r["node_id"],
                "point_id":r["point_id"],
                "source_year":int(r["source_year"]),
                "target_year":int(r["target_year"]),
                "source_class":r["source_class"],
                "taxon":taxon,
                "fate":"persistent" if taxon in src else "novel",
            })
    return pd.DataFrame(rows)


def year_descriptive(d:pd.DataFrame)->list[dict]:
    rows=[]
    for year,g in d.groupby("target_year",sort=True):
        rows.append({
            "target_year":int(year),
            "events":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "replacement_fraction":float(g["target_replacement"].mean()),
            "mixed_source_fraction":float((g["source_class"]=="mixed_source").mean()),
        })
    return rows


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    if len(py)!=45494:
        raise RuntimeError(f"consensus point-year registry drift: {len(py)}")
    repeated_points=int((py.groupby("point_id")["year"].nunique()>=2).sum())
    if repeated_points!=3917:
        raise RuntimeError(f"repeated stable-point registry drift: {repeated_points}")

    d=build_transitions(py)
    if len(d)==0:
        raise RuntimeError("no exact-point Thalassia-loss transitions under frozen period rule")
    if int(d["source_year"].min())<START or int(d["target_year"].max())>END:
        raise RuntimeError("frozen period rule violated")
    if not (d["target_year"].astype(int)==d["source_year"].astype(int)+1).all():
        raise RuntimeError("non-consecutive exact-point transition found")

    h1=bootstrap_h1(d)
    h2=bootstrap_h2(d)
    fates=taxon_fates(d)

    result={
        "schema":"tampa.microsite_diversity_insurance_v1.result",
        "status":(
            "both_supported" if h1["supported"] and h2["supported"] else
            "insurance_supported_persistence_not_supported" if h1["supported"] else
            "persistence_supported_insurance_not_supported" if h2["supported"] else
            "microsite_diversity_insurance_not_supported"
        ),
        "contract":"results/microsite_diversity_insurance_v1_contract.json",
        "registry":{
            "consensus_point_years":int(len(py)),
            "stable_point_ids_total":int(py["point_id"].nunique()),
            "repeated_stable_points":repeated_points,
            "post2016_exact_point_thalassia_loss_events":int(len(d)),
            "nodes_with_loss":int(d["node_id"].nunique()),
        },
        "H1_microsite_insurance":h1,
        "H2_persistence_component":h2,
        "bay_segment_descriptive":bay_descriptive(d),
        "year_descriptive":year_descriptive(d),
        "taxon_fates_descriptive":(
            fates.groupby(["taxon","fate"],as_index=False)
            .size()
            .rename(columns={"size":"events"})
            .to_dict("records")
            if len(fates) else []
        ),
        "interpretation":(
            "Pre-existing microsite seagrass diversity acts as statistical insurance if mixed-source points "
            "retain seagrass occupancy more often than pure-Thalassia source points after exact focal loss. "
            "A second test distinguishes persistence of source co-occurring taxa from target taxa that appear "
            "only after focal loss."
        ),
        "claim_boundary":C["claim_boundary"],
    }

    d.to_csv(outdir/"microsite_insurance_transitions.csv",index=False)
    fates.to_csv(outdir/"microsite_insurance_taxon_fates.csv",index=False)
    pd.DataFrame(result["bay_segment_descriptive"]).to_csv(
        outdir/"microsite_insurance_by_bay.csv",index=False
    )
    (outdir/"microsite_diversity_insurance_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_microsite_insurance"))
    p.add_argument("--out",type=Path,default=Path("results/generated_microsite_insurance"))
    a=p.parse_args()
    main(a.input,a.out)
