# External geographic check: two other SWFWMD Suncoast estuaries (2026-11-19)

## Why an external check is needed

The linked [Charlotte Harbor source-overlap analysis](https://github.com/zuizui0223/Tampa/pull/164) found mapped two-way 2022–2024 seagrass ↔ attached-macroalgae class changes and later reconstructed a 2016 historical seagrass-positive mask. Its latest archived-source specificity falsification is **negative for exceptional algae occupation of historical seagrass habitat**:

- 2022 mapped attached algae: **92.979%** overlaps the 2016 seagrass-positive map;
- 2022 mapped seagrass: **96.945%** overlaps that exact historical positive map;
- algae minus seagrass: **−3.966 percentage points**.

These numbers are from a complete successful [source-pinned reference replay](https://github.com/zuizui0223/Tampa/actions/runs/44452243281), not from a fresh model refit. Historical mapped seagrass occurrence was widespread and cannot, by itself, identify a special algae-colonization preference.

A useful next step is **transport across geographically separate map regions** (rather than additional optimizations inside Charlotte), while keeping in mind that the same district photo-interpretation protocols and mapping errors are partly shared.

## Preselected sites and original public sources

Two other regional water bodies were chosen **before opening their year-specific class counts or polygon geometry**. Neither is a random draw from all estuaries.

| Area | 2022 service | 2024 service |
|---|---|---|
| Lemon Bay | [2022 mapped vegetation](https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2022_in_Lemon_Bay/FeatureServer) | [2024 mapped vegetation](https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2024_in_Lemon_Bay/FeatureServer) |
| Dona and Roberts Bays | [2022 mapped vegetation](https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2022_in_Dona_and_Roberts_Bay/FeatureServer) | [2024 mapped vegetation](https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2024_in_Dona_and_Roberts_Bays/FeatureServer) |

The service naming changes singular `Bay` to plural `Bays` for Dona/Roberts in 2024; the source gate does not assume it is the same footprint simply because of the names. The published description identifies 2024 mapped polygons as aligned to the 2022 Suncoast seagrass imagery product, but actual spatial and categorization equivalence remains to be tested.

## Fixed Gate 0: without opening GIS geometry

The script `analysis/104_two_estuary_algae_map_source_gate.py` validates, for both sites and both years:

1. Exactly one official source FeatureServer polygon layer and a documented OID field;
2. Same categorical FLUCCS schema: `9113` patchy seagrass, `9116` continuous seagrass, `9121` **attached macroalgae** (not drift algae);
3. Year-specific independent source-area attributes (`Geodesic` in 2022; `ACRES` in 2024) and declared map CRS;
4. Complete class-count closure, feature count and metadata hash;
5. The geographic bounding rectangles overlap; **not** sufficient to assert identical mapped footprint;
6. Zero mapped algae is retained as a negative/partially non-estimable outcome, **never** reason to switch estuary or search a favorable substitute.

Any missing field, class-count mismatch, invalid polygon-type or source request failure stops all source conclusions. This is a **source eligibility check**, not a positive biological result.

## Next fixed endpoint if both source checks are eligible

Perform same-source equal-area (EPSG:6933) polygon overlay, retaining mapped 2022 seagrass classes and attached algae separately. For each estuary, report:

- `2022 attached algae -> 2024 seagrass` area and fraction of the 2022 mapped algae footprint;
- `2022 seagrass -> 2024 attached algae` area and fraction of the 2022 mapped seagrass footprint;
- mapped same-class persistence and 'unmapped in 2024' as **unresolved classification**, not observed bare seabed or mortality;
- a 10 m both-year polygon-boundary erosion sensitivity fixed before geometry outcomes;
- original source OID, original-acre field, complete feature hashes and extent/topology provenance.

If either year's attached algae class is truly unmapped, label the algae-conversion endpoint **NON_ESTIMABLE_ZERO_MAPPED_CLASS**, report that failure and do not replace the region or invent mapped absence.

**Inference:** a repeated nonzero mapped two-way conversion indicates nonstatic categorical mosaics across more than one map region, not algae inhibiting reestablishment, demographic recolonization or plant-competition mechanism. The two regions belong to the same agency's Suncoast survey program and are not two independent ecological studies in the strict meta-analytic sense.

## Relationship to causal Tampa interpretation

Do not change Tampa's published recorded-presence and condition decoupling conclusion, PR #155 internal recorded-loss forecast, PR #162 registered CHAP biological workbook access boundary, or Charlotte's 2016 source-mapped negative specificity test.

The science remains:

> How often does mapped seagrass–algal class turnover occur across settings, and can it be separated from changing sampling footprints, class boundaries and local plant condition?

All endpoint outcomes are outcome-context-exposed and exploratory. No intervention was made and no physiological reserve buffering, seedling survival or macroalgae competition was measured.

**Status when authored:** public service metadata/count preflight coded; no source class count or polygon geometry for these two new sites has yet been inspected in this branch.
