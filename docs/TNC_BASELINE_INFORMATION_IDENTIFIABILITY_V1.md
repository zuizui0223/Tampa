# Pre-outcome TNC anchor study: baseline information/measurement boundary

## Why this audit exists

The frozen Tampa decisive primary is:

```
future_BB_anchor ~ baseline_BB_anchor + within_node_centered_anchor_TNC + node_fixed_effect
```

It asks if measured rhizome TNC predicts future local Braun–Blanquet (BB) state beyond the *recorded* current BB class and persistent node identity. This is a legitimate **incremental prediction** estimand.

It does **not**, by itself, establish that TNC is a causal reserve buffer, or even that TNC carries future information beyond the **latent true current local plant state**. The measured baseline is a coarse ordinal score, not error-free current plant biomass/condition. A TNC measurement correlated with true current condition may be a second proxy for current condition.

No future Tampa TNC or BB outcome has been opened by this audit. No primary model, field geometry, assay gate, intervention, or support rule changes.

## Simple counterexample

Let local measured reserve `T` be correlated with **true current** physiological state `Q`. Assume that the true future state follows the current state plus noise and that TNC has **zero additional biological effect** conditional on Q:

```
Q = rho*T + sqrt(1-rho^2)*U
B0 = Q + measurement_error
Yfuture = Q + new_noise
```

With standardized T and Q and classical independent baseline measurement-error variance `s2`, the population coefficient of T in the linear regression `Yfuture ~ B0 + T` is:

```
beta_T = rho*s2 / (1 + s2 - rho^2)
```

For `rho > 0` and `s2 > 0`, this is **positive despite a zero TNC mechanism**. Stable-node fixed effects do not remove *within-node* unresolved true condition. Ordinal BB coarsening also leaves within-class current-state information unmeasured even with a perfectly consistent observer.

This example is a measurement/identifiability fact, not a claim about Tampa's actual reader error or biological effect.

## Response-free matched-design simulation

Code: `analysis/79_tnc_baseline_information_stress_test.py`

The **illustrative**, deliberately uncalibrated known-truth simulation uses:

- 38 stable nodes × three anchors (114 anchor rows);
- independent within-node predictors and a shared node intercept;
- correlation of TNC proxy with true current local state `rho=0.6`;
- latent future condition equal to true current condition plus independent noise;
- **no direct or lagged TNC effect**;
- five-class *stylized* ordinal current/future measurements; deliberately not calibrated to Tampa BB category frequencies;
- fixed random seed, 1,200 replays, unchanged fixed-node model.

For transparency, the **mean fitted TNC coefficient** in these synthetic scenarios was:

| Baseline representation | Mean coefficient |
|---|---:|
| Exact latent current state (infeasible ideal) | +0.001 |
| Ordinal current state, no reader error | +0.045 |
| Ordinal current state, independent reader error | +0.308 |
| Mean of two independently noisy readers | +0.192 |

These numeric values are specific to synthetic assumptions and **must never be used as empirical Tampa bias corrections, p-values, power estimates, or mechanistic effect sizes**. The resulting coefficients are on a stylized ordinal-score scale, not measured mg/g-TNC units or observed Tampa BB effect scales. More than one independent baseline reading can attenuate reader error but does not eliminate ordinal coarsening.

## What this changes scientifically

The frozen primary tests:

> Does TNC carry incremental predictive information beyond *measured* current local BB score within the same stable transect?

An eventual supported positive result would **not** distinguish the following two mechanisms without further evidence:

1. TNC reflects a biologically relevant reserve contributing to future resistance or growth.
2. TNC is a more informative proxy for the current latent within-class local meadow condition that BB incompletely measures.

Both produce legitimate measured-state prediction. Only the first supports a reserve-buffer explanation.

This distinction is particularly important when claiming that a "hidden biological carrier" has been identified rather than that a predictive biomarker has been found.

## Low-disruption measurement recommendation (prospective, not an amendment)

Before first outcome-bearing baseline collection, assess feasibility with monitoring partners for one **blinded second BB reading** or archived standardized quadrat photo at the already-frozen q25/q50/q75 meter marks, taken without extra destructive sampling. Preserve the original BB as the authoritative primary predictor and keep the second reading as **QC context only**, never a post-outcome replacement for baseline BB.

- Blind the second observer to TNC values, prior BB class where practical, and all future endpoints.
- Freeze the replicate protocol, completeness rules and data schema before baseline outcome-bearing fieldwork; if not feasible, do not manufacture ratings.
- Quantify reader agreement and disagreement by BB class in a response-independent report; do not use later biological outcomes to choose a preferred observer or to recode the primary BB.
- Agreement is **not** proof that the ordinal class exhaustively captures latent true current state; the remaining coarsening issue should stay in the manuscript's causal-interpretation boundary.

Leaf N/P, meristem state, same-meter depth and other existing secondary diagnostics remain distinct; this proposal does **not** replace the frozen within-node TNC primary, the predeclared depth sensitivity, or the broader field campaign.


## Real upstream interobserver calibration: no fabricated error variance

A separate, publicly released and version-pinned measurement dataset can test whether actual Tampa Bay survey teams disagree on Thalassia Braun–Blanquet assessments:

- upstream: `tbep-tech/seagrasstransect-training-reports`, commit `9b90538998a0707ddafc13075c1b4715e5fb3290`;
- source: `data/trndat.rda`, verified Git blob `0335f81880001524541dc66083be9a02b77daa95`;
- program: Tampa Bay interagency training, in which agencies independently assess **the same calibration quadrats**;
- period fixed for this descriptive audit: 2024–2026;
- taxon/measurement: exact `Species == "Thalassia"` and `var == "Abundance"`.

The actual Braun–Blanquet categories are `0, 0.1, 0.5, 1, 2, 3, 4, 5`, i.e. **eight ordinal category positions**, not the five stylized ordinal categories in the known-truth illustration above. The latter is a mathematical counterexample; it was never claimed as an empirical reconstruction of the Tampa observation process.

`analysis/80_thalassia_bb_intercalibration_external.R` verifies the upstream Git blob, preserves these eight categories, and pairs *independent group ratings at exactly the same calibration quadrat and year*. It reports annual total group-pair counts, exact and within-one-category agreement, mean absolute ordinal category difference and explicit-zero-versus-positive disagreement. Unknown or missing species reports are **not** imputed to absence.

No calibration agreement estimates are inserted into this report before actually running the script. The R/CI output is an aggregate descriptive **measurement-layer diagnostic**, not a model of TNC or next-year meadow state.

### Important limitations

1. Training quadrats are not the focal q25/q50/q75 permanent meter marks in the proposed prospective TNC study. They may underrepresent difficult sparse-patch conditions.
2. Multiple agency pairs within one site/year share observations; pair counts are not independent ecological sample sizes.
3. Cross-group consensus is not an external truth standard. All agencies could agree on a systematically imperfect BB class.
4. Raw BB class is ordinal and must never be translated into percent cover or a normally distributed additive error merely from this calibration.
5. Field-calibration agreement alone cannot identify how much of a future TNC coefficient reflects truly depleted storage versus unmeasured current local condition.

This constitutes a **more empirical test of measurement reliability**, not a new ecological endpoint, a transfer-valid error correction, or an amendment of the frozen TNC primary.

## Separate ecological sign ambiguity: carbohydrate stock is not growth by definition

A published multi-region study of *Thalassia testudinum* found **negative associations between tissue nutrient status and rhizome carbohydrate content**, including in Tampa Bay (reported regional Spearman rho about -0.2). Higher carbohydrate can reflect reserve accumulation when growth is limited by nutrients, not necessarily greater net growth or resistance (https://www.sciencedirect.com/science/article/abs/pii/S0304377012000204).

This reinforces the role of the already-frozen leaf N/P diagnostic. It must be described alongside future positive or negative reserve associations, but must not be added to or substituted for the original confirmatory model after outcomes are opened. The prospective ecological choice remains **buffer versus current-state proxy / allocation regime**, not simply whether stored carbon is numerically high.

## Gate for honest interpretation

- Primary unsupported: do not rescue it with duplicate-reader BB, post-hoc continuous proxies, alternate TNC transformations or a cross-node result.
- Primary supported: report *predictive augmentation beyond measured ordinal baseline* first; label buffering causal interpretation unresolved without direct dynamic/process evidence.
- Primary supported and temporal event->reserve->future-state chain also supported independently: stronger consistency with reserve-buffer depletion, but observational common-cause explanations still need consideration.
- No duplicate reading feasible: report measurement resolution as an explicit limitation, not an excuse to reinterpret an outcome after inspection.

## Reproduce without ecological outcome data

```bash
python analysis/79_tnc_baseline_information_stress_test.py --self-test
python analysis/79_tnc_baseline_information_stress_test.py
```

The report is a **pre-outcome interpretation audit**, not a new preregistered ecological endpoint, not a rescue simulation of historical memory, and not a license to reopen closed retrospective Tampa analyses.
