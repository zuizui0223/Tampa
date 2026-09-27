#!/usr/bin/env python3
"""Post-hoc external test of quantitative temporal memory in the NPS Tier-3 Zostera panel.

This analysis asks whether next-year quantitative eelgrass cover is better predicted by:
1) space/time identity alone,
2) + immediately previous-year cover,
3) + older within-transect cover history beyond the previous year.

It is an ecological replication of Tampa's temporal-memory idea, not a prospective
external validation of the Tampa recorded-loss early-warning endpoint.
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
MIN_TRAIN_ROWS = 30
MIN_TRAIN_TARGET_YEARS = 3
ALPHA = 1.0


def build_rows(annual: pd.DataFrame) -> pd.DataFrame:
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

            older = g[g["year"] < int(src["year"])].copy()
            # Matched analysis requires at least two older observations so that
            # a genuine pre-lag history and trend exist for every scored row.
            if len(older) < 2:
                continue

            ox = older["year"].to_numpy(float)
            oy = older["focal_mean_cover"].to_numpy(float)
            xc = ox - ox.mean()
            den = float(np.dot(xc, xc))
            older_slope = 0.0 if den <= 0 else float(np.dot(xc, oy - oy.mean()) / den)

            rows.append({
                "node_id": str(node),
                "Location": str(src["Location"]),
                "source_year": int(src["year"]),
                "target_year": int(tgt["year"]),
                "source_cover": float(src["focal_mean_cover"]),
                "older_mean_cover": float(np.mean(oy)),
                "older_slope_cover": older_slope,
                "older_n": int(len(older)),
                "target_cover": float(tgt["focal_mean_cover"]),
            })
    return pd.DataFrame(rows).sort_values(["target_year", "node_id"]).reset_index(drop=True)


def model(categorical, numeric):
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", StandardScaler(), numeric),
        ],
        remainder="drop",
    )
    return make_pipeline(pre, Ridge(alpha=ALPHA))


def fit_predict(train, test, categorical, numeric):
    pipe = model(categorical, numeric)
    pipe.fit(train[categorical + numeric], train["target_cover"])
    pred = pipe.predict(test[categorical + numeric])
    return np.clip(np.asarray(pred, dtype=float), 0.0, 100.0)


def score(y, p):
    return {
        "mae": float(mean_absolute_error(y, p)),
        "rmse": float(math.sqrt(mean_squared_error(y, p))),
    }


def walk_forward(rows: pd.DataFrame):
    categorical = ["Location", "node_id"]
    arms = {
        "baseline": ["target_year"],
        "lag1": ["target_year", "source_cover"],
        "long_history": [
            "target_year",
            "source_cover",
            "older_mean_cover",
            "older_slope_cover",
            "older_n",
        ],
    }

    years = sorted(rows["target_year"].unique())
    per_year = []
    predictions = []
    for year in years:
        train = rows[rows["target_year"] < year].copy()
        test = rows[rows["target_year"] == year].copy()
        train_years = sorted(train["target_year"].unique())
        if len(train) < MIN_TRAIN_ROWS or len(train_years) < MIN_TRAIN_TARGET_YEARS or len(test) == 0:
            continue

        y = test["target_cover"].to_numpy(float)
        rec = {"target_year": int(year), "n_test": int(len(test))}
        for arm, numeric in arms.items():
            p = fit_predict(train, test, categorical, numeric)
            s = score(y, p)
            rec[f"{arm}_mae"] = s["mae"]
            rec[f"{arm}_rmse"] = s["rmse"]
            for node, yi, pi in zip(test["node_id"], y, p):
                predictions.append({
                    "target_year": int(year),
                    "node_id": str(node),
                    "arm": arm,
                    "observed_cover": float(yi),
                    "predicted_cover": float(pi),
                })
        per_year.append(rec)
    return pd.DataFrame(per_year), pd.DataFrame(predictions)


def paired_summary(per_year: pd.DataFrame, left: str, right: str):
    # right-minus-left: negative means right is better.
    delta = per_year[f"{right}_mae"] - per_year[f"{left}_mae"]
    return {
        "mean_mae_left": float(per_year[f"{left}_mae"].mean()),
        "mean_mae_right": float(per_year[f"{right}_mae"].mean()),
        "mean_delta_right_minus_left": float(delta.mean()),
        "median_delta_right_minus_left": float(delta.median()),
        "right_wins": int((delta < 0).sum()),
        "left_wins": int((delta > 0).sum()),
        "ties": int((delta == 0).sum()),
        "target_years": int(len(delta)),
    }


def permutation_test_yearwise(per_year: pd.DataFrame, left: str, right: str, seed: int = SEED, reps: int = 20000):
    # Paired sign-flip permutation on year-level MAE differences.
    d = (per_year[f"{right}_mae"] - per_year[f"{left}_mae"]).to_numpy(float)
    obs = float(np.mean(d))
    rng = np.random.default_rng(seed)
    vals = np.empty(reps, dtype=float)
    for i in range(reps):
        signs = rng.choice(np.array([-1.0, 1.0]), size=len(d), replace=True)
        vals[i] = float(np.mean(d * signs))
    # one-sided: improvement means observed mean < 0.
    p = float((1 + np.sum(vals <= obs)) / (reps + 1))
    return {"observed_mean_delta": obs, "one_sided_signflip_p": p, "replicates": reps}


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "nps_tier3_annual_state.csv")
    required = {"node_id", "Location", "year", "focal_mean_cover", "recorded_presence"}
    missing = required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing columns: {sorted(missing)}")

    # Bind to the already-frozen NPS state-decoupling panel.
    if len(annual) != 240 or annual["node_id"].nunique() != 18:
        raise RuntimeError("NPS annual panel identity drift")
    if not annual["recorded_presence"].astype(bool).all():
        raise RuntimeError("NPS binary-presence saturation no longer reproduces")

    rows = build_rows(annual)
    if len(rows) < 100:
        raise RuntimeError(f"too few matched memory rows: {len(rows)}")

    per_year, preds = walk_forward(rows)
    if len(per_year) < 8:
        raise RuntimeError(f"too few scored target years: {len(per_year)}")

    baseline_vs_lag1 = paired_summary(per_year, "baseline", "lag1")
    lag1_vs_history = paired_summary(per_year, "lag1", "long_history")
    baseline_vs_history = paired_summary(per_year, "baseline", "long_history")

    summary = {
        "schema": "tampa.nps_quantitative_memory_v1",
        "status": "posthoc_external_quantitative_memory_test",
        "source_result": "results/nps_persistent_cover_v1.json",
        "analysis_unit": "same-transect consecutive target year with at least two observations older than the source year",
        "matched_rows": int(len(rows)),
        "nodes": int(rows["node_id"].nunique()),
        "target_year_range": [int(rows["target_year"].min()), int(rows["target_year"].max())],
        "model": {
            "learner": "Ridge(alpha=1.0)",
            "split": "strict walk-forward by target year",
            "categorical_baseline": ["Location", "node_id"],
            "baseline_numeric": ["target_year"],
            "lag1_increment": ["source_cover"],
            "long_history_increment": ["older_mean_cover", "older_slope_cover", "older_n"],
            "primary_metric": "target-year MAE; unweighted macro mean across target years",
            "prediction_clip": [0, 100],
        },
        "scored_target_years": int(len(per_year)),
        "baseline_vs_lag1": baseline_vs_lag1,
        "lag1_vs_long_history": lag1_vs_history,
        "baseline_vs_long_history": baseline_vs_history,
        "lag1_vs_long_history_signflip": permutation_test_yearwise(per_year, "lag1", "long_history"),
        "interpretation": (
            "This post-hoc external test asks whether quantitative seagrass state has temporal memory. "
            "Lag-1 improvement supports immediate state dependence. Additional improvement from older history, "
            "if observed, supports path dependence beyond the immediately previous year. It does not estimate "
            "a universal biological memory constant and is not a prospective test of recorded-loss early warning."
        ),
        "claim_boundary": [
            "Post-hoc external ecological replication because NPS response data were previously opened.",
            "Continuous cover prediction is a different endpoint from Tampa recorded-loss early warning.",
            "Node identity is included in every arm, so memory increments are evaluated beyond persistent site differences.",
            "No environmental cause is inferred.",
            "The fixed long-history feature set is not tuned on held-out target years.",
        ],
    }

    rows.to_csv(outdir / "nps_quantitative_memory_rows.csv", index=False)
    per_year.to_csv(outdir / "nps_quantitative_memory_year_scores.csv", index=False)
    preds.to_csv(outdir / "nps_quantitative_memory_predictions.csv", index=False)
    (outdir / "nps_quantitative_memory_v1.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/generated_nps_memory"))
    p.add_argument("--out", type=Path, default=Path("results/generated_nps_memory"))
    args = p.parse_args()
    main(args.input, args.out)
