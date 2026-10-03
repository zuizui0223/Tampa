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
- authoritative prospective contract: `results/clonal_state_prospective_v2_contract.json` (four-bay v2; v1 retained for provenance).

### Distinguishing prediction

Among meadows with similar baseline above-ground frequency/abundance and bay context:

> higher baseline rhizome TNC -> more positive / less negative future change in focal frequency.

### What would weaken this mechanism

A null primary TNC result under the authoritative four-bay prospective design weakens **rhizome TNC as the measured reserve explanation** only when the frozen precision gate is met (>=36 analyzable nodes total and >=6 per bay). Below that gate, a null remains a pilot/sensitivity estimate.

Secondary clonal traits, soluble sugar alone, starch alone or a nutrient-adjusted metric cannot be selected after outcome access to rescue the primary TNC result.

### Required interpretation diagnostics

Rhizome carbohydrate is not a generic health score.

- *Thalassia* rhizome carbohydrate is seasonally variable, so the primary design uses one <=28-day campaign and requires TNC sampling within +/-14 days of the paired baseline transect survey.
- Florida work shows negative associations between plant nutrient content and rhizome carbohydrate. High TNC can therefore reflect stored reserve, reduced growth demand under nutrient limitation, or both.
- Contemporaneous leaf N, P and N:P are collected as a secondary nutrient-state diagnostic.
- The primary TNC assay is standardized as soluble NSC + starch under one HPLC workflow; method switching after outcome access is prohibited.

A positive TNC -> future-state result therefore supports **predictive information in measured below-ground reserve state**, not proof that carbohydrate itself is the causal buffering mechanism.

### Secondary competing below-ground mechanism: regenerative meristem bank

Do not collapse all below-ground biology into one "clonal memory" variable.

The same field cores can separate two candidate axes:

- **energetic reserve:** rhizome TNC;
- **regenerative capacity:** rhizome meristem / apex density.

Integrated-growth work in *T. testudinum* has proposed inactive shoots and associated meristematic structures as a dormant meristem bank. A meristem-density signal would therefore support a regenerative-capacity mechanism distinct from the primary TNC reserve hypothesis.

This is predeclared as secondary and cannot rescue a null primary TNC result.

### What it does not require

It does not require blade length to decline before frequency. The rejected one-year condition -> thinning cascade is therefore not a contradiction.

### Persistent site-template alternative: two orthogonal diagnostics

A supported cross-node TNC association alone can still arise if persistent site quality makes both rhizome reserve and later meadow state high.

The reserve program therefore predeclares two **secondary site-template-resistant diagnostics** that attack this common-cause alternative in different dimensions.

**Spatial diagnostic — within the same transect**

At nodes with three distinct q25/q50/q75 anchors:

```text
future_BB_anchor
  ~ baseline_BB_anchor
  + within_node_centered_anchor_TNC
  + node_fixed_effect
```

The baseline-only feasibility audit supports this design at 30 nodes (Old 8, Middle 10, Lower 12).

A positive centered-TNC coefficient means that local reserve differences predict local future quantitative state **after stable transect identity is removed**. This weakens a transect-level site-template explanation, but persistent meter-mark microhabitat remains possible.

**Temporal diagnostic — within the same node**

Using the frozen 39-45 day pre/post TNC pair:

```text
delta_tnc_42d = tnc_post - tnc_pre

future_delta_frequency
  ~ baseline_frequency_post
  + tnc_post
  + delta_tnc_42d
  + water_body
```

The focal question is whether recent reserve trajectory adds information **beyond current post-exposure reserve level**.

A positive delta-TNC coefficient is less compatible with a purely time-invariant node-quality explanation, but time-varying common causes and TNC measurement error remain possible.

**Interpretation matrix**

- node-level static TNC only supported -> reserve state predicts the future, but persistent site quality remains a strong alternative;
- within-transect anchor diagnostic supported -> stable transect identity alone is insufficient;
- dynamic reserve-change diagnostic supported -> time-invariant node quality alone is insufficient;
- both site-template-resistant diagnostics supported -> a purely fixed site-template explanation becomes substantially less complete, while local microhabitat and time-varying confounding still remain;
- both unsupported -> do not promote the static TNC association into a strong process claim.

Neither diagnostic can rescue a null primary node-level TNC result. They refine interpretation; they do not create a second route to significance.

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

## H3. Event-scale hot-fresh stress debt

### Mechanism

The failed annual/segment temperature-salinity tests may have averaged over local short events.

The new test does **not** search for a new better-looking threshold. It keeps the published Tampa 30 C / 25 ppt suboptimal-condition definition and asks whether the same condition has biological meaning when measured at <=15-minute, node scale.

Prospective contract:

- `results/event_stress_debt_prospective_v1_contract.json`
- `docs/EVENT_SCALE_STRESS_DEBT_PROTOCOL_V1.md`

### Primary mechanistic link

Deploy synchronized temperature + salinity loggers at the same census-oriented baseline-*Thalassia*-positive node frame used by the TNC program.

Measure TNC before and after the common logger exposure window.

Primary model:

~~~text
tnc_post
  ~ tnc_pre
  + joint_hot_fresh_hours_30_25
  + water_body
~~~

Prediction:

> more simultaneous local hot-fresh exposure -> lower post-exposure TNC after pre-exposure TNC is represented.

This makes the immediate biological response **reserve depletion**, rather than another annual presence/loss endpoint.

### Exposure-scale falsification

The design separates two explanations for the old null result.

- node/event-scale test supported -> coarse spatial/temporal aggregation is a plausible reason the retrospective test failed;
- node/event-scale test unsupported with adequate exposure variation and precision -> the specific Tampa hot-fresh mechanism becomes substantially weaker;
- joint exposure lacks variation -> classify non-estimable and do not retune thresholds.

### Two-gate stress-debt chain

The independently frozen clonal test supplies the second link:

1. event exposure -> reserve depletion;
2. post-exposure TNC -> future focal-frequency change.

Both links supported is consistent with:

> event stress -> reserve depletion -> future persistence.

It is not formal mediation or causal proof.

### Why PAR is not added here

PAR/light stress is retained as H4, a separate leaf/canopy optical mechanism.

Adding PAR to H3 after seeing a hot-fresh result would recreate the same rescue-search problem that the measurement-layer hard stop was designed to prevent.

### What would weaken this mechanism

A primary null with:

- >=30 analyzable nodes;
- >=8 per core bay;
- >=35 days common overlap;
- >=85% paired logger coverage per node;
- adequate joint-exposure variation;

weakens the fixed 30 C / 25 ppt event-scale stress-debt mechanism.

Do not rescue it with a different temperature threshold, salinity threshold, lag, exposure percentile, season or node subset.

---

## H4. Direct optical microenvironment versus mature-canopy marker

### Motivation

Bulk Secchi × depth did not explain plant-condition trajectories, and the existing qualitative `EpiphyteDensity` field does not behave as a simple annual stress indicator. That closes the coarse/ordinal routes, not leaf-scale light biology.

The new prospective test measures the light environment actually experienced inside the standing *Thalassia* canopy over the same 39–45 day biological interval used for pre/post TNC.

Primary contract:

- `results/optical_microenvironment_prospective_v1_contract.json`
- `docs/OPTICAL_MICROENVIRONMENT_PROTOCOL_V1.md`

### Primary actual-light link

Primary exposure:

```text
mean_daily_within_canopy_dli
```

Primary model:

```text
tnc_post
  ~ tnc_pre
  + mean_daily_within_canopy_dli
  + water_body
```

Prediction:

> higher actual within-canopy daily light integral -> higher post-exposure rhizome TNC after pre-exposure TNC is represented.

No low-light threshold is searched. DLI is continuous.

### Optical-source attribution is a separate layer

Low within-canopy DLI can arise from several sources:

- cloud / incident-light variation;
- water-column turbidity / attenuation;
- canopy self-shading;
- epiphyte load on leaves.

Therefore a nested paired subset measures simultaneous **above-canopy** and **within-canopy** PAR.

```text
T_canopy = DLI_within / DLI_above
A_canopy = 1 - T_canopy
```

This separates the broader actual-light exposure test from local canopy-associated optical attenuation.

Interpretation:

- DLI -> TNC supported + positive canopy attenuation -> consistent with biologically consequential low light plus a local canopy-associated optical gradient;
- DLI -> TNC supported + weak attenuation -> light matters, but cloud/water-column forcing may dominate;
- attenuation positive + null DLI -> canopy alters light, but that change is not shown to deplete reserve over the frozen interval.

The paired attenuation diagnostic cannot replace a null actual-DLI primary.

### Epiphyte-specific attribution

Historical qualitative epiphyte categories are not reused as the primary predictor.

Secondary direct measurements may include:

- epiphyte biomass per standardized leaf area;
- paired intact-versus-cleaned leaf transmittance under a response-independent cleaning-damage pilot.

These ask whether epiphytes physically account for part of the observed optical attenuation.

### Measurement integrity

A response-independent vertical-profile pilot freezes one proportional within-canopy sensor height before outcome-bearing deployment. Daily DLI also has a photoperiod-specific missing-data rule; overall row coverage alone is insufficient.

The optical programme reuses the same two pre/post TNC rounds as the event-stress programme and does not authorize a third destructive reserve-sampling round.

### Site-template boundary

Direct PAR and reserve change are dynamic measurements over a common interval and are less compatible with a purely static site label than one-time proxies.

However, time-varying turbidity, nutrients, hypoxia and disturbance can still be common causes. A supported primary is therefore a **prospective actual-light / reserve association**, not experimental proof that light or epiphytes are the sole causal driver.

### Conditional physiological escalation: internal aeration / sulfide exclusion

If the frozen actual-DLI -> TNC primary is supported, the next physiological question is predeclared in:

- `docs/OXYGEN_SULFIDE_ESCALATION_V1.md`

Candidate process:

> low irradiance -> reduced internal plant O2 -> greater H2S intrusion into meristem/rhizome tissue -> reserve and/or regenerative-capacity loss.

This pathway is grounded in direct *Thalassia testudinum* oxygen/sulfide studies, but it is not added as another primary to the current campaign.

Water-column DO and porewater sulfide alone are external-context measurements. A strong **aeration-failure** claim requires direct internal meristem/rhizome O2 and/or tissue H2S intrusion measurements in a separately frozen future study.

If the optical primary is null with adequate precision, do not add O2/sulfide variables to rescue it post hoc.

### No-rescue rule

Do not reopen Secchi windows, ordinal epiphyte categories, low-light thresholds or favorable PAR aggregation after TNC inspection.

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

## Multilevel buffering synthesis

The competing mechanisms above can be organized by **where ecological buffering is stored**.

This is a candidate synthesis, not a current empirical result.

### Level 1 — internal biological buffer

State carrier:

> rhizome non-structural carbohydrate reserve.

Organizational level:

> ramet / below-ground plant system.

Frozen test:

> does baseline rhizome TNC predict more favorable future quantitative *Thalassia* change beyond current above-ground state?

This mechanism can operate even if annual blade length and shoot density do not lead frequency change. It is therefore compatible with the rejected simple condition -> thinning cascade.

### Level 2 — external engineered buffer

State carrier:

> the physical environment modified by the standing canopy.

Organizational level:

> meadow / foundation-species patch.

Frozen tests require two links:

1. vegetation-associated attenuation beyond the matched bare-bed boundary-layer gradient;
2. greater attenuation predicts more favorable future *Thalassia* quantitative change.

Only both links together support hydrodynamic self-facilitation.

### Level 3 — community functional buffer

State carrier:

> persistence of alternative habitat-forming species and the physical function of the mixed canopy.

Organizational level:

> seagrass community.

Frozen question:

> when *Thalassia* prominence decreases, does alternative-seagrass vegetation preserve the measured hydrodynamic function after total cover and canopy height are represented?

This distinguishes **habitat occupancy insurance** from **functional insurance**.

### External forcing — buffer depletion rather than another buffer

Event-scale temperature/salinity/light/oxygen forcing is not a fourth memory store.

Its mechanistic role is as a possible **input that consumes or overwhelms buffers**.

The currently frozen hot-fresh prospective study asks only whether a published Tampa compound event condition is associated with short-term rhizome reserve depletion. A supported event -> TNC link would connect external forcing to the internal buffer; it would not by itself identify the long-term meadow response.

### Why this framework explains state decoupling

The annual archive showed that plant condition, focal abundance/occupancy and community composition do not form one supported serial cascade.

A multilevel-buffer model does not require such a cascade.

Different buffers can operate in parallel and at different organizational levels:

```text
short-timescale forcing
        |
        v
internal reserve --------------------+
        |                             |
        +------> focal plant state <--+------ engineered physical buffer
                         |
                         v
               focal quantitative persistence
                         |
             if focal state is lost
                         v
             community functional insurance
```

Coarse presence can therefore remain stable while one or more finer state axes change, because persistence is an **outcome jointly produced by partially independent buffers**, not a single latent health variable.

### Predeclared interpretation matrix

| Prospective result | Ecological interpretation |
|---|---|
| TNC supported; engineering unsupported | internal reserve buffering is the supported measured mechanism |
| engineering supported; TNC unsupported | external physical self-buffering is the supported measured mechanism |
| both supported | consistent with multiple buffering mechanisms operating in the same foundation-species system |
| neither supported | current persistence lag requires another hidden state; do not rescue either mechanism post hoc |
| alternative canopies retain occupancy but differ in attenuation | occupancy insurance without full functional insurance |
| alternative canopies retain comparable attenuation | consistent with hydrodynamic functional redundancy over the sampled range |
| event exposure predicts TNC depletion, and TNC predicts future change | consistent with an event -> reserve depletion -> future-state chain; not formal mediation |
| event exposure does not predict TNC | do not invoke the tested hot-fresh condition as the cause of reserve differences |

### What is potentially general

The general ecological proposition is not that seagrass possesses a special form of "memory".

It is:

> **foundation-species persistence can be buffered at multiple organizational levels, and the apparent stability of a coarse state may reflect different combinations of internal storage, environmental engineering and community functional redundancy.**

This structure can in principle apply to forests, marshes, reefs, kelp systems and other long-lived habitat-forming organisms.

### Novelty boundary

Internal biological memory, niche construction / ecosystem engineering, foundation-species facilitation and community insurance are all established ideas individually.

The Tampa contribution would be the **prospective decomposition of these buffers in the same long-monitored foundation-species system**, using independent measurements and predeclared failure rules.

Do not claim "multilevel buffering" is a new ecological concept merely because this document gives it a compact name.

Do not combine the primary tests into a post-hoc composite score.

Do not fit TNC x attenuation x event-stress interactions unless a separately powered study is frozen before response access.

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
