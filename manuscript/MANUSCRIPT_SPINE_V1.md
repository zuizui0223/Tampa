# Tampa manuscript spine v1 — Cryptic degradation beneath persistent seagrass occurrence

## Status

Scientific synthesis after closure of the public-dataset external-validation search.

The paper is a **long-term seagrass ecology study**, not an EOG methods paper. EOG motivated the initial question, but all primary ecological results are reconstructed directly from the pinned Tampa Bay monitoring data.

## Central ecological question

> **Can a foundation species remain recorded at fixed monitoring transects while its quantitative meadow condition deteriorates or its community context reorganizes?**

The central contrast is therefore not presence versus absence alone. It is whether **binary persistence and ecological condition remain congruent through time**.

## Core claim

Across 1997–2025 Tampa Bay fixed-transect monitoring, recorded *Thalassia testudinum* occurrence has strong temporal persistence, yet post-2016 quantitative condition does not track binary occurrence uniformly. Different bay segments express different degradation modes: reduced plant condition, reduced within-transect occurrence/abundance, or community reorganization.

A secondary, exploratory result is that quantitative source-year state contains out-of-time information about next-year **recorded-state loss** inside Tampa. That early-warning result is **not externally confirmed**.

## Study system and state variables

Primary panel:

- 71 stable transects;
- 1,497 eligible visits;
- 1,480 annual transect-years;
- 1997–2025;
- focal foundation species: *Thalassia testudinum*.

Four focal state dimensions:

1. recorded presence;
2. within-transect frequency occurrence;
3. Braun-Blanquet abundance index;
4. plant-condition variables, including blade length and short-shoot density.

Community extension:

- *Halodule wrightii*;
- *Syringodium filiforme*;
- *Ruppia maritima*.

## Result 1 — Persistence contains long ecological memory

Strict walk-forward prediction shows that site history is not reducible to current space/time position.

- space/time baseline macro log loss: 0.3312;
- + previous-year recorded state: 0.1701;
- + exponentially weighted earlier history: 0.1395;
- long-history model beats lag-1 in 14/22 target years.

Interpretation:

> A transect's present recorded state is strongly conditioned by its own ecological history.

Do **not** interpret the best tested 10-year decay candidate as a universal biological memory constant.

## Result 2 — Persistent occurrence can conceal quantitative degradation

For 2016–2025, within-transect models with node fixed effects, cyclic survey timing and sampled-point effort show state decoupling.

### Old Tampa Bay

Binary detection changes weakly, while:

- blade length declines about 1.09 mm yr^-1;
- shoot density declines about 38.3 shoots m^-2 yr^-1.

This is primarily a **plant-condition degradation** mode.

### Middle Tampa Bay

Binary detection is stable to weakly recovering, while blade length declines about 0.405 mm yr^-1.

This is another **presence–condition decoupling** mode.

### Lower Tampa Bay

Binary detection changes weakly, while:

- *Thalassia* frequency declines about 0.0126–0.0128 yr^-1;
- *Thalassia* Braun-Blanquet abundance declines about 0.0412 yr^-1.

This is primarily a **within-transect occupancy/abundance contraction** mode.

Boca Ciega Bay does not show the same clear pattern.

## Result 3 — Degradation mode is bay-specific rather than Tampa-wide

Lower Tampa Bay shows the clearest compositional reorganization:

- *Thalassia* frequency decreases;
- *Syringodium* frequency decreases;
- *Halodule* frequency increases.

This is consistent with community reorganization, but it does not demonstrate competition or mechanistic replacement.

Old Tampa Bay is instead dominated by within-*Thalassia* plant-condition decline. Middle Tampa Bay does not show the same compensatory species pattern.

The general ecological result is therefore:

> **A persistent foundation-species occurrence state can hide multiple, spatially distinct pathways of ecological degradation.**

## Result 4 — Quantitative condition is an internal early-warning candidate

Among 688 source-positive consecutive transitions:

- 24 are followed by next-year recorded loss;
- 664 are followed by recorded persistence.

Before recorded loss:

- median focal frequency = 0.0627 versus 0.302 before persistence;
- median Braun-Blanquet all-point index = 0.0495 versus 0.713.

Strict walk-forward prediction across 23 target years:

- baseline macro log loss = 0.1556;
- quantitative-state augmentation = 0.1465;
- augmented arm wins 17/23 years;
- one-sided paired Wilcoxon p = 0.00271;
- pooled AUC changes from 0.636 to 0.739.

The adverse 2016 target year remains in the primary result.

Interpretation:

> Quantitative degradation may precede loss of the binary recorded state.

Boundary:

- this is recorded-state instability, not demographic extinction;
- it is exploratory because the hypothesis was generated after observing Tampa state decoupling;
- it has **zero valid external scored replications** so far.

## Result 5 — Simple environmental attribution is not supported

Two declared screens are negative.

### Annual bay-segment screen

Post-2016 state changes versus annual salinity, temperature, chlorophyll, total nitrogen, Secchi depth and turbidity:

- FDR < 0.05: 0;
- FDR 0.05–0.10: 0.

### Pre-survey seasonal hot/fresh screen

3- and 6-month temperature/salinity windows:

- FDR < 0.05: 0/8;
- FDR 0.05–0.10: 0/8.

Therefore the manuscript should not attribute the observed degradation modes to a single temperature, salinity, nutrient or water-quality mechanism.

## The 2016/2017 pulse

Five transects lost recorded *Thalassia* in 2016 and all five recorded it again in 2017.

Do not make this a headline result because:

- survey-date coding is protocol-sensitive;
- effort changed substantially at several pulse transects;
- the pinned conversion and current source-reader differ in multi-day date handling.

The pulse remains exploratory context only.

## External-validation closure

A prospectively constrained public-data programme attempted to externally validate the early-warning result.

Final denominator:

- protocol attempts: 10;
- distinct external systems: 5;
- valid externally scored endpoints: **0**;
- external favorable/adverse/null endpoints: **0 / 0 / 0**.

Stops arose from:

- response schema mismatch;
- HTTP Range/transport behavior;
- missing zero-versus-no-estimate semantics;
- authenticated metadata access;
- workbook/parser mismatch;
- dynamic server filenames;
- partial raw archive access before transport rejection.

These are **validation-infrastructure outcomes, not ecological outcomes**.

Candidate hunting is therefore hard-stopped. The paper must not imply external confirmation or external contradiction of the early-warning hypothesis.

The next valid independent test is either:

1. a future Tampa survey wave whose model contract is frozen before those responses exist; or
2. a preselected collaborator/provider dataset with immutable schema, explicit zero-versus-missing semantics and stable identifiers available before response inspection.

## Manuscript hierarchy

### Primary story

**Persistent occurrence can conceal cryptic, spatially heterogeneous degradation in a seagrass foundation species.**

### Secondary story

Long site history is ecologically informative beyond last-year state.

### Tertiary / hypothesis-generating story

Quantitative degradation may provide early warning of later recorded-state instability.

### Not the paper

- EOG predictive performance;
- a climate-causality paper;
- a confirmed extinction/recolonization paper;
- a universal ecological-memory constant;
- a universal *Halodule* replacement mechanism.

## Figure plan

### Figure 1 — Study design and state hierarchy

Tampa Bay fixed transects, 1997–2025, and the four nested state dimensions from binary recorded presence to quantitative plant condition.

### Figure 2 — Persistence versus quantitative condition

Bay-specific trajectories showing where binary occurrence remains stable while frequency, Braun-Blanquet abundance, blade length or shoot density deteriorate.

### Figure 3 — Multiple degradation modes

Contrast Old, Middle and Lower Tampa Bay, including the Lower Tampa Bay community reorganization signal.

### Figure 4 — Internal early-warning test

Source-year quantitative state distributions before persistence versus recorded loss, plus target-year walk-forward log-loss differences.

### Figure 5 or Supplement — Validation and claim boundary

Ten external-validation attempts, zero externally scored endpoints, with STOP stage rather than favorable/adverse outcome.

## Submission-ready claim boundary

### Supported

- recorded *Thalassia* state has strong temporal dependence;
- earlier site history adds information beyond previous-year state;
- binary recorded occurrence can diverge from quantitative meadow condition;
- degradation mode differs among bay segments;
- Lower Tampa Bay shows a compositional reorganization signal consistent with increasing *Halodule* frequency while *Thalassia* and *Syringodium* decline;
- quantitative state contains internal out-of-time information about next-year recorded-state instability;
- simple annual and declared seasonal hot/fresh explanations are unsupported.

### Not supported

- demographic extinction/recolonization inferred from recorded detection;
- causal temperature, salinity, nutrient or hydrologic mechanism;
- a universal 10-year memory constant;
- competitive replacement;
- equivalence between fixed-transect condition and bay-wide mapped acreage;
- external generality of the quantitative early-warning hypothesis.

## Current scientific stopping rule

Do not add another public external dataset to improve the external-validation record.

The next scientific work should be one of two things only:

1. manuscript/figure completion around the state-decoupling result; or
2. prospective confirmation when a genuinely future or pre-authorized external response becomes available.
