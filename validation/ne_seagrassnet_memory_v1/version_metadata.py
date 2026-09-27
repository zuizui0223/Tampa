#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
G=json.loads((ROOT/"gate0_metadata_result.json").read_text())
C=json.loads((ROOT/"version_metadata_contract.json").read_text())
OUT=ROOT/"version_metadata_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def getj(url):
    if url.startswith("/"): url="https://datadryad.org"+url
    req=Request(url,headers={"Accept":"application/json","Accept-Encoding":"identity","User-Agent":"Tampa-NE-SeagrassNet-VersionMeta/1.0"})
    with urlopen(req,timeout=60) as r:
        if r.status!=200: raise RuntimeError(f"http_{r.status}:{url}")
        raw=r.read(2_000_001)
    if len(raw)>2_000_000: raise RuntimeError("metadata_too_large")
    return json.loads(raw.decode("utf-8"))
def main():
    out={"schema":"tampa.ne_seagrassnet_state_memory_v1.version_metadata_result","status":None,
         "response_file_gets":0,"response_bytes_opened":0,"response_values_opened":False}
    try:
        if G["fingerprint"]!=C["requires_gate0_fingerprint"] or G["status"]!="gate0_metadata_pass":
            raise RuntimeError("gate0_mismatch")
        v=getj(f"https://datadryad.org/api/v2/versions/{C['version_id']}")
        links=v.get("_links",{}) if isinstance(v,dict) else {}
        safe={"version_id":v.get("id"),"versionNumber":v.get("versionNumber"),
              "publicationDate":v.get("publicationDate"),"top_level_keys":sorted(v.keys()),
              "links":links}
        files_href=None
        for k,val in links.items():
            if "file" in k.lower() and isinstance(val,dict) and val.get("href"):
                files_href=val["href"]; break
        if files_href is None:
            # Dryad documents a /files child on a version; this is still metadata, never file content.
            files_href=f"/api/v2/versions/{C['version_id']}/files"
        fm=getj(files_href)
        seq=[]
        if isinstance(fm,dict):
            emb=fm.get("_embedded",{})
            if isinstance(emb,dict):
                for val in emb.values():
                    if isinstance(val,list): seq.extend(val)
            if isinstance(fm.get("files"),list): seq.extend(fm["files"])
        if isinstance(fm,list): seq=fm
        seen=set(); files=[]
        for f in seq:
            if not isinstance(f,dict): continue
            name=str(f.get("path") or f.get("filename") or f.get("name") or "")
            if not name or name in seen: continue
            seen.add(name)
            links2=f.get("_links",{}) if isinstance(f.get("_links",{}),dict) else {}
            files.append({"id":f.get("id"),"name":name,"size":f.get("size"),
                          "mimeType":f.get("mimeType"),"status":f.get("status"),"links":links2})
        safe["files"]=files
        names={x["name"] for x in files}
        exp=set(C["expected_filenames"])
        if not exp.issubset(names): raise RuntimeError("expected_file_metadata_missing:"+repr(sorted(names)))
        out["safe_metadata"]=safe
        out["safe_metadata_fingerprint"]=canon(safe)
        out["status"]="version_file_metadata_pass"
        out["next_gate"]="freeze README file id and read README only; biological CSV remains unopened"
    except Exception as exc:
        out["status"]="version_metadata_stop"; out["reason"]=str(exc); out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
