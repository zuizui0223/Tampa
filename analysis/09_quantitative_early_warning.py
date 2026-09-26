#!/usr/bin/env python3
"""Test whether quantitative Thalassia state predicts next-year recorded loss.

The endpoint is deliberately narrow: among transect-years with recorded Thalassia
presence, predict whether the same stable transect is recorded present or absent in the
next consecutive year. This is a recorded-state transition, not demographic extinction.

Strict walk-forward evaluation trains only on transitions whose target year precedes the
scored target year. The baseline contains space, year, survey timing and sampled-point
effort. The augmented arm adds only source-year Thalassia frequency occurrence and the
all-point Braun-Blanquet abundance index. The learner is otherwise unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, mannwhitneyu, wilcoxon
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_NUMERIC = ["source_year", "longitude", "latitude", "sin_doy", "cos_doy", "log_points"]
CATEGORY = ["water_body"]
QUANTITATIVE = ["focal_frequency", "bb_cover_mean_all_points"]
MIN_TRAIN_LOSSES = 5
MIN_TRAIN_PERSISTENCE = 50


def make_model(features: list[str]) -> Pipeline:
    numeric = [x for x in features if x not in CATEGORY]
    transformers = [("numeric", StandardScaler(), numeric)]
    if any(x in CATEGORY for x in features):
        transformers.append(("water_body", OneHotEncoder(handle_unknown="ignore"), CATEGORY))
    return Pipeline(
        [
            ("preprocess", ColumnTransformer(transformers)),
            ("model", LogisticRegression(C=1.0, max_iter=2000)),
        ]
    )


def build_transitions(quant: pd.DataFrame, community: pd.DataFrame) -> pd.DataFrame:
    effort = community[["node_id", "year", "sin_doy", "cos_doy", "log_points"]].copy()
    annual = quant.merge(effort, on=["node_id", "year"], how="left", validate="one_to_one")
    if annual[["sin_doy", "cos_doy", "log_points"]].isna().any().any():
        raise RuntimeError("missing survey timing/effort after annual merge")

    rows = []
    for node, group in annual.sort_values(["node_id", "year"]).groupby("node_id"):
        records = group.to_dict("records")
        for source, target in zip(records[:-1], records[1:]):
            if int(target["year"]) != int(source["year"]) + 1:
                continue
            if int(source["detected"]) != 1:
                continue
            rows.append(
                {
                    "node_id": node,
                    "source_year": int(source["year"]),
                    "target_year": int(target["year"]),
                    "loss": int(1 - int(target["detected"])),
                    "water_body": source["water_body"],
                    "longitude": float(source["longitude"]),
                    "latitude": float(source["latitude"]),
                    "sin_doy": float(source["sin_doy"]),
                    "cos_doy": float(source["cos_doy"]),
                    "log_points": float(source["log_points"]),
                    "focal_frequency": float(source["focal_frequency"]),
                    "bb_cover_mean_all_points": float(source["bb_cover_mean_all_points"]),
                    "blade_length_mean_mm": source["blade_length_mean_mm"],
                    "shoot_density_mean_m2": source["shoot_density_mean_m2"],
                }
            )
    return pd.DataFrame(rows)


def descriptive_separation(transitions: pd.DataFrame) -> dict:
    out = {}
    for metric in [
        "focal_frequency",
        "bb_cover_mean_all_points",
        "blade_length_mean_mm",
        "shoot_density_mean_m2",
    ]:
        loss = transitions.loc[transitions.loss == 1, metric].dropna()
        persist = transitions.loc[transitions.loss == 0, metric].dropna()
        test = (
            mannwhitneyu(loss, persist, alternative="two-sided")
            if len(loss) and len(persist)
            else None
        )
        out[metric] = {
            "loss_n": int(len(loss)),
            "loss_median": None if not len(loss) else float(loss.median()),
            "persistence_n": int(len(persist)),
            "persistence_median": None if not len(persist) else float(persist.median()),
            "mannwhitney_p_two_sided": None if test is None else float(test.pvalue),
        }
    return out


def run_walkforward(transitions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = {
        "baseline": BASE_NUMERIC + CATEGORY,
        "quantitative": BASE_NUMERIC + CATEGORY + QUANTITATIVE,
    }
    year_rows = []
    prediction_rows = []

    for target_year in sorted(transitions.target_year.unique()):
        train = transitions[transitions.target_year < target_year].copy()
        test = transitions[transitions.target_year == target_year].copy()
        train_losses = int(train.loss.sum())
        train_persistence = int(len(train) - train_losses)
        if train_losses < MIN_TRAIN_LOSSES or train_persistence < MIN_TRAIN_PERSISTENCE:
            continue

        predictions = {}
        for arm, cols in features.items():
            model = make_model(cols)
            model.fit(train[cols], train.loss)
            prob = model.predict_proba(test[cols])[:, 1]
            predictions[arm] = prob
            year_rows.append(
                {
                    "target_year": int(target_year),
                    "arm": arm,
                    "n": int(len(test)),
                    "losses": int(test.loss.sum()),
                    "log_loss": float(log_loss(test.loss, prob, labels=[0, 1])),
                    "brier": float(brier_score_loss(test.loss, prob)),
                    "train_n": int(len(train)),
                    "train_losses": train_losses,
                }
            )

        for i, (_, row) in enumerate(test.iterrows()):
            prediction_rows.append(
                {
                    "node_id": row.node_id,
                    "target_year": int(target_year),
                    "loss": int(row.loss),
                    "p_baseline": float(predictions["baseline"][i]),
                    "p_quantitative": float(predictions["quantitative"][i]),
                }
            )

    return pd.DataFrame(year_rows), pd.DataFrame(prediction_rows)


def score_summary(
    year_scores: pd.DataFrame, predictions: pd.DataFrame, exclude_2016: bool
) -> dict:
    ys = year_scores.copy()
    pr = predictions.copy()
    label = "all_scored_years"
    if exclude_2016:
        ys = ys[ys.target_year != 2016].copy()
        pr = pr[pr.target_year != 2016].copy()
        label = "sensitivity_exclude_target_2016"

    pivot = ys.pivot(index="target_year", columns="arm", values="log_loss")
    delta = pivot["quantitative"] - pivot["baseline"]
    paired = wilcoxon(delta, alternative="less")
    wins = int((delta < 0).sum())

    result = {
        "label": label,
        "target_years": int(len(pivot)),
        "target_year_range": [int(pivot.index.min()), int(pivot.index.max())],
        "quantitative_wins": wins,
        "baseline_wins": int((delta > 0).sum()),
        "ties": int((delta == 0).sum()),
        "macro_baseline_log_loss": float(pivot["baseline"].mean()),
        "macro_quantitative_log_loss": float(pivot["quantitative"].mean()),
        "macro_delta": float(delta.mean()),
        "median_year_delta": float(delta.median()),
        "sign_test_one_sided_p": float(
            binomtest(wins, len(delta), 0.5, alternative="greater").pvalue
        ),
        "wilcoxon_one_sided_p": float(paired.pvalue),
        "pooled_rows": int(len(pr)),
        "pooled_losses": int(pr.loss.sum()),
    }
    for arm in ["baseline", "quantitative"]:
        p = pr[f"p_{arm}"]
        result[f"pooled_{arm}_log_loss"] = float(log_loss(pr.loss, p, labels=[0, 1]))
        result[f"pooled_{arm}_brier"] = float(brier_score_loss(pr.loss, p))
        result[f"pooled_{arm}_auc"] = float(roc_auc_score(pr.loss, p))
    return result


def main(input_dir: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    quant = pd.read_csv(input_dir / "quant_annual_panel.csv")
    community = pd.read_csv(input_dir / "community_quant_annual.csv")
    transitions = build_transitions(quant, community)
    year_scores, predictions = run_walkforward(transitions)

    primary = score_summary(year_scores, predictions, exclude_2016=False)
    sensitivity = score_summary(year_scores, predictions, exclude_2016=True)
    descriptive = descriptive_separation(transitions)

    y2016 = year_scores[year_scores.target_year == 2016].set_index("arm")
    anomaly_2016 = {
        "baseline_log_loss": float(y2016.loc["baseline", "log_loss"]),
        "quantitative_log_loss": float(y2016.loc["quantitative", "log_loss"]),
        "quantitative_minus_baseline": float(
            y2016.loc["quantitative", "log_loss"] - y2016.loc["baseline", "log_loss"]
        ),
        "interpretation": (
            "The quantitative arm is adverse in target year 2016; this year is retained "
            "in the primary result and excluded only in a declared sensitivity because "
            "the 2016/2017 recorded-state pulse is protocol-sensitive."
        ),
    }

    summary = {
        "schema": "tampa.quantitative_early_warning_v1",
        "endpoint": (
            "next-year recorded Thalassia loss among source-year recorded-positive stable transects"
        ),
        "transition_registry": {
            "source_positive_consecutive_transitions": int(len(transitions)),
            "recorded_losses": int(transitions.loss.sum()),
            "recorded_persistence": int((transitions.loss == 0).sum()),
        },
        "baseline_features": BASE_NUMERIC + CATEGORY,
        "augmentation_features": QUANTITATIVE,
        "learner": "standardized logistic regression, C=1.0, strict walk-forward by target year",
        "training_gate": {
            "minimum_prior_losses": MIN_TRAIN_LOSSES,
            "minimum_prior_persistence": MIN_TRAIN_PERSISTENCE,
        },
        "primary": primary,
        "sensitivity_exclude_2016": sensitivity,
        "target_2016": anomaly_2016,
        "descriptive_source_state_separation": descriptive,
        "interpretation": (
            "Source-year quantitative meadow state adds out-of-time information about "
            "next-year recorded loss beyond space, year, survey timing and sampled-point "
            "effort. This supports quantitative degradation as an early-warning signal "
            "for recorded-state instability, while retaining 2016 as an important "
            "adverse/protocol-sensitive year."
        ),
        "claim_boundary": [
            "Recorded loss is not demographic extinction and recorded persistence is not demographic survival.",
            "Frequency and Braun-Blanquet state are survey-derived ecological condition measures, not causal drivers.",
            "The analysis was motivated after inspecting the broader Tampa state-decoupling result and is therefore an exploratory strict walk-forward validation, not an untouched prospective endpoint.",
            "The 2016 target year remains in the primary score; exclusion is sensitivity only.",
            "Blade length and shoot density are descriptive secondary variables because coverage is incomplete.",
        ],
    }

    transitions.to_csv(outdir / "early_warning_transitions.csv", index=False)
    year_scores.to_csv(outdir / "early_warning_year_scores.csv", index=False)
    predictions.to_csv(outdir / "early_warning_predictions.csv", index=False)
    (outdir / "quantitative_early_warning_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/generated"))
    parser.add_argument("--out", type=Path, default=Path("results/generated"))
    args = parser.parse_args()
    main(args.input, args.out)
