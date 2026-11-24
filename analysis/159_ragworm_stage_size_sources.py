#!/usr/bin/env python3
"""Retrieve public, versioned source bytes only. No fitted biological result.
Never retry restricted files with authentication or alternate bypass routes."""
import csv, hashlib, io, json, re, urllib.parse, urllib.request, zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
OUT=Path("ragworm_stage_sources"); OUT.mkdir(exist_ok=True)
CAP=40_000_000
def get(url,cap=CAP):
    assert urllib.parse.urlparse(url).scheme=="https"
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-ecology-source-audit/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=60) as r:
        length=r.headers.get("Content-Length")
        if length and int(length)>cap: raise ValueError("content length exceeds cap")
        data=r.read(cap+1)
    if len(data)>cap: raise ValueError("byte cap exceeded")
    return data
def save(name,data):
    name=re.sub(r"[^a-zA-Z0-9_.-]","_",name)
    (OUT/name).write_bytes(data)
    return dict(file=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def profile(name,data):
    result={}
    if name.lower().endswith((".csv",".tsv",".tab")):
        for enc in ("utf-8-sig","cp1252"):
            try:
                s=data.decode(enc);dialect=csv.Sniffer().sniff(s[:16384],delimiters=",;\t")
                reader=csv.reader(io.StringIO(s),dialect=dialect);header=next(reader);n=bad=0
                for r in reader:
                    if not r:continue
                    n+=1;bad+=len(r)!=len(header)
                result.update(encoding=enc,delimiter=dialect.delimiter,columns=header,rows=n,irregular_rows=bad)
                break
            except (UnicodeError,csv.Error,StopIteration):continue
    elif name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            result["members"]=[dict(name=i.filename,bytes=i.file_size) for i in z.infolist() if i.filename.lower().endswith((".csv",".tsv",".txt",".xlsx",".r",".rmd"))][:250]
    return result
def sibes():
    doi="10.25850/nioz/7b.b.ug";base="https://dataverse.nioz.nl"
    r=dict(doi=doi,files=[])
    try:
        raw=get(base+"/api/datasets/:persistentId/?persistentId="+urllib.parse.quote("doi:"+doi,safe=""))
        d=json.loads(raw)["data"]
        assert d["identifier"].lower()=="7b.b.ug" and d["authority"].lower()=="nioz"
        r["metadata"]=save("sibes_metadata.json",raw)
        fs=d["latestVersion"]["files"]
        for f in fs:
            v=f["dataFile"]; name=v["filename"]; label=f.get("label",name)
            if not ({name.lower(),label.lower()} & {"biota.csv","samples.csv","sample.csv","species.csv","biota.tab","samples.tab","species.tab"}):continue
            x={"name":name,"label":label,"id":v["id"],"restricted":bool(f.get("restricted"))}
            try:
                if f.get("restricted"):raise ValueError("restricted file")
                if v.get("filesize",0)>CAP:raise ValueError("file size exceeds cap")
                data=get(base+"/api/access/datafile/"+str(v["id"]))
                checksum=v.get("checksum",{})
                if checksum.get("type","").upper()=="MD5":assert hashlib.md5(data).hexdigest()==checksum["value"].lower().zfill(32)
                if checksum.get("type","").upper()=="SHA-1":assert hashlib.sha1(data).hexdigest()==checksum["value"].lower()
                x.update(save("sibes_"+str(v["id"])+"_"+name,data));x.update(profile(name,data));x["status"]="RAW_ACQUIRED"
            except Exception as e:x.update(status="STOP",reason=str(e)[:250])
            r["files"].append(x)
        r["status"]="RAW_ACQUIRED" if len(r["files"])==3 and all(f["status"]=="RAW_ACQUIRED" for f in r["files"]) else "PARTIAL_OR_STOP"
    except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return r
def hautekiet():
    doi="10.5281/zenodo.15182547";r=dict(doi=doi,files=[])
    try:
        b=get("https://zenodo.org/api/records/15182547")
        j=json.loads(b);assert str(j["id"])=="15182547" and "fibrous algae" in j["metadata"]["title"].lower()
        r["metadata"]=save("hautekiet_metadata.json",b)
        for f in j["files"]:
            name=f["key"];x={"name":name,"size":f.get("size"),"checksum":f.get("checksum"),"links":f.get("links")}
            try:
                if not name.lower().endswith((".csv",".tsv",".txt",".xlsx",".zip",".r",".rmd")):raise ValueError("not a tabular or code/archive source")
                if f.get("size",0)>CAP:raise ValueError("archive/file above cap; manual table-only extraction needed")
                url=f["links"].get("content") or f["links"]["self"]
                bb=get(url);assert len(bb)==f["size"]
                chk=f.get("checksum","")
                if chk.startswith("md5:"):assert hashlib.md5(bb).hexdigest()==chk[4:].lower()
                x.update(save("hautekiet_"+name,bb));x.update(profile(name,bb));x["status"]="RAW_ACQUIRED"
            except Exception as e:x.update(status="STOP_OR_SKIPPED",reason=str(e)[:250])
            r["files"].append(x)
        r["status"]="RAW_TABLE_OR_ARCHIVE_ACQUIRED" if any(f.get("status")=="RAW_ACQUIRED" for f in r["files"]) else "METADATA_ONLY"
    except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return r
def dryad():
    doi="10.5061/dryad.23j62";r=dict(doi=doi,files=[])
    try:
        b=get("https://datadryad.org/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe=""))
        j=json.loads(b);assert "spartina" in j["title"].lower() and "seed burial" in j["title"].lower()
        r["metadata"]=save("zhu2015_metadata.json",b)
        link=j.get("_links",{}).get("stash:version",{}).get("href")
        if not link:raise ValueError("no version link")
        v=get(urllib.parse.urljoin("https://datadryad.org",link));r["version_metadata"]=save("zhu2015_version.json",v)
        z=json.loads(v); href=z.get("_links",{}).get("stash:files",{}).get("href")
        if not href:raise ValueError("no version files link")
        ff=get(urllib.parse.urljoin("https://datadryad.org",href));r["file_metadata"]=save("zhu2015_files.json",ff)
        for f in json.loads(ff).get("_embedded",{}).get("stash:files",[]):
            x={"name":f.get("path")}
            try:
                h=f["_links"]["stash:download"]["href"];data=get(urllib.parse.urljoin("https://datadryad.org",h));x.update(save("zhu2015_"+str(f["path"]),data));x.update(profile(f["path"],data));x["status"]="RAW_ACQUIRED"
            except Exception as e:x.update(status="STOP",reason=str(e)[:250])
            r["files"].append(x)
        r["status"]="RAW_ACQUIRED" if r["files"] and all(f["status"]=="RAW_ACQUIRED" for f in r["files"]) else "METADATA_OR_STOP"
    except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return r
with ThreadPoolExecutor(max_workers=3) as ex:
    futures=[ex.submit(sibes),ex.submit(hautekiet),ex.submit(dryad)]
    results=[f.result() for f in futures]
(OUT/"manifest.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results,indent=2))
