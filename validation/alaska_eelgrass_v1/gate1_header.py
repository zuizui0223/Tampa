#!/usr/bin/env python3
"""Header-only Gate 1 for Alaska eelgrass v1.

Reads exactly the physical CSV header, one ranged byte at a time, and stops at LF.
No data-row byte is authorized.
"""
from __future__ import annotations
import csv, hashlib, io, json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
G0 = json.loads((ROOT / "gate0_metadata_result.json").read_text())
C = json.loads((ROOT / "gate1_header_contract.json").read_text())
OUT = ROOT / "gate1_header_result.json"


def canon(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def main():
    out = {
        "schema": "tampa.alaska_eelgrass_external_early_warning_v1.gate1_header_result",
        "status": None,
        "requires_gate0_fingerprint": C["requires_gate0_fingerprint"],
        "data_row_bytes_opened": 0,
        "response_values_opened": False,
    }
    try:
        if G0["fingerprint"] != C["requires_gate0_fingerprint"] or G0["status"] != "gate0_metadata_pass":
            raise RuntimeError("gate0_identity_or_status_mismatch")
        frozen = C["csv_identity"]
        observed = G0["safe_metadata"]["csv"]
        if observed["name"] != frozen["name"] or int(observed["size"]) != int(frozen["size"]) or observed["url"] != frozen["url"]:
            raise RuntimeError("csv_identity_drift")
        buf = bytearray()
        max_bytes = int(C["allowed_access"]["maximum_header_bytes"])
        request_count = 0
        for i in range(max_bytes):
            req = Request(
                frozen["url"],
                headers={
                    "Range": f"bytes={i}-{i}",
                    "Accept-Encoding": "identity",
                    "User-Agent": "Tampa-Alaska-Eelgrass-Gate1/1.0",
                },
            )
            request_count += 1
            with urlopen(req, timeout=60) as resp:
                if resp.status != 206:
                    raise RuntimeError(f"range_not_honored_http_{resp.status}_at_byte_{i}")
                cr = resp.headers.get("Content-Range", "")
                expected = f"bytes {i}-{i}/{frozen['size']}"
                if cr != expected:
                    raise RuntimeError(f"content_range_mismatch_at_byte_{i}:{cr!r}")
                b = resp.read(2)
            if len(b) != 1:
                raise RuntimeError(f"range_returned_{len(b)}_bytes_at_{i}")
            buf.extend(b)
            if b == b"\n":
                break
        else:
            raise RuntimeError("header_exceeds_frozen_maximum")
        physical = bytes(buf)
        # Because retrieval stopped exactly at LF, no following row byte was read.
        text = physical.decode("utf-8")
        line = text[:-1]
        if line.endswith("\r"):
            line = line[:-1]
            terminator = "CRLF"
        else:
            terminator = "LF"
        row = next(csv.reader(io.StringIO(line)))
        if not row or any(not str(x).strip() for x in row):
            raise RuntimeError("empty_or_blank_header_cell")
        if len(set(row)) != len(row):
            raise RuntimeError("duplicate_header_name")
        safe = {
            "header": row,
            "column_count": len(row),
            "terminator": terminator,
            "physical_header_bytes": len(physical),
            "header_sha256": hashlib.sha256(physical).hexdigest(),
            "range_request_count": request_count,
        }
        out["status"] = "gate1_header_pass"
        out["safe_header"] = safe
        out["next_gate"] = "freeze exact parser and statistical endpoint from this header before opening any data row"
    except Exception as exc:
        out["status"] = "terminal_pre_response_header_stop"
        out["reason"] = str(exc)
        out["next_gate"] = "none"
    out["fingerprint"] = canon(out)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
