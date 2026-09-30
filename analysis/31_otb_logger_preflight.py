#!/usr/bin/env python3
"""Response-independent source/alignment gate for OTB continuous temperature loggers."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/otb_continuous_logger_preflight_v1_contract.json").read_text())

EVENT_BLOB=C["tampa_registry_source"]["event_git_blob_sha1"]

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def haversine(lon1,lat1,lon2,lat2):
    r=6371.0
    a1=np.radians(np.asarray(lat1,dtype=float))
    a2=np.radians(np.asarray(lat2,dtype=float))
    dlat=a2-a1
    dlon=np.radians(np.asarray(lon2,dtype=float)-np.asarray(lon1,dtype=float))
    a=np.sin(dlat/2)**2+np.cos(a1)*np.cos(a2)*np.sin(dlon/2)**2
    return 2*r*np.arcsin(np.minimum(1.0,np.sqrt(a)))

def parse_otb_nodes(event_path:Path):
    data=event_path.read_bytes()
    if git_blob_sha1(data)!=EVENT_BLOB:
        raise RuntimeError("Tampa Event Git blob drift")
    reader=csv.DictReader(io.StringIO(data.decode("utf-8"),newline=""))
    rows=[]
    for row in reader:
        if row["eventType"].strip()!="Transect":
            continue
        if row["waterBody"].strip()!="Old Tampa Bay":
            continue
        rows.append({
            "node_id":row["locationID"].strip(),
            "longitude":float(row["decimalLongitude"]),
            "latitude":float(row["decimalLatitude"]),
        })
    d=pd.DataFrame(rows)
    if d.empty:
        raise RuntimeError("no Old Tampa Bay transect rows")
    # All repeated visits of a stable node must have effectively fixed coordinates.
    audit=(d.groupby("node_id")
             .agg(longitude_min=("longitude","min"),longitude_max=("longitude","max"),
                  latitude_min=("latitude","min"),latitude_max=("latitude","max"),
                  visits=("node_id","size"))
             .reset_index())
    if ((audit.longitude_max-audit.longitude_min).abs()>1e-6).any() or ((audit.latitude_max-audit.latitude_min).abs()>1e-6).any():
        raise RuntimeError("Old Tampa Bay stable-node coordinate drift")
    nodes=(d.groupby("node_id",as_index=False)
             .agg(longitude=("longitude","first"),latitude=("latitude","first"),visits=("node_id","size")))
    return nodes.sort_values("node_id").reset_index(drop=True)

def main(meta_path:Path,deploy_path:Path,event_path:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    meta=pd.read_csv(meta_path)
    dep=pd.read_csv(deploy_path)
    nodes=parse_otb_nodes(event_path)

    reqm={"yr_site_logger","yr","site","logger","deploy_date","depthm","longitude","latitude"}
    reqd={"yr_site_logger","yr","site","logger","rows","duration_days","median_interval_minutes","temp_min_c","temp_max_c"}
    if miss:=reqm.difference(meta.columns): raise RuntimeError(f"metadata missing {sorted(miss)}")
    if miss:=reqd.difference(dep.columns): raise RuntimeError(f"deployment summary missing {sorted(miss)}")

    merged=dep.merge(
        meta[["yr_site_logger","deploy_date","stratum","depthm","longitude","latitude"]],
        on="yr_site_logger",how="left",validate="one_to_one",indicator=True
    )
    key_match=float((merged["_merge"]=="both").mean())
    merged=merged.drop(columns=["_merge"])
    if merged[["longitude","latitude"]].isna().any().any():
        # Preserve unmatched rows in denominator; they cannot qualify spatially.
        pass

    q=C["logger_quality_gate"]
    merged["qualified_temporal"]=(
        (merged["duration_days"]>=float(q["qualified_deployment_minimum_duration_days"])) &
        (merged["median_interval_minutes"]<=float(q["qualified_deployment_maximum_median_interval_minutes"])) &
        merged["longitude"].notna() & merged["latitude"].notna()
    )

    # Nearest fixed OTB transect for each deployment.
    nearest_node=[]; nearest_km=[]
    for r in merged.itertuples(index=False):
        if not (math.isfinite(float(r.longitude)) and math.isfinite(float(r.latitude))):
            nearest_node.append(None); nearest_km.append(np.nan); continue
        dist=haversine(float(r.longitude),float(r.latitude),nodes["longitude"].to_numpy(),nodes["latitude"].to_numpy())
        j=int(np.argmin(dist))
        nearest_node.append(str(nodes.iloc[j]["node_id"]))
        nearest_km.append(float(dist[j]))
    merged["nearest_fixed_node"]=nearest_node
    merged["nearest_fixed_distance_km"]=nearest_km

    primary=float(C["spatial_alignment_gate"]["primary_max_distance_km"])
    sens=float(C["spatial_alignment_gate"]["sensitivity_max_distance_km"])
    merged["primary_spatial_match"]=merged["qualified_temporal"] & (merged["nearest_fixed_distance_km"]<=primary)
    merged["sensitivity_spatial_match"]=merged["qualified_temporal"] & (merged["nearest_fixed_distance_km"]<=sens)

    qualified=merged[merged["qualified_temporal"]].copy()
    primary_rows=merged[merged["primary_spatial_match"]].copy()
    sens_rows=merged[merged["sensitivity_spatial_match"]].copy()

    total_temp_rows=int(dep["rows"].sum())
    years=sorted(qualified["yr"].dropna().astype(int).unique().tolist())
    temporal_pass=(
      len(years)>=int(q["minimum_unique_years"]) and
      len(qualified)>=int(q["minimum_qualified_deployments"]) and
      total_temp_rows>=int(q["minimum_temperature_rows"]) and
      key_match>=float(q["minimum_metadata_key_match_fraction"])
    )
    unique_primary=int(primary_rows["nearest_fixed_node"].nunique())
    spatial_pass=unique_primary>=int(C["spatial_alignment_gate"]["minimum_unique_fixed_transects_with_primary_match"])
    status=("preflight_pass" if temporal_pass and spatial_pass else
            "temporal_pass_spatial_stop" if temporal_pass else
            "source_stop")

    byyear=(qualified.groupby("yr",as_index=False)
            .agg(qualified_deployments=("yr_site_logger","size"),
                 unique_logger_sites=("site","nunique"),
                 median_duration_days=("duration_days","median"),
                 median_interval_minutes=("median_interval_minutes","median"),
                 max_temperature_c=("temp_max_c","max")))
    bynode=(primary_rows.groupby("nearest_fixed_node",as_index=False)
            .agg(deployments=("yr_site_logger","size"),
                 logger_years=("yr","nunique"),
                 logger_sites=("site","nunique"),
                 nearest_distance_km=("nearest_fixed_distance_km","min"),
                 median_distance_km=("nearest_fixed_distance_km","median"),
                 first_logger_year=("yr","min"),last_logger_year=("yr","max")))
    if len(bynode):
        bynode=bynode.sort_values(["nearest_distance_km","nearest_fixed_node"])

    summary={
      "schema":"tampa.otb_continuous_logger_preflight_v1.result",
      "status":status,
      "source":{
        "repository":C["logger_source"]["repository"],
        "commit":C["logger_source"]["commit"],
        "metadata_git_blob_sha1":C["logger_source"]["metadata_git_blob_sha1"],
        "temperature_git_blob_sha1":C["logger_source"]["temperature_git_blob_sha1"],
        "tampa_event_git_blob_sha1":EVENT_BLOB
      },
      "response_access":{"focal_thalassia_response_opened":False},
      "registry":{
        "logger_metadata_rows":int(len(meta)),
        "logger_deployments":int(len(dep)),
        "temperature_rows":total_temp_rows,
        "metadata_key_match_fraction":key_match,
        "qualified_deployments":int(len(qualified)),
        "qualified_years":years,
        "qualified_year_count":int(len(years)),
        "fixed_otb_transects":int(len(nodes))
      },
      "temporal_quality":{
        "pass":bool(temporal_pass),
        "median_qualified_duration_days":float(qualified["duration_days"].median()) if len(qualified) else None,
        "median_qualified_interval_minutes":float(qualified["median_interval_minutes"].median()) if len(qualified) else None,
        "p95_qualified_interval_minutes":float(qualified["median_interval_minutes"].quantile(.95)) if len(qualified) else None,
        "maximum_observed_temperature_c":float(qualified["temp_max_c"].max()) if len(qualified) else None,
      },
      "spatial_alignment":{
        "primary_threshold_km":primary,
        "primary_matched_deployments":int(len(primary_rows)),
        "primary_unique_fixed_transects":unique_primary,
        "primary_unique_logger_sites":int(primary_rows["site"].nunique()),
        "primary_pass":bool(spatial_pass),
        "sensitivity_threshold_km":sens,
        "sensitivity_matched_deployments":int(len(sens_rows)),
        "sensitivity_unique_fixed_transects":int(sens_rows["nearest_fixed_node"].nunique()),
        "sensitivity_is_descriptive_only":True,
        "qualified_nearest_distance_median_km":float(qualified["nearest_fixed_distance_km"].median()) if len(qualified) else None,
        "qualified_nearest_distance_q90_km":float(qualified["nearest_fixed_distance_km"].quantile(.90)) if len(qualified) else None,
      },
      "decision":C["decision_map"][status if status in C["decision_map"] else "source_stop"],
      "claim_boundary":C["claim_boundary"]
    }
    merged.to_csv(outdir/"otb_logger_deployment_crosswalk.csv",index=False)
    byyear.to_csv(outdir/"otb_logger_preflight_by_year.csv",index=False)
    bynode.to_csv(outdir/"otb_logger_primary_matched_fixed_nodes.csv",index=False)
    nodes.to_csv(outdir/"otb_fixed_transect_registry.csv",index=False)
    (outdir/"otb_continuous_logger_preflight_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--metadata",type=Path,required=True)
    p.add_argument("--deployments",type=Path,required=True)
    p.add_argument("--event",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    main(a.metadata,a.deployments,a.event,a.out)
