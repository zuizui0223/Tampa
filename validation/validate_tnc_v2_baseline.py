#!/usr/bin/env python3
"""Fail-closed validator for Tampa four-bay TNC prospective baseline.

This checks baseline collection only. It intentionally refuses to read any future
meadow outcome. The precollection freeze must be completed before the first
outcome-bearing core.

Primary rules are inherited from:
  results/clonal_state_prospective_v2_contract.json
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import Counter, defaultdict
from pathlib import Path

BAYS = {
    "Old Tampa Bay",
    "Middle Tampa Bay",
    "Lower Tampa Bay",
    "Boca Ciega Bay",
}
FORBIDDEN_OUTCOME_TOKENS = {
    "future_frequency",
    "future_delta_frequency",
    "future_braun_blanquet",
    "future_blade_length",
    "future_shoot_density",
    "outcome",
    "response",
}
REQUIRED_COLUMNS = {
    "node_id",
    "water_body",
    "core_id",
    "design_class",
    "transect_offset_m",
    "collection_datetime",
    "baseline_survey_date",
    "rhizome_tissue_class",
    "core_diameter_cm",
    "core_depth_cm",
    "preservation_start_datetime",
    "preservation_method",
    "assay_batch",
    "soluble_nsc_mg_g",
    "starch_mg_g",
    "primary_qc_pass",
    "exclusion_reason",
}


def parse_dt(value: str) -> dt.datetime:
    v = value.strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ):
        try:
            return dt.datetime.strptime(v, fmt)
        except ValueError:
            pass
    raise ValueError(f"unparseable datetime: {value!r}")


def as_float(value: str, field: str) -> float:
    try:
        return float(value)
    except Exception as exc:
        raise ValueError(f"{field} must be numeric, got {value!r}") from exc


def is_true(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "pass", "passed"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="field/tnc_v2_collection_manifest.csv")
    ap.add_argument("--freeze", default="field/tnc_v2_precollection_freeze.json")
    ap.add_argument("--contract", default="results/clonal_state_prospective_v2_contract.json")
    ap.add_argument("--out", default="results/tnc_v2_baseline_validation.json")
    args = ap.parse_args()

    freeze = json.loads(Path(args.freeze).read_text(encoding="utf-8"))
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))

    authority_errors = []
    if freeze.get("contract") != args.contract:
        authority_errors.append("freeze contract path does not match authoritative v2 contract")
    if contract.get("version_authority", {}).get("status") != "authoritative_outcome_bearing_tnc_primary":
        authority_errors.append("TNC v2 contract is not marked authoritative")
    if set(contract.get("eligibility", {}).get("geography", [])) != BAYS:
        authority_errors.append("contract geography does not match the frozen four-bay set")
    if int(contract.get("eligibility", {}).get("minimum_confirmatory_analyzable_nodes", -1)) != int(freeze["fixed_rules"]["minimum_primary_nodes_total"]):
        authority_errors.append("contract/freeze total-node gate mismatch")
    if int(contract.get("eligibility", {}).get("minimum_confirmatory_nodes_per_bay", -1)) != int(freeze["fixed_rules"]["minimum_primary_nodes_per_bay"]):
        authority_errors.append("contract/freeze per-bay gate mismatch")
    if contract.get("baseline_new_measurements", {}).get("analytical_standardization", {}).get("preferred_assay", "").startswith("HPLC") is False:
        authority_errors.append("authoritative contract no longer specifies HPLC primary assay")
    if freeze["fixed_rules"].get("assay_method") != "HPLC":
        authority_errors.append("precollection freeze assay does not match HPLC contract")
    if contract.get("eligibility", {}).get("planning_target_nodes") != 41:
        authority_errors.append("authoritative v2 planning frame is not 41 nodes")

    if authority_errors:
        result = {
            "schema": "tampa.tnc_v2_baseline_validation.v1",
            "status": "STOP_CONTRACT_FREEZE_MISMATCH",
            "errors": authority_errors,
            "message": "Do not accept outcome-bearing TNC cores until authoritative v2 contract and field freeze agree."
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        return

    pending = [
        k for k, v in freeze["fields_to_freeze_before_first_outcome_bearing_core"].items()
        if v in (None, "", "PENDING")
    ]
    if pending:
        result = {
            "schema": "tampa.tnc_v2_baseline_validation.v1",
            "status": "STOP_PRECOLLECTION_FREEZE_INCOMPLETE",
            "pending_fields": pending,
            "message": "Do not accept outcome-bearing TNC cores until all response-independent freeze fields are fixed.",
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        return

    start = parse_dt(freeze["fields_to_freeze_before_first_outcome_bearing_core"]["campaign_start_date"])
    end = parse_dt(freeze["fields_to_freeze_before_first_outcome_bearing_core"]["campaign_end_date"])
    if (end - start).days > freeze["fixed_rules"]["campaign_window_days"]:
        raise SystemExit("frozen campaign itself exceeds 28 days")

    with Path(args.manifest).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - header)
        forbidden = sorted(h for h in header if h.strip().lower() in FORBIDDEN_OUTCOME_TOKENS)
        if missing:
            raise SystemExit(f"missing required columns: {missing}")
        if forbidden:
            raise SystemExit(
                "future outcome columns are forbidden in the baseline manifest: "
                + ", ".join(forbidden)
            )
        rows = list(reader)

    errors: list[str] = []
    node_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    collection_times = []
    tissue = freeze["fields_to_freeze_before_first_outcome_bearing_core"]["horizontal_rhizome_tissue_class"]
    min_offset = float(freeze["fields_to_freeze_before_first_outcome_bearing_core"]["minimum_perpendicular_transect_offset_m"])
    frozen_diameter = float(freeze["fields_to_freeze_before_first_outcome_bearing_core"]["core_diameter_cm"])
    frozen_depth = float(freeze["fields_to_freeze_before_first_outcome_bearing_core"]["core_depth_cm"])
    max_pres_min = float(freeze["fields_to_freeze_before_first_outcome_bearing_core"]["maximum_collection_to_preservation_minutes"])
    frozen_pres = freeze["fields_to_freeze_before_first_outcome_bearing_core"]["preservation_method"]

    for i, r in enumerate(rows, start=2):
        node = r["node_id"].strip()
        bay = r["water_body"].strip()
        if not node:
            errors.append(f"row {i}: blank node_id")
            continue
        if bay not in BAYS:
            errors.append(f"row {i}: invalid water_body {bay!r}")
        node_rows[node].append(r)

        try:
            coll = parse_dt(r["collection_datetime"])
            base = parse_dt(r["baseline_survey_date"])
            pres = parse_dt(r["preservation_start_datetime"])
            collection_times.append(coll)

            if coll < start or coll > end + dt.timedelta(days=1):
                errors.append(f"row {i}: collection outside frozen campaign")

            align = abs((coll.date() - base.date()).days)
            if align > freeze["fixed_rules"]["baseline_alignment_days_each_side"]:
                errors.append(f"row {i}: baseline alignment {align} d exceeds ±14 d")

            pres_min = (pres - coll).total_seconds() / 60
            if pres_min < 0 or pres_min > max_pres_min:
                errors.append(f"row {i}: preservation delay {pres_min:.1f} min outside frozen rule")
        except ValueError as exc:
            errors.append(f"row {i}: {exc}")

        try:
            if as_float(r["transect_offset_m"], "transect_offset_m") < min_offset:
                errors.append(f"row {i}: transect offset below frozen minimum")
            if abs(as_float(r["core_diameter_cm"], "core_diameter_cm") - frozen_diameter) > 1e-9:
                errors.append(f"row {i}: core diameter differs from frozen value")
            if abs(as_float(r["core_depth_cm"], "core_depth_cm") - frozen_depth) > 1e-9:
                errors.append(f"row {i}: core depth differs from frozen value")
        except ValueError as exc:
            errors.append(f"row {i}: {exc}")

        if r["rhizome_tissue_class"].strip() != tissue:
            errors.append(f"row {i}: rhizome tissue class differs from frozen class")
        if r["preservation_method"].strip() != frozen_pres:
            errors.append(f"row {i}: preservation method differs from frozen method")

        # Primary TNC is complete-case. Missing components are not imputed.
        if is_true(r["primary_qc_pass"]):
            for field in ("soluble_nsc_mg_g", "starch_mg_g"):
                try:
                    as_float(r[field], field)
                except ValueError:
                    errors.append(f"row {i}: QC-pass row missing numeric {field}")

    valid_nodes = {}
    for node, rr in node_rows.items():
        bay_set = {r["water_body"].strip() for r in rr}
        if len(bay_set) != 1:
            errors.append(f"node {node}: inconsistent water_body across cores")
            continue
        bay = next(iter(bay_set))
        valid_cores = [
            r for r in rr
            if is_true(r["primary_qc_pass"])
            and r["soluble_nsc_mg_g"].strip()
            and r["starch_mg_g"].strip()
        ]
        if len(valid_cores) >= freeze["fixed_rules"]["minimum_cores_per_node"]:
            valid_nodes[node] = bay

    bay_counts = Counter(valid_nodes.values())
    total = len(valid_nodes)
    replication_ok = (
        total >= freeze["fixed_rules"]["minimum_primary_nodes_total"]
        and all(bay_counts.get(b, 0) >= freeze["fixed_rules"]["minimum_primary_nodes_per_bay"] for b in BAYS)
    )

    result = {
        "schema": "tampa.tnc_v2_baseline_validation.v1",
        "status": (
            "PASS_CONFIRMATORY_BASELINE"
            if not errors and replication_ok
            else "PASS_PILOT_ONLY"
            if not errors
            else "STOP_VALIDATION_ERRORS"
        ),
        "rows": len(rows),
        "valid_primary_nodes": total,
        "valid_nodes_by_bay": dict(bay_counts),
        "confirmatory_replication_gate": replication_ok,
        "errors": errors,
        "boundary": (
            "This validates the prospective baseline only. It does not open, join, "
            "or inspect any future meadow response."
        ),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
