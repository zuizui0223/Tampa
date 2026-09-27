#!/usr/bin/env python3
"""README-only schema gate for Northeast USA SeagrassNet v1."""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
G0=json.loads((ROOT/"gate0_result.json").read_text())
C=json.loads((ROOT/"readme_gate_contract.json").read_text())
OUT=ROOT/"readme_gate_result.json"


def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()


def main():
    out={
        "schema":"tampa.northeast_seagrassnet_external_early_warning_v1.readme_gate_result",
        "status":None,
        "readme_gets":0,
        "response_file_gets":0,
        "response_file_bytes_opened":0,
        "response_values_opened":False,
    }
    try:
        if G0["status"]!="gate0_metadata_pass" or G0["fingerprint"]!=C["requires_gate0_fingerprint"]:
            raise RuntimeError("gate0_identity_or_status_mismatch")
        r=C["readme"]
        req=Request(r["download_url"],headers={
            "Accept-Encoding":"identity",
            "User-Agent":"Tampa-Northeast-SeagrassNet-README/1.0",
        })
        out["readme_gets"]=1
        with urlopen(req,timeout=60) as resp:
            if resp.status!=200:
                raise RuntimeError(f"readme_http_{resp.status}")
            raw=resp.read(int(r["size"])+1)
        if len(raw)!=int(r["size"]):
            raise RuntimeError(f"readme_size_mismatch:{len(raw)}")
        if hashlib.sha256(raw).hexdigest()!=r["sha256"]:
            raise RuntimeError("readme_sha256_mismatch")
        if raw.startswith(b"\xef\xbb\xbf"):
            raw=raw[3:]
        text=raw.decode("utf-8")
        rows=list(csv.reader(io.StringIO(text,newline="")))
        if not rows:
            raise RuntimeError("empty_readme")
        if len(rows)>100:
            raise RuntimeError("readme_unexpectedly_row_like")
        safe={
            "row_count":len(rows),
            "rows":rows,
            "readme_sha256":r["sha256"],
        }
        blob="\n".join(" | ".join(cell for cell in row) for row in rows).lower()
        has_time=any(k in blob for k in ["year","date"])
        has_cover=("cover" in blob and ("zostera" in blob or "eelgrass" in blob or "percent" in blob))
        has_unit=any(k in blob for k in ["site","quadrat","transect","station","plot"])
        zero_semantics=("0" in blob and any(k in blob for k in ["absence","absent","presence","percent cover","cover"]))
        out["safe_readme"]=safe
        out["safe_readme_fingerprint"]=canon(safe)
        out["semantic_screen"]={
            "has_time_semantics":has_time,
            "has_cover_semantics":has_cover,
            "has_spatial_unit_semantics":has_unit,
            "mentions_zero_in_state_context":zero_semantics
        }
        if not (has_time and has_cover and has_unit):
            out["status"]="terminal_pre_response_readme_semantics_stop"
            out["reason"]="README_does_not_define_required_time_cover_or_sampling_unit_semantics"
            out["next_gate"]="none"
        else:
            out["status"]="readme_schema_available"
            out["next_gate"]="manually freeze exact parser/state/estimability contract from this README before response-file GET"
    except Exception as exc:
        out["status"]="terminal_pre_response_readme_transport_or_parse_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
