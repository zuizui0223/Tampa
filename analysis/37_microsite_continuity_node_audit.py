#!/usr/bin/env python3
"""Within-node audit of the exact-point habitat-continuity recovery association.

Frozen design:
results/microsite_continuity_node_audit_v1_contract.json

This audit asks whether the pooled association between loss-year vegetation and
next-year Thalassia re-recording persists within the same stable transects.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/microsite_continuity_node_audit_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
MIN_NODES=int(H["minimum_informative_nodes"])


def return_fraction(d:pd.DataFrame)->float:
    return float(d["thalassia_return"].mean()) if len(d) else math.nan


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    seq=pd.read_csv(input_dir/"microsite_recovery_sequences.csv")
    required={"node_id","intermediate_state","thalassia_return","source_year","loss_year","recovery_year"}
    missing=required.difference(seq.columns)
    if missing:
        raise RuntimeError(f"missing recovery-sequence columns: {sorted(missing)}")

    rows=[]
    for node,g in seq.groupby("node_id",sort=True):
        veg=g[g["intermediate_state"]=="other_seagrass"]
        bare=g[g["intermediate_state"]=="no_seagrass"]
        if len(veg)==0 or len(bare)==0:
            continue
        pv=return_fraction(veg)
        pb=return_fraction(bare)
        rows.append({
            "node_id":str(node),
            "vegetated_sequences":int(len(veg)),
            "bare_sequences":int(len(bare)),
            "vegetated_return_fraction":pv,
            "bare_return_fraction":pb,
            "within_node_difference":float(pv-pb),
        })
    nodes=pd.DataFrame(rows)
    estimable=bool(len(nodes)>=MIN_NODES)

    result={
        "schema":"tampa.microsite_continuity_node_audit_v1.result",
        "status":"non_estimable" if not estimable else None,
        "contract":"results/microsite_continuity_node_audit_v1_contract.json",
        "registry":{
            "all_recovery_sequences":int(len(seq)),
            "all_nodes":int(seq["node_id"].nunique()),
            "informative_nodes":int(len(nodes)),
            "minimum_informative_nodes":MIN_NODES,
        },
        "primary":{
            "equal_node_mean_difference":None,
            "ci95":None,
            "supported":False,
        },
        "secondary":{
            "median_node_difference":None,
            "positive_nodes":0,
            "zero_nodes":0,
            "negative_nodes":0,
            "event_weighted_difference_in_informative_nodes":None,
        },
        "interpretation":None,
        "claim_boundary":C["claim_boundary"],
    }

    if estimable:
        diffs=nodes["within_node_difference"].to_numpy(float)
        point=float(diffs.mean())
        rng=np.random.default_rng(SEED)
        boot=np.empty(BOOT,float)
        for i in range(BOOT):
            sample=rng.choice(diffs,size=len(diffs),replace=True)
            boot[i]=float(sample.mean())
        ci=np.quantile(boot,[.025,.975])

        informative_ids=set(nodes["node_id"].astype(str))
        d=seq[seq["node_id"].astype(str).isin(informative_ids)].copy()
        veg=d[d["intermediate_state"]=="other_seagrass"]
        bare=d[d["intermediate_state"]=="no_seagrass"]
        pooled=float(return_fraction(veg)-return_fraction(bare))

        positive=int((diffs>0).sum())
        zero=int((diffs==0).sum())
        negative=int((diffs<0).sum())
        supported=bool(ci[0]>0)
        status="within_node_microsite_continuity_supported" if supported else "within_node_microsite_continuity_not_supported"

        result["status"]=status
        result["primary"]={
            "equal_node_mean_difference":point,
            "ci95":[float(ci[0]),float(ci[1])],
            "bootstrap_replicates":BOOT,
            "supported":supported,
        }
        result["secondary"]={
            "median_node_difference":float(np.median(diffs)),
            "positive_nodes":positive,
            "zero_nodes":zero,
            "negative_nodes":negative,
            "event_weighted_difference_in_informative_nodes":pooled,
            "informative_vegetated_sequences":int(len(veg)),
            "informative_bare_sequences":int(len(bare)),
        }
        result["interpretation"]=(
            C["interpretation"]["supported"] if supported else C["interpretation"]["unsupported"]
        )
    else:
        result["interpretation"]="Frozen informative-node minimum not met; retain non-estimable outcome."

    nodes.to_csv(outdir/"microsite_continuity_node_differences.csv",index=False)
    (outdir/"microsite_continuity_node_audit_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_microsite_continuity"))
    p.add_argument("--out",type=Path,default=Path("results/generated_microsite_continuity"))
    a=p.parse_args()
    main(a.input,a.out)
