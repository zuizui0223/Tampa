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

## Synchronized exposure window

Target:

- 42 days continuous deployment;
- all starts within 7 days;
- all retrievals within 7 days;
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

### Exposure-variation gate

Before fitting the biological response:

- >=10 confirmatory nodes must have non-zero joint exposure;
- non-zero exposure must occur in >=2 core bays.

If this fails, classify the primary exposure as non-estimable.

Do not alter thresholds, deployment dates or node membership to create variation.

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
