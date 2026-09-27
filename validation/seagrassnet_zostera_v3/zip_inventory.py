#!/usr/bin/env python3
"""SeagrassNet v3 response-blind ZIP central-directory inventory."""
from __future__ import annotations
import hashlib,json,struct
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT.parent/"seagrassnet_zostera_v1"/"preflight_result.json").read_text())
C=json.loads((ROOT/"zip_inventory_contract.json").read_text())
OUT=ROOT/"zip_inventory_result.json"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def endpoint_and_ids():
    if P["fingerprint"]!=C["candidate_universe"]["v1_preflight_fingerprint"]:
        raise RuntimeError("preflight_fingerprint_drift")
    sites=sorted(P["safe_interface"]["candidate_sites"],key=lambda x:(x.get("code",""),x["uuid"]))
    ids=[x["uuid"] for x in sites]
    if len(ids)!=C["candidate_universe"]["candidate_site_count"]:
        raise RuntimeError("candidate_site_count_drift")
    if hashlib.sha256("\n".join(ids).encode()).hexdigest()!=C["candidate_universe"]["candidate_uuid_sha256"]:
        raise RuntimeError("candidate_uuid_hash_drift")
    return C["endpoint"]["url"]+"?"+urlencode({C["endpoint"]["query_parameter"]:",".join(ids)}),ids

def main():
    out={
        "schema":"tampa.seagrassnet_zostera_external_early_warning_v3.zip_inventory_result",
        "status":None,
        "head_requests":0,
        "archive_metadata_range_requests":0,
        "archive_metadata_bytes_opened":0,
        "member_payload_requests":0,
        "member_payload_bytes_opened":0,
        "response_values_opened":False
    }
    try:
        endpoint,ids=endpoint_and_ids()
        hreq=Request(endpoint,method="HEAD",headers={"Accept-Encoding":"identity","User-Agent":"Tampa-SeagrassNet-v3-Inventory/1.0"})
        out["head_requests"]=1
        with urlopen(hreq,timeout=60) as resp:
            hs=resp.status
            hctype=(resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            hlen=resp.headers.get("Content-Length","")
            hdisp=resp.headers.get("Content-Disposition","")
        if hs<200 or hs>=300 or hctype!=C["endpoint"]["expected_content_type"]:
            raise RuntimeError(f"head_identity_failure:{hs}:{hctype}")
        cap=int(C["allowed_access"]["maximum_archive_metadata_bytes"])
        rreq=Request(endpoint,headers={"Range":f"bytes=-{cap}","Accept-Encoding":"identity","User-Agent":"Tampa-SeagrassNet-v3-Inventory/1.0"})
        out["archive_metadata_range_requests"]=1
        with urlopen(rreq,timeout=60) as resp:
            status=resp.status
            cr=resp.headers.get("Content-Range","")
            ctype=(resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            data=resp.read(cap+1)
        out["archive_metadata_bytes_opened"]=len(data)
        if status!=206:
            raise RuntimeError(f"range_not_honored_http_{status}")
        if ctype!=C["endpoint"]["expected_content_type"]:
            raise RuntimeError(f"range_content_type_drift:{ctype}")
        if len(data)>cap:
            raise RuntimeError("archive_metadata_cap_exceeded")
        eocd=data.rfind(b"PK\x05\x06")
        if eocd<0 or eocd+22>len(data):
            raise RuntimeError("zip_eocd_not_found")
        disk,cd_disk,n_disk,n_total,cd_size,cd_offset,comment_len=struct.unpack_from("<HHHHIIH",data,eocd+4)
        if disk!=0 or cd_disk!=0 or n_disk!=n_total:
            raise RuntimeError("multi_disk_zip_unsupported")
        if n_total in (0,0xffff) or cd_size==0xffffffff or cd_offset==0xffffffff:
            raise RuntimeError("zip64_or_empty_unsupported")
        try:
            range_part,total_s=cr.split(" ",1)[1].split("/")
            start_s,end_s=range_part.split("-")
            suffix_start=int(start_s); suffix_end=int(end_s); total=int(total_s)
        except Exception as exc:
            raise RuntimeError(f"invalid_content_range:{cr!r}") from exc
        rel=cd_offset-suffix_start
        if rel<0 or rel+cd_size>len(data):
            raise RuntimeError("central_directory_not_fully_in_suffix")
        pos=rel
        members=[]
        for _ in range(n_total):
            if data[pos:pos+4]!=b"PK\x01\x02":
                raise RuntimeError("central_directory_signature_mismatch")
            # fixed central directory header after signature
            vals=struct.unpack_from("<6H3I5H2I",data,pos+4)
            method=vals[3]; crc=vals[6]; csize=vals[7]; usize=vals[8]
            nlen=vals[9]; xlen=vals[10]; clen=vals[11]; loff=vals[15]
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
            "candidate_site_count":len(ids),
            "candidate_uuid_sha256":C["candidate_universe"]["candidate_uuid_sha256"],
            "head_content_type":hctype,
            "head_content_length":hlen,
            "head_filename_pattern_matches":bool(hdisp.startswith('attachment; filename="site_data_') and hdisp.endswith('.zip"')),
            "range_content_range":cr,
            "archive_total_bytes":total,
            "central_directory_offset":cd_offset,
            "central_directory_size":cd_size,
            "member_count":n_total,
            "members":members
        }
        out["safe_inventory"]=safe
        out["safe_inventory_fingerprint"]=canon(safe)
        out["status"]="gate1_zip_inventory_qualified"
        out["next_gate"]="freeze exact member-selection and payload parser before first member payload access"
    except Exception as exc:
        out["status"]="terminal_pre_response_zip_inventory_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
