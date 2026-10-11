#!/usr/bin/env python3
"""Response-free counterexample: local TNC predicts future ordinal state with zero TNC effect.

This is an identifiability/measurement stress test of the frozen Tampa within-node
TNC analysis, NOT a new analysis of observed Tampa biological outcomes. Parameters
are deliberately illustrative, not calibrated to Tampa. No threshold tuning.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

SEED = 20261008
N_NODES = 38
ANCHORS_PER_NODE = 3
RHO = 0.6
N_REPLAYS = 1200
ERROR_SD = 0.6
FUTURE_SD = 0.35
CUTPOINTS = (-0.75, -0.25, 0.25, 0.75)  # stylized ordinal categories 0..4


def node_center(a: np.ndarray) -> np.ndarray:
    z = np.asarray(a, float).reshape(N_NODES, ANCHORS_PER_NODE)
    return (z - z.mean(axis=1, keepdims=True)).ravel()


def coeff(y: np.ndarray, current: np.ndarray, tnc: np.ndarray) -> float:
    # Frisch-Waugh-Lovell removal of stable node fixed effects.
    x = np.column_stack((node_center(current), node_center(tnc)))
    if np.linalg.matrix_rank(x) < 2:
        raise ValueError("rank-deficient within-node design")
    return float(np.linalg.lstsq(x, node_center(y), rcond=None)[0][1])


def ordinal(z: np.ndarray) -> np.ndarray:
    return np.digitize(z, CUTPOINTS).astype(float)


def simulate(seed: int = SEED, reps: int = N_REPLAYS) -> dict:
    rng = np.random.default_rng(seed)
    results = {k: [] for k in (
        "ideal_latent_current", "ordinal_current_no_reader_error",
        "ordinal_current_with_reader_error", "two_independent_reader_average",
    )}
    for _ in range(reps):
        tnc = rng.normal(size=N_NODES * ANCHORS_PER_NODE)
        q = RHO * tnc + np.sqrt(1 - RHO**2) * rng.normal(size=tnc.size)
        site = np.repeat(rng.normal(scale=0.45, size=N_NODES), ANCHORS_PER_NODE)
        latent = q + site
        future = ordinal(latent + rng.normal(scale=FUTURE_SD, size=tnc.size))
        bb_clean = ordinal(latent)
        bb_reader1 = ordinal(latent + rng.normal(scale=ERROR_SD, size=tnc.size))
        bb_reader2 = ordinal(latent + rng.normal(scale=ERROR_SD, size=tnc.size))
        cases = {
            "ideal_latent_current": latent,
            "ordinal_current_no_reader_error": bb_clean,
            "ordinal_current_with_reader_error": bb_reader1,
            "two_independent_reader_average": (bb_reader1 + bb_reader2) / 2,
        }
        for name, baseline in cases.items():
            results[name].append(coeff(future, baseline, tnc))
    output = {
        "schema": "tampa.tnc_baseline_information_stress_test_v1",
        "class": "illustrative_response_free_known_truth_counterexample",
        "seed": seed, "replicates": reps,
        "design": {"nodes": N_NODES, "anchors_per_node": ANCHORS_PER_NODE,
                   "tnc_correlation_with_true_current_latent_state": RHO,
                   "reader_error_sd": ERROR_SD, "future_latent_noise_sd": FUTURE_SD,
                   "ordinal_cutpoints": list(CUTPOINTS),
                   "tnc_direct_or_lagged_effect_on_future_state": 0.0},
        "scenarios": {},
        "interpretation": (
            "Predictive augmentation by measured TNC can occur when TNC proxies "
            "unresolved current state inside ordinal Braun-Blanquet classes; "
            "it does not by itself identify a causal reserve buffering effect. "
            "This simulation has no Tampa biological or HPLC data."
        )
    }
    for name, values in results.items():
        z = np.asarray(values)
        output["scenarios"][name] = {
            "mean_tnc_coefficient": float(z.mean()),
            "median_tnc_coefficient": float(np.median(z)),
            "fraction_positive": float(np.mean(z > 0)),
            "replay_interval_2p5_97p5": np.quantile(z, [.025, .975]).tolist()
        }
    return output


def self_test() -> None:
    rng = np.random.default_rng(123)
    t = rng.normal(size=N_NODES * ANCHORS_PER_NODE)
    b = rng.normal(size=t.size)
    y = 2 * b + 3 * t + np.repeat(rng.normal(size=N_NODES), ANCHORS_PER_NODE)
    assert abs(coeff(y, b, t) - 3.0) < 1e-10
    assert np.all(np.isin(ordinal(np.array([-100, -1, 0, 1, 100])), [0, 1, 2, 3, 4]))
    print("PASS: node fixed-effect coefficient recovery and ordinal coding")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("results/generated_pilot_design/tnc_baseline_information_stress_test_v1.json"))
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    result = simulate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: round(v["mean_tnc_coefficient"], 4) for k, v in result["scenarios"].items()}, indent=2))


if __name__ == "__main__":
    main()
