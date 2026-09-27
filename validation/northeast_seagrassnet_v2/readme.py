#!/usr/bin/env python3
"""README-only public-browser gate for Northeast SeagrassNet v2."""
from __future__ import annotations
import csv, hashlib, io, json
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"readme_contract.json").read_text())
OUT=ROOT/"readme_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def main():
    out={
      "schema":"tampa.northeast_seagrassnet_external_early_warning_v2.readme_result",
      "status":None,
      "readme_gets":0,
      "response_file_gets":0,
      "response_file_bytes_opened":0,
      "response_values_opened":False,
    }
    try:
        spec=C["source"]["metadata_file"]
        req=Request(spec["public_browser_url"],headers={
          "Accept-Encoding":"identity",
          "User-Agent":"Tampa-Northeast-SeagrassNet-v2-README/1.0"
        })
        out["readme_gets"]=1
        with urlopen(req,timeout=60) as resp:
            if resp.status!=200:
                raise RuntimeError(f"readme_http_{resp.status}")
            raw=resp.read(int(spec["size"])+1)
        if len(raw)!=int(spec["size"]):
            raise RuntimeError(f"readme_size_mismatch:{len(raw)}")
        if hashlib.sha256(raw).hexdigest()!=spec["sha256"]:
            raise RuntimeError("readme_sha256_mismatch")
        if raw.startswith(b"\xef\xbb\xbf"):
            raw=raw[3:]
        text=raw.decode("utf-8")
        rows=list(csv.reader(io.StringIO(text,newline="")))
        if not rows or len(rows)>100:
            raise RuntimeError(f"readme_shape_unexpected:{len(rows)}")
        safe={"row_count":len(rows),"rows":rows,"sha256":spec["sha256"]}
        blob="\n".join(" | ".join(r) for r in rows).lower()
        out["safe_readme"]=safe
        out["safe_readme_fingerprint"]=canon(safe)
        out["semantic_screen"]={
          "mentions_year_or_date": any(k in blob for k in ["year","date"]),
          "mentions_cover": "cover" in blob,
          "mentions_site_or_quadrat_or_transect": any(k in blob for k in ["site","quadrat","transect","plot"]),
          "mentions_zero_or_presence_absence": any(k in blob for k in ["0","presence","absence","absent","present"])
        }
        if not (out["semantic_screen"]["mentions_year_or_date"] and out["semantic_screen"]["mentions_cover"] and out["semantic_screen"]["mentions_site_or_quadrat_or_transect"]):
            out["status"]="terminal_pre_response_readme_semantics_stop"
            out["reason"]="README_insufficient_for_time_cover_or_stable_unit_semantics"
            out["next_gate"]="none"
        else:
            out["status"]="readme_schema_available"
            out["next_gate"]="freeze exact parser, stable unit, state definition, estimability, learner and terminal decision before response access"
    except Exception as exc:
        out["status"]="terminal_pre_response_readme_transport_or_parse_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
