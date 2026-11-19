#!/usr/bin/env python3
"""Audit public Charlotte Harbor 2022/2024 ArcGIS seagrass+attached algae layers.

Fetches metadata and aggregate *feature counts*, not polygon coordinates or
biological field-transect data. Counts are not acreage, change, or recovery.
Never uses 2025 East Wall algae to predict a 2024 seagrass outcome.
"""
import argparse
import hashlib
import json
import sys
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from pathlib import Path

HOST="https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services"
SOURCES={
    "2022": f"{HOST}/Seagrass_in_2022_in_Charlotte_Harbor/FeatureServer/1",
    "2024": f"{HOST}/Seagrass_in_2024_in_Charlotte_Harbor/FeatureServer/1",
}
CODES={9113:"patchy_seagrass",9116:"continuous_seagrass",9121:"attached_macroalgae"}
SCHEMA="tampa.charlotte_arcgis_metadata_preflight_v1"
USER_AGENT="Academic provenance audit for public seagrass map layers/1.0"

class SourceStop(Exception): pass

def arcgis_json(url,params,opener=urlopen):
    suffix=urlencode(params)
    uri=url+"?"+suffix
    req=Request(uri,headers={"User-Agent":USER_AGENT,
                             "Accept":"application/json"})
    try:
        with opener(req, timeout=45) as response:
            body=response.read(8_000_001)
    except (URLError,HTTPError,TimeoutError,OSError) as e:
        raise SourceStop("SOURCE_NETWORK_FAILURE:"+type(e).__name__) from e
    if len(body)>8_000_000:
        raise SourceStop("OVERSIZE_METADATA_OR_COUNT_RESPONSE")
    try: ans=json.loads(body)
    except (UnicodeDecodeError,ValueError) as e:
        raise SourceStop("NON_JSON_RESPONSE") from e
    if not isinstance(ans,dict) or "error" in ans:
        raise SourceStop("ARCGIS_SERVICE_ERROR:"+str(ans.get("error","unexpected shape"))[:250])
    return ans

def inspect_layer(meta):
    if meta.get("type")!="Feature Layer" or meta.get("geometryType")!="esriGeometryPolygon":
        raise SourceStop("NOT_POLYGON_FEATURE_LAYER")
    fields={v.get("name"):v.get("type") for v in meta.get("fields",[])}
    if fields.get("FLUCCSCODE") not in ("esriFieldTypeInteger","esriFieldTypeSmallInteger"):
        raise SourceStop("FLUCCSCODE_NOT_INTEGER")
    if fields.get("FLUCCSDESC")!="esriFieldTypeString":
        raise SourceStop("FLUCCSDESC_NOT_STRING")
    if meta.get("objectIdField") not in fields:
        raise SourceStop("OBJECT_ID_FIELD_MISSING")
    crs=(meta.get("extent") or {}).get("spatialReference") or {}
    if str(crs.get("wkid",crs.get("latestWkid"))) not in ("102100","3857"):
        raise SourceStop("UNEXPECTED_LAYER_CRS")
    if meta.get("maxRecordCount",0)<100:
        raise SourceStop("IMPLAUSIBLE_SERVICE_RECORD_LIMIT")
    return {
        "name":meta.get("name"),
        "oid_field":meta["objectIdField"],
        "extent":meta["extent"],
        "max_record_count":meta["maxRecordCount"],
        "fields":[k for k in ("FLUCCSCODE","FLUCCSDESC") if k in fields],
        "last_edit_date":(meta.get("editingInfo") or {}).get("lastEditDate"),
        "metadata_sha256":hashlib.sha256(json.dumps(meta,sort_keys=True,default=str).encode()).hexdigest(),
    }

def inventory(fetch=arcgis_json):
    report={"schema":SCHEMA,"access_status":"PENDING","date_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
            "source_program":"SWFWMD biennial seagrass photography, Charlotte Harbor public ArcGIS",
            "map_codes":{str(k):v for k,v in CODES.items()},
            "layers":{},
            "raw_transect_workbook_opened":False,
            "published_aggregate_outcome_exposure":True,
            "untouched_predictive_confirmation":False,
            "polygon_geometry_downloaded":False,
            "feature_counts_are_areas":False,
            "no_2025_predictors":True}
    for year,url in SOURCES.items():
        meta=fetch(url,{"f":"json"})
        entry=inspect_layer(meta)
        entry["source_url"]=url
        all_count=fetch(url+"/query",{"f":"json","where":"1=1","returnCountOnly":"true"})
        total=all_count.get("count")
        if not isinstance(total,int) or total<=0:
            raise SourceStop(f"{year}:INVALID_TOTAL_COUNT")
        by_code={}
        for k in sorted(CODES):
            n=fetch(url+"/query",{"f":"json","where":f"FLUCCSCODE={k}",
                                  "returnCountOnly":"true"}).get("count")
            if not isinstance(n,int) or n<0:
                raise SourceStop(f"{year}:BAD_COUNT_FOR_CODE:{k}")
            by_code[str(k)]=n
        if sum(by_code.values())!=total:
            raise SourceStop(f"{year}:OTHER_CLASS_OR_NULL_UNACCOUNTED")
        entry["counts_by_code"]=by_code
        entry["feature_count"]=total
        report["layers"][year]=entry
    # Same region labels and close bounding boxes are evidence of candidate
    # alignment, not proof of spatially identical survey footprint.
    a=report["layers"]["2022"]["extent"];b=report["layers"]["2024"]["extent"]
    for k in ("xmin","ymin","xmax","ymax"):
        if not isinstance(a.get(k),(float,int)) or not isinstance(b.get(k),(float,int)):
            raise SourceStop("EXTENT_COORDINATES_MISSING")
    report["approximate_extent_delta_m_webmercator"]={
        k:round(float(b[k]-a[k]),2) for k in ("xmin","ymin","xmax","ymax")}
    report["access_status"]="PASS_METADATA_AND_COUNTS_ONLY"
    report["next_gate"]="Download source polygons and construct 2022-to-2024 area transition only with explicit geodesic/equal-area unit and topology audit."
    report["ecological_claim"]="NONE: polygon counts do not measure attached-algae cover, seagrass recovery, or competition"
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",required=True)
    args=ap.parse_args(argv)
    try: result=inventory()
    except SourceStop as e:
        result={"schema":SCHEMA,"access_status":"STOP_SOURCE_PREFLIGHT",
                "reason":str(e),"published_aggregate_outcome_exposure":True,
                "no_ecological_result":True}
    p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    return 0 if result["access_status"]=="PASS_METADATA_AND_COUNTS_ONLY" else 2

if __name__=="__main__":
    sys.exit(main())
