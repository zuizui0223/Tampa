#!/usr/bin/env python3
"""A known-truth detection-only counterexample to Tampa re-recording fragility.

This is an EXACT analytic illustration: all true Thalassia states are occupied
for four consecutive years. No original Point-event table is read, model fitted,
latent process estimated, observation endpoint retuned, or new test performed.
Only the published frozen JSON summary is used for contextual comparison.

Across marks, annual recording probability p_i is stable but heterogeneous.
Conditional on p_i, annual observations are independent Bernoulli(p_i).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = Path("results/return_fragility_v1.json")
ILLUSTRATIVE_ALPHA = 1.0
ILLUSTRATIVE_BETA = 0.5


def beta_counterexample(alpha: float, beta: float) -> dict:
    """Condition on detections at t and t+2, then classify t+1 and score t+3."""
    if not all(math.isfinite(x) and x > 0 for x in (alpha, beta)):
        raise ValueError("Beta parameters must be strictly positive finite numbers")
    fraction_gap = beta / (alpha + beta + 2)
    later_absent_given_gap = (beta + 1) / (alpha + beta + 3)
    later_absent_given_continuous = beta / (alpha + beta + 3)
    overall_later_absence = (
        fraction_gap * later_absent_given_gap
        + (1 - fraction_gap) * later_absent_given_continuous
    )
    event_share_gap = fraction_gap * later_absent_given_gap / overall_later_absence
    return {
        "prior_recording_probability": f"Beta({alpha:g}, {beta:g}) across marks",
        "true_occupancy_trajectory": [1, 1, 1, 1],
        "conditional_group_definition": "O(t)=1,O(t+2)=1; gap if O(t+1)=0",
        "fraction_gap_group": fraction_gap,
        "later_non_detection_given_gap": later_absent_given_gap,
        "later_non_detection_given_continuous": later_absent_given_continuous,
        "risk_difference_percentage_points": 100 * (
            later_absent_given_gap - later_absent_given_continuous
        ),
        "risk_ratio": later_absent_given_gap / later_absent_given_continuous,
        "later_non_detection_fraction_overall": overall_later_absence,
        "gap_group_fraction_of_later_non_detections": event_share_gap,
        "event_concentration_ratio": event_share_gap / fraction_gap,
    }


def discrete_selection_identity(p_values: list[float],
                                prior_weights: list[float]) -> dict:
    """General proof check via heterogeneous static, conditionally i.i.d. p."""
    if len(p_values) != len(prior_weights) or not p_values:
        raise ValueError("Need matched nonempty probabilities and weights")
    if any(not math.isfinite(p) or not 0 < p < 1 for p in p_values):
        raise ValueError("p must lie strictly between zero and one")
    if any(not math.isfinite(w) or w < 0 for w in prior_weights):
        raise ValueError("Weights must be finite and nonnegative")
    z = sum(w * p * p for w, p in zip(prior_weights, p_values))
    if z <= 0:
        raise ValueError("No positive weighted support")
    conditioned_weights = [
        w * p * p / z for w, p in zip(prior_weights, p_values)
    ]
    qs = [1 - p for p in p_values]
    mu = sum(w * q for w, q in zip(conditioned_weights, qs))
    second = sum(w * q * q for w, q in zip(conditioned_weights, qs))
    var = second - mu * mu
    if not 0 < mu < 1:
        raise ValueError("Undefined conditional subgroup")
    rate_gap = second / mu
    rate_cont = (mu - second) / (1 - mu)
    delta = rate_gap - rate_cont
    identity_rhs = var / (mu * (1 - mu))
    if not math.isclose(delta, identity_rhs, abs_tol=1e-12, rel_tol=1e-12):
        raise AssertionError("Selection identity failed")
    return {
        "conditional_mean_non_detection_probability": mu,
        "conditional_variance_non_detection_probability": max(0.0, var),
        "later_non_detection_given_gap": rate_gap,
        "later_non_detection_given_continuous": rate_cont,
        "gap_minus_continuous_probability": delta,
        "variance_identity_rhs": identity_rhs,
    }


def observed_summary(source: dict) -> dict:
    if source.get("schema") != "tampa.return_fragility_v1.canonical_summary":
        raise ValueError("Canonical source schema mismatch")
    if source.get("status") != "return_fragility_supported":
        raise ValueError("Unexpected canonical source status")
    r, s = source["registry"], source["secondary"]
    total = int(r["four_year_sequences"])
    gap = int(r["recovered_sequences"])
    cont = int(r["continuous_sequences"])
    events = int(r["total_recorded_relosses"])
    if gap + cont != total or min(gap, cont, events) <= 0:
        raise ValueError("Incoherent counts")
    gap_events = round(float(s["recovered_reloss_fraction"]) * gap)
    cont_events = round(float(s["continuous_reloss_fraction"]) * cont)
    if (gap_events + cont_events != events
            or not math.isclose(gap_events / gap, s["recovered_reloss_fraction"], abs_tol=1e-12)
            or not math.isclose(cont_events / cont, s["continuous_reloss_fraction"], abs_tol=1e-12)):
        raise ValueError("Canonical loss fractions do not match integer counts")
    return {
        "sequences_total": total,
        "gap_group_sequences": gap,
        "uninterrupted_sequences": cont,
        "later_non_detections_total": events,
        "later_non_detections_gap_group": gap_events,
        "later_non_detections_uninterrupted": cont_events,
        "gap_group_fraction": gap / total,
        "later_non_detection_given_gap": gap_events / gap,
        "later_non_detection_given_continuous": cont_events / cont,
        "risk_difference_percentage_points": 100 * (gap_events / gap - cont_events / cont),
        "risk_ratio": (gap_events / gap) / (cont_events / cont),
        "gap_group_fraction_of_later_non_detections": gap_events / events,
    }


def derive(source: dict) -> dict:
    return {
        "schema": "tampa.return_fragility_detection_only_counterexample_v1",
        "evidence_class": "response_free_analytic_sufficiency_counterexample_with_frozen_descriptive_comparison",
        "source": str(SOURCE),
        "observed_frozen_reaggregation": observed_summary(source),
        "illustrative_known_truth_no_demographic_change": beta_counterexample(
            ILLUSTRATIVE_ALPHA, ILLUSTRATIVE_BETA
        ),
        "general_identity": (
            "For weights w_i proportional to prior_mark_weight_i*p_i^2, q_i=1-p_i, "
            "mu=E_w[q], risk_gap=E_w[q^2]/mu, "
            "risk_cont=(mu-E_w[q^2])/(1-mu), "
            "risk_gap-risk_cont=Var_w(q)/(mu*(1-mu))>=0."
        ),
        "static_heterogeneity_example": discrete_selection_identity(
            [0.95, 0.50], [0.5, 0.5]
        ),
        "limits": [
            "The illustrative Beta parameters were chosen after the published outcome was known; do not treat them as fitted, independently calibrated, or confirming this explanation.",
            "All organisms are assumed truly present in the counterexample; p_i is effective yearly mark-level recording probability, including patch encounter and detectability.",
            "Original observations do not identify the distribution of p_i or prove detection-only versus true demographic transitions.",
            "Node and year adjustments do not eliminate persistent heterogeneity among meter marks within the same node.",
            "No new p-values, confidence intervals or empirical model comparisons are produced.",
            "Retain the original positive observation-level coefficient; do not upgrade it to biological recovery fragility or causal hysteresis.",
            "A new repeated-mark measurement process and independently recorded outcomes are needed to distinguish detection heterogeneity from ecology.",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=SOURCE)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    raw = a.source.read_bytes()
    out = derive(json.loads(raw))
    out["canonical_source_sha256"] = hashlib.sha256(raw).hexdigest()
    serialized = json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if a.out is None:
        print(serialized, end="")
    else:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
