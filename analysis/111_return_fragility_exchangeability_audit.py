#!/usr/bin/env python3
"""Aggregate-only audit: static mark-detection exchangeability and survey design.

No biological response rows are refit. Four-year sequences are NOT independent.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

DEFAULT = Path("results/return_fragility_v1.json")


def cells_from_frozen(source):
    if source.get("schema") != "tampa.return_fragility_v1.canonical_summary" or source.get("status") != "return_fragility_supported":
        raise ValueError("Invalid canonical source")
    r, s = source["registry"], source["secondary"]
    n = int(r["four_year_sequences"])
    gap, cont = int(r["recovered_sequences"]), int(r["continuous_sequences"])
    total_lost = int(r["total_recorded_relosses"])
    if n <= 0 or gap <= 0 or cont <= 0 or gap + cont != n:
        raise ValueError("Invalid registry")
    a = round(gap * float(s["recovered_reloss_fraction"]))
    c = round(cont * float(s["continuous_reloss_fraction"]))
    if (a + c != total_lost or
        not math.isclose(a / gap, float(s["recovered_reloss_fraction"]), abs_tol=1e-12) or
        not math.isclose(c / cont, float(s["continuous_reloss_fraction"]), abs_tol=1e-12) or
        not 0 <= a <= gap or not 0 <= c <= cont):
        raise ValueError("Frozen count/fraction inconsistency")
    return {"middle_missing_next_missing": a, "middle_missing_next_present": gap - a,
            "middle_present_next_missing": c, "middle_present_next_present": cont - c}


def analyze(cells):
    a, b, c, d = tuple(cells[k] for k in (
        "middle_missing_next_missing", "middle_missing_next_present",
        "middle_present_next_missing", "middle_present_next_present"))
    if any(type(x) is not int or x < 0 for x in (a,b,c,d)):
        raise ValueError("Counts must be nonnegative integers")
    n = a+b+c+d
    if n <= 0:
        raise ValueError("Empty table")
    # Under stationary conditional independent recording with mark-specific p,
    # missing at t+1 and t+3 are exchangeable after two positive observations.
    # For a LOGICAL COMPATIBILITY example only, average the two off-diagonals.
    mean_offdiag = (b+c)/2
    mu = (a+mean_offdiag)/n
    m2 = a/n
    variance = m2-mu*mu
    feasible = bool(0 < mu < 1 and variance >= -1e-12 and m2 <= mu+1e-12)
    mixture = None
    if feasible and m2 > 0:
        q_high = m2/mu
        w_high = mu*mu/m2
        if not (0 <= q_high <= 1 and 0 <= w_high <= 1):
            raise ValueError("Invalid illustrative detection mixture")
        mixture = {
            "conditional_q_low": 0.0, "conditional_q_high": q_high,
            "weight_q_high": w_high, "weight_q_low": 1-w_high,
            "reconstructed_first_moment": w_high*q_high,
            "reconstructed_second_moment": w_high*q_high*q_high,
            "true_occupancy_all_years": "present",
        }
    return {
        "n_sequences_not_independent": n, "cells": cells,
        "middle_missing_count": a+b, "future_missing_count": a+c,
        "offdiagonal_gap_to_detection": b, "offdiagonal_detection_to_gap": c,
        "observed_offdiagonal_asymmetry_count": c-b,
        "stationary_detection_requires_equal_expected_offdiagonals": True,
        "not_a_valid_unclustered_mcnemar_test": True,
        "symmetrized_compatibility_example_not_actual_observations": {
            "a_both_missing": a/n,
            "b_middle_only_missing": mean_offdiag/n,
            "c_next_only_missing": mean_offdiag/n,
            "d_both_present": d/n,
            "mean_q": mu, "second_moment_q": m2,
            "variance_q": variance, "feasible_stationary_heterogeneous_q": feasible,
            "one_exact_two_point_conditional_mixture": mixture,
        },
    }


def repeats_for_detection(p, target_miss=0.05):
    if not (math.isfinite(p) and 0 < p < 1 and math.isfinite(target_miss) and 0 < target_miss < 1):
        raise ValueError("Detection probability and target must be in (0,1)")
    k = max(1, math.ceil(math.log(target_miss)/math.log1p(-p)))
    while (1-p)**k > target_miss+1e-14:
        k += 1
    return {"assumed_independent_single_survey_p": p, "repeat_visits": k,
            "all_miss_probability_given_presence": (1-p)**k}


def derive(source):
    return {
        "schema": "tampa.return_history_exchangeability_audit_v1",
        "evidence_class": "posthoc_descriptive_observation_identifiability_not_mechanism",
        "source": str(DEFAULT),
        "assumption": "True occupancy constant; yearly mark recordings iid Bernoulli(p_i) conditionally on mark-specific time-invariant p_i; condition on year t and t+2 positive.",
        "audit": analyze(cells_from_frozen(source)),
        "independent_revisit_design_illustrations": [repeats_for_detection(x) for x in (.3,.4,.5,.6,.7,.8)],
        "three_visit_p_needed_for_95_percent_cumulative_detection": 1-.05**(1/3),
        "limits": [
            "Observed source and retrospective hypothesis have already been opened; no independent validation.",
            "The same marks contribute overlapping four-year sequences within fixed transects, invalidating an unclustered McNemar p-value.",
            "Offdiagonal equality is a population expectation, not a deterministic observed-count prediction.",
            "Symmetrization is a mathematical compatibility exercise, not a fitted Tampa detection distribution.",
            "Stationary detection heterogeneity is neither established nor refuted from these four counts.",
            "Same-image independent observers estimate recognition reliability, not annual patch encounter probability.",
            "Independent repeated mark surveys assume true within-window closure and detection independence; neither verified.",
            "No new biological transition, demographic recovery, rhizome buffer or conservation intervention supported.",
            "Protect prior four-bay TNC eligibility and frozen confirmatory design.",
        ],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,default=DEFAULT)
    ap.add_argument("--out",type=Path,default=None)
    args=ap.parse_args()
    raw=args.source.read_bytes()
    report=derive(json.loads(raw))
    report["source_sha256"]=hashlib.sha256(raw).hexdigest()
    payload=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")


if __name__=="__main__":
    main()
