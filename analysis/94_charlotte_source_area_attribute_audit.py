#!/usr/bin/env python3
"""Inspect original source area attributes for invalid Charlotte GIS polygon OIDs.

No geometry repair, no species abundance, no new seagrass->algae transition.
This is an independent source-area cross-check to diagnose GeoJSON rings.
"""
import argparse,json,hashlib,sys
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path

SRC={
"2022":("https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2022_in_Charlotte_Harbor/FeatureServer/1",
       (2284,2181,2297,2273)),
"2024":("https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2024_in_Charlotte_Harbor/FeatureServer/1",
       (2997,1620,1612,1298,1428,969,2139))
}
FIELDS=("FID","FLUCCSCODE","FLUCCSDESC","ACRES","Geodesic","SHAPE_STAr",
        "Shape_STAr","Shape__Area")

def fetch(url,params):
    u=url+"?"+urlencode(params)
    with urlopen(Request(u,headers={"User-Agent":"Charlotte research area provenance/1.0"}),timeout=45) as r:
        ans=json.loads(r.read(1_000_000))
    if not isinstance(ans,dict) or "error" in ans:
        raise ValueError("SOURCE_ERROR:"+str(ans)[:250])
    return ans

def inspect(request=fetch):
    info={}
    for year,(url,oids) in SRC.items():
        meta=request(url,{"f":"json"})
        fields=[f["name"] for f in meta["fields"] if f.get("name") in FIELDS]
        if "FID" not in fields or "FLUCCSCODE" not in fields:
            raise ValueError("SOURCE_SCHEMA_DRIFT:"+year)
        d=request(url+"/query",{"where":"FID IN ("+",".join(map(str,oids))+")",
              "outFields":",".join(fields),"returnGeometry":"false","f":"json"})
        feats=d.get("features",[])
        index={f["attributes"].get("FID"):f["attributes"] for f in feats}
        if set(index)!=set(oids):raise ValueError("OID_RETRIEVAL_INCOMPLETE:"+year)
        info[year]={"source":url,
             "fields_used":fields,
             "source_metadata_sha256":hashlib.sha256(json.dumps(meta,sort_keys=True).encode()).hexdigest(),
             "invalid_geometry_oids":list(oids),
             "attributes":{str(k):v for k,v in sorted(index.items())}}
    return {
      "schema":"tampa.charlotte_invalid_geometry_area_attribute_audit_v1",
      "purpose":"Compare original source area attributes to candidate repaired geometry, not choose a repair method after outcome analysis.",
      "no_topological_repair_authorized":True,
      "no_transition_estimate":True,
      "source_attributes":info}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    try:
        res=inspect()
        rc=0
    except Exception as e:
        res={"schema":"tampa.charlotte_invalid_geometry_area_attribute_audit_v1",
             "status":"STOP_SOURCE_ATTRIBUTE_AUDIT","reason":str(e),
             "area_inference_permitted":False}
        rc=2
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(res,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":sys.exit(main())
