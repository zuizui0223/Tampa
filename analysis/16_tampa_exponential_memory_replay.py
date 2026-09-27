#!/usr/bin/env python3
"""Transfer the frozen Tampa binary exponential-memory operator to quantitative states.

The original Tampa binary recorded-state analysis used an exponentially weighted
summary of all prior annual states in addition to lag-1. Its best tested decay
scale was tau=10 years. This analysis transfers that exact representation family
to two quantitative state variables under a stricter matched panel:

- source and target years both record Thalassia;
- stable node identity and water-body identity are in every model arm;
- baseline + lag1 + exponential memory are scored on identical target-year rows;
- tau=10 is the PRIMARY transfer because it is already frozen by the binary result;
- the full historical tau grid is descriptive only and cannot replace tau=10.

The purpose is to distinguish a state-dimension contrast from a representation
contrast. It is post-hoc and does not make a causal biological-memory claim.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TAUS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 50.0, 100.0]
PRIMARY_TAU = 10.0
SEED = 20260927
PERM_REPS = 20000
MIN_TRAIN_ROWS = 80
MIN_TRAIN_TARGET_YEARS = 3

METRICS = {
    "frequency": {
        "column": "focal_frequency",
        "clip": [0.0, 1.0],
        "label": "focal frequency",
    },
    "cover_index": {
        "column": "bb_cover_mean_all_points",
        "clip": None,
        "label": "Braun-Blanquet all-point index",
    },
}


def add_history_features(annual: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    for node, group in annual.groupby("node_id"):
        history: list[tuple[int, float, int]] = []
        for _, row in group.sort_values("year").iterrows():
            year = int(row["year"])
            rec = row.to_dict()

            if history and history[-1][0] == year - 1:
                rec["lag1_metric"] = float(history[-1][1])
                rec["previous_detected"] = int(history[-1][2])
            else:
                rec["lag1_metric"] = np.nan
                rec["previous_detected"] = np.nan

            for tau in TAUS:
                name = f"exp_{tau:g}"
                if history:
                    ages = np.asarray([year - old_year for old_year, _, _ in history], dtype=float)
                    weights = np.exp(-ages / tau)
                    states = np.asarray([value for _, value, _ in history], dtype=float)
                    rec[name] = float(np.average(states, weights=weights))
                else:
                    rec[name] = np.nan

            rows.append(rec)
            history.append((year, float(row[metric]), int(row["detected"])))

    return pd.DataFrame(rows)


def make_model(numeric: list[str]):
    categorical = ["water_body", "node_id"]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", StandardScaler(), numeric),
        ],
        remainder="drop",
    )
    return make_pipeline(pre, Ridge(alpha=1.0))


def predict(train: pd.DataFrame, test: pd.DataFrame, target: str, numeric: list[str], clip):
    categorical = ["water_body", "node_id"]
    model = make_model(numeric)
    model.fit(train[categorical + numeric], train[target])
    pred = np.asarray(model.predict(test[categorical + numeric]), dtype=float)
    if clip is not None:
        pred = np.clip(pred, float(clip[0]), float(clip[1]))
    return pred


def paired_signflip(delta: np.ndarray, seed: int) -> dict:
    delta = np.asarray(delta, dtype=float)
    observed = float(np.mean(delta))
    rng = np.random.default_rng(seed)
    null = np.empty(PERM_REPS, dtype=float)
    for i in range(PERM_REPS):
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=len(delta), replace=True)
        null[i] = float(np.mean(delta * signs))
    return {
        "observed_mean_delta": observed,
        "one_sided_signflip_p": float((1 + np.sum(null <= observed)) / (PERM_REPS + 1)),
        "replicates": PERM_REPS,
    }


def score_tau(frame: pd.DataFrame, target: str, clip, tau: float) -> tuple[pd.DataFrame, dict]:
    memory = f"exp_{tau:g}"
    matched = frame[
        (frame["detected"] == 1)
        & (frame["previous_detected"] == 1)
        & frame["lag1_metric"].notna()
        & frame[memory].notna()
    ].copy()

    score_rows = []
    for target_year in sorted(matched["year"].unique()):
        # Match the frozen binary direct-memory comparison: 2004 onward.
        if int(target_year) < 2004:
            continue
        train = matched[matched["year"] < target_year].copy()
        test = matched[matched["year"] == target_year].copy()
        if len(train) < MIN_TRAIN_ROWS or train["year"].nunique() < MIN_TRAIN_TARGET_YEARS:
            continue
        if len(test) == 0:
            continue

        y = test[target].to_numpy(float)
        lag = predict(train, test, target, ["year", "lag1_metric"], clip)
        aug = predict(train, test, target, ["year", "lag1_metric", memory], clip)

        score_rows.append(
            {
                "target_year": int(target_year),
                "n_test": int(len(test)),
                "lag1_mae": float(mean_absolute_error(y, lag)),
                "exponential_mae": float(mean_absolute_error(y, aug)),
            }
        )

    scores = pd.DataFrame(score_rows)
    if len(scores) != 22:
        raise RuntimeError(f"tau={tau:g}: expected 22 scored target years, got {len(scores)}")

    delta = scores["exponential_mae"] - scores["lag1_mae"]
    permutation = paired_signflip(delta.to_numpy(float), SEED + int(round(tau * 100)))
    summary = {
        "tau_years": float(tau),
        "target_years": int(len(scores)),
        "lag1_mean_mae": float(scores["lag1_mae"].mean()),
        "exponential_mean_mae": float(scores["exponential_mae"].mean()),
        "mean_exponential_minus_lag1": float(delta.mean()),
        "median_exponential_minus_lag1": float(delta.median()),
        "exponential_wins": int((delta < 0).sum()),
        "lag1_wins": int((delta > 0).sum()),
        "ties": int((delta == 0).sum()),
        "signflip": permutation,
    }
    need = math.ceil(0.60 * len(scores))
    summary["support_rule_passed"] = bool(
        summary["exponential_wins"] >= need
        and summary["median_exponential_minus_lag1"] < 0
        and permutation["one_sided_signflip_p"] < 0.05
    )
    return scores, summary


def analyze_metric(annual: pd.DataFrame, key: str, spec: dict, outdir: Path) -> dict:
    target = str(spec["column"])
    if annual[target].isna().any():
        raise RuntimeError(f"{key}: unexpected annual missingness in {target}")

    frame = add_history_features(annual, target)
    grid = []
    primary_scores = None

    for tau in TAUS:
        scores, summary = score_tau(frame, target, spec["clip"], tau)
        grid.append(summary)
        if tau == PRIMARY_TAU:
            primary_scores = scores.copy()

    grid_df = pd.DataFrame(
        [
            {
                "tau_years": row["tau_years"],
                "target_years": row["target_years"],
                "lag1_mean_mae": row["lag1_mean_mae"],
                "exponential_mean_mae": row["exponential_mean_mae"],
                "mean_exponential_minus_lag1": row["mean_exponential_minus_lag1"],
                "median_exponential_minus_lag1": row["median_exponential_minus_lag1"],
                "exponential_wins": row["exponential_wins"],
                "lag1_wins": row["lag1_wins"],
                "ties": row["ties"],
                "signflip_p": row["signflip"]["one_sided_signflip_p"],
                "support_rule_passed": row["support_rule_passed"],
            }
            for row in grid
        ]
    )

    if primary_scores is None:
        raise RuntimeError("primary tau scores missing")
    primary = next(row for row in grid if row["tau_years"] == PRIMARY_TAU)

    grid_df.to_csv(outdir / f"tampa_{key}_exponential_memory_grid.csv", index=False)
    primary_scores.to_csv(outdir / f"tampa_{key}_exponential_tau10_year_scores.csv", index=False)

    return {
        "metric": str(spec["label"]),
        "primary_tau_years": PRIMARY_TAU,
        "primary_transfer": primary,
        "descriptive_grid": {
            "tested_taus": TAUS,
            "support_rule_pass_count": int(grid_df["support_rule_passed"].sum()),
            "best_mean_mae_tau": float(
                grid_df.sort_values(["exponential_mean_mae", "tau_years"]).iloc[0]["tau_years"]
            ),
            "best_mean_mae": float(grid_df["exponential_mean_mae"].min()),
            "minimum_nominal_signflip_p": float(grid_df["signflip_p"].min()),
            "note": "The tau grid is descriptive. It cannot replace the frozen primary tau=10 transfer.",
        },
    }


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "quant_annual_panel.csv")

    required = {
        "node_id",
        "year",
        "water_body",
        "detected",
        "focal_frequency",
        "bb_cover_mean_all_points",
    }
    missing = required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing required columns: {sorted(missing)}")

    if len(annual) != 1480 or annual["node_id"].nunique() != 71:
        raise RuntimeError("Tampa annual quantitative panel identity drift")
    if int(annual["year"].min()) != 1997 or int(annual["year"].max()) != 2025:
        raise RuntimeError("Tampa temporal registry drift")

    metrics = {
        key: analyze_metric(annual, key, spec, outdir)
        for key, spec in METRICS.items()
    }

    summary = {
        "schema": "tampa.exponential_memory_operator_replay_v1",
        "status": "posthoc_representation_matched_memory_replay",
        "purpose": (
            "Transfer the exact exponential-memory representation family used by the frozen "
            "Tampa binary-state analysis to quantitative frequency and Braun-Blanquet state."
        ),
        "primary_transfer_tau_years": PRIMARY_TAU,
        "primary_tau_reason": (
            "tau=10 is the already-frozen best tested binary-state decay scale and was selected "
            "before this quantitative operator-transfer result was opened."
        ),
        "panel": {
            "condition": "Thalassia recorded in both source and target consecutive years",
            "baseline_identity": ["water_body", "node_id", "target year"],
            "target_years": [2004, 2025],
            "scored_target_year_count": 22,
        },
        "metrics": metrics,
        "cross_metric_result": {
            "tau10_supported_for_frequency": bool(
                metrics["frequency"]["primary_transfer"]["support_rule_passed"]
            ),
            "tau10_supported_for_cover_index": bool(
                metrics["cover_index"]["primary_transfer"]["support_rule_passed"]
            ),
            "any_descriptive_tau_supported_for_frequency": bool(
                metrics["frequency"]["descriptive_grid"]["support_rule_pass_count"] > 0
            ),
            "any_descriptive_tau_supported_for_cover_index": bool(
                metrics["cover_index"]["descriptive_grid"]["support_rule_pass_count"] > 0
            ),
        },
        "frozen_binary_reference": {
            "representation": "lag1 + exponentially weighted all-prior-state memory",
            "best_tested_tau_years": 10,
            "baseline_log_loss": 0.3312148,
            "lag1_log_loss": 0.1700713,
            "long_history_log_loss": 0.139493,
            "long_history_wins_vs_lag1": 14,
            "scored_target_years": 22,
        },
        "interpretation": (
            "Using the same exponential-memory representation family does not yield a supported "
            "older-history increment for either quantitative state variable. This weakens the "
            "alternative explanation that the binary-versus-quantitative contrast arose only because "
            "the previous quantitative analyses encoded history as older mean/slope rather than exponential memory."
        ),
        "claim_boundary": [
            "Post-hoc representation-matched replay.",
            "The binary tau=10 value was frozen by the earlier binary analysis; the quantitative tau grid is descriptive only.",
            "Different response distributions and learners remain, so this does not causally prove that state dimension determines memory horizon.",
            "Braun-Blanquet is an ordinal abundance index, not percent cover.",
            "No environmental mechanism is inferred.",
        ],
    }

    (outdir / "tampa_exponential_memory_operator_replay_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/generated_exp_memory"))
    parser.add_argument("--out", type=Path, default=Path("results/generated_exp_memory"))
    args = parser.parse_args()
    main(args.input, args.out)
