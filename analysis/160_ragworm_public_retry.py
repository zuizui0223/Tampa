#!/usr/bin/env python3
"""Retry documented public sources. Never use restricted or unauthorized file routes."""
import hashlib,io,json,os,re,urllib.request,urllib.parse,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
OUT=Path("ragworm_retry");OUT.mkdir(exist_ok=True)
def get(url,cap=80_000_000):
    assert urllib.parse.urlparse(url).scheme=="https"
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Tampa-research/1.0","Accept-Encoding":"identity"}),timeout=45) as f:
        b=f.read(cap+1)
    if len(b)>cap:raise ValueError("cap exceeded")
    return b
def save(name,b):
    (OUT/name).write_bytes(b)
    return dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def package():
    r={"kind":"author_public_R_package_example","commit":"24d3f06418a8aca77db4e7fbef66c45dc55873f8","expected_git_blob":"859c598928fa7e51430119c9ef79abe7386a6220"}
    try:
        b=get("https://raw.githubusercontent.com/allertbijleveld/SIBES/"+r["commit"]+"/data/SIBES_dataset.rda",2_000_000)
        assert hashlib.sha1(("blob "+str(len(b))+"\0").encode()+b).hexdigest()==r["expected_git_blob"]
        r.update(save("SIBES_dataset.rda",b),status="ACQUIRED_EXAMPLE_COVERAGE_UNVERIFIED")
    except Exception as e:r.update(status="STOP",reason=str(e))
    return r
def official():
    r={"kind":"NIOZ official CKAN","doi":"10.25850/nioz/7b.b.ug","files":[]}
    try:
        b=get("https://doi.nioz.nl/api/3/action/package_show?id=sibes-dataset",4_000_000);d=json.loads(b)["result"]
        assert d["name"]=="sibes-dataset" and "SIBES" in d["title"]
        r["metadata"]=save("sibes_ckan.json",b)
        for f in d.get("resources",[]):
            name=f.get("name","");url=f.get("url","")
            if name.lower() not in ["biota.csv","sample.csv","samples.csv","species.csv"]:continue
            x={"name":name,"url":url,"id":f.get("id"),"size":f.get("size"),"hash":f.get("hash")}
            try:
                bb=get(url,100_000_000)
                assert b"\x00" not in bb[:1024] and not bb.lstrip().startswith(b"<"),"not a CSV"
                if x["hash"] and re.fullmatch("[a-fA-F0-9]{32}",x["hash"]):assert hashlib.md5(bb).hexdigest()==x["hash"].lower()
                x.update(save("official_"+name,bb),status="ACQUIRED")
            except Exception as e:x.update(status="STOP",reason=str(e))
            r["files"].append(x)
        r["status"]="ACQUIRED" if len(r["files"])==3 and all(x["status"]=="ACQUIRED" for x in r["files"]) else "PARTIAL_OR_STOP"
    except Exception as e:r.update(status="STOP",reason=str(e))
    return r
def zenodo():
    # One public immutable 940 MB archive; stream to temp disk, validate full publisher MD5.
    # Only tabular and code members are retained as artifacts; no pictures or videos.
    r={"kind":"Hautekiet public archive","doi":"10.5281/zenodo.15182547","size":940479031,"md5":"2d41d07639e52d05da53b53d25d1ae63","members":[]}
    tmp=OUT/"_archive.tmp"
    try:
        md=hashlib.md5();n=0
        url="https://zenodo.org/api/records/15182547/files/data.zip/content"
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Tampa-research/1.0","Accept-Encoding":"identity"}),timeout=90) as f,tmp.open("wb") as o:
            while True:
                b=f.read(4*1024*1024)
                if not b:break
                n+=len(b)
                if n>r["size"]:raise ValueError("publisher size exceeded")
                md.update(b);o.write(b)
        assert n==r["size"] and md.hexdigest()==r["md5"],"publisher checksum/size mismatch"
        total=0
        with zipfile.ZipFile(tmp) as z:
            r["archive_members"]=[{"path":v.filename,"size":v.file_size} for v in z.infolist()]
            for i,v in enumerate(z.infolist()):
                if v.is_dir() or not v.filename.lower().endswith((".csv",".tsv",".txt",".xlsx",".r",".rmd")):continue
                if v.file_size>10_000_000 or total+v.file_size>40_000_000:continue
                b=z.read(v);total+=len(b)
                r["members"].append(dict(path=v.filename,**save("hautekiet_"+str(i)+"_"+re.sub(r"[^a-zA-Z0-9_.-]","_",Path(v.filename).name),b)))
        r["status"]="ACQUIRED_TABLES" if r["members"] else "NO_TABLES"
    except Exception as e:r.update(status="STOP",reason=str(e))
    finally:
        tmp.unlink(missing_ok=True)
    return r
with ThreadPoolExecutor(max_workers=3) as ex:
    futures=[ex.submit(package),ex.submit(official),ex.submit(zenodo)]
    records=[f.result() for f in futures]
(OUT/"manifest.json").write_text(json.dumps(records,indent=2)+"\n")
print(json.dumps([{k:v for k,v in r.items() if k!="archive_members"} for r in records],indent=2))
