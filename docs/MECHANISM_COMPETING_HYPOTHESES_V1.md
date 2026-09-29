# Tampa competing mechanism hypotheses v1

## Purpose

The current Tampa archive identifies ecological state structure but does not identify one causal mechanism. This document keeps the next measurements as **competing tests**, rather than allowing every new variable to be interpreted as support for a generic "ecological memory" story.

The present annual/exact-point archive is mechanistically saturated. No new mechanism is authorized from another retrospective loss/re-recording subgroup, lag window, threshold, radius or hidden-state decomposition.

## Empirical anchors that any mechanism must respect

1. Recorded occurrence, within-transect abundance, plant condition and community composition are partly decoupled.
2. Blade length / shoot density do **not** provide a supported simple one-year leading signal for next-year frequency or Braun-Blanquet thinning beyond current state and stable node identity.
3. Annual and frozen seasonal temperature/salinity summaries, the published 30 C / 25 ppt compound-stress metric, bulk benthic-light proxy, depth/sediment template, simple neighborhood state and static accessibility do not identify a common mechanism.
4. Longer focal *Thalassia* local history can contain later re-recording information, but that observational legacy does not identify rhizome survival, clonal memory or ecological recovery.
5. Lower Tampa Bay shows community reorganization, but alternative-seagrass persistence is often pre-existing occupancy rather than demonstrated post-loss replacement.
6. TBOFS is useful regional context but is not accepted as literal meadow-scale near-bed exposure because its bathymetry is systematically deeper than the shallow transect record.
7. The existing qualitative epiphyte-density record does not support a simple annual epiphyte-stress -> next-year recorded-loss interpretation; direct optical/biomass measurement would be required.

Therefore the next program tests hidden **biological and physical states**, not another ordering of the old annual variables.

---

## H1. Below-ground reserve / clonal buffering

### Mechanism

A meadow can maintain above-ground quantitative state because rhizome reserve and clonal connectivity buffer temporary deficits in local carbon balance or shoot performance.

### Frozen primary measurement

- rhizome total non-structural carbohydrate (TNC);
- prospective contract: `results/clonal_state_prospective_v1_contract.json`.

### Distinguishing prediction

Among meadows with similar baseline above-ground frequency/abundance and bay context:

> higher baseline rhizome TNC -> more positive / less negative future change in focal frequency.

### What would weaken this mechanism

A null primary TNC result under the frozen prospective design weakens **rhizome TNC as the measured reserve explanation**. Secondary clonal traits cannot be selected after outcome access to rescue it.

### What it does not require

It does not require blade length to decline before frequency. The rejected one-year condition -> thinning cascade is therefore not a contradiction.

---

## H2. Canopy hydrodynamic self-facilitation

### Mechanism

Established vegetation changes its local physical environment. If that engineering feeds back on meadow persistence, stronger canopy-associated flow attenuation should reduce subsequent quantitative loss.

### Frozen measurements

- paired shallow-water velocity inside/near the canopy and in a local upper-water-column reference;
- nested matched bare-bed counterfactual subset;
- direct protocol: `docs/DIRECT_HYDRODYNAMIC_SAMPLING_PROTOCOL_V1.md`;
- prospective contract: `results/direct_hydrodynamic_prospective_v1_contract.json`.

### Two required links

**A. Physical engineering gate**

```text
A_veg  = 1 - p90(U_veg_nearbed) / p90(U_veg_reference)
A_bare = 1 - p90(U_bare_nearbed) / p90(U_bare_reference)

excess_canopy_attenuation = A_veg - A_bare
```

The frozen paired interval for mean excess canopy attenuation must lie above zero.

This control is required because an ordinary seabed boundary layer can create lower velocity near the bed even without vegetation.

**B. Prospective ecological gate**

```text
future_delta_frequency
  ~ baseline_frequency
  + ambient_p90
  + attenuation_p90
  + water_body
```

Higher attenuation must predict more positive / less negative future focal-frequency change under the frozen rule.

### Interpretation matrix

- A supported, B supported -> consistent with hydrodynamic self-facilitation.
- A supported, B unsupported -> canopy modifies flow, but that modification is not shown to stabilize future *Thalassia*.
- A unsupported, B supported -> hydrodynamic state predicts the future, but canopy causation is not identified.
- A unsupported, B unsupported -> no support for hydrodynamic self-facilitation under this design.

Even A+B support remains observational at meadow scale rather than experimental proof of a feedback.

---

## H3. Event-scale physiological stress debt

### Mechanism

The failed annual/seasonal summaries may average over biologically important short events. Repeated heat, freshening, low-PAR or hypoxic pulses may accumulate physiological cost even when annual means look benign.

### New measurements

Node-scale high-frequency:

- temperature;
- salinity;
- PAR;
- optionally dissolved oxygen and turbidity.

### Distinguishing prediction

A response-independent, physiology-motivated event metric measured before the future survey predicts future quantitative change beyond baseline state.

Examples must be frozen before outcome access:

- cumulative heat load;
- duration above an externally chosen thermal threshold;
- low-salinity event duration;
- joint heat x fresh duration;
- diel/cumulative PAR deficit;
- recovery time after events.

### What would weaken this mechanism

If frozen high-frequency exposure features add no prospective information despite adequate temporal coverage and node replication, the explanation should not be rescued by threshold or window searching.

---

## H4. Leaf/canopy optical stress versus mature-canopy marker

### Motivation

Bulk Secchi x depth did not explain plant-condition trajectories. A local leaf-scale pathway remains possible through epiphyte shading, self-shading or local turbidity.

However, the existing qualitative `EpiphyteDensity` record does **not** behave as a simple annual stress indicator: the adjusted primary association was positive rather than negative and became interval-ambiguous when target year 2016 was restored.

### Competing predictions

**Optical-stress version**

> greater measured epiphyte biomass / lower leaf-level PAR -> more negative future plant or meadow state.

**Mature-canopy-marker version**

> qualitative epiphyte load covaries with leaf age, canopy persistence or favorable microsite state, but directly measured optical attenuation does not independently predict future decline.

### Required new measurements

- epiphyte biomass per leaf area;
- leaf-level or within-canopy PAR attenuation;
- leaf age / turnover proxy;
- canopy height and total cover;
- local turbidity.

Do not mine additional categories, epiphyte types or lag windows from the old qualitative field.

---

## H5. Community functional insurance

### Mechanism question

Existing exact-point results show **occupancy insurance**: when *Thalassia* is lost from a point, pre-existing alternative seagrasses often keep the point vegetated.

That does not establish functional equivalence.

### New physical prediction

Using the direct velocity deployment:

```text
attenuation_p90
  ~ total_vegetated_cover
  + canopy_height
  + thalassia_fraction
  + water_body
```

The composition term asks whether an alternative-seagrass canopy provides a different hydrodynamic function after total structure is represented.

### Interpretation

- composition effect -> retained vegetation is not automatically hydrodynamically equivalent;
- no composition effect -> consistent with functional redundancy only over the sampled range and uncertainty.

This is secondary and cannot rescue a null primary attenuation -> future *Thalassia* result.

---

## H6. Resistance-to-recovery strategy shift under community reorganization

### Mechanism question

Lower Tampa Bay shows declining *Thalassia* and *Syringodium* with increasing *Halodule*, but the annual observation record does not show that *Halodule* newly colonized after focal loss. Much alternative occupancy is persistence of species already present.

The stronger ecological hypothesis is therefore not "Halodule recolonizes after Thalassia disappears". It is:

> disturbance or chronic stress can shift a meadow from a **persistence/resistance strategy** dominated by slow, long-lived *Thalassia* toward a **rapid-cover / recovery strategy** in which pre-existing or expanding *Halodule* becomes more prominent.

This is motivated by established life-history contrasts in the literature: *H. wrightii* is widely treated as a fast-growing pioneer/early-successional species, whereas *T. testudinum* is slower-growing and late-successional. Classic comparative flume work also found stronger canopy friction and sediment protection for *T. testudinum* than for *H. wrightii*, with *Syringodium* lower still under the tested conditions (Fonseca & Fisher 1986, MEPS 29:15–22).

### Tampa-specific discriminating prediction

Occupancy insurance and functional insurance need not be the same.

The direct hydrodynamic deployment therefore asks whether alternative-seagrass prominence preserves the physical function of the meadow:

```text
attenuation_p90
  ~ total_vegetated_cover
  + canopy_height
  + thalassia_fraction
  + water_body
```

If composition still explains attenuation after structural controls, then community reorganization changes ecosystem-engineering function even when the point remains vegetated.

If composition does not add information, the result is consistent with hydrodynamic functional redundancy over the sampled structural range.

### Why this is more informative than "successional reset"

The current archive cannot distinguish new colonization, competitive release, clonal expansion of pre-existing *Halodule*, or shared microsite persistence. "Successional reset" therefore remains too mechanistically specific.

The resistance-to-recovery framing requires only directly testable differences in life-history state and physical function. It also turns the Lower Tampa pattern into a general foundation-species question:

> can community turnover preserve habitat occupancy while changing the mechanism by which the habitat resists disturbance?

### Claim boundary

Do not call the Lower Tampa pattern a demonstrated succession sequence until recruitment/expansion dynamics are measured directly.

Do not infer that *Halodule* is functionally inferior from taxonomy alone. The Tampa functional result must come from measured canopy structure and hydrodynamic attenuation.

## Cross-mechanism discrimination

The mechanisms make different observations necessary.

| Future result | Clonal reserve | Canopy engineering | Event stress | Optical stress |
|---|---|---|---|---|
| TNC predicts future change | supports measured reserve explanation | not required | not required | not required |
| Excess canopy attenuation > 0 | not required | supports physical link A | not required | not required |
| Attenuation predicts future change | not required | supports ecological link B | possible confound unless ambient exposure represented | not required |
| High-frequency event load predicts future change | possible moderator | possible external forcing | supports | possible if PAR/turbidity |
| Epiphyte biomass / leaf PAR predicts future change | not required | possible canopy covariate | possible interaction | supports |
| Alternative composition changes attenuation after structural controls | not required | identifies species-dependent engineering | not required | possible canopy-structure consequence |

No single positive measurement should be relabeled as "ecological memory". The mechanism name follows the measured state and the frozen discriminating prediction.

---

## Candidate synthesis only after future tests

If both rhizome reserve and independently attributed canopy attenuation predict future quantitative persistence, Tampa would support a **multiple-buffer foundation-species model**:

> persistence can arise from an internal biological buffer (stored below-ground reserve) and an external engineered buffer (modification of the local physical environment).

This synthesis is **not a current result**. It is deliberately withheld until both new-measurement tests exist.

An interaction between TNC and attenuation is not predeclared as a confirmatory endpoint because the realistic node sample is too small for a stable high-order interaction test. Any future integration must be frozen before response access.
