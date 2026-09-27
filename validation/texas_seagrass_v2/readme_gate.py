#!/usr/bin/env python3
from __future__ import annotations
import binascii, hashlib, json, struct, zlib
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"readme_gate_contract.json").read_text())
OUT=ROOT/"readme_gate_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def rg(url,start,end,total):
    req=Request(url,headers={"Range":f"bytes={start}-{end}","Accept-Encoding":"identity","User-Agent":"Tampa-Texas-ReadmeGate/1.0"})
    with urlopen(req,timeout=45) as r:
        if r.status!=206: raise RuntimeError(f"range_http_{r.status}")
        if str(r.headers.get("Content-Range",""))!=f"bytes {start}-{end}/{total}":
            raise RuntimeError("content_range_mismatch")
        b=r.read(end-start+2)
    if len(b)!=end-start+1: raise RuntimeError("range_length_mismatch")
    return b

def entry_bytes(s):
    off=int(s["local_header_offset"]); total=int(s["archive_size"])
    h=rg(s["url"],off,off+29,total)
    if h[:4]!=b"PK\x03\x04": raise RuntimeError("local_header_signature")
    method=struct.unpack_from("<H",h,8)[0]
    fn=struct.unpack_from("<H",h,26)[0]; ex=struct.unpack_from("<H",h,28)[0]
    if method!=int(s["compression_method"]): raise RuntimeError("compression_method_drift")
    n=rg(s["url"],off+30,off+30+fn+ex-1,total) if fn+ex else b""
    name=n[:fn].decode("utf-8")
    if name!=s["name"]: raise RuntimeError("entry_name_drift")
    start=off+30+fn+ex; end=start+int(s["compressed_size"])-1
    raw=rg(s["url"],start,end,total)
    data=raw if method==0 else zlib.decompress(raw,-15)
    if len(data)!=int(s["uncompressed_size"]): raise RuntimeError("uncompressed_size_drift")
    if f"{binascii.crc32(data)&0xffffffff:08x}"!=s["crc32"]: raise RuntimeError("crc_drift")
    return data

def main():
    out={"schema":"tampa.texas_seagrass_external_early_warning_v2.readme_gate_result",
         "status":None,"cover_entry_payload_requests":0,"response_values_opened":False}
    try:
        rows=[]
        for s in C["allowed_entries"]:
            b=entry_bytes(s)
            rows.append({"year":s["year"],"name":s["name"],"text":b.decode("utf-8","replace")})
        safe={"readmes":rows}
        out["safe_readmes"]=safe
        out["safe_readmes_fingerprint"]=canon(safe)
        out["status"]="readme_metadata_pass"
        out["next_gate"]="freeze cover-table parser and statistical outcome contract before any QuadratPercentCover payload access"
    except Exception as exc:
        out["status"]="terminal_pre_response_readme_metadata_stop"; out["reason"]=str(exc); out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
