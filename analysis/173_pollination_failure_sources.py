#!/usr/bin/env python3
"""Public pollination data acquisition only; validate record, filename and publisher MD5."""
import json,hashlib,urllib.request,urllib.parse,concurrent.futures
from pathlib import Path
OUT=Path("pollination_failure_sources");OUT.mkdir(exist_ok=True)
SOURCES={
10814705:{"PLdataindividual.csv":"b84fa5c83513dbe75c0bf7840d1c74aa","pollinator.csv":"81e0deaa78a6a97e1211484cb9d0d3b3"},
3987488:{"fruit_set_multiple_visits_experiments_JAPPL-2020-00197.csv":"5617777fcef1c46bb4e0bab5ccc22ce6","fruit_set_multiple_visits_experiments_JAPPL-2020-00197.R":"51c7cbcdd1327a1b3401f6654005a16e","fruit_set_pollination_experiments_JAPPL-2020-00197.csv":"e630cd466935e7709e874ff6706f7ce0","fruit_set_pollination_experiments_JAPPL-2020-00197.R":"b037c411fee16f948dfd0b103cfa8f58","fruit_set_single_visit_experiments_JAPPL-2020-00197.csv":"d7ed02c7aa254a963043539c06c99ed7","fruit_weight_multiple_visits_experiments_JAPPL-2020-00197.csv":"112922b9ad4e5a2e068df25b900e6f53","fruit_weight_pollination_experiments_JAPPL-2020-00197.csv":"1b0e4705a26f96109d271c0caf73af0f","README.pdf":"fce6d69734b9d587aca8bffc363fda3b"}}
def get(url,cap=5_000_000):
 assert urllib.parse.urlparse(url).scheme=="https" and urllib.parse.urlparse(url).hostname=="zenodo.org"
 req=urllib.request.Request(url,headers={"User-Agent":"Tampa-source-audit/1.0","Accept-Encoding":"identity"})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read(cap+1)
 if len(b)>cap:raise ValueError("byte cap exceeded")
 return b
def save(n,b):
 (OUT/n).write_bytes(b);return {"file":n,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def retrieve(record,files):
 r={"record":record,"doi":"10.5281/zenodo."+str(record),"files":[]}
 try:
  b=get("https://zenodo.org/api/records/"+str(record));m=json.loads(b);assert str(m["id"])==str(record)
  r["metadata"]=save(str(record)+"_metadata.json",b)
  if m.get("metadata",{}).get("access_right") not in ("open",None):raise ValueError("not open access")
  listing={f["key"]:f for f in m["files"]}
  for name,md in files.items():
   v={"name":name}
   try:
    f=listing[name];assert f["checksum"]=="md5:"+md and f["size"]<=5_000_000
    url=f["links"].get("content") or f["links"]["self"];bb=get(url)
    assert len(bb)==f["size"] and hashlib.md5(bb).hexdigest()==md
    v.update(save(str(record)+"_"+name,bb),status="ACQUIRED")
   except Exception as e:v.update(status="STOP",reason=str(e)[:250])
   r["files"].append(v)
  r["status"]="ACQUIRED" if all(x["status"]=="ACQUIRED" for x in r["files"]) else "PARTIAL_OR_STOP"
 except Exception as e:r.update(status="STOP",reason=str(e)[:250])
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 result=list(ex.map(lambda item:retrieve(*item),SOURCES.items()))
(OUT/"manifest.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
