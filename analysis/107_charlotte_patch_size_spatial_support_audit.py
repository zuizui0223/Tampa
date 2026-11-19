#!/usr/bin/env python3
"""Patch-size and coarse-spatial-support audit of mapped seagrass/algae stability.

Uses SHA256-pinned successful 2022/2024 original SWFWMD FeatureServer GeoJSON
archive. Builds no new cohort and reads no live biological response.
2024 "same mapped class" is the endpoint; no plant survival/competition claim.

Two *descriptive* restrictions fixed before this script's outcome access:
  (A) size bins: [0,0.5),[0.5,2),[2,10),[10,50),[50,inf) acres;
      direct standardization to the 2022 attached-algae *area* distribution
      on size bins with >=3 source polygons per class and >=1 acre per class.
  (B) 5km map grids in EPSG:6933 using each source polygon's in-polygon
      representative point; bin x grid cells with >=2 source polygons per
      class and >=0.5 acre per class, standardized to algae area share.

Bins and map-grid criteria are NOT optimized against the 2024 responses. If
algae common-support area is <80%, do NOT make full-area adjusted claims.
The 5km centroid grid is a support check, not a spatial causal adjustment.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("ch106",ROOT/"analysis/106_charlotte_archived_map_class_retention.py")
P=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)
G=P.G
BINS=((0.0,0.5,"lt0.5ac"),(0.5,2.0,"0.5-2ac"),(2.0,10.0,"2-10ac"),
      (10.0,50.0,"10-50ac"),(50.0,math.inf,"ge50ac"))
GRID_M=5000
GROUPS=("seagrass","attached_macroalgae")
MIN_SIZE_N=3
MIN_SIZE_AREA_AC=1.0
MIN_CELL_N=2
MIN_CELL_AREA_AC=0.5
MIN_COVERAGE=0.8

class Stop(RuntimeError):pass

def _size_bin(area_ac):
    for lo,hi,label in BINS:
        if lo<=area_ac<hi:return label
    raise Stop("INVALID_SOURCE_ACREAGE")

def _props_geom(feature):
    p=feature.get("properties") or {}
    area_off=p.get("Geodesic")
    if not isinstance(area_off,(int,float)) or not math.isfinite(area_off) or area_off<=0:
        raise Stop("SOURCE_OFFICIAL_ACRE_MISSING")
    g=G.shape(feature.get("geometry"))
    if g.geom_type not in ("Polygon","MultiPolygon") or g.is_empty:
        raise Stop("INVALID_SOURCE_GEOMETRY")
    if not g.is_valid:
        pieces=G.polygon_parts(G.make_valid(g))
        if not pieces:raise Stop("INVALID_SOURCE_REPAIR")
        g=G.unary_union(pieces)
    q=G.transform(G.TRANSFORM,g)
    if not q.is_valid or q.area<=0:
        raise Stop("INVALID_PROJECTED_SOURCE_GEOMETRY")
    acres=q.area/G.M2_PER_ACRE
    if abs(acres-area_off)>max(0.005,0.002*area_off):
        raise Stop("ORIGINAL_ACRE_FIELD_FAILED_INDEPENDENT_REVALIDATION")
    return p,q,acres

def annotate_patches(features,target):
    sea_union=G.unary_union([target[9113],target[9116]])
    algae_union=target[9121]
    if sea_union.area<=0 or algae_union.area<=0:raise Stop("FROZEN_TARGET_CLASS_UNESTIMABLE")
    groups=defaultdict(list)
    unique=set()
    for f in features:
        props,geom,area_ac=_props_geom(f)
        fid=props.get("FID");code=props.get("FLUCCSCODE")
        if not isinstance(fid,int) or fid in unique:
            raise Stop("DUPLICATE_OR_UNKNOWN_SOURCE_OID")
        if code not in (9113,9116,9121):
            raise Stop("SOURCE_CLASS_OUTSIDE_FROZEN_DICTIONARY")
        unique.add(fid)
        class_name="attached_macroalgae" if code==9121 else "seagrass"
        other=algae_union if code==9121 else sea_union
        area_ret=geom.intersection(other).area/G.M2_PER_ACRE
        exact_ret=geom.intersection(target[code]).area/G.M2_PER_ACRE
        if area_ret>area_ac+1e-6 or exact_ret>area_ac+1e-6:
            raise Stop("IMPLAUSIBLE_AREA_OVERLAP")
        rep=geom.representative_point()
        b=_size_bin(area_ac)
        key=f"{math.floor(rep.x/GRID_M)}:{math.floor(rep.y/GRID_M)}"
        groups[class_name].append({
          "fid":fid,"code":code,"source_acres":area_ac,
          "same_group_retained_acres":area_ret,
          "exact_code_retained_acres":exact_ret,
          "size_bin":b,"grid_id":key})
    if len(groups["attached_macroalgae"])!=95 or len(groups["seagrass"])!=2208:
        raise Stop("FROZEN_2022_PATCH_COUNTS_CHANGED")
    return groups

def _summ(rows):
    n=len(rows)
    total=sum(x["source_acres"] for x in rows)
    ret=sum(x["same_group_retained_acres"] for x in rows)
    exact=sum(x["exact_code_retained_acres"] for x in rows)
    if total<=0:return {"patches":n,"source_area_acres":0,"retained_area_acres":0,
                        "same_class_rate_percent":None,"exact_code_rate_percent":None}
    return {"patches":n,"source_area_acres":round(total,3),
            "retained_area_acres":round(ret,3),
            "same_class_rate_percent":round(100*ret/total,3),
            "exact_code_rate_percent":round(100*exact/total,3)}

def _matched(groups,key_fn,min_count,min_area):
    cells=defaultdict(lambda:{group:[] for group in GROUPS})
    for group, rows in groups.items():
        for row in rows: cells[key_fn(row)][group].append(row)
    out={}
    accepted=[]
    for key, d in sorted(cells.items()):
        s={g:_summ(d[g]) for g in GROUPS}
        eligible=all(s[g]["patches"]>=min_count and
                     s[g]["source_area_acres"]>=min_area for g in GROUPS)
        out[str(key)]={g:s[g] for g in GROUPS}
        out[str(key)]["in_common_support"]=eligible
        if eligible: accepted.append((key,d))
    algae_total=sum(x["source_acres"] for x in groups["attached_macroalgae"])
    sea_total=sum(x["source_acres"] for x in groups["seagrass"])
    algae_shared=sum(sum(x["source_acres"] for x in d["attached_macroalgae"]) for _,d in accepted)
    sea_shared=sum(sum(x["source_acres"] for x in d["seagrass"]) for _,d in accepted)
    if algae_total<=0 or sea_total<=0:raise Stop("UNESTIMABLE_ORIGINAL_GROUP")
    weight_sum=0.0
    weighted={g:0.0 for g in GROUPS}
    for _,d in accepted:
        algae_area=sum(x["source_acres"] for x in d["attached_macroalgae"])
        if algae_area<=0:raise Stop("ZERO_ALGAE_MATCHED_WEIGHT")
        frac=algae_area
        for g in GROUPS:
            total=sum(x["source_acres"] for x in d[g])
            retained=sum(x["same_group_retained_acres"] for x in d[g])
            weighted[g]+=frac*(retained/total)
        weight_sum+=frac
    coverage=algae_shared/algae_total
    if accepted and weight_sum>0:
        weighted={g:round(100*v/weight_sum,3) for g,v in weighted.items()}
        contrast=round(weighted["seagrass"]-weighted["attached_macroalgae"],3)
    else:
        weighted=None
        contrast=None
    return {
      "matched_n_cells":len(accepted),
      "all_n_cells":len(cells),
      "matched_algae_area_acres":round(algae_shared,3),
      "matched_seagrass_area_acres":round(sea_shared,3),
      "algae_source_area_with_comparable_seagrass_percent":round(100*coverage,3),
      "seagrass_source_area_with_comparable_algae_percent":round(100*sea_shared/sea_total,3),
      "standardization_target":"source-area share of attached macroalgae in eligible bins/cells",
      "weighted_mapped_same_class_persistence_percent":weighted,
      "weighted_seagrass_minus_algae_points":contrast,
      "can_generalize_to_full_algae_area":coverage>=MIN_COVERAGE,
      "if_low_support":"If algae coverage <80%, weighted contrast is explicitly conditional on matched bins, not a classwide adjusted effect.",
      "cell_data":out,
    }

def run(groups, frozen):
    observed={g:_summ(groups[g]) for g in GROUPS}
    reference=frozen["results"]["classes"]
    for g in GROUPS:
        f=reference[g]
        if abs(observed[g]["source_area_acres"]-f["2022_class_area_acres"])>.004:
            raise Stop("PATCH_AREA_DOES_NOT_REPRODUCE_FROZEN_2022_UNION")
        if abs(observed[g]["retained_area_acres"]-
               f["boundary_interior_m"]["0"]["same_class_overlap_acres"])>.004:
            raise Stop("PATCH_RETENTION_DOES_NOT_REPRODUCE_FROZEN_AREA")
    size=_matched(groups,lambda x:x["size_bin"],MIN_SIZE_N,MIN_SIZE_AREA_AC)
    grid=_matched(groups,lambda x:x["grid_id"],MIN_CELL_N,MIN_CELL_AREA_AC)
    size_grid=_matched(groups,lambda x:x["size_bin"]+"|"+x["grid_id"],MIN_CELL_N,MIN_CELL_AREA_AC)
    return {
      "schema":"tampa.charlotte_patch_size_spatial_support_retention_v1",
      "status":"SOURCE_ARCHIVE_VERIFIED_POSTHOC_DESCRIPTIVE_SIZE_AND_GRID_SUPPORT",
      "fixed_bins_acres":[[lo,hi if math.isfinite(hi) else "inf",label] for lo,hi,label in BINS],
      "fixed_grid_width_metres":GRID_M,
      "support_gates":{"size_n_each":MIN_SIZE_N,"size_area_each_acres":MIN_SIZE_AREA_AC,
                       "spatial_n_each":MIN_CELL_N,"spatial_area_each_acres":MIN_CELL_AREA_AC,
                       "minimum_algae_source_area_support_percent":80},
      "unmatched_original":{"by_2022_class":observed,
          "strict_same_FLUCCS_code_seagrass_percent":observed["seagrass"]["exact_code_rate_percent"]},
      "size_stratification":size,
      "five_kilometre_representative_point_grid":grid,
      "size_by_grid_stratification":size_grid,
      "no_causal_or_demographic_interpretation":True,
      "no_independent_polygon_sample_size":True,
      "no_unmapped_as_bare":True,
      "limitations":[
          "A size-matched map-class retention contrast does NOT control photographic detection, phenology, water depth, patch shape or plant demographic survival.",
          "Source polygons are spatially dependent; no p values or independent observational replicates are inferred.",
          "The 5km grid is based on representative point of each source polygon; large polygons cross grid cells, so the grid is only a coarse geographic common-support screen.",
          "Both class aggregation (patchy+continuous seagrass) and strict original FLUCCS code are reported to expose categorical coarsening.",
          "If common-support algae area <80%, do not generalize to entire algae mapped footprint.",
          "Same region, same remote sensing agency, post-hoc; not independent external validation."
      ]
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--archive-root",required=True)
    a.add_argument("--out",required=True)
    args=a.parse_args()
    try:
        original=P.A.load_frozen_report()
        source,target,qc=P.get_locked_geometries(args.archive_root,original)
        f22,_=P.A.load_source_features(args.archive_root,"2022",
                 original["modern_source"]["2022"]["raw_geojson_canonical_sha256"],2303)
        groups=annotate_patches(f22,target)
        frozen=json.loads((ROOT/"results/charlotte_map_class_retention_source_verified_20261119.json").read_text(encoding="utf-8"))
        if frozen.get("schema")!="tampa.charlotte_map_class_retention_source_verified_v1" or frozen.get("report",{}).get("source",{}).get("archive_sha256")!=P.A.ARCHIVE_ZIP_DIGEST:
            raise Stop("SOURCE_RETENTION_RELEASE_NOT_VERIFIED")
        data=run(groups,frozen["report"])
        data["original_archive"]={"artifact_id":P.A.ARCHIVE_ID,"run_id":P.A.ARCHIVE_RUN_ID,
            "zip_digest":P.A.ARCHIVE_ZIP_DIGEST}
        data["source_sha256"]={
           "2022":original["modern_source"]["2022"]["raw_geojson_canonical_sha256"],
           "2024":original["modern_source"]["2024"]["raw_geojson_canonical_sha256"]}
        rc=0
    except (Stop,P.A.Stop,ValueError,TypeError,KeyError,FileNotFoundError) as e:
        data={"schema":"tampa.charlotte_patch_size_spatial_support_retention_v1",
              "status":"STOP_ARCHIVE_OR_COMMON_SUPPORT_QC","reason":str(e),
              "source_class_adjusted_effect_estimated":False}
        rc=2
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True))
    return rc

if __name__=="__main__":sys.exit(main())
