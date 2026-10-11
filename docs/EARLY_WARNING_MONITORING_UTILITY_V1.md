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

**Eligibility / prospective deployment limit.** Historical scored rows are conditional on a source-positive transect being **resurveyed in the immediately next calendar year**. This fact is known for the retrospective evaluation, but not necessarily when a manager would issue a forward-looking watchlist. Ranking only these scored rows therefore does not test full-network prospective deployment, where future survey participation, missing visits, inaccessible nodes and unit-level cost are additional unknowns. It is best called a *conditional follow-up audit*, not an implemented annual surveillance program. No missing target survey is imputed to persistence or loss.

**Scale / units.** The index uses annual transect-level recorded absence (zero focal sampled marks), not permanent metre-mark demographic extinction. Sampled point counts vary; low frequency could predict non-detection through finite sampling as well as biological state. The model does not separate those processes.

## Biological-process boundary: a no-change detection-floor null

There is a simpler reason that low source-year focal frequency can predict next-year *recorded absence*, even when there is **no real biological deterioration** between years.

If every sampled mark independently detects focal seagrass with constant probability `p` and `n` marks are sampled next year, the probability of zero recorded detections is

```text
P(no recorded Thalassia at next visit | p, n) = (1 - p)^n.
```

For two illustrative **constant** focal occupancy probabilities corresponding approximately to the previously reported median source frequencies of historically lost and persistent groups (`p = 0.0627` vs `0.3022`), and a hypothetical `n=20` independent sampled marks, this detection-only probability is approximately **27.4% versus 0.075%**, despite an unchanged biological state in both cases.

**These numbers are not Tampa estimates of false absence rates.** Actual transect marks are spatially structured and often revisited, conditional detection is not independent, p is measured with finite sampling and a different n, the source groups were defined retrospectively by their later outcomes, and survey schedules/effort can change (notably around 2016).

This analytical counterexample establishes a crucial inferential limit: lower observed source frequency can increase risk of next-year recorded absence **without any decrease in latent occurrence or abundance**. Out-of-time improvement of a frequency-based classifier by itself therefore supports *forecasting a recorded observation transition*, but not a biological condition-to-loss mechanism, an extinction warning, or a measured lead time for habitat decline.

A biological early-warning claim would require external detection-aware observations (e.g. repeat surveys or robust plot-level occupancy/abundance evidence of true change), not reinterpretation or retuning of the existing annual predictor. No further post-hoc occupancy-parameter grids are authorized in this descriptive operational audit.

## Interpretation

- **Positive node-saturated discrimination + more captured losses at capacity:** evidence of potentially useful historical prioritization, still requiring external operational validation.
- **Positive discrimination but no additional losses captured:** the predictive improvement has not shown useful prioritization under these capacity choices.
- **No supported node-saturated discrimination:** do not claim changing meadow state warns beyond stable transect risk, regardless of this exploratory top-k audit.
- **Large watchlist turnover but equal captured losses:** monitoring targets are sensitive to model choice without proven improvement.
- **2016 failure dominates:** publish the instability; do not exclude 2016 to rescue the claim.

The result is **not** a measured physiological buffer, confirmed earlier intervention window, true mortality model, or demonstration that remediation is effective.

## Conservation implication

The directly supported retrospective advice is to **interpret quantitative state alongside occurrence** rather than treating binary presence as sufficient. Quantitative state can reveal changes not visible on presence maps. This is **not a new monitoring protocol**: the existing Tampa Bay Interagency Seagrass Monitoring Program already measures canopy height, short-shoot density, abundance/cover and species frequency along annual transects, alongside biennial aerial-extent assessments (https://tampabay.wateratlas.usf.edu/seagrass-monitoring/). The unresolved contribution is whether these already collected signals support genuinely better prospective targeting of *recorded* losses beyond stable site vulnerability.

An algorithmic Amber/Red watchlist based on one-year recorded-loss prediction is a **separate**, higher-evidence claim. It requires independent validation, operational precision and an explicit management utility/cost framework. Until then, quantitative monitoring is justified as **descriptive surveillance**, not as a verified alarm classifier.

## Run

```bash
python analysis/78_early_warning_monitoring_utility.py --self-test
python analysis/78_early_warning_monitoring_utility.py \
  --predictions results/generated_site_warning/early_warning_site_identity_predictions.csv \
  --out results/generated_site_warning/early_warning_monitoring_utility_v1.json
```

The preceding frozen model and source reconstruction must succeed. No empirical capacity-audit result is stored in this document in advance.
