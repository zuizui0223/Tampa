# TNC complete-triplet fragility: pre-outcome design audit

**Date:** 2026-10-14  
**Evidence:** Response-free arithmetic scenarios only; no measured TNC, HPLC yield, future *Thalassia* outcomes or observed QC attrition.  
**Computed by:** `analysis/82_tnc_anchor_triplet_fragility.py`; frozen-input result `results/tnc_anchor_triplet_fragility_v1.json`.

## Why this is the immediate field-design risk

The current preflight for the **decisive within-meadow TNC model** has **38 nodes** with three historically distinct quantitative q25/q50/q75 meter-mark anchors each:

| Bay | Currently preflighted complete-anchor nodes |
|---|---:|
| Old Tampa Bay | 8 |
| Middle Tampa Bay | 10 |
| Lower Tampa Bay | 12 |
| Boca Ciega Bay | 8 |
| **Total** | **38** |

The frozen confirmatory gate remains **at least 36 complete nodes**, with **at least six in each bay**, and **all three original anchors complete at every included node**. At this exact historical 38-node frame, only **two whole-node losses** are tolerable. The six-per-bay floors follow automatically whenever at most two of these 38 nodes are lost; the stringent bottleneck is the 36-node total.

This **38-node decisive analysis frame** is distinct from the **41-node four-bay network sampling frame** (123 baseline cores if every 41-node site uses three cores). The cross-node supportive analysis cannot rescue a missing within-node decisive primary.

## A deterministic warning: global QC % can be misleading

- The preflight implies **114 needed anchor measurements** across 38 complete candidate nodes.
- Losing one anchor at each of **three distinct nodes** leaves **111/114 = 97.4% valid anchors**, but **35** fully complete nodes: confirmatory gate **FAIL**.
- Losing three anchors in **one** node also leaves **111/114** valid anchors, but **37** complete nodes: confirmatory gate **PASS**.
- A single core, BB record or future aligned mark that becomes invalid makes its entire frozen three-anchor node ineligible under the analysis contract; do not replace or impute it after outcomes.

Therefore QC must be summarized in units of **complete matched three-anchor nodes by bay**, not solely as a percentage of passing HPLC runs or cores.

## Explicit hypothetical independence calculation — not a yield forecast

For demonstration **only**, suppose each of the three anchors has an identical all-requirements-complete probability `p`, independent of the other anchors and across nodes. Then the whole-node completion probability is `q=p³`. In the currently preflighted 38-node frame,

```text
P(confirmatory sample gate) =
    sum_{k=36}^{38} choose(38,k) (p^3)^k (1-p^3)^(38-k).
```

| Hypothetical all-requirements-complete probability per anchor | Expected complete nodes | Probability of reaching 36 of 38 |
|---:|---:|---:|
| 90% | 27.70 | **0.07%** |
| 95% | 32.58 | **7.73%** |
| 97% | 34.68 | **34.37%** |
| 98% | 35.77 | **61.16%** |
| 98.5% | 36.32 | **76.33%** |
| 99% | 36.87 | **89.73%** |
| 99.5% | 37.43 | **98.10%** |

Under *only those* strong full-independence assumptions, a **hypothetical 80%** chance of passing the original gate would require per-anchor full completeness about **98.63%**, and a 90% chance about **99.01%**. These numbers are *not* statistical power to detect a TNC effect and **not empirical targets or adopted QC acceptance thresholds**.

Actual failures may be correlated within nodes, across bays and by preservation/HPLC batch, and actual contemporaneous eligibility may differ from the historical preflight. Even the probability of complete three-anchor data can depart from `p³` when failures cluster; never extrapolate these numeric probabilities directly to Tampa field conditions.

## Method pilot ≠ complete 36-node outcome-bearing readiness

The [existing method-pilot execution card](TNC_V2_PILOT_EXECUTION_CARD_V1.md) requires **at least 9/10** recovery/dry-mass successes from candidate core geometry and an independent HPLC matrix-quality check. Passing these is necessary to choose a workable method; a ten-attempt pilot cannot demonstrate that the later 38×3 full quantitative anchor cohort will be sufficiently complete, particularly when the future same-meter BB outcome is not yet observed.

No frozen field or statistical rule is revised here. Instead, the planning review should check whether the protected full baseline survey, three independently verified anchor identities, high-quality tissue preservation, batch coverage, and future repeat monitoring can plausibly retain at least 36 entire node triplets. Record node-level feasibility **before outcome access**. Missing TNC or future BB is not allowed to be filled from neighboring marks or replaced based on observed effects.

A successful core or HPLC method pilot does **not** guarantee that this narrow cohort-level gate can be met. If it fails later, report the decisive TNC analysis **non-estimable**, regardless of an encouraging network-scale result. The project should not retroactively relax the 36/6 gates, move anchors, or choose favorable surviving sites.

## Reproduction

```bash
python analysis/82_tnc_anchor_triplet_fragility.py --self-test
python analysis/82_tnc_anchor_triplet_fragility.py --out results/tnc_anchor_triplet_fragility_v1.json
```

This audit uses the existing frozen contract `results/clonal_state_augmentation_primary_v1_contract.json` and does not load measured rhizome carbohydrate, fitted ecological outcomes or existing recorded-loss predictions. It is a **risk communication and field QC accounting tool** only.
