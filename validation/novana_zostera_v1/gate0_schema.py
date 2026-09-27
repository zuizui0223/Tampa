#!/usr/bin/env python3
"""Response-blind WFS DescribeFeatureType gate for Danish NOVANA eelgrass.

This gate must never issue GetFeature and never inspect biological rows.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"gate0_schema_contract.json").read_text())
OUT=ROOT/"gate0_schema_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def lname(tag):
    return tag.rsplit("}",1)[-1]

def main():
    state={
      "schema":"tampa.novana_zostera_external_early_warning_v1.gate0_schema_result",
      "status":None,
      "describe_feature_type_requests":0,
      "get_feature_requests":0,
      "csv_download_requests":0,
      "biological_feature_rows_opened":0,
      "response_values_opened":False,
    }
    try:
        q=urlencode({
          "service":"WFS",
          "version":"2.0.0",
          "request":"DescribeFeatureType",
          "typeNames":C["source"]["type_name"],
        })
        url=C["source"]["wfs_endpoint"]+"?"+q
        req=Request(url,headers={"Accept":"application/xml,text/xml","Accept-Encoding":"identity","User-Agent":"Tampa-NOVANA-Gate0/1.0"})
        state["describe_feature_type_requests"]+=1
        with urlopen(req,timeout=60) as r:
            if r.status!=200:
                raise RuntimeError(f"describe_feature_type_http_{r.status}")
            raw=r.read(2_000_001)
        if len(raw)>2_000_000:
            raise RuntimeError("describe_feature_type_too_large")
        root=ET.fromstring(raw)
        elements=[]
        for el in root.iter():
            if lname(el.tag)!="element":
                continue
            name=el.attrib.get("name")
            typ=el.attrib.get("type")
            if name:
                elements.append({
                  "name":name,
                  "type":typ or "",
                  "minOccurs":el.attrib.get("minOccurs",""),
                  "maxOccurs":el.attrib.get("maxOccurs",""),
                  "nillable":el.attrib.get("nillable",""),
                })
        # preserve order but drop exact duplicates
        uniq=[]
        seen=set()
        for rec in elements:
            key=(rec["name"],rec["type"],rec["minOccurs"],rec["maxOccurs"],rec["nillable"])
            if key not in seen:
                seen.add(key); uniq.append(rec)
        if not uniq:
            raise RuntimeError("no_xsd_elements_found")
        safe={
          "request_url":url,
          "response_bytes":len(raw),
          "response_sha256":hashlib.sha256(raw).hexdigest(),
          "element_count":len(uniq),
          "elements":uniq,
        }
        state["safe_schema"]=safe
        state["safe_schema_fingerprint"]=canon(safe)
        state["status"]="gate0_schema_inventory_complete"
        state["next_gate"]="map required semantic roles using only this schema plus official dataset documentation; do not issue GetFeature yet"
    except Exception as exc:
        state["status"]="terminal_pre_response_schema_transport_or_parse_stop"
        state["reason"]=str(exc)
        state["next_gate"]="none"
    state["fingerprint"]=canon(state)
    OUT.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    print(json.dumps(state,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
