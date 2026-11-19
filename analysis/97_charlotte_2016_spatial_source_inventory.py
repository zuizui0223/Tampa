#!/usr/bin/env python3
"""Live source-only feasibility of 2016 historical seagrass vs 2022/24 Charlotte layers.

Does not open feature geometry or compute any three-date ecological transition.
The 2016 SWFWMD legacy map is wider (21k objects) than 2022/24 Charlotte GIS.
Count only how many 2016 category features intersect the spatial envelope of
the 2022/24 maps; do not infer area from counts nor exact common footprint.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

HIST="https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental/MapServer/20"
CURRENT_BASE="https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services"
CURRENT={
"2022":CURRENT_BASE+"/Seagrass_in_2022_in_Charlotte_Harbor/FeatureServer/1",
"2024":CURRENT_BASE+"/Seagrass_in_2024_in_Charlotte_Harbor/FeatureServer/1"
}
HIST_CODES={"9113":"patchy_seagrass","9116":"continuous_seagrass",
            "9121":"attached_macroalgae"}
BACKGROUND_CODES=("6510","6540","7210","0","5400")
USER_AGENT="Charlotte Harbor historical GIS schema and selection audit/1.0"
class GateStop(Exception):pass

def request(url,params):
    req=Request(url+"?"+urlencode(params),headers={"User-Agent":USER_AGENT,
                                             "Accept":"application/json"})
    try:
        with urlopen(req,timeout=60) as r: raw=r.read(4_000_001)
    except (URLError,HTTPError,OSError,TimeoutError) as e:
        raise GateStop("SOURCE_UNREACHABLE:"+type(e).__name__) from e
    if len(raw)>4_000_000:raise GateStop("OVERSIZE_RESPONSE")
    try:res=json.loads(raw)
    except (ValueError,UnicodeDecodeError) as e:raise GateStop("SOURCE_NON_JSON") from e
    if not isinstance(res,dict) or res.get("error"):
        stage=("LEGACY_DISTINCT" if params.get("returnDistinctValues") else
               "LEGACY_SPATIAL_COUNT" if params.get("returnCountOnly") and "geometry" in params else
               "LEGACY_WHOLE_COUNT" if params.get("returnCountOnly") else
               "METADATA")
        where=str(params.get("where",""))[:80]
        raise GateStop("ARCGIS_SOURCE_ERROR_STAGE_"+stage+":where="+where+":"+str(res.get("error",res))[:300])
    return res

def checksum(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def spatial_counts(req=request):
    m16=req(HIST,{"f":"json"})
    fields={f.get("name"):f.get("type") for f in m16.get("fields",[])}
    if m16.get("geometryType")!="esriGeometryPolygon" or fields.get("FLUCCS_CODE")!="esriFieldTypeString" or fields.get("ACRES")!="esriFieldTypeDouble":
        raise GateStop("LEGACY_SCHEMA_UNEXPECTED")
    sr=(m16.get("extent") or {}).get("spatialReference") or {}
    if sr.get("wkid")!=2882:raise GateStop("LEGACY_CRS_UNEXPECTED")
    sources={}
    for yr,url in CURRENT.items():
        meta=req(url,{"f":"json"})
        if meta.get("geometryType")!="esriGeometryPolygon" or meta.get("objectIdField")!="FID":
            raise GateStop("MODERN_SCHEMA_UNEXPECTED:"+yr)
        e=meta.get("extent") or {}
        if (e.get("spatialReference") or {}).get("latestWkid")!=3857:
            raise GateStop("MODERN_CRS_UNEXPECTED:"+yr)
        if not all(isinstance(e.get(k),(int,float)) for k in ("xmin","ymin","xmax","ymax")):
            raise GateStop("MODERN_EXTENT_UNAVAILABLE:"+yr)
        sources[yr]={"url":url,"extent":{k:e[k] for k in ("xmin","ymin","xmax","ymax")},
                     "source_metadata_sha256":checksum(meta)}
    # Cover *both* footprint envelopes and allow no geometry-driven post-hoc choices.
    bbox={k:(min(sources[y]["extent"][k] for y in sources) if k in ("xmin","ymin")
             else max(sources[y]["extent"][k] for y in sources)) for k in ("xmin","ymin","xmax","ymax")}
    geometry=",".join(str(bbox[k]) for k in ("xmin","ymin","xmax","ymax"))
    base={"geometry":geometry,"geometryType":"esriGeometryEnvelope",
          "inSR":3857,"spatialRel":"esriSpatialRelIntersects","f":"json"}
    all_count=req(HIST+"/query",{**base,"where":"1=1","returnCountOnly":"true"}).get("count")
    if not isinstance(all_count,int) or all_count<1:raise GateStop("SPATIAL_TOTAL_COUNT_INVALID")
    whole_count=req(HIST+"/query",{"f":"json","where":"1=1","returnCountOnly":"true"}).get("count")
    if not isinstance(whole_count,int) or whole_count<all_count:
        raise GateStop("WHOLE_LAYER_COUNT_INVALID")
    per={}
    for code in tuple(HIST_CODES)+BACKGROUND_CODES:
        q={**base,"where":"FLUCCS_CODE='"+code+"'","returnCountOnly":"true"}
        n=req(HIST+"/query",q).get("count")
        if not isinstance(n,int) or n<0:raise GateStop("BAD_CODE_COUNT:"+code)
        per[code]=n
    unknown=all_count-sum(per.values())
    if unknown<0:raise GateStop("COUNTS_EXCEED_TOTAL")
    # The legacy MapServer rejects spatially filtered returnDistinctValues
    # (HTTP 400), despite advertising distinct support. Do NOT weaken class
    # coverage: accept only if all intersecting polygons are exhaustively
    # accounted for by independently checked official 2016 legend classes.
    # A positive count of any unspecified class remains a terminal STOP.
    if unknown != 0:
        raise GateStop("UNKNOWN_CLASS_COUNT_IN_2016_ENVELOPE:"+str(unknown))
    verified_codes=[code for code,num in per.items() if num>0]
    return {
      "schema":"tampa.charlotte_2016_spatial_source_inventory_v1",
      "status":"PASS_METADATA_SPATIAL_COUNTS_ONLY",
      "historical_url":HIST,
      "historical_metadata_sha256":checksum(m16),
      "whole_district_2016_polygon_count":whole_count,
      "spatial_filter_envelope_3857":bbox,
      "spatial_envelope_source_layers":sources,
      "2016_envelope_intersecting_polygon_count":all_count,
      "2016_envelope_counts_by_code":per,
      "2016_envelope_unmatched_code_count":unknown,
      "2016_envelope_documented_codes_with_positive_counts":verified_codes,
      "original_mapping_class_dictionary_reference":"https://manatee.wateratlas.usf.edu/upload/documents/TBEP_03_17_Hard_Bottom.pdf",
      "2016_explicit_land_code":"0",
      "2016_explicit_open_water_code":"5400",
      "land_or_mapped_open_water_does_not_prove_seagrass_demographic_absence":True,
      "spatial_distinct_query_status":"UNSUPPORTED_BY_LEGACY_SERVER; six official 2016 mapped classes verified by exhaustive category-count closure",
      "strictly_seagrass_only_historical_codes":["9113","9116"],
      "attached_macroalgae_code":"9121",
      "source_feature_geometries_downloaded":False,
      "source_class_areas_calculated":False,
      "2016_to_2022_2024_overlap_computed":False,
      "observation_scope_warning":"Bounding envelope does not equal exact common mappable footprint and may include non-Charlotte bay fragments; use source polygons and footprint crosswalk before biological recovery claims.",
      "prior_published_outcome_context_exposed":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    try:
        data=spatial_counts();rc=0
    except (GateStop,ValueError,TypeError) as e:
        data={"schema":"tampa.charlotte_2016_spatial_source_inventory_v1",
              "status":"STOP_HISTORICAL_SOURCE_INVENTORY","reason":str(e),
              "2016_to_2022_2024_overlap_computed":False};rc=2
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(data,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":sys.exit(main())
