#!/usr/bin/env python3
"""NOAA ISO-metadata gate for Texas seagrass external validation v2.

Only the official ISO metadata XML is fetched. Distribution URLs are inventoried
but never followed. No biological data/archive body is requested.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"iso_metadata_contract.json").read_text())
OUT=ROOT/"iso_metadata_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def norm(s):
    return re.sub(r"\s+"," ",str(s or "")).strip()

def local(tag):
    return tag.rsplit("}",1)[-1] if "}" in tag else tag

def main():
    out={
        "schema":"tampa.texas_seagrass_external_early_warning_v2.iso_metadata_result",
        "status":None,
        "raw_data_or_archive_gets":0,
        "raw_data_or_archive_bytes_opened":0,
        "response_values_opened":False,
    }
    try:
        url=C["source"]["iso_metadata_url"]
        req=Request(url,headers={"Accept":"application/xml,text/xml","Accept-Encoding":"identity","User-Agent":"Tampa-Texas-Seagrass-v2-ISO/1.0"})
        with urlopen(req,timeout=60) as r:
            if r.status!=200:
                raise RuntimeError(f"iso_metadata_http_{r.status}")
            raw=r.read(3_000_001)
        if len(raw)>3_000_000:
            raise RuntimeError("iso_metadata_too_large")
        root=ET.fromstring(raw)
        texts=[]
        urls=[]
        semantic_records=[]
        wanted=("station","site","year","date","species","seagrass","percent cover","cover","absence","absent","zero","missing","no data","no_data","thalas","halodule")
        for elem in root.iter():
            txt=norm(elem.text)
            if txt:
                texts.append(txt)
                low=txt.lower()
                if any(k in low for k in wanted):
                    semantic_records.append({"element":local(elem.tag),"text":txt[:1000]})
                if txt.startswith(("http://","https://","ftp://")):
                    urls.append(txt)
        joined=" ".join(texts).lower()
        requirements={
            "accession_identity":("0181898" in joined),
            "fixed_station_semantics":("permanent station" in joined or "fixed station" in joined),
            "multiyear_semantics":("2011" in joined and ("2023" in joined or "2018" in joined)),
            "percent_cover_semantics":("percent cover" in joined),
            "species_semantics":("thlassia testudinum" in joined or "thalassia testudinum" in joined or "halodule wrightii" in joined or "seagrass" in joined),
        }
        distribution_urls=[]
        seen=set()
        for u in urls:
            if u not in seen:
                seen.add(u)
                distribution_urls.append(u)
        # URLs are metadata only here; none are followed.
        candidate_data_urls=[u for u in distribution_urls if any(x in u.lower() for x in ("download","archive","accession","ftp","data"))]
        safe={
            "iso_metadata_url":url,
            "iso_metadata_bytes":len(raw),
            "iso_metadata_sha256":hashlib.sha256(raw).hexdigest(),
            "requirements":requirements,
            "semantic_records":semantic_records[:300],
            "distribution_urls":distribution_urls[:200],
            "candidate_data_urls":candidate_data_urls[:100],
        }
        out["safe_metadata"]=safe
        out["safe_metadata_fingerprint"]=canon(safe)
        failed=[k for k,v in requirements.items() if not v]
        if failed:
            out["status"]="terminal_pre_response_iso_semantics_stop"
            out["reason"]="missing:"+",".join(failed)
            out["next_gate"]="none"
        elif not candidate_data_urls:
            out["status"]="terminal_pre_response_distribution_identity_stop"
            out["reason"]="no_official_distribution_url_in_iso_metadata"
            out["next_gate"]="none"
        else:
            out["status"]="gate0_iso_metadata_qualified"
            out["next_gate"]="inspect only the frozen ISO inventory; select and freeze a response-independent schema/data-dictionary source before any biological data file is opened"
    except Exception as exc:
        out["status"]="terminal_pre_response_iso_metadata_transport_or_parse_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
