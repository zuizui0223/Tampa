#!/usr/bin/env python3
"""Public source acquisition only; explicit non-estimable stops, original bytes retained."""
import concurrent.futures,csv,hashlib,io,json,re,urllib.parse,urllib.request,zipfile
from pathlib import Path
OUT=Path("stage_partner_sources");OUT.mkdir(exist_ok=True)
CAP=35_000_000
def get(url):
    if not url.startswith("https://"):raise ValueError("HTTPS required")
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Tampa-research-source-audit/1.0","Accept-Encoding":"identity"}),timeout=45) as f:
        b=f.read(CAP+1);end=f.geturl()
    if len(b)>CAP:raise ValueError("file cap exceeded")
    return b,end
def save(name,b):
    name=re.sub(r"[^A-Za-z0-9_.-]","_",name)
    (OUT/name).write_bytes(b)
    return {"file":name,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def pang(id):
    doi="10.1594/PANGAEA."+id
    r={"doi":doi}
    try:
        b,end=get("https://doi.pangaea.de/"+doi+"?format=textfile")
        t=b.decode("utf-8-sig");assert doi.lower() in t.lower() and "\t" in t
        # PANGAEA embeds metadata in C-style comment, followed by tabular data.
        body=t.split("*/",1)[-1].strip()
        rows=list(csv.reader(io.StringIO(body),delimiter="\t"))
        assert len(rows)>1 and len(rows[0])>2 and all(len(x)==len(rows[0]) for x in rows[1:])
        r.update(save("pangaea_"+id+".tsv",b));r.update(status="RAW_TABLE_ACQUIRED",columns=rows[0],rows=len(rows)-1)
    except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return r
def fig():
    r={"doi":"10.6084/m9.figshare.32328606","files":[]}
    try:
        b,_=get("https://api.figshare.com/v2/articles/32328606");j=json.loads(b)
        assert j["doi"].lower().startswith(r["doi"]) and "seed" in j["title"].lower()
        r["metadata"]=save("figshare_metadata.json",b)
        for f in j["files"]:
            x={"name":f["name"]}
            try:
                b,_=get(f["downloadUrl"]);assert len(b)==f["size"]
                if f.get("computed_md5"):assert hashlib.md5(b).hexdigest()==f["computed_md5"]
                x.update(save("figshare_"+str(f["id"])+"_"+f["name"],b));x["status"]="ACQUIRED"
            except Exception as e:x.update(status="STOP",reason=str(e)[:250])
            r["files"].append(x)
        r["status"]="ACQUIRED" if r["files"] and all(x["status"]=="ACQUIRED" for x in r["files"]) else "PARTIAL_OR_STOP"
    except Exception as e:r.update(status="STOP",reason=type(e).__name__+": "+str(e)[:250])
    return r
def dans():
    doi="10.17026/dans-x38-abzq";r={"doi":doi,"files":[],"attempts":[]}
    for base in ["https://archaeology.datastations.nl","https://socialsciences.datastations.nl","https://ssh.datastations.nl","https://lifesciences.datastations.nl","https://phys-techsciences.datastations.nl","https://dataverse.nl"]:
        try:
            b,_=get(base+"/api/datasets/:persistentId/?persistentId="+urllib.parse.quote("doi:"+doi))
            j=json.loads(b);d=j["data"];assert d.get("persistentUrl","").lower().endswith(doi) or d.get("identifier","").lower()=="dans-x38-abzq"
            r["metadata"]=save("dans_metadata.json",b)
            for f in d["latestVersion"]["files"]:
                ff=f["dataFile"];x={"name":ff["filename"],"id":ff["id"]}
                try:
                    if f.get("restricted"):raise ValueError("restricted file; stop")
                    b,_=get(base+"/api/access/datafile/"+str(ff["id"]))
                    chk=ff.get("checksum",{})
                    if chk.get("type")=="MD5":assert hashlib.md5(b).hexdigest()==chk["value"]
                    x.update(save("dans_"+str(ff["id"])+"_"+ff["filename"],b));x["status"]="ACQUIRED"
                except Exception as e:x.update(status="STOP",reason=str(e)[:250])
                r["files"].append(x)
            r["status"]="ACQUIRED" if r["files"] and all(x["status"]=="ACQUIRED" for x in r["files"]) else "PARTIAL_OR_STOP"
            return r
        except Exception as e:r["attempts"].append({"host":base,"error":str(e)[:200]})
    r["status"]="STOP";return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    futures=[ex.submit(pang,"984655"),ex.submit(pang,"984656"),ex.submit(fig),ex.submit(dans)]
    records=[f.result() for f in futures]
(OUT/"manifest.json").write_text(json.dumps(records,indent=2)+"\n");print(json.dumps(records,indent=2))
