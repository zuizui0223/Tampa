# Three independent ecology programmes — executable status

## 1. Azores — two-stage mobility control

### Completed
- EOG seed clue separated from ecological claim;
- Europe-wide public eel panel audited;
- exact Durif cohort identified;
- successful-migrant endpoint analysed with project and timing/size controls;
- full six-project migration files recovered through Git blob API;
- migration-initiation analysis completed;
- initiation-versus-completion decomposition completed;
- Dutch consecutive-barrier confirmation protocol and schema gate implemented.

### Current developmental result

#### Migration initiation
Among 575 tracked FIII/FIV/FV individuals, after applying the source-study 2015 expert nonmigrant exclusions:

- FIII initiation: **59.0%**
- FIV initiation: **77.9%**
- FV initiation: **87.4%**

Adjusted model:
- project × release year fixed effects;
- within-stratum body length;
- within-stratum release timing.

Durif effect:
- OR **2.08** per FIII -> FIV -> FV increment;
- 95% CI **1.56–2.76**;
- p approximately **4.2e-7**.

#### Completion after initiation
Among **422 initiators**:

- adjusted Durif OR **1.15**;
- 95% CI **0.83–1.59**;
- p = **0.41**.

### Interpretation

> **Internal migratory readiness strongly regulates whether migration is expressed, but does not provide a general advantage for completion once movement has begun.**

The downstream ecological filter is unresolved.

Barrier/hydrological opportunity is now the confirmation target, not an assumed explanation.

### Next decisive input
- Dutch consecutive-barrier dataset, DOI 10.17026/LS/WTSUNG;
- run `analysis/08_dutch_barrier_confirmation_gate.py` after download;
- test whether passage opportunity/barrier identity explains post-initiation fate and whether that effect depends on Durif stage.

---

## 2. Louisiana — within-home-range micro-niche tracking

### Completed
- EOG detection anomaly separated from ecological claim;
- Lake Erie independent design frozen before file-level response analysis;
- individual bird fixed as the biological replication unit;
- SRI/state-retention metric implemented;
- Lake Erie schema gate implemented;
- South Carolina 2026 King Rail telemetry added as broad-relocation boundary;
- fully public Senegal Delta Godwit dataset identified;
- Dryad dataset/version/file IDs resolved;
- Godwit fetcher and seasonal geography-vs-habitat-state analysis implemented;
- Godwit external-generality contract frozen.

### Primary hypothesis

> **A resident wetland bird can move inside familiar space so that the environmental state it experiences varies less than time-matched local availability.**

### Primary King Rail test
Lake Erie published design:
- 10 birds with stabilized home ranges;
- 206 used/homing surveys;
- 401 nearby random surveys;
- repeated water-depth and vegetation measurements.

Primary metric:
- individual SRI.

### Current access boundary
Dryad metadata and file IDs are public and resolved for the Godwit generality panel, but direct file downloads from this execution environment are blocked by the provider security/download layer.

Lake Erie Zenodo files remain similarly unresolved in this environment.

No SRI or Godwit numerical result is claimed until actual file bytes are read.

### Independent ecological boundary
South Carolina King Rails:
- 9 birds with both breeding and non-breeding telemetry;
- 5/9 shifted seasonal home ranges;
- mean shift about 2.9 km, range 0.7–7.5 km.

This supplies the predicted broad-relocation regime when local habitat-state compensation fails.

### Next decisive input
Primary:
- Lake Erie archive files with bird/event/used-random/water-depth linkage;
- run `analysis/04_state_fidelity_gate.py` then `analysis/05_state_retention_index.py`.

Parallel generality:
- Senegal Delta Godwit `location_data.csv` + `habitat_use_df.csv`;
- run `analysis/07_godwit_seasonal_state_displacement.py`.

---

## 3. Tampa — buffered persistence under quantitative degradation

### Completed
- retrospective state decoupling established;
- Tampa positioned as the third independent ecological programme;
- TNC selected as first decisive prospective mechanism test;
- Boca Ciega added prospectively before outcome-bearing sampling;
- four-bay `clonal_state_prospective_v2` contract frozen;
- precollection freeze schema added;
- collection manifest added;
- fail-closed baseline validator added;
- actual 41-node historical field-planning registry generated and committed;
- reproducible registry exporter and registry validator added;
- raw pilot-record schemas added for HPLC QC, tissue class, core geometry, preservation latency and transect offset;
- raw-pilot -> candidate-summary builder added;
- existing fail-closed method-pilot validator strengthened to require calibration identity and all matrix spikes within 85–115%.

### Historical four-bay candidate registry

Total: **41 nodes**

By bay:
- Old Tampa Bay: **8**
- Middle Tampa Bay: **11**
- Lower Tampa Bay: **14**
- Boca Ciega Bay: **8**

Core-design classes:
- three distinct spatial anchors: **38**
- single-mark / three-offset fallback: **2**
- two-mark / one repeated-anchor fallback: **1**

Historical latest state:
- 2025: **32 nodes**
- 2024: **9 nodes**

Every row remains explicitly:
- `historical_only = TRUE`
- `contemporaneous_eligibility = PENDING`

The registry is field planning, not current biological eligibility.

### Confirmatory baseline gate
- >=36 analyzable nodes;
- >=6 per bay;
- the six-node per-bay floor is a representation guardrail; the >=36 total-node requirement carries the main precision burden;
- <=28-day synchronized campaign;
- paired baseline survey within +/-14 days;
- >=3 valid cores per node;
- one frozen HPLC TNC method.

### Current hard stop
The fail-closed validator intentionally returns STOP until response-independent pilot/logistics freeze:
- campaign dates;
- horizontal rhizome tissue class;
- minimum transect offset;
- core diameter;
- core depth;
- maximum collection-to-preservation time;
- preservation method;
- assay-batch randomization rule.

### Next decisive input
- populate the raw pilot-record schemas with response-independent Thalassia tissue/HPLC/field-pilot measurements;
- run `validation/build_tnc_v2_method_pilot_summary.py`;
- require `PASS_METHOD_PILOT` from `validation/validate_tnc_v2_method_pilot.py`;
- then copy the accepted method fields once into the authoritative precollection freeze;
- complete `field/tnc_v2_precollection_freeze.json`;
- contemporaneously recheck all 41 historical candidates before coring.

---

# Current order of work

1. **Azores:** obtain/run Dutch within-landscape barrier confirmation.
2. **Louisiana:** obtain Lake Erie matched-event files; in parallel run the open Godwit generality test when Dryad file bytes are accessible.
3. **Tampa:** finish response-independent tissue/assay/logistics pilot, then convert the 41-node historical registry into the contemporaneous eligible field cohort.

These remain three separate ecological papers. Any later synthesis is secondary.
