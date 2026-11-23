# Tampa: known-truth detection-only counterexample to the return-fragility association

**Date:** 2026-11-22  
**Status:** Exact mathematical sufficiency example / no new response fitting / no new causal inference  
**Source:** `results/return_fragility_v1.json`, `results/return_fragility_v1_contract.json` (Tampa main)

## Scientific motivation

The fixed four-year exact-meter-mark result is real *as an observation-level association*: after recorded 1,0,1, the t+3 recorded non-detection is **30/83 = 36.14%**, against **64/497 = 12.88%** after recorded 1,1,1. The adjusted, node-bootstrapped coefficient is **0.320 [0.077, 0.569]** on a standardized covariate, not a direct odds ratio.

**Open biological question:** does this indicate weakened *Thalassia* regeneration after a true loss, or can stable differences among meter marks in the *chance of recording the same species* create the pattern without mortality, recolonization, reserve depletion, temporal shocks or history-dependent biology?

## Exact counterexample: all plants continuously present

Let each meter mark \(i\) be truly occupied at **all four annual observations** and retain one time-invariant recording probability \(p_i\). Conditional on \(p_i\), annual observation \(O_{it}\) is independent Bernoulli\((p_i)\). The probability summarizes imperfect detection, local spatial patch encounter, sampled footprint and effective recording; it is **not estimated in Tampa**.

Compare four-year sequences with \(O_t=O_{t+2}=1\), then classify the middle year as:

- **Gap/re-recorded:** \(O_{t+1}=0\);
- **Uninterrupted:** \(O_{t+1}=1\).

In the population conditioned on \(O_t=O_{t+2}=1\), weights over marks are proportional to prior mark weight \(\times p_i^2\). Write \(q_i=1-p_i\), \(\mu=E_w[q_i]\), \(m_2=E_w[q_i^2]\). Then the conditional next-year absence rates are

\[
 P(O_{t+3}=0\mid O_{t+1}=0,O_t=O_{t+2}=1)=\frac{m_2}{\mu}
\]

and

\[
 P(O_{t+3}=0\mid O_{t+1}=1,O_t=O_{t+2}=1)=\frac{\mu-m_2}{1-\mu}.
\]

Consequently,

\[
 \boxed{\Delta=\frac{\mathrm{Var}_w(q_i)}{\mu(1-\mu)}\geq 0.}
\]

Thus **any nonzero persistent heterogeneity of mark-level recording probability generates a positive re-recorded-group effect**, even though there is no true biological transition. This is an exact selection identity under the stated observational model, not a statistical test on Tampa.

### Simple round-parameter illustration (not calibrated)

Take *prior* across-mark recording probabilities \(p_i\sim\mathrm{Beta}(\alpha=1,\beta=0.5)\) before observing the four-year patterns. Conditioning on two positive observations yields \(\mathrm{Beta}(\alpha+2,\beta)\). Hence:

- Fraction with 1,0,1 among sequences with 1,?,1: \(\beta/(\alpha+\beta+2)=1/7=\mathbf{14.29\%}\).
- Next-year recorded non-detection after 1,0,1: \((\beta+1)/(\alpha+\beta+3)=1/3=\mathbf{33.33\%}\).
- Next-year recorded non-detection after 1,1,1: \(\beta/(\alpha+\beta+3)=1/9=\mathbf{11.11\%}\).
- Difference: **+22.22 points**, ratio **3.00**; all true states remain occupied.
- Gap group share of observed next-year non-detections: **33.33%** (as against Tampa **31.91%**), even though it is only **14.29%** of eligible modeled sequences.

| Statistic | Actual frozen Tampa sequences | Illustrative stationary-detection truth |
| --- | ---: | ---: |
| Re-recorded group fraction | 14.31% | 14.29% |
| Re-recorded next-year non-detection | 36.14% | 33.33% |
| Uninterrupted next-year non-detection | 12.88% | 11.11% |
| Difference | +23.27 pp | +22.22 pp |
| Relative rate | 2.81 | 3.00 |

**The Beta values were selected after looking at the published outcome** as a particularly transparent counterexample; the visual closeness is *not* cross-validation, a likelihood fit, or confirmation that this is Tampa's true observation process. The example demonstrates sufficiency/identifiability failure, nothing more. The real annual recording probabilities and true occupancy histories remain unmeasured. The original adjusted result still supports a *recorded-state instability* association.

## Why a node-fixed-effect model does not close this alternative

A fixed transect node may include many distinct meter marks. The existing model controls `node_id` and return year, but **does not estimate one persistent recording probability per exact mark from independent repeat visits**. Permanent among-mark differences in abundance, placement or detection can therefore retain the same selection effect inside a fixed transect.

The adjacent 701-sequence Braun–Blanquet result (1.95 vs 2.93 after a gap) is biologically interesting, but a low/unstable patch-recording propensity could also correlate with recorded abundance. The separately frozen quantitative-mediation test did **not** establish that return BB drives later recorded loss. These distinct sequence cohorts cannot be merged.

## How to distinguish the two processes using *new independent measurements*

1. **Mark and effort audit before biological outcomes.** Permanent meter/quadrat identity, actual sampled zero vs unsampled, visit date, water conditions, camera images, observer and blade/shoot measurement protocol. Do not impute loss when the mark was not visited.
2. **Short-interval, repeated, independent surveys of the same marks** during a defensible occupancy-closure window. Explicitly measure mark-specific detection/patch encounter and interobserver agreement. Photographic repeat of exactly the same patch is useful but may not separate detector error from spatial patch heterogeneity unless footprint is controlled.
3. **Prospectively distinguish models:** (A) static latent occupancy + heterogeneous \(p_i\); (B) dynamic latent occupancy + heterogeneous \(p_i\) and pre-specified state covariates; (C) add directly measured rhizome reserve or other new physical states only when independently available. All models must address repeated marks within nodes and nonindependent four-year windows. Do not infer transition states from single detection alone.
4. **Hold out actual next-year same-mark outcomes** and compare calibration/log loss under a previously frozen protocol. A biological claim requires improved latent-state prediction beyond the detection-only model, together with direct state measurements; a risk-ranking gain alone is not a regeneration mechanism.
5. **No retrospective rescue:** do not retune the already-opened 2016–2025 four-year events, select new mark subsets based on risk, infer an effective p distribution from the observed 2.81 risk ratio, or label a post-hoc calibration an independent validation.

Occupancy models explicitly separate occupancy from imperfect detection and, in dynamic settings, estimated colonization/extinction (MacKenzie et al., 2002, *Ecology* 83:2248–2255, DOI 10.1890/0012-9658(2002)083[2248:ESORWD]2.0.CO;2; MacKenzie et al. 2003 *Ecology* 84:2200–2207, DOI 10.1890/02-3090). Aquatic-plant occupancy has also been studied with spatial sub-sampling to address imperfect detection (e.g. Nielson et al. 2011, *Aquatic Botany* 95:221–225, DOI 10.1016/j.aquabot.2011.06.004). These are methodological precedents, not claims about Tampa-specific estimates.

## Implication for conservation and novelty

- **Robust ecological result unaffected:** different *Thalassia* axes (plant condition, within-transect frequency and abundance, species composition) diverge under persistent *recorded* occurrence, with post-hoc *Zostera* replication.
- **Retain, but downgrade mechanistic interpretation:** 1,0,1 predicts more 0 next year in the observed panel; this is useful for confirmation sampling, but need not mean a weakened organism or recovery debt.
- **Prospective novelty opportunity:** independently measure whether *the same recorded state* has a different future after accounting for true mark-level recording probability, current quantity and rhizome reserve. If not, publish the observation-selection explanation and change monitoring methods rather than report biological hysteresis.

## Reproduce

This code reads only the frozen canonical `results/return_fragility_v1.json` summary and uses standard-library exact probability identities. It never accesses original individual event-level outcomes.

~~~bash
python -m unittest discover -s validation -p 'test_return_fragility_detection_only_counterexample.py' -v
python analysis/110_return_fragility_detection_only_counterexample.py \
  --source results/return_fragility_v1.json \
  --out /tmp/return_fragility_detection_only_counterexample.json
~~~

This is a separate falsification note. It neither alters `results/return_fragility_v1.json` nor the original manuscript, TNC programme, early-warning endpoint or prospective field contracts.
