#!/usr/bin/env python3
"""Export the historical four-bay TNC candidate-node registry.

This is a field-planning registry only.

It reuses the pinned response-open feasibility logic in:
  analysis/60_bcb_tnc_expansion_preflight.py

The output does NOT establish current eligibility. Every node must be
re-evaluated at the contemporaneous baseline before coring.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "analysis/60_bcb_tnc_expansion_preflight.py"

EXPECTED_BY_BAY = {
    "Old Tampa Bay": 8,
    "Middle Tampa Bay": 11,
    "Lower Tampa Bay": 14,
    "Boca Ciega Bay": 8,
}


def load_preflight_module():
    spec = importlib.util.spec_from_file_location("tampa_bcb_preflight", SRC)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def nearest_unique(vals: list[float], target: float, used: set[float]) -> float:
    candidates = sorted(
        (abs(x - target), x)
        for x in vals
        if x not in used
    )
    if not candidates:
        raise RuntimeError("unique anchor assignment failed")
    return float(candidates[0][1])


def assign_anchors(vals: list[float]) -> tuple[str, list[float]]:
    vals = sorted(set(float(x) for x in vals))
    if not vals:
        raise RuntimeError("positive node has no historical positive meter marks")

    if len(vals) >= 3:
        q = np.quantile(np.asarray(vals, float), [0.25, 0.50, 0.75])
        used: set[float] = set()
        anchors = []
        for target in q:
            hit = nearest_unique(vals, float(target), used)
            anchors.append(hit)
            used.add(hit)
        return "three_spatial_anchors", anchors

    if len(vals) == 2:
        midpoint = float(np.mean(vals))
        third = min(vals, key=lambda x: (abs(x - midpoint), x))
        return "two_marks_one_replicated_anchor", [vals[0], vals[1], third]

    return "single_mark_three_offsets", [vals[0], vals[0], vals[0]]


def main(out: Path) -> None:
    m = load_preflight_module()

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "preflight.json"
        m.main(tmp)
        preflight = json.loads(tmp.read_text(encoding="utf-8"))

    if preflight["status"] != "four_bay_tnc_expansion_feasible":
        raise RuntimeError("four-bay feasibility no longer passes")

    rows = []
    for node in preflight["nodes"]:
        design, anchors = assign_anchors(node["positive_site_m"])
        rows.append({
            "node_id": node["node_id"],
            "water_body": node["water_body"],
            "historical_latest_year": node["year"],
            "historical_focal_frequency": node["focal_frequency"],
            "positive_meter_marks": node["positive_meter_marks"],
            "design_class": design,
            "anchor1_site_m": anchors[0],
            "anchor2_site_m": anchors[1],
            "anchor3_site_m": anchors[2],
            "historical_only": "TRUE",
            "contemporaneous_eligibility": "PENDING",
        })

    rows.sort(key=lambda x: (x["water_body"], x["node_id"]))

    counts = {}
    for row in rows:
        counts[row["water_body"]] = counts.get(row["water_body"], 0) + 1

    if len(rows) != 41:
        raise RuntimeError(f"candidate-node drift: {len(rows)} != 41")
    if counts != EXPECTED_BY_BAY:
        raise RuntimeError(
            f"bay-count drift: {counts!r} != {EXPECTED_BY_BAY!r}"
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "node_id",
        "water_body",
        "historical_latest_year",
        "historical_focal_frequency",
        "positive_meter_marks",
        "design_class",
        "anchor1_site_m",
        "anchor2_site_m",
        "anchor3_site_m",
        "historical_only",
        "contemporaneous_eligibility",
    ]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({
        "status": "historical_candidate_registry_exported",
        "rows": len(rows),
        "by_water_body": counts,
        "output": str(out),
        "boundary": (
            "Historical 2023-2025 state is field-planning evidence only. "
            "Contemporaneous baseline Thalassia eligibility must be rechecked "
            "before any outcome-bearing core."
        ),
    }, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "field/tnc_v2_historical_candidate_nodes.csv",
    )
    args = ap.parse_args()
    main(args.out)
