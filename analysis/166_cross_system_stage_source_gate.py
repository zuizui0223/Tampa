#!/usr/bin/env python3
"""Public data acquisition for pollination and trophic cascade candidates.
Source inventory only: confirm design and matching before effect extraction.
"""
import hashlib,importlib.util,json,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path("cross_system_sources")
s=importlib.util.spec_from_file_location("source",Path(__file__).with_name("160_paired_stage_mutualism_source_gate.py"))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def dryad(name,doi):
    m.d.ROOT=ROOT
    return m.d.dryad(name,doi)
def figshare_apple():
    a,h=m.metadata("https://api.figshare.com/v2/articles/13023224/versions/1")
    if "pollen tube" not in a["title"].lower():raise ValueError("unexpected article title")
    files=[]
    for f in a["files"]:
        if Path(f["name"]).suffix.lower() not in {".csv",".tsv",".xlsx",".xls",".txt",".zip",".r",".md",".rdata",".rds"}:continue
        urls={f[k] for k in ("download_url","downloadUrl") if isinstance(f.get(k),str) and f[k]}
        if len(urls)!=1:raise ValueError("no unique advertised file URL")
        files.append(m.save(ROOT/"apple_2020",f["name"],next(iter(urls)),f.get("size")))
    return dict(status="ACQUIRED_SCHEMA_UNVERIFIED" if files else "NO_MAPPED_DATA_FILES",title=a["title"],metadata_sha256=h,files=files)
def raymond():
    # DataONE public CNRead resolve and indexed package metadata, no guessed file IDs.
    pid="doi:10.5063/V986FN"
    cn="https://cn.dataone.org/cn/v2/"
    raw=m.fetch(cn+"resolve/"+urllib.parse.quote(pid,safe=""))
    root=ET.fromstring(raw)
    loc=[x.text for x in root.iter() if x.tag.split("}")[-1]=="url" and x.text]
    if not loc:raise ValueError("no public object locations")
    dest=ROOT/"raymond_2021";dest.mkdir(exist_ok=True)
    (dest/"resolve.xml").write_bytes(raw)
    idx,sha=m.metadata(cn+"query/solr/?"+urllib.parse.urlencode({"q":f'id:"{pid}" OR seriesId:"{pid}"',"fl":"id,seriesId,title,formatId,resourceMap,documents,size","wt":"json","rows":30}))
    (dest/"index.json").write_text(json.dumps(idx,indent=2,sort_keys=True))
    return {"status":"METADATA_RESOLVED_NOT_RAW_ANALYSIS","resolve_sha256":hashlib.sha256(raw).hexdigest(),"index_sha256":sha,"locations":loc,"index_docs":idx.get("response",{}).get("docs",[])}
if __name__=="__main__":
    ROOT.mkdir(exist_ok=True)
    items=[m.safe("gallagher_2020",lambda:dryad("gallagher_2020","10.7280/D19X0D")),
      m.safe("gallagher_2021",lambda:dryad("gallagher_2021","10.7280/D16D7Z")),
      m.safe("apple_2020_figshare",figshare_apple),
      m.safe("clarkia_reproduction",lambda:dryad("clarkia_reproduction","10.5061/dryad.k3j9kd56r")),
      m.safe("herbivory_pollinator",lambda:dryad("herbivory_pollinator","10.5061/dryad.xpnvx0kvp")),
      m.safe("penstemon_2026",lambda:dryad("penstemon_2026","10.5061/dryad.xpnvx0kwt")),
      m.safe("raymond_2021_dataone",raymond)]
    report={"status":"source_gate_only","sources":items,"boundaries":["Gallagher phenology experiment and single-visit experiment separate; check pollen and seed units before matching. Week 4 floral display was augmented, do not infer natural seasonal causal slope.","Apple tissue pollen-tube assays may be destructive; do not assume flowers linked to fruit outcomes.","Clarkia supplemental pollination isolates pollinator-dependent component; not measured visitation unless source contains it.","Raymond 21 sites observational; no randomized predator effect. Hughes 2013 factorial/cage experiments registered separately, raw source not yet located."]}
    (ROOT/"source_manifest.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True,default=str))
