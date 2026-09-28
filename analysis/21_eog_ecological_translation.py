#!/usr/bin/env python3
"""Post-hoc ecological translation of the frozen Tampa EOG failure.

This analysis asks two descriptive/predictive questions using the Tampa annual panel:

1. How much of each seagrass state dimension is structured by stable transect identity
   versus year?
2. Does a response-aligned, annually refreshed neighborhood state add out-of-time
   information beyond stable node identity and the focal transect's own lag-1 state?

The neighborhood radii are transferred unchanged from the frozen Tampa EOG world family.
This is a post-hoc ecological audit. It does not repair or reclassify the consumed EOG
endpoint and does not identify a causal dispersal mechanism.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import log_loss, mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

EOG_RADII_KM = [
    14.910552760894076,
    23.92945001793242,
    34.70605518869811,
    43.48070387866193,
]
TARGET_YEARS = list(range(2004, 2026))
SEED = 20260928
PERM_REPS = 100000

STATE_VARS = [
    "detected",
    "focal_frequency",
    "bb_cover_mean_all_points",
    "blade_length_mean_mm",
    "shoot_density_mean_m2",
]


def group_mean_r2(data: pd.DataFrame, ycol: str, groups: list[str]) -> float:
    d = data.dropna(subset=[ycol, *groups]).copy()
    y = d[ycol].to_numpy(float)
    fit = d.groupby(groups, observed=False)[ycol].transform("mean").to_numpy(float)
    sst = float(np.sum((y - y.mean()) ** 2))
    return float(1.0 - np.sum((y - fit) ** 2) / sst) if sst > 0 else 0.0


def additive_node_year_r2(data: pd.DataFrame, ycol: str) -> float:
    d = data.dropna(subset=[ycol, "node_id", "year"]).copy()
    X = pd.get_dummies(
        d[["node_id", "year"]].astype({"node_id": str, "year": str}),
        drop_first=True,
        dtype=float,
    )
    model = LinearRegression().fit(X, d[ycol].astype(float))
    return float(model.score(X, d[ycol].astype(float)))


def haversine_matrix(nodes: pd.DataFrame) -> np.ndarray:
    lat = np.radians(nodes["latitude"].to_numpy(float))
    lon = np.radians(nodes["longitude"].to_numpy(float))
    dlat = lat[None, :] - lat[:, None]
    dlon = lon[None, :] - lon[:, None]
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2.0) ** 2
    out = 6371.0 * 2.0 * np.arcsin(np.sqrt(a))
    np.fill_diagonal(out, np.nan)
    return out


def build_lagged_neighborhood_panel(annual: pd.DataFrame) -> pd.DataFrame:
    nodes = (
        annual[["node_id", "longitude", "latitude"]]
        .drop_duplicates("node_id")
        .sort_values("node_id")
        .reset_index(drop=True)
    )
    ids = nodes["node_id"].tolist()
    idx = {node: i for i, node in enumerate(ids)}
    dist = haversine_matrix(nodes)
    panel = annual.set_index(["year", "node_id"]).sort_index()

    rows: list[dict] = []
    for _, row in annual.iterrows():
        year = int(row["year"])
        node = row["node_id"]
        prev = year - 1
        if (prev, node) not in panel.index:
            continue
        rec = row.to_dict()
        prow = panel.loc[(prev, node)]
        rec["lag_detected"] = float(prow["detected"])
        rec["lag_frequency"] = float(prow["focal_frequency"])
        i = idx[node]

        for radius in EOG_RADII_KM:
            fvals: list[float] = []
            dvals: list[float] = []
            n_neighbors = 0
            for j, other in enumerate(ids):
                dij = dist[i, j]
                if np.isnan(dij) or dij > radius:
                    continue
                if (prev, other) not in panel.index:
                    continue
                n_neighbors += 1
                other_prev = panel.loc[(prev, other)]
                fvals.append(float(other_prev["focal_frequency"]))
                dvals.append(float(other_prev["detected"]))
            tag = f"{radius:.2f}"
            rec[f"neighbor_count_{tag}"] = int(n_neighbors)
            rec[f"neighbor_frequency_{tag}"] = float(np.mean(fvals)) if fvals else np.nan
            rec[f"neighbor_detected_{tag}"] = float(np.mean(dvals)) if dvals else np.nan
        rows.append(rec)

    return pd.DataFrame(rows)


def predictor(train, test, target, numeric, learner):
    cats = ["water_body", "node_id"]
    pre = ColumnTransformer(
        [
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cats),
        ]
    )
    if learner == "logistic":
        model = make_pipeline(pre, LogisticRegression(max_iter=2000, C=1.0))
        model.fit(train[numeric + cats], train[target].astype(int))
        return model.predict_proba(test[numeric + cats])[:, 1]
    if learner == "ridge":
        model = make_pipeline(pre, Ridge(alpha=1.0))
        model.fit(train[numeric + cats], train[target].astype(float))
        return np.clip(model.predict(test[numeric + cats]), 0.0, 1.0)
    raise RuntimeError(learner)


def signflip_mc(delta: np.ndarray, seed: int) -> float:
    d = np.asarray(delta, dtype=float)
    obs = float(d.mean())
    rng = np.random.default_rng(seed)
    count = 0
    remaining = PERM_REPS
    while remaining:
        n = min(5000, remaining)
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=(n, len(d)), replace=True)
        vals = (signs * d[None, :]).mean(axis=1)
        count += int(np.sum(vals <= obs + 1e-15))
        remaining -= n
    return float((count + 1) / (PERM_REPS + 1))


def walkforward_neighborhood(panel: pd.DataFrame, outcome: str, lag: str, prefix: str, learner: str, seed: int):
    neigh = [f"{prefix}_{r:.2f}" for r in EOG_RADII_KM]
    rows = []
    for year in TARGET_YEARS:
        train = panel[panel["year"] < year].copy()
        test = panel[panel["year"] == year].copy()
        if len(test) == 0:
            raise RuntimeError(f"no test rows in {year}")
        base_numeric = ["longitude", "latitude", "year", lag]
        aug_numeric = base_numeric + neigh
        if train[aug_numeric].isna().any().any() or test[aug_numeric].isna().any().any():
            raise RuntimeError(f"missing neighborhood predictor in target year {year}")

        p0 = predictor(train, test, outcome, base_numeric, learner)
        p1 = predictor(train, test, outcome, aug_numeric, learner)
        y = test[outcome].to_numpy()

        if learner == "logistic":
            s0 = float(log_loss(y.astype(int), p0, labels=[0, 1]))
            s1 = float(log_loss(y.astype(int), p1, labels=[0, 1]))
            metric = "log_loss"
        else:
            s0 = float(mean_absolute_error(y.astype(float), p0))
            s1 = float(mean_absolute_error(y.astype(float), p1))
            metric = "mae"

        rows.append(
            {
                "target_year": int(year),
                "n": int(len(test)),
                "baseline_score": s0,
                "dynamic_neighborhood_score": s1,
                "delta": s1 - s0,
            }
        )

    yr = pd.DataFrame(rows)
    delta = yr["delta"].to_numpy(float)
    return {
        "metric": metric,
        "target_years": int(len(yr)),
        "baseline_mean_score": float(yr["baseline_score"].mean()),
        "dynamic_neighborhood_mean_score": float(yr["dynamic_neighborhood_score"].mean()),
        "mean_delta": float(delta.mean()),
        "median_delta": float(np.median(delta)),
        "dynamic_neighborhood_wins": int(np.sum(delta < 0)),
        "baseline_wins": int(np.sum(delta > 0)),
        "ties": int(np.sum(delta == 0)),
        "signflip_mc_one_sided_p": signflip_mc(delta, seed),
        "yearly": rows,
    }


def main(input_dir: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "quant_annual_panel.csv")

    required = {
        "node_id",
        "year",
        "water_body",
        "longitude",
        "latitude",
        "detected",
        "focal_frequency",
        "bb_cover_mean_all_points",
        "blade_length_mean_mm",
        "shoot_density_mean_m2",
    }
    missing = required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing annual columns: {sorted(missing)}")
    if len(annual) != 1480 or annual["node_id"].nunique() != 71:
        raise RuntimeError("Tampa annual panel identity drift")

    variance = {}
    for var in STATE_VARS:
        d = annual.dropna(subset=[var]).copy()
        variance[var] = {
            "n": int(len(d)),
            "stable_node_r2": group_mean_r2(d, var, ["node_id"]),
            "year_r2": group_mean_r2(d, var, ["year"]),
            "water_body_r2": group_mean_r2(d, var, ["water_body"]),
            "bay_year_r2": group_mean_r2(d, var, ["water_body", "year"]),
            "node_plus_year_additive_r2": additive_node_year_r2(d, var),
        }

    lagged = build_lagged_neighborhood_panel(annual)
    if len(lagged) != 1176:
        raise RuntimeError(f"unexpected consecutive-year row count: {len(lagged)}")

    binary = walkforward_neighborhood(
        lagged,
        outcome="detected",
        lag="lag_detected",
        prefix="neighbor_detected",
        learner="logistic",
        seed=SEED + 1,
    )
    frequency = walkforward_neighborhood(
        lagged,
        outcome="focal_frequency",
        lag="lag_frequency",
        prefix="neighbor_frequency",
        learner="ridge",
        seed=SEED + 2,
    )

    result = {
        "schema": "tampa.eog_ecological_translation_v1",
        "status": "posthoc_ecological_translation",
        "source_panel": {
            "annual_node_years": int(len(annual)),
            "stable_nodes": int(annual["node_id"].nunique()),
            "consecutive_year_rows": int(len(lagged)),
            "years": [int(annual["year"].min()), int(annual["year"].max())],
        },
        "eog_translation": {
            "frozen_radii_km": EOG_RADII_KM,
            "structural_failure_fact": "The consumed Tampa EOG Layer-B block became a static injective node-level geometry signature reused across repeated visits while all five worlds remained compatible.",
            "ecological_question": "Does annually refreshed previous-year neighborhood state add information beyond stable site identity and the focal transect's own previous-year state?",
        },
        "state_structure": variance,
        "dynamic_neighborhood": {
            "binary_detected": binary,
            "focal_frequency": frequency,
        },
        "interpretation": (
            "Stable transect identity explains most level variation in recorded detection, focal frequency and Braun-Blanquet state, whereas blade length and shoot density are much less site-saturated. "
            "A simple response-aligned neighborhood state using the four frozen EOG radii does not improve mean heldout prediction beyond node identity plus local lag-1 for either binary detection or focal frequency. "
            "Together these results favor a local-site-template/local-meadow-state hypothesis over a simple dynamic-neighborhood-accessibility explanation, while remaining post-hoc and noncausal."
        ),
        "hypotheses": [
            {
                "id": "H1_site_template_buffer",
                "statement": "Persistent local site quality and clonal meadow legacy stabilize recorded Thalassia occurrence while above-ground condition can deteriorate within occupied transects.",
            },
            {
                "id": "H2_local_threshold_loss",
                "statement": "Recorded loss is more likely to occur when local meadow condition has thinned toward a detection/occupancy threshold than because regional spatial accessibility has changed.",
            },
            {
                "id": "H3_dynamic_neighborhood",
                "statement": "If regional meadow configuration matters at annual scales, previous-year neighborhood state should add prediction beyond stable node identity and local lag-1; this simple four-radius implementation is not supported descriptively.",
            },
            {
                "id": "H4_multiple_degradation_paths",
                "statement": "Different bay segments can approach the same persistent binary state through distinct degradation pathways: plant-condition decline, within-transect contraction, or community reorganization.",
            },
        ],
        "claim_boundary": [
            "Post-hoc ecological translation of an already-consumed EOG endpoint.",
            "No EOG endpoint is repaired, rerun or reclassified.",
            "Variance-explained quantities are descriptive and not causal effects.",
            "Node identity is a saturated site reference, not a measured habitat mechanism.",
            "The dynamic-neighborhood comparison tests one simple annual neighborhood formulation only.",
            "Clonal persistence, light limitation and local recruitment are mechanistic candidates requiring direct ecological measurements or external evidence.",
        ],
    }

    pd.DataFrame(binary["yearly"]).to_csv(outdir / "eog_translation_binary_yearly.csv", index=False)
    pd.DataFrame(frequency["yearly"]).to_csv(outdir / "eog_translation_frequency_yearly.csv", index=False)
    (outdir / "eog_ecological_translation_v1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/generated_eog_ecology"))
    p.add_argument("--out", type=Path, default=Path("results/generated_eog_ecology"))
    a = p.parse_args()
    main(a.input, a.out)
