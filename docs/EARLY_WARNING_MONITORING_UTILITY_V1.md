# Capacity-limited seagrass watchlist: operational falsification

## Question

The Tampa archive shows retrospective, out-of-time discrimination of next-year **recorded Thalassia absence** when source-year quantitative frequency and Braun–Blanquet state augment a space/time/effort baseline. But recorded-loss events are rare (**19 of 570** scored transect-year cases), and the original comparator omits stable transect identity.

AUC or log-loss improvement does **not** prove that managers with a fixed number of survey visits can find more vulnerable transects.

This post-hoc diagnostic therefore asks:

> Under a fixed annual monitoring budget, does the quantitative-state model capture more subsequently recorded absences than the same model with stable site identity but without source-year quantitative state?

## Existing endpoint cannot be promoted yet

The site-saturated falsification is implemented in `analysis/77_early_warning_site_identity_saturation.py` but was marked **not yet confirmed** in the 2026-10-08 mainline. Its result must be opened and interpreted before asserting within-node early-warning value.

The new audit does not improve or replace that result. If quantitative information fails the node-saturated comparison, an apparently useful top-k watchlist is exploratory operational stratification rather than evidence that **dynamic within-meadow deterioration** is being detected.

## Fixed descriptive comparison

Use **the exact predictions** written by the site-saturated walk-forward script. No refitting, predictor subset changes, re-ranking based on responses, or deletion of 2016.

At each scored target year, rank the same surveyed nodes by existing out-of-time predicted next-year recorded-absence probability. Flag the top 10% and 20% under a fixed per-year visit cap, with integer flooring and at least one flagged node. Compare all four existing arms: space, space+quantitative, node, node+quantitative.

Primary operational contrast is **node+quantitative versus node** at the same actual number of yearly flagged transects. Output integer true captured losses, total alerts, event recall, alert precision, realized alerted fraction and 2016-specific results. All are explicitly **descriptive**, not a fresh confirmatory endpoint.

The nominal 10% and 20% are illustrations, not adopted management budgets. Actual alert fractions are reported because integer node counts may create deviations.

## Interpretation

- **Positive node-saturated discrimination + more captured losses at capacity:** evidence of potentially useful historical prioritization, still requiring external operational validation.
- **Positive discrimination but no additional losses captured:** the predictive improvement has not shown useful prioritization under these capacity choices.
- **No supported node-saturated discrimination:** do not claim changing meadow state warns beyond stable transect risk, regardless of this exploratory top-k audit.
- **Large watchlist turnover but equal captured losses:** monitoring targets are sensitive to model choice without proven improvement.
- **2016 failure dominates:** publish the instability; do not exclude 2016 to rescue the claim.

The result is **not** a measured physiological buffer, confirmed earlier intervention window, true mortality model, or demonstration that remediation is effective.

## Conservation implication

The directly supported retrospective advice is to **monitor quantitative state alongside occurrence** rather than treating binary presence as sufficient. Quantitative state can reveal changes not visible on presence maps.

An algorithmic Amber/Red watchlist based on one-year recorded-loss prediction is a **separate**, higher-evidence claim. It requires independent validation, operational precision and an explicit management utility/cost framework. Until then, quantitative monitoring is justified as **descriptive surveillance**, not as a verified alarm classifier.

## Run

```bash
python analysis/78_early_warning_monitoring_utility.py --self-test
python analysis/78_early_warning_monitoring_utility.py \
  --predictions results/generated_site_warning/early_warning_site_identity_predictions.csv \
  --out results/generated_site_warning/early_warning_monitoring_utility_v1.json
```

The preceding frozen model and source reconstruction must succeed. No empirical capacity-audit result is stored in this document in advance.
