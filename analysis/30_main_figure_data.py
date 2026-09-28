#!/usr/bin/env python3
"""Build source tables for Tampa manuscript Figures 1, 2, 3A and 4.

This script does not fit new ecological models or choose endpoints. It transforms
already-generated primary analysis tables plus the canonical validation ledger into
figure-facing tables with explicit provenance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=json.loads((ROOT/"figures/main_figure_data_contract_v1.json").read_text())
CANON=json.loads((ROOT/"results/current_validation_v2.json").read_text())

STATE_VARS=[
    ("recorded_detection","detected"),
    ("focal_frequency","focal_frequency"),
    ("braun_blanquet_index","bb_cover_mean_all_points"),
    ("blade_length_mm","blade_length_mean_mm"),
    ("shoot_density_m2","shoot_density_mean_m2"),
]

def group_mean_r2(d:pd.DataFrame,ycol:str,group:str)->float:
    x=d.dropna(subset=[ycol,group]).copy()
    y=x[ycol].to_numpy(float)
    fit=x.groupby(group,observed=False)[ycol].transform("mean").to_numpy(float)
    sst=float(np.sum((y-y.mean())**2))
    return float(1.0-np.sum((y-fit)**2)/sst) if sst>0 else 0.0

def fig1(annual:pd.DataFrame,out:Path):
    nodes=(annual[["node_id","water_body","longitude","latitude"]]
           .drop_duplicates("node_id")
           .sort_values(["water_body","node_id"]))
    if len(nodes)!=71:
        raise RuntimeError(f"figure1 node registry drift: {len(nodes)}")
    nodes.to_csv(out/"figure1A_tampa_nodes.csv",index=False)

    rows=[]
    for label,col in STATE_VARS:
        d=annual.dropna(subset=[col]).copy()
        rows.append({
            "state_dimension":label,
            "column":col,
            "n_node_years":int(len(d)),
            "stable_node_r2":group_mean_r2(d,col,"node_id"),
            "year_r2":group_mean_r2(d,col,"year"),
        })
    state=pd.DataFrame(rows)
    state.to_csv(out/"figure1B_state_hierarchy.csv",index=False)

    expected=CANON["eog_ecological_translation"]["stable_node_r2"]
    lookup={
        "recorded_detection":"detected",
        "focal_frequency":"focal_frequency",
        "braun_blanquet_index":"bb_cover_mean_all_points",
        "blade_length_mm":"blade_length_mean_mm",
        "shoot_density_m2":"shoot_density_mean_m2",
    }
    for _,r in state.iterrows():
        e=float(expected[lookup[r["state_dimension"]]])
        if not np.isclose(float(r["stable_node_r2"]),e,rtol=1e-10,atol=1e-10):
            raise RuntimeError(f"stable-node R2 drift {r['state_dimension']}: {r['stable_node_r2']} != {e}")
    return state

def fig2(seg:pd.DataFrame,out:Path):
    cols=[
      "water_body","year","n_nodes","prevalence","frequency_mean","cover_index_mean",
      "blade_length_mean_mm","shoot_density_mean_m2"
    ]
    missing=set(cols).difference(seg.columns)
    if missing:
        raise RuntimeError(f"figure2 segment columns missing: {sorted(missing)}")
    d=seg[seg["year"].between(2016,2025)][cols].copy()
    d.to_csv(out/"figure2A_D_segment_state_2016_2025.csv",index=False)

    q=CANON["quantitative_state"]
    rows=[
      {
        "water_body":"Old Tampa Bay","state":"recorded_detection","slope":q["old_tampa_bay"]["binary_detection_slope"],
        "ci_low":q["old_tampa_bay"]["binary_detection_ci95"][0],"ci_high":q["old_tampa_bay"]["binary_detection_ci95"][1],
        "role":"binary_reference"
      },
      {
        "water_body":"Old Tampa Bay","state":"blade_length_mm","slope":q["old_tampa_bay"]["blade_length_mm_per_year"],
        "ci_low":q["old_tampa_bay"]["blade_length_ci95"][0],"ci_high":q["old_tampa_bay"]["blade_length_ci95"][1],
        "role":"degradation"
      },
      {
        "water_body":"Old Tampa Bay","state":"shoot_density_m2","slope":q["old_tampa_bay"]["shoot_density_per_m2_per_year"],
        "ci_low":q["old_tampa_bay"]["shoot_density_ci95"][0],"ci_high":q["old_tampa_bay"]["shoot_density_ci95"][1],
        "role":"degradation"
      },
      {
        "water_body":"Middle Tampa Bay","state":"recorded_detection","slope":q["middle_tampa_bay"]["binary_detection_slope"],
        "ci_low":q["middle_tampa_bay"]["binary_detection_ci95"][0],"ci_high":q["middle_tampa_bay"]["binary_detection_ci95"][1],
        "role":"binary_reference"
      },
      {
        "water_body":"Middle Tampa Bay","state":"blade_length_mm","slope":q["middle_tampa_bay"]["blade_length_mm_per_year"],
        "ci_low":q["middle_tampa_bay"]["blade_length_ci95"][0],"ci_high":q["middle_tampa_bay"]["blade_length_ci95"][1],
        "role":"degradation"
      },
      {
        "water_body":"Lower Tampa Bay","state":"recorded_detection","slope":q["lower_tampa_bay"]["binary_detection_slope"],
        "ci_low":q["lower_tampa_bay"]["binary_detection_ci95"][0],"ci_high":q["lower_tampa_bay"]["binary_detection_ci95"][1],
        "role":"binary_reference"
      },
      {
        "water_body":"Lower Tampa Bay","state":"focal_frequency","slope":q["lower_tampa_bay"]["focal_frequency_per_year"],
        "ci_low":q["lower_tampa_bay"]["focal_frequency_ci95"][0],"ci_high":q["lower_tampa_bay"]["focal_frequency_ci95"][1],
        "role":"degradation"
      },
    ]
    slopes=pd.DataFrame(rows)
    slopes.to_csv(out/"figure2E_canonical_slopes.csv",index=False)
    return d,slopes

def fig3_tampa(comm:pd.DataFrame,out:Path):
    cols=["water_body","year","Thalassia_frequency","Syringodium_frequency","Halodule_frequency"]
    missing=set(cols).difference(comm.columns)
    if missing:
        raise RuntimeError(f"figure3 community columns missing: {sorted(missing)}")
    d=comm[(comm["water_body"]=="Lower Tampa Bay") & comm["year"].between(2016,2025)][cols].copy()
    if d["year"].nunique()!=10:
        raise RuntimeError(f"figure3 Lower Tampa year coverage drift: {d['year'].nunique()}")
    d.to_csv(out/"figure3A_lower_tampa_community.csv",index=False)
    return d

def fig4(trans:pd.DataFrame,scores:pd.DataFrame,out:Path):
    cols=["node_id","source_year","target_year","loss","water_body","focal_frequency","bb_cover_mean_all_points"]
    missing=set(cols).difference(trans.columns)
    if missing:
        raise RuntimeError(f"figure4 transition columns missing: {sorted(missing)}")
    d=trans[cols].copy()
    d["next_year_state"]=np.where(d["loss"].astype(int)==1,"recorded_loss","recorded_persistence")
    d.to_csv(out/"figure4A_B_source_state_before_outcome.csv",index=False)

    p=scores.pivot(index="target_year",columns="arm",values="log_loss").reset_index()
    if not {"baseline","quantitative"}.issubset(p.columns):
        raise RuntimeError("figure4 year score arms missing")
    p["quantitative_minus_baseline"]=p["quantitative"]-p["baseline"]
    p["adverse_2016"]=p["target_year"].astype(int).eq(2016)
    if 2016 not in set(p["target_year"].astype(int)):
        raise RuntimeError("Figure 4 primary target year 2016 missing")
    p.to_csv(out/"figure4C_target_year_logloss_delta.csv",index=False)
    return d,p

def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"quant_annual_panel.csv")
    seg=pd.read_csv(input_dir/"quant_segment_year.csv")
    comm=pd.read_csv(input_dir/"community_quant_segment_year.csv")
    trans=pd.read_csv(input_dir/"early_warning_transitions.csv")
    scores=pd.read_csv(input_dir/"early_warning_year_scores.csv")

    f1=fig1(annual,outdir)
    f2,_=fig2(seg,outdir)
    f3=fig3_tampa(comm,outdir)
    f4,ys=fig4(trans,scores,outdir)

    summary={
      "schema":"tampa.main_figure_data_v1",
      "contract":"figures/main_figure_data_contract_v1.json",
      "status":"figure_data_built",
      "source_generated_dir":str(input_dir),
      "figure1":{"nodes":71,"state_dimensions":int(len(f1))},
      "figure2":{"segment_year_rows_2016_2025":int(len(f2))},
      "figure3_tampa":{"lower_tampa_years":int(f3["year"].nunique())},
      "figure4":{
        "source_positive_transitions":int(len(f4)),
        "recorded_losses":int((f4["loss"]==1).sum()),
        "scored_target_years":int(len(ys)),
        "target_2016_retained":bool((ys["target_year"].astype(int)==2016).any())
      },
      "claim_boundary":CONTRACT["rules"]
    }
    if summary["figure4"]["source_positive_transitions"]!=688 or summary["figure4"]["recorded_losses"]!=24:
        raise RuntimeError("Figure 4 transition registry drift")
    (outdir/"main_figure_data_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated"))
    p.add_argument("--out",type=Path,default=Path("results/generated/figure_data"))
    a=p.parse_args(); main(a.input,a.out)
