#!/usr/bin/env python3
"""Metadata-only Gate 0 for Alaska eelgrass external validation v1.

This stage is deliberately unable to download the biological response CSV.
It reads only the ScienceBase item metadata and records response-file identity.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
CONTRACT = json.loads((ROOT / "frozen_contract.json").read_text())
OUT = ROOT / "gate0_metadata_result.json"


def canonical_sha256(x):
    return hashlib.sha256(
        json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def main():
    url = CONTRACT["gate0_metadata_only"]["sciencebase_metadata_url"]
    req = Request(url, headers={
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "User-Agent": "Tampa-Alaska-Eelgrass-Gate0/1.0",
    })
    state = {
        "schema": "tampa.alaska_eelgrass_external_early_warning_v1.gate0_metadata_result",
        "status": None,
        "sciencebase_metadata_requests": 1,
        "response_csv_downloads": 0,
        "response_csv_bytes_opened": 0,
        "response_values_opened": False,
    }
    try:
        with urlopen(req, timeout=60) as resp:
            if resp.status != 200:
                raise RuntimeError(f"sciencebase_metadata_http_{resp.status}")
            raw = resp.read(5_000_001)
        if len(raw) > 5_000_000:
            raise RuntimeError("sciencebase_metadata_too_large")
        item = json.loads(raw.decode("utf-8"))
        expected_id = CONTRACT["source"]["sciencebase_item_id"]
        if str(item.get("id", "")) != expected_id:
            raise RuntimeError("sciencebase_item_id_mismatch")
        files = item.get("files")
        if not isinstance(files, list):
            raise RuntimeError("sciencebase_files_not_list")
        csvs = [f for f in files if str(f.get("name", "")).lower().endswith(".csv")]
        if len(csvs) != CONTRACT["gate0_metadata_only"]["required_csv_count"]:
            raise RuntimeError(f"expected_one_csv_found_{len(csvs)}")
        f = csvs[0]
        file_url = f.get("url") or f.get("downloadUri") or f.get("downloadURL")
        if not file_url:
            raise RuntimeError("csv_metadata_has_no_download_url")
        size = f.get("size")
        try:
            size_int = int(size)
        except Exception as exc:
            raise RuntimeError("csv_metadata_size_not_integer") from exc
        if size_int <= 0:
            raise RuntimeError("csv_metadata_size_not_positive")
        safe = {
            "item_id": str(item.get("id")),
            "title": str(item.get("title", "")),
            "citation": str(item.get("citation", "")),
            "provenance": item.get("provenance", {}),
            "csv": {
                "name": str(f.get("name", "")),
                "size": size_int,
                "contentType": str(f.get("contentType", "")),
                "url": str(file_url),
            },
        }
        state["status"] = "gate0_metadata_pass"
        state["safe_metadata"] = safe
        state["safe_metadata_fingerprint"] = canonical_sha256(safe)
        state["next_gate"] = (
            "freeze exact CSV identity and perform schema/header-only validation; "
            "no data rows or cover values may be opened until that contract is committed"
        )
    except Exception as exc:
        state["status"] = "terminal_pre_response_metadata_stop"
        state["reason"] = str(exc)
        state["next_gate"] = "none"
    state["fingerprint"] = canonical_sha256(state)
    OUT.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(json.dumps(state, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
