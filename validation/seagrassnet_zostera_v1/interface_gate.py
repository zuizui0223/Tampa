#!/usr/bin/env python3
"""Inspect only SeagrassNet public interface code and upload template."""
from __future__ import annotations
import csv, hashlib, html, io, json, re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"interface_contract.json").read_text())
P=json.loads((ROOT/"preflight_result.json").read_text())
OUT=ROOT/"interface_result.json"
BASE="https://www.seagrassnet.org"

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def fetch(url, max_bytes, ua):
    req=Request(url,headers={"Accept-Encoding":"identity","User-Agent":ua})
    with urlopen(req,timeout=60) as r:
        if r.status!=200:
            raise RuntimeError(f"http_{r.status}:{url}")
        b=r.read(max_bytes+1)
    if len(b)>max_bytes:
        raise RuntimeError(f"resource_too_large:{url}")
    return b

def snippets(text, keywords):
    out=[]
    low=text.lower()
    for k in keywords:
        start=0
        while True:
            i=low.find(k,start)
            if i<0: break
            a=max(0,i-260); z=min(len(text),i+520)
            s=re.sub(r"\s+"," ",text[a:z])
            if s not in out: out.append(s)
            start=i+len(k)
            if len(out)>=100: return out
    return out

def main():
    out={
        "schema":"tampa.seagrassnet_zostera_external_early_warning_v1.interface_result",
        "status":None,
        "biological_download_requests":0,
        "biological_download_bytes":0,
        "response_values_opened":False
    }
    try:
        if P["fingerprint"]!=C["requires_preflight_fingerprint"] or P["status"]!="preflight_interface_inventory_complete":
            raise RuntimeError("preflight_identity_or_status_mismatch")
        page=fetch(f"{BASE}/download",2_000_000,"Tampa-SeagrassNet-Interface/1.0").decode("utf-8")
        template=fetch(f"{BASE}/templates/data-upload-template.csv",1_000_000,"Tampa-SeagrassNet-Interface/1.0")
        rows=list(csv.reader(io.StringIO(template.decode("utf-8-sig"))))
        scripts=[]
        total=0
        for src in re.findall(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\']',page,flags=re.I):
            u=urljoin(BASE,html.unescape(src))
            if urlparse(u).netloc!="www.seagrassnet.org":
                continue
            b=fetch(u,2_000_000,"Tampa-SeagrassNet-Interface/1.0")
            total += len(b)
            if total>int(C["allowed_access"]["maximum_total_javascript_bytes"]):
                raise RuntimeError("javascript_total_exceeds_cap")
            txt=b.decode("utf-8",errors="replace")
            sn=snippets(txt,[
                "download","site_ids","siteids","selectedsites","selected_sites",
                "fetch(","axios","csv","blob","content-disposition","/api/","/download"
            ])
            scripts.append({
                "url":u,
                "sha256":hashlib.sha256(b).hexdigest(),
                "size":len(b),
                "relevant_snippets":sn
            })
        inline=snippets(page,[
            "download","site_ids","siteids","selectedsites","selected_sites",
            "fetch(","axios","csv","blob","/api/"
        ])
        safe={
            "download_page_sha256":hashlib.sha256(page.encode()).hexdigest(),
            "template_sha256":hashlib.sha256(template).hexdigest(),
            "template_rows":rows,
            "inline_interface_snippets":inline,
            "javascript_resources":scripts,
            "javascript_total_bytes":total
        }
        out["safe_interface"]=safe
        out["safe_interface_fingerprint"]=canon(safe)
        all_text=json.dumps({"inline":inline,"scripts":scripts},ensure_ascii=False).lower()
        endpoint_evidence=any(x in all_text for x in ["/api/","download"])
        site_shape=any(x in all_text for x in ["site_ids","siteids","selectedsites","selected_sites","site="])
        if not endpoint_evidence or not site_shape:
            out["status"]="terminal_pre_response_download_interface_stop"
            out["reason"]=f"insufficient_interface_evidence:endpoint={endpoint_evidence},site_shape={site_shape}"
            out["next_gate"]="none"
        else:
            out["status"]="gate1_interface_inventory_complete"
            out["next_gate"]="freeze exact biological download request and parser from recorded interface snippets before first data request"
    except Exception as exc:
        out["status"]="terminal_pre_response_interface_stop"
        out["reason"]=str(exc)
        out["next_gate"]="none"
    out["fingerprint"]=canon(out)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
