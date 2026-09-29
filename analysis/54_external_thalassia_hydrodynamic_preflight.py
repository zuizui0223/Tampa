#!/usr/bin/env python3
"""Response-independent preflight for an external Thalassia hydrodynamic dataset.

The source is the PANGAEA archive accompanying Kaack, Fugate & Thomas (2024).
This script only inventories the public binary-file index. It does not read Tampa
biological responses and does not select an external endpoint.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

import pandas as pd
import requests

DOI="10.1594/PANGAEA.967585"
URL=f"https://doi.org/{DOI}"

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
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
    (outdir/"pangaea_967585_index.tsv").write_text(text)
    df=pd.read_csv(io.StringIO(text),sep="\t",comment="#")
    summary={
        "schema":"tampa.external_thalassia_hydrodynamic_preflight_v1",
        "status":"external_binary_index_opened_response_independent",
        "source":{
            "doi":DOI,
            "landing":"https://doi.pangaea.de/10.1594/PANGAEA.967585",
            "license":"CC-BY-4.0",
            "supplement_to":"Kaack, Fugate & Thomas 2024, All Earth, DOI 10.1080/27669645.2024.2419236",
        },
        "rows":int(len(df)),
        "columns":[str(x) for x in df.columns],
        "records":df.fillna("").astype(str).to_dict(orient="records"),
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
