#!/usr/bin/env python3
"""Known-truth test of threshold-induced apparent ecological memory.

The latent ecological state is first-order Markov by construction. Quantitative
frequency and binary detection are then derived from the SAME Binomial point
sample. Both observed-state prediction tasks use the SAME learner (Ridge), loss
(MSE/Brier), train/test years, site identity, and transferred exponential tau=10.

Primary question:
Does older observed history improve the thresholded binary state more than the
quantitative frequency state, even though the underlying ecological process has
no state dependence beyond t-1?
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "results/threshold_induced_memory_known_truth_v1_contract.json").read_text()
)

SITES = int(CONTRACT["simulation_grid"]["sites"])
YEARS = int(CONTRACT["simulation_grid"]["years"])
REPS = int(CONTRACT["simulation_grid"]["replicates_per_cell"])
PHIS = [float(x) for x in CONTRACT["simulation_grid"]["phi"]]
MEANS = [float(x) for x in CONTRACT["simulation_grid"]["mean_logit"]]
LATENT_SDS = [float(x) for x in CONTRACT["simulation_grid"]["latent_stationary_sd"]]
POINT_COUNTS = [int(x) for x in CONTRACT["simulation_grid"]["point_count"]]
SITE_SD = float(CONTRACT["simulation_grid"]["site_intercept_sd"])
MASTER_SEED = int(CONTRACT["simulation_grid"]["random_seed"])
TAU = float(CONTRACT["prediction_design"]["exponential_tau_years"])
ALPHA = 1.0
TRAIN_START, TRAIN_END = [int(x) for x in CONTRACT["prediction_design"]["train_target_years"]]
TEST_START, TEST_END = [int(x) for x in CONTRACT["prediction_design"]["test_target_years"]]


def logistic(x: np.ndarray) -> np.ndarray:
    out = np.empty_like(x, dtype=float)
    pos = x >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-x[pos]))
    expx = np.exp(x[~pos])
    out[~pos] = expx / (1.0 + expx)
    return out


def simulate_observations(
    rng: np.random.Generator,
    phi: float,
    mean_logit: float,
    latent_sd: float,
    point_count: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = mean_logit + rng.normal(0.0, SITE_SD, size=SITES)
    z = np.empty((SITES, YEARS), dtype=float)
    z[:, 0] = mu + rng.normal(0.0, latent_sd, size=SITES)
    innovation_sd = latent_sd * math.sqrt(max(0.0, 1.0 - phi * phi))
    for t in range(1, YEARS):
        z[:, t] = mu + phi * (z[:, t - 1] - mu) + rng.normal(
            0.0, innovation_sd, size=SITES
        )

    p = logistic(z)
    k = rng.binomial(point_count, p)
    frequency = k.astype(float) / float(point_count)
    binary = (k > 0).astype(float)
    return p, frequency, binary


def exponential_history(obs: np.ndarray, tau: float) -> np.ndarray:
    sites, years = obs.shape
    out = np.full((sites, years), np.nan, dtype=float)
    for t in range(1, years):
        ages = np.arange(t, 0, -1, dtype=float)
        weights = np.exp(-ages / tau)
        weights /= weights.sum()
        out[:, t] = obs[:, :t] @ weights
    return out


def design_rows(obs: np.ndarray) -> dict[str, np.ndarray]:
    hist = exponential_history(obs, TAU)
    rows = {
        "site": [],
        "year": [],
        "target": [],
        "lag1": [],
        "history": [],
    }
    for t in range(2, YEARS):
        for i in range(SITES):
            rows["site"].append(i)
            rows["year"].append(t)
            rows["target"].append(float(obs[i, t]))
            rows["lag1"].append(float(obs[i, t - 1]))
            rows["history"].append(float(hist[i, t]))
    return {k: np.asarray(v) for k, v in rows.items()}


def fixed_site_matrix(site: np.ndarray) -> np.ndarray:
    x = np.zeros((len(site), SITES - 1), dtype=float)
    mask = site > 0
    row = np.nonzero(mask)[0]
    col = site[mask].astype(int) - 1
    x[row, col] = 1.0
    return x


def matrices(rows: dict[str, np.ndarray], train_mask: np.ndarray, use_history: bool):
    site_x = fixed_site_matrix(rows["site"])
    year = rows["year"].astype(float)
    mean_year = float(year[train_mask].mean())
    sd_year = float(year[train_mask].std(ddof=0))
    if sd_year <= 0:
        raise RuntimeError("nonpositive training year SD")
    year_z = ((year - mean_year) / sd_year)[:, None]

    numeric = [year_z, rows["lag1"][:, None]]
    if use_history:
        numeric.append(rows["history"][:, None])
    return np.hstack([site_x] + numeric)


def fit_score(rows: dict[str, np.ndarray], use_history: bool) -> float:
    year = rows["year"].astype(int)
    train = (year >= TRAIN_START) & (year <= TRAIN_END)
    test = (year >= TEST_START) & (year <= TEST_END)
    if train.sum() == 0 or test.sum() == 0:
        raise RuntimeError("empty train/test partition")

    x = matrices(rows, train, use_history)
    y = rows["target"].astype(float)

    model = Ridge(alpha=ALPHA)
    model.fit(x[train], y[train])
    pred = np.clip(model.predict(x[test]), 0.0, 1.0)
    return float(mean_squared_error(y[test], pred))


def score_state(obs: np.ndarray) -> dict:
    rows = design_rows(obs)
    lag = fit_score(rows, use_history=False)
    long = fit_score(rows, use_history=True)
    absolute = long - lag
    relative_gain = (lag - long) / lag if lag > 0 else 0.0
    return {
        "lag1_mse": lag,
        "long_history_mse": long,
        "long_minus_lag1": absolute,
        "relative_gain": relative_gain,
    }


def cell_key(phi: float, mean_logit: float, latent_sd: float, point_count: int) -> str:
    return (
        f"phi={phi:g}|mean={mean_logit:g}|sd={latent_sd:g}|"
        f"points={point_count}"
    )


def main(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)

    replicate_rows = []
    cell_index = 0
    for phi in PHIS:
        for mean_logit in MEANS:
            for latent_sd in LATENT_SDS:
                for point_count in POINT_COUNTS:
                    key = cell_key(phi, mean_logit, latent_sd, point_count)
                    for rep in range(REPS):
                        seed = MASTER_SEED + cell_index * 10000 + rep
                        rng = np.random.default_rng(seed)
                        p, frequency, binary = simulate_observations(
                            rng, phi, mean_logit, latent_sd, point_count
                        )
                        f = score_state(frequency)
                        b = score_state(binary)
                        amplification = b["relative_gain"] - f["relative_gain"]
                        replicate_rows.append(
                            {
                                "cell": key,
                                "cell_index": cell_index,
                                "replicate": rep,
                                "seed": seed,
                                "phi": phi,
                                "mean_logit": mean_logit,
                                "latent_sd": latent_sd,
                                "point_count": point_count,
                                "latent_probability_mean": float(p.mean()),
                                "frequency_mean": float(frequency.mean()),
                                "binary_prevalence": float(binary.mean()),
                                "frequency_lag1_mse": f["lag1_mse"],
                                "frequency_long_history_mse": f["long_history_mse"],
                                "frequency_relative_gain": f["relative_gain"],
                                "binary_lag1_mse": b["lag1_mse"],
                                "binary_long_history_mse": b["long_history_mse"],
                                "binary_relative_gain": b["relative_gain"],
                                "thresholding_amplification": amplification,
                            }
                        )
                    cell_index += 1

    rep = pd.DataFrame(replicate_rows)
    if len(rep) != 24 * REPS:
        raise RuntimeError(f"unexpected replicate count: {len(rep)}")

    cells = (
        rep.groupby(
            ["cell", "cell_index", "phi", "mean_logit", "latent_sd", "point_count"],
            as_index=False,
        )
        .agg(
            replicates=("replicate", "size"),
            mean_binary_prevalence=("binary_prevalence", "mean"),
            mean_frequency=("frequency_mean", "mean"),
            median_frequency_relative_gain=("frequency_relative_gain", "median"),
            median_binary_relative_gain=("binary_relative_gain", "median"),
            median_amplification=("thresholding_amplification", "median"),
            positive_amplification_fraction=(
                "thresholding_amplification",
                lambda x: float((x > 0).mean()),
            ),
            binary_history_gain_fraction=(
                "binary_relative_gain",
                lambda x: float((x > 0).mean()),
            ),
            frequency_history_gain_fraction=(
                "frequency_relative_gain",
                lambda x: float((x > 0).mean()),
            ),
        )
    )

    cells["cell_support"] = (
        (cells["median_amplification"] > 0)
        & (cells["positive_amplification_fraction"] >= 0.65)
    )

    phi_summary = (
        cells.groupby("phi", as_index=False)
        .agg(
            cells=("cell", "size"),
            supporting_cells=("cell_support", "sum"),
            median_cell_amplification=("median_amplification", "median"),
        )
    )
    phi_summary["phi_level_robust"] = phi_summary["supporting_cells"] >= 6

    supporting_cells = int(cells["cell_support"].sum())
    global_positive_fraction = float((rep["thresholding_amplification"] > 0).mean())
    robust_phi_levels = int(phi_summary["phi_level_robust"].sum())

    rule = CONTRACT["global_support_rule"]
    passed = bool(
        supporting_cells >= int(rule["minimum_supporting_cells"])
        and global_positive_fraction
        >= float(rule["minimum_global_positive_replicate_fraction"])
        and robust_phi_levels >= 2
    )

    summary = {
        "schema": "tampa.threshold_induced_memory_known_truth_v1.result",
        "status": "mechanism_supported" if passed else "mechanism_not_supported",
        "known_truth": {
            "latent_markov_order": 1,
            "binary_and_frequency_share_same_binomial_count": True,
            "learner_same_both_states": "Ridge(alpha=1.0)",
            "loss_same_both_states": "MSE on [0,1]",
            "exponential_tau_years": TAU,
        },
        "design": {
            "cells": int(len(cells)),
            "replicates_per_cell": REPS,
            "total_replicates": int(len(rep)),
            "sites": SITES,
            "years": YEARS,
            "phi": PHIS,
            "mean_logit": MEANS,
            "latent_stationary_sd": LATENT_SDS,
            "point_count": POINT_COUNTS,
        },
        "primary": {
            "supporting_cells": supporting_cells,
            "required_supporting_cells": int(rule["minimum_supporting_cells"]),
            "global_positive_amplification_fraction": global_positive_fraction,
            "required_global_positive_fraction": float(
                rule["minimum_global_positive_replicate_fraction"]
            ),
            "robust_phi_levels": robust_phi_levels,
            "required_robust_phi_levels": 2,
            "global_median_amplification": float(
                rep["thresholding_amplification"].median()
            ),
            "global_median_binary_relative_gain": float(
                rep["binary_relative_gain"].median()
            ),
            "global_median_frequency_relative_gain": float(
                rep["frequency_relative_gain"].median()
            ),
            "support_rule_passed": passed,
        },
        "by_phi": phi_summary.to_dict("records"),
        "interpretation": (
            "If supported, lossy thresholding is sufficient to make older observed history "
            "more predictively valuable for a binary detection state than for the quantitative "
            "frequency from which it was derived, even though the latent ecological process is "
            "strictly first-order Markov. This would make apparent long memory in coarse state "
            "an observation/aggregation mechanism that must be separated from biological memory."
            if passed
            else
            "The frozen known-truth design did not show robust thresholding amplification. "
            "This weakens a coarse-graining-only explanation for the Tampa state-dimension contrast."
        ),
        "claim_boundary": CONTRACT["interpretation_boundary"],
    }

    rep.to_csv(outdir / "threshold_memory_replicates.csv", index=False)
    cells.to_csv(outdir / "threshold_memory_cells.csv", index=False)
    phi_summary.to_csv(outdir / "threshold_memory_phi_summary.csv", index=False)
    (outdir / "threshold_induced_memory_known_truth_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/generated_threshold_memory"))
    args = parser.parse_args()
    main(args.out)
