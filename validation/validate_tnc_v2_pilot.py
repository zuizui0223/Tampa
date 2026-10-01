#!/usr/bin/env python3
"""Fail-closed validator for the Tampa TNC response-independent technical pilot.

No future meadow response is accepted or used.

Pilot decisions:
- smallest passing declared core geometry;
- species-matrix solvent selected among QC-passing solvents using frozen
  yield/equivalence/tie-break rules;
- longest passing preservation delay under a frozen bias criterion.

The resulting technical decision is not itself an ecological result.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

FORBIDDEN = {
    "future_frequency", "future_delta_frequency", "future_braun_blanquet",
    "future_blade_length", "future_shoot_density", "future_decline_class",
    "outcome", "response",
}

REQUIRED_COLUMNS = {
    "pilot_sample_id", "donor_location_id",
    "permanently_excluded_from_confirmatory_cohort", "tissue_rule_id",
    "core_geometry_id", "core_diameter_cm", "core_depth_cm",
    "processing_time_minutes", "rhizome_dry_mass_mg",
    "tissue_rule_unambiguous", "pooled_matrix_id", "solvent_class",
    "technical_replicate_id", "calibration_qc_pass", "spike_recovery_pct",
    "technical_cv_pct", "chromatographic_interference_pass",
    "soluble_nsc_mg_g", "starch_mg_g", "tnc_mg_g",
    "preservation_workflow", "preservation_delay_minutes",
    "preservation_reference_tnc_mg_g",
}


def truth(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "pass", "passed"}


def num(value: str, name: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(f"{name} must be numeric: {value!r}") from exc
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite: {value!r}")
    return x


def pending_preflight(freeze: dict) -> list[str]:
    f = freeze
    required = {
        "tissue_rule.horizontal_rhizome_tissue_class":
            f["tissue_rule"]["horizontal_rhizome_tissue_class"],
        "field_geometry_pilot.candidate_core_geometries":
            f["field_geometry_pilot"]["candidate_core_geometries"],
        "field_geometry_pilot.lab_required_dry_mass_mg_per_core":
            f["field_geometry_pilot"]["lab_required_dry_mass_mg_per_core"],
        "matrix_hplc_pilot.starch_workflow":
            f["matrix_hplc_pilot"]["starch_workflow"],
        "matrix_hplc_pilot.calibration_acceptance_rule":
            f["matrix_hplc_pilot"]["calibration_acceptance_rule"],
        "matrix_hplc_pilot.spike_recovery_lower_pct":
            f["matrix_hplc_pilot"]["spike_recovery_lower_pct"],
        "matrix_hplc_pilot.spike_recovery_upper_pct":
            f["matrix_hplc_pilot"]["spike_recovery_upper_pct"],
        "matrix_hplc_pilot.maximum_technical_cv_pct":
            f["matrix_hplc_pilot"]["maximum_technical_cv_pct"],
        "matrix_hplc_pilot.chromatographic_interference_rule":
            f["matrix_hplc_pilot"]["chromatographic_interference_rule"],
        "matrix_hplc_pilot.equivalence_tolerance_pct_for_tiebreak":
            f["matrix_hplc_pilot"]["equivalence_tolerance_pct_for_tiebreak"],
        "matrix_hplc_pilot.equivalence_tiebreak_preference":
            f["matrix_hplc_pilot"]["equivalence_tiebreak_preference"],
        "preservation_pilot.reference_workflow":
            f["preservation_pilot"]["reference_workflow"],
        "preservation_pilot.candidate_workflows":
            f["preservation_pilot"]["candidate_workflows"],
        "preservation_pilot.candidate_delays_minutes":
            f["preservation_pilot"]["candidate_delays_minutes"],
        "preservation_pilot.maximum_allowed_relative_bias_pct":
            f["preservation_pilot"]["maximum_allowed_relative_bias_pct"],
    }
    return sorted(k for k, v in required.items() if v is None or v == "" or v == [])


def declared_geometries(freeze: dict) -> dict[str, dict]:
    rows = freeze["field_geometry_pilot"]["candidate_core_geometries"]
    required = set(freeze["field_geometry_pilot"]["candidate_geometry_required_fields"])
    out = {}
    for item in rows:
        missing = required - set(item)
        if missing:
            raise ValueError(f"candidate geometry missing fields {sorted(missing)}: {item}")
        gid = str(item["id"])
        if gid in out:
            raise ValueError(f"duplicate candidate geometry id: {gid}")
        d = float(item["diameter_cm"])
        z = float(item["depth_cm"])
        if d <= 0 or z <= 0:
            raise ValueError(f"non-positive geometry: {gid}")
        out[gid] = {"id": gid, "diameter_cm": d, "depth_cm": z}
    return out


def cylindrical_volume_cm3(diameter_cm: float, depth_cm: float) -> float:
    return math.pi * (diameter_cm / 2.0) ** 2 * depth_cm


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", default="field/tnc_v2_pilot_freeze.json")
    ap.add_argument("--manifest", default="field/tnc_v2_pilot_manifest.csv")
    ap.add_argument("--out", default="results/tnc_v2_pilot_validation.json")
    args = ap.parse_args()

    freeze = json.loads(Path(args.freeze).read_text(encoding="utf-8"))
    pending = pending_preflight(freeze)
    if pending:
        result = {
            "schema": "tampa.tnc_v2_pilot_validation.v1",
            "status": "STOP_PRE_PILOT_FREEZE_INCOMPLETE",
            "pending_fields": pending,
            "message": "Freeze all response-independent technical criteria before pilot assay results are opened.",
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        return

    geometries = declared_geometries(freeze)

    candidate_solvents = list(freeze["matrix_hplc_pilot"]["candidate_solvents"])
    allowed_solvents = set(candidate_solvents)
    preference = list(freeze["matrix_hplc_pilot"]["equivalence_tiebreak_preference"])
    if set(preference) != allowed_solvents or len(preference) != len(set(preference)):
        raise SystemExit("equivalence_tiebreak_preference must rank each candidate solvent exactly once")

    with Path(args.manifest).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - header)
        forbidden = sorted(h for h in header if h.strip().lower() in FORBIDDEN)
        if missing:
            raise SystemExit(f"missing pilot columns: {missing}")
        if forbidden:
            raise SystemExit(f"future-response columns forbidden: {forbidden}")
        rows = list(reader)

    errors: list[str] = []
    donor_locations = set()
    frozen_tissue = freeze["tissue_rule"]["horizontal_rhizome_tissue_class"]

    for i, row in enumerate(rows, start=2):
        donor_locations.add(row["donor_location_id"].strip())
        if not truth(row["permanently_excluded_from_confirmatory_cohort"]):
            errors.append(f"row {i}: donor not permanently excluded")
        if row["tissue_rule_id"].strip() != frozen_tissue:
            errors.append(f"row {i}: tissue rule differs from freeze")

        gid = row["core_geometry_id"].strip()
        if gid:
            if gid not in geometries:
                errors.append(f"row {i}: undeclared geometry {gid!r}")
            else:
                gd = geometries[gid]
                try:
                    rd = num(row["core_diameter_cm"], "core_diameter_cm")
                    rz = num(row["core_depth_cm"], "core_depth_cm")
                    if abs(rd - gd["diameter_cm"]) > 1e-9 or abs(rz - gd["depth_cm"]) > 1e-9:
                        errors.append(f"row {i}: geometry dimensions differ from predeclared {gid}")
                except ValueError as exc:
                    errors.append(f"row {i}: {exc}")

        solvent = row["solvent_class"].strip()
        if solvent and solvent not in allowed_solvents:
            errors.append(f"row {i}: undeclared solvent {solvent!r}")

    min_donor = int(freeze["donor_rule"]["minimum_independent_donor_locations"])
    if len(donor_locations) < min_donor:
        errors.append(f"only {len(donor_locations)} donor locations; require >= {min_donor}")

    # Field geometry: one record per physical pilot core.
    core_rows: dict[str, dict] = {}
    for row in rows:
        sid = row["pilot_sample_id"].strip()
        if sid and sid not in core_rows:
            core_rows[sid] = row

    by_geometry = defaultdict(list)
    for row in core_rows.values():
        gid = row["core_geometry_id"].strip()
        if gid:
            by_geometry[gid].append(row)

    dry_req = float(freeze["field_geometry_pilot"]["lab_required_dry_mass_mg_per_core"])
    pass_fraction = float(freeze["field_geometry_pilot"]["dry_mass_sufficiency_pass_fraction"])
    min_core_n = int(freeze["field_geometry_pilot"]["minimum_independent_cores_per_geometry"])

    geometry_results = {}
    passing_geometry = []
    for gid, geometry in geometries.items():
        rr = by_geometry.get(gid, [])
        passed_rows = []
        times = []
        for row in rr:
            try:
                mass_ok = num(row["rhizome_dry_mass_mg"], "rhizome_dry_mass_mg") >= dry_req
                tissue_ok = truth(row["tissue_rule_unambiguous"])
                times.append(num(row["processing_time_minutes"], "processing_time_minutes"))
                passed_rows.append(mass_ok and tissue_ok)
            except ValueError as exc:
                errors.append(f"geometry {gid}: {exc}")

        frac = sum(passed_rows) / len(passed_rows) if passed_rows else 0.0
        volume = cylindrical_volume_cm3(geometry["diameter_cm"], geometry["depth_cm"])
        process_median = statistics.median(times) if times else None
        passed = len(rr) >= min_core_n and frac >= pass_fraction
        geometry_results[gid] = {
            "declared_diameter_cm": geometry["diameter_cm"],
            "declared_depth_cm": geometry["depth_cm"],
            "cylindrical_disturbed_volume_cm3": volume,
            "n_independent_cores": len(rr),
            "mass_and_tissue_pass_fraction": frac,
            "median_processing_time_minutes": process_median,
            "passed": passed,
        }
        if passed:
            passing_geometry.append((
                volume,
                geometry["diameter_cm"],
                geometry["depth_cm"],
                process_median if process_median is not None else float("inf"),
                gid,
            ))

    selected_geometry = sorted(passing_geometry)[0][-1] if passing_geometry else None

    # HPLC solvent QC and extraction yield.
    min_matrices = int(freeze["matrix_hplc_pilot"]["minimum_pooled_matrices"])
    min_rep = int(freeze["matrix_hplc_pilot"]["minimum_technical_replicates_per_solvent_per_matrix"])
    rec_low = float(freeze["matrix_hplc_pilot"]["spike_recovery_lower_pct"])
    rec_high = float(freeze["matrix_hplc_pilot"]["spike_recovery_upper_pct"])
    max_cv = float(freeze["matrix_hplc_pilot"]["maximum_technical_cv_pct"])
    equivalence_tol = float(freeze["matrix_hplc_pilot"]["equivalence_tolerance_pct_for_tiebreak"])

    by_solvent_matrix = defaultdict(list)
    for row in rows:
        solvent = row["solvent_class"].strip()
        matrix = row["pooled_matrix_id"].strip()
        if solvent and matrix:
            by_solvent_matrix[(solvent, matrix)].append(row)

    solvent_results = {}
    passing_yields: dict[str, float] = {}
    for solvent in candidate_solvents:
        matrices = {
            matrix: rr
            for (s, matrix), rr in by_solvent_matrix.items()
            if s == solvent
        }
        all_pass = len(matrices) >= min_matrices
        yields = []
        details = {}

        for matrix, rr in sorted(matrices.items()):
            eligible = [
                row for row in rr
                if truth(row["calibration_qc_pass"])
                and truth(row["chromatographic_interference_pass"])
            ]
            try:
                recovery = [num(row["spike_recovery_pct"], "spike_recovery_pct") for row in eligible]
                cvs = [num(row["technical_cv_pct"], "technical_cv_pct") for row in eligible]
                syield = [num(row["soluble_nsc_mg_g"], "soluble_nsc_mg_g") for row in eligible]
            except ValueError as exc:
                errors.append(f"{solvent}/{matrix}: {exc}")
                recovery, cvs, syield = [], [], []

            passed = (
                len(eligible) >= min_rep
                and all(rec_low <= value <= rec_high for value in recovery)
                and all(value <= max_cv for value in cvs)
            )
            if not passed:
                all_pass = False
            yields.extend(syield)
            details[matrix] = {
                "n_qc_rows": len(eligible),
                "recovery_range_pct": [min(recovery), max(recovery)] if recovery else None,
                "maximum_cv_pct": max(cvs) if cvs else None,
                "mean_soluble_nsc_mg_g": statistics.mean(syield) if syield else None,
                "passed": passed,
            }

        mean_yield = statistics.mean(yields) if yields else None
        solvent_results[solvent] = {
            "passed": all_pass,
            "overall_mean_soluble_nsc_mg_g": mean_yield,
            "matrices": details,
        }
        if all_pass and mean_yield is not None:
            passing_yields[solvent] = mean_yield

    selected_solvent = None
    equivalent_solvents = []
    if passing_yields:
        maximum = max(passing_yields.values())
        equivalent_solvents = [
            solvent for solvent, mean_yield in passing_yields.items()
            if maximum == 0
            or 100.0 * (maximum - mean_yield) / abs(maximum) <= equivalence_tol
        ]
        for solvent in preference:
            if solvent in equivalent_solvents:
                selected_solvent = solvent
                break

    # Preservation delay.
    allowed_workflows = set(freeze["preservation_pilot"]["candidate_workflows"])
    allowed_delays = {float(x) for x in freeze["preservation_pilot"]["candidate_delays_minutes"]}
    max_bias = float(freeze["preservation_pilot"]["maximum_allowed_relative_bias_pct"])
    min_delay_n = int(freeze["preservation_pilot"]["minimum_replicates_per_delay"])

    by_preservation = defaultdict(list)
    for row in rows:
        workflow = row["preservation_workflow"].strip()
        if not workflow:
            continue
        try:
            delay = num(row["preservation_delay_minutes"], "preservation_delay_minutes")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if workflow in allowed_workflows and delay in allowed_delays:
            by_preservation[(workflow, delay)].append(row)

    preservation_results = {}
    passing_delays = []
    for (workflow, delay), rr in sorted(by_preservation.items()):
        biases = []
        for row in rr:
            try:
                ref = num(row["preservation_reference_tnc_mg_g"], "preservation_reference_tnc_mg_g")
                obs = num(row["tnc_mg_g"], "tnc_mg_g")
            except ValueError as exc:
                errors.append(f"{workflow}/{delay}: {exc}")
                continue
            if ref != 0:
                biases.append(100.0 * (obs - ref) / ref)

        mean_abs_bias = statistics.mean(abs(v) for v in biases) if biases else None
        passed = (
            len(biases) >= min_delay_n
            and mean_abs_bias is not None
            and mean_abs_bias <= max_bias
        )
        preservation_results[f"{workflow}::{delay:g}"] = {
            "n": len(biases),
            "mean_absolute_relative_bias_pct": mean_abs_bias,
            "passed": passed,
        }
        if passed:
            passing_delays.append((delay, workflow))

    selected_preservation = None
    if passing_delays:
        delay, workflow = sorted(passing_delays, reverse=True)[0]
        selected_preservation = {
            "workflow": workflow,
            "maximum_delay_minutes": delay,
        }

    if errors:
        status = "STOP_PILOT_ERRORS"
    elif selected_geometry is None:
        status = "STOP_NO_CORE_GEOMETRY_PASSES"
    elif selected_solvent is None:
        status = "STOP_NO_SOLVENT_PASSES"
    elif selected_preservation is None:
        status = "STOP_NO_PRESERVATION_RULE_PASSES"
    else:
        status = "PASS_TECHNICAL_PILOT"

    result = {
        "schema": "tampa.tnc_v2_pilot_validation.v1",
        "status": status,
        "donor_locations_n": len(donor_locations),
        "geometry_results": geometry_results,
        "selected_geometry_id": selected_geometry,
        "solvent_results": solvent_results,
        "equivalent_qc_passing_solvents": equivalent_solvents,
        "selected_solvent": selected_solvent,
        "frozen_starch_workflow": freeze["matrix_hplc_pilot"]["starch_workflow"],
        "preservation_results": preservation_results,
        "selected_preservation": selected_preservation,
        "errors": errors,
        "next_step": (
            "Write results/tnc_v2_pilot_decision.json, freeze remaining logistics "
            "such as transect offset and batch randomization, then copy exact values "
            "into field/tnc_v2_precollection_freeze.json."
            if status == "PASS_TECHNICAL_PILOT"
            else "Close or version the technical pilot before confirmatory sampling."
        ),
        "claim_boundary": "Technical feasibility only; no future ecological response is used.",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
