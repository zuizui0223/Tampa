# Charlotte Harbor: from mapped class turnover to ecological mechanism
*Pre-outcome field-confirmation design draft, 19 November 2026 — not a sampling authorization*

## What is truly supported now

The archived 2016/2022/2024 official SWFWMD polygons were source-validated and used for descriptive class-change and spatial boundary tests. Their main findings and *status*:

| Analysis | Observed | Evidence boundary |
|---|---|---|
| Long-run map history | 92.979% of 2022 attached-algae area overlaps mapped 2016 seagrass | Historical map-positive association, **not selective algae occupation** |
| Reference falsification | 2022 seagrass historical overlap **96.945%**, *higher* than 2022 algae | Disproves interpretation of **92.979% alone** as ecological selective replacement |
| Two-way 2022–2024 map change | 2022 algae → 2024 sea 83.433 ac; 2022 sea → 2024 algae 280.957 ac | Mapped classifications, not observed plants dying/colonizing |
| Same-class mapped retention | 2022 sea **90.266%**, attached algae **36.364%** mapped as same class in 2024 | Spatially dependent, detection/season/protocol differences unresolved; not different lifespans |
| Boundary sensitivity | Sea retention at 25m interior **50.491%** of initial sea map area vs algae **8.253%** | Raw original denominator remains fixed; erosion also preferentially affects small/fragmented polygons |
| External negative/estimability | Preselected Lemon Bay and Dona–Roberts have **zero 2022 mapped class-9121 algae polygons** | Their algae→sea mapped-transition endpoint is **non-estimable**, not external confirmation nor biological absence |
| Confirmation map | **145** mapped 10m/25m geometry features, including overlapping nested cores | Neither 145 independent biological sites nor access approvals |

Source releases:
- `results/charlotte_historical_overlap_reference_verified_20261119.json`
- `results/charlotte_map_class_retention_source_verified_20261119.json`
- `results/charlotte_historical_field_verification_geojson_release_20261119.json`
- mapped external source counterexamples: [PR #165](https://github.com/zuizui0223/Tampa/pull/165).

## Scientific question: observation turnover or ecological turnover?

### Model M0 — remote-sensing/observation mechanism

An aerial map class differs from the actual ecological state because of view conditions, phenology, water clarity, image classification, patch fragmentation, seasonal drift versus attached macroalgae, and the 0.25-acre mapping threshold.

**Prediction:** within-site, repeated field quadrat and standardized imagery surveys reveal nontrivial seagrass underneath or within remotely mapped algae areas, or algae classified inconsistently through seasons. The measured map-class persistence gap between seagrass and algae should shrink after accounting for observation error and comparable sampling intervals.

A result consistent with M0 is *not* ecological invalidity of algae: it means aerial maps are not sufficient to identify the transition mechanism.

### Model M1 — differential biological persistence

Established clonal *Thalassia testudinum* meadows can retain local shoot occupancy/structure while attached-algal cover varies more rapidly.

**Prediction:** repeated **independent in-situ** observations show longer *occupancy duration* for focal seagrass than for attached algae in true quadrat-level records after seasonal/environmental observation effort and site differences are modeled.

**Not sufficient:** a two-date map-class retention contrast (90.266% vs 36.364%), because mapped persistence is not a survival-rate estimate.

### Model M2 — algal-shading/low-light effect on subsequent seagrass condition

At a fixed site, sustained attached macroalgal cover can reduce actual benthic irradiance, potentially lowering later seagrass growth or shoot density. At present this is **a candidate mechanism**, not a Tampa/Charlotte-identified effect. Existing work on seagrass–sediment–light feedback means the novelty would be distinguishing reserve/process/detection layers against the same future response, not inventing an algal competition mechanism.

**Two distinct links needed:**
1. *Contemporaneous physical link:* attached algae/epiphyte burden negatively predicts measured within-canopy/benthic PAR relative to appropriate above-canopy PAR and water-column attenuation controls.
2. *Prospective biological link:* after baseline true live *Thalassia* frequency/cover, true sampling effort, depth and season are controlled, measured pre-outcome algal cover and light jointly predict subsequent **same-mark** seagrass quantitative change.

Even both observational links do **not prove** algal removal will reverse decline. That requires a properly permitted randomized manipulation or an independently valid quasi-experiment.

### Model M3 — hidden belowground reserve, *separate* from algae

Rhizome non-structural carbohydrate stock and growing meristems are possible seagrass persistence buffers; the separate Tampa four-bay TNC prospective program remains the authoritative primary test. Do **not** infer plant reserve depletion from mapped algae class, nor use post-hoc Charlotte maps as a rescue for an absent TNC sample.

## Practical confirmatory field-sampling design (authorization-dependent)

The previously verified 10m interior candidate cores in Charlotte consist of **21 mapped-return-to-seagrass polygons (24.464 ac), 43 mapped-algae-persistent polygons (108.071 ac), 37 unmapped-2024 polygons (211.651 ac)**. These are source-geometry candidates only, not independent sites. The stricter nested 25m cores (2 / 23 / 19) overlap 10m candidates.

1. **Source & permission gate.** Confirm original mapping footprint and latest site access; obtain field authority, habitats/water-depth/safety approval, and a real contemporary observed site roster before field work. Revisit source GPS mark/area; *unvisited* is never zero.
2. **Spatial independence gate.** Construct non-overlapping sampling blocks from polygon footprints **before viewing biological responses**; choose one or a limited number of candidate points per block, retain neighboring patches as clustered repeated measures. Pre-evaluate 250m and 500m block definitions for sample availability without using biological outcomes; if too few independent blocks, report non-estimable.
3. **Detection gate.** Repeat marked/quadrat measurements within comparable season and with documented effort; distinguish attached and drifting macroalgae, *Thalassia*, *Halodule*, empty sampled quadrat, and not visited. Acquire independent expert-interobserver repeat classification and photo standards. Measure percent cover, shoots per area, leaf blade selection protocol and composition.
4. **Physics gate.** At each true field-quadrat visit, measure calibrated above- and below-canopy photosynthetically active irradiance (same sensor angular response), depth, turbidity, epiphyte cover, and local flow/current exposure. Do not treat agency bay-mean benthic light as within-meadow exposure.
5. **Temporal gate.** Measure source-year true algae/light and focal seagrass state before the next same-mark quantitative outcome. A current field visit cannot reconstruct a purported measured biological 2024 condition. Freeze follow-up visit window and detection rules before viewing later outcomes.
6. **Outcome/model gate.** Use an explicitly declared hierarchical repeated-state model with spatial blocks, survey-date/observer/detection process and baseline quantitative seagrass state. Compare a state-only, state+mapped-class, state+field-algae, and state+light model under temporal holdout. Report the full family even if extra predictors worsen performance. A future map-class label is never allowed to predict a prior year.

## Falsification decisions

- **If map labels frequently disagree with repeated independent site observations:** retain the apparent mapped class stability gap as a remote-sensing/monitoring contrast; do not publish a biological persistence difference.
- **If true algal duration is not shorter than true seagrass duration:** M1 not supported despite the mapped 90% vs 36% contrast.
- **If attached algae does not reduce measured benthic light after within-site/above-canopy comparison:** M2 algal shading link not supported under this design.
- **If light link holds but algae/light adds no future same-mark seagrass-state information:** M2 is a physical association, not an established delayed ecological mechanism.
- **If prospective biological and detection-aware links both hold:** a mechanistic predictor is plausible; *not* a randomized effect of algae treatment.
- **If functional/biological sample gates fail:** stop the mechanism test, keep the public spatial maps as descriptive monitoring products.

## Conservation output

Managers can use the map as a **verification sampling aid**, stratified by different remotely mapped outcomes. Do not trigger algae removal, transplants, official site risk categories or restoration spending solely from these maps. The useful field deliverable is a validated *observation-quality and actual plant-condition* record at independently selected mapped patch cores.

There are no genuine new field surveys, laboratory TNC values, approved sites or intervention outcomes in the repository as of this draft.
