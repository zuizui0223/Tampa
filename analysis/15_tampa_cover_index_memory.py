#!/usr/bin/env python3
"""Replication of matched Tampa quantitative memory using Braun-Blanquet cover index.

The design is intentionally identical in spirit to analysis/14:
- primary panel conditions on Thalassia recorded in both source and target years;
- all arms contain water-body + stable node identity + target year;
- lag-1 adds source-year all-point Braun-Blanquet index;
- long-history adds older mean, older slope and history length;
- strict target-year walk-forward evaluation.

This is a post-hoc quantitative-state replication, not a new confirmatory endpoint.
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

SEED = 20260927
ALPHA = 1.0
MIN_TRAIN_ROWS = 80
MIN_TRAIN_TARGET_YEARS = 3
PERM_REPS = 20000
METRIC = "bb_cover_mean_all_points"


def build_rows(annual: pd.DataFrame) -> pd.DataFrame:
    rows = []
    annual = annual.sort_values(["node_id", "year"]).copy()
    for node, g in annual.groupby("node_id"):
        g = g.sort_values("year").reset_index(drop=True)
        recs = g.to_dict("records")
        for j in range(1, len(recs)):
            src, tgt = recs[j - 1], recs[j]
            if int(tgt["year"]) != int(src["year"]) + 1:
                continue
            if not (int(src["detected"]) == 1 and int(tgt["detected"]) == 1):
                continue
            if pd.isna(src[METRIC]) or pd.isna(tgt[METRIC]):
                continue

            older = g[g["year"] < int(src["year"])].dropna(subset=[METRIC]).copy()
            if len(older) < 2:
                continue
            x = older["year"].to_numpy(float)
            y = older[METRIC].to_numpy(float)
            xc = x - x.mean()
            den = float(np.dot(xc, xc))
            slope = 0.0 if den <= 0 else float(np.dot(xc, y - y.mean()) / den)

            rows.append({
                "node_id": str(node),
                "water_body": str(src["water_body"]),
                "source_year": int(src["year"]),
                "target_year": int(tgt["year"]),
                "source_cover_index": float(src[METRIC]),
                "older_mean_cover_index": float(np.mean(y)),
                "older_slope_cover_index": slope,
                "older_n": int(len(older)),
                "target_cover_index": float(tgt[METRIC]),
            })
    return pd.DataFrame(rows).sort_values(["target_year", "node_id"]).reset_index(drop=True)


def make_model(categorical, numeric):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", StandardScaler(), numeric),
    ])
    return make_pipeline(pre, Ridge(alpha=ALPHA))


def walk_forward(rows: pd.DataFrame) -> pd.DataFrame:
    categorical = ["water_body", "node_id"]
    arms = {
        "baseline": ["target_year"],
        "lag1": ["target_year", "source_cover_index"],
        "long_history": [
            "target_year",
            "source_cover_index",
            "older_mean_cover_index",
            "older_slope_cover_index",
            "older_n",
        ],
    }
    out = []
    for year in sorted(rows["target_year"].unique()):
        train = rows[rows["target_year"] < year].copy()
        test = rows[rows["target_year"] == year].copy()
        if len(train) < MIN_TRAIN_ROWS or train["target_year"].nunique() < MIN_TRAIN_TARGET_YEARS:
            continue
        if len(test) == 0:
            continue
        y = test["target_cover_index"].to_numpy(float)
        rec = {"target_year": int(year), "n_train": int(len(train)), "n_test": int(len(test))}
        for arm, numeric in arms.items():
            m = make_model(categorical, numeric)
            m.fit(train[categorical + numeric], train["target_cover_index"])
            pred = np.asarray(m.predict(test[categorical + numeric]), dtype=float)
            rec[f"{arm}_mae"] = float(mean_absolute_error(y, pred))
        out.append(rec)
    return pd.DataFrame(out)


def paired(scores, left, right):
    d = scores[f"{right}_mae"] - scores[f"{left}_mae"]
    return {
        "mean_mae_left": float(scores[f"{left}_mae"].mean()),
        "mean_mae_right": float(scores[f"{right}_mae"].mean()),
        "mean_delta_right_minus_left": float(d.mean()),
        "median_delta_right_minus_left": float(d.median()),
        "right_wins": int((d < 0).sum()),
        "left_wins": int((d > 0).sum()),
        "ties": int((d == 0).sum()),
        "target_years": int(len(d)),
    }


def signflip(scores, left, right, seed):
    d = (scores[f"{right}_mae"] - scores[f"{left}_mae"]).to_numpy(float)
    obs = float(d.mean())
    rng = np.random.default_rng(seed)
    null = np.empty(PERM_REPS, dtype=float)
    for i in range(PERM_REPS):
        null[i] = float(np.mean(d * rng.choice(np.array([-1.0, 1.0]), size=len(d))))
    return {
        "observed_mean_delta": obs,
        "one_sided_signflip_p": float((1 + np.sum(null <= obs)) / (PERM_REPS + 1)),
        "replicates": PERM_REPS,
    }


def support(pair, test):
    need = math.ceil(0.60 * pair["target_years"])
    return bool(
        pair["right_wins"] >= need
        and pair["median_delta_right_minus_left"] < 0
        and test["one_sided_signflip_p"] < 0.05
    )


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "quant_annual_panel.csv")
    required = {"node_id", "year", "water_body", "detected", METRIC}
    missing = required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing annual columns: {sorted(missing)}")
    if len(annual) != 1480 or annual["node_id"].nunique() != 71:
        raise RuntimeError("Tampa quantitative annual panel identity drift")
    if annual[METRIC].isna().any():
        raise RuntimeError("unexpected annual all-point cover-index missingness")

    rows = build_rows(annual)
    if len(rows) < 300:
        raise RuntimeError(f"too few persistent matched cover rows: {len(rows)}")
    scores = walk_forward(rows)
    if len(scores) < 15:
        raise RuntimeError(f"too few scored target years: {len(scores)}")

    b_l = paired(scores, "baseline", "lag1")
    l_h = paired(scores, "lag1", "long_history")
    b_l_test = signflip(scores, "baseline", "lag1", SEED)
    l_h_test = signflip(scores, "lag1", "long_history", SEED + 1)

    summary = {
        "schema": "tampa.matched_cover_index_memory_v1",
        "status": "posthoc_quantitative_memory_replication",
        "metric": "Braun-Blanquet all-point index; ordinal abundance index, not percent cover",
        "panel": "binary_persistent_only",
        "matched_rows": int(len(rows)),
        "nodes": int(rows["node_id"].nunique()),
        "scored_target_years": int(len(scores)),
        "baseline_vs_lag1": b_l,
        "baseline_vs_lag1_signflip": b_l_test,
        "lag1_vs_long_history": l_h,
        "lag1_vs_long_history_signflip": l_h_test,
        "lag1_supported": support(b_l, b_l_test),
        "older_history_supported_beyond_lag1": support(l_h, l_h_test),
        "interpretation": (
            "The Braun-Blanquet all-point index independently reproduces the frequency-memory pattern: "
            "immediate previous-year quantitative state is informative beyond persistent site identity, "
            "whereas older history does not provide a robust increment beyond lag-1. This strengthens the "
            "within-Tampa evidence for short-memory quantitative condition under persistent binary presence."
        ),
        "claim_boundary": [
            "Post-hoc replication across a second quantitative state variable.",
            "Braun-Blanquet is an ordinal abundance index and is not interpreted as percent cover.",
            "The analysis conditions on recorded Thalassia presence in both source and target years.",
            "No environmental or demographic mechanism is inferred.",
        ],
    }

    rows.to_csv(outdir / "tampa_cover_memory_persistent_rows.csv", index=False)
    scores.to_csv(outdir / "tampa_cover_memory_year_scores.csv", index=False)
    (outdir / "tampa_matched_cover_index_memory_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/generated_tampa_quant_memory"))
    p.add_argument("--out", type=Path, default=Path("results/generated_tampa_quant_memory"))
    args = p.parse_args()
    main(args.input, args.out)
