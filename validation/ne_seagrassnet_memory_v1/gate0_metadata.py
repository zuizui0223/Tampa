#!/usr/bin/env python3
"""Metadata-only Dryad Gate0 for Northeast SeagrassNet matched memory v1."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"candidate_contract.json").read_text())
OUT=ROOT/"gate0_metadata_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def get_json(url):
    req=Request(url,headers={"Accept":"application/json","Accept-Encoding":"identity","User-Agent":"Tampa-NE-SeagrassNet-Gate0/1.0"})
    with urlopen(req,timeout=60) as r:
        if r.status!=200:
            raise RuntimeError(f"http_{r.status}:{url}")
        raw=r.read(2_000_001)
    if len(raw)>2_000_000:
        raise RuntimeError("metadata_response_too_large")
    return json.loads(raw.decode("utf-8"))

def main():
    out={
      "schema":"tampa.ne_seagrassnet_state_memory_v1.gate0_metadata_result",
      "status":None,
      "response_file_gets":0,
      "response_bytes_opened":0,
      "response_values_opened":False
    }
    try:
        doi=C["source"]["doi"]
        # Dryad v2 public API DOI lookup. No file download endpoint is followed.
        url="https://datadryad.org/api/v2/datasets/"+quote("doi:"+doi,safe="")
        ds=get_json(url)
        safe={
          "dataset_id":ds.get("id"),
          "doi":ds.get("identifier") or ds.get("doi") or doi,
          "title":ds.get("title"),
          "publicationDate":ds.get("publicationDate"),
          "versionNumber":ds.get("versionNumber"),
          "top_level_keys":sorted(ds.keys()),
          "links":ds.get("_links",{})
        }
        # Follow metadata/version links only when present; never a download URL.
        candidates=[]
        links=ds.get("_links",{}) if isinstance(ds.get("_links",{}),dict) else {}
        for key,val in links.items():
            href=val.get("href") if isinstance(val,dict) else None
            if href and ("version" in key.lower() or "file" in key.lower()):
                candidates.append((key,href))
        safe["candidate_metadata_links"]=[{"rel":k,"href":h} for k,h in candidates]
        file_meta=None
        for key,href in candidates:
            if "file" in key.lower():
                obj=get_json(href)
                file_meta=obj
                break
        if file_meta is not None:
            # retain metadata only, strip any accidental preview/content fields
            safe_files=[]
            embedded=file_meta.get("_embedded",{}) if isinstance(file_meta,dict) else {}
            seq=[]
            if isinstance(embedded,dict):
                for v in embedded.values():
                    if isinstance(v,list):
                        seq.extend(v)
            if not seq and isinstance(file_meta,dict) and isinstance(file_meta.get("files"),list):
                seq=file_meta["files"]
            for f in seq:
                if not isinstance(f,dict):
                    continue
                safe_files.append({
                  "id":f.get("id"),
                  "path":f.get("path") or f.get("filename") or f.get("name"),
                  "size":f.get("size"),
                  "mimeType":f.get("mimeType"),
                  "status":f.get("status")
                })
            safe["files"]=safe_files
        out["safe_metadata"]=safe
        out["safe_metadata_fingerprint"]=canon(safe)
        names={str(x.get("path")) for x in safe.get("files",[])}
        expected={x["name"] for x in C["source"]["public_files_from_landing_page"]}
        if safe.get("files") and not expected.issubset(names):
            raise RuntimeError("dryad_file_identity_mismatch")
        out["status"]="gate0_metadata_pass"
        out["next_gate"]="freeze README/documentation access only; biological CSV remains unopened"
    except Exception as exc:
        out["status"]="metadata_transport_or_schema_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
