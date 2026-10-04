# Three independent ecology programmes — executable status

These are three separate ecological projects. EOG is only the discovery route.

---

## 1. Azores — phase-specific control of eel migration

### Current paper-level question

> **Does the effect of internal migratory readiness attenuate after migration has been activated?**

### Completed evidence

Six Europe-wide projects with exact FIII/FIV/FV stage and compatible migration reconstruction.

Canonical source-study expert corrections are preserved.

#### Gate 1 — activation

Expert-corrected migration initiation:

- FIII: **154/261 = 59.0%**
- FIV: **53/68 = 77.9%**
- FV: **215/246 = 87.4%**

Adjusted initiation model:

- OR per FIII -> FIV -> FV increment: **2.08**
- 95% CI **1.56–2.76**
- p approximately **4.2e-7**

Censored onset timing:

- stratified Cox HR per stage: **1.28**
- 95% CI **1.12–1.45**
- p = **0.00022**

#### Gate 2 — progression after activation

Conditional completion:

- adjusted Durif OR: **1.15**
- 95% CI **0.83–1.59**
- p = **0.412**

Post-initiation migration speed:

- multiplicative stage ratio: **0.983**
- 95% CI **0.852–1.134**
- p = **0.815**

#### Direct phase interaction — primary novel evidence

- OR(initiation) / OR(completion): **1.81**
- cluster-robust 95% CI **1.15–2.84**
- p = **0.0099**

The stage effect is therefore significantly stronger at activation than after activation.

#### External-context bridge

Project median WRS:

- vs initiation: rho **+0.029**, exact p **0.983**
- vs completion after initiation: rho **-0.928**, exact p **0.022**

This is bridge evidence only because WRS is project-confounded.

#### Independent Dutch constraint

The 2026 pump -> lake -> tidal-sluice study is compatible with stronger post-activation control by:

- discharge opportunity;
- wind;
- lunar illumination;
- prior barrier experience;
- route-specific movement/body-condition effects.

Durif does not remain a clean generic passage predictor.

### Paper status

**Story spine frozen.**

Canonical files:
- docs/PAPER_SPINE_PHASE_CONTROL_V1.md
- docs/CLAIM_EVIDENCE_MAP_PHASE_CONTROL_V1.md
- docs/novelty_boundary.md
- docs/specific_general_principle.md

### Current main interpretation

> **Internal silvering state strongly predicts entry into migration; its general predictive advantage attenuates during progression, when route-specific opportunity increasingly filters realised movement.**

Do not claim a complete switch from internal to external control.

---

## 2. Louisiana — within-home-range micro-niche tracking

### Primary question

> **Do resident wetland birds move within familiar space so that the environmental state they experience varies less than local time-matched availability?**

### Primary Lake Erie design

Published structure:

- 10 birds with stabilized home ranges;
- 206 used/homing microhabitat surveys;
- 401 nearby random surveys;
- intended one used + two 75-m random points per event;
- sampling within 72 h;
- repeated water depth and vegetation measurements.

Primary statistic:

~~~text
SRI
= 1 - variance(used environmental state)
      / median variance(matched-availability pseudo-trajectories)
~~~

Biological replication unit:

**individual bird (n=10)**

not the 607 point records.

### Implemented

- state-fidelity schema gate;
- SRI randomization analysis;
- South Carolina same-species broad-relocation boundary;
- Senegal Delta Godwit external-generality contract and analysis;
- second Lake Erie movement-data route through the 2025 bagged-movement supplement;
- generic supplement scanner for King Rail individual/time/coordinate tables.

### Data-access state

#### Route A — 2023 Lake Erie Zenodo

Paper states data/code are at Zenodo 6604660.

The current execution environment has not resolved/downloaded its physical files.

#### Route B — 2025 bagged movement supplement

The article explicitly states King Rail movement data are included in:

~~~text
ECE3-15-e72060-s001.zip
Appendices S1-S13
~~~

A scanner is ready:

~~~bash
python analysis/08_scan_bagged_movement_supplement.py --zip <ZIP>
~~~

Movement coordinates alone cannot replace paired habitat availability for SRI.

#### Route C — Godwit external generality

Dryad DOI 10.5061/dryad.4tmpg4fm3 contains:

- 22-bird GPS data;
- wet/dry seasonal habitat composition;
- scripts.

Dryad metadata/file IDs are public, but current direct file download requires/encounters repository access constraints in this environment.

Fetcher and geography-vs-state analysis are implemented.

### Independent ecological boundary

2026 South Carolina King Rail telemetry:

- 9 birds with both breeding and non-breeding data;
- 5/9 shifted seasonal home ranges;
- mean shift about 2.9 km, range 0.7–7.5 km.

This represents the predicted broader-relocation regime when local habitat-state compensation fails.

### Current hard stop

No SRI value is claimed until actual event-linked Lake Erie files are obtained.

---

## 3. Tampa — buffered persistence under quantitative degradation

### Current ecological question

> **What allows a sessile foundation species to remain present while quantitative condition deteriorates, and which hidden buffer predicts future persistence?**

### Supported retrospective result

Recorded presence can remain stable while:

- within-transect frequency;
- abundance;
- blade length;
- shoot density;
- community composition

change substantially.

External Zostera monitoring reproduces the broad binary–quantitative state-decoupling pattern.

### Mechanism priority

**TNC first.**

Four-bay v2 prospective frame fixed before future outcome-bearing sampling:

- Old Tampa Bay: 8 recent positive nodes
- Middle Tampa Bay: 11
- Lower Tampa Bay: 14
- Boca Ciega Bay: 8
- planning total: **41 nodes**

Primary confirmatory gate:

- >=36 analyzable nodes
- >=8 per bay
- <=28-day synchronized campaign
- baseline survey within +/-14 d
- >=3 valid cores/node
- one frozen HPLC TNC workflow

### Implemented fail-closed field infrastructure

- results/clonal_state_prospective_v2_contract.json
- field/tnc_v2_precollection_freeze.json
- field/tnc_v2_collection_manifest.csv
- validation/validate_tnc_v2_baseline.py
- docs/TAMPA_DECISIVE_TEST_PRIORITY_V1.md

The validator returns STOP until the response-independent pilot freezes:

- rhizome tissue class;
- transect offset;
- core diameter/depth;
- maximum preservation delay;
- preservation method;
- assay-batch randomization;
- campaign dates.

### Next physical mechanism lines

Second:
- direct canopy hydrodynamic self-facilitation.

Third:
- community functional insurance.

Do not combine mechanisms post hoc to rescue a null TNC result.

---

# Active execution order

1. **Azores:** analysis/story is sufficiently closed for manuscript drafting; no further exploratory model family is needed before drafting.
2. **Louisiana:** obtain either Lake Erie Zenodo files or the 2025 supplement ZIP; run the prepared scanner/gates; compute SRI only if paired habitat availability survives.
3. **Tampa:** complete response-independent tissue/HPLC + field logistics pilot, then fill the precollection freeze and run the validator before sampling.

## Hard boundary

The target remains **three independent ecological papers**, not one universal-rule paper.
