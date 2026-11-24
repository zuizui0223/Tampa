#!/usr/bin/env python3
"""Official public sources, no authentication or access-control bypass.
Source availability, not an ecological result. Foster bulk routes previously STOP.
"""
import hashlib,io,json,zipfile,urllib.parse,urllib.request,urllib.error,csv
from pathlib import Path
BASE="https://datadryad.org"
ROOT=Path("otter_sources")
MAX=15_000_000
FOSTER="10.5061/dryad.ns1rn8pt4"
WASSON="10.7291/D1FX0Z"
def fetch(link):
    url=urllib.parse.urljoin(BASE,link)
    if urllib.parse.urlsplit(url).scheme!="https" or urllib.parse.urlsplit(url).netloc!="datadryad.org":
        raise ValueError("unexpected API origin")
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-otter-public-source-audit/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=45) as r:
        b=r.read(MAX+1)
    if len(b)>MAX:raise ValueError("source exceeds cap")
    return b
def sha(b):return hashlib.sha256(b).hexdigest()
def links(o):return {k:v["href"] for k,v in o.get("_links",{}).items() if isinstance(v,dict) and isinstance(v.get("href"),str)}
def meta(url):
    b=fetch(url);return json.loads(b),sha(b)
def unique_link(o,name):
    a=[v for k,v in links(o).items() if k.split(":")[-1]==name]
    if len(a)!=1:raise ValueError("missing or ambiguous "+name+" link")
    return a[0]
def source(doi):
    m,sh=meta("/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe=""))
    v,vs=meta(unique_link(m,"version"))
    return m,v,dict(doi=doi,title=m.get("title"),dataset_metadata_sha256=sh,version_metadata_sha256=vs)
def inventory_zip(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if len(z.infolist())>150 or sum(x.file_size for x in z.infolist())>50_000_000:raise ValueError("archive cap")
        out=[]
        for x in z.infolist():
            if x.is_dir():continue
            if Path(x.filename).is_absolute() or ".." in Path(x.filename).parts:raise ValueError("unsafe archive member")
            raw=z.read(x)
            out.append(dict(name=x.filename,bytes=len(raw),sha256=sha(raw)))
        return out
def foster():
    m,v,out=source(FOSTER)
    f,fs=meta(unique_link(v,"files"))
    entries=f.get("_embedded",{}).get("stash:files",[])
    out["file_listing_sha256"]=fs
    out["files"]=[]
    for item in entries:
        info=dict(path=item.get("path"),size=item.get("size"),links=links(item))
        # Follow only the advertised public download route; never guess links.
        try:
            link=unique_link(item,"download")
            b=fetch(link)
            if len(b)==0:raise ValueError("empty file")
            filename=Path(item["path"]).name
            if not filename or filename in {".",".."}:raise ValueError("invalid basename")
            if filename.lower().endswith(".zip"):
                info["archive_members"]=inventory_zip(b)
            elif filename.lower().endswith(".pdf"):
                if not b.startswith(b"%PDF"):raise ValueError("not PDF")
            else:raise ValueError("unmapped source format")
            dest=ROOT/"foster";dest.mkdir(exist_ok=True);(dest/filename).write_bytes(b)
            info.update(status="PUBLIC_FILE_RETRIEVED",sha256=sha(b),bytes=len(b))
        except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
            info.update(status="ACCESS_OR_SCHEMA_STOP",reason=str(e)[:240])
        out["files"].append(info)
    out["status"]="FILE_INVENTORY_ONLY"
    return out
def wasson():
    m,v,out=source(WASSON); b=fetch(unique_link(v,"download"));out["archive_sha256"]=sha(b)
    files=inventory_zip(b);out["files"]=files
    dest=ROOT/"wasson";dest.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        selected={"Elkhorn_Otter_Eelgrass.csv","Elkhorn_Otter_Site_Season.csv","Elkhorn_Otter_Site_Tides.csv","Otter_Elkhorn_LongTerm.csv","README_Otter_Wasson.txt"}
        seen=set()
        for item in z.infolist():
            if item.is_dir():continue
            n=Path(item.filename).name
            if n not in selected:continue
            if n in seen:raise ValueError("duplicate basename")
            seen.add(n);raw=z.read(item)
            (dest/n).write_bytes(raw)
            if n.endswith(".csv"):
                r=csv.reader(io.StringIO(raw.decode("utf-8-sig")))
                out.setdefault("csv_inventory",{})[n]=dict(header=next(r),rows=sum(1 for _ in r),sha256=sha(raw))
        if seen!=selected:raise ValueError("source member roster changed")
    out["status"]="SOURCE_ACQUIRED_SCHEMA_ONLY"
    return out
def safe(name,fn):
    try:return dict(name=name,**fn())
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile) as e:return dict(name=name,status="ACCESS_OR_SCHEMA_STOP",reason=str(e)[:240])
if __name__=="__main__":
    ROOT.mkdir(exist_ok=True)
    out={"status":"source_audit_only","sources":[safe("Foster_genetics",foster),safe("Wasson_extent",wasson)]}
    (ROOT/"source_manifest.json").write_text(json.dumps(out,indent=2,sort_keys=True))
    print(json.dumps(out,indent=2,sort_keys=True))
