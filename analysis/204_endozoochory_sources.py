#!/usr/bin/env python3
"""Public source-only audit of marine animal endozoochory; no auth bypass."""
import concurrent.futures,hashlib,io,json,re,urllib.request,urllib.parse,zipfile
from html.parser import HTMLParser
from pathlib import Path
OUT=Path("endozoochory_sources"); OUT.mkdir(exist_ok=True)
def get(url,cap=10_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-public-source-research/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=20) as f:
        b=f.read(cap+1)
        if len(b)>cap: raise ValueError("cap")
        return b,{"url":url,"host":urllib.parse.urlsplit(f.geturl()).netloc,"status":f.status,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"content_type":f.headers.get("Content-Type")}
class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":self.urls.extend(v for k,v in attrs if k=="href" and v)
def tol():
    result={"doi":"10.4225/28/57ABBA449E639","probes":[],"files":[]}
    for url in ["https://doi.org/10.4225/28/57ABBA449E639","https://researchdata.jcu.edu.au/published/0d8a44334ae3e5ef81609a4d59d8f2ef"]:
        try:
            b,m=get(url,2_000_000);parser=Links();parser.feed(b.decode("utf-8",errors="replace"))
            links=list(dict.fromkeys(urllib.parse.urljoin(url,u) for u in parser.urls))
            candidate=[u for u in links if urllib.parse.urlsplit(u).scheme=="https" and urllib.parse.urlsplit(u).netloc.endswith("jcu.edu.au") and (re.search(r"\.(xlsx|ods|csv|zip)(?:$|\?)",u,re.I) or "/download/" in u.lower() or "/download?" in u.lower())]
            result["probes"].append({**m,"candidate_links":candidate[:20]})
            for n,u in enumerate(candidate[:5]):
                try:
                    data,info=get(u);z=zipfile.ZipFile(io.BytesIO(data));names=z.namelist()
                    if "xl/workbook.xml" in names:ext=".xlsx"
                    elif "content.xml" in names:ext=".ods"
                    else:raise ValueError("not a workbook")
                    name="tol_"+str(n)+ext;(OUT/name).write_bytes(data)
                    result["files"].append({**info,"file":name,"state":"ACQUIRED","members":names[:30]})
                except Exception as e: result["files"].append({"url":u,"state":"STOP","reason":str(e)[:200]})
            if any(x["state"]=="ACQUIRED" for x in result["files"]):break
        except Exception as e:result["probes"].append({"url":url,"state":"STOP","reason":str(e)[:200]})
    return result
def pdf():
    try:
        b,m=get("https://www.int-res.com/articles/feature/m471p001.pdf")
        if not b.startswith(b"%PDF"):raise ValueError("not PDF")
        (OUT/"sumoski2012.pdf").write_bytes(b);return {**m,"file":"sumoski2012.pdf","state":"ACQUIRED"}
    except Exception as e:return {"state":"STOP","reason":str(e)[:200]}
if __name__=="__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:
        a=e.submit(tol);b=e.submit(pdf);result=[a.result(),b.result()]
    (OUT/"manifest.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
