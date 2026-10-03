#!/usr/bin/env python3
"""Validate the committed Tampa TNC v2 historical candidate registry."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "field/tnc_v2_historical_candidate_nodes.csv"

EXPECTED = {
    "Old Tampa Bay": 8,
    "Middle Tampa Bay": 11,
    "Lower Tampa Bay": 14,
    "Boca Ciega Bay": 8,
}
VALID_DESIGNS = {
    "three_spatial_anchors",
    "two_marks_one_replicated_anchor",
    "single_mark_three_offsets",
}


def main() -> None:
    with PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    counts = Counter(r["water_body"] for r in rows)
    errors = []

    if len(rows) != 41:
        errors.append(f"row count {len(rows)} != 41")
    if dict(counts) != EXPECTED:
        errors.append(f"bay counts {dict(counts)!r} != {EXPECTED!r}")

    ids = [r["node_id"] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate node_id")

    for i, row in enumerate(rows, start=2):
        if row["historical_only"] != "TRUE":
            errors.append(f"row {i}: historical_only must be TRUE")
        if row["contemporaneous_eligibility"] != "PENDING":
            errors.append(f"row {i}: contemporaneous eligibility must start PENDING")
        if row["design_class"] not in VALID_DESIGNS:
            errors.append(f"row {i}: invalid design class")
        for field in ("anchor1_site_m", "anchor2_site_m", "anchor3_site_m"):
            try:
                float(row[field])
            except Exception:
                errors.append(f"row {i}: nonnumeric {field}")

    result = {
        "schema": "tampa.tnc_v2_candidate_registry_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "rows": len(rows),
        "by_water_body": dict(counts),
        "errors": errors,
        "boundary": (
            "PASS certifies reproducible historical planning state only, "
            "not current biological eligibility for coring."
        ),
    }
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
