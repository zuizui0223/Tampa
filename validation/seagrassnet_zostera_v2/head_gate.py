#!/usr/bin/env python3
"""Body-free HEAD qualification of the SeagrassNet multi-site download endpoint."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT.parent/"seagrassnet_zostera_v1"/"preflight_result.json").read_text())
C=json.loads((ROOT/"head_contract.json").read_text())
OUT=ROOT/"head_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def main():
    out={
        "schema":"tampa.seagrassnet_zostera_external_early_warning_v2.head_result",
        "status":None,
        "head_requests":0,
        "response_body_read_calls":0,
        "response_body_bytes":0,
        "response_values_opened":False
    }
    try:
        if P["fingerprint"]!=C["prior_v1"]["preflight_fingerprint"] or P["status"]!="preflight_interface_inventory_complete":
            raise RuntimeError("candidate_universe_fingerprint_or_status_mismatch")
        sites=sorted(P["safe_interface"]["candidate_sites"],key=lambda x:(x.get("code",""),x["uuid"]))
        ids=[x["uuid"] for x in sites]
        if len(ids)<5 or len(ids)!=len(set(ids)):
            raise RuntimeError("invalid_candidate_uuid_universe")
        endpoint=C["request"]["base"]+C["request"]["path"]+"?"+urlencode({"sites":",".join(ids)})
        req=Request(endpoint,method="HEAD",headers={"Accept-Encoding":"identity","User-Agent":"Tampa-SeagrassNet-v2-HEAD/1.0"})
        out["head_requests"]=1
        with urlopen(req,timeout=60) as resp:
            status=resp.status
            headers={k.lower():v for k,v in resp.headers.items()}
            final_url=resp.geturl()
            # Intentionally do not call read().
        if status<200 or status>=300:
            raise RuntimeError(f"head_http_{status}")
        ctype=headers.get("content-type","")
        disp=headers.get("content-disposition","")
        if not ctype and not disp:
            raise RuntimeError("head_missing_content_type_and_disposition")
        safe={
            "candidate_site_count":len(ids),
            "candidate_uuid_sha256":hashlib.sha256("\n".join(ids).encode()).hexdigest(),
            "endpoint_path":C["request"]["path"],
            "query_parameter":C["request"]["query_parameter"],
            "http_status":status,
            "content_type":ctype,
            "content_disposition":disp,
            "content_length":headers.get("content-length",""),
            "final_host":urlparse(final_url).hostname or "",
            "final_path":urlparse(final_url).path,
            "etag":headers.get("etag",""),
            "last_modified":headers.get("last-modified","")
        }
        out["safe_head"]=safe
        out["safe_head_fingerprint"]=canon(safe)
        out["status"]="gate0_head_qualified"
        out["next_gate"]="freeze exact return-container parser and biological endpoint semantics before one full GET"
    except Exception as exc:
        out["status"]="terminal_pre_response_head_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
