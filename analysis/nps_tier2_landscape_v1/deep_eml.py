#!/usr/bin/env python3
"""Deep EML semantic gate for NPS Tier-2 cross-scale seagrass analysis."""
from __future__ import annotations
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"metadata_contract.json").read_text())
M=json.loads((ROOT/"metadata_result.json").read_text())
OUT=ROOT/"deep_eml_result.json"

def lname(tag): return tag.rsplit("}",1)[-1]
def t(el,path):
    x=el.find(path); return "" if x is None or x.text is None else x.text.strip()
def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def attr_record(a):
    rec={"attributeName":t(a,"attributeName"),"attributeDefinition":t(a,"attributeDefinition"),
         "enumerated":[],"numeric":{},"missing":[]}
    for e in a.iter():
        if lname(e.tag)=="codeDefinition":
            code=t(e,"code"); definition=t(e,"definition")
            if code or definition: rec["enumerated"].append({"code":code,"definition":definition})
        if lname(e.tag)=="numericDomain":
            rec["numeric"]={"numberType":t(e,"numberType"),
                            "minimum":t(e,"bounds/minimum"),
                            "maximum":t(e,"bounds/maximum")}
        if lname(e.tag)=="missingValueCode":
            code=t(e,"code"); ex=t(e,"codeExplanation")
            if code or ex: rec["missing"].append({"code":code,"codeExplanation":ex})
    return rec

def main():
    out={"schema":"tampa.nps_tier2_landscape_state_v1.deep_eml_result","status":None,
         "eml_gets":0,"csv_gets":0,"csv_bytes_opened":0,"response_values_opened":False}
    try:
        if M["status"]!="metadata_inventory_complete":
            raise RuntimeError("metadata_gate_not_complete")
        req=Request(C["source"]["eml_url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier2-DeepEML/1.0"})
        out["eml_gets"]+=1
        with urlopen(req,timeout=60) as r:
            if r.status!=200: raise RuntimeError(f"eml_http_{r.status}")
            raw=r.read(5_000_001)
        if len(raw)>5_000_000: raise RuntimeError("eml_too_large")
        observed_sha=hashlib.sha256(raw).hexdigest()
        if observed_sha!=M["safe_eml"]["eml_sha256"]:
            raise RuntimeError("eml_identity_drift")
        root=ET.fromstring(raw)
        wanted={}
        required={"Species","Percent_Cover","QuadratData_ID","Event_Code","Park_Code","Station","Quadrat_Ltr","Date","GPS_Accuracy_m"}
        for a in root.iter():
            if lname(a.tag)!="attribute": continue
            name=t(a,"attributeName")
            if name in required:
                wanted[name]=attr_record(a)
        missing=sorted(required-set(wanted))
        if missing: raise RuntimeError("missing_required_attributes:"+",".join(missing))
        safe={"eml_sha256":observed_sha,"attributes":wanted}
        out["safe_semantics"]=safe
        out["safe_semantics_fingerprint"]=canon(safe)
        out["status"]="deep_eml_inventory_complete"
        out["next_gate"]="freeze sampled-quadrat denominator, focal Zostera mapping, zero/missing rules and cross-scale trend estimands before CSV access"
    except Exception as exc:
        out["status"]="terminal_pre_response_deep_eml_stop"
        out["reason"]=str(exc); out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
