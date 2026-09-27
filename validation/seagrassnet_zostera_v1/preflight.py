#!/usr/bin/env python3
"""Response-blind SeagrassNet interface/schema preflight.

Fetches only public directory/site metadata, the download-form HTML, and the contributor
CSV template. It does not submit the download form or request biological site data.
"""
from __future__ import annotations
import csv, hashlib, html, io, json, re
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"preflight_contract.json").read_text())
OUT=ROOT/"preflight_result.json"
BASE="https://www.seagrassnet.org"

USA_CANADA_PREFIXES=(
    "BH74","CS49","CU69","CF72","CP73",
    "AL36","CH42","ME57","MD12","MA20","MS45","NH9","NY41","OR25","RN31","VI46","WA50"
)

def canon(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def fetch(url, ua):
    req=Request(url,headers={"Accept-Encoding":"identity","User-Agent":ua})
    with urlopen(req,timeout=60) as r:
        if r.status!=200:
            raise RuntimeError(f"http_{r.status}:{url}")
        return r.read()

def strip_tags(s):
    s=re.sub(r"<script\b[^>]*>.*?</script>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<style\b[^>]*>.*?</style>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",html.unescape(s)).strip()

def form_inventory(page):
    forms=[]
    for m in re.finditer(r"<form\b([^>]*)>(.*?)</form>",page,flags=re.I|re.S):
        attrs=m.group(1)
        body=m.group(2)
        action_m=re.search(r"\baction\s*=\s*['\"]([^'\"]*)",attrs,flags=re.I)
        method_m=re.search(r"\bmethod\s*=\s*['\"]([^'\"]*)",attrs,flags=re.I)
        inputs=[]
        for im in re.finditer(r"<(?:input|select|button)\b([^>]*)>",body,flags=re.I|re.S):
            a=im.group(1)
            name_m=re.search(r"\bname\s*=\s*['\"]([^'\"]*)",a,flags=re.I)
            type_m=re.search(r"\btype\s*=\s*['\"]([^'\"]*)",a,flags=re.I)
            value_m=re.search(r"\bvalue\s*=\s*['\"]([^'\"]*)",a,flags=re.I)
            inputs.append({
                "name": name_m.group(1) if name_m else "",
                "type": type_m.group(1) if type_m else "",
                "value": value_m.group(1) if value_m else ""
            })
        forms.append({
            "action": action_m.group(1) if action_m else "",
            "method": (method_m.group(1) if method_m else "GET").upper(),
            "inputs": inputs
        })
    return forms

def main():
    state={
        "schema":"tampa.seagrassnet_zostera_external_early_warning_v1.preflight_result",
        "status":None,
        "biological_download_requests":0,
        "biological_download_bytes":0,
        "response_values_opened":False
    }
    try:
        sites_html=fetch(C["metadata_sources"]["sites_page"],"Tampa-SeagrassNet-Preflight/1.0").decode("utf-8")
        download_html=fetch(C["metadata_sources"]["download_page"],"Tampa-SeagrassNet-Preflight/1.0").decode("utf-8")
        template=fetch(C["metadata_sources"]["upload_template"],"Tampa-SeagrassNet-Preflight/1.0")
        template_text=template.decode("utf-8-sig")
        template_rows=list(csv.reader(io.StringIO(template_text)))
        if not template_rows:
            raise RuntimeError("empty_template")
        template_header=[x.strip() for x in template_rows[0]]
        # Public site-directory links expose stable internal site UUIDs and visible site codes.
        candidates=[]
        for m in re.finditer(r'href=["\'](/sites/(site_[0-9a-f]+))["\'][^>]*>(.*?)</a>',sites_html,flags=re.I|re.S):
            path,uuid,label=m.group(1),m.group(2),strip_tags(m.group(3))
            code=(label.split()[0] if label else "")
            if code.startswith(USA_CANADA_PREFIXES):
                candidates.append({"uuid":uuid,"path":path,"label":label,"code":code})
        # If cards wrap code/name outside anchor, fall back to UUID links and fetch pages;
        # candidate geography remains frozen by accepted site-code prefixes on the fetched page.
        if len(candidates)<C["requirements"]["minimum_candidate_sites_before_response"]:
            raw_links=sorted(set(re.findall(r'/sites/(site_[0-9a-f]+)',sites_html,flags=re.I)))
            candidates=[]
            for uuid in raw_links:
                page=fetch(f"{BASE}/sites/{uuid}","Tampa-SeagrassNet-Preflight/1.0").decode("utf-8")
                text=strip_tags(page)
                code_match=re.search(r"\b([A-Z]{2}\d{1,2}\.\d+)\b",text)
                code=code_match.group(1) if code_match else ""
                if code.startswith(USA_CANADA_PREFIXES):
                    candidates.append({"uuid":uuid,"path":f"/sites/{uuid}","code":code,"metadata_text_sha256":hashlib.sha256(text.encode()).hexdigest()})
        if len(candidates)<C["requirements"]["minimum_candidate_sites_before_response"]:
            raise RuntimeError(f"too_few_candidate_sites:{len(candidates)}")

        forms=form_inventory(download_html)
        if not forms:
            raise RuntimeError("download_form_not_identified")
        safe={
            "sites_page_sha256":hashlib.sha256(sites_html.encode()).hexdigest(),
            "download_page_sha256":hashlib.sha256(download_html.encode()).hexdigest(),
            "template_sha256":hashlib.sha256(template).hexdigest(),
            "template_size":len(template),
            "template_header":template_header,
            "template_row_count":len(template_rows),
            "candidate_sites":sorted(candidates,key=lambda x:(x.get("code",""),x["uuid"])),
            "download_forms":forms
        }
        state["safe_interface"]=safe
        state["safe_interface_fingerprint"]=canon(safe)
        state["status"]="preflight_interface_inventory_complete"
        state["next_gate"]="freeze exact download endpoint, selected site UUID universe, parser, zero/missing semantics, annualization and once-only outcome rules before submitting any biological download"
    except Exception as exc:
        state["status"]="terminal_pre_response_interface_stop"
        state["reason"]=str(exc)
        state["next_gate"]="none"
    state["fingerprint"]=canon(state)
    OUT.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    print(json.dumps(state,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
