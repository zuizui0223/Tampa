#!/usr/bin/env python3
"""Official SWFWMD 2018/2020 original OID and acreage-source eligibility.

Use ONLY the prevalidated 2018/2020 dated layer identities and exact original
2016/22/24 Charlotte envelope. Distinguish:
 - map metadata source (already authenticated),
 - exact unique polygon OID roster (new check),
 - independent original source-acre attribute (may be absent),
 - original polygon geometry and habitat classification (NOT downloaded here).

DO NOT calculate areas by counting polygons, impute seagrass absent where a
code is not mapped, or switch endpoints after looking at outcome values.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("old110",ROOT/"analysis/110_charlotte_2018_2020_legacy_map_preflight.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
RELEASE=ROOT/"results/charlotte_2018_2020_legacy_source_counts_verified_20261119.json"
SCHEMA="tampa.charlotte_2018_2020_historical_unique_geometry_eligibility_v1"
AREA_FIELDS=("ACRES","Geodesic","Area_Acres","AREA_ACRES","SHAPE_Area","Shape__Area")
ID_PREFIX="FLUCCSCODE"
class Stop(ValueError):pass

def sha(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def released_source():
    x=json.loads(RELEASE.read_text(encoding="utf8"))
    if not x.get("verified_ci",{}).get("run_id")==44512363799:
        raise Stop("UNVERIFIED_2018_2020_ORIGINAL_CLASS_GATE")
    r=x["report"]
    if r.get("status")!="PASS_OFFICIAL_LEGACY_MAP_METADATA_AND_CLASS_COUNTS_ONLY":
        raise Stop("NO_VERIFIED_ORIGINAL_MAP_CLASS_COUNTS")
    return r

def audit(query=M.request,source=released_source):
    src=source()
    fixed=src["years"]
    bbox=src["years"]["2018"]["map_extent_2016_2024_reference_envelope_3857"]
    bboxstr=",".join(str(bbox[k]) for k in ("xmin","ymin","xmax","ymax"))
    envelope={"geometry":bboxstr,"geometryType":"esriGeometryEnvelope",
              "inSR":3857,"spatialRel":"esriSpatialRelIntersects","f":"json"}
    out={}
    for year,layerid in M.LAYERS.items():
        layer=M.SOURCE_BASE+"/"+str(layerid)
        meta=query(layer,{"f":"json"})
        if sha(meta)!=fixed[year]["metadata_sha256"]:
            raise Stop("HISTORIC_MAP_LAYER_SHA_DRIFT:"+year)
        fields={f.get("name"):f.get("type") for f in meta.get("fields",[]) if isinstance(f,dict)}
        candidates=[k for k,v in fields.items() if v=="esriFieldTypeOID"]
        if len(candidates)!=1:
            raise Stop("LEGACY_MAP_NOT_UNIQUE_TYPED_OID_FIELD:"+year+":"+str(candidates))
        oid=candidates[0]
        count=src["years"][year]["n_legacy_source_features_intersecting_envelope"]
        q=query(layer+"/query",{**envelope,"where":"1=1","returnIdsOnly":"true"})
        ids=q.get("objectIds")
        if not isinstance(ids,list) or len(ids)!=count or len(set(ids))!=count:
            raise Stop("LEGACY_ORIGINAL_ID_SET_INCOMPLETE:"+year)
        if q.get("objectIdFieldName") not in (oid,None):
            raise Stop("LEGACY_ARCGIS_ADVERTISED_ID_CONFLICT:"+year)
        if not all(isinstance(i,int) for i in ids):
            raise Stop("LEGACY_MAP_NONTINTEGER_SOURCE_OID:"+year)
        class_roster={}
        for code in (9113,9116,9121):
            where="FLUCCSCODE="+str(code)
            response=query(layer+"/query",{**envelope,"where":where,"returnIdsOnly":"true"})
            r=response.get("objectIds")
            expected=fixed[year]["n_by_focal_legacy_flucss_code"][str(code)]
            # ArcGIS MapServer commonly emits null rather than [] for an
            # empty ID set. Normalize ONLY for an independently verified
            # zero-count class and never invent missing positive responses.
            if expected==0 and r is None:r=[]
            if not isinstance(r,list) or len(r)!=expected or len(set(r))!=len(r):
                raise Stop("LEGACY_CLASS_EXACT_SOURCE_ID_COUNT_DRIFT:"+year+":"+str(code))
            if set(r)-set(ids):
                raise Stop("LEGACY_CLASS_ID_OUTSIDE_FULL_INVENTORY:"+year+":"+str(code))
            class_roster[str(code)]={"count":len(r),"OID_set_sha256":sha(sorted(r))}
        area=[{"field":field,"declared_type":fields[field]}
              for field in AREA_FIELDS if field in fields]
        out[year]={
          "source_url":layer,"layer_metadata_sha256":sha(meta),
          "oid_field_verified_by_single_typed_esri_oid":oid,
          "returnIdsOnly_objectIdFieldName":q.get("objectIdFieldName"),
          "bbox_all_oid_count":len(ids),
          "bbox_all_source_oid_sha256":sha(sorted(ids)),
          "focal_class_id_audits":class_roster,
          "official_original_area_attributes":area,
          "strict_original_source_acreage_crosscheck_possible":any(
              v["declared_type"]=="esriFieldTypeDouble" for v in area),
          "no_polygon_geometries_downloaded":True,
          "future_polygon_geometry_and_area_transition_fitted":False
        }
    return {
      "schema":SCHEMA,"status":"PASS_HISTORICAL_GIS_EXACT_SOURCE_ID_INVENTORIES_ONLY",
      "years":out,
      "2018_and_2020_polygon_areas_computed":False,
      "independent_source_acre_validation_may_be_unavailable":True,
      "do_not_use_polygon_counts_as_area_or_biomass":True,
      "not_a_causal_or_field_biological_result":True,
      "interpretation":"Exact official 2018/2020 OID rosters confirm whether original geometries could in principle be opened, but do not prove source mapping coverage, original-acre attributes, true attached algae absence or reproducible area transitions."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    window=M.official_service_window()
    if not window["portal_open_time"]:
        obj={"schema":SCHEMA,"status":"SKIP_OUTSIDE_DISTRICT_GIS_OPEN_HOURS",
             "access_window":window,"no_historical_areas_estimated":True}
        rc=0
    else:
        try:obj=audit();obj["access_window"]=window;rc=0
        except (Stop,M.Stop,ValueError,TypeError,KeyError) as e:
            obj={"schema":SCHEMA,"status":"STOP_EXACT_HISTORICAL_OID_SOURCE_AUDIT",
                 "reason":str(e),"access_window":window,
                 "no_historical_areas_estimated":True};rc=2
    q=Path(a.out);q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(obj,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":sys.exit(main())
