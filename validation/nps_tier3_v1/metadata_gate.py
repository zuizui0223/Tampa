#!/usr/bin/env python3
"""Metadata-only EML qualification for NPS Tier-3 seagrass external validation v1."""
from __future__ import annotations
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"metadata_contract.json").read_text())
OUT=ROOT/"metadata_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def local(tag):
    return tag.rsplit("}",1)[-1] if "}" in tag else tag

def txt(e,name):
    for x in e.iter():
        if local(x.tag)==name and x.text:
            return re.sub(r"\s+"," ",x.text.strip())
    return ""

def main():
    out={"schema":"tampa.nps_tier3_external_early_warning_v1.metadata_result",
         "status":None,"response_csv_gets":0,"response_csv_bytes_opened":0,"response_values_opened":False}
    try:
        req=Request(C["source"]["metadata_xml_url"],headers={"Accept":"application/xml,text/xml","Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier3-Metadata/1.0"})
        with urlopen(req,timeout=60) as r:
            if r.status!=200: raise RuntimeError(f"metadata_http_{r.status}")
            raw=r.read(5_000_001)
        if len(raw)>5_000_000: raise RuntimeError("metadata_too_large")
        root=ET.fromstring(raw)
        attrs=[]
        for e in root.iter():
            if local(e.tag)!="attribute": continue
            name=txt(e,"attributeName")
            definition=txt(e,"attributeDefinition")
            unit=txt(e,"standardUnit") or txt(e,"customUnit")
            missing=[]
            for x in e.iter():
                if local(x.tag) in {"code","codeDefinition","missingValueCode"} and x.text:
                    missing.append(re.sub(r"\s+"," ",x.text.strip()))
            attrs.append({"name":name,"definition":definition,"unit":unit,"codes":missing})
        physical=[]
        for e in root.iter():
            if local(e.tag)=="dataTable":
                physical.append({
                    "entityName":txt(e,"entityName"),
                    "entityDescription":txt(e,"entityDescription"),
                    "objectName":txt(e,"objectName"),
                    "url":txt(e,"url"),
                    "numberOfRecords":txt(e,"numberOfRecords"),
                })
        alltext=(" ".join(
            [a["name"]+" "+a["definition"]+" "+a["unit"]+" "+" ".join(a["codes"]) for a in attrs]
            +[json.dumps(x) for x in physical]
        )).lower()
        semantics={
            "stable_unit":any(k in alltext for k in ("station","site id","siteid","transect","plot","location id","sample location")),
            "time":any(k in alltext for k in ("year","date","sample date","sampling date")),
            "park_or_region":any(k in alltext for k in ("park","asis","caco","fiis","location")),
            "species":any(k in alltext for k in ("species","taxon","zostera","ruppia")),
            "quantitative_state":any(k in alltext for k in ("percent cover","cover abundance","abundance","braun","frequency")),
            "zero_or_missing_text":any(k in alltext for k in ("missing","no data","nodata","not collected","not sampled","zero","absent","absence")),
            "data_table_declared":bool(physical),
        }
        safe={"xml_bytes":len(raw),"xml_sha256":hashlib.sha256(raw).hexdigest(),
              "attributes":attrs,"data_tables":physical,"semantic_screen":semantics}
        out["safe_metadata"]=safe
        out["safe_metadata_fingerprint"]=canon(safe)
        missing=[k for k,v in semantics.items() if not v]
        if missing:
            out["status"]="terminal_pre_response_metadata_semantics_stop"
            out["reason"]="missing:"+",".join(missing)
            out["next_gate"]="none"
        else:
            out["status"]="gate0_metadata_semantics_qualified"
            out["next_gate"]="inspect only frozen metadata attributes; freeze exact focal taxon, annual-state parser, zero/missing rule and once-only response runner before CSV access"
    except Exception as exc:
        out["status"]="terminal_pre_response_metadata_transport_or_parse_stop"
        out["reason"]=str(exc); out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
