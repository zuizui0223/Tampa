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

## Ecological hypothesis H1 — persistent site template + local meadow buffer

**Hypothesis.** Long-lived local habitat properties and meadow legacy stabilize whether *Thalassia* remains established at a transect, while above-ground condition can change substantially before the binary state changes.

Candidate components of the unmeasured site template include depth/light climate, sediment and rhizosphere properties, exposure/hydrodynamics, chronic water-quality regime and long-lived clonal/rhizome structure.

### Existing evidence consistent with H1

- stable node identity strongly structures detection, frequency and Braun–Blanquet levels;
- blade length and shoot density are far less site-saturated;
- older-history prediction loses formal support after node identity is added;
- the simple dynamic-neighborhood augmentation adds no mean heldout benefit;
- decomposing that signal into water-body-wide state and finer local neighborhood deviation still yields no supported increment at any of the four frozen EOG radii.

### Predictions

1. measured persistent habitat variables should explain part of the current node-ID effect;
2. plant-condition variables should respond earlier than binary occurrence to short-term stress;
3. established meadows should often retain presence through periods of declining blade length/density;
4. the strongest spatial predictor of long-run state should be local habitat template rather than distance to one arbitrary source.

## Ecological hypothesis H2 — local degradation crosses a recorded-state threshold

**Hypothesis.** Many recorded losses are the endpoint of local meadow thinning or condition decline, not an annual failure of regional accessibility.

This is directly motivated by the existing early-warning result: source-year frequency and Braun–Blanquet state contain information about next-year recorded loss.

### Predictions

1. local quantitative condition should outperform regional accessibility metrics for next-year recorded loss;
2. loss risk should rise nonlinearly at low local frequency/abundance;
3. some apparent loss/return sequences should represent local thinning, detection and recovery rather than extinction/recolonization;
4. a threshold model of local state should be more useful than a single-source dispersal-distance model.

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

The current best working picture is:

```text
persistent site template
(depth / light / sediment / hydrodynamics / meadow legacy)
                ↓
       long-run local meadow state
                ↓
  strong year-to-year local persistence
                ↓
shorter-term physiological / demographic stress
                ↓
 blade length / shoot density / local frequency decline
                ↓
     quantitative degradation accumulates
                ↓
 possible recorded-state loss after a threshold
```

Regional neighborhood geometry may still matter during establishment, recovery after major disturbance, or true range/front movement. The present data do not support it as the dominant annual predictor for already monitored Tampa transects.

## Claim boundary

- H1–H4 are ecological hypotheses, not identified causal mechanisms.
- `node_id` is a placeholder for persistent site differences, not a biological variable.
- The dynamic-neighborhood test covers one annual, four-radius formulation only.
- The EOG failure cannot itself prove clonal buffering, light limitation or local recruitment.
- Future causal work should measure the persistent site template directly rather than add more abstract memory or connectivity representations.
