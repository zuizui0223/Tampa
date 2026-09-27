#!/usr/bin/env python3
"""Remote ZIP central-directory inventory for Texas seagrass v2.

Reads HTTP headers plus ZIP EOCD/central-directory bytes only. It never requests
a local-file payload and never decompresses biological data.
"""
from __future__ import annotations
import hashlib,json,struct
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"archive_inventory_contract.json").read_text())
ISO=json.loads((ROOT/"iso_metadata_result.json").read_text())
OUT=ROOT/"archive_inventory_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def head(url):
    req=Request(url,method="HEAD",headers={"Accept-Encoding":"identity","User-Agent":"Tampa-Texas-ZipInventory/1.0"})
    with urlopen(req,timeout=45) as r:
        if r.status not in (200,204):
            raise RuntimeError(f"head_http_{r.status}")
        length=r.headers.get("Content-Length")
        if length is None:
            raise RuntimeError("head_missing_content_length")
        return {
            "content_length":int(length),
            "content_type":str(r.headers.get("Content-Type","")),
            "etag":str(r.headers.get("ETag","")),
            "last_modified":str(r.headers.get("Last-Modified","")),
            "accept_ranges":str(r.headers.get("Accept-Ranges",""))
        }

def range_get(url,start,end,total):
    req=Request(url,headers={"Range":f"bytes={start}-{end}","Accept-Encoding":"identity","User-Agent":"Tampa-Texas-ZipInventory/1.0"})
    with urlopen(req,timeout=45) as r:
        if r.status!=206:
            raise RuntimeError(f"range_http_{r.status}_{start}_{end}")
        cr=str(r.headers.get("Content-Range",""))
        if cr!=f"bytes {start}-{end}/{total}":
            raise RuntimeError(f"content_range_mismatch:{cr}")
        data=r.read((end-start+1)+1)
    if len(data)!=(end-start+1):
        raise RuntimeError("range_length_mismatch")
    return data

def parse_eocd(tail,tail_start,total):
    sig=b"PK\x05\x06"
    pos=tail.rfind(sig)
    if pos<0 or pos+22>len(tail):
        raise RuntimeError("eocd_not_found")
    fields=struct.unpack_from("<4s4H2LH",tail,pos)
    _,disk,cd_disk,n_disk,n_total,cd_size,cd_offset,comment_len=fields
    if disk!=0 or cd_disk!=0 or n_disk!=n_total:
        raise RuntimeError("multi_disk_zip_not_supported")
    if cd_offset+cd_size>total:
        raise RuntimeError("central_directory_out_of_bounds")
    return {"entries":n_total,"cd_size":cd_size,"cd_offset":cd_offset,"comment_len":comment_len}

def parse_cd(buf,expected):
    entries=[]
    p=0
    for _ in range(expected):
        if p+46>len(buf) or buf[p:p+4]!=b"PK\x01\x02":
            raise RuntimeError("central_directory_record_mismatch")
        method=struct.unpack_from("<H",buf,p+10)[0]
        crc=struct.unpack_from("<L",buf,p+16)[0]
        csize=struct.unpack_from("<L",buf,p+20)[0]
        usize=struct.unpack_from("<L",buf,p+24)[0]
        fnlen=struct.unpack_from("<H",buf,p+28)[0]
        xlen=struct.unpack_from("<H",buf,p+30)[0]
        clen=struct.unpack_from("<H",buf,p+32)[0]
        loff=struct.unpack_from("<L",buf,p+42)[0]
        start=p+46; end=start+fnlen
        if end>len(buf):
            raise RuntimeError("filename_out_of_bounds")
        name=buf[start:end].decode("utf-8","replace")
        entries.append({"name":name,"compression_method":method,"crc32":f"{crc:08x}","compressed_size":csize,"uncompressed_size":usize,"local_header_offset":loff})
        p=end+xlen+clen
    return entries

def inventory_one(spec):
    h=head(spec["url"])
    total=h["content_length"]
    if total<=22:
        raise RuntimeError("archive_too_small")
    tail_len=min(total,65557)
    start=total-tail_len
    tail=range_get(spec["url"],start,total-1,total)
    e=parse_eocd(tail,start,total)
    if e["cd_size"]>int(C["allowed_access"]["max_central_directory_bytes_per_archive"]):
        raise RuntimeError("central_directory_too_large")
    cd_start=e["cd_offset"]; cd_end=cd_start+e["cd_size"]-1
    if cd_start>=start and cd_end<total:
        cd=tail[cd_start-start:cd_end-start+1]
        cd_extra_request=0
    else:
        cd=range_get(spec["url"],cd_start,cd_end,total)
        cd_extra_request=1
    entries=parse_cd(cd,e["entries"])
    return {"year":spec["year"],"url":spec["url"],"head":h,"eocd":e,"central_directory_extra_request":cd_extra_request,"central_directory_bytes":len(cd),"entries":entries}

def main():
    out={"schema":"tampa.texas_seagrass_external_early_warning_v2.archive_inventory_result","status":None,"zip_entry_payload_requests":0,"decompressed_data_bytes":0,"response_values_opened":False}
    try:
        if ISO["fingerprint"]!=C["requires_iso_fingerprint"] or ISO["status"]!="gate0_iso_metadata_qualified":
            raise RuntimeError("iso_gate_identity_or_status_mismatch")
        inv=[inventory_one(x) for x in C["archives"]]
        safe={"focal_taxon":C["focal_taxon"],"archives":inv}
        out["safe_archive_inventory"]=safe
        out["safe_archive_inventory_fingerprint"]=canon(safe)
        if any(not x["entries"] for x in inv):
            raise RuntimeError("empty_archive_inventory")
        out["status"]="gate1_archive_inventory_pass"
        out["next_gate"]="freeze exact archive-entry selection plus long/wide schema aliases and statistical endpoint before any entry payload is requested"
    except Exception as exc:
        out["status"]="terminal_pre_response_archive_inventory_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
