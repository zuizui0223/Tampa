#!/usr/bin/env python3
"""Open-data source eligibility, no fitting or untouched external validation."""
import json, hashlib, io, zipfile, csv, urllib.request, urllib.parse, urllib.error
from pathlib import Path
import openpyxl
ROOT=Path("external_reproductive")
MAX=20_000_000
PLOS="https://journals.plos.org/plosone/article/file?id=10.1371%2Fjournal.pone.0199275.s004&type=supplementary"
DRYAD="https://datadryad.org"
DOIS={"zostera_paternity":"10.5061/dryad.dfn2z358x","posidonia_adult_seedling":"10.5061/dryad.dfn2z3577"}
def get(url):
    url=urllib.parse.urljoin(DRYAD,url)
    if urllib.parse.urlsplit(url).scheme!="https":raise ValueError("non-HTTPS")
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-reproductive-source-audit/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=45) as r:
        data=r.read(MAX+1)
    if len(data)>MAX:raise ValueError("byte cap")
    return data
def sha(b):return hashlib.sha256(b).hexdigest()
def links(x):
    return {k:v["href"] for k,v in x.get("_links",{}).items() if isinstance(v,dict) and isinstance(v.get("href"),str)}
def xlsx_info(b):
    w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    out=[]
    for s in w:
        # First 5 row previews for schema only; no numeric effect calculation.
        rows=list(s.iter_rows(min_row=1,max_row=5,values_only=True))
        out.append(dict(sheet=s.title,declared_rows=s.max_row,declared_columns=s.max_column,first_rows=rows))
    w.close()
    return out
def plos():
    b=get(PLOS); info=xlsx_info(b); (ROOT/"zostera_noltei_s004.xlsx").write_bytes(b)
    return dict(status="SOURCE_ACQUIRED_SCHEMA_ONLY",url=PLOS,sha256=sha(b),size=len(b),worksheets=info)
def dryad(name,doi):
    b=get(DRYAD+"/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe=""))
    m=json.loads(b); l=links(m)
    v=[x for k,x in l.items() if k.split(":")[-1]=="version"]
    if len(v)==1:m=json.loads(get(v[0]));l=links(m)
    dl=[x for k,x in l.items() if k.split(":")[-1]=="download"]
    if len(dl)!=1:return dict(status="METADATA_ONLY_NO_UNAMBIGUOUS_DOWNLOAD_LINK",doi=doi,links=l)
    zraw=get(dl[0])
    with zipfile.ZipFile(io.BytesIO(zraw)) as z:
        if len(z.infolist())>100 or sum(x.file_size for x in z.infolist())>50_000_000:raise ValueError("archive cap")
        dest=ROOT/name;dest.mkdir(exist_ok=True)
        report=[]; seen=set()
        for x in z.infolist():
            if x.is_dir():continue
            path=Path(x.filename)
            if path.is_absolute() or ".." in path.parts or path.name in seen:raise ValueError("unsafe/duplicate member")
            seen.add(path.name); raw=z.read(x)
            # Retain only actual tabular, genotype and README source files for analysis.
            if path.suffix.lower() not in {".xlsx",".csv",".tsv",".txt",".md"}:continue
            entry=dict(name=x.filename,bytes=len(raw),sha256=sha(raw))
            if path.suffix.lower()==".xlsx":entry["worksheets"]=xlsx_info(raw)
            if path.suffix.lower() in {".csv",".tsv"}:
                try:
                    reader=csv.reader(io.StringIO(raw.decode("utf-8-sig")),delimiter="\t" if path.suffix.lower()==".tsv" else ",")
                    entry["header"]=next(reader,None);entry["rows"]=sum(1 for _ in reader)
                except (UnicodeError,csv.Error):entry["schema_stop"]=True
            (dest/path.name).write_bytes(raw);report.append(entry)
    return dict(status="SOURCE_ACQUIRED_SCHEMA_ONLY",doi=doi,archive_sha256=sha(zraw),files=report)
def safe(name,fn):
    try:return dict(name=name,**fn())
    except (OSError,ValueError,KeyError,TypeError,AttributeError,zipfile.BadZipFile,openpyxl.utils.exceptions.InvalidFileException) as e:
        return dict(name=name,status="ACCESS_OR_SCHEMA_STOP",reason=f"{type(e).__name__}: {str(e)[:240]}")
if __name__=="__main__":
    ROOT.mkdir(exist_ok=True)
    out=[safe("zostera_noltei_spatial",plos)]+[safe(k,lambda k=k,v=v:dryad(k,v)) for k,v in DOIS.items()]
    report=dict(status="source_inventory_not_ecological_result",sources=out)
    (ROOT/"source_manifest.json").write_text(json.dumps(report,indent=2,default=str,sort_keys=True))
    print(json.dumps(report,indent=2,default=str,sort_keys=True))
