#!/usr/bin/env python3
"""Dryad metadata-only Gate0 for Northeast USA SeagrassNet v1.

This stage retrieves dataset/version/file descriptors only. It never follows a file
download link and never opens the README or biological response table.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT / "gate0_contract.json").read_text())
OUT = ROOT / "gate0_result.json"
API_ROOT = "https://datadryad.org"


def canon(x):
    return hashlib.sha256(
        json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def get_json(url):
    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "X-API-Version": "2.1.0",
            "User-Agent": "Tampa-Northeast-SeagrassNet-Gate0/1.0",
        },
    )
    with urlopen(req, timeout=60) as resp:
        if resp.status != 200:
            raise RuntimeError(f"metadata_http_{resp.status}:{url}")
        raw = resp.read(5_000_001)
    if len(raw) > 5_000_000:
        raise RuntimeError(f"metadata_too_large:{url}")
    return json.loads(raw.decode("utf-8"))


def embedded(obj, suffix):
    emb = obj.get("_embedded", {}) if isinstance(obj, dict) else {}
    for key, value in emb.items():
        if str(key).endswith(suffix) and isinstance(value, list):
            return value
    return []


def href(obj, suffix):
    links = obj.get("_links", {}) if isinstance(obj, dict) else {}
    for key, value in links.items():
        if str(key).endswith(suffix) and isinstance(value, dict) and value.get("href"):
            return urljoin(API_ROOT, str(value["href"]))
    return None


def slim_file(f):
    links = f.get("_links", {}) if isinstance(f, dict) else {}
    download = None
    for key, value in links.items():
        if "download" in str(key).lower() and isinstance(value, dict) and value.get("href"):
            download = urljoin(API_ROOT, str(value["href"]))
            break
    return {
        "id": f.get("id"),
        "path": str(f.get("path") or f.get("name") or f.get("filename") or ""),
        "size": f.get("size"),
        "digest": f.get("digest") or f.get("checksum"),
        "mimeType": f.get("mimeType") or f.get("mime_type"),
        "download_href": download,
    }


def main():
    state = {
        "schema": "tampa.northeast_seagrassnet_external_early_warning_v1.gate0_result",
        "status": None,
        "metadata_requests": 0,
        "file_download_requests": 0,
        "response_file_bytes_opened": 0,
        "response_values_opened": False,
    }
    try:
        dataset = get_json(C["source"]["api_dataset_url"])
        state["metadata_requests"] += 1
        identifier = str(dataset.get("identifier") or dataset.get("doi") or "")
        if "10.5061/dryad.z34tmpggg" not in identifier.lower():
            raise RuntimeError(f"dataset_identifier_mismatch:{identifier!r}")

        versions_obj = get_json(C["source"]["api_versions_url"])
        state["metadata_requests"] += 1
        versions = embedded(versions_obj, "versions")
        if not versions:
            # Some Dryad dataset responses expose the current version directly.
            vlink = href(dataset, "version")
            if not vlink:
                raise RuntimeError("no_version_metadata")
            current = get_json(vlink)
            state["metadata_requests"] += 1
            versions = [current]

        # Published public record; choose latest version deterministically.
        def vnum(v):
            try:
                return int(v.get("versionNumber", -1))
            except Exception:
                return -1
        versions = sorted(versions, key=vnum)
        selected = versions[-1]
        version_id = selected.get("id")
        if version_id is None:
            self_link = href(selected, "self")
            if self_link:
                version_id = self_link.rstrip("/").split("/")[-1]
        if version_id is None:
            raise RuntimeError("selected_version_has_no_id")

        files_url = f"{API_ROOT}/api/v2/versions/{version_id}/files"
        files_obj = get_json(files_url)
        state["metadata_requests"] += 1
        files = embedded(files_obj, "files")
        if not files and isinstance(files_obj, list):
            files = files_obj
        slim = [slim_file(f) for f in files]
        names = sorted(x["path"].split("/")[-1] for x in slim)
        expected = sorted(C["source"]["expected_file_names"])
        if names != expected:
            raise RuntimeError(f"unexpected_file_inventory:{names!r}")

        safe = {
            "dataset": {
                "identifier": identifier,
                "title": str(dataset.get("title", "")),
                "versionNumber": dataset.get("versionNumber"),
                "versionStatus": dataset.get("versionStatus"),
                "publicationDate": dataset.get("publicationDate"),
                "license": dataset.get("license"),
            },
            "selected_version": {
                "id": version_id,
                "versionNumber": selected.get("versionNumber"),
                "versionStatus": selected.get("versionStatus"),
                "publicationDate": selected.get("publicationDate"),
            },
            "files": slim,
        }
        state["status"] = "gate0_metadata_pass"
        state["safe_metadata"] = safe
        state["safe_metadata_fingerprint"] = canon(safe)
        state["next_gate"] = (
            "freeze the exact README file identity from this certificate, then open only "
            "README_seagrass_for_modeling.csv to define schema before any response-file GET"
        )
    except Exception as exc:
        state["status"] = "terminal_pre_response_metadata_stop"
        state["reason"] = str(exc)
        state["next_gate"] = "none"
    state["fingerprint"] = canon(state)
    OUT.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(json.dumps(state, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
