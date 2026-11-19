#!/usr/bin/env python3
"""Source-only gate for historical SWFWMD 2016 mapped seagrass layer.

Does not inspect 2016 polygon geometry, 2022/2024 overlap, or biological
responses. Provides the minimum source metadata required before assessing
whether historical seagrass extent may define a valid recovery pool.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

SOURCE="https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental/MapServer/20"
SCHEMA="tampa.charlotte_2016_historical_seagrass_metadata_gate_v1"
UA="Seagrass ecological public source metadata audit (2016 legacy)/1.0"
EXPECTED_CLASS_FIELDS={"FLUCCS_CODE","FLUCCSCODE"}

class SourceStop(Exception): pass

def fetch(params,base=SOURCE):
    url=base+"?"+urlencode(params)
    try:
        with urlopen(Request(url,headers={"User-Agent":UA,"Accept":"application/json"}),timeout=45) as response:
            raw=response.read(5_000_001)
    except (URLError,HTTPError,OSError,TimeoutError) as e:
        raise SourceStop("LEGACY_SOURCE_UNREACHABLE:"+type(e).__name__) from e
    if len(raw)>5_000_000:
        raise SourceStop("LEGACY_SOURCE_TOO_LARGE_FOR_METADATA_GATE")
    try: data=json.loads(raw)
    except (UnicodeDecodeError,ValueError) as e: raise SourceStop("LEGACY_NOT_JSON") from e
    if not isinstance(data,dict) or "error" in data:
        raise SourceStop("LEGACY_SERVICE_ERROR:"+str(data.get("error",data))[:300])
    return data

def validate_layer(meta):
    if meta.get("type")!="Feature Layer" or meta.get("geometryType")!="esriGeometryPolygon":
        raise SourceStop("LEGACY_NOT_POLYGON_FEATURE_LAYER")
    fields={f.get("name"):f.get("type") for f in meta.get("fields",[]) if isinstance(f,dict)}
    ids=[k for k,t in fields.items() if t=="esriFieldTypeOID"]
    cls=sorted(EXPECTED_CLASS_FIELDS.intersection(fields))
    if not ids or not cls:
        raise SourceStop("LEGACY_IDENTIFIER_OR_CLASS_CODE_UNRESOLVED")
    sr=(meta.get("extent") or {}).get("spatialReference") or {}
    if not any(k in sr for k in ("wkid","latestWkid","wkt")):
        raise SourceStop("LEGACY_CRS_UNRESOLVED")
    return {"name":meta.get("name"),"description":str(meta.get("description") or "")[:3000],
      "object_id_field":meta.get("objectIdField") or ids[0],
      "class_fields":cls,
      "fields":{k:t for k,t in fields.items() if k in cls or k in ids
                or "AREA" in k.upper() or "ACRE" in k.upper() or "YEAR" in k.upper()
                or "SHAPE" in k.upper()},
      "source_extent":meta.get("extent"),
      "extent_spatial_reference":sr,
      "max_record_count":meta.get("maxRecordCount"),
      "capabilities":meta.get("capabilities"),
      "drawing_class_expression":(meta.get("drawingInfo") or {}).get("renderer",{}).get("field1"),
      "metadata_sha256":hashlib.sha256(json.dumps(meta,sort_keys=True).encode()).hexdigest()}

def check(fetcher=fetch):
    meta=fetcher({"f":"json"})
    details=validate_layer(meta)
    count=fetcher({"where":"1=1","returnCountOnly":"true","f":"json"},SOURCE+"/query").get("count")
    if not isinstance(count,int) or count<1:
        raise SourceStop("LEGACY_FEATURE_COUNT_UNRESOLVED")
    return {"schema":SCHEMA,"status":"PASS_2016_METADATA_AND_COUNT_ONLY",
        "source_url":SOURCE,
        "legacy_layer":details,
        "feature_count_whole_legacy_layer":count,
        "source_polygons_downloaded":False,
        "source_classes_geospatially_harmonized":False,
        "charlotte_harbor_footprint_extracted":False,
        "2016_2022_spatial_overlay_computed":False,
        "cannot_identify_recovered_historically_vegetated_bottom":True,
        "next_gate":"Verify source date and class dictionary; isolate exact Charlotte footprint, transform declared CRS, compare 2016 seagrass class acreage against original official per-polygon area, and only then pair with 2022-2024."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True)
    x=p.parse_args()
    try:
        result=check();rc=0
    except (SourceStop,ValueError,TypeError) as e:
        result={"schema":SCHEMA,"status":"STOP_2016_SOURCE_GATE","reason":str(e),
                "2016_2022_spatial_overlay_computed":False,
                "cannot_identify_recovered_historically_vegetated_bottom":True};rc=2
    dst=Path(x.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":sys.exit(main())
