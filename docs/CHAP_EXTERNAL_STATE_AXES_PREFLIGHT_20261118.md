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
