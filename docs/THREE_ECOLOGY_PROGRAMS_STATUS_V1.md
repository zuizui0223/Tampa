# Three independent ecology programmes — current executable status

These are three separate ecological papers. EOG is provenance/discovery only.

---

## 1. Azores — phase-specific control of eel migration

### Paper-level question

> **Does the effect of internal migratory readiness attenuate after migration has been activated?**

### Current evidence

Gate 1 — activation:

- expert-corrected initiation:
  - FIII **154/261 = 59.0%**
  - FIV **53/68 = 77.9%**
  - FV **215/246 = 87.4%**
- adjusted initiation OR per FIII -> FIV -> FV increment: **2.08**
- 95% CI **1.56–2.76**
- p approximately **4.2e-7**
- censored onset HR per stage: **1.28**
- 95% CI **1.12–1.45**
- p = **0.00022**

Gate 2 — progression after activation:

- conditional completion Durif OR **1.15**
- 95% CI **0.83–1.59**
- p = **0.412**
- post-initiation migration-speed stage ratio **0.983**
- 95% CI **0.852–1.134**
- p = **0.815**

Direct phase interaction:

- OR(initiation) / OR(completion) = **1.81**
- cluster-robust 95% CI **1.15–2.84**
- p = **0.0099**

### Current interpretation

> **Internal silvering state strongly predicts entry into migration; its general predictive advantage attenuates during progression, when route-specific opportunity increasingly filters realised movement.**

Project-level WRS is bridge evidence only because resistance is project-confounded.

### Status

**Analysis/story closed enough for manuscript drafting.**

Canonical:
- `docs/PAPER_SPINE_PHASE_CONTROL_V1.md`
- `docs/CLAIM_EVIDENCE_MAP_PHASE_CONTROL_V1.md`

No new exploratory model family is required before drafting.

---

## 2. Louisiana — hydrological buffering inside resident home ranges

### Paper-level question

> **Do resident King Rails buffer the water-depth variation they experience relative to local time-matched habitat availability?**

### Independent Lake Erie result

Source-defined QC:

- 607 source microhabitat rows;
- 17 source-defined missing rows excluded;
- 2 malformed IDs excluded without repair;
- **190 valid matched events**
- **10 individual birds**
- 173 strict two-random events.

State Retention Index:

- **10/10 birds SRI > 0**
- median SRI **0.886**
- range **0.402–0.976**
- sign-test p **0.00098**
- strict two-random subset: 10/10 positive, median **0.882**

Time-ordered state retention:

- **10/10 positive**
- median **0.658**
- strict subset median **0.667**
- 10/10 individually p < 0.05.

Availability coupling:

- pooled used-on-local-availability slope **0.162**
- pseudo-used null median **1.001**
- coupling reduction **83.8%**
- 10/10 birds below own null median
- flooded-habitat sensitivities retain **82–85.5%** reduction.

Buffering-limit decomposition:

- 10/10 birds below pseudo-null mismatch slope;
- **9/10** retain positive buffering during top-quartile local hydrological mismatch;
- median extreme retention **0.629**;
- buffering is strong but not unlimited.

### Current interpretation

> **Repeated realised microhabitat use strongly dampens temporal hydrological variation experienced by resident King Rails relative to what is locally available.**

### Boundary

The public UTM coordinate files lack a verified event/date key.

Therefore do **not** say measured geographic displacement caused the hydrological buffering.

Supported:
- realised microhabitat use buffers state.

Unresolved:
- direct movement-distance -> state-retention mechanism.

### Status

**Paper spine now frozen.**

Canonical:
- `docs/PAPER_SPINE_HYDROLOGICAL_BUFFERING_V1.md`
- `docs/CLAIM_EVIDENCE_MAP_HYDROLOGICAL_BUFFERING_V1.md`
- `docs/lake_erie_state_fidelity_result.md`
- `docs/lake_erie_availability_coupling.md`

Further Lake Erie post-hoc metrics should stop unless they resolve:
1. coordinate-event linkage;
2. exact independent replication;
3. a dynamic habitat surface that directly tests portfolio failure.

---

## 3. Tampa — buffered persistence under quantitative degradation

### Paper-level ecological question

> **What allows a sessile foundation species to remain present while quantitative condition deteriorates, and which hidden buffer predicts future persistence?**

### Supported retrospective result

Recorded occurrence can remain stable while:

- within-transect frequency;
- abundance;
- blade length;
- shoot density;
- community composition

change substantially.

A separate Zostera monitoring panel reproduces broad binary–quantitative state decoupling.

No retrospective candidate mechanism is promoted as causal.

### First decisive prospective mechanism

**Rhizome TNC first.**

Authoritative four-bay v2 planning frame:

- Old Tampa Bay: 8 recent positive nodes
- Middle Tampa Bay: 11
- Lower Tampa Bay: 14
- Boca Ciega Bay: 8
- planning total: **41**

Confirmatory gate:

- **>=36 analyzable nodes total**
- **>=6 analyzable nodes per bay**
- >=3 valid cores/node
- one <=28-day TNC campaign
- baseline survey within +/-14 d
- one frozen HPLC workflow.

The >=6/bay floor is a representation guardrail allowing limited field/QC attrition; the >=36 total gate carries the main precision requirement.

Primary model is already frozen:

~~~text
future_delta_frequency
  ~ baseline_frequency
  + baseline_Braun_Blanquet
  + z_rhizome_TNC
  + water_body
~~~

with water-body-stratified node bootstrap, 10,000 replicates, seed 20261003.

### Method-pilot authority

Current authoritative pipeline:

~~~text
raw response-independent pilot records
 -> build_tnc_v2_method_pilot_summary.py
 -> validate_tnc_v2_method_pilot.py
 -> PASS_METHOD_PILOT
 -> 69_apply_tnc_v2_method_pilot.py
 -> tnc_v2_precollection_freeze.json
 -> validate_tnc_v2_baseline.py
~~~

Legacy `tnc_v2_pilot_freeze.json` is deprecated/provenance only.

### Current hard stop

Outcome-bearing coring is **not authorized** until response-independent pilot/logistics freeze:

- campaign dates;
- horizontal-rhizome tissue class;
- transect offset;
- core diameter/depth;
- maximum preservation delay;
- preservation method.

Assay-batch randomization is already frozen.

### Status

Scientific contract and software are ready.

The remaining decisive input is **physical field/laboratory pilot evidence**, not another retrospective analysis.

---

# Active order

1. **Azores:** draft manuscript from frozen phase-control spine.
2. **Louisiana:** draft manuscript from frozen hydrological-buffering spine; pursue coordinate-event linkage only if an authoritative mapping source appears.
3. **Tampa:** execute response-independent method/field pilot; do not begin outcome-bearing TNC cores before PASS_METHOD_PILOT and baseline validator readiness.

## Hard boundary

The target remains **three independent ecological papers**.

Do not merge them into one universal-rule manuscript.
