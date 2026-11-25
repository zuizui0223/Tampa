#!/usr/bin/env python3
"""Public original-data acquisition, no fitted effects or inferred sample joins."""
import hashlib,json,urllib.request,urllib.error,socket
from pathlib import Path
ROOT=Path("reserve_sources")
SOURCES={
 "cimon_2021":{"931121":"carbohydrates","931119":"shoot_density","931120":"biomass_distribution","931117":"biomass","931114":"leaf_elongation_epiphytes"},
 "munkes_2015":{"854839":"biomass","849669":"leaf_length","854836":"mortality","849670":"shoot_density","855022":"sugar_concentration"},
}
def fetch(group,accession,endpoint):
    doi="10.1594/PANGAEA."+accession
    url="https://doi.pangaea.de/"+doi+"?format=textfile"
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-reserve-source-gate/1.0","Accept":"text/plain","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read(4_000_001)
    if not raw or len(raw)>4_000_000:raise ValueError("empty or over size cap")
    txt=raw.decode("utf-8-sig")
    if not txt.startswith("/* DATA DESCRIPTION:") or "*/" not in txt:raise ValueError("not expected PANGAEA textfile")
    meta,tab=txt.split("*/",1)
    if doi not in meta:raise ValueError("accession not identified in source metadata")
    lines=[line for line in tab.splitlines() if line.strip()]
    if len(lines)<2 or "\t" not in lines[0]:raise ValueError("missing tab-delimited table")
    dest=ROOT/group;dest.mkdir(parents=True,exist_ok=True)
    file=dest/(accession+".tab");file.write_bytes(raw)
    return {"status":"ACQUIRED_SCHEMA_UNVERIFIED","doi":doi,"endpoint":endpoint,"source_url":url,"file":str(file),"sha256":hashlib.sha256(raw).hexdigest(),"rows_including_header":len(lines),"header":lines[0].split("\t")}
def main():
    ROOT.mkdir(exist_ok=True);items=[]
    for group,records in SOURCES.items():
        for accession,endpoint in records.items():
            try:out=fetch(group,accession,endpoint)
            except (OSError,ValueError,UnicodeError) as e:out={"status":"ACCESS_OR_SCHEMA_STOP","doi":"10.1594/PANGAEA."+accession,"endpoint":endpoint,"reason":str(e)[:240]}
            items.append({"study":group,**out})
    report={"status":"source_inventory_only","items":items,"scope":"Validate exact plot keys, tissue and time labels, density denominators and treatment assignment before any effects. Cimon T2 carbohydrate may be linked to T3 density only after plot alignment; no reserve recovery trajectory. Munkes cohorts may differ by duration; no assumed repeated measures. Access failure is not a biological null."}
    (ROOT/"source_manifest.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":main()
