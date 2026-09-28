# Tampa ecology manuscript — Supplement outline v1

The Supplement should document methodological restraint and reproducibility without competing with the ecological main text. The main paper carries the state-decoupling result; the Supplement carries the audits, sensitivities and bounded mechanism ledger.

## Supplementary Methods S1 — Source reconstruction and identity checks

- pinned `tbep-tech/obis-example` commit and Git-blob verification;
- Event / Occurrence / eMoF joins;
- eligible visit definition;
- stable `node_id` semantics;
- annualization of repeated visits;
- Braun–Blanquet handling and nonnumeric `Reported` records;
- survey timing and sampled-point effort variables.

Primary source scripts:
- `analysis/01_transition_memory.py`
- `analysis/03_quantitative_state.py`
- `analysis/06_source_protocol_audit.py`

## Supplementary Methods S2 — Post-2016 within-transect trend models

- fixed-transect comparison design;
- cyclic survey-date control;
- sampled-point effort control;
- node-cluster bootstrap;
- estimability / missingness rules for blade length and shoot density.

Primary source:
- `analysis/04_state_change_validation.py`

### Supplementary Table S1

Per-bay, per-state slopes, bootstrap intervals, observations and node counts.

## Supplementary Methods S3 — Community reorganization analysis

- focal and co-occurring seagrass reconstruction;
- within-transect post-2016 slopes;
- consecutive-year species-change correlations;
- explicit boundary against causal competition claims.

Primary source:
- `analysis/05_community_compensation.py`

### Supplementary Figure S1

Full four-species frequency / Braun–Blanquet trajectories by bay segment.

## Supplementary Methods S4 — External NPS *Zostera marina* state-decoupling analysis

- source and eligibility semantics;
- frozen non-estimable early-warning endpoint provenance;
- post-hoc persistent-cover analysis;
- repeated-node slope construction;
- node bootstrap;
- reverse-ID sensitivity and no-repair rule.

Primary sources:
- `analysis/11_nps_persistent_cover.py`
- `analysis/12_nps_persistent_cover_sensitivity.py`

### Supplementary Table S2

Repeated NPS node slopes and location-level pooled slopes, including Moriches Bay as a positive-trend counterexample.

## Supplementary Methods S5 — Tampa next-year recorded-state instability

- source-positive transition construction;
- recorded loss definition;
- baseline and quantitative augmentation;
- target-year walk-forward design;
- training gates;
- log loss, Brier score and pooled AUC;
- target 2016 retained in primary result.

Primary source:
- `analysis/09_quantitative_early_warning.py`

### Supplementary Figure S2

Year-specific baseline and quantitative log loss, including 2016.

### Supplementary Table S3

Target-year test counts, losses, model scores and training-event counts.

## Supplementary Methods S6 — Temporal-state diagnostics

- original binary lag-1 / older-history comparison;
- matched Tampa quantitative frequency memory;
- Braun–Blanquet quantitative memory;
- transfer of the same exponential-memory operator;
- quantitative conditioning audit;
- stable-node reference saturation.

Primary sources:
- `analysis/14_tampa_matched_quantitative_memory.py`
- `analysis/15_tampa_cover_index_memory.py`
- `analysis/16_tampa_exponential_memory_replay.py`
- `analysis/18_tampa_quantitative_memory_conditioning_audit.py`
- `analysis/19_tampa_site_identity_memory_audit.py`

### Supplementary Figure S3

Lag-1 versus older-history score differences by target year, with and without stable node identity.

### Supplementary Table S4

All tested tau values and support-rule outcomes by state dimension/reference.

## Supplementary Methods S7 — Known-truth mechanism tests

Three prospectively bounded response-free simulation families:

1. simple thresholding of first-order quantitative state;
2. slow latent AR(1) suitability + faster condition;
3. persistent latent occupancy + imperfect detection.

Primary sources:
- `analysis/17_threshold_induced_memory.py`
- `analysis/19_two_timescale_hidden_state_memory.py`
- `analysis/20_latent_occupancy_detection_memory.py`

### Supplementary Figure S4

Observed target pattern versus support frequency across the three known-truth families.

### Supplementary Table S5

Frozen grids, replicate counts, support thresholds and global decision outcomes.

## Supplementary Methods S8 — Environmental screens

- response-independent annual water-quality aggregation;
- post-2016 segment-year coupling;
- 3/6-month pre-survey hot/fresh screen;
- multiplicity control;
- explicit no-window-retuning rule.

Primary sources:
- `analysis/02_water_quality_screen.py`
- `analysis/07_environmental_coupling.py`
- `analysis/08_seasonal_stress_screen.py`

### Supplementary Figure S5

Post-2016 ecological change versus declared environmental summaries, shown primarily as a null-screen overview rather than a selected best association.

## Supplementary Methods S9 — EOG-to-ecology spatial translation

- consumed EOG structural failure fact;
- stable-node descriptive state hierarchy;
- annually refreshed neighbor-state test;
- segment-state / local-residual decomposition;
- frozen four EOG spatial radii.

Primary sources:
- `analysis/21_eog_ecological_translation.py`
- `analysis/22_dynamic_neighborhood_state.py`

### Supplementary Figure S6

Predictive increment of dynamic spatial context across the four frozen radii.

## Supplementary Methods S10 — Measured persistent-site components

- response-independent depth/sediment preflight;
- held-out-node site-template prediction;
- coverage and sediment-label audit;
- boundary that `node_id` is not a biological mechanism.

Primary sources:
- `analysis/23_site_template_preflight.py`
- `analysis/24_site_template_outcome.py`

### Supplementary Table S6

Spatial-reference versus depth, sediment and combined-template held-out-node scores.

## Supplementary Methods S11 — Benthic-light proxy

- response-independent exposure preflight;
- visit depth;
- Secchi-to-Kd transform;
- six-month primary and three-month sensitivity;
- baseline controlling node identity, survey context, depth and bulk Secchi.

Primary sources:
- `analysis/25_benthic_light_preflight.py`
- `analysis/26_benthic_light_condition.py`

### Supplementary Table S7

Blade length, shoot density, frequency and Braun–Blanquet year-level support summaries.

## Supplementary Methods S12 — Published compound hot–fresh stress

- pinned Beck et al. published environmental artifact;
- 30 °C / 25 ppt thresholds;
- station-level daily GAM reconstruction provenance;
- joint duration tested beyond marginal hot/fresh durations;
- retrospective climate-stressor hard stop.

Primary sources:
- `analysis/27_compound_hotfresh_preflight.R`
- `analysis/28_compound_hotfresh_preflight_summary.py`
- `analysis/29_compound_hotfresh_condition.py`

### Supplementary Figure S7

Marginal and joint published stress duration by bay segment/year, with no species-response selection.

### Supplementary Table S8

Plant-condition predictive comparison for marginal versus joint stress.

## Supplementary Methods S13 — External early-warning validation ledger

Document terminal outcomes rather than hiding them:

- Caribbean SeagrassNet v1: schema/protocol STOP before fitting;
- NPS Tier-3 v2: non-estimable due zero recorded-loss transitions.

These attempts are provenance for why the current early-warning result remains exploratory.

### Supplementary Table S9

External endpoint, frozen eligibility, opened response, terminal status, model fits, scored predictions, and whether the endpoint counts as independent predictive evidence.

## Supplementary Methods S14 — Reproducibility and claim boundary

- `results/current_validation_v2.json`;
- `docs/ECOLOGICAL_MECHANISM_BOUNDARY_V1.md`;
- `manuscript/CLAIM_EVIDENCE_MAP_V1.md`;
- primary figure-data contract;
- NPS external figure-data sidecar;
- manuscript integrity workflow.

## Supplement writing rule

The Supplement should expose adverse and null analyses in the order they were consumed. It should not retrospectively reorganize them into a selected “best” mechanism. The purpose is to show why the main manuscript remains mechanistically bounded.
