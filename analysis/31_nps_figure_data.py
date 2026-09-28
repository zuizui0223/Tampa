#!/usr/bin/env python3
"""Build external NPS Zostera sidecar data for Tampa manuscript Figure 3.

No ecological model is fit here. The script filters the already-generated annual NPS
state to the repeated nodes used by the canonical within-node cover analysis and
verifies the state-decoupling registry against committed results.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
CANON=json.loads((ROOT/"results/nps_persistent_cover_v1.json").read_text())

def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    annual=pd.read_csv(input_dir/"nps_tier3_annual_state.csv")
    slopes=pd.read_csv(input_dir/"nps_tier3_cover_node_slopes.csv")

    required={"node_id","Location","year","recorded_presence","focal_frequency","focal_mean_cover"}
    missing=required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"NPS annual columns missing: {sorted(missing)}")

    if len(annual)!=240 or annual["node_id"].nunique()!=18:
        raise RuntimeError("NPS annual registry drift")
    if not annual["recorded_presence"].astype(bool).all():
        raise RuntimeError("NPS binary state is no longer saturated")
    if not np.allclose(annual["focal_frequency"].to_numpy(float),1.0,rtol=0,atol=1e-12):
        raise RuntimeError("NPS focal frequency is no longer saturated at 1")

    repeated=set(slopes["node_id"].astype(str))
    if len(repeated)!=15:
        raise RuntimeError(f"expected 15 repeated cover nodes, got {len(repeated)}")

    traj=annual[annual["node_id"].astype(str).isin(repeated)][
        ["node_id","Location","year","recorded_presence","focal_frequency","focal_mean_cover"]
    ].copy()
    traj=traj.sort_values(["Location","node_id","year"])
    traj.to_csv(outdir/"figure3B_nps_repeated_cover_trajectories.csv",index=False)

    slope_cols=["node_id","Location","n","year_min","year_max","slope","min","max","range"]
    missing=set(slope_cols).difference(slopes.columns)
    if missing:
        raise RuntimeError(f"NPS slope columns missing: {sorted(missing)}")
    sl=slopes[slope_cols].copy().sort_values(["Location","node_id"])
    sl.to_csv(outdir/"figure3C_nps_cover_node_slopes.csv",index=False)

    pooled=float((slopes["sxy"].sum())/(slopes["sxx"].sum()))
    exp=CANON["quantitative_state"]["cover"]
    if not np.isclose(pooled,float(exp["within_node_slope_per_year"]),rtol=1e-12,atol=1e-12):
        raise RuntimeError("NPS pooled cover slope drift")
    if int((slopes["slope"]<0).sum())!=int(exp["negative_node_slopes"]):
        raise RuntimeError("NPS negative node slope count drift")

    summary={
      "schema":"tampa.nps_figure_data_v1",
      "status":"external_posthoc_figure_sidecar",
      "source_result":"results/nps_persistent_cover_v1.json",
      "annual_units":int(len(annual)),
      "all_recorded_present":True,
      "all_focal_frequency_one":True,
      "repeated_cover_nodes":int(len(repeated)),
      "trajectory_rows":int(len(traj)),
      "locations":int(traj["Location"].nunique()),
      "cover_range":[float(annual["focal_mean_cover"].min()),float(annual["focal_mean_cover"].max())],
      "negative_node_slopes":int((slopes["slope"]<0).sum()),
      "positive_node_slopes":int((slopes["slope"]>0).sum()),
      "pooled_within_node_cover_slope_per_year":pooled,
      "claim_boundary":[
        "Post-hoc external ecological replication; not untouched predictive confirmation.",
        "Binary recorded presence and frequency are saturated by panel construction and monitoring eligibility.",
        "Cover trajectories are observational and do not identify an environmental cause.",
        "Single-year identities do not enter repeated-node slope trajectories."
      ]
    }
    (outdir/"nps_figure_data_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_nps_figure"))
    p.add_argument("--out",type=Path,default=Path("results/generated_nps_figure/figure_data"))
    a=p.parse_args(); main(a.input,a.out)
