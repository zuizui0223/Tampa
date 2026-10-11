#!/usr/bin/env python3
"""Post-hoc sampled-meter-mark overlap audit for Tampa recorded-loss warning.

Question: were marks where Thalassia was recorded in source year actually
resampled in the next-year transect visit? A generic independent point-draw
non-detection null cannot describe a fixed mark revisited without additional
detection error, displacement or true ecological change.

This audit is descriptive ONLY; does not refit or rescue early-warning models.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "results/quantitative_early_warning_v1.json"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mark_index(point_visits: pd.DataFrame):
    required = {"node_id", "year", "point_id", "thalassia_present"}
    if not required.issubset(point_visits.columns):
        raise RuntimeError(f"missing point-visit columns: {required - set(point_visits.columns)}")
    x = point_visits[list(required)].copy()
    if x.isna().any().any():
        raise RuntimeError("missing stable mark IDs/years/focal state")
    x["year"] = x["year"].astype(int)
    x["thalassia_present"] = x["thalassia_present"].astype(bool)
    x = x.groupby(["node_id", "year", "point_id"], as_index=False)["thalassia_present"].max()
    index = {}
    for (node, year), g in x.groupby(["node_id", "year"]):
        sampled = set(g["point_id"].astype(str))
        focal = set(g.loc[g.thalassia_present, "point_id"].astype(str))
        if not focal.issubset(sampled):
            raise RuntimeError("positive points not a subset of sampled marks")
        index[(str(node), int(year))] = (sampled, focal)
    return index


def quantify(transitions: pd.DataFrame, point_visits: pd.DataFrame) -> pd.DataFrame:
    index = mark_index(point_visits)
    rows = []
    for t in transitions.itertuples(index=False):
        node = str(t.node_id)
        sy, ty = int(t.source_year), int(t.target_year)
        if ty != sy + 1:
            raise RuntimeError("nonconsecutive year transition")
        if (node, sy) not in index or (node, ty) not in index:
            raise RuntimeError(f"missing eligible mark observation: {node} {sy}->{ty}")
        sm, sp = index[(node, sy)]
        tm, tp = index[(node, ty)]
        if not sp:
            raise RuntimeError("registered source-positive transition has zero positive marks")
        if int(t.loss) != int(not tp):
            raise RuntimeError(f"recorded-loss registry mismatch {node} {ty}")
        seen = sp & tm
        rows.append({
            "node_id": node,
            "source_year": sy,
            "target_year": ty,
            "recorded_loss": int(t.loss),
            "source_sampled_mark_count": len(sm),
            "target_sampled_mark_count": len(tm),
            "source_positive_mark_count": len(sp),
            "source_positive_marks_resampled": len(seen),
            "fraction_source_positive_marks_resampled": len(seen) / len(sp),
            "shared_any_mark_count": len(sm & tm),
            "same_positive_mark_resampled": int(bool(seen)),
            "all_source_positive_marks_resampled": int(seen == sp),
            "any_target_focal_record": int(bool(tp)),
        })
    return pd.DataFrame(rows)


def summarize(d: pd.DataFrame) -> dict:
    def block(z):
        n = len(z)
        return {
            "transect_transitions": n,
            "nodes": int(z.node_id.nunique()) if n else 0,
            "recorded_loss_events": int(z.recorded_loss.sum()) if n else 0,
            "resampled_at_least_one_source_positive_mark": int(z.same_positive_mark_resampled.sum()) if n else 0,
            "all_source_positive_marks_resampled": int(z.all_source_positive_marks_resampled.sum()) if n else 0,
            "zero_source_positive_marks_resampled": int((z.source_positive_marks_resampled == 0).sum()) if n else 0,
            "median_fraction_source_positive_resampled": float(z.fraction_source_positive_marks_resampled.median()) if n else None,
            "median_target_sampled_marks": float(z.target_sampled_mark_count.median()) if n else None,
        }
    return {
        "overall": block(d),
        "recorded_losses": block(d[d.recorded_loss == 1]),
        "recorded_persistence": block(d[d.recorded_loss == 0]),
        "target_2016_losses": block(d[(d.recorded_loss == 1) & (d.target_year == 2016)]),
        "by_target_year": [
            {"target_year": int(y), **block(g)}
            for y, g in d.groupby("target_year")
        ],
    }


def self_test():
    v = pd.DataFrame([
        {"node_id": "n1", "year": 2020, "point_id": "n1:10", "thalassia_present": True},
        {"node_id": "n1", "year": 2020, "point_id": "n1:20", "thalassia_present": False},
        {"node_id": "n1", "year": 2021, "point_id": "n1:10", "thalassia_present": False},
        {"node_id": "n1", "year": 2021, "point_id": "n1:30", "thalassia_present": False},
        {"node_id": "n2", "year": 2020, "point_id": "n2:10", "thalassia_present": True},
        {"node_id": "n2", "year": 2021, "point_id": "n2:30", "thalassia_present": False},
    ])
    t = pd.DataFrame([
        {"node_id": "n1", "source_year": 2020, "target_year": 2021, "loss": 1},
        {"node_id": "n2", "source_year": 2020, "target_year": 2021, "loss": 1},
    ])
    d = quantify(t, v).set_index("node_id")
    assert d.loc["n1", "source_positive_marks_resampled"] == 1
    assert d.loc["n2", "source_positive_marks_resampled"] == 0
    assert d.loc["n1", "same_positive_mark_resampled"] == 1
    assert d.loc["n2", "same_positive_mark_resampled"] == 0
    bad = t.copy()
    bad.loc[0, "loss"] = 0
    try:
        quantify(bad, v)
    except RuntimeError:
        pass
    else:
        raise AssertionError("registered outcome mismatch should fail closed")
    print("PASS: exact-mark overlap and loss-registry falsification self-test")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/generated_site_warning"))
    p.add_argument("--out", type=Path, default=Path("results/generated_site_warning"))
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    orig = load_script("tampa_original_early_warning", ROOT / "analysis/09_quantitative_early_warning.py")
    community = load_script("tampa_original_point_builder", ROOT / "analysis/33_community_buffering.py")
    quant = pd.read_csv(args.input / "quant_annual_panel.csv")
    annual = pd.read_csv(args.input / "community_quant_annual.csv")
    transitions = orig.build_transitions(quant, annual)
    frozen = json.loads(FROZEN.read_text())
    if len(transitions) != frozen["transition_registry"]["source_positive_consecutive_transitions"] or int(transitions.loss.sum()) != frozen["transition_registry"]["recorded_losses"]:
        raise RuntimeError("frozen cohort drift before mark reconstruction")
    raw = {k: community.fetch(v) for k, v in community.FILES.items()}
    parents, points, children, _ = community.parse_event(raw["event"])
    occurrence = community.parse_occurrence(raw["occurrence"], set(points))
    _, point_visits = community.build_visit_panel(parents, points, children, occurrence)
    d = quantify(transitions, point_visits)
    s = summarize(d)
    predictions = pd.read_csv(args.input / "early_warning_site_identity_predictions.csv")
    scored = d.merge(predictions[["node_id", "target_year", "loss"]],
                     on=["node_id", "target_year"], how="inner", validate="one_to_one")
    if len(scored) != 570 or int(scored.recorded_loss.sum()) != 19 or (scored.recorded_loss != scored.loss).any():
        raise RuntimeError("walk-forward prediction cohort/label mismatch")
    s["scored_early_warning_cohort"] = summarize(scored)["overall"]
    s["scored_recorded_losses"] = summarize(scored)["recorded_losses"]
    report = {
        "schema": "tampa.fixed_mark_overlap_observation_audit_v1",
        "evidence_class": "post_hoc_descriptive_source_response_opened",
        "source": "tbep-tech/obis-example pinned 6c567beff95ea04f0e397101befb49d5233ace8f",
        "registry": {"source_positive_transitions": len(d), "recorded_losses": int(d.recorded_loss.sum()),
                     "walkforward_scored_rows": len(scored), "scored_losses": int(scored.recorded_loss.sum())},
        "summary": s,
        "interpretation_boundary": [
            "Revisiting an earlier positive mark with subsequent non-detection is incompatible with the *joint assumption* of completely unchanged local mark presence and perfect detection; it does NOT identify which assumption failed.",
            "Zero mark overlap makes changed sampling footprint a possible explanation, not evidence for or against actual focal mortality.",
            "Annual source/target states use any occurrence over eligible visits; they cannot distinguish within-year turnover or observation errors.",
            "Marked locations are fixed nominal metre marks, but survey repositioning or protocol changes may alter effective micro-site footprints.",
            "This is a retrospective observation-process diagnostic, not a positive test of a biological early-warning mechanism.",
            "No new performance threshold, subgroup rescue, learned detection parameter or extinction claim is authorized.",
        ],
    }
    args.out.mkdir(parents=True, exist_ok=True)
    d.to_csv(args.out / "early_warning_fixed_mark_overlap_transitions_v1.csv", index=False)
    (args.out / "early_warning_fixed_mark_overlap_v1.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"registry": report["registry"],
                      "overall_losses": s["recorded_losses"],
                      "scored_losses": s["scored_recorded_losses"],
                      "target_2016_losses": s["target_2016_losses"]}, indent=2))


if __name__ == "__main__":
    main()
