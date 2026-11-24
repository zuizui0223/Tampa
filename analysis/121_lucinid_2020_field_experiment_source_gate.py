#!/usr/bin/env python3
"""Read the public 2020 seagrass-lucinid FIELD experimental data source gate.

Published van der Geest et al. "First field-based evidence ..." Dryad DOI
10.5061/dryad.jm63xsj6n. This is explicitly exploratory reanalysis of a
published field experiment, NOT a novel independent coastal experiment.

Acquire data ONLY through official Dryad API, selected by the exact original
file labels. No biological inference until treatment and plot definitions
are verified against the dataset ReadMe and original manuscript.
"""
from __future__ import annotations
import argparse
import csv
import io
import hashlib
import json
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

HOST="https://datadryad.org"
DOI="10.5061/dryad.jm63xsj6n"
DATASET_ENDPOINT=HOST+"/api/v2/datasets/doi%3A10.5061%2Fdryad.jm63xsj6n"
KEY_FILES=(
    "ReadMe_file.txt",
    "Table_7_Field_experiment_porewater_nutrient_and_sulfide_concentrations.txt",
    "Table_9_Field_experiment_Z_noltei_AND_L_orbiculatus_data_per_experimental_plot.txt",
)
MAX=150000

def fetch(url,fetcher=None):
    if not url.startswith(HOST+"/api/v2/"):
        raise ValueError("Unexpected non-Dryad API download")
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-2020-lucinid-field-response-open/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(MAX+1)
    if len(b)>MAX:raise ValueError("File too large to inspect without separate approval")
    return b

def href(root,key):
    links=root.get("_links",{})
    val=links.get(key,{})
    out=val if isinstance(val,str) else val.get("href","")
    if not out.startswith("/api/v2/"):
        raise ValueError(f"Missing/invalid {key} in official Dryad response")
    return HOST+out

def resolve_files(obj):
    if not isinstance(obj,dict):raise ValueError("Unexpected Dryad file manifest")
    result={}
    def descend(node):
        if isinstance(node,list):
            for x in node:descend(x)
        elif isinstance(node,dict):
            path=node.get("path") or node.get("filename")
            if path in KEY_FILES:
                if path in result:raise ValueError("Duplicate official file path")
                ident=node.get("id")
                link=node.get("_links",{}).get("stash:download",{}).get("href")
                if not link:
                    if type(ident) is not int:raise ValueError("Cannot derive requested file download")
                    link=f"/api/v2/files/{ident}/download"
                if not link.startswith("/api/v2/"):raise ValueError("Invalid file href")
                result[path]={"id":ident,"url":HOST+link}
            for x in node.values():descend(x)
    descend(obj)
    return result

def summarize_text(b):
    try:t=b.decode("utf-8-sig")
    except UnicodeDecodeError:
        t=b.decode("latin-1")
    lines=t.splitlines()
    if not lines:raise ValueError("Empty official file")
    sample=lines[:8]
    first_header=lines[0]
    sep="\t" if "\t" in first_header else ("," if "," in first_header else None)
    header=first_header.split(sep) if sep else [first_header]
    return {
        "lines":len(lines),"first8_original_lines":sample,
        "first_row_fields":header,
        "candidate_treatment_fields":[x for x in header if any(k in x.lower() for k in ("treatment","clam","lucinid","organic","sulfide","block"))],
        "text_parse_status":"HEADERS_AND_FIRST_ROWS_ONLY_NO_FACTORIAL_EFFECT",
    }

def report(fetcher=fetch):
    base={"schema":"tampa.lucinid_2020_field_original_source_preflight_v1",
          "doi":DOI,"source_status":"SOURCE_NOT_AVAILABLE","file_summaries":[]}
    try:
        metadata=json.loads(fetcher(DATASET_ENDPOINT))
        versions=href(metadata,"stash:version")
        manifest=json.loads(fetcher(versions+"/files"))
        registry=resolve_files(manifest)
        missing=[x for x in KEY_FILES if x not in registry]
        if missing:raise ValueError("Missing required original Dryad file: "+",".join(missing))
        entries=[]
        for filename in KEY_FILES:
            data=fetcher(registry[filename]["url"])
            entries.append({
                "file":filename,
                "download_url":registry[filename]["url"],
                "file_id":registry[filename]["id"],
                "bytes":len(data),
                "sha256":hashlib.sha256(data).hexdigest(),
                "preview":summarize_text(data),
            })
        base.update({
          "source_status":"ORIGINAL_FIELD_FILES_RETRIEVED_TREATMENT_MAPPING_NOT_FROZEN",
          "files_from_authoritative_version":entries,
          "file_summaries":[{"file":x["file"],"bytes":x["bytes"],"lines":x["preview"]["lines"]} for x in entries],
          "version_url":versions,
          "no_effect_estimators_fitted":True,
        })
    except (ValueError,KeyError,json.JSONDecodeError,urllib.error.URLError,OSError) as ex:
        base.update({
            "source_status":"OFFICIAL_SOURCE_OR_SCHEMA_STOP",
            "failure":f"{type(ex).__name__}: {str(ex)[:300]}",
            "no_effect_estimators_fitted":True,
        })
    return base

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    x=json.dumps(report(),sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(x,encoding="utf-8")
    else:print(x,end="")

if __name__=="__main__":main()
