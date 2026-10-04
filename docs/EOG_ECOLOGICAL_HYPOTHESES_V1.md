# EOG → Tampa ecological hypotheses v1

## Why this exists

The frozen Tampa EOG endpoint was adverse: adding the EOG Layer-B representation increased heldout log loss. A response-independent audit later showed why the representation was structurally suspicious in Tampa: all five declared worlds survived, and the prediction-facing Layer-B state collapsed to an injective, static node-level geography/topology signature reused across repeated visits.

That is a modelling result. This document asks the ecological question that follows from it:

> **If static regional geometry is not the changing biological signal, what kind of ecological state is actually changing in Tampa Bay seagrass?**

This is a post-hoc hypothesis document. It does not repair or reclassify the consumed EOG endpoint.

## New ecological result 1 — the monitored state hierarchy has two very different temporal characters

Using the 1,480 annual transect-years, stable transect identity alone accounts descriptively for:

- recorded *Thalassia* detection: **R² = 0.823**
- focal frequency: **R² = 0.874**
- Braun–Blanquet all-point state: **R² = 0.862**
- blade length: **R² = 0.259**
- shoot density: **R² = 0.232**

Year alone accounts for only about **1–3%** of detection/frequency/Braun–Blanquet level variation, but about **13.6%** of blade-length and **9.3%** of shoot-density variation.

This is not a causal variance partition. It nevertheless exposes a strong state hierarchy:

> **where the meadow is and its long-run occupancy/abundance level are highly site-anchored, while plant condition is much more temporally labile.**

This fits the already observed post-2016 decoupling: a transect can remain recorded-positive while stature, density or within-transect occupancy deteriorates.

## New ecological result 2 — simply making the spatial signal dynamic does not rescue it

A direct ecological translation of the EOG failure was tested.

For every target year, the previous year's state of other Tampa transects was recomputed within the four frozen EOG radii:

- 14.91 km
- 23.93 km
- 34.71 km
- 43.48 km

The baseline already contained stable node identity, geography, year and the focal transect's own lag-1 state. The augmented model added the annually refreshed neighborhood state.

### Recorded detection

- baseline log loss: **0.15708**
- + dynamic neighborhood: **0.16079**
- mean delta: **+0.00371** (worse)
- neighborhood wins: **12/22** target years
- one-sided sign-flip Monte Carlo p: **0.692**

### Focal frequency

- baseline MAE: **0.04702**
- + dynamic neighborhood: **0.04797**
- mean delta: **+0.000953** (worse)
- neighborhood wins: **7/22**
- p: **0.991**

So the EOG problem is not obviously fixed by replacing static geometry with this simple annually refreshed neighborhood state.

## New ecological result 3 — the missing annual signal is not simple segment synchrony or local propagation

The previous dynamic-neighborhood test added all four spatial summaries at once. To separate spatial scales, a frozen follow-up decomposed previous-year context into:

1. the leave-one-node-out mean state of the focal transect's **water-body segment**; and
2. the **local neighborhood deviation** from that segment mean.

Stable node identity and the focal transect's own lag-1 state were already in the reference.

At the primary frozen EOG radius of **23.93 km**:

- focal frequency: segment state worsened mean MAE from **0.04724 to 0.04763** (p = **0.927**), and local deviation worsened it further to **0.04843** (p = **0.9993**);
- Braun–Blanquet state: segment state changed mean MAE from **0.16831 to 0.16805** but was unsupported (p = **0.257**), while local deviation worsened it to **0.16979** (p = **0.9989**).

Across all four frozen radii, no segment or local-neighborhood increment passed the declared support rule for either outcome.

The useful ecological boundary is therefore narrower than “regional state does not matter.” Rather:

> **once persistent site identity and the meadow's own recent state are known, a simple previous-year spatial average—whether segment-wide or local—does not explain the remaining annual variation.**

Shared forcing may still exist, but it may be event-scale, nonlinear, asynchronous among sites, or mediated by persistent local habitat properties rather than by one-year spatial propagation.

## New ecological result 4 — simple bathymetry and sediment do not recover the stable-site effect

The persistent-site hypothesis was next made more concrete. Before reopening any focal response model, a response-independent physical preflight showed that all **71** stable transects had point-depth observations and sediment information. Depth was densely sampled (median **492** point observations per covered node; minimum **18**), and sediment resolved to five normalized classes. Thirty-nine point events with conflicting sediment labels were excluded.

The outcome model was then frozen before opening this result. Each stable node's long-run *Thalassia* state was predicted under leave-one-node-out validation from:

- reference: water-body identity + longitude + latitude;
- measured template: reference + depth median/IQR + modal sediment + sediment dominance/entropy.

The measured-template increment was unsupported for every primary state dimension:

- detection prevalence: MAE **0.2174 → 0.2268**, p = **0.731**;
- focal frequency: **0.1347 → 0.1483**, p = **0.977**;
- Braun–Blanquet state: **0.4673 → 0.4796**, p = **0.693**.

Thus the persistent node effect cannot be reduced to the tested depth and sediment summaries.

This negative result matters because it rules out the easiest physical interpretation of `node_id`. The next candidate components are therefore less static/simple: **benthic light climate, chronic water clarity, hydrodynamic exposure/residence time, fine-scale chronic water-quality regime, below-ground meadow reserves and clonal legacy**, plus their interaction with episodic stress.

## New ecological result 5 — the bulk benthic-light proxy is also insufficient

Light remains a biologically strong candidate in Tampa Bay, but the relevant question is whether the available monitoring data recover the light signal at the scale of individual transects.

A response-independent preflight combined visit depth with monthly segment Secchi to estimate a simplified pre-survey benthic-light fraction. The six-month exposure was available for **1,236 visits across 57 nodes and 28 years**, spanning **0.082–0.989**.

The outcome test was deliberately stringent. The reference already contained stable node identity, water body, year, survey timing, effort, depth and bulk Secchi. The augmented model added only the nonlinear light-at-depth proxy.

Neither primary plant-condition outcome was supported:

- blade length: **6.7684 → 6.7668 mm MAE**, p = **0.468**;
- shoot density: **173.86 → 175.13 shoots m⁻² MAE**, p = **0.945**.

The three-month sensitivity and the quantitative frequency/abundance outcomes were also unsupported.

This is consistent with recent Tampa Bay synthesis showing that substantial post-2016 seagrass loss occurred even while segment-scale light environments were broadly considered supportive of growth. The remaining mechanism may therefore depend on **local optical heterogeneity, compound event-scale stress, below-ground reserve state, or interactions among these factors**, rather than a simple bay-segment light deficit.

## New ecological result 6 — even the published joint hot–fresh duration does not explain plant condition

A final climate-stress rescue hypothesis asked whether the earlier temperature and salinity screens failed because they treated the stressors separately. Rather than inventing another index, the test reused the exact published Tampa Bay daily-GAM reconstruction from Beck et al. (2024).

The exposure series covered all four major bay segments from **1997–2022**. The published thresholds were **temperature ≥ 30 °C** and **salinity ≤ 25 ppt**. Joint hot–fresh exposure was common enough to test: about **58%** of segment-years had non-zero overlap, with strong contrasts among segments.

The outcome design then controlled the marginal hot-run and fresh-run durations and asked whether their **simultaneous overlap duration** added information.

It did not:

- blade length: MAE **6.332 → 6.433**, 5/19 yearly wins, p = **0.996**;
- shoot density: **186.28 → 188.67**, 7/19 wins, p = **0.741**;
- focal frequency and Braun–Blanquet state were also unsupported.

This matters because it closes an obvious explanation for the earlier null screens: the missing signal is not recovered simply by combining hot and fresh conditions into the published threshold-overlap metric.

The current retrospective evidence therefore points away from further tuning of broad water-quality stress indices. Mechanistic progress now requires **new state information**—especially meadow-scale high-frequency physical exposure, epiphytes/light at the canopy, below-ground carbohydrate/rhizome state, or acute disturbance/disease observations.

## Ecological hypothesis H1 — persistent site template + unresolved slow state

**Hypothesis.** Persistent local site properties and unmeasured slow biological states help structure long-run *Thalassia* occurrence/abundance, while plant condition and community composition can vary more rapidly and need not move in a single ordered sequence.

Simple depth/sediment summaries, a segment-Secchi × visit-depth benthic-light proxy, the published 30 °C / 25 ppt joint hot–fresh duration, and simple annual neighborhood state have been tested without recovering the unresolved site/condition signal. Remaining candidates require genuinely new information: measured rhizome reserve/regenerative state, direct within-canopy optical exposure, node-scale event forcing, hydrodynamics, rhizosphere chemistry, acute disturbance or disease.

### Existing evidence consistent with H1

- stable node identity strongly structures detection, frequency and Braun–Blanquet levels;
- blade length and shoot density are far less site-saturated;
- older-history prediction loses formal support after node identity is added;
- simple dynamic-neighborhood, segment-state and local-neighborhood augmentations add no supported year-ahead information;
- direct depth/sediment, coarse light and coarse hot/fresh screens do not explain the unresolved local template.

### Prospective discriminating predictions

1. directly measured slow state such as rhizome TNC should predict future quantitative change beyond current above-ground state if it is a relevant hidden state;
2. within-node anchor TNC and recent reserve trajectory provide stricter tests against a purely time-invariant transect template;
3. direct within-canopy DLI or node-scale event exposure may predict reserve change if short-timescale forcing updates that slow state;
4. none of these predictions requires blade length or shoot density to decline before frequency.

## Ecological hypothesis H2 — low quantitative state predicts recorded loss, but the transition mechanism is unresolved

**Supported pattern.** Source-year focal frequency and Braun–Blanquet state contain information about next-year recorded *Thalassia* loss.

This supports a monitoring statement:

> a transect can be recorded present while its local quantitative state already indicates elevated risk of later non-detection.

It does **not** establish a deterministic biological threshold, a condition → thinning cascade, or extinction/recolonization.

A frozen cross-lag test found that source blade length and shoot density did not add robust one-year-ahead information about next-year frequency or Braun–Blanquet state beyond current quantitative state and stable node identity.

### Predictions / boundaries

1. local quantitative frequency/abundance should remain more useful for next-year recorded loss than the tested regional accessibility metrics;
2. nonlinear loss-risk shapes may be described if prespecified, but no critical ecological threshold is currently identified;
3. plant condition, focal abundance and community composition are treated as partially distinct state axes rather than obligatory stages;
4. later re-recording is an observation-state return, not demonstrated ecological recovery or recolonization.

## Ecological hypothesis H3 — regional connectivity is saturated for established Tampa meadows

**Hypothesis.** At the scale of these long-established fixed transects, regional accessibility is often not limiting; most sites already belong to a broadly connected potential source network, so annual changes are controlled mainly by local state.

This is the ecological analogue of the EOG observation that all five worlds survived and the support summary became mostly a static node signature.

### Predictions

1. generic distance/connectivity terms and simple previous-year spatial averages will add little after local state and persistent site identity;
2. connectivity should matter more at genuine colonisation/recovery fronts than at continuously occupied established transects;
3. multi-source or local-recruitment representations should be more biologically plausible than an arbitrary single-source anchor, but need not improve prediction if established meadows are locally persistent.

## Ecological hypothesis H4 — multiple degradation pathways converge on the same binary state

The bay segments already suggest different routes:

- **Old Tampa Bay:** declining blade length and shoot density — plant-condition pathway;
- **Middle Tampa Bay:** declining blade length with weak binary change — condition pathway;
- **Lower Tampa Bay:** declining *Thalassia* frequency/Braun–Blanquet plus increasing *Halodule* frequency — spatial/compositional pathway.

Thus binary occurrence is a compressed endpoint. Different ecological processes can produce the same value `present = 1`.

### Prediction

A useful monitoring framework should treat presence, within-transect occupancy, abundance, morphology/density and community composition as a state hierarchy rather than interchangeable proxies.

## What this suggests mechanistically

The current working model is **state augmentation**, not a serial degradation cascade.

```text
             persistent local site template
                       +
             unmeasured slow state
        (reserve / regenerative / local physical state)
                       |
       +---------------+----------------+
       |               |                |
 occurrence /      plant condition    community
 abundance         morphology/density composition
       \               |                /
        \              |               /
         ---- coarse recorded state ----
                       |
             future state transitions
```

Short-timescale forcing may update one or more slow states, but the annual archive does not establish one universal ordering among the observed axes.

The prospective question is therefore:

> does augmenting the observed state with directly measured slow variables reduce the unexplained future-state information currently carried by stable site identity and history?

Regional neighborhood geometry may still matter during establishment, major-disturbance recovery, or genuine range/front movement. The present data do not support it as the dominant annual predictor for the monitored Tampa transects.

## Claim boundary

- H1–H4 are ecological hypotheses / interpretation frames, not identified causal mechanisms.
- The condition → thinning → threshold-loss sequence is not a current supported mechanism; the frozen cross-lag test was negative.
- Binary re-recording is not ecological recovery or recolonization.
- `node_id` is a placeholder for persistent site differences, not a biological variable.
- The dynamic-neighborhood test covers one annual, four-radius formulation only.
- The EOG failure cannot itself prove clonal buffering, light limitation or local recruitment.
- Future causal work should measure the persistent site template and meadow physiological state directly rather than add more abstract memory/connectivity features or retrospectively tune additional temperature/salinity stress indices.
