#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"response_head_contract.json").read_text())
EML=json.loads((ROOT/"deep_eml_result.json").read_text())
OUT=ROOT/"response_head_result.json"
def canon(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def main():
 out={"schema":"tampa.nps_tier3_external_early_warning_v2.response_head_result","status":None,
      "response_body_gets":0,"response_body_bytes_opened":0,"response_values_opened":False}
 try:
  if EML["fingerprint"]!=C["requires_eml_fingerprint"] or EML["status"]!="gate0_deep_eml_qualified":
   raise RuntimeError("eml_gate_identity_or_status_mismatch")
  req=Request(C["response_csv"]["url"],method="HEAD",headers={"Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier3-v2-HEAD/1.0"})
  with urlopen(req,timeout=60) as r:
   if r.status not in (200,204): raise RuntimeError(f"head_http_{r.status}")
   length=r.headers.get("Content-Length")
   if length is None or int(length)<=0: raise RuntimeError("missing_or_nonpositive_content_length")
   safe={"requested_url":C["response_csv"]["url"],"resolved_url":r.geturl(),"content_length":int(length),
         "content_type":str(r.headers.get("Content-Type","")),"etag":str(r.headers.get("ETag","")),
         "last_modified":str(r.headers.get("Last-Modified",""))}
  out["safe_response_identity"]=safe
  out["safe_response_identity_fingerprint"]=canon(safe)
  out["status"]="gate1_response_identity_pass"
  out["next_gate"]="freeze exact CSV header/parser, transect-year construction, estimability, model and terminal decision before the single response GET"
 except Exception as exc:
  out["status"]="terminal_pre_response_head_stop";out["reason"]=str(exc);out["next_gate"]="none"
 out["fingerprint"]=canon(out)
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
