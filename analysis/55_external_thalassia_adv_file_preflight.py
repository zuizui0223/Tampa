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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DOI="10.1594/PANGAEA.967585"
BASE="https://download.pangaea.de/dataset/967585/files/"
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"results/external_thalassia_hydrodynamic_preflight_v1.json"

def fetch(url):
    retry=Retry(
        total=6,
        connect=6,
        read=6,
        status=6,
        backoff_factor=2.0,
        status_forcelist=[429,500,502,503,504],
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    s=requests.Session()
    s.mount("https://",HTTPAdapter(max_retries=retry))
    r=s.get(
        url,
        headers={
            "User-Agent":"pangaeapy/1.1.3 Tampa-external-ADV",
            "Accept":"text/plain,*/*",
        },
        timeout=120,
        allow_redirects=True,
    )
    r.raise_for_status()
    return r.content

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(MANIFEST.read_text())
    selected=[]
    for x in manifest["catalogue"]["files"]:
        selected.append({
            "Binary":x["filename"],
            "Binary (Hash)":x["md5"],
            "Content":f"{x['component']}-dimension ADV velocity at {x['site']} site; selected from frozen PANGAEA manifest"
        })
    if len(selected)!=6:
        raise RuntimeError(f"frozen manifest drift: expected six ADV component files, found {len(selected)}")
    records=[]
    unavailable=[]
    for r in selected:
        name=r["Binary"]
        try:
            data=fetch(BASE+name)
        except requests.RequestException as exc:
            unavailable.append({"filename":name,"error":str(exc)})
            continue
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
        "status":(
            "all_label_selected_adv_components_downloaded_and_verified"
            if len(records)==len(selected)
            else "catalogue_fixed_binary_delivery_unavailable"
        ),
        "source":{
            "doi":DOI,
            "license":"CC-BY-4.0",
            "selection_rule":"all six ADV component files frozen in results/external_thalassia_hydrodynamic_preflight_v1.json from the response-independent PANGAEA catalogue",
            "manifest":"results/external_thalassia_hydrodynamic_preflight_v1.json",
        },
        "selected_file_count":len(selected),
        "downloaded_file_count":len(records),
        "unavailable_file_count":len(unavailable),
        "records":records,
        "unavailable":unavailable,
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
