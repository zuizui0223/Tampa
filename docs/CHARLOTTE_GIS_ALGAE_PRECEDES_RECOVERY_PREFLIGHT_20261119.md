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
