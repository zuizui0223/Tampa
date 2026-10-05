# Three independent ecology programmes derived from EOG — current scientific state

These are three **separate ecological papers**. EOG is provenance/discovery only.

The point of keeping them together in this status document is not to force one
umbrella theory, but to keep the biological distinction and evidence boundary
clear.

---

## 1. Azores — phase-specific control of eel migration

### Biological question

> **Does internal migratory readiness control the activation of migration more
> strongly than it controls what happens after migration has begun?**

The Flores yellow-eel system supplied the original clue: extreme residency in a
taxon capable of large-scale migration.

The Europe-wide public eel panel now resolves migration into two sequential
gates.

### Gate 1 — activation

Expert-corrected initiation rates:

- FIII: **154/261 = 59.0%**
- FIV: **53/68 = 77.9%**
- FV: **215/246 = 87.4%**

Adjusted Durif-stage effect:

- OR per FIII -> FIV -> FV increment: **2.08**
- 95% CI: **1.56–2.76**
- p approximately **4.2e-7**

Time to onset:

- HR per stage: **1.29**
- 95% CI: **1.13–1.47**
- p = **0.00016**

### Gate 2 — progression/completion after activation

Among activated eels:

- completion OR per stage: **1.15**
- 95% CI: **0.83–1.59**

Post-activation migration-speed ratio per stage:

- **0.983**
- 95% CI: **0.852–1.134**

### Direct phase test

The stage effect is significantly stronger at activation than at completion:

- initiation/completion OR ratio: **1.81**
- 95% CI: **1.15–2.84**
- p = **0.0099**
- direction preserved in **6/6** leave-one-project-out analyses.

### Current ecological interpretation

> **Internal silvering state strongly controls entry into the migratory movement
> state, but its general predictive advantage attenuates once migration is
> underway.**

This separates **readiness to move** from **ability to realise movement through a
route**.

Project-level WRS alignment is contextual only, not causal.

### Status

**Scientific analysis closed for drafting.**

Canonical source:
- `results/phase_control_canonical_v1.json`
- `manuscript/AZORES_PHASE_CONTROL_MANUSCRIPT_V2.md`

---

## 2. Louisiana — hydrological buffering inside resident home ranges

### Biological question

> **Can a resident wetland bird repeatedly use local microhabitats so that the
> hydrological state it experiences varies less through time than the habitat
> available around it?**

This is not another habitat-selection analysis.

The western Lake Erie King Rail archive provides time-matched used and nearby
random microhabitat observations.

### Independent Lake Erie result

After source-defined QC:

- **190** valid matched events;
- **10** birds.

State Retention Index:

- **10/10** birds positive;
- median SRI **0.886**;
- exact sign-test p **0.00098**.

Time-ordered state retention:

- **10/10** positive;
- median **0.658**.

Hydrological availability coupling:

- observed used-on-availability slope **0.162**;
- matched pseudo-used null median **1.001**;
- coupling reduction **83.8%**;
- **10/10** birds below their own null median.

The pattern survives restriction to flooded habitat.

Under top-quartile local hydrological mismatch:

- **9/10** birds retain positive buffering;
- median extreme-state retention **0.629**.

### Current ecological interpretation

> **King Rails repeatedly occupy a substantially smoother hydrological
> trajectory than the local habitat available at the same times.**

This is fine-scale regulation of the **experienced environment** inside resident
home ranges.

The separate coordinate archive cannot be joined unambiguously to event IDs, so
the paper does **not** claim that measured geographic displacement caused the
buffering.

### Status

**Scientific analysis closed for drafting.**

Canonical source:
- `manuscript/MANUSCRIPT_NUMERIC_CONTRACT_V1.json`
- `manuscript/LOUIS_HYDROLOGICAL_BUFFERING_MANUSCRIPT_V1.md`

---

## 3. Tampa — buffered persistence under quantitative degradation

### Biological question

> **What allows a sessile foundation species to remain present while its
> quantitative condition deteriorates, and which hidden buffer predicts its
> future state?**

Unlike the two animal systems, *Thalassia* cannot relocate to reduce ecological
mismatch.

### Retrospective result already supported

Recorded occurrence can remain stable while finer meadow dimensions change:

- focal frequency;
- Braun–Blanquet abundance;
- blade length;
- shoot density;
- community composition.

An external *Zostera marina* panel reproduces the broad binary–quantitative
state-decoupling pattern.

Simple annual environment, local propagation and several known-truth hidden-state
explanations do not identify one common mechanism.

### Prospective mechanism programme

Candidate buffers are deliberately separated.

1. **internal biological reserve**
   - rhizome TNC;
   - regenerative meristem state.

2. **self-engineered physical buffer**
   - canopy-specific hydrodynamic attenuation.

3. **community functional buffer**
   - whether alternative seagrass canopies preserve function as focal
     *Thalassia* declines.

### Decisive first test

**Four-bay rhizome TNC prospective design.**

Planning frame:

- Old Tampa Bay: 8 nodes;
- Middle Tampa Bay: 11;
- Lower Tampa Bay: 14;
- Boca Ciega Bay: 8;
- total: **41**.

Confirmatory gate:

- >=36 analyzable nodes total;
- >=6 analyzable nodes per bay;
- >=3 valid cores per node;
- one <=28-day campaign;
- paired baseline within +/-14 days;
- one frozen HPLC TNC workflow.

Primary model is already frozen:

~~~text
future_delta_frequency
  ~ baseline_frequency
  + baseline_Braun_Blanquet
  + rhizome_TNC
  + water_body
~~~

### Current hard stop

The analysis is ready; the missing information is **physical field/laboratory
pilot data**, not another retrospective model.

The repository intentionally stops until response-independent pilot measurements
fix tissue class, core geometry, preservation timing/method and campaign/resource
constraints.

### Status

**Active science blocker: TNC method/field pilot.**

---

# Why these remain three papers

| Project | Biological problem | Main process | Current evidence |
|---|---|---|---|
| Azores | when does latent mobility become expressed? | internal readiness -> migration activation, then route filtering | phase attenuation directly supported |
| Louisiana | how can residency coexist with environmental variability? | repeated local habitat use buffers experienced hydrology | matched-availability buffering directly supported |
| Tampa | how can a sessile foundation species remain present while condition erodes? | internal / engineered / community buffers | state decoupling supported; mechanism prospective |

The publication goal remains **three independently strong ecological papers**.

Any later synthesis is secondary.
