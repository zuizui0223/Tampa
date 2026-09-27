#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
INV=json.loads((ROOT/"metadata_schema_result.json").read_text())
C=json.loads((ROOT/"fgdc_schema_contract.json").read_text())
OUT=ROOT/"fgdc_schema_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def txt(el,path):
    x=el.find(path)
    return "" if x is None or x.text is None else x.text.strip()

def main():
    out={"schema":"tampa.alaska_eelgrass_external_early_warning_v2.fgdc_schema_result","status":None,"response_csv_gets":0,"response_csv_bytes_opened":0,"response_values_opened":False}
    try:
        if INV["fingerprint"]!=C["requires_metadata_inventory_fingerprint"]:
            raise RuntimeError("metadata_inventory_fingerprint_mismatch")
        spec=C["metadata_xml"]
        req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-Alaska-Eelgrass-v2-FGDC/1.0"})
        with urlopen(req,timeout=60) as resp:
            if resp.status!=200: raise RuntimeError(f"fgdc_http_{resp.status}")
            raw=resp.read(int(spec["size"])+1)
        if len(raw)!=int(spec["size"]): raise RuntimeError(f"fgdc_size_mismatch:{len(raw)}")
        if hashlib.md5(raw).hexdigest()!=spec["md5"]: raise RuntimeError("fgdc_md5_mismatch")
        root=ET.fromstring(raw)
        entities=[]
        for ent in root.findall(".//detailed"):
            entity={"label":txt(ent,"enttyp/enttypl"),"definition":txt(ent,"enttyp/enttypd"),"attributes":[]}
            for a in ent.findall("attr"):
                domains=[]
                for e in a.findall(".//edom"):
                    domains.append({"value":txt(e,"edomv"),"definition":txt(e,"edomvd")})
                for r in a.findall(".//rdom"):
                    domains.append({"range_min":txt(r,"rdommin"),"range_max":txt(r,"rdommax"),"units":txt(r,"attrunit")})
                entity["attributes"].append({"label":txt(a,"attrlabl"),"definition":txt(a,"attrdef"),"source":txt(a,"attrdefs"),"domains":domains})
            if entity["label"] or entity["attributes"]: entities.append(entity)
        processes=[]
        for p in root.findall(".//procstep"):
            processes.append({"description":txt(p,"procdesc"),"date":txt(p,"procdate")})
        quality={
            "logic":txt(root,".//logic"),
            "complete":txt(root,".//complete"),
            "horizontal":txt(root,".//horizpar"),
            "vertical":txt(root,".//vertacc"),
        }
        safe={"entities":entities,"process_steps":processes,"data_quality":quality}
        out["fgdc_md5"]=spec["md5"]
        out["safe_schema"]=safe
        out["safe_schema_fingerprint"]=canon(safe)
        labels=[a["label"] for e in entities for a in e["attributes"]]
        defs=" ".join((a["label"]+" "+a["definition"]).lower() for e in entities for a in e["attributes"])
        # This is only a semantic screen; exact parser mapping is frozen manually from the emitted metadata.
        has_time=any(k in defs for k in ["year","date","time"])
        has_unit=any(k in defs for k in ["transect","site","station","location"])
        has_cover=("zostera" in defs or "eelgrass" in defs) and ("percent" in defs and "cover" in defs)
        out["semantic_screen"]={"has_time_semantics":has_time,"has_repeated_unit_semantics":has_unit,"has_zostera_percent_cover_semantics":has_cover,"attribute_labels":labels}
        if not (has_time and has_unit and has_cover):
            out["status"]="terminal_pre_response_schema_semantics_stop"
            out["reason"]="official_fgdc_metadata_does_not_unambiguously_supply_all_required_semantics"
            out["next_gate"]="none"
        else:
            out["status"]="fgdc_schema_qualified"
            out["next_gate"]="freeze exact CSV parser, annual-state construction, estimability and once-only outcome runner before any CSV GET"
    except Exception as exc:
        out["status"]="terminal_pre_response_fgdc_transport_or_parse_stop"; out["reason"]=str(exc); out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
