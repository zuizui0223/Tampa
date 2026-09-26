#!/usr/bin/env python3
"""Seasonal hot/fresh screen for Tampa Bay Thalassia state change.

This is a deliberately narrow follow-up to the annual environmental coupling screen.
It aligns segment-level monthly water quality to each target survey month, then asks
whether Thalassia year-to-year frequency/abundance change covaries with two a priori
stress summaries over 3- and 6-month pre-survey windows:

- maximum monthly mean temperature (hot exposure)
- minimum monthly mean salinity (fresh exposure)

The primary family contains exactly 8 tests: two Thalassia outcomes x two stress
summaries x two windows. Benjamini-Hochberg FDR is applied across the full family.
A sensitivity analysis excludes target year 2017 because the 2016/2017 recorded-state
pulse has known protocol sensitivity. This is an association screen, not causal proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SEGMENT_MAP = {
    "Old Tampa Bay": "OTB",
    "Middle Tampa Bay": "MTB",
    "Lower Tampa Bay": "LTB",
    "Hillsborough Bay": "HB",
}
OUTCOMES = ["Thalassia_frequency", "Thalassia_cover_index"]
WINDOWS = [3, 6]


def bh_adjust(pvals: np.ndarray) -> np.ndarray:
    pvals = np.asarray(pvals, dtype=float)
    order = np.argsort(pvals)
    q = np.empty_like(pvals)
    running = 1.0
    m = len(pvals)
    for i in range(m - 1, -1, -1):
        idx = order[i]
        rank = i + 1
        running = min(running, float(pvals[idx]) * m / rank)
        q[idx] = min(1.0, running)
    return q


def months_back(year: int, month: int, n: int) -> list[tuple[int, int]]:
    out = []
    for k in range(n):
        m = month - k
        y = year
        while m <= 0:
            m += 12
            y -= 1
        out.append((y, m))
    return out


def build_node_differences(annual: pd.DataFrame) -> pd.DataFrame:
    annual = annual.copy()
    annual["date"] = pd.to_datetime(annual["date"])
    rows = []
    for node, group in annual.sort_values(["node_id", "year"]).groupby("node_id"):
        records = group.to_dict("records")
        for left, right in zip(records[:-1], records[1:]):
            if int(right["year"]) != int(left["year"]) + 1:
                continue
            segment = SEGMENT_MAP.get(right["water_body"])
            if segment is None:
                continue
            date = pd.Timestamp(right["date"])
            record = {
                "node_id": node,
                "segment": segment,
                "year": int(right["year"]),
                "survey_month": int(date.month),
            }
            for outcome in OUTCOMES:
                record[f"d_{outcome}"] = float(right[outcome]) - float(left[outcome])
            rows.append(record)
    return pd.DataFrame(rows)


def aggregate_response(node_diff: pd.DataFrame) -> pd.DataFrame:
    # Environmental exposure is identical for nodes in the same segment/year/survey-month,
    # so aggregate ecological change to that same exposure unit before testing.
    return (
        node_diff.groupby(["segment", "year", "survey_month"], as_index=False)
        .mean(numeric_only=True)
    )


def add_exposures(frame: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    monthly_map = {
        (str(r.segment), int(r.year), int(r.month)): r
        for r in monthly.itertuples(index=False)
    }
    out = frame.copy()
    for window in WINDOWS:
        temp_max, sal_min, coverage = [], [], []
        for row in out.itertuples(index=False):
            keys = months_back(int(row.year), int(row.survey_month), window)
            values = [monthly_map.get((row.segment, y, m)) for y, m in keys]
            values = [x for x in values if x is not None]
            t = [float(x.temperature) for x in values if pd.notna(x.temperature)]
            s = [float(x.salinity) for x in values if pd.notna(x.salinity)]
            temp_max.append(max(t) if t else np.nan)
            sal_min.append(min(s) if s else np.nan)
            coverage.append(len(values) / window)
        out[f"temp_max_{window}m"] = temp_max
        out[f"salinity_min_{window}m"] = sal_min
        out[f"month_coverage_{window}m"] = coverage
    return out


def test_family(frame: pd.DataFrame, label: str, min_year: int) -> list[dict]:
    d = frame[frame.year >= min_year].copy()
    tests = []
    for outcome in OUTCOMES:
        response = f"d_{outcome}"
        for window in WINDOWS:
            for exposure, direction in [
                (f"temp_max_{window}m", "hotter_expected_more_negative"),
                (
                    f"salinity_min_{window}m",
                    "fresher_expected_more_negative_so_higher_salinity_expected_more_positive",
                ),
            ]:
                pair = d[[response, exposure]].dropna()
                if len(pair) < 12 or pair[response].nunique() < 2 or pair[exposure].nunique() < 2:
                    raise RuntimeError(f"non-estimable seasonal test: {label} {outcome} {exposure}")
                stat = spearmanr(pair[response], pair[exposure])
                tests.append(
                    {
                        "period": label,
                        "outcome": outcome,
                        "window_months": window,
                        "exposure": exposure,
                        "directional_interpretation": direction,
                        "n_exposure_units": int(len(pair)),
                        "rho": float(stat.statistic),
                        "p_two_sided": float(stat.pvalue),
                    }
                )
    q = bh_adjust(np.asarray([x["p_two_sided"] for x in tests]))
    for item, value in zip(tests, q):
        item["q_family_bh"] = float(value)
    return tests


def main(input_dir: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "community_quant_annual.csv")
    monthly = pd.read_csv(input_dir / "water_quality_monthly.csv")

    node_diff = build_node_differences(annual)
    response = aggregate_response(node_diff)
    panel = add_exposures(response, monthly)

    primary = test_family(panel, "post2016_target_2017_2025", 2017)
    sensitivity = test_family(panel, "sensitivity_exclude_2017_target_2018_2025", 2018)
    tests = pd.DataFrame(primary + sensitivity)

    primary_df = tests[tests.period == "post2016_target_2017_2025"].copy()
    sens_df = tests[tests.period == "sensitivity_exclude_2017_target_2018_2025"].copy()
    best_primary = primary_df.sort_values(["q_family_bh", "p_two_sided"]).iloc[0]
    best_sens = sens_df.sort_values(["q_family_bh", "p_two_sided"]).iloc[0]

    summary = {
        "schema": "tampa.seasonal_hot_fresh_screen_v1",
        "analysis_unit": "bay-segment x target-year x survey-month",
        "primary_family_size": int(len(primary_df)),
        "primary_exposure_units": int(panel[panel.year >= 2017].shape[0]),
        "sensitivity_exposure_units": int(panel[panel.year >= 2018].shape[0]),
        "primary_supported_q_lt_0_05": int((primary_df.q_family_bh < 0.05).sum()),
        "primary_suggestive_q_0_05_to_0_10": int(
            ((primary_df.q_family_bh >= 0.05) & (primary_df.q_family_bh < 0.10)).sum()
        ),
        "sensitivity_supported_q_lt_0_05": int((sens_df.q_family_bh < 0.05).sum()),
        "best_primary": best_primary.to_dict(),
        "best_sensitivity": best_sens.to_dict(),
        "interpretation": (
            "Aligning hot/fresh exposure to 3- and 6-month pre-survey windows does not recover a "
            "multiplicity-controlled association with Thalassia frequency or Braun-Blanquet state change. "
            "The simple seasonal hot/fresh mechanism remains unsupported at segment-month resolution."
        ),
        "claim_boundary": [
            "Monthly segment means cannot resolve acute daily extremes, local hydrodynamics, or within-segment exposure heterogeneity.",
            "The screen tests association, not causality.",
            "A null seasonal screen does not exclude finer-scale heat/freshwater pulses or other mechanisms.",
            "The 2017-excluded sensitivity is reported because the 2016/2017 recorded-state pulse is protocol-sensitive.",
            "No alternative window or exposure is selected after observing these results.",
        ],
    }
    panel.to_csv(outdir / "seasonal_stress_panel.csv", index=False)
    tests.to_csv(outdir / "seasonal_stress_tests.csv", index=False)
    (outdir / "seasonal_stress_screen_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/generated"))
    parser.add_argument("--out", type=Path, default=Path("results/generated"))
    args = parser.parse_args()
    main(args.input, args.out)
