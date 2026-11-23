# Tampa: return-history exchangeability and new-observation gate (2026-11-24)

**Evidence class:** Post-hoc logical observation-process audit; no new biological outcome fit. This extends PR #167 and leaves PR #166 and the frozen TNC programme intact.

## Frozen 2 by 2 table

All four-year sequences are observed Thalassia-positive at t and t+2. Source: results/return_fragility_v1.json; 580 eligible overlapping sequences, 21 stable nodes. O denotes a recorded state, **not true demographic occupancy**.

| O(t+1) | O(t+3) absent | O(t+3) present | Total |
| --- | ---: | ---: | ---: |
| absent | 30 | 53 | 83 |
| present | 64 | 433 | 497 |
| total | 94 | 486 | 580 |

The original higher recorded-loss rate after a gap is retained (30/83 = 36.14% vs 64/497 = 12.88%). A different observable implication is that the two discordant transition counts are 53 versus 64 (difference 11).

## New falsification boundary: stationary detection must be exchangeable in expectation

Suppose every true mark remains occupied for all four years. A mark i has a time-invariant effective annual recording probability p_i; annual observations are independent conditional on p_i. Conditioning on positive recordings at t and t+2, annual O(t+1) and O(t+3) are exchangeable. Hence the *expected* off-diagonal counts must agree, although actual counts need not. The observed 53 versus 64 do **not** constitute a cluster-valid hypothesis test: four-year sequences share meter marks and nodes, often with overlapping windows, and this check was formulated after the outcomes were known.

For an exact compatibility illustration only, symmetrize 53 and 64 to 58.5 each, leaving the diagonal counts unchanged. For the resulting hypothetical exchangeable table, conditional on two positives:

- Mean yearly failure probability mu = (30+58.5)/580 = **0.152586**.
- Second moment E(q squared) = 30/580 = **0.051724**.
- Variance of q=1-p = E(q squared) minus mu squared = **0.028442**.
- Since mu squared <= E(q squared) <= mu, a stationary non-degenerate distribution of effective mark-specific failure probabilities can generate *exactly this symmetrized table*.
- An explicit two-point conditional mixture is q_low = 0 and q_high = E(q squared)/mu, with high-q mixing weight mu squared/E(q squared). The code reproduces both moments exactly. All true organisms stay present.

This is an *existence proof*, not fitted Tampa recording probabilities, not evidence of a stationary detection process, and not a claim that the unsymmetrized observed 53 and 64 should be identical. The historical contrast remains identified only at **recorded-state** level. The data do not prove biological recovery debt.

## How much independent observation is theoretically needed?

Conditional on truly occupied status and independent survey-specific recording probability p, the probability all K repeat surveys miss the species is (1-p) to the power K.

| Assumed per-survey p | K needed for <=5% all misses |
| ---: | ---: |
| 0.3 | 9 |
| 0.4 | 6 |
| 0.5 | 5 |
| 0.6 | 4 |
| 0.7 | 3 |
| 0.8 | 2 |

Three independent observations only exceed a 95% cumulative detection probability if p >= **0.6316**. None of these p values is estimated for Tampa; this is *conditional* design arithmetic, not a powered sample-size calculation. No number of repeats can substitute for missing true mark identity or eliminate all dependence if observations are correlated.

## Response-independent future audit (non-invasive)

1. **Reconcile identity first.** Preserve exact sampled meter marks, quadrat footprint, observer, survey time, sampled-zero versus unsampled, GPS/photo metadata, and coverage of the original marks. Missing visits must not become zeros.
2. **Separate observer error and patch encounter.** Independent blind classification of the exact same registered photo measures recognition/classification error, not independent patch encounter. Repeat truly independent surveys of the same fixed frame during an independently justified short closure window to estimate within-window detection. Additional offset subquadrats are *spatial subunits*, not repeated detections of the identical footprint.
3. **Control observer/time confounding.** Rotate observers, randomize order, and retain dates and environmental conditions; check whether the effective recording process changes by season.
4. **Freeze before future outcomes.** Specify K, closure window, mark roster, detection and coverage definitions, missingness, future quantitative BB/shoot endpoint and node-level holdouts before seeing next-year results.
5. **Compare models prospectively.** A static true-occupancy + heterogeneous mark-detection process is the null reference; compare with a dynamic latent occupancy model that uses genuine repeat observations. Add independent rhizome TNC only if it has been measured before future outcomes; predictive improvement alone does not prove biochemical causation.

**Existing frozen TNC study has priority.** Historical feasibility is 41 recent Thalassia-positive nodes across four bays; 38 nodes have 3 distinct quantitative q25/q50/q75 baseline anchors (114 historical anchors). These are NOT approved contemporary sites. The separate TNC-v2 primary requires >=36 analyzable nodes, >=6 per bay, one synchronized <=28-day campaign, lab pilot and sampling permits. Project documentation currently reports STOP_RESOURCE_FREEZE_INCOMPLETE. An optional detection pilot must not alter that registration or consume its outcome-bearing field budget.

## Prior work and novelty

Detection-adjusted dynamic occupancy and repeat-survey designs are already established: MacKenzie et al. (2003), Ecology 84:2200-2207 (https://doi.org/10.1890/02-3090); MacKenzie & Royle (2005), Journal of Applied Ecology 42:1105-1114 (https://doi.org/10.1111/j.1365-2664.2005.01098.x). Seagrass-Watch monitoring guidance (https://www.seagrasswatch.org/seagrass-monitoring/) documents permanent-transect designs and seasonal consistency. None is direct confirmation about Tampa.

## Reproduction

- analysis/111_return_fragility_exchangeability_audit.py: standard-library only; builds counts exclusively from the frozen canonical summary, creates conditional moment witness and independent-repeat effort table.
- validation/test_return_fragility_exchangeability_audit.py: source/count fail-closed and mathematical tests.
- .github/workflows/return-fragility-exchangeability-audit.yml: inspectable output and exact current source digest.

No new ecological result, true mortality, demographic recolonization, biological hysteresis, TNC buffering or intervention efficacy is claimed.
