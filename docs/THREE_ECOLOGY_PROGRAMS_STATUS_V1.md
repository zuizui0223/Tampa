# Three independent ecology programmes — current executable status

These are three separate ecological papers. EOG is provenance/discovery only.

---

## 1. Azores — phase-specific control of eel migration

### Scientific status

**Activation/onset and pooled post-activation speed analyses reproduce exactly. The project-specific speed audit is complete and shows no detectable between-project heterogeneity in the Durif-speed coefficient. Reference SVG render QC PASS.**

Primary evidence:

**Migration activation**
- initiation Durif OR per FIII -> FIV -> FV increment: **2.08**
- 95% CI **1.56–2.76**
- p approximately **4.2e-7**

**Behavioral onset**
- Cox HR per stage: **1.29**
- 95% CI **1.13–1.47**
- p = **0.00016**

**Post-activation progression**
- migration-speed ratio per stage: **0.983**
- 95% CI **0.852–1.134**
- p = **0.815**

Interpretation:
> capture-time silvering readiness strongly predicts whether and when migration becomes behaviorally active, whereas the same Durif-stage gradient is absent from generic post-activation migration speed.

### Endpoint boundary

The upstream terminal-positive file is not a validated binary success/failure variable.

Therefore:
- terminal-set OR **1.15** is secondary sensitivity only;
- former initiation/terminal OR-ratio **1.81** is secondary sensitivity only;
- non-membership is not biological migration failure;
- no escapement probability is estimated here.

### Canonical artifacts

Manuscript:
- `manuscript/AZORES_PHASE_CONTROL_MANUSCRIPT_V3.md`

Numeric/interpretation:
- `results/phase_control_canonical_v2.json`
- `manuscript/MANUSCRIPT_NUMERIC_CONTRACT_V2.json`
- `manuscript/MANUSCRIPT_QC_V2.json` — **PASS**

Figures:
- `manuscript/FIGURE_PLAN_V2.md`
- `manuscript/FIGURE_CAPTIONS_V2.md`
- `manuscript/FIGURE_DATA_CONTRACT_V2.json`
- `manuscript/FIGURE_QC_V2.json` — **PASS**
- `manuscript/figure_data_v2/`

Older V1 completion-centred figure specifications and simplified initiation scripts are explicitly superseded/fail-closed.

### Remaining non-scientific submission inputs

- author/affiliation/contribution fields;
- target-journal formatting;
- source-study ethics wording check;
- release/archive.

**PASS_SPEED_REPRODUCTION / HETEROGENEITY_AUDIT_COMPLETE:** pooled speed n=418 and ratio 0.983 reproduce exactly from the pinned upstream blobs; project-specific speed effects show no detectable heterogeneity (Q=2.47, df=5, p=0.781, I²=0%). Do not generalize this to every route-specific progression endpoint.

---

## 2. Louisiana — hydrological buffering inside resident home ranges

### Scientific status

**Analysis closed for drafting. Canonical figure data materialized. Reference Figure 1–5 SVG render QC PASS.**

Primary independent Lake Erie result:
- **190** valid matched events;
- **10** birds;
- **10/10** positive SRI;
- median SRI **0.886**;
- exact sign-test p **0.00098**.

Temporal retention:
- 10/10 positive;
- median **0.658**.

Availability coupling:
- observed slope **0.162**;
- pseudo-used null median **1.001**;
- coupling reduction **83.8%**;
- 10/10 birds below own null median.

Buffering limit:
- **9/10** retain positive buffering under top-quartile local mismatch;
- median extreme retention **0.629**.

Interpretation:
> repeated realised microhabitat use strongly dampens temporal hydrological variation experienced by resident King Rails relative to local time-matched availability.

Boundary:
- coordinate-to-event join remains unresolved;
- do not claim measured geographic displacement caused the buffering.

### Manuscript status

Canonical manuscript:
- `manuscript/LOUIS_HYDROLOGICAL_BUFFERING_MANUSCRIPT_V1.md`

Numeric contract:
- `manuscript/MANUSCRIPT_NUMERIC_CONTRACT_V2.json`

Submission QC:
- logical equivalent of `validation/validate_manuscript_v1.py`: **PASS**
- no control-character / LaTeX corruption;
- all canonical sample-flow and SRI/coupling values present;
- coordinate-linkage boundary explicit;
- no EOG wording;
- no forbidden causal claims;
- Brewer source citation, Zenodo DOI and References section present.

### Remaining non-scientific submission inputs

- author/affiliation/contribution fields;
- target-journal formatting;
- source ethics wording verification;
- submission release/archive.

**No further Lake Erie post-hoc metric is required unless authoritative coordinate-event linkage appears.**

### Published Godwit boundary

The Senegal Delta Black-tailed Godwit system is retained as an opposite-scale ecological boundary rather than an SRI replication: seasonal movement is associated with habitat-state replacement/resource tracking rather than strict state retention. Louisiana therefore asks the broader question **when local movement buffers experienced environmental variation and when animals must switch or relocate to a different resource state**.

---

## 3. Tampa — buffered persistence under quantitative degradation

### Scientific status

Retrospective ecology is closed.

Supported:
- recorded occurrence can remain stable while frequency, abundance, blade length, shoot density or composition deteriorate;
- external Zostera panel reproduces broad binary–quantitative state decoupling.

Mechanism remains prospective.

### Decisive prospective test

**Four-bay rhizome TNC sampling first; within-meadow state augmentation is the decisive primary inference.**

Planning frame:
- Old Tampa Bay: 8 recent positive nodes
- Middle Tampa Bay: 11
- Lower Tampa Bay: 14
- Boca Ciega Bay: 8
- planning total: **41**

Confirmatory gate:
- >=36 analyzable nodes total;
- >=6 analyzable nodes per bay;
- >=3 valid cores/node;
- one <=28-day campaign;
- paired baseline within +/-14 days;
- one frozen HPLC workflow.

Primary sampling/model infrastructure is already frozen. The paper-level decisive hierarchy is now refined before outcome-bearing sampling: the within-node anchor test (`results/clonal_state_augmentation_primary_v1_contract.json`) is primary because it controls stable node identity and baseline local state; the cross-node four-bay TNC -> future-frequency model is supportive/generalization evidence.

### Independent high-novelty functional-insurance branch

A second prospective mechanism question is frozen independently of the TNC line:

> **After documented local loss of Thalassia, does continued occupancy by another seagrass retain the same directly measured hydrodynamic attenuation as nearby persistent Thalassia within the same long-monitored meadow?**

Response-independent historical preflight identified **18 Old+Middle Tampa Bay matched pairs** linking:
- documented focal Thalassia loss;
- present alternative-seagrass occupancy at the same stable meter mark;
- a nearby >=3-year persistent-Thalassia comparator in the same stable node.

The future response is new paired canopy/near-bed velocity, not another transformation of the retrospective biological table.

This separates:
- **occupancy insurance** — some seagrass remains;
- **functional insurance** — the physical ecosystem-engineering function is retained.

A resolved attenuation difference would show that persistence of a vegetated label is not equivalent to persistence of foundation-species function. A null difference is not interpreted as functional equivalence because no equivalence margin is frozen.

Canonical files:
- `docs/FUNCTIONAL_INSURANCE_NOVELTY_BOUNDARY_V1.md`
- `results/functional_insurance_loss_legacy_preflight_v1.json`
- `results/functional_insurance_loss_legacy_primary_v1_contract.json`
- `field/functional_insurance_loss_legacy_analysis_freeze.json`

This branch is scientifically independent of TNC and cannot rescue an unsupported TNC result.

### Remote CI verification

The TNC-v2 method/baseline implementation has been executed on GitHub Actions.

Verified run:
- workflow: `TNC v2 response-independent method pilot`
- run id: **37253769624**
- conclusion: **success**
- commit: `07bb332a14715aac8eaeac92e7e6a6b7a6d64b54`

Confirmed steps:
- synthetic fail-closed method-pilot pipeline: **PASS**
- synthetic baseline-validator tests: **PASS**
- blank repository pilot records: correctly return **STOP_PILOT_INCOMPLETE**
- candidate builder/validator/artifact handoff: **PASS**

The logs explicitly contain:
- `TNC-v2 method-pilot pipeline self-test: OK`
- `TNC-v2 baseline validator self-test: OK`

Therefore the present Tampa stop is **not a software failure**.

The only valid blocker is missing response-independent physical/laboratory pilot measurements.

### Software/readiness status

Authoritative pilot path:

~~~text
raw response-independent pilot records
 -> validation/build_tnc_v2_method_pilot_summary.py
 -> field/tnc_v2_method_pilot_candidate.json
 -> validation/validate_tnc_v2_method_pilot.py
 -> PASS_METHOD_PILOT
 -> apply selected values to field/tnc_v2_precollection_freeze.json
 -> validation/validate_tnc_v2_baseline.py
~~~

The following templates already exist:
- `field/tnc_v2_raw_pilot_metadata.json`
  - must include pre-result HPLC analytical-QC minimum counts frozen by the receiving laboratory
- `field/tnc_v2_hplc_matrix_pilot.json`
- `field/tnc_v2_tissue_class_pilot.csv`
- `field/tnc_v2_core_geometry_pilot.csv`
- `field/tnc_v2_offset_pilot.csv`
- `field/tnc_v2_preservation_pilot.csv`

### Current hard stop

**STOP_RESOURCE_FREEZE_INCOMPLETE**

The unresolved values are physical field/laboratory facts, not analytical choices:

1. campaign start date;
2. campaign end date;
3. selected horizontal-rhizome tissue class;
4. minimum perpendicular transect offset;
5. selected core diameter;
6. selected core depth;
7. maximum collection-to-preservation time;
8. preservation method;
9. final four-bay node/date/resource manifests;
10. optional forcing modules must be explicitly confirmatory or disabled.

These values cannot be inferred from existing retrospective data and must not be fabricated.

### Single next external input

The next scientifically valid input is:

> **response-independent TNC method/field pilot measurements entered into the existing pilot files.**

Once those values exist, the repository already contains the builder, validator and fail-closed transition into the outcome-bearing four-bay campaign.

---

# Active order

1. **Azores:** manuscript scientifically QC-passed; submission formatting only.
2. **Louisiana:** manuscript scientifically QC-passed; submission formatting only.
3. **Tampa:** active science blocker is the physical TNC method/field pilot.

## Hard boundary

Do not restart exploratory analyses in Azores or Louisiana merely because Tampa is waiting on external field/laboratory input.

The target remains three independent ecological papers.

- [TNC-v2 method pilot execution card](docs/TNC_V2_PILOT_EXECUTION_CARD_V1.md)
