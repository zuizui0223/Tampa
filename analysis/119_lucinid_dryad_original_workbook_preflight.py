#!/usr/bin/env python3
"""Read original Dryad Zostera-Loripes-Sulfide experiment workbook metadata.

Dryad version 19536 was obtained from the 2012 dataset's official API.
This first stage inspects sheets and a SMALL amount of header structure to
freeze factor and response definitions. It DOES NOT infer sample independence
or estimate scientific contrasts from an unmapped XLSX.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import urllib.request
import urllib.error
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT="https://datadryad.org"
VERSION_FILES=ROOT+"/api/v2/versions/19536/files"
EXPECTED="Experimental_data.xlsx"
MAX_BYTES=1_000_000
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def fetch(url):
    if not url.startswith(ROOT+"/api/v2/"):
        raise ValueError("Refuse off-site resource URL")
    req=urllib.request.Request(url,headers={
        "Accept-Encoding":"identity","User-Agent":"Tampa-2012-lucinid-dryad-experiment/1.0"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(MAX_BYTES+1)
    if len(b)>MAX_BYTES:raise ValueError("Source size exceeded")
    return b

def file_manifest(obj):
    if not isinstance(obj,dict):
        raise ValueError("Unexpected Dryad file-list schema")
    found=[]
    def descend(node):
        if isinstance(node,list):
            for v in node:descend(v)
        elif isinstance(node,dict):
            if node.get("path") == EXPECTED or node.get("filename") == EXPECTED:
                found.append(node)
            for v in node.values():descend(v)
    descend(obj)
    if len(found)!=1:raise ValueError(f"Expected one Dryad file named {EXPECTED}, got {len(found)}")
    one=found[0]
    href=one.get("_links",{}).get("stash:download",{}).get("href")
    if not href:
        # API is documented to return a files ID. This is a fallback using the ID,
        # NOT an invented external mirror.
        fid=one.get("id")
        if type(fid) is not int:raise ValueError("No original Dryad file ID")
        href=f"/api/v2/files/{fid}/download"
    if not href.startswith("/api/v2/"):
        raise ValueError("Unexpected Dryad download href")
    return {"file_id":one.get("id"),"path":one.get("path") or one.get("filename"),
            "download_url":ROOT+href,
            "raw_metadata_fields":sorted(one.keys())}

def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    r=ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join((t.text or "") for t in s.iter(NS+"t")) for s in r.iter(NS+"si")]

def cell_value(cell,strings):
    t=cell.get("t","")
    v=cell.find(NS+"v")
    if t=="s" and v is not None:
        idx=int(v.text)
        if idx<0 or idx>=len(strings):raise ValueError("Bad shared string index")
        return strings[idx]
    if t=="inlineStr":
        return "".join((t.text or "") for t in cell.iter(NS+"t"))
    return v.text if v is not None and v.text else ""

def workbook_outline(raw):
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Dryad file not valid XLSX ZIP")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        xml=ET.fromstring(z.read("xl/workbook.xml"))
        sheets=[x.attrib.get("name") for x in xml.iter(NS+"sheet")]
        strings=shared_strings(z)
        previews={}
        for path in sorted(x for x in names if re.match(r"xl/worksheets/sheet\d+\.xml$",x)):
            tree=ET.fromstring(z.read(path))
            rows=list(tree.iter(NS+"row"))
            preview=[]
            for row in rows[:10]:
                preview.append({
                    "row_number":row.get("r"),
                    "cells":{c.get("r",""):cell_value(c,strings)[:180]
                             for c in row.findall(NS+"c") if cell_value(c,strings)}
                })
            previews[path]={"nonempty_preview_rows_max10":preview,
                            "worksheet_xml_rows":len(rows)}
        return {"sheet_names":sheets,"worksheet_previews":previews,
                "shared_string_count":len(strings),
                "status":"FIRST_ROWS_FOR_FACTOR_MAPPING_ONLY_NO_EFFECT_FIT"}

def report(fetcher=fetch):
    try:
        b=fetcher(VERSION_FILES)
        listing=json.loads(b)
        file=file_manifest(listing)
        data=fetcher(file["download_url"])
        out={
            "schema":"tampa.dryad_lucinid_2012_original_workbook_preflight_v1",
            "status":"ORIGINAL_WORKBOOK_RETRIEVED_TREATMENT_MAPPING_REQUIRED",
            "dataset_doi":"10.5061/dryad.210mp",
            "publication_doi":"10.1126/science.1219973",
            "original_file_metadata":file,
            "original_xlsx_sha256":hashlib.sha256(data).hexdigest(),
            "original_xlsx_bytes":len(data),
            "workbook":workbook_outline(data),
            "inference_scope":"No plant biomass or sulfide effect until experimental factor/replicate columns and units are independently mapped from original workbook."
        }
    except (ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError, zipfile.BadZipFile, OSError) as e:
        out={"schema":"tampa.dryad_lucinid_2012_original_workbook_preflight_v1",
             "status":"OFFICIAL_SOURCE_OR_SCHEMA_BLOCKED",
             "reason":f"{type(e).__name__}: {str(e)[:280]}",
             "dataset_doi":"10.5061/dryad.210mp",
             "new_experimental_effects":None}
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    data=json.dumps(report(),ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(data,encoding="utf-8")
    else:print(data,end="")

if __name__=="__main__":main()
