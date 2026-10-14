#!/usr/bin/env python3
"""Reproduce a history-only Tampa TNC meter-mark field reference.

Consumes the pinned 2023-2025 result of analysis/62. Never assigns present-day
eligibility, authorizes coring, changes q25/q50/q75, or reads future outcomes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BAYS = ("Old Tampa Bay", "Middle Tampa Bay", "Lower Tampa Bay", "Boca Ciega Bay")
CLASSES = ("q25", "q50", "q75")
RAW_COMMIT = "6c567beff95ea04f0e397101befb49d5233ace8f"
SOURCE_URL = "https://github.com/tbep-tech/obis-example/tree/" + RAW_COMMIT + "/dwc"
EXPECTED_COUNTS = {"Old Tampa Bay": (8, 8), "Middle Tampa Bay": (11, 10),
                   "Lower Tampa Bay": (14, 12), "Boca Ciega Bay": (8, 8)}
ANCHOR_HEADER = ["node_id", "water_body", "historical_year", "anchor_class",
                 "historical_site_m", "historical_bb_mean", "reference_status",
                 "current_location_check", "field_notes", "source_url"]
NODE_HEADER = ["node_id", "water_body", "historical_year",
               "historical_positive_mark_count", "historical_triplet_feasible",
               "historical_anchor_site_m", "current_eligibility_recheck",
               "field_notes"]


def construct(raw: dict) -> tuple[list[list], list[list], dict]:
    if raw.get("schema") != "tampa.tnc_anchor_bb_four_bay_preflight_v1":
        raise ValueError("unexpected preflight schema")
    if raw.get("source", {}).get("commit") != RAW_COMMIT:
        raise ValueError("unpinned biological source")
    if raw.get("status") != "anchor_level_quantitative_diagnostic_feasible":
        raise ValueError("historical preflight does not pass")
    nodes = raw.get("nodes")
    marks = raw.get("anchors")
    if not isinstance(nodes, list) or len(nodes) != 41 or not isinstance(marks, list) or len(marks) != 114:
        raise ValueError("historical 41/114 registry changed")
    by_node = defaultdict(list)
    for item in marks:
        nid = item["node_id"]
        if nid is None:
            raise ValueError("missing mark node ID")
        by_node[nid].append(item)

    anchor_rows = []
    node_rows = []
    seen_nodes = set()
    totals = Counter()
    eligible = Counter()
    for node in sorted(nodes, key=lambda x: (x["water_body"], x["node_id"])):
        nid, bay, year = node["node_id"], node["water_body"], int(node["year"])
        if not nid or nid in seen_nodes or bay not in BAYS or year not in (2023, 2024, 2025):
            raise ValueError("duplicate/invalid historical node")
        seen_nodes.add(nid)
        totals[bay] += 1
        selected = node["anchor_site_m"]
        is_triplet = bool(node["anchors_all_quantitative_bb"])
        if is_triplet:
            if not node["three_distinct_anchor_design"] or len(selected) != 3 or len(set(selected)) != 3:
                raise ValueError(f"{nid}: invalid ordered historical q25/q50/q75 marks")
            a = by_node[nid]
            if len(a) != 3 or len({m["site_m"] for m in a}) != 3:
                raise ValueError(f"{nid}: missing or duplicated quantitative mark records")
            eligible[bay] += 1
            for cls, site in zip(CLASSES, selected):
                match = [m for m in a if m["site_m"] == site]
                if len(match) != 1:
                    raise ValueError(f"{nid}: mark does not map uniquely to source record")
                row = match[0]
                bb = row["baseline_bb_mean"]
                if (row["water_body"] != bay or int(row["year"]) != year
                        or row["quantitative_baseline_ok"] is not True
                        or not isinstance(bb, (int, float)) or not math.isfinite(float(bb))):
                    raise ValueError(f"{nid}: inconsistent or incomplete historical BB")
                anchor_rows.append([nid, bay, year, cls, float(site), float(bb),
                                    "HISTORICAL_REFERENCE_ONLY", "Not checked", "", SOURCE_URL])
        else:
            if selected or by_node.get(nid, []) or int(node["positive_meter_marks"]) >= 3:
                raise ValueError(f"{nid}: sparse node contradicts historical anchor registry")
        node_rows.append([nid, bay, year, int(node["positive_meter_marks"]),
                          "Yes" if is_triplet else "No",
                          ", ".join(str(x) for x in selected) if selected
                          else "Insufficient positive marks",
                          "Not checked", ""])

    if set(by_node) != seen_nodes - {x[0] for x in node_rows if x[4] == "No"}:
        raise ValueError("orphan or missing historical anchor records")
    for bay in BAYS:
        if (totals[bay], eligible[bay]) != EXPECTED_COUNTS[bay]:
            raise ValueError(f"{bay}: historical coverage mismatch")
    if len(anchor_rows) != 114 or sum(eligible.values()) != 38:
        raise ValueError("historical complete-node denominator drift")
    counts = raw["frozen_gate"]
    if (counts["nodes_with_three_distinct_quantitative_bb_anchors"] != 38
            or counts["minimum_nodes_with_three_distinct_quantitative_anchors"] != 36
            or counts["minimum_nodes_per_bay"] != 6 or counts["passed"] is not True):
        raise ValueError("historical frozen gate drift")
    report = {
        "schema": "tampa.historical_tnc_anchor_reference_2023_2025_v1",
        "status": "HISTORICAL_REFERENCE_NOT_A_FROZEN_FUTURE_ANCHOR_MANIFEST",
        "pinned_raw_source_commit": RAW_COMMIT,
        "source_preflight": "analysis/62_tnc_anchor_bb_four_bay_preflight.py",
        "historical_positive_nodes": len(node_rows),
        "historical_quantitative_three_anchor_nodes": 38,
        "historical_mark_records": len(anchor_rows),
        "bay_counts": {b: {"historically_positive": totals[b],
                           "historical_complete_triplet": eligible[b]} for b in BAYS},
        "boundary": [
            "Historical q25/q50/q75 mark IDs are field-reconnaissance references only.",
            "Do not authorize coring from this archival table or use old BB values as contemporary baseline.",
            "Recheck current focal presence, three unique quantitative anchors, permissions, non-disturbance offset and prospective source registry before any outcome-bearing core.",
            "Do not select or replace field anchors on the basis of HPLC or future ecological response.",
            "This archive contains no new TNC, future meadow response or ecological mechanism evidence."
        ],
    }
    return anchor_rows, node_rows, report


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def self_test() -> None:
    nodes, marks = [], []
    for bi, (bay, (positive, complete)) in enumerate(EXPECTED_COUNTS.items()):
        for n in range(positive):
            nid = f"synthetic-{bi}-{n}"
            ok = n < complete
            sites = [20.0, 40.0, 60.0] if ok else []
            nodes.append({"node_id": nid, "water_body": bay, "year": 2025,
                          "positive_meter_marks": 3 if ok else 1,
                          "three_distinct_anchor_design": ok,
                          "anchors_all_quantitative_bb": ok, "anchor_site_m": sites})
            for site in sites:
                marks.append({"node_id": nid, "water_body": bay, "year": 2025,
                              "site_m": site, "baseline_bb_mean": 1.5,
                              "quantitative_baseline_ok": True})
    inp = {"schema": "tampa.tnc_anchor_bb_four_bay_preflight_v1",
           "source": {"commit": RAW_COMMIT},
           "status": "anchor_level_quantitative_diagnostic_feasible",
           "nodes": nodes, "anchors": marks,
           "frozen_gate": {"nodes_with_three_distinct_quantitative_bb_anchors": 38,
                            "minimum_nodes_with_three_distinct_quantitative_anchors": 36,
                            "minimum_nodes_per_bay": 6, "passed": True}}
    a, n, _ = construct(inp)
    assert len(a) == 114 and len(n) == 41
    changed = json.loads(json.dumps(inp))
    changed["nodes"][0]["anchor_site_m"][1] = 20.0
    try:
        construct(changed)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate selected meter-mark should fail")
    changed = json.loads(json.dumps(inp))
    changed["anchors"][0]["baseline_bb_mean"] = None
    try:
        construct(changed)
    except ValueError:
        pass
    else:
        raise AssertionError("missing numeric baseline BB should fail")
    print("PASS: history-only 41/38/114 crosswalk and fail-closed mismatched marks")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path,
                    default=Path("results/generated_tnc_anchor_bb_four_bay/tnc_anchor_bb_four_bay_preflight_v1.json"))
    ap.add_argument("--out-dir", type=Path,
                    default=Path("results/generated_tnc_anchor_bb_four_bay"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    data = args.source.read_bytes()
    rows, nodes, report = construct(json.loads(data))
    report["historical_preflight_json_sha256"] = hashlib.sha256(data).hexdigest()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "historical_tnc_anchor_marks_2023_2025.csv", ANCHOR_HEADER, rows)
    write_csv(args.out_dir / "historical_tnc_candidate_nodes_2023_2025.csv", NODE_HEADER, nodes)
    (args.out_dir / "historical_tnc_anchor_reference_v1.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "status", "historical_positive_nodes",
        "historical_quantitative_three_anchor_nodes", "historical_mark_records")}, indent=2))


if __name__ == "__main__":
    main()
