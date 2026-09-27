#!/usr/bin/env python3
"""Metadata-only Gate0 for Texas seagrass external validation v1.

Fetches only NCEI accession descriptive HTML and the download-index HTML.
It never follows a data/archive link.
"""
from __future__ import annotations
import hashlib, html, json, re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"gate0_contract.json").read_text())
OUT=ROOT/"gate0_result.json"

DETAILS="https://www.ncei.noaa.gov/archive/archive-management-system/OAS/bin/prd/jquery/accession/details/181898/11"
INDEX="https://www.ncei.noaa.gov/archive/accession/download/181898"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def fetch_text(url):
    req=Request(url,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-Texas-Seagrass-Gate0/1.0"})
    with urlopen(req,timeout=60) as r:
        if r.status!=200:
            raise RuntimeError(f"http_{r.status}:{url}")
        raw=r.read(5_000_001)
    if len(raw)>5_000_000:
        raise RuntimeError("metadata_page_too_large")
    return raw.decode("utf-8","strict"),len(raw)

def visible_text(s):
    s=re.sub(r"(?is)<script.*?</script>|<style.*?</style>"," ",s)
    s=re.sub(r"(?s)<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",html.unescape(s)).strip()

def link_inventory(s):
    out=[]
    for m in re.finditer(r'(?is)<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',s):
        href=html.unescape(m.group(1)).strip()
        label=visible_text(m.group(2))
        low=(href+" "+label).lower()
        if any(tok in low for tok in (".csv",".zip",".txt",".xml",".json",".xlsx",".xls","download","archive")):
            out.append({"label":label[:300],"href":href[:1000]})
    # deterministic unique
    seen=set(); uniq=[]
    for x in out:
        key=(x["label"],x["href"])
        if key not in seen:
            seen.add(key); uniq.append(x)
    return uniq

def main():
    state={
        "schema":"tampa.texas_seagrass_external_early_warning_v1.gate0_result",
        "status":None,
        "raw_data_file_gets":0,
        "raw_data_bytes_opened":0,
        "response_values_opened":False,
    }
    try:
        details,db=fetch_text(DETAILS)
        index,ib=fetch_text(INDEX)
        dt=visible_text(details)
        it=visible_text(index)
        alltxt=(dt+" "+it).lower()
        requirements={
            "accession_identity":("0181898" in alltxt),
            "permanent_station_semantics":("permanent station" in alltxt or "fixed station" in alltxt),
            "multiyear_dates":("2011" in alltxt and ("2023" in alltxt or "2018" in alltxt)),
            "percent_cover":("percent cover" in alltxt),
            "csv_or_archive_description":(".csv" in alltxt or "csv format" in alltxt or "download" in alltxt),
        }
        links=link_inventory(index)
        candidate_links=[x for x in links if any(t in (x["href"]+" "+x["label"]).lower() for t in (".csv",".zip",".txt",".xlsx",".xls","archive","download"))]
        requirements["candidate_link_inventory_nonempty"]=bool(candidate_links)
        safe={
            "details_url":DETAILS,
            "download_index_url":INDEX,
            "details_bytes":db,
            "download_index_bytes":ib,
            "details_text_excerpt":dt[:5000],
            "download_index_text_excerpt":it[:5000],
            "candidate_link_inventory":candidate_links[:100],
            "requirements":requirements,
        }
        state["safe_metadata"]=safe
        state["safe_metadata_fingerprint"]=canon(safe)
        if not all(requirements.values()):
            state["status"]="terminal_pre_response_metadata_qualification_stop"
            state["reason"]="failed:"+",".join(k for k,v in requirements.items() if not v)
            state["next_gate"]="none"
        else:
            state["status"]="gate0_metadata_qualified"
            state["next_gate"]="freeze exactly one official response/archive identity and a schema-only route before opening any biological row/value"
    except Exception as exc:
        state["status"]="terminal_pre_response_metadata_transport_or_parse_stop"
        state["reason"]=str(exc)
        state["next_gate"]="none"
    state["fingerprint"]=canon(state)
    OUT.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    print(json.dumps(state,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
