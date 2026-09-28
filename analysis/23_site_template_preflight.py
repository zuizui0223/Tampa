#!/usr/bin/env python3
"""Response-independent preflight for persistent Tampa transect site-template covariates.

Uses only fixed source identity plus physical point depth and sediment measurements.
It does not read or model focal Thalassia occurrence/cover outcomes.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
import numpy as np
import pandas as pd

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
    "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
    "emof":{"url":f"{BASE}/emof.csv","size":16449353,"blob":"e463046726080334637824555309fd89c7c447da"},
}
EVENT_HEADER=["eventID","parentEventID","eventType","eventDate","year","month","day","decimalLatitude","decimalLongitude","geodeticDatum","minimumDepthInMeters","maximumDepthInMeters","country","countryCode","stateProvince","waterBody","locality","locationID","samplingProtocol","institutionCode","datasetName","datasetID","license","locationRemarks"]
EMOF_HEADER=["eventID","occurrenceID","measurementType","measurementTypeID","measurementValue","measurementUnit","measurementUnitID","measurementRemarks"]
SEDIMENT_TYPE="sediment type"

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-site-template-preflight/1.0"})
    with urlopen(req,timeout=180) as resp:
        data=resp.read(spec["size"]+1)
    if len(data)!=spec["size"]:
        raise RuntimeError(f"size drift {spec['url']} {len(data)}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError(f"blob drift {spec['url']}")
    return data

def maybe_float(x):
    try:
        y=float(str(x).strip())
    except Exception:
        return math.nan
    return y if math.isfinite(y) else math.nan

def norm_sediment(x):
    return " ".join(str(x).strip().lower().split())

def parse_event(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EVENT_HEADER:
        raise RuntimeError("event header drift")
    parents={}
    child_rows={}
    parent_children=defaultdict(list)
    for row in reader:
        eid=row["eventID"].strip()
        typ=row["eventType"].strip()
        if typ=="Transect":
            parents[eid]={
                "node_id":row["locationID"].strip(),
                "water_body":row["waterBody"].strip(),
                "longitude":float(row["decimalLongitude"]),
                "latitude":float(row["decimalLatitude"]),
            }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            depth=maybe_float(row["minimumDepthInMeters"])
            child_rows[eid]={"parent_id":pid,"depth_m":depth}
            parent_children[pid].append(eid)
        else:
            raise RuntimeError(f"unsupported event type {typ}")
    eligible={pid for pid in parents if len(parent_children.get(pid,[]))>=3}
    child_rows={eid:r for eid,r in child_rows.items() if r["parent_id"] in eligible}
    return parents,eligible,child_rows

def parse_sediment(data:bytes,child_rows):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    if reader.fieldnames!=EMOF_HEADER:
        raise RuntimeError("emof header drift")
    by_event=defaultdict(set)
    raw_rows=0
    for row in reader:
        if row["measurementType"]!=SEDIMENT_TYPE:
            continue
        eid=row["eventID"].strip()
        if eid not in child_rows:
            continue
        val=norm_sediment(row["measurementValue"])
        if not val:
            continue
        raw_rows+=1
        by_event[eid].add(val)
    conflicts={eid:sorted(vals) for eid,vals in by_event.items() if len(vals)>1}
    resolved={eid:next(iter(vals)) for eid,vals in by_event.items() if len(vals)==1}
    return raw_rows,resolved,conflicts

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    raw={k:fetch(v) for k,v in FILES.items()}
    parents,eligible,children=parse_event(raw["event"])
    sediment_raw,sed_by_event,conflicts=parse_sediment(raw["emof"],children)

    node_depth=defaultdict(list)
    node_sed=defaultdict(list)
    node_meta={}
    for eid,c in children.items():
        p=parents[c["parent_id"]]
        node=p["node_id"]
        node_meta[node]=p
        if math.isfinite(c["depth_m"]):
            node_depth[node].append(float(c["depth_m"]))
        if eid in sed_by_event:
            node_sed[node].append(sed_by_event[eid])

    rows=[]
    all_categories=Counter()
    for node in sorted(node_meta):
        p=node_meta[node]
        depths=np.asarray(node_depth.get(node,[]),dtype=float)
        sediments=node_sed.get(node,[])
        counts=Counter(sediments)
        all_categories.update(counts)
        total=sum(counts.values())
        modal=None
        modal_fraction=None
        if total:
            modal_count=max(counts.values())
            modal=sorted([k for k,v in counts.items() if v==modal_count])[0]
            modal_fraction=float(modal_count/total)
        probs=np.asarray([v/total for v in counts.values()],dtype=float) if total else np.asarray([])
        entropy=float(-np.sum(probs*np.log(probs))) if len(probs) else None
        rows.append({
            "node_id":node,
            "water_body":p["water_body"],
            "longitude":p["longitude"],
            "latitude":p["latitude"],
            "depth_n":int(len(depths)),
            "depth_median_m":float(np.median(depths)) if len(depths) else None,
            "depth_q25_m":float(np.quantile(depths,0.25)) if len(depths) else None,
            "depth_q75_m":float(np.quantile(depths,0.75)) if len(depths) else None,
            "depth_iqr_m":float(np.quantile(depths,0.75)-np.quantile(depths,0.25)) if len(depths) else None,
            "sediment_point_events":int(total),
            "sediment_category_count":int(len(counts)),
            "sediment_modal":modal,
            "sediment_modal_fraction":modal_fraction,
            "sediment_entropy":entropy,
        })
    node=pd.DataFrame(rows)
    node.to_csv(outdir/"site_template_node_preflight.csv",index=False)

    summary={
        "schema":"tampa.site_template_preflight_v1",
        "status":"physical_covariate_preflight",
        "response_access":{
            "thalassia_occurrence_opened":False,
            "thalassia_cover_opened":False,
            "event_physical_depth_opened":True,
            "emof_sediment_rows_opened":True,
            "sediment_parsed_across_all_occurrences_without_taxon_filter":True,
        },
        "source":{"commit":COMMIT,"files":{k:{"size":v["size"],"blob":v["blob"]} for k,v in FILES.items()}},
        "registry":{
            "eligible_transect_visits":int(len(eligible)),
            "stable_nodes":int(len(node)),
            "point_events":int(len(children)),
        },
        "depth":{
            "nodes_with_depth":int((node["depth_n"]>0).sum()),
            "nodes_without_depth":int((node["depth_n"]==0).sum()),
            "minimum_point_depth_observations_per_covered_node":int(node.loc[node["depth_n"]>0,"depth_n"].min()) if (node["depth_n"]>0).any() else 0,
            "median_point_depth_observations_per_covered_node":float(node.loc[node["depth_n"]>0,"depth_n"].median()) if (node["depth_n"]>0).any() else 0,
        },
        "sediment":{
            "raw_emof_sediment_rows":int(sediment_raw),
            "unique_point_events_with_single_sediment":int(len(sed_by_event)),
            "point_events_with_conflicting_sediment_labels":int(len(conflicts)),
            "conflict_examples":dict(list(sorted(conflicts.items()))[:10]),
            "nodes_with_sediment":int((node["sediment_point_events"]>0).sum()),
            "nodes_without_sediment":int((node["sediment_point_events"]==0).sum()),
            "categories":dict(sorted(all_categories.items())),
            "category_count":int(len(all_categories)),
        },
        "next_gate":"Freeze the site-template outcome model only after depth/sediment coverage and label structure are known from this response-independent preflight.",
        "claim_boundary":[
            "Depth is a point-visit physical measurement and may include tidal/sampling variation; node summaries are habitat-template proxies, not exact bathymetry.",
            "Sediment eMoF rows are parsed across all occurrence records without selecting Thalassia, but sediment availability can still depend on biological sampling/record structure.",
            "No focal response model is fit in this preflight."
        ]
    }
    (outdir/"site_template_preflight_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_site_template"))
    a=p.parse_args(); main(a.out)
