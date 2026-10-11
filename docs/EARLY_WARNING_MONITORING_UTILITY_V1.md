# Capacity-limited seagrass watchlist: operational falsification

## Question

The Tampa archive shows retrospective, out-of-time discrimination of next-year **recorded Thalassia absence** when source-year quantitative frequency and Braun–Blanquet state augment a space/time/effort baseline. But recorded-loss events are rare (**19 of 570** scored transect-year cases), and the original comparator omits stable transect identity.

AUC or log-loss improvement does **not** prove that managers with a fixed number of survey visits can find more vulnerable transects.

This post-hoc diagnostic therefore asks:

> Under a fixed annual monitoring budget, does the quantitative-state model capture more subsequently recorded absences than the same model with stable site identity but without source-year quantitative state?

## Completed original reference-saturation result

The [original site-saturated falsification](../results/early_warning_site_identity_saturation_v1_contract.json) was fixed as a post-hoc reference audit before this monitoring-utility extension, and succeeded on [GitHub Actions #38109049710](https://github.com/zuizui0223/Tampa/actions/runs/38109049710).

| Matched frozen reference | Pooled AUC | Macro target-year log loss |
|---|---:|---:|
| node identity + space/time/effort | 0.67055 | 0.148268 |
| node identity + same reference + frequency/BB | 0.73636 | 0.147230 |

The node+quant arm won **17 of 23** target years; the one-sided sign-test p was **0.01734**, and the frozen support rule passed. The macro log-loss increment is small (**-0.001037**); 2016 was strongly adverse (**+0.30563**, retained).

This establishes **conditional prediction of a future recorded state** beyond the specified L2-regularized node-ID reference, not beyond every possible persistent-site explanation. It does **not** identify active degradation or rule out finite sampling, detection variation or temporally changing local conditions. The entire endpoint remains internally evaluated and outcome-exposed at the research-program level, not independent external validation.

## Fixed descriptive comparison

Use **the exact predictions** written by the site-saturated walk-forward script. No refitting, predictor subset changes, re-ranking based on responses, or deletion of 2016.

At each scored target year, rank the same surveyed nodes by existing out-of-time predicted next-year recorded-absence probability. Flag the top 10% and 20% under a fixed per-year visit cap, with integer flooring and at least one flagged node. Compare all four existing arms: space, space+quantitative, node, node+quantitative.

Primary operational contrast is **node+quantitative versus node** at the same actual number of yearly flagged transects. Output integer true captured losses, total alerts, event recall, alert precision, realized alerted fraction and 2016-specific results. All are explicitly **descriptive**, not a fresh confirmatory endpoint.

The nominal 10% and 20% are illustrations, not adopted management budgets. Actual alert fractions are reported because integer node counts may create deviations.

**Eligibility / prospective deployment limit.** Historical scored rows are conditional on a source-positive transect being **resurveyed in the immediately next calendar year**. This fact is known for the retrospective evaluation, but not necessarily when a manager would issue a forward-looking watchlist. Ranking only these scored rows therefore does not test full-network prospective deployment, where future survey participation, missing visits, inaccessible nodes and unit-level cost are additional unknowns. It is best called a *conditional follow-up audit*, not an implemented annual surveillance program. No missing target survey is imputed to persistence or loss.

**Scale / units.** The index uses annual transect-level recorded absence (zero focal sampled marks), not permanent metre-mark demographic extinction. Sampled point counts vary; low frequency could predict non-detection through finite sampling as well as biological state. The model does not separate those processes.

## Empirical results of historical capacity audit

The same successful run evaluated the frozen 570 matched walk-forward predictions (19 recorded-loss events, 23 years). The annual integer cap yields **47 alerts** for the nominal 10% rule and **105 alerts** for the nominal 20% rule; these correspond to realized **8.25%** and **18.42%** of the scored rows.

| Nominal cap | Fixed-node reference | Node + quantitative state | Additional captured events |
|---|---|---|---:|
| 10% (47 alerts) | **6/19** recorded losses (precision 12.8%) | **9/19** (precision 19.1%) | +3 |
| 20% (105 alerts) | **9/19** (precision 8.6%) | **13/19** (precision 12.4%) | +4 |

The operational advantage occurred without changing the number of flagged transects: 13 annual selections differed at the 10% cap and 35 at the 20% cap. **2016 did not improve at either cap**, with 1/5 recorded losses captured by either model at the 10% or 20% cap.

These are post-hoc **descriptive event capture** counts, not a new significance test. They are potentially useful for prioritizing closer observation of *recorded absence*, but do not quantify preventing losses, treatment efficacy or the benefit of a policy in a fully eligible prospective network.

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

## Fixed-mark revisit falsification of the independent-resampling explanation

The elementary `(1-p)^n` model above **assumes independent new draws of sampling locations**. The actual Tampa monitoring programme uses stable transect identifiers and recurring metre-mark `locationID`s. The fixed-mark geometry provides a sharper discriminating question than the independent-draw example:

> For a transect recorded Thalassia-positive in year t and unrecorded in year t+1, were the **specific metre marks that were Thalassia-positive at t** resampled at t+1?

This is answerable from the source's `Point`-event `locationID` rather than inferred from transect frequency.

Let `P_t` be source-year Thalassia-positive mark IDs and `S_(t+1)` the actually sampled mark IDs in the target year. Define:

```text
m = |P_t ∩ S_(t+1)|
f = m / |P_t|
```

- `m=0`: the original positive marks were not resampled, so a change in the sampling footprint can contribute to recorded disappearance even if those unvisited patches persisted.
- `m>=1`: at least one previously focal-positive mark was re-examined; if the whole transect is unrecorded, the combination of **unchanged local mark occupancy + perfect detection** is contradicted at that mark. This does not distinguish true shoot loss, temporary non-detection, physical shifting of the survey quadrat, or protocol variation.
- `m=|P_t|`: all previously positive marks are nominally revisited. A generic independent-redraw explanation is particularly inappropriate, but source and target detection processes still need direct validation.

`analysis/81_early_warning_fixed_mark_overlap.py` reconstructs the original **688 consecutive source-positive transect transitions with 24 recorded losses**, validates mark-level states against the original annual endpoint, and reports positive-mark revisit overlap for those outcomes, 2016 specifically, and the **exact scored 570/19 walk-forward subset**. It uses the already-frozen point-event reconstruction in `analysis/33_community_buffering.py` and verifies pinned raw-source blob hashes; no new predictor, fitted model, sensitivity-window tuning or biological-response exclusion is allowed.

The audit was authored after the long-term outcomes had already been opened. It is a descriptive assessment of **observation-process plausibility**, not a new preregistered test of seagrass deterioration. The computation is now complete: **17/24** full-cohort losses and **14/19** scored losses revisited at least one former positive mark. The none/some/all partitions were 7/7/10 and 5/7/7. All five 2016 losses had a revisit. In the unchanged lists, revisited-event captures increased 4 to 6 at the 10% cap and 7 to 9 at the 20% cap. These descriptive partitions do not identify mortality or justify reranking. See [the verified report](EARLY_WARNING_FIXED_MARK_VERIFIED_V1.md).

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

The source reconstruction and existing model replay succeeded in GitHub Actions #38109049710; the counts above come from its archived JSON artifact. The fixed-mark audit also succeeded in run 38109944875; Tables S10–S12 and the verified report now contain its result. No new mechanism test was added.
