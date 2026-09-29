#!/usr/bin/env python3
"""Fetch the complete external ADV velocity subset from PANGAEA 967585.

Selection is response-independent and exhaustive: all binary rows whose filename and
content label identify an ADV velocity component are downloaded. MD5 is checked
against the curated PANGAEA index. This stage inventories format before analysis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import requests

DOI="10.1594/PANGAEA.967585"
INDEX_URL=f"https://doi.org/{DOI}"
BASE="https://download.pangaea.de/dataset/967585/files/"

def fetch(url):
    r=requests.get(url,headers={"User-Agent":"Tampa-external-ADV/1.0"},timeout=120,allow_redirects=True)
    r.raise_for_status()
    return r.content

def parse_index(text):
    lines=text.splitlines()
    header_i=next(i for i,x in enumerate(lines) if x.startswith("Binary\tContent\t"))
    reader=csv.DictReader(io.StringIO("\n".join(lines[header_i:])),delimiter="\t")
    return list(reader)

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    idx=requests.get(
        INDEX_URL,
        headers={"Accept":"text/tab-separated-values","User-Agent":"Tampa-external-ADV/1.0"},
        timeout=120,allow_redirects=True,
    )
    idx.raise_for_status()
    rows=parse_index(idx.text)
    selected=[
        r for r in rows
        if "ADV" in r["Binary"] and "velocity measured from an ADV" in r["Content"]
    ]
    if len(selected)!=6:
        raise RuntimeError(f"expected exactly six ADV component files, found {len(selected)}")
    records=[]
    for r in selected:
        name=r["Binary"]
        data=fetch(BASE+name)
        md5=hashlib.md5(data).hexdigest()
        if md5!=r["Binary (Hash)"]:
            raise RuntimeError(f"MD5 mismatch {name}: {md5} != {r['Binary (Hash)']}")
        (outdir/name).write_bytes(data)
        text=data.decode("utf-8",errors="replace")
        lines=text.splitlines()
        records.append({
            "filename":name,
            "content":r["Content"],
            "bytes":len(data),
            "md5":md5,
            "line_count":len(lines),
            "head_lines":lines[:40],
        })
    result={
        "schema":"tampa.external_thalassia_adv_file_preflight_v1",
        "status":"all_label_selected_adv_components_downloaded_and_verified",
        "source":{
            "doi":DOI,
            "license":"CC-BY-4.0",
            "selection_rule":"all index rows with ADV in filename and exact content phrase 'velocity measured from an ADV'",
        },
        "selected_file_count":len(selected),
        "records":records,
        "claim_boundary":[
            "All six XYZ component files from both barren and vegetated sites are retained.",
            "No file is selected or excluded based on observed velocity direction or magnitude.",
            "This stage inspects file structure only; ecological effect estimation is deferred until parsing rules are frozen."
        ],
    }
    (outdir/"external_thalassia_adv_file_preflight_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_external_hydro"))
    a=p.parse_args(); main(a.out)
