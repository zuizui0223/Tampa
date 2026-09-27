#!/usr/bin/env python3
"""Matched Tampa test of quantitative temporal memory under persistent binary presence.

Primary question:
Among same-transect consecutive years in which Thalassia is recorded in both source
and target years, does within-transect focal frequency show:
1) immediate previous-year state dependence beyond persistent site identity; and
2) additional information from older history beyond the previous year?

This is deliberately matched to the external NPS quantitative-memory analysis.
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
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 20260927
ALPHA = 1.0
MIN_TRAIN_ROWS = 80
MIN_TRAIN_TARGET_YEARS = 3
PERM_REPS = 20000


def build_rows(annual: pd.DataFrame, persistent_only: bool) -> pd.DataFrame:
    rows = []
    annual = annual.sort_values(["node_id", "year"]).copy()

    for node, g in annual.groupby("node_id"):
        g = g.sort_values("year").reset_index(drop=True)
        recs = g.to_dict("records")

        for j in range(1, len(recs)):
            src = recs[j - 1]
            tgt = recs[j]
            if int(tgt["year"]) != int(src["year"]) + 1:
                continue
            if persistent_only and not (int(src["detected"]) == 1 and int(tgt["detected"]) == 1):
                continue

            older = g[g["year"] < int(src["year"])].copy()
            if len(older) < 2:
                continue

            ox = older["year"].to_numpy(float)
            oy = older["focal_frequency"].to_numpy(float)
            xc = ox - ox.mean()
            den = float(np.dot(xc, xc))
            older_slope = 0.0 if den <= 0 else float(np.dot(xc, oy - oy.mean()) / den)

            rows.append({
                "node_id": str(node),
                "water_body": str(src["water_body"]),
                "source_year": int(src["year"]),
                "target_year": int(tgt["year"]),
                "source_frequency": float(src["focal_frequency"]),
                "older_mean_frequency": float(np.mean(oy)),
                "older_slope_frequency": older_slope,
                "older_n": int(len(older)),
                "target_frequency": float(tgt["focal_frequency"]),
                "source_detected": int(src["detected"]),
                "target_detected": int(tgt["detected"]),
            })

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["target_year", "node_id"]).reset_index(drop=True)


def pipeline(categorical: list[str], numeric: list[str]):
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", StandardScaler(), numeric),
        ],
        remainder="drop",
    )
    return make_pipeline(pre, Ridge(alpha=ALPHA))


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, categorical: list[str], numeric: list[str]) -> np.ndarray:
    p = pipeline(categorical, numeric)
    p.fit(train[categorical + numeric], train["target_frequency"])
    pred = p.predict(test[categorical + numeric])
    return np.clip(np.asarray(pred, dtype=float), 0.0, 1.0)


def walk_forward(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    categorical = ["water_body", "node_id"]
    arms = {
        "baseline": ["target_year"],
        "lag1": ["target_year", "source_frequency"],
        "long_history": [
            "target_year",
            "source_frequency",
            "older_mean_frequency",
            "older_slope_frequency",
            "older_n",
        ],
    }

    score_rows = []
    pred_rows = []
    for year in sorted(rows["target_year"].unique()):
        train = rows[rows["target_year"] < year].copy()
        test = rows[rows["target_year"] == year].copy()
        train_years = sorted(train["target_year"].unique())
        if len(train) < MIN_TRAIN_ROWS or len(train_years) < MIN_TRAIN_TARGET_YEARS or len(test) == 0:
            continue

        y = test["target_frequency"].to_numpy(float)
        rec = {
            "target_year": int(year),
            "n_train": int(len(train)),
            "n_test": int(len(test)),
            "train_target_years": int(len(train_years)),
        }

        for arm, numeric in arms.items():
            pred = fit_predict(train, test, categorical, numeric)
            rec[f"{arm}_mae"] = float(mean_absolute_error(y, pred))
            rec[f"{arm}_rmse"] = float(math.sqrt(mean_squared_error(y, pred)))
            for node, yi, pi in zip(test["node_id"], y, pred):
                pred_rows.append({
                    "target_year": int(year),
                    "node_id": str(node),
                    "arm": arm,
                    "observed_frequency": float(yi),
                    "predicted_frequency": float(pi),
                })
        score_rows.append(rec)

    return pd.DataFrame(score_rows), pd.DataFrame(pred_rows)


def paired_summary(scores: pd.DataFrame, left: str, right: str) -> dict:
    delta = scores[f"{right}_mae"] - scores[f"{left}_mae"]
    return {
        "mean_mae_left": float(scores[f"{left}_mae"].mean()),
        "mean_mae_right": float(scores[f"{right}_mae"].mean()),
        "mean_delta_right_minus_left": float(delta.mean()),
        "median_delta_right_minus_left": float(delta.median()),
        "right_wins": int((delta < 0).sum()),
        "left_wins": int((delta > 0).sum()),
        "ties": int((delta == 0).sum()),
        "target_years": int(len(delta)),
    }


def signflip(scores: pd.DataFrame, left: str, right: str, seed: int) -> dict:
    d = (scores[f"{right}_mae"] - scores[f"{left}_mae"]).to_numpy(float)
    observed = float(np.mean(d))
    rng = np.random.default_rng(seed)
    null = np.empty(PERM_REPS, dtype=float)
    for i in range(PERM_REPS):
        null[i] = float(np.mean(d * rng.choice(np.array([-1.0, 1.0]), size=len(d), replace=True)))
    p = float((1 + np.sum(null <= observed)) / (PERM_REPS + 1))
    return {
        "observed_mean_delta": observed,
        "one_sided_signflip_p": p,
        "replicates": PERM_REPS,
    }


def supported(pair: dict, test: dict) -> bool:
    if pair["target_years"] <= 0:
        return False
    need = math.ceil(0.60 * pair["target_years"])
    return bool(
        pair["right_wins"] >= need
        and pair["median_delta_right_minus_left"] < 0
        and test["one_sided_signflip_p"] < 0.05
    )


def analyze_panel(rows: pd.DataFrame, label: str, seed_offset: int) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    scores, preds = walk_forward(rows)
    if len(scores) < 8:
        raise RuntimeError(f"{label}: too few scored target years: {len(scores)}")

    b_l = paired_summary(scores, "baseline", "lag1")
    l_h = paired_summary(scores, "lag1", "long_history")
    b_h = paired_summary(scores, "baseline", "long_history")
    b_l_test = signflip(scores, "baseline", "lag1", SEED + seed_offset)
    l_h_test = signflip(scores, "lag1", "long_history", SEED + seed_offset + 1)

    result = {
        "panel": label,
        "matched_rows": int(len(rows)),
        "nodes": int(rows["node_id"].nunique()),
        "source_positive_fraction": float(rows["source_detected"].mean()),
        "target_positive_fraction": float(rows["target_detected"].mean()),
        "target_year_range": [int(rows["target_year"].min()), int(rows["target_year"].max())],
        "scored_target_years": int(len(scores)),
        "baseline_vs_lag1": b_l,
        "baseline_vs_lag1_signflip": b_l_test,
        "lag1_vs_long_history": l_h,
        "lag1_vs_long_history_signflip": l_h_test,
        "baseline_vs_long_history": b_h,
        "lag1_supported": supported(b_l, b_l_test),
        "older_history_supported_beyond_lag1": supported(l_h, l_h_test),
    }
    return result, scores, preds


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "quant_annual_panel.csv")

    required = {"node_id", "year", "water_body", "detected", "focal_frequency"}
    missing = required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing annual columns: {sorted(missing)}")

    # Bind to frozen Tampa quantitative registry.
    if len(annual) != 1480 or annual["node_id"].nunique() != 71:
        raise RuntimeError("Tampa quantitative annual panel identity drift")
    if int(annual["year"].min()) != 1997 or int(annual["year"].max()) != 2025:
        raise RuntimeError("Tampa year range drift")
    if not annual["focal_frequency"].between(0.0, 1.0).all():
        raise RuntimeError("frequency outside [0,1]")

    persistent_rows = build_rows(annual, persistent_only=True)
    all_rows = build_rows(annual, persistent_only=False)

    primary, p_scores, p_preds = analyze_panel(persistent_rows, "binary_persistent_only", 0)
    supplementary, a_scores, a_preds = analyze_panel(all_rows, "all_consecutive_states", 100)

    frozen_binary_reference = {
        "source": "results/current_validation_v2.json::memory",
        "baseline_mean_log_loss": 0.3312148,
        "lag1_mean_log_loss": 0.1700713,
        "long_history_mean_log_loss": 0.139493,
        "long_history_wins_vs_lag1": 14,
        "scored_target_years": 22,
        "note": "Different response and loss function; magnitudes are not directly comparable to quantitative-frequency MAE."
    }

    summary = {
        "schema": "tampa.matched_quantitative_memory_v1",
        "status": "posthoc_matched_state_dimension_memory_test",
        "primary": primary,
        "supplementary": supplementary,
        "model": {
            "learner": "Ridge(alpha=1.0)",
            "split": "strict walk-forward by target year",
            "categorical_baseline": ["water_body", "node_id"],
            "baseline_numeric": ["target_year"],
            "lag1_increment": ["source_frequency"],
            "long_history_increment": ["older_mean_frequency", "older_slope_frequency", "older_n"],
            "primary_metric": "target-year MAE in focal frequency; unweighted macro mean",
            "frequency_prediction_clip": [0, 1],
            "support_rule": "increment supported only when it wins >=60% of target years, median paired MAE delta is negative, and one-sided paired sign-flip p<0.05",
        },
        "frozen_binary_memory_reference": frozen_binary_reference,
        "interpretation": (
            "The primary panel conditions on Thalassia being recorded in both consecutive years, "
            "so quantitative-memory evidence cannot be attributed simply to binary loss or colonization. "
            "If lag-1 is supported but older history is not, the result is consistent with shorter memory "
            "for within-transect quantitative frequency than for Tampa's coarse recorded-state response. "
            "Because the comparison uses different response scales/models, it motivates but does not by itself "
            "prove a state-dimension-dependent biological memory horizon."
        ),
        "claim_boundary": [
            "Post-hoc matched ecological analysis.",
            "Binary and quantitative models use different response distributions and metrics; effect magnitudes are not compared directly.",
            "The primary frequency panel conditions on recorded presence in both source and target years.",
            "Node identity is present in every quantitative arm, so temporal increments are beyond persistent site differences.",
            "No environmental mechanism is inferred.",
        ],
    }

    persistent_rows.to_csv(outdir / "tampa_quant_memory_persistent_rows.csv", index=False)
    all_rows.to_csv(outdir / "tampa_quant_memory_all_rows.csv", index=False)
    p_scores.to_csv(outdir / "tampa_quant_memory_persistent_year_scores.csv", index=False)
    a_scores.to_csv(outdir / "tampa_quant_memory_all_year_scores.csv", index=False)
    p_preds.to_csv(outdir / "tampa_quant_memory_persistent_predictions.csv", index=False)
    a_preds.to_csv(outdir / "tampa_quant_memory_all_predictions.csv", index=False)
    (outdir / "tampa_matched_quantitative_memory_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/generated_tampa_quant_memory"))
    p.add_argument("--out", type=Path, default=Path("results/generated_tampa_quant_memory"))
    args = p.parse_args()
    main(args.input, args.out)
