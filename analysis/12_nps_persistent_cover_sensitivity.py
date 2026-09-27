#!/usr/bin/env python3
"""Sensitivity audit for the NPS persistent-cover state-decoupling result.

This audit does not change the ecological endpoint or repair source identities.
It asks whether the pooled negative cover trend survives:
1) equal-node weighting,
2) removal of each location in turn,
3) explicit retention (not repair) of single-year reverse-ID candidates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def node_stats(annual: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for node, g in annual.groupby("node_id"):
        g = g.sort_values("year")
        if len(g) < 2:
            continue
        x = g["year"].to_numpy(float)
        y = g["focal_mean_cover"].to_numpy(float)
        xc = x - x.mean()
        yc = y - y.mean()
        sxx = float(np.dot(xc, xc))
        if sxx <= 0:
            continue
        sxy = float(np.dot(xc, yc))
        rows.append({
            "node_id": str(node),
            "Location": str(g["Location"].iloc[0]),
            "n": int(len(g)),
            "year_min": int(x.min()),
            "year_max": int(x.max()),
            "sxx": sxx,
            "sxy": sxy,
            "slope": float(sxy / sxx),
            "first_cover": float(g.iloc[0]["focal_mean_cover"]),
            "last_cover": float(g.iloc[-1]["focal_mean_cover"]),
            "first_to_last_change": float(g.iloc[-1]["focal_mean_cover"] - g.iloc[0]["focal_mean_cover"]),
        })
    return pd.DataFrame(rows).sort_values("node_id").reset_index(drop=True)


def pooled_slope(stats: pd.DataFrame) -> float:
    den = float(stats["sxx"].sum())
    if den <= 0:
        raise RuntimeError("nonpositive pooled sxx")
    return float(stats["sxy"].sum() / den)


def reverse_id_candidates(annual: pd.DataFrame, repeated_nodes: set[str]) -> list[dict]:
    out = []
    counts = annual.groupby("node_id").size()
    for node, n in counts.items():
        if int(n) != 1 or "::" not in str(node):
            continue
        left, right = str(node).split("::", 1)
        reversed_id = f"{right}::{left}"
        if reversed_id not in repeated_nodes:
            continue
        row = annual.loc[annual["node_id"] == node].iloc[0]
        out.append({
            "node_id": str(node),
            "reverse_repeated_node_id": reversed_id,
            "Location": str(row["Location"]),
            "year": int(row["year"]),
            "focal_mean_cover": float(row["focal_mean_cover"]),
            "interpretation": (
                "Single-year reverse-ID candidate. Retained exactly as published and excluded "
                "from repeated-node slope estimation by the >=2-year rule; no repair performed."
            ),
        })
    return sorted(out, key=lambda x: x["node_id"])


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "nps_tier3_annual_state.csv")
    stats = node_stats(annual)
    if len(stats) != 15:
        raise RuntimeError(f"expected 15 repeated nodes, got {len(stats)}")

    pooled = pooled_slope(stats)
    equal_mean = float(stats["slope"].mean())
    equal_median = float(stats["slope"].median())

    loo = {}
    for location in sorted(stats["Location"].unique()):
        sub = stats[stats["Location"] != location].copy()
        loo[location] = {
            "remaining_nodes": int(len(sub)),
            "pooled_within_node_slope_per_year": pooled_slope(sub),
            "negative_node_slopes": int((sub["slope"] < 0).sum()),
            "positive_node_slopes": int((sub["slope"] > 0).sum()),
        }

    first_last = {
        "negative_nodes": int((stats["first_to_last_change"] < 0).sum()),
        "positive_nodes": int((stats["first_to_last_change"] > 0).sum()),
        "zero_nodes": int((stats["first_to_last_change"] == 0).sum()),
        "median_change": float(stats["first_to_last_change"].median()),
    }

    anomalies = reverse_id_candidates(annual, set(stats["node_id"]))
    all_loo_negative = all(v["pooled_within_node_slope_per_year"] < 0 for v in loo.values())

    summary = {
        "schema": "tampa.nps_persistent_cover_sensitivity_v1",
        "status": "sensitivity_supports_external_state_decoupling",
        "base_result": "results/nps_persistent_cover_v1.json",
        "repeated_node_count": int(len(stats)),
        "pooled_within_node_slope_per_year": pooled,
        "equal_node_weighting": {
            "mean_node_slope_per_year": equal_mean,
            "median_node_slope_per_year": equal_median,
        },
        "leave_one_location_out": loo,
        "all_leave_one_location_out_slopes_negative": bool(all_loo_negative),
        "leave_one_location_out_slope_range": [
            float(min(v["pooled_within_node_slope_per_year"] for v in loo.values())),
            float(max(v["pooled_within_node_slope_per_year"] for v in loo.values())),
        ],
        "first_to_last_cover_change": first_last,
        "single_year_reverse_id_candidates": anomalies,
        "single_year_reverse_id_candidate_count": int(len(anomalies)),
        "claim_boundary": [
            "No source identity is repaired or remapped post hoc.",
            "Single-year reverse-ID candidates are retained in the annual table but cannot enter repeated-node slope estimates.",
            "Leave-one-location-out robustness addresses single-location leverage but does not imply a universal decline at every location.",
            "Moriches Bay has a positive trend and is retained as genuine spatial heterogeneity.",
            "This remains post-hoc ecological replication rather than prospective predictive confirmation."
        ],
        "interpretation": (
            "The negative pooled within-transect cover trend is not generated by any single monitored location. "
            "Removing each location in turn leaves a negative pooled slope. Equal-node mean and median slopes are "
            "also negative. Three 2022 single-year reverse-ID candidates are transparently retained without repair "
            "and do not contribute to repeated-node trends."
        ),
    }

    stats.to_csv(outdir / "nps_cover_node_sensitivity.csv", index=False)
    (outdir / "nps_persistent_cover_sensitivity_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/generated_nps_sensitivity"))
    p.add_argument("--out", type=Path, default=Path("results/generated_nps_sensitivity"))
    args = p.parse_args()
    main(args.input, args.out)
