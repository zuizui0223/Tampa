#!/usr/bin/env python3
"""Conservative environmental-coupling screen for Tampa Bay seagrass state change.

Uses outputs produced by 02_water_quality_screen.py and 05_community_compensation.py.
The ecological unit is segment-year, not individual transect rows, so annual water-quality
values are not pseudo-replicated across transects. Tests are descriptive and FDR-adjusted.
No causal interpretation is allowed.
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
ENV = ["salinity", "temperature", "chlorophyll", "total_nitrogen", "secchi", "turbidity"]
OUTCOMES = [
    "Thalassia_frequency",
    "Thalassia_cover_index",
    "Halodule_frequency",
    "Syringodium_frequency",
]


def build_state_differences(annual: pd.DataFrame) -> pd.DataFrame:
    rows = []
    annual = annual.sort_values(["node_id", "year"])
    for node, group in annual.groupby("node_id"):
        records = group.to_dict("records")
        for left, right in zip(records[:-1], records[1:]):
            if int(right["year"]) != int(left["year"]) + 1:
                continue
            segment = SEGMENT_MAP.get(right["water_body"])
            if segment is None:
                continue
            rec = {"node_id": node, "segment": segment, "year": int(right["year"])}
            for metric in OUTCOMES:
                rec[f"d_{metric}"] = float(right[metric]) - float(left[metric])
            rows.append(rec)
    return pd.DataFrame(rows)


def segment_year_state(node_diff: pd.DataFrame) -> pd.DataFrame:
    return node_diff.groupby(["segment", "year"], as_index=False).mean(numeric_only=True)


def add_wq_differences(wq: pd.DataFrame) -> pd.DataFrame:
    wq = wq.sort_values(["segment", "year"]).copy()
    for metric in ENV:
        wq[f"d_{metric}"] = wq.groupby("segment")[metric].diff()
    keep = ["segment", "year"] + ENV + [f"d_{m}" for m in ENV]
    return wq[keep]


def bh_adjust(pvals: np.ndarray) -> np.ndarray:
    order = np.argsort(pvals)
    adjusted = np.empty_like(pvals, dtype=float)
    m = len(pvals)
    running = 1.0
    for rank_from_end, idx in enumerate(order[::-1], start=1):
        rank = m - rank_from_end + 1
        running = min(running, float(pvals[idx]) * m / rank)
        adjusted[idx] = min(1.0, running)
    return adjusted


def screen(frame: pd.DataFrame, period_name: str, year_min: int | None) -> list[dict]:
    d = frame if year_min is None else frame[frame.year >= year_min]
    rows = []
    for outcome in OUTCOMES:
        response = f"d_{outcome}"
        for exposure_mode in ["annual_level", "annual_change"]:
            cols = ENV if exposure_mode == "annual_level" else [f"d_{x}" for x in ENV]
            local = []
            for env_col in cols:
                pair = d[[response, env_col]].dropna()
                if len(pair) < 12 or pair[response].nunique() < 2 or pair[env_col].nunique() < 2:
                    continue
                test = spearmanr(pair[response], pair[env_col])
                local.append({
                    "period": period_name,
                    "outcome": outcome,
                    "exposure_mode": exposure_mode,
                    "environment": env_col.removeprefix("d_"),
                    "n_segment_years": int(len(pair)),
                    "rho": float(test.statistic),
                    "p": float(test.pvalue),
                })
            if local:
                q = bh_adjust(np.asarray([x["p"] for x in local], dtype=float))
                for item, qi in zip(local, q):
                    item["q_within_outcome_mode"] = float(qi)
                    rows.append(item)
    return rows


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "community_quant_annual.csv")
    wq = pd.read_csv(input_dir / "water_quality_annual.csv")

    node_diff = build_state_differences(annual)
    state = segment_year_state(node_diff)
    merged = state.merge(add_wq_differences(wq), on=["segment", "year"], how="inner")

    tests = screen(merged, "full_1998_2025", None)
    tests += screen(merged, "post2016_2017_2025", 2017)
    tests_df = pd.DataFrame(tests).sort_values(
        ["period", "outcome", "exposure_mode", "q_within_outcome_mode", "p"]
    )

    post = tests_df[tests_df.period == "post2016_2017_2025"].copy()
    supported = post[post.q_within_outcome_mode < 0.05]
    suggestive = post[(post.q_within_outcome_mode >= 0.05) & (post.q_within_outcome_mode < 0.10)]

    summary = {
        "schema": "tampa.environmental_coupling_v1",
        "unit": "bay-segment x target-year; ecological response is mean consecutive-year within-transect state change",
        "periods": ["full_1998_2025", "post2016_2017_2025"],
        "environmental_metrics": ENV,
        "outcomes": OUTCOMES,
        "post2016_segment_years": int(merged[merged.year >= 2017].shape[0]),
        "post2016_fdr_lt_0_05": int(len(supported)),
        "post2016_fdr_0_05_to_0_10": int(len(suggestive)),
        "post2016_supported_rows": supported.to_dict("records"),
        "post2016_suggestive_rows": suggestive.to_dict("records"),
        "interpretation": (
            "No simple annual water-quality variable currently provides a multiplicity-controlled, "
            "segment-year explanation of post-2016 Thalassia/community state changes. Environmental "
            "causation remains unresolved; the stronger result is spatially heterogeneous ecological-state "
            "decoupling and community reorganization."
        ),
        "claim_boundary": [
            "Annual segment means are a coarse exposure scale and cannot represent acute events or within-segment gradients.",
            "Associations are descriptive and are not causal effects.",
            "Absence of FDR-supported annual coupling does not reject temperature, salinity, hydrologic, or other mechanisms operating at finer temporal/spatial scales.",
            "Do not select one nominally small unadjusted p-value as a mechanism after inspecting the screen.",
        ],
    }

    node_diff.to_csv(outdir / "environment_node_year_differences.csv", index=False)
    merged.to_csv(outdir / "environment_segment_year_panel.csv", index=False)
    tests_df.to_csv(outdir / "environment_coupling_tests.csv", index=False)
    (outdir / "environmental_coupling_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/generated"))
    parser.add_argument("--out", type=Path, default=Path("results/generated"))
    args = parser.parse_args()
    main(args.input, args.out)
