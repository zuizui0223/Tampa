#!/usr/bin/env python3
"""Current-main Tampa scale-decoupling test.

Question
--------
Do baywide aerial seagrass extent and repeated fixed-transect states tell the
same ecological story?

This analysis deliberately separates:
  1) any-seagrass point frequency at fixed transects;
  2) focal Thalassia testudinum point frequency;
  3) baywide mapped seagrass acreage.

The annual transect panel is rebuilt independently by
analysis/33_community_buffering.py from the pinned Darwin Core source. No stale
annual panel from the historical extent-local branch is used.

Primary aerial series
---------------------
data/tbep_seagrass_extent_current.csv, transcribed from the TBEP
State-of-the-Bay subtidal land-use table (1988-2024).

The 2024 TBEP Reasonable Assurance report gives 31,544 acres whereas the
State-of-the-Bay table gives 31,563 acres. The continuous State-of-the-Bay
series is primary; replacing only 2024 with 31,544 is a declared sensitivity.

Evidence class: post-hoc ecological scale audit. It cannot identify mechanism.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import pandas as pd

SEED = 20261005
N_PERM = 50000
ALT_2024_ACRES = 31544.0
REQUIRED = {
    "node_id", "year", "water_body",
    "thalassia_frequency", "any_seagrass_frequency",
}


def pearson(xs, ys):
    xs=list(map(float,xs)); ys=list(map(float,ys))
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    xx=sum((x-mx)**2 for x in xs)
    yy=sum((y-my)**2 for y in ys)
    if xx<=0 or yy<=0:
        return math.nan
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(xx*yy)


def permutation_p(xs, ys, observed, seed=SEED, reps=N_PERM):
    rng=random.Random(seed)
    work=list(map(float,ys))
    exceed=0
    for _ in range(reps):
        rng.shuffle(work)
        if abs(pearson(xs,work)) >= abs(observed):
            exceed += 1
    return (exceed+1)/(reps+1)


def summarize_network(annual, matched_years, fixed_nodes=None):
    d=annual[annual["year"].isin(matched_years)].copy()
    if fixed_nodes is not None:
        d=d[d["node_id"].isin(fixed_nodes)].copy()
    out=(d.groupby("year",as_index=False)
           .agg(
               n_nodes=("node_id","nunique"),
               any_seagrass_frequency=("any_seagrass_frequency","mean"),
               thalassia_frequency=("thalassia_frequency","mean"),
           )
           .sort_values("year"))
    return out


def compare(extent, states, label):
    d=extent.merge(states,on="year",how="inner").sort_values("year").reset_index(drop=True)
    if len(d)<6:
        raise RuntimeError(f"{label}: too few matched mapping years: {len(d)}")
    metrics=["any_seagrass_frequency","thalassia_frequency"]
    levels={}
    for m in metrics:
        r=pearson(d["acres"],d[m])
        levels[m]={
            "pearson_r":r,
            "permutation_p_two_sided":permutation_p(d["acres"],d[m],r,seed=SEED+11),
        }
    intervals=[]
    for i in range(1,len(d)):
        a=d.iloc[i-1]; b=d.iloc[i]
        dt=float(b.year-a.year)
        rec={
            "from":int(a.year),"to":int(b.year),
            "annualized_acres_change":float((b.acres-a.acres)/dt),
        }
        for m in metrics:
            rec[f"annualized_{m}_change"]=float((b[m]-a[m])/dt)
        intervals.append(rec)
    iv=pd.DataFrame(intervals)
    changes={}
    for j,m in enumerate(metrics):
        y=iv[f"annualized_{m}_change"]
        r=pearson(iv["annualized_acres_change"],y)
        changes[m]={
            "pearson_r":r,
            "permutation_p_two_sided":permutation_p(
                iv["annualized_acres_change"],y,r,seed=SEED+101+j
            ),
        }
    def pct(start,end,col):
        a=d[d.year==start]
        b=d[d.year==end]
        if len(a)!=1 or len(b)!=1:
            return None
        av=float(a.iloc[0][col]); bv=float(b.iloc[0][col])
        return 100*(bv/av-1) if av!=0 else None

    contrasts={}
    for start,end in [(2016,2022),(2016,2024)]:
        contrasts[f"{start}_{end}_pct"]={
            "acres":pct(start,end,"acres"),
            "any_seagrass_frequency":pct(start,end,"any_seagrass_frequency"),
            "thalassia_frequency":pct(start,end,"thalassia_frequency"),
        }
    return {
        "label":label,
        "mapping_year_count":int(len(d)),
        "matched_mapping_years":d.to_dict("records"),
        "level_correlation":levels,
        "annualized_change_correlation":changes,
        "interval_changes":intervals,
        "change_contrasts":contrasts,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--annual",default="results/generated_scale/community_buffering_annual.csv")
    ap.add_argument("--coverage",default="data/tbep_seagrass_extent_current.csv")
    ap.add_argument("--out",default="results/generated_scale/scale_decoupling_current_v1.json")
    args=ap.parse_args()

    annual=pd.read_csv(args.annual)
    missing=REQUIRED.difference(annual.columns)
    if missing:
        raise RuntimeError(f"annual panel missing columns: {sorted(missing)}")
    if len(annual)!=1480 or annual["node_id"].nunique()!=71:
        raise RuntimeError(
            f"current annual-panel identity drift: rows={len(annual)} nodes={annual['node_id'].nunique()}"
        )

    extent=pd.read_csv(args.coverage)[["year","acres"]].copy()
    extent["year"]=extent["year"].astype(int)
    extent["acres"]=extent["acres"].astype(float)
    matched_years=sorted(set(extent.year).intersection(set(annual.year.astype(int))))
    network=summarize_network(annual,matched_years)

    counts=(annual[annual.year.isin(matched_years)]
            .groupby("node_id")["year"].nunique())
    fixed_nodes=sorted(counts[counts==len(matched_years)].index.tolist())
    fixed=summarize_network(annual,matched_years,fixed_nodes=fixed_nodes)

    primary=compare(extent,network,"all_available_fixed_transects")
    fixed_result=(
        compare(extent,fixed,"nodes_observed_in_all_mapping_years")
        if len(fixed_nodes)>=5 else
        {"label":"nodes_observed_in_all_mapping_years","estimable":False,
         "n_fixed_nodes":len(fixed_nodes)}
    )

    alt=extent.copy()
    alt.loc[alt.year==2024,"acres"]=ALT_2024_ACRES
    alt_sensitivity=compare(alt,network,"2024_extent_31544_sensitivity")

    result={
        "schema":"tampa.scale_decoupling_current.v1",
        "evidence_class":"posthoc_ecological_scale_audit",
        "source":{
            "transect_panel":"analysis/33_community_buffering.py -> community_buffering_annual.csv",
            "expected_annual_node_years":1480,
            "expected_stable_nodes":71,
            "aerial_series":"data/tbep_seagrass_extent_current.csv",
            "aerial_series_primary_2024_acres":31563,
            "aerial_2024_official_sensitivity_acres":31544,
        },
        "fixed_node_sensitivity":{
            "definition":"node observed in every matched aerial mapping year",
            "n_fixed_nodes":len(fixed_nodes),
            "nodes":fixed_nodes,
        },
        "primary":primary,
        "fixed_node_panel":fixed_result,
        "official_2024_value_sensitivity":alt_sensitivity,
        "interpretation_rule":{
            "scale_alignment":"aerial acreage should covary with any-seagrass frequency if the two monitoring layers capture a shared broad vegetation signal",
            "focal_decoupling":"weak acreage-Thalassia coupling alongside stronger acreage-any-seagrass coupling means baywide habitat extent is not interchangeable with focal-foundation-species state",
        },
        "claim_boundary":[
            "Aerial extent is total seagrass habitat, whereas Thalassia frequency is species-specific; divergence is an ecological scale/taxon mismatch, not measurement error.",
            "The analysis is post-hoc and descriptive; it does not identify the cause of aerial loss or focal-species change.",
            "Correlations across mapping years are not independent experimental replicates.",
            "The fixed-node sensitivity addresses changing transect composition but does not make the aerial and transect sampling frames identical.",
            "Do not call stable focal frequency evidence of unchanged blade, shoot, reserve, or ecosystem-function state.",
        ],
    }
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
