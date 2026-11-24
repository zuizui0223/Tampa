#!/usr/bin/env python3
"""Paired-stage mutualism source eligibility. Public repositories only.
No response model, no fallback around access denial, no raw files committed.
"""
import hashlib,importlib.util,json,urllib.parse,urllib.request,zipfile,io
from pathlib import Path
ROOT=Path("transmission_sources")
MAX=20_000_000
s=importlib.util.spec_from_file_location("dryad",Path(__file__).with_name("144_external_seagrass_genetic_source_gate.py"))
d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
def fetch(url):
    if urllib.parse.urlsplit(url).scheme!="https":raise ValueError("non-HTTPS")
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-paired-stage-source-audit/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=45) as r:raw=r.read(MAX+1)
    if len(raw)>MAX:raise ValueError("byte cap")
    return raw
def metadata(url):
    b=fetch(url);return json.loads(b),hashlib.sha256(b).hexdigest()
def save(dest,name,url,expected_bytes=None):
    if not name or Path(name).name!=name or name in (".",".."):raise ValueError("invalid file name")
    b=fetch(url)
    if expected_bytes is not None and len(b)!=expected_bytes:raise ValueError("provider size mismatch")
    if not b:raise ValueError("empty file")
    if name.endswith(".xlsx") and not zipfile.is_zipfile(io.BytesIO(b)):raise ValueError("not xlsx")
    dest.mkdir(parents=True,exist_ok=True);(dest/name).write_bytes(b)
    return dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def zenodo():
    url="https://zenodo.org/api/records/4958629";m,sha=metadata(url)
    title=m["metadata"]["title"]
    if "three-stage symbiosis" not in title.lower():raise ValueError("unexpected Zenodo record")
    files=[f for f in m["files"] if f["key"]=="Experimental_data.xlsx"]
    if len(files)!=1:raise ValueError("missing workbook")
    f=files[0];u=f["links"].get("content") or f["links"].get("self")
    if not u:raise ValueError("missing advertised download URL")
    return dict(status="ACQUIRED_SCHEMA_UNVERIFIED",metadata_sha256=sha,title=title,files=[save(ROOT/"lucinid_2012",f["key"],u,f.get("size"))])
def figshare():
    m,sha=metadata("https://api.figshare.com/v2/articles/12574010/versions/1")
    if "facilitation of a tropical seagrass" not in m["title"].lower():raise ValueError("unexpected Figshare article")
    files=[f for f in m["files"] if Path(f["name"]).suffix.lower() in {".csv",".xlsx",".xls",".txt",".zip",".r",".md"}]
    if not files or len(files)>40:raise ValueError("unmapped file roster")
    return dict(status="ACQUIRED_SCHEMA_UNVERIFIED",metadata_sha256=sha,title=m["title"],files=[save(ROOT/"chin_2021",f["name"],f["downloadUrl"],f.get("size")) for f in files])
def dans():
    base="https://lifesciences.datastations.nl"
    doi="doi:10.17026/dans-x9d-ytww"
    m,sha=metadata(base+"/api/datasets/:persistentId/?"+urllib.parse.urlencode({"persistentId":doi}))
    v=m["data"]["latestVersion"]
    title=next(f["value"] for f in v["metadataBlocks"]["citation"]["fields"] if f["typeName"]=="title")
    if "sulfide-detoxification mutualism" not in title.lower():raise ValueError("unexpected dataset title")
    fs=[f["dataFile"] for f in v["files"] if not f.get("restricted",False) and f["dataFile"]["filename"].lower().endswith((".csv",".tab",".txt",".zip"))]
    if not fs or len(fs)>20:raise ValueError("unmapped or restricted file roster")
    out=[]
    for f in fs:
        # Standard Dataverse public API, ID from provider metadata.
        u=f"{base}/api/access/datafile/{int(f['id'])}?format=original"
        out.append(save(ROOT/"de_fouw_2022",f["filename"],u))
    return dict(status="ACQUIRED_SCHEMA_UNVERIFIED",metadata_sha256=sha,title=title,files=out)
def dryad(name,doi):
    d.ROOT=ROOT;return d.dryad(name,doi)
def safe(name,fn):
    try:return dict(name=name,**fn())
    except (OSError,ValueError,KeyError,TypeError,AttributeError,zipfile.BadZipFile) as e:return dict(name=name,status="ACCESS_OR_SCHEMA_STOP",reason=f"{type(e).__name__}: {str(e)[:220]}")
if __name__=="__main__":
    ROOT.mkdir(exist_ok=True)
    out=[safe("lucinid_2012_zenodo",zenodo),safe("lucinid_2020_dryad",lambda:dryad("lucinid_2020","10.5061/dryad.jm63xsj6n")),safe("donaher_2021_dryad",lambda:dryad("donaher_2021","10.5061/dryad.9cnp5hqh7")),safe("chin_2021_figshare",figshare),safe("de_fouw_2022_dans",dans)]
    report={"status":"source_gate_only_no_effect_fit","sources":out,"scope":"Verify exact experimental-unit keys, endpoint timing, missingness and block assignments before fitting. Access STOP is not zero effect. Do not combine different experiments within an article."}
    (ROOT/"source_manifest.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True,default=str))
