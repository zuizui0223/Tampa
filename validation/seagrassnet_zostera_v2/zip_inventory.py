#!/usr/bin/env python3
"""Read only the ZIP central directory from the SeagrassNet biological download."""
from __future__ import annotations
import hashlib,json,struct
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT.parent/"seagrassnet_zostera_v1"/"preflight_result.json").read_text())
H=json.loads((ROOT/"head_result.json").read_text())
C=json.loads((ROOT/"zip_inventory_contract.json").read_text())
OUT=ROOT/"zip_inventory_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def main():
    out={
        "schema":"tampa.seagrassnet_zostera_external_early_warning_v2.zip_inventory_result",
        "status":None,
        "archive_metadata_range_requests":0,
        "archive_metadata_bytes_opened":0,
        "member_payload_requests":0,
        "member_payload_bytes_opened":0,
        "response_values_opened":False
    }
    try:
        if P["fingerprint"]!=C["requires_preflight_fingerprint"] or H["fingerprint"]!=C["requires_head_fingerprint"]:
            raise RuntimeError("preflight_or_head_identity_drift")
        sites=sorted(P["safe_interface"]["candidate_sites"],key=lambda x:(x.get("code",""),x["uuid"]))
        ids=[x["uuid"] for x in sites]
        if hashlib.sha256("\n".join(ids).encode()).hexdigest()!=C["candidate_uuid_sha256"]:
            raise RuntimeError("candidate_uuid_universe_drift")
        endpoint=C["endpoint"]+"?"+urlencode({C["query_parameter"]:",".join(ids)})
        cap=int(C["allowed_access"]["maximum_archive_metadata_bytes"])
        req=Request(endpoint,headers={"Range":f"bytes=-{cap}","Accept-Encoding":"identity","User-Agent":"Tampa-SeagrassNet-v2-ZIP-Inventory/1.0"})
        out["archive_metadata_range_requests"]=1
        with urlopen(req,timeout=60) as resp:
            status=resp.status
            cr=resp.headers.get("Content-Range","")
            data=resp.read(cap+1)
        out["archive_metadata_bytes_opened"]=len(data)
        if status!=206:
            raise RuntimeError(f"range_not_honored_http_{status}")
        if len(data)>cap:
            raise RuntimeError("archive_metadata_cap_exceeded")
        # Find last non-ZIP64 EOCD.
        eocd=data.rfind(b"PK\x05\x06")
        if eocd<0 or eocd+22>len(data):
            raise RuntimeError("zip_eocd_not_found")
        disk,cd_disk,n_disk,n_total,cd_size,cd_offset,comment_len=struct.unpack_from("<HHHHIIH",data,eocd+4)
        if disk!=0 or cd_disk!=0 or n_disk!=n_total:
            raise RuntimeError("multi_disk_zip_unsupported")
        if n_total==0xffff or cd_size==0xffffffff or cd_offset==0xffffffff:
            raise RuntimeError("zip64_unsupported")
        # Content-Range tells us absolute start of suffix.
        # Format: bytes START-END/TOTAL
        try:
            range_part,total_s=cr.split(" ",1)[1].split("/")
            start_s,end_s=range_part.split("-")
            suffix_start=int(start_s); total=int(total_s)
        except Exception as exc:
            raise RuntimeError(f"invalid_content_range:{cr!r}") from exc
        if cd_offset+cd_size>total:
            raise RuntimeError("central_directory_out_of_bounds")
        rel=cd_offset-suffix_start
        if rel<0 or rel+cd_size>len(data):
            raise RuntimeError("central_directory_not_fully_in_suffix")
        pos=rel
        members=[]
        for _ in range(n_total):
            if data[pos:pos+4]!=b"PK\x01\x02":
                raise RuntimeError("central_directory_signature_mismatch")
            fields=struct.unpack_from("<6H3I5H2I",data,pos+4)
            # versions,flags,method,time,date,crc,csize,usize,nlen,xlen,clen,disk,intattr,extattr,loff
            method=fields[3]; crc=fields[6]; csize=fields[7]; usize=fields[8]
            nlen=fields[9]; xlen=fields[10]; clen=fields[11]; loff=fields[15]
            name_b=data[pos+46:pos+46+nlen]
            try: name=name_b.decode("utf-8")
            except UnicodeDecodeError: name=name_b.decode("cp437")
            members.append({
                "name":name,
                "method":method,
                "crc32":f"{crc:08x}",
                "compressed_size":csize,
                "uncompressed_size":usize,
                "local_header_offset":loff
            })
            pos += 46+nlen+xlen+clen
        safe={
            "http_status":status,
            "content_range":cr,
            "archive_total_bytes":total,
            "central_directory_offset":cd_offset,
            "central_directory_size":cd_size,
            "member_count":n_total,
            "members":members
        }
        out["safe_inventory"]=safe
        out["safe_inventory_fingerprint"]=canon(safe)
        out["status"]="gate1_zip_inventory_qualified"
        out["next_gate"]="freeze exact selected member set and member parser before any member payload access"
    except Exception as exc:
        out["status"]="terminal_pre_response_zip_inventory_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
