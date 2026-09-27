#!/usr/bin/env python3
"""Metadata-schema inventory for Alaska eelgrass v2.

Reads only the ScienceBase item JSON. It never requests the response CSV.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"metadata_schema_contract.json").read_text())
OUT=ROOT/"metadata_schema_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def slim_file(f):
    return {
        "name": str(f.get("name","")),
        "title": str(f.get("title","")),
        "size": f.get("size"),
        "contentType": str(f.get("contentType","")),
        "url": str(f.get("url") or f.get("downloadUri") or f.get("downloadURL") or ""),
        "md5": str(f.get("md5") or f.get("checksum") or ""),
    }

def slim_link(x):
    return {
        "title": str(x.get("title","")),
        "type": str(x.get("type","")),
        "uri": str(x.get("uri") or x.get("url") or ""),
    }

def summarize_facets(facets):
    out=[]
    if not isinstance(facets,list):
        return out
    for f in facets:
        if not isinstance(f,dict):
            continue
        rec={"className":str(f.get("className","")),"keys":sorted(str(k) for k in f.keys())}
        # Preserve only obvious metadata/schema descriptors, never arrays of biological observations.
        for key in ("name","title","description","startDate","endDate","minX","maxX","minY","maxY"):
            if key in f and isinstance(f[key],(str,int,float,bool,type(None))):
                rec[key]=f[key]
        out.append(rec)
    return out

def main():
    state={
        "schema":"tampa.alaska_eelgrass_external_early_warning_v2.metadata_schema_result",
        "status":None,
        "response_csv_gets":0,
        "response_csv_bytes_opened":0,
        "response_values_opened":False,
    }
    try:
        item_id=C["source"]["sciencebase_item_id"]
        url=f"https://www.sciencebase.gov/catalog/item/{item_id}?format=json"
        req=Request(url,headers={"Accept":"application/json","Accept-Encoding":"identity","User-Agent":"Tampa-Alaska-Eelgrass-v2-Metadata/1.0"})
        with urlopen(req,timeout=60) as resp:
            if resp.status!=200:
                raise RuntimeError(f"metadata_http_{resp.status}")
            raw=resp.read(5_000_001)
        if len(raw)>5_000_000:
            raise RuntimeError("metadata_too_large")
        item=json.loads(raw.decode("utf-8"))
        if str(item.get("id",""))!=item_id:
            raise RuntimeError("item_id_mismatch")
        files=[slim_file(f) for f in item.get("files",[]) if isinstance(f,dict)]
        response_name=C["source"]["response_csv_name"]
        matched=[f for f in files if f["name"]==response_name]
        if len(matched)!=1 or int(matched[0]["size"])!=int(C["source"]["response_csv_size"]):
            raise RuntimeError("response_csv_identity_drift")
        safe={
            "item_id":item_id,
            "title":str(item.get("title","")),
            "summary":str(item.get("summary","")),
            "body":str(item.get("body","")),
            "tags":[str(t.get("name","")) for t in item.get("tags",[]) if isinstance(t,dict)],
            "files":files,
            "webLinks":[slim_link(x) for x in item.get("webLinks",[]) if isinstance(x,dict)],
            "facets":summarize_facets(item.get("facets",[])),
            "top_level_keys":sorted(str(k) for k in item.keys()),
        }
        state["status"]="metadata_schema_inventory_complete"
        state["safe_metadata_inventory"]=safe
        state["safe_metadata_fingerprint"]=canon(safe)
        state["next_gate"]="inspect only this metadata inventory; freeze official metadata-document selection before any further network access"
    except Exception as exc:
        state["status"]="terminal_pre_response_metadata_schema_stop"
        state["reason"]=str(exc)
        state["next_gate"]="none"
    state["fingerprint"]=canon(state)
    OUT.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    print(json.dumps(state,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
