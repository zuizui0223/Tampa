#!/usr/bin/env python3
"""Public Glacier Bay source inventory. No biological inference from unknown schemas."""
import argparse,csv,hashlib,io,json,re,urllib.parse,urllib.request,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
CAP=60_000_000
UA="Tampa-seagrass-public-source-audit/1.0"
SOURCES=[
 ("forage","10.5066/P9T6UB5G","Glacier Bay National Park and Preserve Sea Otter Forage Data, 1993-2019"),
 ("benthos","10.5066/P9LODH0Z","Intertidal and Subtidal Sea Otter Prey Sampling in Mixed Sediment Habitat in Glacier Bay National Park and Preserve, Alaska, 1998 to 2011"),
]
def get(url):
    u=urllib.parse.urlparse(url)
    if u.scheme!="https":raise ValueError("HTTPS required")
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Encoding":"identity"}),timeout=45) as f:
        data=f.read(CAP+1);final=f.geturl()
    if len(data)>CAP:raise ValueError("download cap exceeded")
    return data,final
def norm(s):return re.sub(r"[^a-z0-9]+"," ",str(s).lower()).strip()
def safe(s):return re.sub(r"[^A-Za-z0-9_.-]","_",s)
def profile(b,name):
    if name.lower().endswith((".csv",".tsv")):
        reader=csv.reader(io.StringIO(b.decode("utf-8-sig")),delimiter="\t" if name.lower().endswith(".tsv") else ",")
        header=next(reader)
        if len(header)<2 or len(header)!=len(set(header)):raise ValueError("invalid table header")
        n=0;bad=0;first=[]
        for row in reader:
            n+=1
            if len(row)!=len(header):bad+=1
            if n<=3:first.append(row)
        return dict(columns=header,rows=n,irregular_rows=bad,first_three_rows=first)
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(b)) as z:return {"members":[{"name":i.filename,"uncompressed_bytes":i.file_size} for i in z.infolist()][:250]}
    return {}
def save(out,name,b):
    name=safe(name)
    (out/name).write_bytes(b)
    return dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def sciencebase(out,name,doi,title):
    rec=dict(name=name,doi=doi,expected_title=title,files=[],metadata=[],attempts=[])
    root="https://www.sciencebase.gov/catalog/"
    def jget(u):
        b,_=get(u)
        return json.loads(b)
    def extract_id(u):
        m=re.search(r"/item/([0-9a-f]{24})",u,re.I)
        return m.group(1) if m else None
    def find_id():
        try:
            b,u=get("https://doi.org/"+doi);rec["attempts"].append({"doi_final":u})
            i=extract_id(u)
            if i:return i
            ids=re.findall(r"https?://(?:www\.)?sciencebase\.gov/catalog/item/([0-9a-f]{24})",b.decode("utf-8",errors="ignore"))
            if len(set(ids))==1:return ids[0]
        except Exception as e:rec["attempts"].append({"doi_error":str(e)[:250]})
        for q in (doi,title):
            try:
                j=jget(root+"items?"+urllib.parse.urlencode({"q":q,"format":"json","max":20}))
                hits=[r for r in j.get("items",[]) if norm(r.get("title",""))==norm(title)]
                rec["attempts"].append({"search":q,"hits":[{"id":r.get("id"),"title":r.get("title")} for r in j.get("items",[])][:20]})
                if len(hits)==1:return hits[0]["id"]
            except Exception as e:rec["attempts"].append({"search_error":str(e)[:250]})
        raise ValueError("source item not resolved")
    try:
        iid=find_id();rec["item_id"]=iid
        queue=[iid];seen=set()
        while queue and len(seen)<25:
            i=queue.pop(0)
            if i in seen:continue
            seen.add(i)
            meta=jget(root+"item/"+i+"?format=json")
            if i==iid and norm(meta.get("title"))!=norm(title) and doi.lower() not in json.dumps(meta).lower():
                raise ValueError("item title/DOI mismatch")
            rec["metadata"].append(save(out,name+"_"+i+".json",json.dumps(meta,indent=2).encode()))
            for k,f in enumerate(meta.get("files",[])):
                fn=f.get("name","")
                if not re.search(r"\.(csv|tsv|xml|txt|zip|xlsx|pdf)$",fn,re.I):continue
                r={"source_name":fn,"item":i}
                try:
                    u=f.get("downloadUri") or f.get("url")
                    if not u:raise ValueError("no file URL")
                    b,final=get(urllib.parse.urljoin(root,u));r["final_url"]=final
                    r.update(profile(b,fn));r.update(save(out,name+"_"+i+"_"+str(k)+"_"+fn,b));r["status"]="ACQUIRED"
                except Exception as e:r.update(status="STOP",reason=str(e)[:250])
                rec["files"].append(r)
            if meta.get("hasChildren"):
                child=jget(root+"items?"+urllib.parse.urlencode({"parentId":i,"format":"json","max":100}))
                queue.extend(r["id"] for r in child.get("items",[]))
        rec["status"]="TABLES_ACQUIRED" if any(f.get("status")=="ACQUIRED" and "rows" in f for f in rec["files"]) else "NO_TABLE_ACQUIRED"
    except Exception as e:rec.update(status="STOP",reason=str(e)[:300])
    return rec
def zenodo(out):
    rec={"name":"published_code","doi":"10.5281/zenodo.14042546","files":[]}
    try:
        b,_=get("https://zenodo.org/api/records/14042546")
        j=json.loads(b);rec["title"]=j.get("metadata",{}).get("title")
        rec["metadata"]=save(out,"zenodo_14042546.json",b)
        for k,f in enumerate(j.get("files",[])):
            r={"source_name":f.get("key")}
            try:
                b,_=get(f["links"]["self"]);r.update(profile(b,r["source_name"]));r.update(save(out,"zenodo_"+str(k)+"_"+r["source_name"],b));r["status"]="ACQUIRED"
            except Exception as e:r.update(status="STOP",reason=str(e)[:250])
            rec["files"].append(r)
        rec["status"]="ACQUIRED" if rec["files"] and all(f["status"]=="ACQUIRED" for f in rec["files"]) else "PARTIAL_OR_STOP"
    except Exception as e:rec.update(status="STOP",reason=str(e)[:250])
    return rec
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        jobs=[ex.submit(sciencebase,a.out,*s) for s in SOURCES]+[ex.submit(zenodo,a.out)]
        records=[j.result() for j in jobs]
    report={"scope":"public source and schema audit only; no biological effect fit","sources":records}
    (a.out/"manifest.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2))
if __name__=="__main__":main()
