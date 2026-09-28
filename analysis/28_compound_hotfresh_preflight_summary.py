#!/usr/bin/env python3
"""Summarize response-independent published hot-fresh exposure coverage."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def main(segment_csv:Path, station_csv:Path, out:Path):
    seg=pd.read_csv(segment_csv)
    sta=pd.read_csv(station_csv)
    required_seg={"bay_segment","trnyr","station_count","mean_max_hotfresh_run_days","median_max_hotfresh_run_days"}
    required_sta={"bay_segment","station","trnyr","max_hotfresh_run_days"}
    if m:=required_seg.difference(seg.columns): raise RuntimeError(f"segment columns missing {sorted(m)}")
    if m:=required_sta.difference(sta.columns): raise RuntimeError(f"station columns missing {sorted(m)}")
    req_segments={"OTB","HB","MTB","LTB"}
    observed=set(seg["bay_segment"].astype(str))
    years=sorted(seg["trnyr"].astype(int).unique().tolist())
    passed=(
      len(observed & req_segments)>=4 and
      len(years)>=20 and
      len(seg)>=70 and
      len(sta)>=200
    )
    byseg=(seg.groupby("bay_segment",as_index=False)
      .agg(segment_years=("trnyr","nunique"),
           first_year=("trnyr","min"),last_year=("trnyr","max"),
           median_station_count=("station_count","median"),
           median_mean_max_run=("mean_max_hotfresh_run_days","median"),
           maximum_mean_max_run=("mean_max_hotfresh_run_days","max")))
    summary={
      "schema":"tampa.compound_hotfresh_v1.preflight",
      "status":"preflight_pass" if passed else "preflight_stop",
      "response_access":{"focal_thalassia_response_opened":False},
      "source":{
        "repository":"tbep-tech/temp-manu",
        "commit":"e5aaec93c7501fc38c63b615a89e68636b36421f",
        "path":"data/thralltrndat.RData",
        "git_blob_sha1":"f6518ea25685369057bfe92e71973ec04c57eac1",
        "blob_verified_by_git_hash_object":True
      },
      "exposure":{
        "temperature_threshold_c":30,
        "salinity_threshold_ppt":25,
        "station_metric":"maximum consecutive daily run where published GAM predictions satisfy temp>=30 and salinity<=25",
        "segment_metric":"mean station-level maximum run per published transect year"
      },
      "registry":{
        "station_intervals":int(len(sta)),
        "segment_years":int(len(seg)),
        "segments":sorted(observed),
        "year_range":[int(min(years)),int(max(years))] if years else None,
        "year_count":int(len(years))
      },
      "by_segment":byseg.to_dict("records"),
      "overall":{
        "median_segment_mean_max_run_days":float(seg["mean_max_hotfresh_run_days"].median()),
        "max_segment_mean_max_run_days":float(seg["mean_max_hotfresh_run_days"].max()),
        "fraction_segment_years_nonzero":float((seg["mean_max_hotfresh_run_days"]>0).mean())
      },
      "next_gate":"Freeze focal Thalassia plant-condition outcome analysis only if status is preflight_pass.",
      "claim_boundary":[
        "The daily sequence is a published GAM reconstruction from monthly observations, not direct daily monitoring.",
        "This exposure is retrospective and should not be described as a prospective environmental predictor.",
        "The published 30 C and 25 ppt thresholds are stress indices rather than experimentally identified Tampa-specific physiological boundaries."
      ]
    }
    out.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--segment",type=Path,required=True)
    p.add_argument("--station",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(); main(a.segment,a.station,a.out)
