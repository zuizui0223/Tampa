#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"deep_eml_contract.json").read_text())
OUT=ROOT/"deep_eml_result.json"

def local(tag): return tag.rsplit("}",1)[-1] if "}" in tag else tag
def clean(x): return re.sub(r"\s+"," ",str(x or "").strip())
def canon(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def subtree(e):
    rows=[]
    def walk(x,path):
        tag=local(x.tag)
        p=path+[tag]
        if x.text and clean(x.text):
            rows.append({"path":"/".join(p),"text":clean(x.text)})
        for k,v in sorted(x.attrib.items()):
            rows.append({"path":"/".join(p)+"/@"+k,"text":clean(v)})
        for ch in list(x):
            walk(ch,p)
    walk(e,[])
    return rows

def attr_name(e):
    for x in e.iter():
        if local(x.tag)=="attributeName" and x.text:
            return clean(x.text)
    return ""

def main():
    out={"schema":"tampa.nps_tier3_external_early_warning_v2.deep_eml_result","status":None,
         "response_csv_gets":0,"response_csv_bytes_opened":0,"response_values_opened":False}
    try:
        req=Request(C["source"]["metadata_xml_url"],headers={"Accept":"application/xml,text/xml","Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier3-v2-EML/1.0"})
        with urlopen(req,timeout=60) as r:
            if r.status!=200: raise RuntimeError(f"metadata_http_{r.status}")
            raw=r.read(5_000_001)
        if len(raw)>5_000_000: raise RuntimeError("metadata_too_large")
        root=ET.fromstring(raw)
        targets={}
        for e in root.iter():
            if local(e.tag)!="attribute": continue
            name=attr_name(e)
            if name in C["targets"]:
                targets[name]=subtree(e)
        missing=[x for x in C["targets"] if x not in targets]
        if missing: raise RuntimeError("target_attributes_missing:"+",".join(missing))
        def textblob(name):
            return " ".join(r["text"] for r in targets[name]).lower()
        checks={
            "quadrat_permanent":("permanent sampling location" in textblob("Quadrat")),
            "species_zm_code":("zostera marina" in textblob("Species") and "zm" in textblob("Species")),
            "percent_cover_percent_unit":("percent" in textblob("Percent Cover")),
            "percent_cover_missing_na":("na" in textblob("Percent Cover")),
            "date_defined":("date of the sampling event" in textblob("Date")),
        }
        # extract numeric bounds and missing codes from Percent Cover subtree
        pc=targets["Percent Cover"]
        mins=[r["text"] for r in pc if r["path"].endswith("/minimum")]
        maxs=[r["text"] for r in pc if r["path"].endswith("/maximum")]
        miss=[r["text"] for r in pc if "missingValueCode" in r["path"]]
        safe={
            "xml_bytes":len(raw),"xml_sha256":hashlib.sha256(raw).hexdigest(),
            "target_attributes":targets,"checks":checks,
            "percent_cover_numeric_minimums":mins,
            "percent_cover_numeric_maximums":maxs,
            "percent_cover_missing_value_codes":miss,
            "proposed_stable_unit":"Location::Transect::Quadrat",
            "focal_species_code":"ZM",
        }
        out["safe_eml_audit"]=safe
        out["safe_eml_fingerprint"]=canon(safe)
        failed=[k for k,v in checks.items() if not v]
        if failed:
            out["status"]="terminal_pre_response_deep_eml_stop"
            out["reason"]="failed:"+",".join(failed)
            out["next_gate"]="none"
        else:
            out["status"]="gate0_deep_eml_qualified"
            out["next_gate"]="freeze a narrower Zostera persistence/loss endpoint conditional on re-observation of the same permanent quadrat before opening CSV"
    except Exception as exc:
        out["status"]="terminal_pre_response_deep_eml_transport_or_parse_stop"
        out["reason"]=str(exc); out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
