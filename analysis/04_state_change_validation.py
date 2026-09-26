#!/usr/bin/env python3
"""Within-transect validation of quantitative Thalassia state change.

This script consumes outputs produced by 03_quantitative_state.py in the same CI run.
It asks whether binary recorded presence can remain comparatively stable while
quantitative meadow state changes within fixed transects.

The primary quantitative variables are point frequency and the ordinal
Braun-Blanquet cover index. Blade length and shoot density are secondary because
measurement availability is incomplete. Trend models use node fixed effects and
adjust for survey season (cyclic day of year) plus log sampled-point count.
Cluster bootstrap resamples transect nodes, not rows.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

SEGMENTS = [
    "Old Tampa Bay",
    "Middle Tampa Bay",
    "Lower Tampa Bay",
    "Boca Ciega Bay",
    "Hillsborough Bay",
]
METRICS = [
    "detected",
    "focal_frequency",
    "bb_cover_mean_all_points",
    "blade_length_mean_mm",
    "shoot_density_mean_m2",
]
PRIMARY_QUANT = ["focal_frequency", "bb_cover_mean_all_points"]
SECONDARY_QUANT = ["blade_length_mean_mm", "shoot_density_mean_m2"]
PULSE_NODES = [
    "TBEP:seagrass:loc:S1T1",
    "TBEP:seagrass:loc:S3T12",
    "TBEP:seagrass:loc:S3T3",
    "TBEP:seagrass:loc:S3T4",
    "TBEP:seagrass:loc:S3T5",
]
BOOTSTRAPS = 3000
SEED = 20260926


def _safe_float(x):
    return None if x is None or not math.isfinite(float(x)) else float(x)


def _fit_within_node(
    frame: pd.DataFrame,
    metric: str,
    controls: bool,
    min_years: int = 5,
) -> dict | None:
    variables = ["year"]
    if controls:
        variables += ["sin_doy", "cos_doy", "log_points"]
    columns = ["node_id", metric] + variables
    d = frame[columns].dropna().copy()
    counts = d.groupby("node_id").size()
    nodes = sorted(counts[counts >= min_years].index.tolist())
    d = d[d.node_id.isin(nodes)].copy()
    if len(nodes) < 3:
        return None

    cross = {}
    for node, group in d.groupby("node_id"):
        y = group[metric].to_numpy(float)
        x = group[variables].to_numpy(float)
        y = y - y.mean()
        x = x - x.mean(axis=0)
        cross[node] = (x.T @ x, x.T @ y)

    def estimate(selected):
        xtx = np.sum([cross[node][0] for node in selected], axis=0)
        xty = np.sum([cross[node][1] for node in selected], axis=0)
        return np.linalg.pinv(xtx) @ xty

    beta = estimate(nodes)
    rng = np.random.default_rng(SEED)
    boot = np.empty((BOOTSTRAPS, len(beta)), dtype=float)
    for i in range(BOOTSTRAPS):
        selected = rng.choice(nodes, size=len(nodes), replace=True).tolist()
        boot[i] = estimate(selected)

    ci = np.quantile(boot[:, 0], [0.025, 0.975])
    return {
        "nodes": len(nodes),
        "rows": int(len(d)),
        "year_slope": float(beta[0]),
        "year_slope_ci95": [float(ci[0]), float(ci[1])],
        "adjusted_for": variables[1:],
    }


def trend_audit(annual: pd.DataFrame, visit: pd.DataFrame) -> dict:
    v = visit.copy()
    v["date"] = pd.to_datetime(v["date"])
    v["doy"] = v.date.dt.dayofyear
    effort = (
        v.groupby(["node_id", "year"], as_index=False)
        .agg(doy=("doy", "median"), point_count=("child_point_count", "mean"))
    )
    d = annual.merge(effort, on=["node_id", "year"], how="left")
    d["sin_doy"] = np.sin(2 * np.pi * (d.doy - 1) / 365.2425)
    d["cos_doy"] = np.cos(2 * np.pi * (d.doy - 1) / 365.2425)
    d["log_points"] = np.log(d.point_count)

    result = {}
    for segment in SEGMENTS:
        segment_frame = d[
            (d.water_body == segment) & d.year.between(2016, 2025)
        ].copy()
        result[segment] = {}
        for metric in METRICS:
            result[segment][metric] = {
                "unadjusted": _fit_within_node(segment_frame, metric, controls=False),
                "season_effort_adjusted": _fit_within_node(
                    segment_frame, metric, controls=True
                ),
            }

    # A conservative descriptive flag: binary detection has no wholly-negative
    # adjusted CI, while at least one quantitative-state metric does.
    cryptic = []
    for segment in SEGMENTS:
        det = result[segment]["detected"]["season_effort_adjusted"]
        if not det:
            continue
        det_ci = det["year_slope_ci95"]
        detection_not_clearly_declining = det_ci[1] >= 0
        negative_metrics = []
        for metric in PRIMARY_QUANT + SECONDARY_QUANT:
            item = result[segment][metric]["season_effort_adjusted"]
            if item and item["year_slope_ci95"][1] < 0:
                negative_metrics.append(metric)
        if detection_not_clearly_declining and negative_metrics:
            cryptic.append(
                {
                    "segment": segment,
                    "negative_quantitative_metrics": negative_metrics,
                    "detection_year_slope": det["year_slope"],
                    "detection_ci95": det_ci,
                }
            )
    return {"models": result, "cryptic_degradation_candidates": cryptic}


def pulse_recovery(annual: pd.DataFrame) -> dict:
    d = annual[
        annual.node_id.isin(PULSE_NODES)
        & annual.year.isin([2015, 2016, 2017, 2018])
    ].copy()
    out = {"nodes": PULSE_NODES, "metrics": {}}
    for metric in [
        "focal_frequency",
        "bb_cover_mean_all_points",
        "blade_length_mean_mm",
        "shoot_density_mean_m2",
    ]:
        pivot = d.pivot(index="node_id", columns="year", values=metric)
        metric_out = {}
        for target in [2017, 2018]:
            if 2015 not in pivot or target not in pivot:
                continue
            pair = pivot[[2015, target]].dropna()
            if len(pair) == 0:
                continue
            base = pair[2015].replace(0, np.nan)
            ratio = pair[target] / base
            metric_out[str(target)] = {
                "n": int(len(pair)),
                "mean_change_from_2015": float((pair[target] - pair[2015]).mean()),
                "median_ratio_to_2015": _safe_float(ratio.median()),
                "node_ratios": {
                    str(node): _safe_float(value)
                    for node, value in ratio.items()
                },
            }
        out["metrics"][metric] = metric_out
    return out


def protocol_audit(visit: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    v = visit.copy()
    v["date"] = pd.to_datetime(v["date"])
    v["doy"] = v.date.dt.dayofyear
    yearly = (
        v.groupby("year", as_index=False)
        .agg(
            visits=("unit_id", "size"),
            nodes=("node_id", "nunique"),
            doy_median=("doy", "median"),
            doy_min=("doy", "min"),
            doy_max=("doy", "max"),
            point_count_median=("child_point_count", "median"),
            point_count_mean=("child_point_count", "mean"),
        )
    )
    pulse = v[
        v.node_id.isin(PULSE_NODES) & v.year.isin([2015, 2016, 2017])
    ][
        [
            "node_id",
            "year",
            "date",
            "water_body",
            "child_point_count",
            "focal_point_count",
            "focal_frequency",
        ]
    ].sort_values(["node_id", "year"])

    y2016 = v[v.year == 2016].copy()
    dec25 = y2016[y2016.date == pd.Timestamp("2016-12-25")]
    dec25_by_segment = (
        dec25.groupby("water_body")
        .agg(
            visits=("unit_id", "size"),
            positive_visits=("focal_point_count", lambda x: int((x > 0).sum())),
            sampled_points=("child_point_count", "sum"),
        )
        .reset_index()
    )

    paired = (
        v[v.year.isin([2015, 2016])]
        .groupby(["node_id", "year"], as_index=False)
        .agg(points=("child_point_count", "mean"))
        .pivot(index="node_id", columns="year", values="points")
        .dropna()
    )
    paired["ratio_2016_to_2015"] = paired[2016] / paired[2015]
    pulse_ratios = paired.loc[
        paired.index.intersection(PULSE_NODES), "ratio_2016_to_2015"
    ]

    summary = {
        "yearly_survey_calendar": yearly.to_dict("records"),
        "2016_dec25": {
            "visit_count": int(len(dec25)),
            "fraction_of_2016_visits": float(len(dec25) / len(y2016)),
            "by_segment": dec25_by_segment.to_dict("records"),
        },
        "point_effort_ratio_2016_to_2015": {
            "paired_nodes": int(len(paired)),
            "median": float(paired["ratio_2016_to_2015"].median()),
            "mean": float(paired["ratio_2016_to_2015"].mean()),
            "pulse_nodes": {
                str(node): float(value) for node, value in pulse_ratios.items()
            },
        },
        "interpretation": (
            "The 2016 turnover pulse is protocol-sensitive: survey dates shift late "
            "and several pulse transects change sampled-point counts. The pulse is "
            "therefore retained as exploratory until original-date/protocol semantics "
            "are independently resolved."
        ),
    }
    return summary, pulse


def main(outdir: Path) -> None:
    annual_path = outdir / "quant_annual_panel.csv"
    visit_path = outdir / "quant_visit_panel.csv"
    if not annual_path.exists() or not visit_path.exists():
        raise RuntimeError(
            "Run analysis/03_quantitative_state.py first in the same output directory"
        )
    annual = pd.read_csv(annual_path)
    visit = pd.read_csv(visit_path)

    trends = trend_audit(annual, visit)
    pulse = pulse_recovery(annual)
    protocol, pulse_protocol = protocol_audit(visit)
    summary = {
        "analysis": "within_transect_quantitative_state_validation_v1",
        "period": [2016, 2025],
        "bootstrap_nodes": BOOTSTRAPS,
        "trend_audit": trends,
        "pulse_recovery": pulse,
        "protocol_audit": protocol,
        "claim_boundary": [
            "Within-transect slopes are descriptive long-term state changes, not climate-causal effects.",
            "Braun-Blanquet cover is an ordinal index, not percentage cover.",
            "Blade length and shoot density are secondary because quantitative measurement coverage is incomplete.",
            "The 2016/2017 pulse remains protocol-sensitive and is not treated as confirmed ecological collapse/recolonization.",
        ],
    }
    (outdir / "state_change_validation.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str)
    )
    pulse_protocol.to_csv(outdir / "pulse_protocol_audit.csv", index=False)
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/generated"))
    args = parser.parse_args()
    main(args.out)
