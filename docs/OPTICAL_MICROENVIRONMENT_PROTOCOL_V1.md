# Tampa direct optical microenvironment protocol v1

## Goal

Test whether the light actually experienced inside *Thalassia testudinum* canopies predicts short-term change in below-ground reserve.

The retrospective Tampa programme already rejected two weaker proxies:

- bay/segment bulk Secchi-derived benthic light did not explain the focal plant-condition trajectories under the frozen tests;
- qualitative annual `EpiphyteDensity` did not behave as a simple year-ahead stress indicator.

The new mechanism therefore changes the **measurement layer**, not the old categories.

Primary question:

> does lower directly measured within-canopy daily light correspond to lower post-exposure rhizome TNC after pre-exposure TNC is represented?

Paired contract:

- `results/optical_microenvironment_prospective_v1_contract.json`.

## Biological motivation

Experimental work on *T. testudinum* shows that sustained light reduction can alter growth, pigments and carbohydrate allocation, and chronic shading can substantially reduce rhizome carbohydrate. Other experiments also show that intermediate-duration low irradiance can produce faster leaf-level responses without an immediate rhizome-TNC response.

Therefore a 42-day field test is deliberately falsifiable:

- support would show that natural node-scale light variation is large and persistent enough to register in reserve state;
- a well-powered null would show that direct light over this interval does not explain the reserve differences, rather than being rescued by another Secchi window.

Relevant background includes Lee & Dunton's *T. testudinum* light-reduction experiments and classic work on epiphyte shading and seagrass light budgets.

## Sampling frame

Use the same census-oriented contemporaneously baseline-*Thalassia*-positive core-bay nodes as the TNC/event programme.

Historical planning frame:

- Old Tampa Bay: 8;
- Middle Tampa Bay: 11;
- Lower Tampa Bay: 14;
- total: 33.

Confirmatory minimum:

- >=30 analyzable nodes;
- >=8 analyzable nodes in each core bay.

Below this gate, report the optical coefficient and uncertainty as a pilot. Do not use a null to reject optical stress.

## Shared 42-day biological interval

Preferred design is co-deployment with the event-stress campaign:

> **July 24 through September 3**

Target:

- 42 days;
- minimum common valid overlap: 35 days;
- PAR interval <=15 minutes;
- the same pre/post TNC samples and 39-45 day biological interval already frozen for the event/clonal programme.

Sharing the biological interval is efficient but does **not** merge the hypotheses. Optical and hot-fresh exposures remain separate primary tests.

## Representative deployment meter mark

Choose the optical deployment location before any PAR record exists.

For the primary *Thalassia* cohort:

- identify all contemporaneously vegetated meter marks;
- compute their median `site_m`;
- among contemporaneously *Thalassia*-positive marks, choose the mark closest to that vegetated median;
- exact tie -> lower `site_m`.

Do **not** use preliminary PAR, mapped meadow-edge distance, accessibility to a nearby bare patch, or visual darkness/brightness to move the logger.

If the preselected representative mark cannot satisfy the frozen PAR geometry, the node is optical-primary-ineligible rather than relocated to a more convenient optical position.

This mirrors the representative-placement rule already used to prevent edge-biased hydrodynamic sensor placement.

## Optical quantity and angular-response class

The outcome-bearing study must measure **one optical quantity consistently**.

Before interpreting the response-independent method pilot, freeze exactly one of:

- `2pi_cosine_ppfd` — hemispherical cosine-corrected photosynthetic photon flux density;
- `4pi_scalar_ppffr` — scalar photosynthetic photon flux fluence rate / scalar photon irradiance.

The choice is a measurement-design decision, not an ecological-result choice.

Rules:

1. all outcome-bearing within-canopy channels use the same class;
2. the in-water calibration reference uses the same class;
3. if the paired above-canopy attribution subset is retained, its reference channels use the same class;
4. no scalar↔cosine calibration transfer is allowed in this v1 study;
5. the paper reports the chosen quantity by name rather than calling both variants generic interchangeable "PAR DLI."

The computational primary column may remain `mean_daily_within_canopy_dli`, but its physical meaning must be carried from the method freeze into analysis and reporting.

This matters because canopy leaves alter the angular distribution of underwater light. Two sensors can agree under a calibration field yet respond differently inside a directional or diffuse canopy light field if their angular collectors differ.

## Within-canopy PAR placement

At each node, measure PAR at one preselected within-canopy position.

Frozen placement concept:

> sensor center at 50% of baseline canopy height above the sediment.

Before outcome-bearing deployment, a response-independent field pilot must freeze:

- sensor model;
- scalar/cosine geometry;
- orientation;
- exact proportional-height rule;
- minimum height above sediment;
- allowed height tolerance;
- mounting design;
- rule for avoiding artificial shade from the mount;
- rule for nodes whose canopy is too short/shallow to support the geometry.

Minimum target height above bed is 0.05 m.

Do not move a sensor higher or lower after seeing PAR/TNC because one position gives a more favorable signal.

## Response-independent vertical-profile pilot

The outcome-bearing study will use one fixed within-canopy PAR height per node. Before choosing that height, run a short physical pilot without TNC/future-response access.

At a subset spanning short and tall canopies, measure a local PAR profile at:

- 25% of canopy height;
- 50% of canopy height;
- 75% of canopy height;
- one above-canopy reference.

Use simultaneous sensors where possible; otherwise use a predeclared rapid profiling procedure under sufficiently stable irradiance.

The pilot asks only whether one proportional height provides a reproducible, field-feasible representation of within-canopy irradiance.

Freeze the final proportional-height rule before the first outcome-bearing TNC core.

After that point:

- no node-specific height optimization;
- no switching to the brightest/darkest level;
- no selection of whichever height later correlates with TNC.

## Optical QC

Freeze before deployment:

- factory/laboratory PAR calibration;
- cross-calibration among sensors;
- dark/offset checks if relevant;
- anti-fouling treatment;
- cleaning schedule if any;
- cleaning-event flags;
- drift/fouling rejection rule;
- burial/exposure rule;
- clock alignment;
- gap/interpolation rule.

Each confirmatory node must retain >=85% valid PAR observations across the common overlap.

Biofouling is especially important for an underwater optical study. A fouled sensor is not interpreted as biologically low light.

## Daily DLI integrity

Daily light integral is sensitive to when missing observations occur.

Before deployment, freeze:

- expected observations per day;
- minimum valid fraction across the local photoperiod;
- maximum allowable continuous daytime gap;
- the only gap length eligible for interpolation.

A day failing the frozen daylight-integrity rule is not used for DLI.

The primary node mean requires **at least 30 valid daily DLIs** within the common overlap, in addition to the network-wide >=85% PAR coverage rule.

Do not reconstruct long daytime gaps from neighboring nodes, weather stations or the above-canopy reference.

## Nested paired above-canopy optical reference

The primary biological exposure remains actual within-canopy DLI. To identify whether low actual light is locally created by the canopy/leaf layer rather than by incident or water-column light, add a nested paired-reference subset.

Planning target:

- 18 nodes;
- minimum analyzable physical-attribution set: 12;
- >=3 nodes in each of Old, Middle and Lower Tampa Bay.

At each retained attribution node, measure PAR **simultaneously above and within the same canopy** using the same sensor family, calibration, clock and QC.

Target above-canopy sensor center:

> 0.10 m above the top of the standing canopy.

Freeze the clearance tolerance and mounting geometry in the physical pilot. The reference must remain submerged, outside the standing leaf canopy and clear of mount shadow.

For each paired node calculate:

```text
T_canopy = mean_daily_DLI_within / mean_daily_DLI_above

A_canopy = 1 - T_canopy
```

Retain negative attenuation values if they occur; do not truncate them.

The physical diagnostic reports the node-level transmittance/attenuation distribution and a two-sided node-bootstrap interval for mean `A_canopy`.

Interpretation:

- actual DLI -> TNC supported + positive canopy attenuation -> consistent with biologically consequential low light plus a local canopy-associated optical gradient;
- actual DLI -> TNC supported + weak canopy attenuation -> light matters, but low light may be driven mainly by cloud/water-column/turbidity forcing;
- positive canopy attenuation + null actual-DLI primary -> canopy modifies light, but the modification is not shown to deplete reserve over this interval.

The paired-reference metric cannot replace or rescue a null actual-DLI primary.

## Quantitative optical pilot gate

The response-independent method/geometry acceptance contract is:

- `results/optical_pilot_acceptance_v1_contract.json`
- implementation guide: `docs/OPTICAL_PAR_METHOD_PILOT_V1.md`

Outcome-bearing optical deployment is not authorized merely because a PAR logger is available.

Before deployment, all planned outcome-bearing sensor channels must pass the frozen in-water reference calibration gate, and the single-height canopy design must pass the frozen vertical-representativeness and placement-repeatability gates.

The pilot also freezes the fouling/maintenance rule.

### Daily DLI QC now fixed

A node-day is valid only when:

- >=90% of scheduled astronomical-daylight observations are present;
- no continuous daylight gap exceeds 30 minutes.

Only daylight gaps <=30 minutes may be linearly interpolated.

A longer daylight gap invalidates the node-day.

The primary node exposure still requires >=30 valid DLIs, >=85% overall PAR coverage and >=35 days of common calendar overlap.

These are measurement-QC rules, not biological light thresholds.

## Primary exposure

For every valid day, integrate calibrated PAR to:

```text
daily_light_integral
  = mol photons m-2 d-1
```

Primary node exposure:

```text
mean_daily_within_canopy_dli
  = mean(valid daily light integrals over the frozen common overlap)
```

No primary light threshold is used.

Do not search retrospectively for:

- a minimum DLI cutoff;
- percent surface irradiance cutoff;
- hours below a chosen PAR threshold;
- alternative percentile;
- a favorable shorter/longer window.

Those can only be used in a separate future study frozen before response access.

## Optical variation / identifiability gate

Before fitting TNC:

- >=30 analyzable nodes total and >=8 per core bay;
- >=2 core bays each contain >=6 analyzable nodes with >=3 distinct node-level DLI values;
- primary DLI must have at least 10 distinct node-level values network-wide.

If the gate fails, classify the optical primary as **non-estimable**.

Do not remove `water_body`, drop a low-variation bay, or tune DLI aggregation to manufacture within-bay variation.

## Primary reserve model

```text
tnc_post
  ~ tnc_pre
  + mean_daily_within_canopy_dli
  + water_body
```

Expected DLI coefficient: **positive**.

Support rule:

- two-sided 95% interval entirely above zero -> supported;
- entirely below zero -> contradicted direction;
- overlaps zero -> unsupported;
- sample/coverage/variation gate fails -> non-estimable.

The stable transect node is the inferential unit. PAR rows and TNC cores are repeated measurements.

## Shared TNC sampling rule

The optical programme uses the **same** pre-exposure and post-exposure TNC rounds already frozen for the event-stress / reserve programme.

It does not authorize a third destructive reserve-sampling round.

All optical primary nodes inherit the frozen:

- 39-45 day pre/post TNC interval;
- q25/q50/q75 spatial-core logic;
- cumulative coring-footprint guardrail;
- tissue/HPLC protocol;
- disturbance sensitivity.

## Epiphyte role

Historical qualitative epiphyte burden is **not** returned to the primary model.

Instead collect a direct leaf-surface measurement if feasible:

- epiphyte dry mass or ash-free dry mass per leaf area;
- one frozen leaf age/position class;
- one frozen removal and weighing method.

This asks whether epiphyte biomass explains actual optical exposure, not whether an ordinal historical category predicts loss.

## Optional paired leaf-optics diagnostic

A stronger epiphyte-specific physical diagnostic can be added only after a response-independent laboratory pilot.

Candidate measurement:

1. measure PAR/spectral transmittance through a standardized intact epiphyte-bearing *Thalassia* leaf segment;
2. remove epiphytes with one validated gentle method;
3. remeasure the same segment;
4. derive paired epiphyte-associated transmittance loss.

Before inferential use, the pilot must show that the cleaning/removal method does not itself materially alter cleaned-leaf optical properties.

This is a physical attribution diagnostic for epiphyte shading.

It does **not** replace the primary actual-light exposure test.

## Competing interpretation: optical stress versus mature-canopy marker

Two explanations remain possible.

### Optical-stress version

> epiphyte biomass / canopy structure materially reduces actual light, and lower actual light predicts reserve depletion.

### Mature-canopy-marker version

> high qualitative epiphyte burden primarily marks older leaves, persistent canopy or favorable microsites; direct light exposure is not sufficiently reduced to explain reserve depletion.

The new direct optical layer can distinguish these better than another analysis of ordinal `EpiphyteDensity`.

## Relationship to hot-fresh exposure

Before TNC results are inspected, if both environmental layers are estimable:

- plot node-level mean DLI versus joint hot-fresh hours;
- report Spearman correlation with two-sided bootstrap interval.

This is descriptive.

Do not fit a joint PAR + hot-fresh primary model after seeing which separate result is favorable.

If both separate primaries support, report two co-occurring measured process associations unless an independently powered joint study has been frozen.

## Secondary future-state link

Predeclare only as secondary:

```text
future_delta_frequency
  ~ baseline_frequency_post
  + mean_daily_within_canopy_dli
  + water_body
```

Expected DLI direction: positive.

This cannot rescue a null light-to-TNC primary.

Binary re-recording remains an observation-state event, not recovery.

## Site-template boundary

Direct PAR and pre/post TNC are dynamic measurements over a common interval, so support is less consistent with a purely static site-label explanation than a one-time cross-node proxy.

But it remains observational.

Time-varying turbidity, nutrients, hypoxia, disturbance or other common causes can affect both light and reserve.

A supported result is therefore:

> a prospective actual-light / reserve association at meadow scale.

It is not experimental proof that light was the sole causal driver.

## No-rescue rules

Do not:

- reopen Secchi windows;
- use historical qualitative epiphyte categories as the primary predictor;
- invent a low-light threshold after seeing TNC;
- add/remove hot-fresh exposure, turbidity or nutrients from the primary model after inspection;
- move sensors based on preliminary PAR values;
- use binary reappearance as recovery.

## Predeployment freeze

Before the first outcome-bearing optical deployment freeze:

- node list and alternates;
- optical sensor model, primary angular-response class and matched-class calibration reference;
- placement geometry and tolerance;
- anti-fouling / cleaning / drift rules;
- sampling interval;
- common-overlap rule;
- DLI integration code;
- variation gate;
- TNC pairing and destructive-sampling rules;
- primary model and uncertainty code;
- epiphyte biomass leaf class/method if retained;
- paired leaf-optics pilot and cleaning method if retained;
- future survey window.
