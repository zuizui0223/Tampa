#!/usr/bin/env python3
"""Inspect source-verified Posidonia nitrogen-fixing symbiont XLSX tables.

Mohr et al. (2021) Nature DOI 10.1038/s41586-021-04063-4.
Only source Data Fig 1 and Fig 2 workbooks. Dataset-level source SHA
and XLSX structure are verified. This reader returns limited first
nonempty lines and numeric column coverage to determine estimable
time/plant contrasts; it does not infer a nitrogen x light manipulation.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

FILES={
    "figure1":{
        "url":"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-021-04063-4/MediaObjects/41586_2021_4063_MOESM8_ESM.xlsx",
        "sha256":"187dd85a1308c18216c3d2ed09a28530cfd9355072a9d3c7e425c52727d7a69b",
        "expected_sheet":"Figure 1"
    },
    "figure2":{
        "url":"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-021-04063-4/MediaObjects/41586_2021_4063_MOESM9_ESM.xlsx",
        "sha256":"877242abb476cb2d933048778037f8eaf53435e346be42adf327d4af75c7156b",
        "expected_sheet":"Figure 2"
    },
}
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def fetch(url):
    if not url.startswith("https://media.springernature.com/original/springer-static/esm/"):
        raise ValueError("Unexpected Nature source host")
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-posidonia-N2-source/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=90) as r:b=r.read(500001)
    if len(b)>500000:raise ValueError("Source workbook exceeds cap")
    return b

def unpack(raw):
    if not zipfile.is_zipfile(io.BytesIO(raw)):raise ValueError("Source was not XLSX")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        strings=[]
        if "xl/sharedStrings.xml" in names:
            tree=ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings=["".join((t.text or "") for t in e.iter(NS+"t")) for e in tree.iter(NS+"si")]
        main=ET.fromstring(z.read("xl/workbook.xml"))
        sheetnames=[x.get("name","") for x in main.iter(NS+"sheet")]
        sheets={}
        for name in names:
            if not re.match(r"xl/worksheets/sheet\d+\.xml$",name):continue
            root=ET.fromstring(z.read(name))
            rows=[]
            for xmlrow in root.iter(NS+"row"):
                cells={}
                for cell in xmlrow.findall(NS+"c"):
                    typ=cell.get("t","")
                    v=cell.find(NS+"v")
                    if typ=="s" and v is not None:
                        value=strings[int(v.text)]
                    elif typ=="inlineStr":
                        value="".join((t.text or "") for t in cell.iter(NS+"t"))
                    else:
                        value=v.text if v is not None and v.text else ""
                    if value:cells[cell.get("r","")]=value
                rows.append({"row":xmlrow.get("r"),"cells":cells})
            sheets[name]=rows
        return sheetnames,sheets

def inspect_one(name,raw):
    spec=FILES[name]
    if hashlib.sha256(raw).hexdigest()!=spec["sha256"]:
        raise ValueError(f"Original Nature source digest drift for {name}")
    titles,sheets=unpack(raw)
    if titles!=[spec["expected_sheet"]] or len(sheets)!=1:
        raise ValueError("Unexpected workbook sheets")
    sheet=next(iter(sheets.values()))
    first=[x for x in sheet if x["cells"]][:25]
    return {
        "source_file":name,"sha256":spec["sha256"],"file_bytes":len(raw),
        "sheet_names":titles,
        "source_sheet_row_count":len(sheet),
        "first25_nonempty_source_rows_for_factor_mapping":first,
        "unmapped_status":"ORIGINAL_VALUES_INSPECTED_NO_INFERENTIAL_COMPARISON",
    }

def report(fetcher=fetch):
    rows={}
    for name in FILES:
        spec=FILES[name]
        try:
            b=fetcher(spec["url"])
            rows[name]=inspect_one(name,b)
        except (ValueError,OSError,TimeoutError,KeyError,IndexError) as exc:
            rows[name]={"source_file":name,"status":"RETRIEVAL_OR_SCHEMA_STOP","reason":str(exc)[:300]}
    return {
        "schema":"tampa.posidonia_nfix_original_source_data_factor_gate_v1",
        "evidence_class":"published_plant_isotope_data_preflight_not_new_physiological_mechanism",
        "source_paper":"10.1038/s41586-021-04063-4",
        "files":rows,
        "claim_limits":[
            "Data columns are not automatically independent biological plant replicates.",
            "Figure 1/2 data can encode root sections and isotope technical replicates.",
            "Seasonal observational contrasts are not a randomized nitrogen-by-light interaction.",
            "No root symbiont cost/benefit estimate or direct Thalassia transfer inferred.",
            "No 2026 untouched validation from previously published Nature data.",
        ],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    s=json.dumps(report(),ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
