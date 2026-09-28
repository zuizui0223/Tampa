#!/usr/bin/env python3
"""Response-blind ArcGIS schema inventory for Sarasota County Seagrass Monitoring.

This script is intentionally forbidden from querying feature records. It uses only:
1. ArcGIS Sharing item search/metadata endpoints; and
2. FeatureServer service/layer definition endpoints ending in ?f=json.

No /query endpoint is called and no biological response values are requested.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SEARCH = "https://www.arcgis.com/sharing/rest/search"
ITEM = "https://www.arcgis.com/sharing/rest/content/items/{item_id}"
TITLE = "SeagrassScallopArchiveLayer"
USER_AGENT = "Tampa-Sarasota-StateMemory-SchemaGate/1.0"

FORBIDDEN = re.compile(r"/query(?:\?|$)", re.I)

ID_TERMS = ("site", "station", "location", "sample", "point", "fixed", "random", "type")
TIME_TERMS = ("date", "year", "survey")
STATE_TERMS = ("seagrass", "grass", "sav", "present", "presence", "absence", "cover", "percent", "pct")


def get_json(url: str) -> dict:
    if FORBIDDEN.search(url):
        raise RuntimeError(f"forbidden response-record endpoint: {url}")
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = resp.read()
    obj = json.loads(raw)
    if isinstance(obj, dict) and "error" in obj:
        raise RuntimeError(f"ArcGIS metadata error for {url}: {obj['error']}")
    return obj


def meta_url(base: str, **params) -> str:
    sep = "&" if "?" in base else "?"
    return base + sep + urllib.parse.urlencode({"f": "json", **params})


def compact_domain(domain):
    if not domain:
        return None
    out = {"type": domain.get("type"), "name": domain.get("name")}
    coded = domain.get("codedValues")
    if isinstance(coded, list):
        out["codedValues"] = [
            {"name": x.get("name"), "code": x.get("code")}
            for x in coded[:100]
        ]
    if domain.get("minValue") is not None:
        out["minValue"] = domain.get("minValue")
    if domain.get("maxValue") is not None:
        out["maxValue"] = domain.get("maxValue")
    return out


def score_field(name: str, alias: str) -> list[str]:
    s = f"{name} {alias}".lower()
    tags = []
    if any(t in s for t in ID_TERMS):
        tags.append("identity_or_sampling")
    if any(t in s for t in TIME_TERMS):
        tags.append("time")
    if any(t in s for t in STATE_TERMS):
        tags.append("state")
    return tags


def main(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    audit = {
        "schema": "tampa.sarasota_state_memory_v1.arcgis_schema_inventory",
        "status": "started",
        "response_values_opened": False,
        "feature_query_requests": 0,
        "metadata_requests": [],
        "search_title": TITLE,
    }

    q = f'title:"{TITLE}"'
    search_url = meta_url(SEARCH, q=q, num=100)
    search = get_json(search_url)
    audit["metadata_requests"].append({"kind": "sharing_search", "url": search_url})

    candidates = []
    for x in search.get("results", []):
        title = str(x.get("title", ""))
        if title.casefold() != TITLE.casefold():
            continue
        candidates.append({
            "id": x.get("id"),
            "title": title,
            "type": x.get("type"),
            "owner": x.get("owner"),
            "url": x.get("url"),
            "description_present": bool(x.get("description")),
            "tags": x.get("tags", []),
        })
    audit["exact_title_candidates"] = candidates

    if not candidates:
        audit["status"] = "terminal_pre_response_item_not_found"
        (outdir / "arcgis_schema_inventory.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
        print(json.dumps(audit, indent=2, sort_keys=True))
        return

    # We do not choose among multiple biological datasets based on response content.
    # Inventory every exact-title Feature Service and require a later frozen identity decision.
    services = []
    for c in candidates:
        item_id = c["id"]
        item_url = meta_url(ITEM.format(item_id=item_id))
        item = get_json(item_url)
        audit["metadata_requests"].append({"kind": "item_metadata", "url": item_url})
        service_url = item.get("url") or c.get("url")
        rec = {
            "id": item_id,
            "title": item.get("title"),
            "type": item.get("type"),
            "owner": item.get("owner"),
            "service_url": service_url,
            "layers": [],
        }
        if service_url and "FeatureServer" in service_url:
            service_meta_url = meta_url(service_url.rstrip("/"))
            service = get_json(service_meta_url)
            audit["metadata_requests"].append({"kind": "service_definition", "url": service_meta_url})
            for lyr in service.get("layers", []):
                lid = lyr.get("id")
                layer_url = meta_url(service_url.rstrip("/") + f"/{lid}")
                layer = get_json(layer_url)
                audit["metadata_requests"].append({"kind": "layer_definition", "url": layer_url})
                fields = []
                for f in layer.get("fields", []):
                    name = str(f.get("name", ""))
                    alias = str(f.get("alias", ""))
                    fields.append({
                        "name": name,
                        "alias": alias,
                        "type": f.get("type"),
                        "nullable": f.get("nullable"),
                        "domain": compact_domain(f.get("domain")),
                        "schema_tags": score_field(name, alias),
                    })
                rec["layers"].append({
                    "id": lid,
                    "name": layer.get("name"),
                    "object_id_field": layer.get("objectIdField"),
                    "global_id_field": layer.get("globalIdField"),
                    "display_field": layer.get("displayField"),
                    "fields": fields,
                })
        services.append(rec)

    audit["services"] = services
    audit["status"] = "schema_inventory_complete_review_required"
    audit["next_rule"] = (
        "Review schema only. Pass requires an unambiguous persistent fixed-site identifier, "
        "fixed/random semantics, calendar date/year, explicit all-seagrass presence/absence, "
        "explicit total percent cover 0-100, and sampled-zero semantics distinct from missing. "
        "If these cannot be established without feature records, terminate before response opening."
    )
    audit["response_values_opened"] = False
    audit["feature_query_requests"] = 0

    out = outdir / "arcgis_schema_inventory.json"
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/generated_sarasota_schema")
    main(out)
