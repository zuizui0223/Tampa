#!/usr/bin/env python3
"""Source-only acquisition for independent emergence and seascape experiments."""
import io,json,hashlib,urllib.request,urllib.parse,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET
out=Path("reproductive_stage_sources");out.mkdir(exist_ok=True)
specs=[("jorgensen_s"+str(i)+".xlsx","https://journals.plos.org/plosone/article/file?id="+urllib.parse.quote("10.1371/journal.pone.0215157.s00"+str(i),safe="")+"&type=supplementary") for i in range(1,5)]
specs.append(("carroll_2019.zip","https://digitalcommons.georgiasouthern.edu/context/biology-data/article/1002/type/native/viewcontent"))
def probe(spec):
 name,url=spec;r={"file":name,"url":url}
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Tampa-reproductive-stage-source-audit/1.0","Accept-Encoding":"identity"})
  with urllib.request.urlopen(req,timeout=45) as resp:b=resp.read(20_000_001)
  if len(b)>20_000_000:raise ValueError("cap exceeded")
  with zipfile.ZipFile(io.BytesIO(b)) as z:
   r["members"]=[{"name":x.filename,"bytes":x.file_size} for x in z.infolist()][:150]
   if name.endswith(".xlsx"):
    root=ET.fromstring(z.read("xl/workbook.xml"))
    r["sheets"]=[x.attrib["name"] for x in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet")]
  (out/name).write_bytes(b);r.update(status="ACQUIRED",sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:300])
 return r
with ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(probe,specs))
(out/"manifest.json").write_text(json.dumps(results,indent=2)+"\n");print(json.dumps(results,indent=2))
