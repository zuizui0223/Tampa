#!/usr/bin/env python3
"""Response-independent depth-relevance audit for TBOFS mapped Tampa nodes.

Reads no Thalassia response. It compares pinned physical point-depth summaries from
Darwin Core Event with TBOFS model bathymetry at the already selected response-blind
current-support cells. This is descriptive physical validation, not a mechanism test.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
import numpy as np

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
EVENT_URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc/event.csv"
EVENT_SIZE=24654717
EVENT_BLOB="583b4d4e328290ab065346579eb4f29f03ea0f99"
CORE={"Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay"}

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def download(url):
    req=Request(url,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-TBOFS-depth-audit/1.0"})
    with urlopen(req,timeout=180) as resp:
        return resp.read()

def maybe_float(x):
    try:
        y=float(str(x).strip())
    except Exception:
        return math.nan
    return y if math.isfinite(y) else math.nan

def node_depths(data:bytes):
    if len(data)!=EVENT_SIZE or git_blob_sha1(data)!=EVENT_BLOB:
        raise RuntimeError("pinned event identity drift")
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    parent_meta={}
    children=defaultdict(list)
    for row in reader:
        typ=row["eventType"].strip()
        if typ=="Transect":
            parent_meta[row["eventID"].strip()]={
                "node_id":row["locationID"].strip(),
                "water_body":row["waterBody"].strip(),
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            children[pid].append(maybe_float(row["minimumDepthInMeters"]))
    bynode=defaultdict(list); wb={}
    for pid,vals in children.items():
        if pid not in parent_meta or len(vals)<3:
            continue
        n=parent_meta[pid]["node_id"]
        wb[n]=parent_meta[pid]["water_body"]
        bynode[n].extend(x for x in vals if math.isfinite(x))
    out={}
    for n,vals in bynode.items():
        a=np.asarray(vals,dtype=float)
        out[n]={
            "water_body":wb[n],
            "point_depth_n":int(a.size),
            "observed_depth_median_m":float(np.median(a)) if a.size else None,
            "observed_depth_q25_m":float(np.quantile(a,0.25)) if a.size else None,
            "observed_depth_q75_m":float(np.quantile(a,0.75)) if a.size else None,
        }
    if len(out)!=71:
        raise RuntimeError(f"depth node registry drift: {len(out)}")
    return out

def summarize(rows):
    obs=np.array([r["observed_depth_median_m"] for r in rows],dtype=float)
    mod=np.array([r["model_bathymetry_m"] for r in rows],dtype=float)
    delta=mod-obs
    return {
        "nodes":len(rows),
        "observed_depth_median_across_nodes_m":float(np.median(obs)),
        "model_bathymetry_median_across_nodes_m":float(np.median(mod)),
        "median_model_minus_observed_m":float(np.median(delta)),
        "median_abs_model_minus_observed_m":float(np.median(np.abs(delta))),
        "p90_abs_model_minus_observed_m":float(np.quantile(np.abs(delta),0.9)),
        "max_abs_model_minus_observed_m":float(np.max(np.abs(delta))),
        "model_deeper_than_observed_nodes":int((delta>0).sum()),
        "model_at_2m_floor_nodes":int(np.isclose(mod,2.0,atol=1e-9).sum()),
        "observed_below_1m_nodes":int((obs<1.0).sum()),
        "observed_below_2m_nodes":int((obs<2.0).sum()),
        "pearson_depth_correlation":float(np.corrcoef(obs,mod)[0,1]) if len(rows)>2 and np.std(obs)>0 and np.std(mod)>0 else None,
    }

def main(mapping_json:Path,out:Path):
    m=json.loads(mapping_json.read_text())
    depth=node_depths(download(EVENT_URL))
    rows=[]
    for x in m["mapping"]["nodes"]:
        d=depth[x["node_id"]]
        if d["observed_depth_median_m"] is None or x.get("model_bathymetry_m") is None:
            continue
        rows.append({
            "node_id":x["node_id"],
            "water_body":x["water_body"],
            "mapping_distance_km":x["distance_km"],
            "model_bathymetry_m":x["model_bathymetry_m"],
            **{k:v for k,v in d.items() if k!="water_body"},
            "model_minus_observed_m":float(x["model_bathymetry_m"]-d["observed_depth_median_m"]),
        })
    core=[r for r in rows if r["water_body"] in CORE]
    result={
        "schema":"tampa.tbofs_depth_relevance_audit_v1",
        "status":"response_independent_physical_relevance_audit",
        "response_blind":True,
        "source":{
            "event_commit":COMMIT,
            "tbofs_mapping_source":str(mapping_json),
        },
        "all_nodes":summarize(rows),
        "tri_bay_core":summarize(core),
        "by_water_body":{
            wb:summarize([r for r in rows if r["water_body"]==wb])
            for wb in sorted({r["water_body"] for r in rows})
        },
        "largest_absolute_mismatches":sorted(
            rows,key=lambda r:abs(r["model_minus_observed_m"]),reverse=True
        )[:10],
        "nodes":rows,
        "interpretation_boundary":[
            "Observed depth is a point-visit physical measurement and includes tide/sampling variation; it is not exact chart bathymetry.",
            "TBOFS h is model bathymetry and may include a minimum-depth treatment; mismatch does not by itself invalidate large-scale flow exposure.",
            "Large systematic depth mismatch weakens any claim that sigma-layer-0 velocity is literal meadow-canopy near-bed current.",
            "No focal biological state or outcome is read in this audit."
        ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "all_nodes":result["all_nodes"],
        "tri_bay_core":result["tri_bay_core"],
        "largest_absolute_mismatches":result["largest_absolute_mismatches"][:5],
    },indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mapping",type=Path,default=Path("results/generated_tbofs_preflight/tbofs_hydrodynamic_preflight_v1.json"))
    p.add_argument("--out",type=Path,default=Path("results/generated_tbofs_preflight/tbofs_depth_relevance_audit_v1.json"))
    a=p.parse_args(); main(a.mapping,a.out)
