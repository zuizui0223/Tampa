#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,io,json,re
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
V=json.loads((ROOT/"version_metadata_result.json").read_text())
C=json.loads((ROOT/"readme_schema_contract.json").read_text())
OUT=ROOT/"readme_schema_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def norm(s):
    return re.sub(r"\s+"," ",str(s or "").strip()).lower()

def main():
    out={"schema":"tampa.ne_seagrassnet_state_memory_v1.readme_schema_result","status":None,
         "readme_gets":0,"readme_bytes_opened":0,"response_file_gets":0,"response_bytes_opened":0,"response_values_opened":False}
    try:
        if V["fingerprint"]!=C["requires_version_metadata_fingerprint"] or V["status"]!="version_file_metadata_pass":
            raise RuntimeError("version_metadata_mismatch")
        fid=int(C["readme_file"]["dryad_file_id"])
        url=f"https://datadryad.org/api/v2/files/{fid}/download"
        req=Request(url,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-NE-SeagrassNet-README/1.0"})
        out["readme_gets"]=1
        with urlopen(req,timeout=60) as r:
            if r.status!=200: raise RuntimeError(f"readme_http_{r.status}")
            raw=r.read(int(C["readme_file"]["size"])+1)
        out["readme_bytes_opened"]=len(raw)
        if len(raw)!=int(C["readme_file"]["size"]):
            raise RuntimeError(f"readme_size_mismatch:{len(raw)}")
        text=raw.decode("utf-8-sig")
        rows=list(csv.reader(io.StringIO(text)))
        flat="\n".join(" | ".join(row) for row in rows)
        low=norm(flat)
        # Keep full README because it is documentation/schema, not biological response.
        safe={"sha256":hashlib.sha256(raw).hexdigest(),"rows":rows,"text":flat}
        checks={
          "site_identifier": any(x in low for x in ["site", "site code"]),
          "quadrat_identifier": "quadrat" in low,
          "time": any(x in low for x in ["year","date"]),
          "percent_cover": ("cover" in low and any(x in low for x in ["percent","%"])),
          "zero_semantics_explicit": any(x in low for x in ["0 =","0%","zero","absence","absent"])
        }
        out["safe_readme"]=safe
        out["schema_checks"]=checks
        out["safe_readme_fingerprint"]=canon(safe)
        # Do not automatically treat generic quadrat mention as proof of stable longitudinal identity.
        if not (checks["site_identifier"] and checks["quadrat_identifier"] and checks["time"] and checks["percent_cover"]):
            out["status"]="terminal_pre_response_readme_schema_stop"
            out["reason"]="required_field_semantics_missing"
            out["next_gate"]="none"
        else:
            out["status"]="readme_schema_inventory_complete"
            out["next_gate"]="human/machine semantic audit of whether quadrat identifier is longitudinally stable and zero is observed absence; response CSV remains unopened"
    except Exception as exc:
        out["status"]="readme_access_or_schema_stop"; out["reason"]=str(exc); out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
