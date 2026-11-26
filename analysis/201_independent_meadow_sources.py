#!/usr/bin/env python3
"""Acquire public, source-documented datasets only; record metadata and byte identity.
No credentials, no authentication circumvention, no replacement/imputed biological data.
"""
import concurrent.futures, hashlib, io, json, re, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
OUT=Path("independent_meadow_sources")
OUT.mkdir(exist_ok=True)
MAX_BYTES=30_000_000
UA="Tampa-eelgrass-independent-source-audit/1.0"
DV="https://dataverse.unc.edu/api/"
CAN="https://api-proxy.edh-cde.dfo-mpo.gc.ca/catalogue/records/56cfea6f-aeca-47ed-94ab-c519d9e63c91/attachments/"
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
def get(url, cap=MAX_BYTES):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=25) as f:
        data=f.read(cap+1)
        if len(data)>cap: raise ValueError("download exceeds cap")
        return data, {"url":url,"final_url":f.geturl(),"status":f.status,"bytes":len(data),"content_type":f.headers.get("Content-Type"),"sha256":hashlib.sha256(data).hexdigest()}
def inspect_bytes(data,name):
    if name.lower().endswith((".zip",".xlsx")):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            members=z.infolist()
            if len(members)>2000 or sum(x.file_size for x in members)>150_000_000: raise ValueError("archive expansion cap")
            res={"members":[{"name":x.filename,"bytes":x.file_size} for x in members][:200]}
            if name.lower().endswith(".xlsx"):
                root=ET.fromstring(z.read("xl/workbook.xml"))
                res["sheets"]=[s.attrib["name"] for s in root.iter(NS+"sheet")]
            return res
    if name.lower().endswith((".csv",".tab",".tsv")):
        s=data.decode("utf-8-sig",errors="replace")
        if s.lstrip().lower().startswith(("<!doctype html","<html")): raise ValueError("HTML received instead of table")
        return {"first_line":s.splitlines()[0][:3000] if s.splitlines() else "", "line_count":len(s.splitlines())}
    raise ValueError("unexpected file type")
def save_valid(data,name,meta,advertised=None):
    info=inspect_bytes(data,name)
    if advertised and advertised.get("checksum"):
        c=advertised["checksum"]; alg=c["type"].lower().replace("-","")
        if alg in hashlib.algorithms_available:
            actual=hashlib.new(alg,data).hexdigest()
            if actual.lower()!=c["value"].lower(): raise ValueError("advertised checksum mismatch")
            info["verified_checksum"]={"algorithm":alg,"value":actual}
    (OUT/name).write_bytes(data)
    return dict(meta,**info,state="ACQUIRED",file=name)
def dv(doi):
    result={"doi":doi,"files":[]}
    try:
        data,meta=get(DV+"datasets/:persistentId/?"+urllib.parse.urlencode({"persistentId":"doi:"+doi}),4_000_000)
        doc=json.loads(data)
        if doc.get("status")!="OK": raise ValueError("metadata not OK")
        dataset=doc["data"]; version=dataset["latestVersion"]
        if version.get("versionState")!="RELEASED": raise ValueError("not released")
        result["metadata"]={**meta,"dataset_id":dataset["id"],"version":[version.get("versionNumber"),version.get("versionMinorNumber")]}
        slug=doi.rsplit("/",1)[-1]
        (OUT/(slug+"_metadata.json")).write_bytes(data)
        for item in version.get("files",[]):
            f=item["dataFile"]; name=f["filename"]
            if item.get("restricted") or f.get("restricted") or f.get("filesize",0)>MAX_BYTES: 
                result["files"].append({"file":name,"state":"STOP","reason":"restricted or oversized"});continue
            if Path(name).suffix.lower() not in {".xlsx",".csv",".tsv",".tab",".zip"}: continue
            safe=slug+"_"+re.sub(r"[^a-zA-Z0-9_.-]+","_",name)
            try:
                b,m=get(DV+"access/datafile/"+str(f["id"])+"?format=original")
                result["files"].append(save_valid(b,safe,m,f))
            except Exception as e: result["files"].append({"file":name,"state":"STOP","reason":type(e).__name__+": "+str(e)[:250]})
        result["state"]="ACQUIRED" if any(f["state"]=="ACQUIRED" for f in result["files"]) else "STOP"
    except Exception as e: result.update(state="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return result
def canada():
    result={"dataset":"56cfea6f-aeca-47ed-94ab-c519d9e63c91","files":[]}
    try:
        data,meta=get("https://open.canada.ca/data/api/action/package_show?id=56cfea6f-aeca-47ed-94ab-c519d9e63c91",4_000_000)
        doc=json.loads(data)
        if not doc.get("success"): raise ValueError("CKAN result not successful")
        (OUT/"canada_metadata.json").write_bytes(data)
        result["metadata"]=meta
        urls=list(dict.fromkeys(r["url"] for r in doc["result"]["resources"] if r.get("url","").startswith(CAN) and urllib.parse.urlparse(r["url"]).path.lower().endswith((".csv",".zip",".xlsx"))))
        if not urls: raise ValueError("no documented attachment URL")
        for url in urls[:5]:
            name="canada_"+re.sub(r"[^a-zA-Z0-9_.-]+","_",urllib.parse.unquote(urllib.parse.urlparse(url).path.rsplit("/",1)[-1]))
            try:
                b,m=get(url);result["files"].append(save_valid(b,name,m))
            except Exception as e: result["files"].append({"file":name,"state":"STOP","reason":type(e).__name__+": "+str(e)[:250]})
        result["state"]="ACQUIRED" if any(f["state"]=="ACQUIRED" for f in result["files"]) else "STOP"
    except Exception as e: result.update(state="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return result
if __name__=="__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        jobs=[ex.submit(dv,d) for d in ["10.15139/S3/MIE0B9","10.15139/S3/C4GJFA","10.15139/S3/GUWZQA"]]+[ex.submit(canada)]
        results=[x.result() for x in jobs]
    (OUT/"manifest.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps(results,indent=2))
