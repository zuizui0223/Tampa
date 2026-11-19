#!/usr/bin/env python3
"""2024 legacy SWFWMD ALL map-class overlay of giant 2022 attached-algae polygons.

This uses the separate original district-wide Environmental_Seagrass2018_sql
MapServer/3, which source-count metadata shows has nine FLUCCSCODE values
including 0,5400,6510,6540,7210,9122 in addition to 9113/9116/9121.

Classify 2024 *map* omissions inside original 2022 algae FIDs 37/2166:
  (A) another original district 2024 code physically covers the region
  (B) original district 2024 9113/9116/9121 covers it despite hosted omission
  (C) no original district code covers it in the fetched original source

No region becomes proven bare bottom, 2024 seagrass death, or new habitat.
Exact old target-source 2016/2022/2024 SHA pinned, source 2024 district
metadata/counts SHA pinned. Original district 2024 MapServer only online
during a published 6am-10pm America/New_York GIS portal window.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,sys
from pathlib import Path
from collections import defaultdict

from shapely.geometry import shape,mapping
from shapely.ops import transform,unary_union
from shapely.validation import make_valid
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location(
    "giant118",ROOT/"analysis/118_charlotte_giant_unmapped_core_depth.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
G=M.G
YEAR=importlib.util.spec_from_file_location(
    "district125",ROOT/"analysis/125_charlotte_2024_district_original_full_class_preflight.py")
D=importlib.util.module_from_spec(YEAR);YEAR.loader.exec_module(D)
PREFLIGHT=ROOT/"results/charlotte_2024_original_district_full_class_counts_verified_20261119.json"
ORIGINAL=ROOT/"results/charlotte_giant_unmapped_interior_source_verified_20261119.json"
CODES=(0,5400,6510,6540,7210,9113,9116,9121,9122)
RESTRICTED=(9113,9116,9121)
BACKGROUND=(0,5400,6510,6540,7210,9122)
SOURCE_OID="OBJECTID"
MAX_OIDS=4000
BATCH=60
AREA=G.M2_PER_ACRE
UTM_MERC=Transformer.from_crs("EPSG:6933","EPSG:3857",always_xy=True).transform
BACK_TO_WGS84=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True).transform
SCHEMA="tampa.charlotte_giant_2024_original_all_map_class_overlay_v1"
class Stop(ValueError):pass

def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def read_source_release():
    obj=json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if obj.get("verified_ci",{}).get("run_id")!=44516615481:
        raise Stop("UNVERIFIED_2024_DISTRICT_SOURCE_RUN")
    p=obj.get("report",{})
    if p.get("status")!="PASS_OFFICIAL_2024_ORIGINAL_DISTRICT_YEAR_CODE_DICTIONARY_ONLY":
        raise Stop("UNVERIFIED_2024_DISTRICT_SOURCE_CLASS_DICTIONARY")
    if p.get("source")!=D.LAYER or p.get("n_source_polygons_of_other_classes")!=3276:
        raise Stop("2024_DISTRICT_LAYER_ID_OR_SOURCE_CLASS_COUNTS_CHANGED")
    if set(p["exhaustive_original_source_code_counts"])!={str(x) for x in CODES}:
        raise Stop("2024_DISTRICT_SOURCE_CLASS_SET_DIFFERENT")
    original=json.loads(ORIGINAL.read_text(encoding="utf-8"))
    if original.get("verified_ci",{}).get("run_id")!=44509444813:
        raise Stop("UNVERIFIED_2022_GIANT_SOURCE")
    return p,original

def _geometry_query(q,bbox,where="1=1",request_ids=False):
    return q(D.LAYER+"/query",{
       "f":"json","geometry":",".join(str(v) for v in bbox),
       "geometryType":"esriGeometryEnvelope","inSR":3857,
       "spatialRel":"esriSpatialRelIntersects","where":where,
       "returnIdsOnly":"true" if request_ids else "false",
       **({"returnCountOnly":"true"} if not request_ids else {})})

def source_ids_by_bbox(g2022,q=G.query):
    if not g2022.is_valid or g2022.is_empty:raise Stop("UNVERIFIED_2022_GIANT_GEOMETRY")
    bbox=transform(UTM_MERC,g2022).bounds
    res=_geometry_query(q,bbox,request_ids=True)
    ids=res.get("objectIds")
    if ids is None:ids=[]
    if not isinstance(ids,list) or len(ids)!=len(set(ids)) or len(ids)>MAX_OIDS:
        raise Stop("2024_DISTRICT_GIANT_BBOX_ID_ROSTER_INVALID")
    if res.get("objectIdFieldName") not in (None,SOURCE_OID):
        raise Stop("2024_DISTRICT_GIANT_BBOX_OID_FIELD_CONFLICT")
    if not all(type(x) is int for x in ids):
        raise Stop("SOURCE_DISTRICT_HAS_NON_INTEGER_IDS")
    n=_geometry_query(q,bbox,request_ids=False).get("count")
    if n!=len(ids):raise Stop("2024_DISTRICT_GIANT_BBOX_COUNT_ID_MISMATCH")
    return sorted(ids),bbox

def fetch_original_features(ids,q=G.query):
    features=[]
    if len(ids)>MAX_OIDS:raise Stop("UNREASONABLE_ORIGINAL_GIS_SOURCE_ROSTER")
    for k in range(0,len(ids),BATCH):
        part=ids[k:k+BATCH]
        res=q(D.LAYER+"/query",{
            "f":"geojson","objectIds":",".join(str(i) for i in part),
            "returnGeometry":"true","outSR":4326,
            "outFields":"OBJECTID,FLUCCSCODE,FLUCCSDESC"})
        fs=res.get("features")
        if res.get("type")!="FeatureCollection" or not isinstance(fs,list):
            raise Stop("2024_DISTRICT_GEOJSON_UNSUPPORTED_OR_TRUNCATED")
        seen=[x.get("properties",{}).get(SOURCE_OID) for x in fs]
        if len(fs)!=len(part) or len(set(seen))!=len(fs) or set(seen)!=set(part):
            raise Stop("2024_DISTRICT_GEOJSON_SOURCE_ID_MISMATCH")
        features.extend(fs)
    return sorted(features,key=lambda x:x.get("properties",{}).get(SOURCE_OID))

def mapped_shapes(features):
    out={code:[] for code in CODES}
    repaired=0
    for f in features:
        props=f.get("properties") or {}
        raw=props.get("FLUCCSCODE")
        if isinstance(raw,(int,float)) and math.isfinite(raw) and raw==int(raw):
            code=int(raw)
        else:raise Stop("2024_GIS_UNRECOGNIZED_OR_NULL_FLUCCS_CODE:"+repr(raw))
        if code not in out:raise Stop("2024_GIS_NEW_CODE_NOT_IN_COUNTED_DICTIONARY:"+str(code))
        g=shape(f.get("geometry"))
        if g.geom_type not in ("Polygon","MultiPolygon") or g.is_empty:
            raise Stop("INVALID_ORIGINAL_2024_POLYGON_TYPE")
        if not g.is_valid:
            repaired+=1
            g=unary_union(G.polygon_parts(make_valid(g)))
        if not g.is_valid or g.is_empty:raise Stop("UNREPAIRABLE_ORIGINAL_2024_GIS_POLYGON")
        projected=transform(G.TRANSFORM,g)
        if not projected.is_valid or projected.is_empty:
            raise Stop("INVALID_PROJECTED_ORIGINAL_2024_POLYGON")
        out[code].append(projected)
    return {code:unary_union(v) for code,v in out.items()},repaired

def independent_source_overlap(giant,target,shapes):
    unknown=giant.difference(target)
    if unknown.area<=0:raise Stop("NO_2024_UNKNOWN_REGION")
    checked={}
    clipped=[]
    for code in CODES:
        other=shapes[code].intersection(unknown)
        other_area=other.area/AREA
        clipped.append(other)
        checked[str(code)]=round(other_area,6)
    covered=unary_union(clipped).area/AREA
    overlap_excess=max(0.0,sum(checked.values())-covered)
    uncovered=max(0,unknown.area/AREA-covered)
    return {
      "unknown_2024_3class_area_acres":round(unknown.area/AREA,6),
      "source_2024_original_code_overlaps_unknown_acres":checked,
      "source_2024_original_non_three_code_coverage_acres":round(
          unary_union([clipped[CODES.index(code)] for code in BACKGROUND]).area/AREA,6),
      "source_2024_original_three_code_coverage_acres":round(
          unary_union([clipped[CODES.index(code)] for code in RESTRICTED]).area/AREA,6),
      "source_2024_original_all_class_coverage_acres":round(covered,6),
      "no_2024_original_class_map_polygon_overlapping_acres":round(uncovered,6),
      "possible_double_class_overlap_acres":round(overlap_excess,6),
      "not_bare_substrate_or_biological_absence":True
    }

def strictly_inside_source_sand(g,hosted_three,sand2024,history,dists=(0,25,50)):
    """Erode source 2022 algae / 2024 7210 sand / hosted-unknown union together.

    A 25m core is at least 25m inside *all three* category boundaries,
    not simply 25m inside a legacy source patch. All stages are map labels.
    """
    if tuple(dists)!=(0,25,50):raise Stop("SAND_CORE_DISTANCE_CHANGED")
    overlap=g.difference(hosted_three).intersection(sand2024)
    if overlap.is_empty or not overlap.is_valid:raise Stop("INVALID_7210_SAND_SOURCE_OVERLAP")
    area0=overlap.area/AREA
    if area0<=0:raise Stop("MISSING_2024_CODE_7210_SAND_IN_TARGET")
    report={};features=[]
    previous=area0+.01
    for dist in dists:
        core=overlap if dist==0 else overlap.buffer(-dist)
        if not core.is_valid:raise Stop("INVALID_ERODED_2024_SAND_GEOMETRY")
        acres=core.area/AREA
        if acres>previous+.002:raise Stop("SAND_INTERIOR_INCREASES_WITH_EROSION")
        his=core.intersection(history).area/AREA
        if his>acres+.001:raise Stop("HISTORIC_SEA_OVERLAP_EXCEEDS_SAND")
        report[str(dist)]={
           "mapped_sand_7210_interior_acres":round(acres,5),
           "share_original_7210_mapped_area_percent":round(100*acres/area0,4),
           "inside_2016_mapped_seagrass_positive_acres":round(his,5),
           "inside_2016_mapped_seagrass_positive_percent":round(100*his/acres,4) if acres>0 else None,
        }
        previous=acres
        if dist in (25,50):
            for poly in G.polygon_parts(core):
                a=poly.area/AREA
                if a<.25:continue
                mid=poly.representative_point()
                lon,lat=BACK_TO_WGS84(mid.x,mid.y)
                if not(-83.5<lon<-81.0 and 25<lat<28):
                    raise Stop("SOURCE_SAND_CORE_OUTSIDE_EXPECTED_REGION")
                features.append({
                    "type":"Feature",
                    "properties":{
                       "code_2024":7210,
                       "official_2024_class":"SWFWMD mapped submerged sand (7210)",
                       "distance_inside_original2022_algae_and_2024_sand_and_outside_hosted_2024_classes_m":dist,
                       "mapped_core_acres":round(a,5),
                       "2016_source_mapped_seagrass_positive_intersection_acres":round(poly.intersection(history).area/AREA,5),
                       "representative_lat":round(lat,7),
                       "representative_lon":round(lon,7),
                       "not_an_approved_field_site":True,
                       "not_plant_mortality_or_vegetation_absence_measure":True},
                    "geometry":mapping(transform(BACK_TO_WGS84,poly))
                })
    return report,features

def run(archive_root,query=G.query):
    prior,old=read_source_release()
    meta=query(D.LAYER,{"f":"json"})
    if D.sha(meta)!=prior["source_metadata_sha256"]:
        raise Stop("ORIGINAL_2024_SOURCE_METADATA_CHANGED")
    giants,target,hist,existing,frozen,qcs,qc16=M.load_sources(archive_root)
    rows={}; all_ids=set(); per_ids={}; sand_cores={}; all_core_features=[]
    for fid in (37,2166):
        ids,bbox=source_ids_by_bbox(giants[fid],query)
        per_ids[str(fid)]={"count_bbox":len(ids),"bbox_source_ids_sha256":sha(ids)}
        all_ids.update(ids)
    if len(all_ids)>MAX_OIDS:raise Stop("TOO_MANY_2024_GIS_IDS")
    features=fetch_original_features(sorted(all_ids),query)
    shapes,repaired=mapped_shapes(features)
    for fid in (37,2166):
        rows[str(fid)]=independent_source_overlap(giants[fid],target,shapes)
        source_row=next((x for x in existing["report"]["two_largest_source_algae_patches"]
            if x["source_2022_FID"]==fid),None)
        if source_row is None:raise Stop("PINNED_SOURCE_GIANT_FID_MISSING:"+str(fid))
        oldarea=source_row["2024_unmapped_area_acres"]
        if abs(rows[str(fid)]["unknown_2024_3class_area_acres"]-oldarea)>.01:
            raise Stop("ORIGINAL_GIANT_2024_UNKNOWN_SOURCE_ACREAGE_DRIFT")
        depth,feats=strictly_inside_source_sand(giants[fid],target,shapes[7210],hist)
        if abs(depth["0"]["mapped_sand_7210_interior_acres"]-
               rows[str(fid)]["source_2024_original_code_overlaps_unknown_acres"]["7210"])>.003:
            raise Stop("SOURCE_SAND_GIS_CORE_DOES_NOT_CLOSE_TO_ORIGINAL_SOURCE_AREA")
        sand_cores[str(fid)]=depth
        for feat in feats:
            feat["properties"]["source_2022_attached_algae_FID"]=fid
            all_core_features.append(feat)
    summary={k:round(sum(rows[str(fid)][k] for fid in (37,2166)),6)
             for k in ("unknown_2024_3class_area_acres",
              "source_2024_original_non_three_code_coverage_acres",
              "source_2024_original_three_code_coverage_acres",
              "source_2024_original_all_class_coverage_acres",
              "no_2024_original_class_map_polygon_overlapping_acres",
              "possible_double_class_overlap_acres")}
    raw_descriptions={str(code):sorted({str(f.get("properties",{}).get("FLUCCSDESC") or "").strip()[:200]
        for f in features if f.get("properties",{}).get("FLUCCSCODE")==code}) for code in CODES}
    sand_sum={str(d):round(sum(sand_cores[str(fid)][str(d)]["mapped_sand_7210_interior_acres"]
                    for fid in (37,2166)),5) for d in (0,25,50)}
    return {
      "schema":SCHEMA,
      "source_2024_actual_raw_class_descriptions":raw_descriptions,
      "sand_7210_three_map_boundary_interior_by_original_giant_FID":sand_cores,
      "sand_7210_combined_interior_acres":sand_sum,
      "field_verification_geojson_candidate_count":len(all_core_features),
      "_source_verified_sand_candidate_geojson":{"type":"FeatureCollection","features":all_core_features},
      "status":"SOURCE_GATED_ORIGINAL_2024_ALL_CODE_POLYGON_INTERSECTION_DESCRIPTIVE",
      "original_2024_district_layer":D.LAYER,
      "source_2024_metadata_sha256":prior["source_metadata_sha256"],
      "source_years":[2022,2024],
      "background_code_semantics_require_original_key":True,
      "per_giant_2022_attached_algae_source_FID":rows,
      "combined_two_giant_area_summaries":summary,
      "fetched_2024_district_source_feature_count":len(features),
      "fetched_2024_district_source_ids_sha256":sha(sorted(all_ids)),
      "source_geojson_canonical_sha256":G.sha(features),
      "original_polygon_repairs":repaired,
      "bbox_original_2024_source_rosters":per_ids,
      "data_classification_limits":[
        "Unknown means absent from hosted 2024 three category polygons, not absent from all original 2024 district categories.",
        "Original district 2024 classes 0,5400,6510,6540,7210,9122 are raw codes; meanings and imagery footprint need official key and QA before habitat narrative.",
        "Original district 2024 MapServer has Shape.STArea() but no verified original ACRES field; source geometry and hosted overlap are descriptive, not independent field accuracy.",
        "Area across different code unions can overlap. Never force counts to be exclusive unless area-overlap is independently negligible.",
        "No confirmed seagrass mortality, algae disappearance, colonization or conservation intervention effect."
      ]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--geojson-out")
    a=p.parse_args()
    clock=D.M.official_service_window()
    if not clock["portal_open_time"]:
        report={"schema":SCHEMA,"status":"SKIP_OUTSIDE_DISTRICT_OPEN_HOURS",
                "access_window":clock,"no_benthic_class_fate_inferred":True};rc=0
    else:
        try:report=run(a.archive_root);report["access_window"]=clock;rc=0
        except (Stop,G.GateStop,ValueError,TypeError,KeyError,OSError,RuntimeError) as e:
            report={"schema":SCHEMA,"status":"STOP_ORIGINAL_DISTRICT_GEOMETRY_SOURCE_AUDIT",
                    "reason":str(e),"no_benthic_class_fate_inferred":True,
                    "access_window":clock};rc=2
    geojson=report.pop("_source_verified_sand_candidate_geojson",{"type":"FeatureCollection","features":[]})
    output=Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if a.geojson_out:
        outfile=Path(a.geojson_out);outfile.parent.mkdir(parents=True,exist_ok=True)
        outfile.write_text(json.dumps(geojson,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":sys.exit(main())
