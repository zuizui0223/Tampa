#!/usr/bin/env python3
"""Public original-data preflight for seagrass interaction experiments.

The sources were discovered from their official article/dataset pages.
Data are explicitly RESPONSE-OPEN EXPLORATORY, not untouched validation.
This program does not infer an effect without a stable treatment/outcome schema.
Source retrieval failures become explicit individual STOP records; they never
convert a missing experiment into a neutral or positive ecological outcome.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

SOURCES={
 "ZEN_2011_multi_site":"https://datadocs.bco-dmo.org/dataset/659737/file/2GGXP4qs6jo9x0/ZEN.csv",
 "lucinid_2012_dryad":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.210mp",
 "Posidonia_N2_2021_figure1":"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-021-04063-4/MediaObjects/41586_2021_4063_MOESM8_ESM.xlsx",
 "Posidonia_N2_2021_figure2":"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-021-04063-4/MediaObjects/41586_2021_4063_MOESM9_ESM.xlsx",
}
MAX_BYTES=5_000_000


def fetch(url:str,max_bytes=MAX_BYTES)->bytes:
    if not url.startswith("https://"):
        raise ValueError("Non-HTTPS remote source forbidden")
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-seagrass-interaction-response-open/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=90) as response:
        data=response.read(max_bytes+1)
    if len(data)>max_bytes:
        raise ValueError("Source file exceeds declared cap")
    return data


def csv_metadata(blob:bytes)->dict:
    text=blob.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text),delimiter=",")
    if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames):
        raise ValueError("Missing/duplicate CSV headers")
    rows=list(reader)
    if any(None in row for row in rows):
        raise ValueError("Malformed CSV record")
    headers=reader.fieldnames
    keys={
        "possible_site_fields":[x for x in headers if re.search(r"site|location|station",x,re.I)],
        "possible_factor_fields":[x for x in headers if re.search(r"fertil|nutrient|deterrent|grazer|treatment|carbaryl",x,re.I)],
        "possible_response_fields":[x for x in headers if re.search(r"biomass|biom|alga|epiphyt|shoot|eelgrass|cover",x,re.I)],
    }
    site_fields=keys["possible_site_fields"]
    return {
        "row_count":len(rows),"column_count":len(headers),"field_names":headers,
        "candidate_columns":keys,
        "site_label_uniques":{k:len({str(r.get(k,"")).strip() for r in rows if str(r.get(k,"")).strip()})
                             for k in site_fields},
        "candidate_factor_level_counts":{
            k:dict(Counter(str(r.get(k,"")).strip() for r in rows if str(r.get(k,"")).strip()).most_common(12))
            for k in keys["possible_factor_fields"]
        },
        "row_level_design_status":"OUTCOME_SCHEMA_NOT_PREDECLARED_NO_EFFECT_FIT",
        "source_independence_boundary":"Plots nested in sites; 2015 published analysis uses 15 treatment sites, while this public dataset page describes 16 sites.",
    }


def xlsx_metadata(blob:bytes)->dict:
    if not zipfile.is_zipfile(io.BytesIO(blob)):
        raise ValueError("Expected workbook ZIP container")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=z.namelist()
        if "xl/workbook.xml" not in names:
            raise ValueError("Missing xl/workbook.xml")
        root=ET.fromstring(z.read("xl/workbook.xml"))
        ns="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        sheets=[
            {"name":x.attrib.get("name",""),"state":x.attrib.get("state","visible")}
            for x in root.iter(ns+"sheet")
        ]
        rowcounts={}
        for name in sorted(x for x in names if re.match(r"xl/worksheets/sheet\d+\.xml$",x)):
            xml=ET.fromstring(z.read(name))
            rows=sum(1 for _ in xml.iter(ns+"row"))
            rowcounts[name]=rows
        return {
            "sheets":sheets,"worksheet_xml_row_counts_including_headers":rowcounts,
            "sheet_count":len(sheets),
            "parse_status":"WORKBOOK_STRUCTURE_ONLY_OUTCOME_COLUMNS_NOT_MAPPED",
            "scope":"No xlsx workbook data values exported or treatment contrasts estimated at preflight.",
        }


def dryad_metadata(blob:bytes)->dict:
    data=json.loads(blob)
    if not isinstance(data,dict):
        raise ValueError("Unexpected Dryad API payload")
    links=data.get("_links") or {}
    names=sorted(data.keys())
    def redacted_href(x):
        if isinstance(x,dict):
            return x.get("href","")
        if isinstance(x,str):
            return x
        return ""
    return {
        "field_names":names,
        "title":data.get("title"),
        "version_number":data.get("versionNumber") or data.get("version"),
        "related_links":{k:redacted_href(v) for k,v in links.items()
                         if re.search(r"files|version|download",k,re.I)},
        "status":"DATASET_API_METADATA_ONLY_EXPERIMENTAL_XLSX_NOT_YET_READ",
        "expected_file":"Experimental_data.xlsx",
    }


def probe_source(name:str,url:str,fetcher=fetch)->dict:
    record={"name":name,"url":url,"evidence_class":"external_response_open_exploratory_not_heldout"}
    try:
        b=fetcher(url)
        record["bytes"]=len(b)
        record["sha256"]=hashlib.sha256(b).hexdigest()
        if name.endswith("_dryad"):record["data"]=dryad_metadata(b)
        elif name.startswith("ZEN"):record["data"]=csv_metadata(b)
        else:record["data"]=xlsx_metadata(b)
        record["status"]="SOURCE_RETRIEVED_METADATA_PROFILED"
    except (ValueError,UnicodeError,json.JSONDecodeError,zipfile.BadZipFile,
            urllib.error.URLError,TimeoutError,OSError) as e:
        record["status"]="SOURCE_ACCESS_OR_SCHEMA_STOP"
        record["reason"]=f"{type(e).__name__}: {str(e)[:280]}"
        record["new_biological_effect_estimated"]=False
    return record


def report(fetcher=fetch):
    return {
        "schema":"tampa.six_seagrass_interactions_external_data_preflight_v1",
        "source_probe_results":[probe_source(k,v,fetcher=fetcher) for k,v in SOURCES.items()],
        "strict_boundaries":[
            "Source failure is non-estimable and is never counted as a zero effect.",
            "ZEN plot measurements are clustered by site and have a factorial design, not independent global study replications.",
            "Dryad API metadata is not a numerical analysis of the experimental workbook.",
            "Nature Source Data workbook structures are not calibrated effect estimates.",
            "The studies are already published results, not independent untouched predictive holdouts.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    s=json.dumps(report(),sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
