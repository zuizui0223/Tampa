"""Retry exact small public USGS source files; preserve bytes, verify publisher MD5, audit encoding."""
import csv,hashlib,io,json,urllib.request,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
OUT=Path("glacier_bay_retry");OUT.mkdir(exist_ok=True)
sources=[
("forage_taxonomy.csv","https://www.sciencebase.gov/catalog/file/get/65fc57bdd34e64ff1548d3c3?f=__disk__dd%2F1d%2F23%2Fdd1d2345ae636d0693586ea7617de789aa95e91a","3e02efaed73711be6bbb8b46eff25314",9278),
("benthos_sites.csv","https://www.sciencebase.gov/catalog/file/get/627d23b2d34e3bef0c9a1d3a?f=__disk__5f%2F2a%2F65%2F5f2a65446c26ff6f25123365d80bbeb5f994d931","cb06a08a8fa17093e3b0a366f98d3c30",10783),
("benthos_metadata.xml","https://www.sciencebase.gov/catalog/file/get/627d23b2d34e3bef0c9a1d3a?f=__disk__bf%2F01%2F42%2Fbf014257b7ae2adb2d198ff7da87ea7a66f11363","430287fc367e9ec16f762c8cb395ddf8",46977)]
def acquire(s):
 name,url,md5,size=s;r=dict(file=name,url=url,expected_md5=md5.zfill(32),expected_bytes=size,errors=[])
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Tampa-source-audit/1.0","Accept-Encoding":"identity"})
   with urllib.request.urlopen(req,timeout=30) as f:b=f.read(1_000_001)
   assert len(b)==size and hashlib.md5(b).hexdigest()==md5.zfill(32),"publisher byte count or MD5 mismatch"
   (OUT/name).write_bytes(b)
   r.update(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),status="RAW_VERIFIED")
   if name.endswith(".csv"):
    for enc in ("utf-8-sig","cp1252","latin-1"):
     try:
      rows=list(csv.reader(io.StringIO(b.decode(enc))));assert len(rows)>1 and len(set(rows[0]))==len(rows[0]);assert all(len(x)==len(rows[0]) for x in rows)
      r.update(encoding=enc,rows=len(rows)-1,columns=rows[0],status="RAW_VERIFIED_SCHEMA_PROFILED")
      break
     except (UnicodeError,AssertionError,csv.Error):continue
   return r
  except Exception as e:r["errors"].append(str(e)[:250]);time.sleep(attempt+1)
 r["status"]="STOP";return r
with ThreadPoolExecutor(max_workers=3) as ex:records=list(ex.map(acquire,sources))
(OUT/"manifest.json").write_text(json.dumps(records,indent=2)+"\n")
print(json.dumps(records,indent=2))
