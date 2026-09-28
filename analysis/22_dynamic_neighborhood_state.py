#!/usr/bin/env python3
"""Exploratory Tampa test of dynamic segment and neighborhood state.

Question: after stable transect identity and a transect's own previous-year
quantitative state are included, does previous-year surrounding meadow state
add information about next-year state?

The distance radii are reused unchanged from the frozen Tampa EOG endpoint-3
Haversine world family. The primary radius is the frozen q50 threshold.
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

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "results/dynamic_neighborhood_state_v1_contract.json").read_text()
)

RADII = [float(x) for x in CONTRACT["spatial_scales_km"]["tested"]]
PRIMARY_RADIUS = float(CONTRACT["spatial_scales_km"]["primary"])
SEED = int(CONTRACT["scoring"]["support_rule"]["random_seed"])
PERM_REPS = int(CONTRACT["scoring"]["support_rule"]["signflip_replicates"])
TARGET_YEARS = list(range(
    int(CONTRACT["transition_design"]["target_years"][0]),
    int(CONTRACT["transition_design"]["target_years"][1]) + 1,
))
MIN_TRAIN_ROWS = 80
MIN_TRAIN_YEARS = 3

METRICS = {
    "frequency": {"column": "focal_frequency", "clip": [0.0, 1.0]},
    "cover_index": {"column": "bb_cover_mean_all_points", "clip": None},
}


def haversine_matrix(nodes: pd.DataFrame) -> np.ndarray:
    lat = np.radians(nodes["latitude"].to_numpy(float))
    lon = np.radians(nodes["longitude"].to_numpy(float))
    dlat = lat[:, None] - lat[None, :]
    dlon = lon[:, None] - lon[None, :]
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2.0) ** 2
    return 6371.0 * 2.0 * np.arcsin(np.minimum(1.0, np.sqrt(a)))


def signflip(delta: np.ndarray, seed: int) -> float:
    d = np.asarray(delta, dtype=float)
    obs = float(d.mean())
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(PERM_REPS):
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=len(d), replace=True)
        if float(np.mean(d * signs)) <= obs:
            count += 1
    return float((1 + count) / (1 + PERM_REPS))


def support(delta: np.ndarray, seed: int) -> dict:
    d = np.asarray(delta, dtype=float)
    p = signflip(d, seed)
    need = math.ceil(float(CONTRACT["scoring"]["support_rule"]["minimum_win_fraction"]) * len(d))
    return {
        "target_years": int(len(d)),
        "wins": int((d < 0).sum()),
        "losses": int((d > 0).sum()),
        "ties": int((d == 0).sum()),
        "mean_delta": float(d.mean()),
        "median_delta": float(np.median(d)),
        "signflip_p": p,
        "supported": bool(
            int((d < 0).sum()) >= need
            and float(np.median(d)) < 0.0
            and p < float(CONTRACT["scoring"]["support_rule"]["one_sided_signflip_p_lt"])
        ),
    }


def build_transition_frame(annual: pd.DataFrame, metric: str, radius: float) -> pd.DataFrame:
    node_meta = (
        annual[["node_id", "longitude", "latitude", "water_body"]]
        .drop_duplicates("node_id")
        .sort_values("node_id")
        .reset_index(drop=True)
    )
    ids = node_meta["node_id"].tolist()
    index = {node: i for i, node in enumerate(ids)}
    dist = haversine_matrix(node_meta)
    within = (dist <= float(radius)) & (dist > 0.0)

    by_year = {
        int(year): g.set_index("node_id")
        for year, g in annual.groupby("year", sort=True)
    }

    rows = []
    for node, g in annual.sort_values(["node_id", "year"]).groupby("node_id"):
        recs = g.sort_values("year").to_dict("records")
        for source, target in zip(recs[:-1], recs[1:]):
            sy = int(source["year"])
            ty = int(target["year"])
            if ty != sy + 1:
                continue

            source_year = by_year[sy]
            wb = str(source["water_body"])
            segment_peers = source_year[
                (source_year["water_body"].astype(str) == wb)
                & (source_year.index.astype(str) != str(node))
            ]
            if len(segment_peers) < int(CONTRACT["predictors"]["minimum_segment_peers"]):
                continue

            i = index[str(node)]
            neighbor_ids = [
                ids[j] for j in range(len(ids))
                if within[i, j] and ids[j] in source_year.index and ids[j] != node
            ]
            if len(neighbor_ids) < int(CONTRACT["predictors"]["minimum_neighborhood_peers"]):
                continue

            own = float(source[metric])
            seg = float(segment_peers[metric].mean())
            neigh = float(source_year.loc[neighbor_ids, metric].mean())

            rows.append({
                "node_id": str(node),
                "water_body": wb,
                "source_year": sy,
                "target_year": ty,
                "target": float(target[metric]),
                "own_lag1": own,
                "segment_lag1_mean": seg,
                "neighborhood_lag1_mean": neigh,
                "local_neighborhood_residual": neigh - seg,
                "segment_peer_count": int(len(segment_peers)),
                "neighborhood_peer_count": int(len(neighbor_ids)),
            })

    return pd.DataFrame(rows).sort_values(["target_year", "node_id"]).reset_index(drop=True)


def model_predict(train: pd.DataFrame, test: pd.DataFrame, numeric: list[str], clip):
    categorical = ["water_body", "node_id"]
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", StandardScaler(), numeric),
    ])
    model = make_pipeline(pre, Ridge(alpha=1.0))
    model.fit(train[categorical + numeric], train["target"].to_numpy(float))
    pred = np.asarray(model.predict(test[categorical + numeric]), dtype=float)
    if clip is not None:
        pred = np.clip(pred, float(clip[0]), float(clip[1]))
    return pred


def score_radius(frame: pd.DataFrame, clip, radius_index: int) -> tuple[pd.DataFrame, dict]:
    yearly = []
    for year in TARGET_YEARS:
        train = frame[frame["target_year"] < year].copy()
        test = frame[frame["target_year"] == year].copy()
        if len(test) == 0:
            raise RuntimeError(f"no test rows for target year {year}")
        if len(train) < MIN_TRAIN_ROWS or train["target_year"].nunique() < MIN_TRAIN_YEARS:
            raise RuntimeError(f"insufficient training rows for target year {year}: {len(train)}")

        y = test["target"].to_numpy(float)
        own = model_predict(train, test, ["target_year", "own_lag1"], clip)
        segment = model_predict(
            train, test,
            ["target_year", "own_lag1", "segment_lag1_mean"],
            clip,
        )
        local = model_predict(
            train, test,
            ["target_year", "own_lag1", "segment_lag1_mean", "local_neighborhood_residual"],
            clip,
        )
        yearly.append({
            "target_year": int(year),
            "n_test": int(len(test)),
            "own_mae": float(mean_absolute_error(y, own)),
            "segment_mae": float(mean_absolute_error(y, segment)),
            "local_mae": float(mean_absolute_error(y, local)),
        })

    ys = pd.DataFrame(yearly)
    if len(ys) != len(TARGET_YEARS):
        raise RuntimeError(f"expected {len(TARGET_YEARS)} target years, got {len(ys)}")

    segment_delta = ys["segment_mae"].to_numpy(float) - ys["own_mae"].to_numpy(float)
    local_delta = ys["local_mae"].to_numpy(float) - ys["segment_mae"].to_numpy(float)

    summary = {
        "radius_km": float(frame.attrs["radius_km"]),
        "rows": int(len(frame)),
        "nodes": int(frame["node_id"].nunique()),
        "target_years": int(len(ys)),
        "mean_mae": {
            "own": float(ys["own_mae"].mean()),
            "segment": float(ys["segment_mae"].mean()),
            "local": float(ys["local_mae"].mean()),
        },
        "segment_increment": support(segment_delta, SEED + radius_index * 100 + 1),
        "local_increment": support(local_delta, SEED + radius_index * 100 + 2),
        "median_segment_peer_count": float(frame["segment_peer_count"].median()),
        "median_neighborhood_peer_count": float(frame["neighborhood_peer_count"].median()),
        "minimum_neighborhood_peer_count": int(frame["neighborhood_peer_count"].min()),
    }
    return ys, summary


def classify(primary: dict) -> str:
    seg = bool(primary["segment_increment"]["supported"])
    local = bool(primary["local_increment"]["supported"])
    if seg and local:
        return "nested_segment_and_local_context_candidate"
    if seg and not local:
        return "segment_synchrony_candidate"
    if local:
        return "local_spatial_coupling_candidate"
    return "own_recent_state_and_site_identity_dominate"


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(input_dir / "quant_annual_panel.csv")
    required = {
        "node_id", "year", "water_body", "longitude", "latitude",
        "focal_frequency", "bb_cover_mean_all_points",
    }
    missing = required.difference(annual.columns)
    if missing:
        raise RuntimeError(f"missing columns: {sorted(missing)}")
    if len(annual) != 1480 or annual["node_id"].nunique() != 71:
        raise RuntimeError("Tampa annual panel identity drift")
    if annual[["focal_frequency", "bb_cover_mean_all_points"]].isna().any().any():
        raise RuntimeError("unexpected missing focal quantitative state")

    results = {}
    for metric_index, (key, spec) in enumerate(METRICS.items()):
        radius_results = []
        primary_years = None
        for radius_index, radius in enumerate(RADII):
            frame = build_transition_frame(annual, spec["column"], radius)
            frame.attrs["radius_km"] = radius
            yearly, summary = score_radius(frame, spec["clip"], metric_index * 10 + radius_index)
            radius_results.append(summary)
            frame.to_csv(outdir / f"dynamic_neighborhood_{key}_{radius:.6f}km_rows.csv", index=False)
            yearly.to_csv(outdir / f"dynamic_neighborhood_{key}_{radius:.6f}km_year_scores.csv", index=False)
            if math.isclose(radius, PRIMARY_RADIUS, rel_tol=0.0, abs_tol=1e-12):
                primary_years = yearly

        primary = next(
            x for x in radius_results
            if math.isclose(float(x["radius_km"]), PRIMARY_RADIUS, rel_tol=0.0, abs_tol=1e-12)
        )
        results[key] = {
            "primary_radius_km": PRIMARY_RADIUS,
            "primary": primary,
            "classification": classify(primary),
            "sensitivity": {
                "tested_radii_km": RADII,
                "segment_supported_radii": int(sum(x["segment_increment"]["supported"] for x in radius_results)),
                "local_supported_radii": int(sum(x["local_increment"]["supported"] for x in radius_results)),
                "radius_results": radius_results,
            },
        }
        if primary_years is None:
            raise RuntimeError("primary radius scores missing")

    overall = {
        "segment_supported_both_metrics": bool(
            results["frequency"]["primary"]["segment_increment"]["supported"]
            and results["cover_index"]["primary"]["segment_increment"]["supported"]
        ),
        "local_supported_both_metrics": bool(
            results["frequency"]["primary"]["local_increment"]["supported"]
            and results["cover_index"]["primary"]["local_increment"]["supported"]
        ),
    }

    summary = {
        "schema": "tampa.dynamic_neighborhood_state_v1.result",
        "status": "posthoc_exploratory_completed",
        "contract": "results/dynamic_neighborhood_state_v1_contract.json",
        "primary_radius_km": PRIMARY_RADIUS,
        "results": results,
        "cross_metric": overall,
        "interpretation": (
            "This analysis separates shared bay-segment state from finer spatial neighborhood state "
            "after stable transect identity and own lag-1 state. Positive increments identify predictive "
            "context at that scale, not causal dispersal or environmental forcing."
        ),
        "claim_boundary": CONTRACT["claim_boundary"],
    }
    (outdir / "dynamic_neighborhood_state_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/generated_dynamic_neighborhood"))
    p.add_argument("--out", type=Path, default=Path("results/generated_dynamic_neighborhood"))
    a = p.parse_args()
    main(a.input, a.out)
