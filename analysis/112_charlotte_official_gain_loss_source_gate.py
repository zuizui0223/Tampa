#!/usr/bin/env python3
"""Official CHNEP/SWFWMD 2022-2024 mapped seagrass gain/loss layer preflight.

Source-only: do not download polygon geometry or claim independent field
confirmation. Same mapping family can reuse the exact original source map
and photo interpretation; gain and loss polygons are NOT biological changes
or a separate independent ecological experiment.

A source definition must establish what these layer classes and included
regions mean BEFORE intersecting them with 2022 algae FIDs 37 and 2166.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

URL_ROOT="https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/"
SERVICES={
  "mapped_seagrass_gain":"Seagrass_Gain_in_Charlotte_Harbor_between_2022_and_2024",
  "mapped_seagrass_loss":"Seagrass_Loss_in_Charlotte_Harbor_between_2022_and_2024"
}
GATES=("2022","2024")
SCHEMA="tampa.charlotte_official_seagrass_change_map_metadata_preflight_v1"
USER_AGENT="Source verification of official Charlotte 2022-2024 GIS map change layers/1.0"
class Stop(Exception):pass

def request(url,params):
    full=url+"?"+urlencode(params)
    try:
        with urlopen(Request(full,headers={"User-Agent":USER_AGENT,"Accept":"application/json"}),timeout=60) as s:
            raw=s.read(6_000_001)
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise Stop("SOURCE_NETWORK_STOP:"+type(e).__name__) from e
    if len(raw)>6_000_000:raise Stop("SOURCE_RESPONSE_TOO_LARGE")
    try:res=json.loads(raw)
    except (ValueError,UnicodeDecodeError) as e:raise Stop("NON_JSON_SOURCE") from e
    if not isinstance(res,dict) or "error" in res:
        raise Stop("SOURCE_RETURNED_SERVICE_ERROR:"+str(res.get("error",res))[:250])
    return res

def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def inspect(fetch=request):
    result={}
    for role,name in SERVICES.items():
        base=URL_ROOT+name+"/FeatureServer"
        server=fetch(base,{"f":"json"})
        layers=server.get("layers")
        if not isinstance(layers,list) or len(layers)!=1 or not isinstance(layers[0].get("id"),int):
            raise Stop("MISSING_OR_MULTIPLE_MAP_CHANGE_LAYERS:"+role)
        lid=layers[0]["id"];url=base+"/"+str(lid)
        meta=fetch(url,{"f":"json"})
        if meta.get("type")!="Feature Layer" or meta.get("geometryType")!="esriGeometryPolygon":
            raise Stop("MAP_CHANGE_LAYER_NOT_POLYGON:"+role)
        # Do not infer class codes: return the actual official field dictionary.
        fields={f.get("name"):f.get("type") for f in meta.get("fields",[]) if isinstance(f,dict)}
        oid=meta.get("objectIdField")
        if not isinstance(oid,str) or fields.get(oid)!="esriFieldTypeOID":
            raise Stop("MAP_CHANGE_MISSING_OBJECTID:"+role)
        extent=(meta.get("extent") or {})
        sr=extent.get("spatialReference") or {}
        if str(sr.get("latestWkid",sr.get("wkid"))) not in ("3857","2882"):
            raise Stop("MAP_CHANGE_UNEXPECTED_SOURCE_CRS:"+role+":"+repr(sr))
        if not all(isinstance(extent.get(k),(int,float)) for k in ("xmin","ymin","xmax","ymax")):
            raise Stop("MAP_CHANGE_MISSING_BOUNDS:"+role)
        n=fetch(url+"/query",{"f":"json","where":"1=1","returnCountOnly":"true"}).get("count")
        if not isinstance(n,int) or n<=0:
            raise Stop("MAP_CHANGE_EMPTY_OR_INACCESSIBLE_SOURCE:"+role)
        counts={}
        for code in (9113,9116,9121):
            k=fetch(url+"/query",{"f":"json","where":"FLUCCSCODE="+str(code),
                                      "returnCountOnly":"true"}).get("count")
            if not isinstance(k,int) or k<0:
                raise Stop("MAP_CHANGE_SOURCE_CODE_COUNT_FAILED:"+role+":"+str(code))
            counts[str(code)]=k
        unknown=n-sum(counts.values())
        if unknown<0:
            raise Stop("MAP_CHANGE_CLASSES_GREATER_THAN_SOURCE_TOTAL:"+role)
        result[role]={
            "service_url":base,"layer_url":url,"layer_id":lid,
            "source_name":meta.get("name"),
            "service_description":str(server.get("serviceDescription") or "")[:2200],
            "layer_description":str(meta.get("description") or "")[:2000],
            "source_field_types":fields,
            "oid_field":oid,
            "source_extent":extent,
            "official_polygon_count":n,
            "mapped_class_counts_9113_9116_9121":counts,
            "source_polygons_of_unlisted_class_count":unknown,
            "strictly_seagrass_9113_9116_only":counts["9121"]==0 and unknown==0,
            "title_cannot_imply_all_features_are_seagrass":counts["9121"]>0 or unknown>0,
            "layer_metadata_sha256":sha(meta),
            "service_metadata_sha256":sha(server),
            "source_class_semantics_directly_verified":False,
            "evidence_is_independent_of_2022_2024_seagrass_maps":False
        }
    return {
     "schema":SCHEMA,"status":"PASS_MAP_CHANGE_GIS_SOURCE_METADATA_COUNTS_ONLY",
     "source_family":"CHNEP web feature layers derived from SWFWMD 2022/2024 mapped seagrass outputs",
     "records":result,
     "no_geometry_downloaded":True,
     "no_2022_algae_to_2024_seagrass_overlay_computed":True,
     "not_a_live_field_or_causal_validation":True,
     "safeguards":[
       "Source 'gain' and 'loss' may be map-category classifications, not observed plant establishment/extinction.",
       "Polygon field definitions and geographic footprints must be audited; do not apply a source role as ecological diagnosis.",
       "Potential same-map provenance makes any overlap a map-source concordance check, not independent ecological replication.",
       "No change to existing 2016 positive-history or 2022/2024 source-affinity conclusions."
     ]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    try:res=inspect();rc=0
    except (Stop,ValueError,TypeError,KeyError) as e:
        res={"schema":SCHEMA,"status":"STOP_SOURCE_SCHEMA_OR_COUNT_GATE",
             "reason":str(e),"no_2022_algae_to_2024_seagrass_overlay_computed":True}
        rc=2
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(res,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(res,indent=2,sort_keys=True,ensure_ascii=False))
    return rc
if __name__=="__main__":sys.exit(main())
