#!/usr/bin/env python3
"""Download published historic telemetry and mapped seagrass polygons, with a strict byte cap."""
import concurrent.futures,hashlib,io,json,urllib.request,urllib.parse,zipfile
from pathlib import Path
OUT=Path("megaherbivore_track_sources");OUT.mkdir(exist_ok=True)
def get(name,url,kind,cap=35_000_000):
    r={"file":name,"url":url}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Tampa-seagrass-dispersal-research/1.0","Accept-Encoding":"identity"})
        with urllib.request.urlopen(req,timeout=45) as f:
            b=f.read(cap+1);r.update(http=f.status,content_type=f.headers.get("Content-Type"))
        if len(b)>cap:raise ValueError("byte cap exceeded")
        if kind=="zip":
            with zipfile.ZipFile(io.BytesIO(b)) as z:r["members"]=[{"name":i.filename,"size":i.file_size} for i in z.infolist()][:100]
        else:
            doc=json.loads(b)
            if kind=="geojson":
                if doc.get("type")!="FeatureCollection" or not doc.get("features"):raise ValueError("not nonempty feature collection")
                r["n_features"]=len(doc["features"]);r["keys"]=list(doc["features"][0]["properties"])
            else:
                if not doc.get("results"):raise ValueError("no results")
                r["n_results"]=len(doc["results"]);r["keys"]=list(doc["results"][0]);r["total"]=doc.get("total")
        (OUT/name).write_bytes(b);r.update(state="ACQUIRED",size=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e:r.update(state="STOP",reason=type(e).__name__+": "+str(e)[:300])
    return r
if __name__=="__main__":
    dataset="08d6a561-fe83-47cb-81dd-913353935c18"
    query=urllib.parse.urlencode({"datasetid":dataset,"size":10000})
    wfs="https://maps.eatlas.org.au/maps/wfs?"+urllib.parse.urlencode({"service":"WFS","version":"1.0.0","request":"GetFeature","typeName":"nesp-mac-1:TS-GOC_JCU_NESP-MaC-1-13_Seagrass-meadows_1983-2022","outputFormat":"application/json","srsName":"EPSG:4326","bbox":"141,-11,145,-9,EPSG:4326"})
    specs=[("tracking_dwca.zip","https://www.marine.csiro.au/ipt/archive.do?r=nerp_1221_dugongs_turtles","zip"),("tracking_obis.json","https://api.obis.org/v3/occurrence?"+query,"obis"),("ts_meadows.geojson",wfs,"geojson")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:res=list(ex.map(lambda x:get(*x),specs))
    (OUT/"manifest.json").write_text(json.dumps(res,indent=2)+"\n");print(json.dumps(res,indent=2))
