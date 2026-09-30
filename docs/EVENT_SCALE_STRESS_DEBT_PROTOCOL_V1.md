# Tampa event-scale hot-fresh stress debt protocol v1

## Goal

Test one specific unresolved mechanism:

> Does high-frequency local hot-fresh exposure deplete below-ground reserve in established *Thalassia testudinum* meadows?

The retrospective annual/segment analyses already tested temperature and salinity, including the published Tampa 30 C / 25 ppt hot-fresh definition, without a supported common mechanism. That retrospective threshold/window search is closed.

The new study changes the measurement scale, not the hypothesis after seeing the result.

## Why retain 30 C and 25 ppt?

Beck et al. (2024, *Estuaries and Coasts*, DOI 10.1007/s12237-024-01385-0) documented increases in Tampa Bay days above 30 C and below 25 ppt and used those values as a suboptimal-condition framework.

The paper also notes that the thresholds were chosen partly because they provided sufficient historical variation. They are not treated here as universal physiological hard limits.

This prospective design therefore asks whether the same Tampa definition becomes informative when measured at 10-15 minute, meadow-local resolution.

## Physiological interpretation of the frozen threshold

The 30 C component must **not** be described as a direct heat-damage threshold for *Thalassia testudinum*.

Classic turtle-grass work places the temperature optimum near 30 C (Zieman 1975, *Aquatic Botany* 1:107-123, DOI 10.1016/0304-3770(75)90016-9). Recent thermal-performance measurements likewise place *T. testudinum* gross-primary-production optimum near 31 C, with a clearer productivity decline above roughly 32 C.

Likewise, marine salinity around 30 is commonly near the species' optimum, although low-salinity pulses can impose osmotic costs.

Therefore this study is not:

> temperature above 30 C causes heat injury.

It is:

> does the already published Tampa **joint hot-fresh condition** (>=30 C and <=25 ppt), when measured at meadow/event scale, carry information about reserve depletion?

A supported result is interpreted as a compound event-complex association. It does not identify 30 C itself as harmful.

## Sampling frame

Use stable fixed-transect nodes in:

- Old Tampa Bay;
- Middle Tampa Bay;
- Lower Tampa Bay.

Attempt census-oriented deployment at every contemporaneously baseline-*Thalassia*-positive node.

Historical planning frame:

- Old: 8;
- Middle: 11;
- Lower: 14;
- total: 33.

Confirmatory minimum:

- 30 analyzable nodes total;
- at least 8 per bay.

Below this gate, the result is a pilot estimate. A null cannot reject event-scale stress debt.

## Frozen deployment calendar

A response-independent preflight scanned every non-wrapping 42-day calendar window using the pinned Beck et al. daily GAM exposure artifact for 1998-2022. The selection rule was frozen before inspection: maximize the **second-highest** bay-specific fraction of station-years with at least one joint 30 C / 25 ppt day, matching the prospective requirement for variation in at least two bays.

Selected calendar:

> **July 24 through September 3**

Historical station-year fraction with at least one joint day in this window:

- Old Tampa Bay: **0.632**;
- Middle Tampa Bay: **0.363**;
- Lower Tampa Bay: **0.000**.

Across historical years, at least two core bays had some joint-event occurrence in **64%** of years; all three bays did so in **0%**.

This is an important design warning, not a reason to optimize again. The future node-scale exposure may fail the frozen variation gate.

If it fails:

> classify the primary hot-fresh exposure as **non-estimable**.

Do not move the deployment to another season, alter 30 C or 25 ppt, extend the window, or drop Lower Tampa Bay after seeing exposure or TNC.

Lower Tampa Bay remains in the deployment because its low-exposure state is ecologically informative context and because the same synchronized post-exposure TNC can contribute to the independently frozen reserve -> future-state study. However, zero exposure in LTB does not count as within-bay exposure variation.

## Synchronized exposure window

Target:

- fixed calendar target: July 24 through September 3;
- 42 days continuous deployment;
- all starts within 7 days of the frozen July 24 start;
- all retrievals within 7 days of the frozen September 3 end;
- primary exposure calculated only over the common calendar overlap shared by confirmatory nodes;
- minimum common overlap 35 days.

Do not compare different seasonal/weather windows and interpret them as spatial exposure.

## Sensor layer

Primary sensors:

- temperature;
- conductivity / salinity.

Sampling interval:

- <=15 minutes.

Target sampling center:

- 0.20 m above sediment.

The instrument family, mounting geometry and allowable height tolerance are frozen in a response-independent field pilot.

Record node, GPS, serial number, height above bed, deployment/retrieval time, depth, calibration metadata, fouling, burial or exposure events.

### QC

Freeze before deployment:

- pre/post calibration;
- temperature drift tolerance;
- conductivity/salinity drift tolerance;
- clock drift tolerance;
- anti-fouling method;
- salinity conversion;
- gap/interpolation rule.

Each confirmatory node requires >=85% paired temperature-salinity coverage over the common window.

## Pre/post reserve sampling

### Pre-exposure

Within 3 days of logger deployment, collect >=3 new adjacent rhizome cores per node under the frozen TNC tissue and HPLC protocol.

Node summary:

tnc_pre = median TNC across valid pre-exposure cores.

### Post-exposure

Within 3 days of logger retrieval, collect >=3 new non-overlapping adjacent cores per node using the same protocol.

Node summary:

tnc_post = median TNC across valid post-exposure cores.

The stable transect node is the inferential unit. Cores are measurement replicates, not independent genets.

## Pre/post TNC temporal pairing

The event-to-reserve response is a change across one fixed exposure interval, so pre/post reserve sampling must not drift across unequal seasonal durations.

For confirmatory nodes:

- target pre-to-post TNC interval: **42 days**;
- allowable confirmatory interval: **39-45 days**;
- pre cores remain within 3 days of that node's logger deployment;
- post cores remain within 3 days of that node's logger retrieval;
- route planning should revisit each node on approximately the same relative day of the 42-day campaign.

A node with pre/post TNC samples outside 39-45 days is descriptive-only for the primary event-to-reserve model.

Do not widen this interval after seeing TNC, and do not add interval length as a post-hoc covariate to rescue the primary coefficient.

This guardrail is separate from the common logger-overlap rule: high-frequency exposure is calculated on the frozen common calendar overlap, while reserve change is measured over a tightly matched node-level biological interval.

## Combined destructive-sampling guardrail

The event study requires two TNC rounds, so destructive sampling itself is treated as a potential intervention.

Primary rule:

> **pre-exposure and post-exposure are the only outcome-bearing TNC rounds.**

If the post-exposure sample is used as the independently frozen clonal-program baseline TNC, do **not** collect a third redundant TNC round.

At each node:

- target 3 valid pre-exposure cores and 3 valid post-exposure cores;
- freeze any replacement-core rule and the absolute maximum number of attempted cores before deployment;
- use the same frozen minimum perpendicular buffer from the permanent monitoring transect as the clonal TNC program;
- never core on a permanent meter mark or inside the routine monitoring footprint;
- at each frozen q25/q50/q75 anchor neighborhood, place pre and post cores at distinct predeclared lateral/perpendicular offsets;
- do not re-core a pre-exposure hole or its immediately disturbed rhizosphere;
- freeze core diameter, depth and the **maximum cumulative disturbed area per node across both rounds** before the first core;
- backfill/restore every hole under the monitoring authority protocol and record visible disturbance after each round.

If future point-level monitoring allows, retain the already declared disturbance sensitivity that removes the fixed permanent meter-mark neighborhood nearest the TNC anchor set.

A strong difference between full-transect and disturbance-excluded future results is reported as a **measurement-intervention concern**, not hidden or interpreted as reserve ecology.

## Primary exposure

For each synchronized observation:

~~~text
hot   = temperature >= 30 C
fresh = salinity <= 25 ppt
joint = hot AND fresh
~~~

Primary node exposure:

joint_hot_fresh_hours_30_25

calculated as:

~~~text
common_overlap_hours
x fraction(valid paired observations satisfying joint)
~~~

### Exposure-variation and identifiability gate

Before fitting the biological response, all of the following must hold:

- >=10 confirmatory nodes have non-zero joint exposure;
- non-zero exposure occurs in >=2 core bays;
- >=2 core bays each contain >=6 analyzable nodes;
- in each of those counted bays, the node-level joint exposure contains >=3 distinct values.

The last rule matters because the primary model includes `water_body`. A signal that is only "OTB high / MTB lower / LTB zero" is a bay contrast, not identified node-scale event stress.

If fewer than two bays satisfy the within-bay variation rule, classify the primary exposure as **non-estimable**.

Do not:

- remove `water_body` to make the exposure coefficient estimable;
- aggregate to bay means and call the result node-scale;
- alter thresholds;
- move the July 24-September 3 deployment;
- extend the exposure window;
- drop a bay or select a favorable node subset.

Small but nonzero within-bay variation is handled by the coefficient uncertainty/precision, not by inventing another threshold.

## Primary reserve model

~~~text
tnc_post
  ~ tnc_pre
  + joint_hot_fresh_hours_30_25
  + water_body
~~~

Expected event-exposure coefficient: negative.

Support rule:

- two-sided 95% interval entirely below 0: supported;
- entirely above 0: opposite direction;
- overlaps 0: unsupported;
- sample/coverage/exposure gate failure: non-estimable.

Do not switch to one-sided inference after inspection.

## Resolution

Approximate 80%-power two-sided detectable partial correlations:

- n=24: ~0.52;
- n=30: ~0.47;
- n=33: ~0.45;
- n=40: ~0.41.

This remains a moderate-to-large-effect design. High-frequency sensor rows do not create extra ecological replicates.

## Secondary diagnostics

Freeze and report:

- hot hours >=30 C;
- fresh hours <=25 ppt;
- temperature p95;
- salinity p05.

These diagnose the joint metric only. They cannot rescue the primary result.

## Two-gate stress-debt chain

The post-exposure TNC sample may also serve as the independently frozen clonal-program baseline predictor if it satisfies all clonal timing and assay rules.

Gate A:

> joint hot-fresh exposure predicts lower post-TNC after pre-TNC is represented.

Gate B:

> higher post-TNC predicts more positive / less negative future focal-frequency change.

Both supported:

> consistent with event stress -> reserve depletion -> future persistence.

This is not formal mediation or experimental causal proof.

Do not add a stress x TNC interaction after outcome access.

## Dynamic reserve-change to future-state diagnostic

The strongest common-cause alternative is a persistent site template: some stable, incompletely measured property could make a node both high in TNC and more stable later.

The pre/post TNC design allows one stronger, still-observational diagnostic without collecting another biological layer.

Define:

```text
delta_tnc_42d = tnc_post - tnc_pre
```

using only nodes whose pre/post TNC samples pass the frozen 39-45 day interval, assay, spatial-core and destructive-sampling rules.

Pair `tnc_post` to its post-exposure fixed-transect baseline under the already frozen clonal timing rule, then predeclare:

```text
future_delta_frequency
  ~ baseline_frequency_post
  + tnc_pre
  + delta_tnc_42d
  + water_body
```

Expected `delta_tnc_42d` direction: **positive**.

Interpretation:

- two-sided 95% interval entirely above zero -> within-node reserve maintenance/recovery carries prospective information about later quantitative stability;
- interval entirely below zero -> opposite direction;
- interval overlaps zero -> unsupported.

Why this is useful:

> a within-node reserve change is less compatible with a purely time-invariant site-quality explanation than a static TNC difference among nodes.

Why it is still not causal proof:

- time-varying local processes can affect both reserve change and future meadow state;
- measurement error in difference scores can be large;
- no random manipulation of reserve occurred.

This is a **secondary site-template-resistant diagnostic**.

It cannot rescue:

- a null primary TNC -> future-state result;
- a null/non-estimable event -> TNC result.

Do not drop `tnc_pre` or `water_body`, switch to one-sided inference, or select only nodes with favorable reserve change after outcome access.

If the hot-fresh exposure itself fails its variation gate, this diagnostic may still be estimated because it asks about measured reserve change, not event attribution.

## Secondary future-state test

Predeclare only as secondary:

~~~text
future_delta_frequency
  ~ baseline_frequency
  + joint_hot_fresh_hours_30_25
  + water_body
~~~

Expected direction: negative.

It cannot rescue a null stress-to-reserve primary.

## Relationship to PR #38

PR #38 remains a separate six-node Old Tampa Bay extreme-effect heat-only pilot.

It is genuinely prospective, but its small-n rejection boundary means it is not the network-scale event-stress mechanism test and its null cannot veto this study.

## Co-event attribution boundary

Hot-fresh events can coincide with a broader rainfall/runoff event complex:

- cloud-driven or turbidity-driven low light;
- freshwater-plume transport;
- changes in dissolved oxygen;
- sediment or other local disturbance.

Therefore even a supported primary result does not uniquely prove that temperature and salinity are the proximate physiological drivers.

If resources allow, co-locate PAR, turbidity and/or dissolved-oxygen measurements as response-independent event context. These variables are not added to or removed from the primary hot-fresh model after seeing TNC.

If the primary hot-fresh result is supported, describe it as a **hot-fresh event-complex association with reserve depletion** unless separate frozen measurements identify the proximate pathway.

A null hot-fresh result cannot be rescued by adding a favorable event-context covariate after inspection.

## Separate optical mechanism

PAR/light stress remains a separate mechanism layer.

Do not add PAR to the hot-fresh primary model after seeing results. Leaf/canopy optical stress should have its own frozen measurement contract.

## Claim boundary

A supported result means local event-scale hot-fresh exposure is associated with subsequent depletion of measured rhizome reserve under a response-frozen prospective design.

It does not mean:

- 30 C / 25 ppt are universal physiological limits;
- hot-fresh exposure is the only driver of TNC;
- reserve depletion mediates future meadow decline unless the independent TNC-to-future gate also supports that link;
- binary re-recording is ecological recovery.
