#!/usr/bin/env python3
"""External map-comparability preflight for two preselected Florida estuaries.

Both pairs are public SWFWMD Suncoast 2022/2024 FLUCCS photography maps. This
checks *only* source schema and feature counts: no GIS polygon geometries,
no field-transect data, no area/recovery estimates, and no outcome-blind claim.

Preselected sites are geographically distinct from primary Charlotte Harbor:
1) Lemon Bay (one publicly labeled combined estuary map per year)
2) Dona & Roberts Bays (the official service uses Bay vs Bays in its name)
Do not substitute a different estuary if any check fails.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

ROOT="https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/"
CASES={
  "Lemon Bay":{
    "2022":"Seagrass_in_2022_in_Lemon_Bay",
    "2024":"Seagrass_in_2024_in_Lemon_Bay"},
  "Dona and Roberts Bays":{
    "2022":"Seagrass_in_2022_in_Dona_and_Roberts_Bay",
    "2024":"Seagrass_in_2024_in_Dona_and_Roberts_Bays"}
}
CODES=(9113,9116,9121)
LABELS={9113:"patchy_seagrass",9116:"continuous_seagrass",9121:"attached_macroalgae"}
EXPECTED_AREA_FIELD={"2022":"Geodesic","2024":"ACRES"}
UA="Auditable Florida regional algae/seagrass source gate/1.0"
SCHEMA="tampa.florida_cross_estuary_algae_map_preflight_v1"
class SourceStop(Exception):pass

def source_get(url,params):
    req=Request(url+"?"+urlencode(params),headers={"User-Agent":UA,"Accept":"application/json"})
    try:
        with urlopen(req,timeout=45) as resp: body=resp.read(5_000_001)
    except (URLError,HTTPError,TimeoutError,OSError) as e:
        raise SourceStop("PUBLIC_SOURCE_UNREACHABLE:"+type(e).__name__) from e
    if len(body)>5_000_000:raise SourceStop("SOURCE_RESPONSE_OVERSIZE")
    try:obj=json.loads(body)
    except (UnicodeDecodeError,ValueError) as e:raise SourceStop("SOURCE_NOT_JSON") from e
    if not isinstance(obj,dict) or "error" in obj:
        raise SourceStop("SOURCE_SERVICE_ERROR:"+str(obj.get("error",obj))[:220])
    return obj

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def inspect_site(name,services,get=source_get):
    result={}
    for year in ("2022","2024"):
        url=ROOT+services[year]+"/FeatureServer"
        service=get(url,{"f":"json"})
        layers=service.get("layers")
        if not isinstance(layers,list) or len(layers)!=1:
            raise SourceStop(name+":"+year+":MISSING_OR_AMBIGUOUS_LAYER")
        layerid=layers[0].get("id")
        if not isinstance(layerid,int):
            raise SourceStop(name+":"+year+":BAD_LAYER_ID")
        layer_url=url+"/"+str(layerid)
        meta=get(layer_url,{"f":"json"})
        fields={p.get("name"):p.get("type") for p in meta.get("fields",[]) if isinstance(p,dict)}
        area=EXPECTED_AREA_FIELD[year]
        if meta.get("type")!="Feature Layer" or meta.get("geometryType")!="esriGeometryPolygon":
            raise SourceStop(name+":"+year+":NOT_POLYGON")
        if fields.get("FLUCCSCODE") not in ("esriFieldTypeInteger","esriFieldTypeSmallInteger"):
            raise SourceStop(name+":"+year+":UNRESOLVED_CLASS_CODE_TYPE")
        if fields.get("FLUCCSDESC")!="esriFieldTypeString" or fields.get(area)!="esriFieldTypeDouble":
            raise SourceStop(name+":"+year+":CLASS_DESCRIPTION_OR_AREA_MISSING")
        idfield=meta.get("objectIdField")
        if not idfield or fields.get(idfield)!="esriFieldTypeOID":
            raise SourceStop(name+":"+year+":UNVERIFIED_OBJECT_ID")
        e=meta.get("extent") or {}
        sr=e.get("spatialReference") or {}
        if str(sr.get("latestWkid",sr.get("wkid")))!="3857" or not all(
                isinstance(e.get(k),(int,float)) for k in ("xmin","ymin","xmax","ymax")):
            raise SourceStop(name+":"+year+":UNRESOLVED_CRS_OR_EXTENT")
        total=get(layer_url+"/query",{"f":"json","where":"1=1","returnCountOnly":"true"}).get("count")
        if not isinstance(total,int) or total<1:raise SourceStop(name+":"+year+":INVALID_TOTAL_FEATURE_COUNT")
        classcount={}
        for cls in CODES:
            response=get(layer_url+"/query",{"f":"json","where":f"FLUCCSCODE={cls}",
                                             "returnCountOnly":"true"})
            n=response.get("count")
            if not isinstance(n,int) or n<0:
                raise SourceStop(name+":"+year+":INVALID_CLASS_COUNT:"+str(cls))
            classcount[str(cls)]=n
        if sum(classcount.values())!=total:
            raise SourceStop(name+":"+year+":MAPPED_CLASS_SUM_NOT_CLOSED")
        result[year]={
            "source_layer":layer_url,
            "source_area_field":area,
            "source_id_field":idfield,
            "class_counts":classcount,
            "total_feature_count":total,
            "extent_3857":{k:e[k] for k in ("xmin","ymin","xmax","ymax")},
            "layer_metadata_sha256":digest(meta),
            "service_metadata_sha256":digest(service),
            "last_edit_date":(meta.get("editingInfo") or {}).get("lastEditDate"),
            "focal_algae_present_in_map":classcount["9121"]>0,
        }
    a,b=result["2022"]["extent_3857"],result["2024"]["extent_3857"]
    dx=min(a["xmax"],b["xmax"])-max(a["xmin"],b["xmin"])
    dy=min(a["ymax"],b["ymax"])-max(a["ymin"],b["ymin"])
    if dx<=0 or dy<=0:
        raise SourceStop(name+":NO_BOUNDING_EXTENT_INTERSECTION")
    result["extent_intersection_warning"]={
        "overlapping_bounding_rectangles":True,
        "strictly_equal_map_footprints_verified":False,
        "overlap_bbox_area_3857_units2":round(dx*dy,2),
        "not_a_benthic_observation_or_areal_recovery_measure":True,
    }
    return result

def run(get=source_get):
    out={"schema":SCHEMA,
        "status":"PASS_SOURCE_METADATA_AND_CATEGORY_COUNTS_ONLY",
        "source_family":"SWFWMD public ArcGIS Suncoast biennial mapped benthic vegetation",
        "two_preselected_map_regions":list(CASES),
        "classes":{str(k):v for k,v in LABELS.items()},
        "data_are_outcome_context_exposed":True,
        "not_untouched_external_confirmatory_validation":True,
        "polygon_geometry_downloaded":False,
        "areal_overlap_computed":False,
        "regional_recovery_cause_estimated":False,
        "map_regions_are_not_independent_studies":True,
        "locations":{}}
    for name,pair in CASES.items():
        out["locations"][name]=inspect_site(name,pair,get)
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    try: obj=run();exit_code=0
    except (SourceStop,KeyError,ValueError,TypeError) as e:
        obj={"schema":SCHEMA,"status":"STOP_SOURCE_SCHEMA_OR_CLASS_GATE",
             "reason":str(e),"areal_overlap_computed":False,
             "no_algae_recovery_effect_estimated":True}
        exit_code=2
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False))
    return exit_code

if __name__=="__main__":sys.exit(main())
