#!/usr/bin/env python3
"""Build a candidate Tampa TNC-v2 method-pilot summary from raw pilot records.

Pipeline:
  granular raw pilot records
    -> field/tnc_v2_method_pilot_candidate.json
    -> validation/validate_tnc_v2_method_pilot.py --pilot <candidate>

This script never modifies:
  field/tnc_v2_method_pilot.json
or:
  field/tnc_v2_precollection_freeze.json

No future ecological response is read.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

FORBIDDEN = (
    "future_frequency",
    "future_delta",
    "future_braun",
    "future_blade",
    "future_shoot",
    "ecological_outcome",
)

METHOD_CODE_TO_CANONICAL_INDEX = {
    "liquid_nitrogen_flash_freeze": 0,
    "dry_ice_rapid_freeze": 1,
}


def as_bool(value):
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"1", "true", "yes", "y", "pass", "passed"}:
        return True
    if s in {"0", "false", "no", "n", "fail", "failed"}:
        return False
    raise ValueError(f"not boolean: {value!r}")


def check_no_future(path: Path) -> None:
    text = path.read_text(encoding="utf-8-sig").lower()
    bad = [x for x in FORBIDDEN if x in text]
    if bad:
        raise RuntimeError(f"{path}: forbidden future-response token(s): {bad}")


def read_csv(path: Path):
    check_no_future(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def quantile(xs, p):
    ys = sorted(xs)
    if not ys:
        return None
    pos = (len(ys)-1)*p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ys[lo]
    return ys[lo] + (ys[hi]-ys[lo])*(pos-lo)


def pair_cv_pct(a, b):
    mean = (a+b)/2
    if mean == 0:
        return 0.0 if a == b else math.inf
    sd = abs(a-b)/math.sqrt(2)
    return 100*sd/mean


def summarize_hplc(path: Path):
    check_no_future(path)
    x = json.loads(path.read_text(encoding="utf-8"))
    standard = [float(v) for v in x.get("standard_recovery_pct", [])]
    matrix = [float(v) for v in x.get("matrix_spike_recovery_pct", [])]

    cvs = []
    for pair in x.get("technical_duplicate_pairs", []):
        a = pair.get("tnc_a_mg_g")
        b = pair.get("tnc_b_mg_g")
        if a in (None, "") or b in (None, ""):
            continue
        cvs.append(pair_cv_pct(float(a), float(b)))

    flags = []
    for row in x.get("extract_calibration_range", []):
        v = row.get("all_primary_analytes_in_range")
        if v in (None, ""):
            continue
        flags.append(as_bool(v))

    matrix_all_pass = bool(matrix) and all(85 <= v <= 115 for v in matrix)

    summary = {
        "calibration_identity_unambiguous": (
            None if x.get("calibration_identity_unambiguous") is None
            else as_bool(x["calibration_identity_unambiguous"])
        ),
        "standard_mix_mean_recovery_pct": statistics.mean(standard) if standard else None,
        "matrix_spike_mean_recovery_pct": statistics.mean(matrix) if matrix else None,
        "matrix_spike_all_within_85_115": matrix_all_pass if matrix else None,
        "technical_duplicate_median_cv_pct": statistics.median(cvs) if cvs else None,
        "technical_duplicate_fraction_gt15pct": (
            sum(v > 15 for v in cvs)/len(cvs) if cvs else None
        ),
        "pilot_extract_fraction_in_calibration_range": (
            sum(flags)/len(flags) if flags else None
        ),
        "blank_below_loq": (
            None if x.get("analytical_blank_below_loq") is None
            else as_bool(x["analytical_blank_below_loq"])
        ),
        "post_high_standard_carryover_below_loq": (
            None if x.get("post_high_standard_carryover_below_loq") is None
            else as_bool(x["post_high_standard_carryover_below_loq"])
        ),
        "raw_counts": {
            "standard_recovery_n": len(standard),
            "matrix_spike_n": len(matrix),
            "technical_duplicate_pairs_n": len(cvs),
            "pilot_extracts_n": len(flags),
        },
    }

    return summary


def summarize_tissue(path: Path, canonical):
    rows = read_csv(path)
    by = defaultdict(list)
    for r in rows:
        if not r.get("candidate_rank", "").strip():
            continue
        by[int(r["candidate_rank"])].append(r)

    candidates = []
    for rank in sorted(by):
        declared = [r for r in by[rank] if r.get("specimen_id", "").strip()]
        rr = [
            r for r in declared
            if r.get("classification_unambiguous", "").strip()
            and r.get("dry_mass_sufficient", "").strip()
            and r.get("destructive_guardrail_pass", "").strip()
        ]
        n = len(rr)
        c = sum(as_bool(r["classification_unambiguous"]) for r in rr)/n if n else 0
        d = sum(as_bool(r["dry_mass_sufficient"]) for r in rr)/n if n else 0
        g = all(as_bool(r["destructive_guardrail_pass"]) for r in rr) if rr else False
        candidates.append({
            "rank": rank, "n_complete": n, "n_declared": len(declared),
            "classification_success_fraction": c,
            "sufficient_dry_mass_fraction": d,
            "all_guardrail_pass": g,
            "pass": n >= 8 and c >= 0.90 and d >= 0.90 and g,
        })

    selected = next((x for x in candidates if x["pass"]), None)
    if selected is None:
        return None, candidates

    idx = selected["rank"] - 1
    order = canonical["tissue_class"]["candidate_order"]
    if idx < 0 or idx >= len(order):
        raise RuntimeError("tissue pilot rank exceeds canonical candidate order")

    return {
        "selected_horizontal_rhizome_tissue_class": order[idx],
        "classification_success_fraction": selected["classification_success_fraction"],
        "sufficient_dry_mass_fraction": selected["sufficient_dry_mass_fraction"],
        "selection_used_tnc_level_or_ecological_state": False,
    }, candidates


def summarize_geometry(path: Path, canonical):
    rows = read_csv(path)
    by = defaultdict(list)
    for r in rows:
        if not r.get("candidate_rank", "").strip():
            continue
        by[int(r["candidate_rank"])].append(r)

    candidates = []
    for rank in sorted(by):
        declared = [r for r in by[rank] if r.get("attempt_id", "").strip()]
        rr = [
            r for r in declared
            if r.get("live_horizontal_rhizome_recovered", "").strip()
            and r.get("dry_mass_sufficient", "").strip()
            and r.get("guardrail_pass", "").strip()
            and r.get("three_anchor_feasible", "").strip()
        ]
        n = len(rr)
        recovery = sum(as_bool(r["live_horizontal_rhizome_recovered"]) for r in rr)
        dry = sum(as_bool(r["dry_mass_sufficient"]) for r in rr)
        guard = all(as_bool(r["guardrail_pass"]) for r in rr) if rr else False
        anchor = all(as_bool(r["three_anchor_feasible"]) for r in rr) if rr else False
        candidates.append({
            "rank": rank, "n_complete": n, "n_declared": len(declared),
            "recovery_success_fraction": recovery/n if n else 0,
            "sufficient_dry_mass_fraction": dry/n if n else 0,
            "all_guardrail_pass": guard,
            "all_three_anchor_feasible": anchor,
            "pass": n >= 10 and recovery >= 9 and dry >= 9 and guard and anchor,
        })

    selected = next((x for x in candidates if x["pass"]), None)
    if selected is None:
        return None, candidates

    idx = selected["rank"] - 1
    order = canonical["core_geometry"]["candidate_order"]
    if idx < 0 or idx >= len(order):
        raise RuntimeError("geometry pilot rank exceeds canonical candidate order")
    chosen = order[idx]

    return {
        "selected_core_diameter_cm": chosen["diameter_cm"],
        "selected_core_depth_cm": chosen["depth_cm"],
        "recovery_success_fraction": selected["recovery_success_fraction"],
        "sufficient_dry_mass_fraction": selected["sufficient_dry_mass_fraction"],
        "three_anchor_geometry_feasible": selected["all_three_anchor_feasible"],
        "least_destructive_passing_geometry_selected": True,
    }, candidates


def summarize_offset(path: Path):
    rows = read_csv(path)
    by = defaultdict(list)
    for r in rows:
        if not r.get("candidate_offset_m", "").strip():
            continue
        by[float(r["candidate_offset_m"])].append(r)

    candidates = []
    for offset in sorted(by):
        declared = [r for r in by[offset] if r.get("placement_id", "").strip()]
        rr = [
            r for r in declared
            if r.get("permit_boundary_pass", "").strip()
            and r.get("permanent_transect_protected", "").strip()
            and r.get("placement_reproducible", "").strip()
            and r.get("restoration_workspace_pass", "").strip()
        ]
        passed = bool(rr) and len(rr) == len(declared) and all(
            as_bool(r["permit_boundary_pass"])
            and as_bool(r["permanent_transect_protected"])
            and as_bool(r["placement_reproducible"])
            and as_bool(r["restoration_workspace_pass"])
            for r in rr
        )
        candidates.append({
            "offset_m": offset, "n_complete": len(rr),
            "n_declared": len(declared), "pass": passed
        })

    selected = next((x for x in candidates if x["pass"]), None)
    if selected is None:
        return None, candidates

    return {
        "monitoring_authority_boundary_documented": True,
        "selected_minimum_perpendicular_transect_offset_m": selected["offset_m"],
        "representative_anchor_placement_test_passed": True,
    }, candidates


def summarize_preservation(path: Path, canonical, drift_absent):
    rows = read_csv(path)
    cells = defaultdict(list)
    for r in rows:
        method = r.get("method", "").strip()
        delay = r.get("delay_minutes", "").strip()
        if not method or not delay:
            continue
        delay = float(delay)
        if delay <= 0:
            continue
        required = (
            r.get("specimen_id", "").strip(),
            r.get("immediate_tnc_mg_g", "").strip(),
            r.get("delayed_tnc_mg_g", "").strip(),
            r.get("physically_suitable", "").strip(),
        )
        if not all(required):
            continue
        a = float(r["immediate_tnc_mg_g"])
        delayed = float(r["delayed_tnc_mg_g"])
        rel = abs(delayed-a)/a*100 if a != 0 else math.inf
        cells[(method, delay)].append({
            "specimen": r["specimen_id"].strip(),
            "rel": rel,
            "physically_suitable": as_bool(r["physically_suitable"]),
        })

    tested_delays = sorted({delay for _, delay in cells})
    results = []
    for (method, delay), vals in cells.items():
        rel = [v["rel"] for v in vals]
        n = len({v["specimen"] for v in vals})
        results.append({
            "method": method,
            "delay_minutes": delay,
            "n_specimens": n,
            "median_abs_relative_tnc_difference_pct": statistics.median(rel),
            "p90_abs_relative_tnc_difference_pct": quantile(rel, 0.90),
            "all_physically_suitable": all(v["physically_suitable"] for v in vals),
            "pass_numeric": (
                n >= 6
                and statistics.median(rel) <= 10
                and quantile(rel, 0.90) <= 15
                and all(v["physically_suitable"] for v in vals)
            ),
        })

    chosen = None
    for code, idx in sorted(
        METHOD_CODE_TO_CANONICAL_INDEX.items(),
        key=lambda x: x[1]
    ):
        passing = [x for x in results if x["method"] == code and x["pass_numeric"]]
        if passing:
            chosen = max(passing, key=lambda x: x["delay_minutes"])
            chosen_code = code
            chosen_idx = idx
            break

    if chosen is None:
        return None, results

    methods = canonical["preservation"]["candidate_methods"]
    if chosen_idx >= len(methods):
        raise RuntimeError("preservation method index exceeds canonical order")

    return {
        "selected_preservation_method": methods[chosen_idx],
        "tested_delays_minutes": tested_delays,
        "selected_maximum_collection_to_preservation_minutes": chosen["delay_minutes"],
        "paired_specimens_at_selected_delay": chosen["n_specimens"],
        "median_abs_relative_tnc_difference_pct": chosen["median_abs_relative_tnc_difference_pct"],
        "p90_abs_relative_tnc_difference_pct": chosen["p90_abs_relative_tnc_difference_pct"],
        "monotonic_directional_drift_absent": drift_absent,
        "candidate_method_order_rule": canonical["preservation"]["candidate_method_order_rule"],
    }, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", default="field/tnc_v2_method_pilot.json")
    ap.add_argument("--metadata", default="field/tnc_v2_raw_pilot_metadata.json")
    ap.add_argument("--hplc", default="field/tnc_v2_hplc_matrix_pilot.json")
    ap.add_argument("--tissue", default="field/tnc_v2_tissue_class_pilot.csv")
    ap.add_argument("--geometry", default="field/tnc_v2_core_geometry_pilot.csv")
    ap.add_argument("--offset", default="field/tnc_v2_offset_pilot.csv")
    ap.add_argument("--preservation", default="field/tnc_v2_preservation_pilot.csv")
    ap.add_argument("--out", default="field/tnc_v2_method_pilot_candidate.json")
    ap.add_argument("--audit-out", default="results/tnc_v2_raw_pilot_summary.json")
    args = ap.parse_args()

    canonical_path = Path(args.canonical)
    meta_path = Path(args.metadata)
    for p in (
        canonical_path, meta_path, Path(args.hplc), Path(args.tissue),
        Path(args.geometry), Path(args.offset), Path(args.preservation)
    ):
        check_no_future(p)

    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    if metadata.get("outcome_response_accessed") is not False:
        raise SystemExit("raw pilot metadata must explicitly keep outcome_response_accessed=false")

    candidate = json.loads(json.dumps(canonical))
    candidate["status"] = "RAW_PILOT_SUMMARY_CANDIDATE"
    candidate["outcome_response_accessed"] = False
    candidate["pilot_material"] = {
        "independent_rhizome_specimens": metadata.get("independent_rhizome_specimens"),
        "collection_locations_or_batches": metadata.get("collection_locations_or_batches"),
        "field_core_attempts": metadata.get("field_core_attempts"),
    }

    hplc = summarize_hplc(Path(args.hplc))
    candidate["analytical_qc"].update({
        k: v for k, v in hplc.items() if k != "raw_counts"
    })

    tissue, tissue_audit = summarize_tissue(Path(args.tissue), canonical)
    if tissue is not None:
        candidate["tissue_class"].update(tissue)

    geometry, geometry_audit = summarize_geometry(Path(args.geometry), canonical)
    if geometry is not None:
        candidate["core_geometry"].update(geometry)

    offset, offset_audit = summarize_offset(Path(args.offset))
    if offset is not None:
        candidate["transect_offset"].update(offset)

    drift = metadata.get("monotonic_directional_drift_absent")
    preservation, preservation_audit = summarize_preservation(
        Path(args.preservation), canonical, drift
    )
    if preservation is not None:
        candidate["preservation"].update(preservation)

    candidate["raw_pilot_provenance"] = {
        "metadata": args.metadata,
        "hplc": args.hplc,
        "tissue": args.tissue,
        "geometry": args.geometry,
        "offset": args.offset,
        "preservation": args.preservation,
    }
    candidate["raw_gate_detail"] = {
        "hplc_counts": hplc["raw_counts"],
        "tissue_candidates": tissue_audit,
        "geometry_candidates": geometry_audit,
        "offset_candidates": offset_audit,
        "preservation_cells": preservation_audit,
        "matrix_spike_all_within_85_115": hplc.get("matrix_spike_all_within_85_115"),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema": "tampa.tnc_v2_raw_pilot_summary.v1",
        "candidate_summary": args.out,
        "raw_gate_detail": candidate["raw_gate_detail"],
        "next_command": (
            "python validation/validate_tnc_v2_method_pilot.py "
            f"--pilot {args.out}"
        ),
        "boundary": "Raw method pilot only; future ecological response is prohibited.",
    }
    audit_out = Path(args.audit_out)
    audit_out.parent.mkdir(parents=True, exist_ok=True)
    audit_out.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
