#!/usr/bin/env python3
"""Test exact-point pre-loss Thalassia persistence as a local legacy signal.

Frozen design: results/preloss_point_legacy_v1_contract.json

For the same three-year exact-point loss/recovery sequences used by the merged
microsite recovery analysis, compute the consecutive Thalassia-presence streak
ending in the source year. The primary comparison is within stable node AND
loss-year intermediate community state, then equally averaged across nodes.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/preloss_point_legacy_v1_contract.json").read_text())
P=C["primary_design"]
BOOT=int(P["bootstrap_replicates"])
SEED=int(P["random_seed"])
MIN_NODES=int(P["minimum_informative_nodes"])


def build_lookup(py:pd.DataFrame):
    lookup={}
    for r in py.itertuples(index=False):
        key=(str(r.point_id),int(r.year))
        if key in lookup:
            raise RuntimeError(f"duplicate point-year {key}")
        lookup[key]=bool(r.thalassia_present)
    return lookup


def streak(lookup,point:str,source_year:int)->int:
    n=0
    y=int(source_year)
    while True:
        key=(str(point),y)
        if key not in lookup:
            break
        if not bool(lookup[key]):
            break
        n+=1
        y-=1
    return n


def enrich(seq:pd.DataFrame,py:pd.DataFrame)->pd.DataFrame:
    lookup=build_lookup(py)
    d=seq.copy()
    d["preloss_thalassia_streak_years"]=[
        streak(lookup,str(r.point_id),int(r.source_year))
        for r in d.itertuples(index=False)
    ]
    if (d["preloss_thalassia_streak_years"]<1).any():
        raise RuntimeError("source-present sequence has zero pre-loss streak")
    return d


def node_effects(d:pd.DataFrame)->pd.DataFrame:
    strata=[]
    for (node,state),g in d.groupby(["node_id","intermediate_state"],sort=True):
        ret=g[g["thalassia_return"].astype(int)==1]
        no=g[g["thalassia_return"].astype(int)==0]
        if len(ret)==0 or len(no)==0:
            continue
        strata.append({
            "node_id":str(node),
            "intermediate_state":str(state),
            "return_sequences":int(len(ret)),
            "nonreturn_sequences":int(len(no)),
            "mean_streak_return":float(ret["preloss_thalassia_streak_years"].mean()),
            "mean_streak_nonreturn":float(no["preloss_thalassia_streak_years"].mean()),
            "stratum_difference":float(
                ret["preloss_thalassia_streak_years"].mean()
                - no["preloss_thalassia_streak_years"].mean()
            ),
        })
    strata_df=pd.DataFrame(strata)
    if len(strata_df)==0:
        return strata_df,pd.DataFrame()
    nodes=(strata_df.groupby("node_id",as_index=False)
           .agg(
               informative_strata=("intermediate_state","size"),
               node_effect=("stratum_difference","mean"),
               total_return_sequences=("return_sequences","sum"),
               total_nonreturn_sequences=("nonreturn_sequences","sum"),
           ))
    return strata_df,nodes


def return_by_streak(d:pd.DataFrame)->pd.DataFrame:
    z=(d.groupby("preloss_thalassia_streak_years",as_index=False)
       .agg(
           sequences=("point_id","size"),
           nodes=("node_id","nunique"),
           thalassia_return_fraction=("thalassia_return","mean"),
       ))
    z["descriptive_eligible"]=z["sequences"]>=10
    return z


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")

    if len(seq)!=259 or seq["node_id"].nunique()!=25:
        raise RuntimeError("frozen recovery sequence registry drift")
    required_py={"point_id","year","thalassia_present"}
    required_seq={"point_id","node_id","source_year","intermediate_state","thalassia_return"}
    if missing:=required_py.difference(py.columns):
        raise RuntimeError(f"missing point-year columns {sorted(missing)}")
    if missing:=required_seq.difference(seq.columns):
        raise RuntimeError(f"missing sequence columns {sorted(missing)}")

    d=enrich(seq,py)
    strata,nodes=node_effects(d)
    estimable=bool(len(nodes)>=MIN_NODES)

    result={
        "schema":"tampa.preloss_point_legacy_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/preloss_point_legacy_v1_contract.json",
        "registry":{
            "recovery_sequences":int(len(d)),
            "nodes":int(d["node_id"].nunique()),
            "informative_strata":int(len(strata)),
            "informative_nodes":int(len(nodes)),
            "minimum_informative_nodes":MIN_NODES,
            "maximum_observed_streak_years":int(d["preloss_thalassia_streak_years"].max()),
        },
        "primary":{
            "equal_node_mean_streak_difference_years":None,
            "ci95":None,
            "bootstrap_replicates":0,
            "supported":False,
        },
        "secondary":{
            "median_node_effect":None,
            "positive_nodes":0,
            "zero_nodes":0,
            "negative_nodes":0,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        vals=nodes["node_effect"].to_numpy(float)
        point=float(vals.mean())
        rng=np.random.default_rng(SEED)
        boot=np.empty(BOOT,float)
        for i in range(BOOT):
            boot[i]=float(rng.choice(vals,size=len(vals),replace=True).mean())
        ci=np.quantile(boot,[.025,.975])
        supported=bool(ci[0]>0)
        result["status"]=(
            "preloss_local_legacy_supported"
            if supported else
            "preloss_local_legacy_not_supported"
        )
        result["primary"]={
            "equal_node_mean_streak_difference_years":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":BOOT,
            "supported":supported,
        }
        result["secondary"]={
            "median_node_effect":float(np.median(vals)),
            "positive_nodes":int((vals>0).sum()),
            "zero_nodes":int((vals==0).sum()),
            "negative_nodes":int((vals<0).sum()),
        }
        result["interpretation"]=(
            C["interpretation"]["supported"]
            if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen informative-node minimum not met; retain non-estimable outcome."

    d.to_csv(outdir/"preloss_point_legacy_sequences.csv",index=False)
    strata.to_csv(outdir/"preloss_point_legacy_strata.csv",index=False)
    nodes.to_csv(outdir/"preloss_point_legacy_node_effects.csv",index=False)
    return_by_streak(d).to_csv(outdir/"preloss_point_legacy_by_streak.csv",index=False)
    (outdir/"preloss_point_legacy_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+chr(10)
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_preloss_legacy"))
    p.add_argument("--out",type=Path,default=Path("results/generated_preloss_legacy"))
    a=p.parse_args()
    main(a.input,a.out)
