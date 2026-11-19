#!/usr/bin/env python3
"""CHAP independent field-monitoring *station registry* source preflight.

Tests a public SEACAR MapServer layer, Program 570 (Charlotte Harbor
Seagrass Monitoring). This is only station POINT metadata, NOT original
field-quadrat values, actual 2022/2024 sampled sites, 2024 live vegetation
truth, or validation of mapped algal loss.

Metadata/count/status are independently checked and pinned. No user email
and no restricted SEACAR workbooks are requested. Only after a successful
gate can a separate spatial-proximity check be attempted.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError

URL="https://gis.waterinstitute.usf.edu/arcgis/rest/services/Maps/SEACAR_Datazoom/MapServer/179"
PROGRAM=570
SCHEMA="tampa.chap_570_public_seagrass_station_registry_preflight_v1"
USER_AGENT="Original SEACAR CHAP station public-data audit/1.0"
class Stop(ValueError):pass

def get(url,params):
    req=Request(url+"?"+urlencode(params),headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    try:
        with urlopen(req,timeout=45) as r:raw=r.read(4_000_001)
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise Stop("PUBLIC_STATION_SOURCE_UNAVAILABLE:"+type(e).__name__) from e
    if len(raw)>4_000_000:raise Stop("PUBLIC_SOURCE_OVERLONG")
    try:v=json.loads(raw)
    except (ValueError,UnicodeDecodeError) as e:raise Stop("STATION_SOURCE_NON_JSON") from e
    if not isinstance(v,dict) or "error" in v:
        raise Stop("STATION_SOURCE_ERROR:"+str(v.get("error",v))[:250])
    return v

def sha(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def audit(fetch=get):
    meta=fetch(URL,{"f":"json"})
    if meta.get("geometryType")!="esriGeometryPoint":
        raise Stop("CHAP_570_SOURCE_NOT_POINT_LAYER")
    fields={x.get("name"):x.get("type") for x in meta.get("fields",[]) if isinstance(x,dict)}
    if fields.get("ProgramID") not in ("esriFieldTypeInteger","esriFieldTypeSmallInteger"):
        raise Stop("CHAP_570_MISSING_PROGRAM_ID")
    oid=meta.get("objectIdField")
    if not isinstance(oid,str) or fields.get(oid)!="esriFieldTypeOID":
        raise Stop("CHAP_570_MISSING_SOURCE_OID")
    if "ProgramLocationID" not in fields:
        raise Stop("CHAP_570_MISSING_SITE_KEY")
    count=fetch(URL+"/query",{"f":"json","where":"ProgramID=570","returnCountOnly":"true"}).get("count")
    if not isinstance(count,int) or count<1:
        raise Stop("CHAP_570_NO_PUBLIC_STATION_RECORDS")
    all_count=fetch(URL+"/query",{"f":"json","where":"1=1","returnCountOnly":"true"}).get("count")
    if not isinstance(all_count,int) or all_count<count:
        raise Stop("CHAP_570_BAD_POINT_UNIVERSE")
    response=fetch(URL+"/query",{"f":"json","where":"ProgramID=570","returnIdsOnly":"true"})
    ids=response.get("objectIds")
    if not isinstance(ids,list) or len(ids)!=count or len(set(ids))!=count:
        raise Stop("CHAP_570_BAD_STATION_OID_ROSTER")
    if not all(isinstance(i,int) for i in ids):raise Stop("CHAP_570_NONINTEGER_OID")
    return {
       "schema":SCHEMA,
       "status":"PASS_PUBLIC_CHAP_570_POINT_LAYER_AND_OID_INVENTORY_ONLY",
       "url":URL,
       "geometryType":"esriGeometryPoint",
       "count_program570_point_features":count,
       "count_all_layer_features":all_count,
       "point_ids_sha256":sha(sorted(ids)),
       "layer_metadata_sha256":sha(meta),
       "object_id_field":oid,
       "field_types":fields,
       "declared_extent":meta.get("extent"),
       "public_source_reference":"https://data.florida-seacar.org/programs/details/570",
       "original_quadrat_data_opened":False,
       "points_confirmed_current_2024_survey":False,
       "source_location_points_are_not_abundance_or_coverage":True,
       "not_an_independent_field_ground_truth_of_unmapped_2024":True,
       "interpretation":"A point-source roster only documents locations in the public SEACAR registry, not which site was visited in 2016/2022/2024 or any field condition. Data-source representativeness/temporal recency must be independently verified before comparing to GIS map classes."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    try: r=audit();rc=0
    except (Stop,TypeError,ValueError,KeyError) as e:
        r={"schema":SCHEMA,"status":"STOP_CHAP_570_PUBLIC_REGISTRY_SOURCE",
           "reason":str(e),"field_biology_verified":False};rc=2
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True))
    return rc

if __name__=="__main__":sys.exit(main())
