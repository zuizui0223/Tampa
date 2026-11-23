#!/usr/bin/env python3
"""Response-free detection-pilot effort sensitivity with stable mark heterogeneity.

For truly occupied marks, p_i is a time-invariant effective annual recording
probability. p_i ~ Beta(alpha,beta) across marks; independent Bernoulli visits
conditional on p_i are marginally correlated with ICC rho=1/(alpha+beta+1).
This is an illustrative planning model, NOT a Tampa-fitted detection analysis.
A separate structural undetectable fraction z gives an asymptotic miss floor.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

PRIMARY_MEANS = (0.4, 0.6, 0.8)
PRIMARY_ICCS = (0.0, 0.1, 0.2)
TARGET_MISS = 0.05
MAX_VISITS = 256


def validate(mean_p: float, rho: float, z: float = 0) -> None:
    if not all(math.isfinite(x) for x in (mean_p, rho, z)):
        raise ValueError("All parameters must be finite")
    if not 0 < mean_p < 1:
        raise ValueError("mean_p must be in (0,1)")
    if not 0 <= rho < 1:
        raise ValueError("rho must be in [0,1)")
    if not 0 <= z < 1:
        raise ValueError("structurally_unrecordable_fraction must be in [0,1)")


def miss_probability(k: int, mean_p: float, rho: float = 0,
                     structurally_unrecordable_fraction: float = 0) -> float:
    """Pr(no detections in k rounds | true occupancy) under a Beta mixture."""
    z = structurally_unrecordable_fraction
    validate(mean_p, rho, z)
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    if k == 0:
        return 1.0
    if rho == 0:
        conditional = (1-mean_p)**k
    else:
        strength = 1/rho - 1
        alpha = mean_p*strength
        beta = (1-mean_p)*strength
        conditional = 1.0
        for i in range(k):
            conditional *= (beta+i)/(alpha+beta+i)
    return z + (1-z)*conditional


def required_visits(mean_p: float, rho: float, target_miss: float = TARGET_MISS,
                    max_visits: int = MAX_VISITS, z: float = 0) -> dict:
    validate(mean_p, rho, z)
    if not math.isfinite(target_miss) or not 0 < target_miss < 1:
        raise ValueError("target_miss must lie in (0,1)")
    if type(max_visits) is not int or max_visits < 1:
        raise ValueError("max_visits must be positive")
    out = {
        "mean_recording_probability_among_recordable_marks": mean_p,
        "conditional_recording_icc_rho": rho,
        "structurally_unrecordable_fraction": z,
        "target_all_miss_probability": target_miss,
        "maximum_considered_rounds": max_visits,
        "asymptotic_miss_probability_floor": z,
        "minimum_rounds": None,
        "status": "UNASSESSED",
        "all_miss_at_three_rounds": miss_probability(3,mean_p,rho,z),
    }
    if z >= target_miss:
        out["status"] = "NO_FINITE_ROUNDS_CAN_MEET_TARGET"
        return out
    for k in range(1,max_visits+1):
        current = miss_probability(k,mean_p,rho,z)
        if current <= target_miss:
            out.update({
                "status": "CONDITIONAL_MATHEMATICAL_TARGET_MET",
                "minimum_rounds": k,
                "all_miss_at_minimum_rounds": current,
                "all_miss_at_one_fewer_round": (
                    miss_probability(k-1,mean_p,rho,z)
                ),
            })
            return out
    out["status"] = "NOT_MET_WITHIN_DECLARED_MAXIMUM"
    out["all_miss_at_declared_maximum"] = miss_probability(max_visits,mean_p,rho,z)
    return out



def posterior_true_presence_after_no_records(
    k: int, mean_p: float, rho: float, prior_true_presence: float,
    z: float = 0,
) -> float:
    """Pr(true presence | k zeros) with perfect specificity and known prior."""
    if not math.isfinite(prior_true_presence) or not 0 < prior_true_presence < 1:
        raise ValueError("prior_true_presence must lie in (0,1)")
    miss = miss_probability(k, mean_p, rho, z)
    return prior_true_presence*miss / (
        1-prior_true_presence+prior_true_presence*miss
    )


def visits_for_posterior_absence(
    mean_p: float, rho: float, prior_true_presence: float,
    target_posterior_presence: float = 0.05,
    max_visits: int = MAX_VISITS, z: float = 0,
) -> dict:
    """Required rounds for illustrative >=95% posterior absence confidence.

    This is *not* estimable for Tampa without an independently defensible
    occupancy prior, specificity and a calibrated recording process.
    """
    if not math.isfinite(prior_true_presence) or not 0 < prior_true_presence < 1:
        raise ValueError("prior_true_presence must lie in (0,1)")
    if not math.isfinite(target_posterior_presence) or not 0 < target_posterior_presence < 1:
        raise ValueError("target_posterior_presence must lie in (0,1)")
    threshold = (
        target_posterior_presence*(1-prior_true_presence)
        / (prior_true_presence*(1-target_posterior_presence))
    )
    if threshold >= 1:
        # Prior presence is already at or below the requested posterior target.
        # Not relevant for monitoring an initially occupied mark.
        return {
            "status":"PRIOR_ALREADY_MEETS_POSTERIOR_TARGET",
            "minimum_rounds":0,
            "prior_true_presence_assumed":prior_true_presence,
            "target_posterior_true_presence":target_posterior_presence,
            "required_conditional_all_miss_probability":threshold,
        }
    d = required_visits(mean_p, rho, target_miss=threshold, max_visits=max_visits, z=z)
    return {
        "status":d["status"],
        "minimum_rounds":d["minimum_rounds"],
        "prior_true_presence_assumed":prior_true_presence,
        "target_posterior_true_presence":target_posterior_presence,
        "required_conditional_all_miss_probability":threshold,
        "conditional_all_miss_at_minimum_rounds":d.get("all_miss_at_minimum_rounds"),
        "posterior_true_presence_at_minimum_rounds":(
            posterior_true_presence_after_no_records(
                d["minimum_rounds"],mean_p,rho,prior_true_presence,z
            ) if d["minimum_rounds"] is not None else None
        ),
    }


def report() -> dict:
    cases=[required_visits(p,rho) for p in PRIMARY_MEANS for rho in PRIMARY_ICCS]
    return {
        "schema":"tampa.detection_revisit_dependence_sensitivity_v1",
        "evidence_class":"response_free_illustrative_measurement_design_not_field_data",
        "primary_grid":cases,
        "structural_unrecordability_example":required_visits(.6,.1,z=.08),
        "posterior_absence_prior_sensitivity_at_mean_p_0_6_rho_0_2": [
            {
                "prior": psi,
                "posterior_true_presence_after_6_zeros":posterior_true_presence_after_no_records(6,.6,.2,psi),
                "rounds_for_posterior_true_presence_at_most_5pct":visits_for_posterior_absence(.6,.2,psi),
            }
            for psi in (.5,.8,.9,.95)
        ],
        "posterior_absence_high_prior_and_lower_detection":visits_for_posterior_absence(.4,.2,.95),
        "interpretation": (
            "Stable across-mark variation in effective p makes same-mark repeat "
            "observations marginally positively correlated; naive independent-repeat "
            "calculations can understate effort. A nonzero p=0 component gives a "
            "lower bound on all-miss probability no finite repeat count can remove."
        ),
        "limitations":[
            "Mean p, ICC and structural-zero values are assumed examples, not Tampa estimates.",
            "Beta random-p heterogeneity and conditional visit independence are model assumptions.",
            "Real same-photo rereads are not independent field revisits.",
            "Repeated observations require independently supported temporary occupancy closure.",
            "A recording probability includes quadrat-footprint mismatch and observer errors; these need separate audits.",
            "This calculation is not power for estimating a latent colonization or extinction parameter.",
            "A 5% conditional all-miss rate is NOT a 95% posterior probability of true absence; posterior absence depends on an unmeasured prior occupancy probability and assumed perfect specificity.",
            "The frozen four-bay TNC primary, mark selections, outcome and permits are unchanged.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=None)
    args=p.parse_args()
    s=json.dumps(report(),ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(s,encoding="utf-8")
    else:
        print(s,end="")


if __name__=="__main__":
    main()
