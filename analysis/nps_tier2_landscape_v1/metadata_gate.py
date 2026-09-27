#!/usr/bin/env python3
"""Metadata-only EML gate for NPS Tier-2 landscape-state analysis."""
from __future__ import annotations
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"metadata_contract.json").read_text())
OUT=ROOT/"metadata_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def local(tag):
    return tag.rsplit("}",1)[-1]

def txt(el,path):
    x=el.find(path)
    return "" if x is None or x.text is None else x.text.strip()

def main():
    out={
      "schema":"tampa.nps_tier2_landscape_state_v1.metadata_result",
      "status":None,
      "eml_gets":0,
      "csv_gets":0,
      "csv_bytes_opened":0,
      "response_values_opened":False
    }
    try:
        req=Request(C["source"]["eml_url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier2-EML/1.0"})
        out["eml_gets"]+=1
        with urlopen(req,timeout=60) as r:
            if r.status!=200: raise RuntimeError(f"eml_http_{r.status}")
            raw=r.read(5_000_001)
        if len(raw)>5_000_000: raise RuntimeError("eml_too_large")
        root=ET.fromstring(raw)
        entities=[]
        attributes=[]
        for dt in root.iter():
            if local(dt.tag)!="dataTable": continue
            ent={
              "entityName":txt(dt,"entityName"),
              "entityDescription":txt(dt,"entityDescription"),
              "physicalName":txt(dt,"physical/physicalName")
            }
            entities.append(ent)
            al=dt.find("attributeList")
            if al is None: continue
            for a in list(al):
                if local(a.tag)!="attribute": continue
                rec={
                  "entityName":ent["entityName"],
                  "attributeName":txt(a,"attributeName"),
                  "attributeLabel":txt(a,"attributeLabel"),
                  "attributeDefinition":txt(a,"attributeDefinition"),
                  "measurementScaleType":"",
                  "missingValues":[]
                }
                ms=a.find("measurementScale")
                if ms is not None and len(list(ms)):
                    rec["measurementScaleType"]=local(list(ms)[0].tag)
                mv=a.find("missingValueCode")
                if mv is not None:
                    rec["missingValues"]=[
                      {
                        "code":txt(x,"code"),
                        "codeExplanation":txt(x,"codeExplanation")
                      }
                      for x in list(mv) if local(x.tag)=="code"
                    ]
                    # Some EML puts multiple missingValueCode siblings rather than nested.
                # generic scan for all descendant missing-value codes
                mvs=[]
                for m in a.iter():
                    if local(m.tag)=="missingValueCode":
                        code=txt(m,"code"); exp=txt(m,"codeExplanation")
                        if code or exp: mvs.append({"code":code,"codeExplanation":exp})
                if mvs: rec["missingValues"]=mvs
                attributes.append(rec)
        if not attributes: raise RuntimeError("no_attribute_dictionary")
        safe={
          "eml_bytes":len(raw),
          "eml_sha256":hashlib.sha256(raw).hexdigest(),
          "entities":entities,
          "attributes":attributes
        }
        out["safe_eml"]=safe
        out["safe_eml_fingerprint"]=canon(safe)
        out["status"]="metadata_inventory_complete"
        out["next_gate"]="map park/time/unit/species/cover/missing semantics from EML only; do not open CSV yet"
    except Exception as exc:
        out["status"]="terminal_pre_response_metadata_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
