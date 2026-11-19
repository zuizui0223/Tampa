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

## Boundary-interior sensitivity (validated live result)

To challenge an artifactual 2022→2024 class swap caused merely by map polygon outlines, the same successful public GIS overlay script eroded **both** mapped source and target class unions by 5 m, 10 m and 25 m in an equal-area projected CRS. The resulting intersection counts only spatial regions which are at least that far inside each year's mapped class. These are **absolute area sensitivities**, not probabilities conditioned on the post-erosion remnant or measurements of independent plant colonizations.

| Both-year minimum interior distance | 2022 algae → 2024 seagrass acres | 2022 seagrass → 2024 algae acres |
|---|---:|---:|
| 0 m (original overlap) | 83.433 | 280.958 |
| 5 m | 49.296 | 199.364 |
| 10 m | 27.616 | 141.080 |
| 25 m | 4.907 | 46.047 |

The sensitivity indicates that a substantial share of the apparent area change occurs near class boundaries, while some changes remain inside both original class polygons even with a 25 m interior criterion. At 10 m, approximately **33.10%** of the original algae→seagrass overlap and **50.21%** of the original seagrass→algae overlap remain. Not all interior class turnover is biological turnover: differences in imagery, classification, seasonal algal persistence, water clarity or map footprint can still account for changes. Thus the comparison remains **a mapped category spatial contrast**, not proof that macroalgae blocked seagrass recovery.

The successful full synthetic + source-area + GIS overlay + boundary-sensitivity workflow is [GitHub Actions #44431639618](https://github.com/zuizui0223/Tampa/actions/runs/44431639618), from code head `1b242d097334f5d2623be25a20905fd0389a9704`. Its original GeoJSON source inventory and exact feature SHA256s are in the archive (artifact #14487067188; ZIP SHA256 `d712335ef03178de292d643efa7eb580ecd6e9c65990cd8273d5e5b6b73eb4c7`).

The **full verified numerical report** has now been copied as an exact parsed output from the completed successful job into `results/charlotte_public_gis_transition_verified_20261119.json`, which retains the source reference, per-class 2022→2024 area matrix, both-year polygon-level original-area verification, all repaired geometry audits, and 5/10/25 m sensitivity results. No scientific coefficients were refitted and no positive causal conclusions were fabricated.

## Historical 2016 source compatibility gate (separate from verified 2022–2024 result)

The 2016 source `https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental/MapServer/20` is a legacy, broader SWFWMD mapping product, not a straightforward third time slice in the later FeatureServer. Its historical class dictionary, geographic footprint, coordinate system and source polygon-area semantics must be independently verified before adding a 2016-history requirement to the 2022→2024 analysis.

The new metadata-only script `analysis/96_charlotte_2016_historical_gis_metadata_gate.py` records the original layer identity, class-field presence, CRS declaration, field schema and whole-layer feature count; it explicitly refuses to open polygons or compute overlaps, and fails closed if the source is unavailable or the schema is not compatible with initial preflight. Synthetic regression tests: `validation/test_charlotte_2016_historical_gis_metadata_gate.py`. Workflow: `.github/workflows/charlotte-2016-legacy-gis-metadata.yml`.

**No historical reoccupation inference follows from this metadata gate.** Even if metadata succeeds, a complete source- and map-footprint-matched source-polygon overlay, confirmed 2016 seagrass class semantics, topology/acreage QC and a detection/classification sensitivity are required. The correct label for the existing 2022→2024 area result remains mapped category reclassification, not recovery of a site verified vegetated in 2016.

## Verified historical map continuity and field verification polygons (2026-11-19)

These results supersede the earlier **metadata-only/pending** status above, but do NOT change the scientific interpretation of classification as direct biological presence/absence. They use official source maps at three dates, not the registered original CHAP long-term point-transect workbook.

**2016 classification gate:** the district-wide legacy feature layer includes 21,026 polygons across several estuaries. The 2022/2024 Charlotte map envelope intersects 3,465 polygons: 2016 `9113` patchy sea-grass 954, `9116` continuous seagrass 428, `9121` attached algae 0, substrate classes `6510` 254 / `6540` 233 / `7210` 914, code `0` (land) 585 and code `5400` (mapped open water) 97. All classes sum exactly; source [CI #44446793167](https://github.com/zuizui0223/Tampa/actions/runs/44446793167). The absence of the `9121` mapping label in 2016 is NOT proof that real algae were absent then. Unmapped source area/land/water codes are NOT direct demographic evidence of seagrass absence.

**Triple mapped-year join:** download of all 1,382 original 2016 mapped-seagrass-positive polygons plus the exact 2,303 (2022) and 3,209 (2024) class polygons passed independent per-feature original-source acreage QC (including legacy 2016 `ACRES`, 2022 `Geodesic`, 2024 `ACRES`; all transformed to EPSG:6933). The 2022 attached-macroalgae map area was 674.188 acres, of which **626.854 acres (92.979%)** fell within 2016 mapped seagrass-positive class boundaries. In these 626.854 acres, the 2024 map shows 81.455 acres sea-grass, 210.417 acres attached algae and 334.983 acres outside the three 2024 mapped vegetation classes. Original [CI #44446322239](https://github.com/zuizui0223/Tampa/actions/runs/44446322239); source-verified release `results/charlotte_historical_positive_three_date_verified_20261119.json`.

**Boundary-interior diagnostic:** eroding *each of three mapped class boundaries* by 0/5/10/25 metres changes the 2016-positive/2022-algae mapped overlap to 626.854 / 509.615 / 412.266 / 229.382 acres and the subset classified 2024 seagrass to 81.455 / 48.238 / 27.418 / 4.907 acres. This demonstrates substantial boundary sensitivity of apparent reclassification. These are NOT fixed-denominator biological recovery rates. Source [CI #44446913647](https://github.com/zuizui0223/Tampa/actions/runs/44446913647), report `results/charlotte_historical_positive_interior_sensitivity_verified_20261119.json`.

**Field-verification polygon export:** a stricter map-core procedure uses 10m and 25m interiors, fixed minimum retained polygon area 0.25 acre, a valid EPSG:4326 GeoJSON `FeatureCollection`, generated nonofficial IDs and independent source SHA256 checks. The fully passed map build is [CI #44447818585](https://github.com/zuizui0223/Tampa/actions/runs/44447818585), ZIP [artifact #14494236985](https://github.com/zuizui0223/Tampa/actions/runs/44447818585/artifacts/14494236985), SHA256 `45c9e98e00459555f529e1112cc6f37cfeb2f4213c11e6826802c73159c3074f`. Its **145 mapped core polygons** include overlap/nesting between the 10m and 25m thresholds, NOT 145 independent approved field sites. At 10m, 21 mapped return-to-seagrass cores (24.464 acres), 43 persistent attached algae cores (108.071 acres), 37 target-unmapped cores (211.651 acres). At 25m, corresponding groups have 2 / 23 / 19 polygons, respectively. This is a geometry-derived *confirmation-survey candidate layer*, not legal field access, restoration site authorization or a ranked impact map.

**Essential ecological limitation and next falsification:** the 2016 mapped-seagrass footprint is extensive. A 92.979% overlap with 2022 algae is not evidence of selective ecological history unless its rate is compared to the 2016 seagrass overlap of contemporaneous 2022 mapped seagrass under the same map geometry. A new diagnostic in `analysis/100_charlotte_2016_2022_2024_positive_only_overlay.py` quantifies all three 2022 class overlaps with the 2016-positive mask; any future estimate is an area-context comparison without spatially independent null or causal claims. Interpretation must remain **historical mapped habitat ↔ later mapped class association, with strong three-year boundary sensitivity and unobserved nonmapped substrate**. Field confirmation must check species-specific *Thalassia*/*Halodule*, attached/drift algae, visibility, benthic light, sampling footprint, and permits.


## 2016 historical-footprint specificity falsification — source-replayed result (2026-11-19)

**Prior tempting claim:** 92.979% of 2022 attached-macroalgae map area overlapped 2016 mapped seagrass, possibly suggesting selective algae encroachment into former seagrass. That interpretation requires a *same-map-class reference*. The previously frozen 2016/2022 GeoJSON source archive from successful Actions run #44446913647 was downloaded through a SHA256-pinned exact artifact, with original 2016 and 2022 OID counts, raw feature hashes, independent per-feature source acreage and all class totals reverified. This avoids live dependence on the intermittently changing 2016 legacy MapServer, whose later runs halted on source-schema drift. It does not use a newly selected favorable population or a different history map.

**Completed [Actions #44452243281](https://github.com/zuizui0223/Tampa/actions/runs/44452243281)**, archived-source replay verified:

| 2022 mapped source class | Area (acres) | Intersected 2016 mapped seagrass (acres) | Percent overlapping historical map |
|---|---:|---:|---:|
| Patchy seagrass (9113) | 4,520.896 | 4,233.181 | 93.636% |
| Continuous seagrass (9116) | 8,576.666 | 8,464.315 | 98.690% |
| **2022 mapped seagrass combined** | **13,097.562** | **12,697.496** | **96.945%** |
| **2022 mapped attached algae (9121)** | **674.188** | **626.854** | **92.979%** |

The algae minus seagrass historical-positive area overlap is **−3.966 percentage points**. **Thus the 92.979% overlap is NOT distinctive to algae; 2022 seagrass has greater historical overlap. Do not claim selective historic seagrass → algae encroachment from the raw 92.979% alone.** This is a substantive negative control and should be foregrounded rather than hidden. It does **not** show that no vegetation replacement or no competitive suppression occurred; those are different questions not answered by this contrast.

This is a **post-hoc descriptive area contrast** across mapped polygons in the same 2016 historical layer, *not* an independent-site significance test, a biological time-series survival study, proof of perfect 2016 detection or a claim of a universal causal process. Original source count checks succeeded and final validated result and artifact SHA are in `results/charlotte_historical_overlap_reference_verified_20261119.json`.

### Consequence for ecology and conservation

Reframe from **'algae favors former seagrass habitat'** to **'both 2022 seagrass and attached algae occupy a landscape historically mapped mainly as seagrass; the relative mapped transitions and observation quality differ'**. Ecological management cannot infer algae removal efficacy from these maps. Prioritize the verified 10m and 25m interior field-confirmation polygons, and collect actual *Thalassia* / *Halodule*, algae (attached vs drift), water clarity, below-canopy light and sampling-process observations. Inference about true recruitment, physiological buffers and large-scale transferability remains open.


## Mapped-class temporal stability: distinct from biological persistence (2026-11-19)

The **archived-source class-retention sensitivity** has been verified at [GitHub Actions #44453758649](https://github.com/zuizui0223/Tampa/actions/runs/44453758649), with exact archive SHA, 2022/2024 source feature hashes, source-reported original polygon acreage checks, and synthetic boundary tests passing. The durable numerical output is `results/charlotte_map_class_retention_source_verified_20261119.json`.

| Retained 2022 source area mapped as the same class in 2024 | No erosion | 5m inside both class boundaries | 10m | 25m |
|---|---:|---:|---:|---:|
| **Seagrass** (patchy + continuous combined) | **90.266%** | 79.862% | 70.639% | 50.491% |
| **Attached macroalgae** | **36.364%** | 27.438% | 20.284% | 8.253% |

The percentage denominator is always the original **2022 source class area**, not the reduced eroded area. Original same-class retained area is **11,822.685 acres for seagrass** and **245.158 acres for attached macroalgae**, a 53.902-percentage-point *descriptive map-class stability contrast*. For 10m erosion, the additional **within-eroded-source-area** stability ratios are 86.176% for seagrass and 30.651% for algae; these differ from the fixed-denominator figures and should never be mixed.

**Key scientific distinction:** this result supports stronger *mapped category persistence* for seagrass in Charlotte Harbor, even when considering class boundaries, not seagrass shoot survival or ephemeral biological lifespan of algal individuals. Algae may be temporally ephemeral, but their imagery detectability, phenology, shape fragmentation and mapping thresholds may also differ. The 2022–2024 interval cannot identify competition, mechanism or change in resilience reserves. Do not infer a genuine alternative stable state or hysteresis from two dates.

### Integrated negative and non-estimable evidence

- **Negative specificity check:** [source archive replay #44452243281](https://github.com/zuizui0223/Tampa/actions/runs/44452243281) found 2016 mapped-seagrass overlap of **92.979% for 2022 algae versus 96.945% for contemporaneous 2022 mapped seagrass**. Algae does not show exceptional historical seagrass-map association in this simple map-reference contrast; `results/charlotte_historical_overlap_reference_verified_20261119.json`.
- **External preselected source check:** [PR #165](https://github.com/zuizui0223/Tampa/pull/165) measured **zero mapped 2022 attached-algae polygons in both Lemon Bay and Dona/Roberts Bays** (and 2024 counts of two and zero, respectively). The registered 2022 algae → 2024 seagrass class-turnover endpoint is **NON_ESTIMABLE**, not a transferability confirmation or contradiction of real biological algae abundance. No favorable replacement estuary was selected.

**Updated ecological interpretation:** the long-term Tampa transect study identifies partially independent quantitative meadow-state axes beneath coarse persistence. Public Charlotte GIS independently documents a category-specific, boundary-sensitive map mosaic with mapped seagrass more class-persistent than mapped attached algae. These observations do not yet establish a common biological buffering mechanism. They support a specific next field measurement task: repeated observations of true focal shoot occurrence, attached/drifting algal abundance, benthic light, mapped microquadrats and observation effort in source-bounded candidate polygons, with site and within-area matching prior to physiological/causal claims.
