#!/usr/bin/env python3
"""Response-open Dryad acquisition gate for reproductive-stage datasets.
No credentials, no guessed file IDs, no ecological effect fitting.
"""
import csv
import hashlib
import io
import json
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ORIGIN="https://datadryad.org"
SOURCES={
    "johnson_2020":"10.5061/dryad.2bvq83bm5",
    "kendrick_2022":"10.5061/dryad.vhhmgqnwz",
    "foster_2022":"10.5061/dryad.ns1rn8pt4",
    "balestri_2021":"10.5061/dryad.t76hdr81n",
    "yu_2019":"10.5061/dryad.sn1h87s",
}
LIMIT=20_000_000

def fetch(url):
    url=urllib.parse.urljoin(ORIGIN,url)
    u=urllib.parse.urlsplit(url)
    if u.scheme!="https" or u.netloc!="datadryad.org":
        raise ValueError("Unexpected API link origin")
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-reproductive-source-audit/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=35) as r:
        raw=r.read(LIMIT+1)
    if len(raw)>LIMIT:
        raise ValueError("Source exceeds byte cap")
    return raw

def payload(url):
    raw=fetch(url)
    return json.loads(raw),hashlib.sha256(raw).hexdigest()

def links(o):
    found={}
    for key,val in (o.get("_links") or {}).items():
        if isinstance(val,dict) and isinstance(val.get("href"),str):
            found[key]=val["href"]
    return found

def zip_inventory(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files=[]
        if len(z.infolist())>250 or sum(x.file_size for x in z.infolist())>50_000_000:
            raise ValueError("Archive expansion exceeds cap")
        for item in z.infolist():
            if item.is_dir(): continue
            data=z.read(item)
            entry=dict(name=item.filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            if item.filename.lower().endswith(".csv"):
                # Inventory only, not outcome parsing or inference.
                try:
                    reader=csv.reader(io.StringIO(data.decode("utf-8-sig")))
                    entry["header"]=next(reader,None)
                    entry["subsequent_rows"]=sum(1 for _ in reader)
                except (UnicodeError,csv.Error):
                    entry["csv_profile"]="schema_stop"
            files.append(entry)
    return files

def audit(name,doi):
    url="/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe="")
    record=dict(name=name,doi=doi,estimated_ecological_effect=False)
    try:
        meta,sha=payload(url)
        record.update(dataset_metadata_sha256=sha,title=meta.get("title"),dataset_links=links(meta))
        # Follow only advertised version link, no synthetic file ID.
        vers=[v for k,v in links(meta).items() if k.split(":")[-1]=="version"]
        vmeta=meta
        if len(vers)==1:
            vmeta,vsha=payload(vers[0])
            record.update(version_metadata_sha256=vsha,version_links=links(vmeta))
        dl=[v for k,v in links(vmeta).items() if k.split(":")[-1]=="download"]
        if len(dl)!=1:
            record["status"]="METADATA_ONLY_NO_UNAMBIGUOUS_DOWNLOAD_LINK"
            return record
        raw=fetch(dl[0])
        record.update(archive_sha256=hashlib.sha256(raw).hexdigest(),archive_bytes=len(raw))
        if not zipfile.is_zipfile(io.BytesIO(raw)):
            record["status"]="DOWNLOADED_NOT_ZIP_SCHEMA_STOP"
            return record
        record["files"]=zip_inventory(raw)
        record["status"]="ARCHIVE_INVENTORIED_NO_EFFECT_FIT"
    except (ValueError,TypeError,AttributeError,KeyError,UnicodeError,zipfile.BadZipFile,urllib.error.URLError,TimeoutError,OSError) as e:
        record.update(status="ACCESS_OR_SCHEMA_STOP",reason=f"{type(e).__name__}: {str(e)[:220]}")
    return record

if __name__=="__main__":
    print(json.dumps({"status":"source_eligibility_only",
                      "datasets":[audit(k,v) for k,v in SOURCES.items()]},indent=2,sort_keys=True))
