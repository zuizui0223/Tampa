#!/usr/bin/env python3
"""Within-node audit of binary pre-existing community insurance.

Frozen design:
  results/community_insurance_node_audit_v1_contract.json

Consumes the exact same 370 Thalassia-loss transitions produced by
analysis/34_community_insurance.py. The predictor is binary source_mixed,
centered within stable transect node. Stable node identity and target year
are included in the reference model.

This is a post-hoc reference-saturation audit of an already-opened endpoint.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / "results/community_insurance_node_audit_v1_contract.json").read_text())
BOOT = int(C["uncertainty"]["bootstrap_replicates"])
SEED = int(C["uncertainty"]["random_seed"])


def as_bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().map({"true": True, "false": False})


def prepare(trans: pd.DataFrame):
    required = {
        "node_id", "target_year", "source_mixed",
        "target_any_seagrass_present",
    }
    missing = required.difference(trans.columns)
    if missing:
        raise RuntimeError(f"missing transition columns: {sorted(missing)}")

    d = trans.copy()
    d["node_id"] = d["node_id"].astype(str)
    d["source_mixed"] = as_bool(d["source_mixed"])
    d["target_any_seagrass_present"] = as_bool(d["target_any_seagrass_present"])

    variation = d.groupby("node_id")["source_mixed"].nunique()
    informative = sorted(variation[variation >= 2].index.tolist())
    d = d[d["node_id"].isin(informative)].copy()

    means = d.groupby("node_id")["source_mixed"].transform("mean")
    d["within_node_centered_source_mixed"] = (
        d["source_mixed"].astype(float) - means.astype(float)
    )
    return d, informative


def make_model():
    pre = ColumnTransformer([
        ("num", StandardScaler(),
         ["target_year", "within_node_centered_source_mixed"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["node_id"]),
    ])
    return make_pipeline(
        pre,
        LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000),
    )


def fit_coef(d: pd.DataFrame) -> float:
    if d["target_any_seagrass_present"].nunique() < 2:
        raise RuntimeError("one-class target")
    m = make_model()
    cols = ["target_year", "within_node_centered_source_mixed", "node_id"]
    m.fit(d[cols], d["target_any_seagrass_present"].astype(int))
    return float(m.named_steps["logisticregression"].coef_[0][1])


def bootstrap(d: pd.DataFrame, informative: list[str]) -> dict:
    full = fit_coef(d)
    by = {n: d[d["node_id"] == n] for n in informative}
    rng = np.random.default_rng(SEED)

    vals = []
    attempts = 0
    while len(vals) < BOOT and attempts < BOOT * 30:
        attempts += 1
        chosen = rng.choice(informative, size=len(informative), replace=True)
        pieces = []
        for j, n in enumerate(chosen):
            x = by[n].copy()
            # Re-label duplicate sampled clusters so each bootstrap copy gets
            # its own node fixed effect while preserving within-node rows.
            x["node_id"] = f"boot_{j}_{n}"
            pieces.append(x)
        z = pd.concat(pieces, ignore_index=True)
        if z["target_any_seagrass_present"].nunique() < 2:
            continue
        try:
            vals.append(fit_coef(z))
        except Exception:
            continue

    if len(vals) < BOOT:
        raise RuntimeError(f"insufficient valid bootstrap fits: {len(vals)}")

    arr = np.asarray(vals, float)
    ci = np.quantile(arr, [0.025, 0.975])
    return {
        "standardized_centered_source_mixed_log_odds_coefficient": float(full),
        "ci95": [float(ci[0]), float(ci[1])],
        "bootstrap_replicates_used": int(len(arr)),
        "bootstrap_attempts": int(attempts),
        "supported": bool(ci[0] > 0),
    }


def node_descriptives(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for n, g in d.groupby("node_id", sort=True):
        mixed = g[g["source_mixed"]]
        alone = g[~g["source_mixed"]]
        rows.append({
            "node_id": n,
            "transitions": int(len(g)),
            "mixed_n": int(len(mixed)),
            "thalassia_only_n": int(len(alone)),
            "mixed_target_occupancy_fraction":
                float(mixed["target_any_seagrass_present"].mean()),
            "thalassia_only_target_occupancy_fraction":
                float(alone["target_any_seagrass_present"].mean()),
            "mixed_minus_alone_difference":
                float(mixed["target_any_seagrass_present"].mean()
                      - alone["target_any_seagrass_present"].mean()),
        })
    return pd.DataFrame(rows)


def main(input_dir: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    trans = pd.read_csv(input_dir / "community_insurance_transitions.csv")
    if len(trans) != 370:
        raise RuntimeError(f"community-insurance transition registry drift: {len(trans)}")

    d, informative = prepare(trans)
    primary = bootstrap(d, informative)
    nodes = node_descriptives(d)

    result = {
        "schema": "tampa.community_insurance_node_audit_v1.result",
        "status": (
            "within_node_binary_community_insurance_supported"
            if primary["supported"]
            else "within_node_binary_community_insurance_not_supported"
        ),
        "contract": "results/community_insurance_node_audit_v1_contract.json",
        "registry": {
            "all_transitions": int(len(trans)),
            "all_nodes": int(trans["node_id"].nunique()),
            "informative_nodes": int(len(informative)),
            "informative_transitions": int(len(d)),
            "mixed_events_informative": int(d["source_mixed"].sum()),
            "thalassia_only_events_informative": int((~d["source_mixed"]).sum()),
        },
        "primary": primary,
        "secondary": {
            "positive_node_differences": int((nodes["mixed_minus_alone_difference"] > 0).sum()),
            "zero_node_differences": int((nodes["mixed_minus_alone_difference"] == 0).sum()),
            "negative_node_differences": int((nodes["mixed_minus_alone_difference"] < 0).sum()),
            "median_node_difference": float(nodes["mixed_minus_alone_difference"].median()),
        },
        "interpretation": (
            C["interpretation"]["supported"]
            if primary["supported"]
            else C["interpretation"]["unsupported"]
        ),
        "claim_boundary": C["claim_boundary"],
    }

    d.to_csv(outdir / "community_insurance_node_audit_transitions.csv", index=False)
    nodes.to_csv(outdir / "community_insurance_node_audit_nodes.csv", index=False)
    (outdir / "community_insurance_node_audit_v1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path,
                   default=Path("results/generated_community_insurance"))
    p.add_argument("--out", type=Path,
                   default=Path("results/generated_community_insurance_node_audit"))
    a = p.parse_args()
    main(a.input, a.out)
