#!/usr/bin/env python3
"""Self-test the Tampa TNC-v2 raw-pilot -> validation -> freeze-handoff pipeline.

Cases:
1. Repository blank templates must build without crashing and validator must STOP.
2. Synthetic fully passing pilot must return PASS_METHOD_PILOT.
3. One individual matrix-spike recovery outside 85-115% must fail even when
   the mean matrix-spike recovery remains acceptable.
4. PASS handoff must preserve the exact candidate/raw-pilot provenance.

No ecological response data are used.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
BUILDER = ROOT / "validation" / "build_tnc_v2_method_pilot_summary.py"
VALIDATOR = ROOT / "validation" / "validate_tnc_v2_method_pilot.py"
APPLY = ROOT / "analysis" / "69_apply_tnc_v2_method_pilot.py"
CANONICAL = ROOT / "field" / "tnc_v2_method_pilot.json"
FREEZE = ROOT / "field" / "tnc_v2_precollection_freeze.json"


def run(*args):
    cp = subprocess.run(
        [PYTHON, *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if cp.returncode != 0:
        raise AssertionError(
            f"command failed ({cp.returncode}): {args}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        )
    return cp


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def build_candidate(tmp, prefix, hplc_obj, metadata_obj, tissue_rows, geometry_rows, offset_rows, preservation_rows):
    meta = tmp / f"{prefix}_metadata.json"
    hplc = tmp / f"{prefix}_hplc.json"
    tissue = tmp / f"{prefix}_tissue.csv"
    geom = tmp / f"{prefix}_geometry.csv"
    offset = tmp / f"{prefix}_offset.csv"
    pres = tmp / f"{prefix}_preservation.csv"
    candidate = tmp / f"{prefix}_candidate.json"
    audit = tmp / f"{prefix}_audit.json"

    write_json(meta, metadata_obj)
    write_json(hplc, hplc_obj)
    write_csv(
        tissue,
        [
            "candidate_rank","candidate_name","specimen_id",
            "classification_unambiguous","dry_mass_sufficient",
            "destructive_guardrail_pass",
        ],
        tissue_rows,
    )
    write_csv(
        geom,
        [
            "candidate_rank","core_diameter_cm","core_depth_cm","attempt_id",
            "live_horizontal_rhizome_recovered","dry_mass_sufficient",
            "guardrail_pass","three_anchor_feasible",
        ],
        geometry_rows,
    )
    write_csv(
        offset,
        [
            "candidate_offset_m","placement_id","permit_boundary_pass",
            "permanent_transect_protected","placement_reproducible",
            "restoration_workspace_pass",
        ],
        offset_rows,
    )
    write_csv(
        pres,
        [
            "method","delay_minutes","specimen_id","immediate_tnc_mg_g",
            "delayed_tnc_mg_g","physically_suitable",
        ],
        preservation_rows,
    )

    run(
        BUILDER,
        "--canonical", CANONICAL,
        "--metadata", meta,
        "--hplc", hplc,
        "--tissue", tissue,
        "--geometry", geom,
        "--offset", offset,
        "--preservation", pres,
        "--out", candidate,
        "--audit-out", audit,
    )
    return candidate


def validate(candidate, out):
    run(VALIDATOR, "--pilot", candidate, "--out", out)
    return json.loads(out.read_text(encoding="utf-8"))


def synthetic_passing_inputs(matrix_spikes=None):
    if matrix_spikes is None:
        matrix_spikes = [95.0, 100.0, 105.0]

    metadata = {
        "schema": "tampa.tnc_v2_raw_pilot_metadata.v1",
        "outcome_response_accessed": False,
        "independent_rhizome_specimens": 8,
        "collection_locations_or_batches": 2,
        "field_core_attempts": 10,
    }

    hplc = {
        "schema": "tampa.tnc_v2_hplc_matrix_pilot.v1",
        "calibration_identity_unambiguous": True,
        "analytical_blank_below_loq": True,
        "post_high_standard_carryover_below_loq": True,
        "standard_recovery_pct": [99.0, 101.0],
        "matrix_spike_recovery_pct": matrix_spikes,
        "technical_duplicate_pairs": [
            {"pair_id": f"d{i}", "tnc_a_mg_g": 100.0, "tnc_b_mg_g": 102.0}
            for i in range(8)
        ],
        "extract_calibration_range": [
            {"extract_id": f"e{i}", "all_primary_analytes_in_range": True}
            for i in range(10)
        ],
    }

    tissue_rows = [
        {
            "candidate_rank": 1,
            "candidate_name": "3 cm",
            "specimen_id": f"t{i}",
            "classification_unambiguous": "true",
            "dry_mass_sufficient": "true",
            "destructive_guardrail_pass": "true",
        }
        for i in range(8)
    ]

    geometry_rows = [
        {
            "candidate_rank": 1,
            "core_diameter_cm": 9,
            "core_depth_cm": 15,
            "attempt_id": f"g{i}",
            "live_horizontal_rhizome_recovered": "true",
            "dry_mass_sufficient": "true",
            "guardrail_pass": "true",
            "three_anchor_feasible": "true",
        }
        for i in range(10)
    ]

    offset_rows = [
        {
            "candidate_offset_m": 1.0,
            "placement_id": f"o{i}",
            "permit_boundary_pass": "true",
            "permanent_transect_protected": "true",
            "placement_reproducible": "true",
            "restoration_workspace_pass": "true",
        }
        for i in range(3)
    ]

    # Three positive delays are required for an empirical monotonic-drift audit.
    # Signed medians +5%, -4%, +3% are deliberately non-monotonic while all
    # absolute preservation-error gates pass.
    preservation_rows = []
    for delay, delayed in ((15, 105.0), (30, 96.0), (60, 103.0)):
        preservation_rows.extend([
            {
                "method": "liquid_nitrogen_flash_freeze",
                "delay_minutes": delay,
                "specimen_id": f"p{i}",
                "immediate_tnc_mg_g": 100.0,
                "delayed_tnc_mg_g": delayed,
                "physically_suitable": "true",
            }
            for i in range(6)
        ])

    return metadata, hplc, tissue_rows, geometry_rows, offset_rows, preservation_rows


def test_blank_templates(tmp):
    candidate = tmp / "blank_candidate.json"
    audit = tmp / "blank_audit.json"
    run(
        BUILDER,
        "--canonical", CANONICAL,
        "--metadata", ROOT / "field" / "tnc_v2_raw_pilot_metadata.json",
        "--hplc", ROOT / "field" / "tnc_v2_hplc_matrix_pilot.json",
        "--tissue", ROOT / "field" / "tnc_v2_tissue_class_pilot.csv",
        "--geometry", ROOT / "field" / "tnc_v2_core_geometry_pilot.csv",
        "--offset", ROOT / "field" / "tnc_v2_offset_pilot.csv",
        "--preservation", ROOT / "field" / "tnc_v2_preservation_pilot.csv",
        "--out", candidate,
        "--audit-out", audit,
    )
    result = validate(candidate, tmp / "blank_validation.json")
    assert result["status"] == "STOP_PILOT_INCOMPLETE", result


def test_pass_and_provenance(tmp):
    inputs = synthetic_passing_inputs()
    candidate = build_candidate(tmp, "pass", *inputs)
    validation_path = tmp / "pass_validation.json"
    result = validate(candidate, validation_path)
    assert result["status"] == "PASS_METHOD_PILOT", result
    assert result["pilot_source"] == str(candidate), result
    assert result["raw_pilot_provenance"], result

    freeze_out = tmp / "freeze_after_pilot.json"
    run(
        APPLY,
        "--validation", validation_path,
        "--freeze", FREEZE,
        "--out", freeze_out,
    )
    freeze = json.loads(freeze_out.read_text(encoding="utf-8"))
    prov = freeze["method_pilot_provenance"]
    assert prov["source_pilot"] == str(candidate), prov
    assert prov["raw_pilot_provenance"], prov
    assert freeze["status"] == "METHOD_PILOT_PASS_LOGISTICS_PENDING", freeze


def test_individual_matrix_spike_failure(tmp):
    # Mean = 110%, which is inside 85-115, but one individual spike is 130%.
    inputs = synthetic_passing_inputs(matrix_spikes=[100.0, 100.0, 130.0])
    candidate = build_candidate(tmp, "bad_spike", *inputs)
    result = validate(candidate, tmp / "bad_spike_validation.json")
    assert result["status"] == "STOP_PILOT_QC_FAILED", result
    assert any("matrix-spike" in x for x in result["errors"]), result


def test_monotonic_preservation_drift_fails(tmp):
    inputs = list(synthetic_passing_inputs())
    preservation_rows = []
    # All absolute-error gates pass, but signed medians drift monotonically
    # +2%, +4%, +6% with increasing delay. Builder must derive drift=False.
    for delay, delayed in ((15, 102.0), (30, 104.0), (60, 106.0)):
        preservation_rows.extend([
            {
                "method": "liquid_nitrogen_flash_freeze",
                "delay_minutes": delay,
                "specimen_id": f"p{i}",
                "immediate_tnc_mg_g": 100.0,
                "delayed_tnc_mg_g": delayed,
                "physically_suitable": "true",
            }
            for i in range(6)
        ])
    inputs[-1] = preservation_rows
    candidate = build_candidate(tmp, "monotonic_drift", *inputs)
    result = validate(candidate, tmp / "monotonic_drift_validation.json")
    assert result["status"] == "STOP_PILOT_QC_FAILED", result
    assert any("monotonic TNC drift" in x for x in result["errors"]), result


def test_too_few_preservation_delays_stays_incomplete(tmp):
    inputs = list(synthetic_passing_inputs())
    inputs[-1] = [
        {
            "method": "liquid_nitrogen_flash_freeze",
            "delay_minutes": 30,
            "specimen_id": f"p{i}",
            "immediate_tnc_mg_g": 100.0,
            "delayed_tnc_mg_g": 103.0,
            "physically_suitable": "true",
        }
        for i in range(6)
    ]
    candidate = build_candidate(tmp, "too_few_delays", *inputs)
    result = validate(candidate, tmp / "too_few_delays_validation.json")
    assert result["status"] == "STOP_PILOT_INCOMPLETE", result
    assert "preservation.monotonic_directional_drift_absent" in result["pending_fields"], result


def main():
    with tempfile.TemporaryDirectory(prefix="tnc_v2_pipeline_") as td:
        tmp = Path(td)
        test_blank_templates(tmp)
        test_pass_and_provenance(tmp)
        test_individual_matrix_spike_failure(tmp)
        test_monotonic_preservation_drift_fails(tmp)
        test_too_few_preservation_delays_stays_incomplete(tmp)
    print("TNC-v2 method-pilot pipeline self-test: OK")


if __name__ == "__main__":
    main()
