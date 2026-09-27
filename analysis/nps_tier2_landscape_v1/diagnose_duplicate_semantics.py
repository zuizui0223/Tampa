#!/usr/bin/env python3
"""Second-stage structure diagnostic for repeated Tier-2 quadrat/species rows.

The response is already open in this post-hoc ecology line. This diagnostic does not
compute ecological trends or choose an aggregation. It asks which columns differ within
repeated Event_Code x Quadrat_Ltr x Species groups.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
C = json.loads((HERE / "analysis_contract.json").read_text())
OUT = HERE / "duplicate_semantics_result.json"

KEY = ["Event_Code", "Quadrat_Ltr", "Species"]
IGNORE_ID = {"QuadratData_ID"}

def norm(x):
    return "" if x is None else str(x).strip()

def main():
    req = Request(
        C["source"]["csv_url"],
        headers={"Accept-Encoding": "identity", "User-Agent": "Tampa-NPS-Tier2-DuplicateDiag/1.0"},
    )
    with urlopen(req, timeout=90) as r:
        if r.status != 200:
            raise RuntimeError(f"csv_http_{r.status}")
        data = r.read(20_000_001)

    rd = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    header = list(rd.fieldnames or [])
    if header != C["source"]["expected_header"]:
        raise RuntimeError("header_drift")

    groups = defaultdict(list)
    for i, row in enumerate(rd, start=2):
        key = tuple(norm(row[k]) for k in KEY)
        rec = {h: norm(row[h]) for h in header}
        rec["_row"] = i
        groups[key].append(rec)

    repeated = {k: v for k, v in groups.items() if len(v) > 1}
    varied_counts = Counter()
    varied_patterns = Counter()
    exact_except_id = 0
    exact_except_id_and_cert = 0
    exact_except_id_cover_same = 0
    examples = []

    for key, rows in repeated.items():
        varied = []
        for col in header:
            vals = {r[col] for r in rows}
            if len(vals) > 1:
                varied.append(col)
                varied_counts[col] += 1
        varied_patterns[tuple(varied)] += 1

        non_id = [c for c in header if c not in IGNORE_ID]
        if all(len({r[c] for r in rows}) == 1 for c in non_id):
            exact_except_id += 1

        non_admin = [c for c in header if c not in {"QuadratData_ID", "Certified_Date", "Certified_By", "QC_notes"}]
        if all(len({r[c] for r in rows}) == 1 for c in non_admin):
            exact_except_id_and_cert += 1

        if len({r["Percent_Cover"] for r in rows}) == 1:
            exact_except_id_cover_same += 1

        if len(examples) < 30:
            examples.append(
                {
                    "key": list(key),
                    "n": len(rows),
                    "varied_columns": varied,
                    "rows": [
                        {c: r[c] for c in header if c in set(varied) | {
                            "QuadratData_ID", "Percent_Cover", "Average_Stem_Ht_cm",
                            "Average_Max_Shoot_Ht_cm", "Average_Max_Shoot_Width_mm",
                            "Average_Number_Lvs", "Shoot_Count", "Biomass",
                            "Biomass_stems", "Biomass_roots", "Grazing Evidence",
                            "Epiphytes", "Wasting", "Certified_By", "Certified_Date", "QC_notes"
                        }}
                        for r in rows
                    ],
                }
            )

    # Compact descriptions of the most common within-group variation patterns.
    pattern_rows = [
        {"varied_columns": list(cols), "group_count": int(n)}
        for cols, n in varied_patterns.most_common(30)
    ]

    out = {
        "schema": "tampa.nps_tier2_landscape_state_v1.duplicate_semantics_diagnostic",
        "csv_bytes": len(data),
        "repeated_group_count": len(repeated),
        "exact_except_quadrat_data_id_group_count": exact_except_id,
        "exact_except_id_certification_qc_group_count": exact_except_id_and_cert,
        "same_percent_cover_group_count": exact_except_id_cover_same,
        "columns_varying_within_repeated_groups": {
            col: int(n) for col, n in varied_counts.most_common()
        },
        "common_variation_patterns": pattern_rows,
        "examples": examples,
        "interpretation_rule": (
            "No aggregation or deduplication is authorized by this diagnostic. "
            "Its sole purpose is to distinguish exact duplicate biological states from "
            "rows representing distinct subordinate measurements."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
