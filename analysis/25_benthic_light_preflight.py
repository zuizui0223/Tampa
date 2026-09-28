#!/usr/bin/env python3
"""Response-independent Tampa benthic-light exposure preflight.

Combines pinned point depth and survey date with the already-generated monthly
segment Secchi series. No focal biological response table is opened.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/benthic_light_exposure_v1_contract.json").read_text())

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc/event.csv"
SIZE=24654717
BLOB="583b4d4e328290ab065346579eb4f29f03ea0f99"
EVENT_HEADER=["eventID","parentEventID","eventType","eventDate","year","month","day","decimalLatitude","decimalLongitude","geodeticDatum","minimumDepthInMeters","maximumDepthInMeters","country","countryCode","stateProvince","waterBody","locality","locationID","samplingProtocol","institutionCode","datasetName","datasetID","license","locationRemarks"]
SEGMENT_MAP={str(k):str(v) for k,v in C["eligible_segments"].items()}

def blob_sha(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch():
    req=Request(URL,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-benthic-light-preflight/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(SIZE+1)
    if len(data)!=SIZE: raise RuntimeError(f"event size drift {len(data)}")
    if blob_sha(data)!=BLOB: raise RuntimeError("event blob drift")
    return data

def maybe_float(x):
    try: y=float(str(x).strip())
    except Exception: return math.nan
    return y if math.isfinite(y) else math.nan

def parse_visits(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EVENT_HEADER: raise RuntimeError("event header drift")
    parents={}; child_depth=defaultdict(list); child_count=defaultdict(int)
    for row in reader:
        typ=row["eventType"].strip()
        eid=row["eventID"].strip()
        if typ=="Transect":
            dt=datetime.strptime(row["eventDate"],"%Y-%m-%d")
            parents[eid]={
              "unit_id":eid,
              "node_id":row["locationID"].strip(),
              "water_body":row["waterBody"].strip(),
              "segment":SEGMENT_MAP.get(row["waterBody"].strip()),
              "date":dt.date().isoformat(),
              "year":dt.year,"month":dt.month,
              "longitude":float(row["decimalLongitude"]),
              "latitude":float(row["decimalLatitude"]),
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            child_count[pid]+=1
            d=maybe_float(row["minimumDepthInMeters"])
            if math.isfinite(d): child_depth[pid].append(d)
        else:
            raise RuntimeError(f"unsupported event type {typ}")
    rows=[]
    min_depths=int(C["visit_depth"]["minimum_point_depths"])
    for pid,p in parents.items():
        if child_count.get(pid,0)<3: continue
        depths=np.asarray(child_depth.get(pid,[]),dtype=float)
        if len(depths)<min_depths: continue
        if p["segment"] is None: continue
        rows.append({
          **p,
          "point_count":int(child_count[pid]),
          "depth_n":int(len(depths)),
          "depth_median_m":float(np.median(depths)),
          "depth_iqr_m":float(np.quantile(depths,.75)-np.quantile(depths,.25)),
        })
    return pd.DataFrame(rows).sort_values(["node_id","date"]).reset_index(drop=True)

def previous_months(year,month,n):
    vals=[]
    y=int(year); m=int(month)
    for k in range(1,n+1):
        mm=m-k; yy=y
        while mm<=0:
            mm+=12; yy-=1
        vals.append((yy,mm))
    return vals

def add_exposure(visits,wq):
    w=wq[["segment","year","month","secchi"]].copy()
    w=w[w["secchi"].notna() & (w["secchi"]>0)].copy()
    lookup={(str(r.segment),int(r.year),int(r.month)):float(r.secchi) for r in w.itertuples()}
    rows=[]
    for r in visits.to_dict("records"):
        out=dict(r)
        for n,label,min_months in [
            (6,"6m",int(C["windows"]["primary_minimum_months"])),
            (3,"3m",int(C["windows"]["sensitivity_minimum_months"])),
        ]:
            vals=[]; secchis=[]
            for yy,mm in previous_months(r["year"],r["month"],n):
                sec=lookup.get((r["segment"],yy,mm))
                if sec is None: continue
                kd=1.7/sec
                frac=math.exp(-kd*float(r["depth_median_m"]))
                vals.append(frac); secchis.append(sec)
            out[f"pre_{label}_months"]=int(len(vals))
            out[f"pre_{label}_benthic_fraction_mean"]=float(np.mean(vals)) if len(vals)>=min_months else math.nan
            out[f"pre_{label}_secchi_mean"]=float(np.mean(secchis)) if len(secchis)>=min_months else math.nan
        rows.append(out)
    return pd.DataFrame(rows)

def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    wq=pd.read_csv(input_dir/"water_quality_monthly.csv")
    required={"segment","year","month","secchi"}
    if missing:=required.difference(wq.columns):
        raise RuntimeError(f"water quality missing {sorted(missing)}")
    visits=parse_visits(fetch())
    x=add_exposure(visits,wq)
    primary=x[x["pre_6m_benthic_fraction_mean"].notna()].copy()
    by_segment=(primary.groupby("water_body",as_index=False)
                .agg(visits=("unit_id","size"),nodes=("node_id","nunique"),
                     years=("year","nunique"),
                     depth_median=("depth_median_m","median"),
                     benthic_fraction_median=("pre_6m_benthic_fraction_mean","median")))
    summary={
      "schema":"tampa.benthic_light_exposure_v1.preflight",
      "status":"preflight_pass" if (
        len(primary)>=int(C["preflight_pass"]["minimum_eligible_visits_with_primary_exposure"])
        and primary["node_id"].nunique()>=int(C["preflight_pass"]["minimum_stable_nodes_with_primary_exposure"])
        and primary["year"].nunique()>=int(C["preflight_pass"]["minimum_calendar_years_with_primary_exposure"])
      ) else "preflight_stop",
      "response_access":{"focal_response_opened":False},
      "event_source":{"commit":COMMIT,"size":SIZE,"blob":BLOB,"verified":True},
      "water_quality_source":"analysis/02_water_quality_screen.py output from pinned wq-static source",
      "eligible_segments":SEGMENT_MAP,
      "registry":{
        "physical_eligible_visits":int(len(visits)),
        "primary_exposure_visits":int(len(primary)),
        "primary_exposure_nodes":int(primary["node_id"].nunique()),
        "primary_exposure_years":[int(primary["year"].min()),int(primary["year"].max())] if len(primary) else None,
        "primary_exposure_year_count":int(primary["year"].nunique()),
        "sensitivity_3m_visits":int(x["pre_3m_benthic_fraction_mean"].notna().sum())
      },
      "exposure":{
        "primary_window":"previous 6 complete calendar months",
        "sensitivity_window":"previous 3 complete calendar months",
        "secchi_to_kd":"Kd=1.7/SecchiDepth",
        "benthic_fraction":"exp(-Kd*visit_depth_median)",
        "primary_fraction_range":[float(primary["pre_6m_benthic_fraction_mean"].min()),float(primary["pre_6m_benthic_fraction_mean"].max())] if len(primary) else None,
        "primary_fraction_median":float(primary["pre_6m_benthic_fraction_mean"].median()) if len(primary) else None
      },
      "by_segment":by_segment.to_dict("records"),
      "next_gate":C["next_gate"],
      "claim_boundary":C["claim_boundary"]
    }
    x.to_csv(outdir/"benthic_light_visit_exposure_preflight.csv",index=False)
    by_segment.to_csv(outdir/"benthic_light_preflight_by_segment.csv",index=False)
    (outdir/"benthic_light_exposure_preflight_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_benthic_light"))
    p.add_argument("--out",type=Path,default=Path("results/generated_benthic_light"))
    a=p.parse_args(); main(a.input,a.out)
