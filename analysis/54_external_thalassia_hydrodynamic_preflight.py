#!/usr/bin/env python3
"""Response-independent preflight for an external Thalassia hydrodynamic dataset.

The source is the PANGAEA archive accompanying Kaack, Fugate & Thomas (2024).
This script only inventories the public binary-file index. It does not read Tampa
biological responses and does not select an external endpoint.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

import requests

DOI="10.1594/PANGAEA.967585"
URL=f"https://doi.org/{DOI}"

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    try:
        r=requests.get(
            URL,
            headers={
                "Accept":"text/tab-separated-values",
                "User-Agent":"Tampa-external-hydro-preflight/1.0",
            },
            timeout=120,
            allow_redirects=True,
        )
        r.raise_for_status()
        text=r.text
    except requests.RequestException as exc:
        text=f"# PANGAEA live index temporarily unavailable: {exc}\n"
        (outdir/"pangaea_967585_index.tsv").write_text(text)
        summary={
            "schema":"tampa.external_thalassia_hydrodynamic_preflight_v1",
            "status":"external_index_temporarily_unavailable",
            "source":{"doi":DOI},
            "error":str(exc),
            "claim_boundary":[
                "Live source availability is operational, not scientific evidence.",
                "The frozen six-file ADV manifest is stored separately in results/external_thalassia_hydrodynamic_preflight_v1.json."
            ],
        }
        (outdir/"external_thalassia_hydrodynamic_preflight_v1.json").write_text(
            json.dumps(summary,indent=2,sort_keys=True)+"\n"
        )
        print(json.dumps(summary,indent=2,sort_keys=True))
        return
    (outdir/"pangaea_967585_index.tsv").write_text(text)
    lines=text.splitlines()
    parsed=[]
    for i,line in enumerate(lines, start=1):
        if not line.strip():
            continue
        fields=next(csv.reader([line],delimiter="\t"))
        parsed.append({"line_number":i,"field_count":len(fields),"fields":fields})
    # PANGAEA binary indexes contain a metadata preamble before the data table.
    # Preserve the raw inventory first; file selection will be frozen only after
    # this structure is visible.
    summary={
        "schema":"tampa.external_thalassia_hydrodynamic_preflight_v1",
        "status":"external_binary_index_opened_response_independent",
        "source":{
            "doi":DOI,
            "landing":"https://doi.pangaea.de/10.1594/PANGAEA.967585",
            "license":"CC-BY-4.0",
            "supplement_to":"Kaack, Fugate & Thomas 2024, All Earth, DOI 10.1080/27669645.2024.2419236",
        },
        "nonempty_lines":len(parsed),
        "tab_structure":parsed,
        "claim_boundary":[
            "This preflight inventories an external physical-data archive only.",
            "No Tampa focal biological response is accessed.",
            "File selection for any benchmark must be based on file content/type labels, not on a desired effect direction."
        ],
    }
    (outdir/"external_thalassia_hydrodynamic_preflight_v1.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_external_hydro"))
    a=p.parse_args()
    main(a.out)
