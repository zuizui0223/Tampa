#!/usr/bin/env python3
"""Acquire public reproductive-interaction sources without fitting unverified endpoints."""
import argparse, hashlib, io, json, re, urllib.request, urllib.parse, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

CAP=15_000_000
UA="Tampa-public-seagrass-source-audit/1.0"
def get(url):
    if not url.startswith("https://"): raise ValueError("HTTPS required")
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Encoding":"identity"}),timeout=35) as response:
        b=response.read(CAP+1)
    if len(b)>CAP: raise ValueError("file cap exceeded")
    return b

def save_blob(out,name,b):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+",name): raise ValueError("unsafe filename")
    (out/name).write_bytes(b)
    return {"file":name,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}

def xlsx(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        root=ET.fromstring(z.read("xl/workbook.xml"))
        ns="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        return {"sheets":[x.attrib["name"] for x in root.iter(ns+"sheet")],
                "worksheet_rows":{n:sum(1 for _ in ET.fromstring(z.read(n)).iter(ns+"row"))
                    for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",n)}}

def plos(out,name,doi):
    url="https://journals.plos.org/plosone/article/file?id="+urllib.parse.quote(doi,safe="")+"&type=supplementary"
    r={"source":doi,"url":url}
    try:
        b=get(url);r.update(xlsx(b));r.update(save_blob(out,name+".xlsx",b));r["status"]="SOURCE_WORKBOOK_ACQUIRED"
    except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return r

def dryad(out,name,doi):
    base="https://datadryad.org"
    url=base+"/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe="")
    r={"source":doi,"url":url,"files":[]}
    def follow(obj,key):
        href=obj.get("_links",{}).get(key,{}).get("href")
        if not href: raise ValueError("missing link "+key)
        u=urllib.parse.urljoin(base,href)
        if urllib.parse.urlparse(u).netloc!="datadryad.org": raise ValueError("unexpected Dryad link host")
        return u
    try:
        data=json.loads(get(url))
        r["title"]=data.get("title")
        r["metadata"]=save_blob(out,name+"_dataset.json",json.dumps(data,indent=2).encode())
        version=json.loads(get(follow(data,"stash:version")))
        r["version"]=save_blob(out,name+"_version.json",json.dumps(version,indent=2).encode())
        listing=json.loads(get(follow(version,"stash:files")))
        r["file_listing"]=save_blob(out,name+"_files.json",json.dumps(listing,indent=2).encode())
        fs=listing.get("_embedded",{}).get("stash:files",[])
        if not fs: raise ValueError("no embedded file records")
        for i,f in enumerate(fs):
            entry={"source_path":f.get("path")}
            try:
                safe=re.sub(r"[^A-Za-z0-9_.-]","_",str(f.get("path") or "file"))
                b=get(follow(f,"stash:download"))
                if safe.lower().endswith(".xlsx"):entry.update(xlsx(b))
                if safe.lower().endswith(".csv"):b.decode("utf-8-sig")
                if safe.lower().endswith(".zip") and not zipfile.is_zipfile(io.BytesIO(b)):raise ValueError("invalid zip")
                entry.update(save_blob(out,f"{name}_{i}_{safe}",b));entry["status"]="ACQUIRED"
            except Exception as e:entry.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
            r["files"].append(entry)
        r["status"]="SOURCE_FILES_ACQUIRED" if all(f["status"]=="ACQUIRED" for f in r["files"]) else "PARTIAL_OR_STOP"
    except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    specs=[(plos,"infantes_burial","10.1371/journal.pone.0168128.s001"),
           (plos,"infantes_one_week","10.1371/journal.pone.0168128.s002"),
           (plos,"infantes_one_month","10.1371/journal.pone.0168128.s003"),
           (plos,"infantes_eight_month","10.1371/journal.pone.0168128.s004"),
           (plos,"meysick_seed_trapping","10.1371/journal.pone.0222020.s007"),
           (dryad,"jeppesen_green_crab","10.7291/D1469B"),
           (dryad,"johnson_recruitment","10.5061/dryad.2bvq83bm5"),
           (dryad,"foster_genetics","10.5061/dryad.ns1rn8pt4"),
           (dryad,"gross_epifauna","10.5061/dryad.np5hqc00p")]
    with ThreadPoolExecutor(max_workers=4) as ex:
        results=list(ex.map(lambda s:s[0](a.out,s[1],s[2]),specs))
    report={"scope":"source acquisition only; no biological effect fit","sources":results}
    (a.out/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
