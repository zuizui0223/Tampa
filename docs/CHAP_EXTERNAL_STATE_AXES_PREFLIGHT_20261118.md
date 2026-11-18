# Charlotte Harbor external state-axis replication: response-unopened preflight (2026-11-18)

## Why this candidate, and why not repeat earlier attempts?

Tampa's supported ecological result is **state-specific change under partially persistent recorded occurrence**, not an annual condition -> thinning -> disappearance cascade, nor a measured rhizome buffer. The site-identity-adjusted Tampa early-warning result is a bounded prediction of **next-year recorded non-detection**, not true death. See the source-validated but currently unmerged PR #155; do not silently treat it as main.

The repository already records terminal, non-confirmatory external early-warning attempts:
- `validation/marinegeo_early_warning_v1/terminal_result.json`: insufficient annual contexts;
- `validation/seagrassnet_zostera_v3/terminal_result.json`: the declared raw-archive transport stop;
- `validation/northeast_seagrassnet_v2/terminal_result.json`: documentation transport stop;
- existing NPS `Zostera` results: post-hoc external **ecological state-decoupling**, not untouched early-warning validation.

Those stop rules remain in force. This candidate addresses **external descriptive state axes**, not a relabeled early-warning rescue.

## Independent candidate (metadata only)

**Source:** [Florida SEACAR Program 570 — Charlotte Harbor Seagrass Monitoring](https://data.florida-seacar.org/programs/details/570), Florida DEP, Office of Resilience and Coastal Protection / Charlotte Harbor Aquatic Preserves.

The public program page describes a 1999-to-current **annual**, fixed-transect monitoring network with 1 m x 1 m sample quadrats, species-specific Braun-Blanquet, shoot counts, blade length, epiphytes, depth, and sediment. It lists a workbook titled `SEACAR_CHAP Seagrass Data_1999-2025_2025 submission.xlsx`, added in 2026. The program also warns that database tables are relational, includes Estero Bay/other program data, has excluded stations, and distinguishes repeat quadrats from variable meadow edges.

**Access caveat:** SEACAR's web portal requests a valid email / data-use registration. No biological workbook has been acquired or inspected here. Do not bypass that access route or substitute an invented identity. This PR is source reconnaissance and a locked initial analysis contract, not new measurements.

## Pre-response questions to settle

Before opening any biological response column, independently validate:

1. **Stable unit**: a real repeated **transect** identifier. Treat quadrat/mark identity as stable only if the documentation proves it. Variable meadow margins are not identical fixed quadrats.
2. **Zero semantics**: a complete survey with no focal records may be a sampled non-detection only if the whole species/effort roster proves it. Missing, not visited, and zero are distinct.
3. **Program scope**: distinguish core Program 570 from bundled 571/5721 or designated excluded stations; never combine as independent site-years by accident.
4. **Units and changes**: BB categories, blade length cm, shoot counts and sampled areas, dates/seasonality, sampling counts, and protocol changes must be documented before harmonizing.
5. **Traceability**: original source/portal, workbook version, hash, metadata and inclusion ledger must be frozen before response calculations.

Failure at a necessary gate is reported as **NON_ESTIMABLE**, not rescued by post-hoc switching of biological units.

## Predeclared ecological question and analysis

> In a different subtropical seagrass monitoring network, can *Thalassia testudinum* remain recorded along a stable transect while shoot density, blade stature or abundance change — and is the changing dimension spatially heterogeneous?

- **Primary window:** 2016–2025, with 1999–2025 contextual analyses only if comparability can be established.
- **Primary eligible unit:** one documented annual stable-transect summary; retain actual effort and survey day. Species identity and a complete sampled roster govern positive/negative states.
- **Primary outcome dimensions:** blade length and shoot density in recorded-positive focal years. BB abundance is secondary because its ordinal scale and all-mark aggregation must be source-validated.
- **Reporting:** stable-transect-adjusted temporal slopes with 95% transect-bootstrap uncertainty; subregion-specific contrasts and counterexamples retained, no pooling across incompatible sampling areas. Holm correction across the two primary plant dimensions.
- **Estimability gate:** at least 20 distinct stable transects with at least five sampled annual visits in the primary window and sufficient positive-year quantitative observations. Failing the gate ends the planned comparison.
- **Interpretive limit:** a negative condition slope while recorded-positive is quantitative state change, not proof of a physiological precursor, slow-state memory, clonal rescue, mortality, or restoration efficacy.

See machine-readable `validation/chap_external_state_axes_v1/pre_response_contract.json` for the exact initial contract. If source documentation exposes incompatible units or field definitions, record a terminal impossibility; do not refit the design after seeing biological responses.

## Why this is useful for Tampa conservation

The [Tampa Bay Estuary Program](https://tbep.org/seagrass-assessment/) already couples bay-scale areal mapping to annual transect monitoring. The official [2025 Tampa Bay compliance assessment](https://tbep-tech.github.io/tbnmc-compliance-assessment-2025/) reports baywide **+1,407 acres** from 2022 to 2024 while Old Tampa Bay lost **326 acres**. Baywide spatial aggregates can therefore mask a declining segment, while locally retained presence can coexist with changing plant state. Neither mismatch identifies cause.

An external Charlotte Harbor replication would ask whether the **multi-axis observation pattern**, not a single universally ordered deterioration trajectory, extends beyond Tampa. If feasible, it may strengthen a monitoring argument for publishing condition, occupancy, composition and observation effort as separate fields. It would **not** validate an Amber/Red collapse alarm or determine what intervention reverses decline.

## Immediate disposition

**METADATA SCREEN COMPLETE / BIOLOGICAL OUTCOME UNOPENED / NO EXTERNAL REPLICATION RESULT.**

The scientific paper and existing tests are unchanged. No human field permission, data-access registration, manuscript submission, or PR merge is implied.


## Verified methodology amendment (2026-11-18; no outcome access)

Independent reading of the [agency program page](https://data.florida-seacar.org/programs/details/570), [2019 field protocol](https://chnep.wateratlas.usf.edu/upload/documents/CHAP_Seagrass_Monitoring_Protocols_2019_Update.pdf) and [1999–2016 agency report](https://floridadep.gov/sites/default/files/CHAP-Seagrass-Report-1999-2016.pdf) disclosed additional comparison threats:

- **Stable marked quadrats vs moving edge quadrats:** field protocol II.E–G distinguishes site-specific repeatedly measured 1 m² quadrats from annual start/end-of-bed positions that move with bed margins. Limit repeated-identity tests to documented repeat quadrats; do not reconstruct absence from missing edge rows.
- **Species abundance coding:** field protocol uses r = solitary and + = few; the portal renders these as 0.1 and 0.5 while one historical PDF text entry says 0.05 for few. Treat original workbook BB values as unresolved until the source dictionary proves their encoding. Do not assume a silent numeric transform.
- **Leaf-selection limitation:** field protocol II.G measures five representative blades per species and only rounded, healthy green-tipped Thalassia blades. A change in this statistic need not reflect mean length across *all* shoots/tissues. Retain this conditioning when interpreting Tampa parallels.
- **Shoot-density construction:** counts are sampled in a subset of 10 × 10 cm squares, with counting pattern set by the BB class and resulting extrapolation. The historical report indicates density monitoring started in 2005. Validate raw-count vs derived-density units before fitting slopes or equating to Tampa shoots m⁻².
- **Survey protocol history:** the historical report notes that some repeat quadrats were added in 2007. The 2019 manual says three named transects are monitored quarterly (MP04, MP05, SC03). Prevent accidental double annual sampling; freeze a season/date selection before biological inspection.
- **Program mixture:** the SEACAR program-page notes acknowledge site-program mixtures (570, 571, 5721) and explicit excluded stations, including CR01–CR05 variants, PI10/PI11 and SC04/SC05.

These are **method-document findings, not a measured ecological change**.

### Executable source preflight

- \`validation/chap_external_state_axes_v1/check_metadata.py\` reads a JSON metadata **manifest**, not a workbook, and refuses undocumented stable IDs, zero semantics, program scope, BB coding, healthy-blade selection, and shoot-area extrapolation.
- \`validation/chap_external_state_axes_v1/metadata_manifest_TEMPLATE.json\` is intentionally incomplete; its correct result is \`STOP_METADATA_GATE\`.
- \`validation/chap_external_state_axes_v1/test_check_metadata.py\` tests positive *synthetic* documentation and failure cases without accessing biology.
- \`.github/workflows/chap-metadata-gate.yml\` runs the synthetic checks in CI.

Example after properly authorized source retrieval and source schema verification:

\`\`\`bash
python validation/chap_external_state_axes_v1/check_metadata.py \
  --manifest validation/chap_external_state_axes_v1/metadata_manifest_TEMPLATE.json \
  --out /tmp/chap_metadata_gate.json
# Expected on unfilled template: STOP_METADATA_GATE, exit code 2.
python -m unittest discover -s validation/chap_external_state_axes_v1 \
  -p 'test_check_metadata.py' -v
\`\`\`

Even a later metadata-gate PASS is just an attested provenance/schema screen, not proof of adequate biological sample size, reproducibility, ecological mechanism, or lawful data access by a third party. The present status remains **external biological data unopened; no new positive replicate**.
