#!/usr/bin/env python3
"""Fail-closed validator for the Tampa TNC response-independent pilot.

No future meadow outcome is accepted or used.
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
    "disturbed_volume_cm3", "processing_time_minutes", "rhizome_dry_mass_mg",
    "tissue_rule_unambiguous", "pooled_matrix_id", "solvent_class",
    "technical_replicate_id", "calibration_qc_pass", "spike_recovery_pct",
    "technical_cv_pct", "chromatographic_interference_pass",
    "soluble_nsc_mg_g", "starch_mg_g", "tnc_mg_g",
    "preservation_workflow", "preservation_delay_minutes",
    "preservation_reference_matched",
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", default="field/tnc_v2_pilot_freeze.json")
    ap.add_argument("--manifest", default="field/tnc_v2_pilot_manifest.csv")
    ap.add_argument("--out", default="results/tnc_v2_pilot_validation.json")
    args = ap.parse_args()

    freeze = json.loads(Path(args.freeze).read_text(encoding="utf-8"))

    required_freeze = {
        "tissue_rule.horizontal_rhizome_tissue_class":
            freeze["tissue_rule"]["horizontal_rhizome_tissue_class"],
        "field_geometry_pilot.candidate_core_geometries":
            freeze["field_geometry_pilot"]["candidate_core_geometries"],
        "field_geometry_pilot.lab_required_dry_mass_mg_per_core":
            freeze["field_geometry_pilot"]["lab_required_dry_mass_mg_per_core"],
        "matrix_hplc_pilot.calibration_acceptance_rule":
            freeze["matrix_hplc_pilot"]["calibration_acceptance_rule"],
        "matrix_hplc_pilot.spike_recovery_lower_pct":
            freeze["matrix_hplc_pilot"]["spike_recovery_lower_pct"],
        "matrix_hplc_pilot.spike_recovery_upper_pct":
            freeze["matrix_hplc_pilot"]["spike_recovery_upper_pct"],
        "matrix_hplc_pilot.maximum_technical_cv_pct":
            freeze["matrix_hplc_pilot"]["maximum_technical_cv_pct"],
        "matrix_hplc_pilot.chromatographic_interference_rule":
            freeze["matrix_hplc_pilot"]["chromatographic_interference_rule"],
        "matrix_hplc_pilot.equivalence_tolerance_pct_for_tiebreak":
            freeze["matrix_hplc_pilot"]["equivalence_tolerance_pct_for_tiebreak"],
        "matrix_hplc_pilot.equivalence_tiebreak_rule":
            freeze["matrix_hplc_pilot"]["equivalence_tiebreak_rule"],
        "preservation_pilot.reference_workflow":
            freeze["preservation_pilot"]["reference_workflow"],
        "preservation_pilot.candidate_workflows":
            freeze["preservation_pilot"]["candidate_workflows"],
        "preservation_pilot.candidate_delays_minutes":
            freeze["preservation_pilot"]["candidate_delays_minutes"],
        "preservation_pilot.maximum_allowed_relative_bias_pct":
            freeze["preservation_pilot"]["maximum_allowed_relative_bias_pct"],
    }
    pending = sorted(
        key for key, value in required_freeze.items()
        if value is None or value == "" or value == []
    )
    if pending:
        result = {
            "schema": "tampa.tnc_v2_pilot_validation.v1",
            "status": "STOP_PRE_PILOT_FREEZE_INCOMPLETE",
            "pending_fields": pending,
            "message": "Complete response-independent pilot rules before collecting/opening pilot assay results.",
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        return

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

    errors = []
    donor_locations = set()
    frozen_tissue = freeze["tissue_rule"]["horizontal_rhizome_tissue_class"]
    for i, row in enumerate(rows, start=2):
        donor_locations.add(row["donor_location_id"].strip())
        if not truth(row["permanently_excluded_from_confirmatory_cohort"]):
            errors.append(f"row {i}: donor not permanently excluded")
        if row["tissue_rule_id"].strip() != frozen_tissue:
            errors.append(f"row {i}: tissue rule differs from freeze")

    if len(donor_locations) < int(freeze["donor_rule"]["minimum_independent_donor_locations"]):
        errors.append("insufficient independent donor locations")

    # Geometry selection.
    by_core = {}
    for row in rows:
        sid = row["pilot_sample_id"].strip()
        if sid and sid not in by_core:
            by_core[sid] = row
    by_geometry = defaultdict(list)
    for row in by_core.values():
        by_geometry[row["core_geometry_id"].strip()].append(row)

    declared_geometries = {
        str(item["id"]): item
        for item in freeze["field_geometry_pilot"]["candidate_core_geometries"]
    }
    dry_req = float(freeze["field_geometry_pilot"]["lab_required_dry_mass_mg_per_core"])
    pass_frac = float(freeze["field_geometry_pilot"]["dry_mass_sufficiency_pass_fraction"])
    min_n = int(freeze["field_geometry_pilot"]["minimum_independent_cores_per_geometry"])

    geometry_results = {}
    passing_geometry = []
    for gid, rr in sorted(by_geometry.items()):
        if gid not in declared_geometries:
            errors.append(f"undeclared core geometry {gid!r}")
            continue
        passes = [
            num(r["rhizome_dry_mass_mg"], "rhizome_dry_mass_mg") >= dry_req
            and truth(r["tissue_rule_unambiguous"])
            for r in rr
        ]
        fraction = sum(passes) / len(passes) if passes else 0.0
        vol = statistics.median(num(r["disturbed_volume_cm3"], "disturbed_volume_cm3") for r in rr)
        diam = statistics.median(num(r["core_diameter_cm"], "core_diameter_cm") for r in rr)
        depth = statistics.median(num(r["core_depth_cm"], "core_depth_cm") for r in rr)
        ptime = statistics.median(num(r["processing_time_minutes"], "processing_time_minutes") for r in rr)
        passed = len(rr) >= min_n and fraction >= pass_frac
        geometry_results[gid] = {
            "n": len(rr),
            "mass_and_tissue_pass_fraction": fraction,
            "median_disturbed_volume_cm3": vol,
            "median_diameter_cm": diam,
            "median_depth_cm": depth,
            "median_processing_time_minutes": ptime,
            "passed": passed,
        }
        if passed:
            passing_geometry.append((vol, diam, depth, ptime, gid))
    selected_geometry = None
    if passing_geometry:
        selected_geometry = sorted(passing_geometry)[0][-1]

    # Solvent QC and extraction yield.
    solvents = set(freeze["matrix_hplc_pilot"]["candidate_solvents"])
    min_matrices = int(freeze["matrix_hplc_pilot"]["minimum_pooled_matrices"])
    min_rep = int(freeze["matrix_hplc_pilot"]["minimum_technical_replicates_per_solvent_per_matrix"])
    rec_low = float(freeze["matrix_hplc_pilot"]["spike_recovery_lower_pct"])
    rec_high = float(freeze["matrix_hplc_pilot"]["spike_recovery_upper_pct"])
    max_cv = float(freeze["matrix_hplc_pilot"]["maximum_technical_cv_pct"])

    sm = defaultdict(list)
    for row in rows:
        s = row["solvent_class"].strip()
        m = row["pooled_matrix_id"].strip()
        if s and m:
            sm[(s, m)].append(row)

    solvent_results = {}
    passing_solvents = []
    for solvent in sorted(solvents):
        matrices = {m: rr for (s, m), rr in sm.items() if s == solvent}
        all_pass = len(matrices) >= min_matrices
        yields = []
        detail = {}
        for matrix, rr in sorted(matrices.items()):
            eligible = [
                r for r in rr
                if truth(r["calibration_qc_pass"])
                and truth(r["chromatographic_interference_pass"])
            ]
            recovery = [num(r["spike_recovery_pct"], "spike_recovery_pct") for r in eligible]
            cvs = [num(r["technical_cv_pct"], "technical_cv_pct") for r in eligible]
            syield = [num(r["soluble_nsc_mg_g"], "soluble_nsc_mg_g") for r in eligible]
            passed = (
                len(eligible) >= min_rep
                and all(rec_low <= x <= rec_high for x in recovery)
                and all(x <= max_cv for x in cvs)
            )
            if not passed:
                all_pass = False
            yields.extend(syield)
            detail[matrix] = {
                "n": len(eligible),
                "recovery_range_pct": [min(recovery), max(recovery)] if recovery else None,
                "max_cv_pct": max(cvs) if cvs else None,
                "mean_soluble_nsc_mg_g": statistics.mean(syield) if syield else None,
                "passed": passed,
            }
        mean_yield = statistics.mean(yields) if yields else None
        solvent_results[solvent] = {
            "passed": all_pass,
            "overall_mean_soluble_nsc_mg_g": mean_yield,
            "matrices": detail,
        }
        if all_pass and mean_yield is not None:
            passing_solvents.append((mean_yield, solvent))

    selected_solvent = None
    if passing_solvents:
        selected_solvent = sorted(passing_solvents, reverse=True)[0][1]

    # Preservation bias.
    allowed_workflows = set(freeze["preservation_pilot"]["candidate_workflows"])
    allowed_delays = {float(x) for x in freeze["preservation_pilot"]["candidate_delays_minutes"]}
    max_bias = float(freeze["preservation_pilot"]["maximum_allowed_relative_bias_pct"])
    min_delay_n = int(freeze["preservation_pilot"]["minimum_replicates_per_delay"])

    by_pres = defaultdict(list)
    for row in rows:
        wf = row["preservation_workflow"].strip()
        if not wf:
            continue
        delay = num(row["preservation_delay_minutes"], "preservation_delay_minutes")
        if wf in allowed_workflows and delay in allowed_delays:
            by_pres[(wf, delay)].append(row)

    preservation_results = {}
    passing_delays = []
    for (wf, delay), rr in sorted(by_pres.items()):
        biases = []
        for row in rr:
            ref = num(row["preservation_reference_matched"], "preservation_reference_matched")
            obs = num(row["tnc_mg_g"], "tnc_mg_g")
            if ref != 0:
                biases.append(100.0 * (obs - ref) / ref)
        mean_abs_bias = statistics.mean(abs(x) for x in biases) if biases else None
        passed = (
            len(biases) >= min_delay_n
            and mean_abs_bias is not None
            and mean_abs_bias <= max_bias
        )
        preservation_results[f"{wf}::{delay:g}"] = {
            "n": len(biases),
            "mean_absolute_relative_bias_pct": mean_abs_bias,
            "passed": passed,
        }
        if passed:
            passing_delays.append((delay, wf))

    selected_preservation = None
    if passing_delays:
        delay, wf = sorted(passing_delays, reverse=True)[0]
        selected_preservation = {
            "workflow": wf,
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
        "selected_solvent": selected_solvent,
        "preservation_results": preservation_results,
        "selected_preservation": selected_preservation,
        "errors": errors,
        "next_step": (
            "Write results/tnc_v2_pilot_decision.json and copy exact final values into "
            "field/tnc_v2_precollection_freeze.json."
            if status == "PASS_TECHNICAL_PILOT"
            else "Close/redesign the technical pilot before confirmatory sampling."
        ),
        "claim_boundary": "Technical feasibility only; no future ecological response is used.",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
