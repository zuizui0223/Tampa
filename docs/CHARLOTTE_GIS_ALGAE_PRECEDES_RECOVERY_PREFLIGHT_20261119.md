# Charlotte Harbor — preceding attached macroalgae and seagrass mapped transitions

**Evidence status:** public GIS layer discovery, metadata/count preflight. NOT a fitted algae-to-recovery effect.

## Biological target

The SWFWMD source defines 2022 benthic mapping classes:
- FLUCCSCODE \`9113\`: patchy seagrass;
- \`9116\`: continuous seagrass;
- \`9121\`: attached macroalgae.

These **compete as mapping labels for a given mapped polygon**, not necessarily as mutually exclusive ecological states at the same centimeter. The categories do not measure drifting algae or physiological plant stress. The [2025 East Wall algae survey](https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/2025_East_Wall_Algae/FeatureServer) is temporally **after** the 2024 seagrass map and cannot serve as a 2022 exposure predictor.

The official source records are:
- [2016 district-wide polygons (legacy CRS)](https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental/MapServer/20); separate field \`FLUCCS_CODE\`, Florida West feet CRS. Site bounding boxes and class definitions need source-specific validation before using 2016 as the historical seagrass pool.
- [2022 Charlotte Harbor polygons](https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2022_in_Charlotte_Harbor/FeatureServer/1) (2021–2022 aerial photographs; minimum mapped unit 0.25 acres).
- [2024 Charlotte Harbor polygons](https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services/Seagrass_in_2024_in_Charlotte_Harbor/FeatureServer/1) (2024 photos; 0.25-acre minimum mapping unit, aligned with 2022 map).

All map-year layers expose *mapped polygon categories*, **not repeated biological quadrat-level detection**. A spatial cell not intersecting a vegetation polygon cannot automatically be labeled true bare sediment, unless the full surveyed benthic footprint is independently defined. Source class-to-class overlap does not establish competition or causal conversion.

## Newly executable Gate 1

\`analysis/91_charlotte_arcgis_source_preflight.py\` reads **only metadata and class-level feature counts** (no geometry) from 2022 and 2024 official FeatureServer layers. It validates:

1. Polygon geometry; published integer \`FLUCCSCODE\` and descriptor schema.
2. Explicit feature counts for 9113/9116/9121, with all records accounted for or terminal stop.
3. Same source-specific WebMercator CRS and map extents documented.
4. Source SHA256s, category counts, original URL and last-edit date.
5. No 2025 predictor leakage; no registered original CHAP quadrat workbook access.

CI tests are synthetic only; a live result, if available, is **source eligibility**, not an ecological result. Importantly, *polygon counts are not areas*: do not conclude extent or macroalgal coverage from counts.

## Gate 2 — frozen proposed spatial descriptive endpoint

**Unit:** matched equal-area geometry at a fixed, source-supported Charlotte Harbor footprint between the 2022 and 2024 layers, not polygon ID (polygon IDs are not persistent).

**Descriptive transitions to estimate:** source 2022 patchy/continuous seagrass or attached macroalgae → target 2024 patchy/continuous seagrass, attached macroalgae, or unmapped. Use an area-weighted transition table (square metres and acres), preserving original mapped class and raw source-revision metadata.

**Required validations before interpreting a transition:**
- Both geometry payloads must be downloaded in full using ordered, paginated queries with exact ID inventories, size/digest, response-code checks and geometry validity.
- Transform both from verified source CRS to a documented **equal-area** CRS; never use uncorrected EPSG:3857 planar area to report acreage.
- Audit within-year polygon overlap and missing/unmapped areas; treat missing polygon class as \`unmapped\` rather than confidently bare bed or extinction.
- Clarify whether 2022 versus 2024 mapped domains are identical or only approximately matched (service text says aligned, not identical).
- Prevent 2024 categories from defining a **2022 predictor**.
- Check that computed sums are consistent with the specific source footprint; *never force agreement with baywide 14,913/14,020 acreage if the published layer's geographic coverage is narrower or different*.
- Retain 2022/2024 hurricane/disturbance timing and geospatial mapping error as possible alternatives.
- Do not treat adjacent pixels/polygon fragments as independent ecological replicates.

**Main scientific inference boundary:** percentage of **2022 attached-macroalgae mapped area** overlapping 2024 mapped seagrass could describe turnover in mapped cover. It cannot on its own establish that algae *caused* slower seagrass recolonization. Testing a **recovery constraint** against an appropriate reference requires a valid full surveyed footprint, pre-2022 historically vegetated bottom and a comparable 2022 nonseagrass control class, plus spatial-block uncertainty and environmental controls.

## Exposure boundary

Public CHNEP and district reports describing regional algae and seagrass trends have been read. This is an exploratory, **outcome-context-exposed** programme, not untouched confirmation or an established early warning. The official 1999–2025 registered SEACAR field workbook remains unopened.

## Status

Pending CI live source query. No source-grounded GIS transition statistic or causal coefficient has been computed as of contract authorship.

## Verified 2022-to-2024 mapped class overlay (19 November 2026)

The original spatial topology audit failed strictly because 4 source-year and 7 target-year GeoJSON polygons had invalid nested shells/ring self-intersections. A separately executed source-attribute crosswalk (GitHub Actions #44430679999) read the authoritative original `Geodesic` (2022) and `ACRES` (2024) attributes for the 11 affected official FIDs. For example, the corrected 2024 continuous-seagrass FID 2997 equal-area area is about **3,340.469545 acres**, closely matching the independent original `ACRES = 3340.46954622`, whereas the original invalid-polygon area would be **5,311.855069 acres**. This is material, not negligible geometry noise.

The repaired pipeline now checks **every source polygon**, not just the 11 invalid ones, against its original acreage field, using a maximum difference of `max(0.005 acres, 0.002 * official acres)`. The 2022 and 2024 classifications, all 5,512 original FIDs, geometry checks, and spatial area-weighted overlap passed in [GitHub Actions #44430960343](https://github.com/zuizui0223/Tampa/actions/runs/44430960343) (scientific-head `67549a55b8d88cbecc431752a6a05248bc43c999`). The matching original/source geometry QC had 0 material within-year overlap; maximum source-attribute discrepancy was 0.0138 acres in 2022 and 0.0 acres in 2024. Full raw class GIS extraction used source-year 2,303 and target-year 3,209 features.

### Actual GIS-mapped areal data (restricted public FeatureServer footprint)

| Class | 2022 acres | 2024 acres | Mapped net delta (acres) |
|---|---:|---:|---:|
| 9113 Patchy seagrass | 4,520.896 | 4,301.811 | -219.085 |
| 9116 Continuous seagrass | 8,576.666 | 7,979.277 | -597.389 |
| 9121 Attached macroalgae | 674.188 | 939.401 | +265.213 |
| Patchy + continuous | 13,097.562 | 12,281.088 | -816.474 |

**Scope requirement:** 2022 GIS patchy+continuous acreage (**13,097.562**) is not identical to separately published baywide **14,913 acres**; 2024 GIS patchy+continuous acreage (**12,281.088**) is not identical to separately published baywide **14,020 acres**. They likely represent different reporting/mapped footprints, revisions, or source definitions and MUST NOT be spliced or used as interchangeable acreage totals without a crosswalk.

### From original mapped 2022 class to mapped 2024 class

| 2022 class (source area) | 2024 patchy | 2024 continuous | 2024 attached algae | 2024 unmapped |
|---|---:|---:|---:|---:|
| Patchy seagrass (4,520.896 acres) | 3,040.975 | 592.315 | 208.071 | 679.535 |
| Continuous seagrass (8,576.666 acres) | 899.360 | 7,290.036 | 72.886 | 314.384 |
| Attached macroalgae (674.188 acres) | 56.419 | 27.014 | 245.158 | 345.596 |

Of **2022 attached macroalgae**, **83.433 acres (12.375%)** mapped as seagrass in 2024, **245.158 acres (36.364%)** still mapped as attached macroalgae, and **345.596 acres (51.261%)** fell outside any mapped target-class polygon. Conversely **280.957 acres of 2022 mapped seagrass** were classified as attached algae in 2024. The large `unmapped` category is an **observation/classification outcome, not verified bare bottom, true loss, or death**.

### Ecology: what changes, and what remains unknown

The observed map contains **two-way reclassification**, rather than a simple deterministic algae-replaces-seagrass sequence. This is a testable spatial churn observation, NOT measured species competition or true recolonization. The increasing 2024 macroalgae mapped area could reflect ecological change, mapping coverage/classification differences, shifting community structure, or a mixture. Independent detection-aware field confirmation and mapping-unit sensitivity tests are required.

The existing 2016 historical mapped-seagrass layer needs a source-area/coordinate/footprint crosswalk before the 2022→2024 mapping could be called **recovery of previously vegetated bottom**. No source data establish that any particular mapped 2022 algae patch prevented seagrass 2024 colonization, no valid 2022 non-seagrass counterfactual control was evaluated, and the public regional reports had already exposed broad outcomes. This result is descriptive GIS class conversion only, not a causal ecological mechanism or blind holdout.

Validation steps: `analysis/91_charlotte_arcgis_source_preflight.py`; `analysis/94_charlotte_source_area_attribute_audit.py`; `analysis/92_charlotte_public_gis_class_transitions.py`. Source reports: the completed CI logs and downloadable GIS/source-checksum artifact of Actions #44430960343.
