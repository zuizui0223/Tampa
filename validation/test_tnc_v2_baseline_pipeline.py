#!/usr/bin/env python3
"""Self-test the Tampa TNC-v2 prospective baseline validator.

Cases:
1. Synthetic 36-node / four-bay baseline with 3 valid cores per node must PASS.
2. Same valid baseline with one bay below the frozen representation gate must
   return PASS_PILOT_ONLY rather than a confirmatory pass.
3. A future-response column in the baseline manifest must fail closed.

No real ecological outcome data are used.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
VALIDATOR = ROOT / "validation" / "validate_tnc_v2_baseline.py"
FREEZE_TEMPLATE = ROOT / "field" / "tnc_v2_precollection_freeze.json"
CONTRACT = ROOT / "results" / "clonal_state_prospective_v2_contract.json"

BAYS = [
    "Old Tampa Bay",
    "Middle Tampa Bay",
    "Lower Tampa Bay",
    "Boca Ciega Bay",
]

FIELDS = [
    "node_id","water_body","core_id","design_class","anchor_site_m",
    "latitude","longitude","transect_offset_m","collection_datetime",
    "baseline_survey_date","rhizome_tissue_class","core_diameter_cm",
    "core_depth_cm","preservation_start_datetime","preservation_method",
    "assay_batch","soluble_nsc_mg_g","starch_mg_g","leaf_n_pct",
    "leaf_p_pct","meristem_density","primary_qc_pass","exclusion_reason",
]


def run(*args, expect_ok=True):
    cp = subprocess.run(
        [PYTHON, *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if expect_ok and cp.returncode != 0:
        raise AssertionError(
            f"command failed ({cp.returncode}): {args}\n"
            f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        )
    if not expect_ok and cp.returncode == 0:
        raise AssertionError(
            f"command unexpectedly succeeded: {args}\nSTDOUT:\n{cp.stdout}"
        )
    return cp


def build_freeze(path: Path):
    x = json.loads(FREEZE_TEMPLATE.read_text(encoding="utf-8"))
    x["status"] = "SYNTHETIC_SELFTEST_ONLY"
    x["fields_to_freeze_before_first_outcome_bearing_core"].update({
        "campaign_start_date": "2030-08-01",
        "campaign_end_date": "2030-08-20",
        "horizontal_rhizome_tissue_class": (
            "live horizontal rhizome, proximal 3-cm segment associated with a "
            "living short shoot; exclude vertical rhizome and roots"
        ),
        "minimum_perpendicular_transect_offset_m": 1.0,
        "core_diameter_cm": 9.0,
        "core_depth_cm": 15.0,
        "maximum_collection_to_preservation_minutes": 30.0,
        "preservation_method": (
            "immediate liquid-nitrogen flash-freeze of cleaned target rhizome "
            "tissue, then frozen transport/storage and freeze-drying"
        ),
    })
    path.write_text(json.dumps(x, indent=2) + "\n", encoding="utf-8")
    return x


def write_manifest(path: Path, freeze: dict, nodes_per_bay: dict[str, int], add_future=False):
    fields = FIELDS + (["future_frequency"] if add_future else [])
    start = datetime(2030, 8, 2, 8, 0)
    rows = []
    node_counter = 0
    for bay_i, bay in enumerate(BAYS):
        for j in range(nodes_per_bay.get(bay, 0)):
            node_counter += 1
            node = f"N{node_counter:03d}"
            collect = start + timedelta(days=(node_counter - 1) % 15, hours=bay_i)
            baseline = collect.date()
            for core in range(1, 4):
                preserve = collect + timedelta(minutes=10 + core)
                row = {
                    "node_id": node,
                    "water_body": bay,
                    "core_id": f"{node}_C{core}",
                    "design_class": "synthetic_selftest",
                    "anchor_site_m": str(core * 10),
                    "latitude": "27.0",
                    "longitude": "-82.5",
                    "transect_offset_m": "1.0",
                    "collection_datetime": collect.strftime("%Y-%m-%d %H:%M:%S"),
                    "baseline_survey_date": baseline.isoformat(),
                    "rhizome_tissue_class": freeze["fields_to_freeze_before_first_outcome_bearing_core"]["horizontal_rhizome_tissue_class"],
                    "core_diameter_cm": "9",
                    "core_depth_cm": "15",
                    "preservation_start_datetime": preserve.strftime("%Y-%m-%d %H:%M:%S"),
                    "preservation_method": freeze["fields_to_freeze_before_first_outcome_bearing_core"]["preservation_method"],
                    "assay_batch": f"B{((node_counter + core) % 4) + 1}",
                    "soluble_nsc_mg_g": str(40 + core),
                    "starch_mg_g": str(60 + core),
                    "leaf_n_pct": "2.0",
                    "leaf_p_pct": "0.2",
                    "meristem_density": "5",
                    "primary_qc_pass": "true",
                    "exclusion_reason": "",
                }
                if add_future:
                    row["future_frequency"] = "0.9"
                rows.append(row)

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def validate(manifest: Path, freeze: Path, out: Path, expect_ok=True):
    cp = run(
        VALIDATOR,
        "--manifest", manifest,
        "--freeze", freeze,
        "--contract", "results/clonal_state_prospective_v2_contract.json",
        "--out", out,
        expect_ok=expect_ok,
    )
    return json.loads(out.read_text(encoding="utf-8")) if out.exists() else None


def main():
    with tempfile.TemporaryDirectory(prefix="tnc_v2_baseline_") as td:
        tmp = Path(td)
        freeze_path = tmp / "freeze.json"
        freeze = build_freeze(freeze_path)

        # 1) Confirmatory pass: 9 nodes per bay = 36 total.
        pass_manifest = tmp / "pass.csv"
        write_manifest(pass_manifest, freeze, {b: 9 for b in BAYS})
        pass_result = validate(pass_manifest, freeze_path, tmp / "pass.json")
        assert pass_result["status"] == "PASS_CONFIRMATORY_BASELINE", pass_result
        assert pass_result["valid_primary_nodes"] == 36, pass_result
        assert all(pass_result["valid_nodes_by_bay"][b] == 9 for b in BAYS), pass_result

        # 2) Representation failure without record-level QC error.
        # 11+11+10+4 = 36 total, but Boca Ciega is below frozen >=6 per-bay gate.
        pilot_manifest = tmp / "pilot.csv"
        write_manifest(
            pilot_manifest,
            freeze,
            {
                "Old Tampa Bay": 11,
                "Middle Tampa Bay": 11,
                "Lower Tampa Bay": 10,
                "Boca Ciega Bay": 4,
            },
        )
        pilot_result = validate(pilot_manifest, freeze_path, tmp / "pilot.json")
        assert pilot_result["status"] == "PASS_PILOT_ONLY", pilot_result
        assert pilot_result["valid_primary_nodes"] == 36, pilot_result
        assert pilot_result["confirmatory_replication_gate"] is False, pilot_result

        # 3) Baseline manifest must never contain future ecological response.
        bad_manifest = tmp / "future_leak.csv"
        write_manifest(bad_manifest, freeze, {b: 9 for b in BAYS}, add_future=True)
        run(
            VALIDATOR,
            "--manifest", bad_manifest,
            "--freeze", freeze_path,
            "--contract", "results/clonal_state_prospective_v2_contract.json",
            "--out", tmp / "future_leak.json",
            expect_ok=False,
        )

    print("TNC-v2 baseline validator self-test: OK")


if __name__ == "__main__":
    main()
