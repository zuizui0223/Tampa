#!/usr/bin/env python3
"""Bounded single-connection HYCOM surface-current subset for historic Torres Strait tracks."""
import hashlib,json,urllib.parse,urllib.request
from pathlib import Path
OUT=Path("torres_hycom_sources");OUT.mkdir(exist_ok=True)
BASE="https://ncss.hycom.org/thredds/ncss/grid/GLBu0.08/reanalysis/3hrly"
# Request one bounded window first. Only if successful, continue with the second.
windows=[("2010","2010-09-12T00:00:00Z","2011-02-06T00:00:00Z"),("2009","2009-07-24T00:00:00Z","2009-08-22T00:00:00Z")]
def retrieve(label,start,end):
    params=[("var","water_u"),("var","water_v"),("north","-7.5"),("south","-12.5"),("west","139"),("east","147"),("vertCoord","0"),("time_start",start),("time_end",end),("accept","netcdf4")]
    url=BASE+"?"+urllib.parse.urlencode(params);r={"label":label,"url":url}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Tampa-historic-seagrass-research/1.0","Accept-Encoding":"identity"})
        with urllib.request.urlopen(req,timeout=90) as f:
            b=f.read(65_000_001);r.update(http=f.status,content_type=f.headers.get("Content-Type"))
        if len(b)>65_000_000:raise ValueError("size cap exceeded")
        if not (b.startswith(b"CDF") or b.startswith(b"\x89HDF\r\n\x1a\n")):raise ValueError("not netCDF bytes")
        path=OUT/("uv_"+label+".nc");path.write_bytes(b)
        r.update(state="ACQUIRED",file=path.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e:r.update(state="STOP",reason=type(e).__name__+": "+str(e)[:300])
    return r
if __name__=="__main__":
    result=[]
    for spec in windows:
        r=retrieve(*spec);result.append(r)
        if r["state"]!="ACQUIRED":break
    (OUT/"manifest.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
