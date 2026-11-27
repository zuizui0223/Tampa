#!/usr/bin/env python3
"""Acquire actual seagrass survey points for both historic tracking regions."""
import hashlib, json, urllib.request, urllib.parse, concurrent.futures
from pathlib import Path
OUT=Path("seagrass_point_sources");OUT.mkdir(exist_ok=True)
SPECS=[("torres","nesp-mac-1:TS-GOC_JCU_NESP-MaC-1-13_Seagrass-sites_1983-2022","141,-11,145,-9,EPSG:4326"),("shoalwater","nesp1:GBR_NESP-TWQ-3-1_JCU_Seagrass_1984-2014_Site-surveys","148.5,-24,152,-20.5,EPSG:4326")]
def fetch(s):
 name,layer,bbox=s
 url="https://maps.eatlas.org.au/maps/wfs?"+urllib.parse.urlencode(dict(service="WFS",version="1.0.0",request="GetFeature",typeName=layer,outputFormat="application/json",srsName="EPSG:4326",bbox=bbox))
 r=dict(name=name,url=url)
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Tampa-seagrass-research/1.0","Accept-Encoding":"identity"}),timeout=65) as f:
   data=f.read(60_000_001)
  if len(data)>60_000_000:raise ValueError("byte cap")
  j=json.loads(data);fs=j["features"]
  assert j["type"]=="FeatureCollection" and len(fs)>0
  total=j.get("totalFeatures");assert total in (None,"unknown") or int(total)==len(fs)
  assert all(x["geometry"]["type"]=="Point" for x in fs)
  file=name+"_survey_points.geojson";(OUT/file).write_bytes(data)
  r.update(state="ACQUIRED",file=file,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),features=len(fs),keys=list(fs[0]["properties"]),example=fs[0]["properties"],reported_total=total)
 except Exception as e:r.update(state="STOP",reason=type(e).__name__+": "+str(e)[:250])
 return r
if __name__=="__main__":
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:res=list(e.map(fetch,SPECS))
 (OUT/"manifest.json").write_text(json.dumps(res,indent=2)+"\n");print(json.dumps(res,indent=2))
