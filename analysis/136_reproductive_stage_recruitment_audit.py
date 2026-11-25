#!/usr/bin/env python3
"""Post-hoc arithmetic from published Kendrick et al. 2023 Tables 3, 4.
DOI: 10.1002/ece3.10456. Not original individual-level data or a model refit.
"""
import json

# Site, cohort, N, confidently local, confidently nonlocal (Table 4).
COHORTS = [
    ("Thomson Bay", 2013, 35, 19, 0),
    ("Stark Bay", 2013, 27, 23, 1),
    ("Parker Point", 2013, 29, 9, 7),
    ("Thomson Bay", 2014, 30, 9, 3),
    ("Stark Bay", 2014, 31, 20, 1),
    ("Parker Point", 2014, 31, 7, 8),
]
# Table 3: exponent b and its published 95% interval for N(age)=a*age**b.
CURVES = [
    ("Parker Point", -.939, -1.087, -.791),
    ("Thomson Bay", -.712, -.869, -.556),
    ("Stark Bay", -.486, -.676, -.295),
]
# Known-source seed individual assignment: N, local, other.
KNOWN_ORIGIN = [("Stark Bay", 110, 100, 0), ("Parker Point", 139, 40, 8)]

def bounds(rows):
    n, local, other = (sum(r[i] for r in rows) for i in (2, 3, 4))
    if n <= 0 or min(local, other) < 0 or local+other > n:
        raise ValueError("Invalid published assignment counts")
    return dict(n=n, local=local, nonlocal_assigned=other,
                unresolved=n-local-other,
                conditional_nonlocal_bounds=[other/n, (n-local)/n])

def analyze():
    sites = sorted({r[0] for r in COHORTS})
    by_cohort = [dict(site=r[0], year=r[1], **bounds([r])) for r in COHORTS]
    pooled = {s: bounds([r for r in COHORTS if r[0]==s]) for s in sites}
    age_doubling = {s: dict(relative_retention=2**b,
                            transformed_exponent_interval=[2**lo, 2**hi])
                    for s,b,lo,hi in CURVES}
    # Break-even arithmetic ONLY, not a fitted multi-species mechanism:
    # if a disturbance reduces fruit supply to 65%, conditional downstream
    # survival must rise by 1/0.65 for equal final recruitment, other things equal.
    result = dict(
        status="published_table_arithmetic_only",
        source_doi="10.1002/ece3.10456",
        by_cohort=by_cohort, pooled=pooled,
        age_doubling_retention=age_doubling,
        known_origin_assignment=[
            dict(site=s,n=n,local=local,nonlocal_assigned=other,
                 unresolved=n-local-other,nonlocal_assigned_fraction=other/n)
            for s,n,local,other in KNOWN_ORIGIN],
        illustrative_break_even_survival_multiplier=1/.65,
        limitations=[
            "Bounds condition on all confident assignments being correct; not statistical confidence intervals or calibrated true migration bounds.",
            "Known-origin Parker Point seeds have 8/139 nonlocal assignments; classification differs by site.",
            "Pooled conditional bounds overlap for Parker Point and Stark Bay.",
            "Age doubling ratios are transformed published curve exponents, not new survival estimates or simultaneous intervals.",
            "Seedling cohorts, adult genets, reproductive density and disturbance are not linked individual experimental units.",
            "Break-even is algebra, not a fitted cross-study effect."
        ])
    assert sum(r["n"] for r in by_cohort)==183
    assert pooled["Parker Point"]["unresolved"]==29
    assert pooled["Stark Bay"]["unresolved"]==13
    assert pooled["Parker Point"]["conditional_nonlocal_bounds"][0] < pooled["Stark Bay"]["conditional_nonlocal_bounds"][1]
    assert age_doubling["Parker Point"]["relative_retention"] < age_doubling["Stark Bay"]["relative_retention"]
    return result

if __name__=="__main__":
    print(json.dumps(analyze(),indent=2,sort_keys=True))
