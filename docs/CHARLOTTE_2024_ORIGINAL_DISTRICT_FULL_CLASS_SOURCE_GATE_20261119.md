# 2024 Charlotte source-class expansion: from three vegetation codes to original district map categories

Source-audited discovery, 2026-11-19. No true field-mapped benthic state or biological mortality has been demonstrated.

## Why this changes the research

The earlier restricted, hosted Charlotte Harbor 2024 FeatureServer included only **9113 patchy seagrass, 9116 continuous seagrass, 9121 attached macroalgae**. A large target-year area inside two 2022 attached-algae giant source polygons was therefore called '2024 unmapped' **only relative to these three hosted vegetation categories**.

The official *district-wide original 2024* SWFWMD Seagrass MapServer is now accessible during the District's 06:00–22:00 local published GIS window:

https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental_Seagrass2018_sql/MapServer/3

A verified live source-count audit within the *same fixed Charlotte historic GIS envelope* found additional classified background polygons, not available in the hosted three-class map:

| Original 2024 FLUCCS code | Polygons intersecting fixed Charlotte bounding rectangle | Working reference descriptor (not a 2024 polygon ground truth) |
|---|---:|---|
| 0 | 587 | Land |
| 5400 | 101 | Open water / nonvegetated bay or estuary surface |
| 6510 | 630 | Tidal flats (definition revised in 2014) |
| 6540 | 259 | Oyster bars |
| 7210 | 1694 | Submerged sand / nonvegetated mapped benthos, SWFWMD 2016 added code |
| 9122 | 5 | Composite colonized algae |
| **Six non-hosted class codes** | **3276** | Do not sum area from polygon counts |

Also in the district 2024 layer's *bounding rectangle*: 9113=2349, 9116=1014, 9121=227. These are not directly comparable with the hosted Charlotte 2024 FeatureServer class feature counts 9113=2087, 9116=912, 9121=210: the district-wide original layer includes bbox-intersecting and potentially outside-Charlotte features. Do not claim area/fate without exact polygon geometry clipping.

**Official source proof:** original code counts sum exactly to the all-class source count, district source metadata SHA256 pinned, class count cross-queries passed, and the source-year/CRS/year-window gate passed at [GitHub Actions run #44516615481](https://github.com/zuizui0223/Tampa/actions/runs/44516615481). The original signed artifact and complete output are embedded in `results/charlotte_2024_original_district_full_class_counts_verified_20261119.json`. The complete source had nine class codes and 3,276 additional original polygon records inside the fixed bounding rectangle. No original source geometry was downloaded in this **metadata-only** audit.

Working class definitions are traceable to the District-modified FLUCCS codebook in [Tampa Bay Environmental Restoration Fund Report #03-17 (2017), Table 1](https://manatee.wateratlas.usf.edu/upload/documents/TBEP_03_17_Hard_Bottom.pdf), the [SWFWMD 2016 mapping results deck, Sand Other Than Beaches – Submerged (7210)](https://sarasota.wateratlas.usf.edu/upload/documents/SWFWMD-2016-Seagrass-Mapping-Results-Kaufman-Seagrass-Working-Group-2017.pdf), and [SWFWMD 2024 Springs Coast mapping class photointerpretation notes](https://www.swfwmd.state.fl.us/sites/default/files/calendar/Item%208%20-%20Springs%20Coast%20Seagrass.pdf). The last source is a separate district subregion; its code 9122 label should NOT be silently substituted for the 2024 Charlotte source's own `FLUCCSDESC` until queried. Classification labels are **mapped appearances**, not verified organism absence.

## Critical next source GIS geometry gate already coded

`analysis/126_charlotte_2024_original_classes_in_giant_unknown.py` and synthetic tests use source archive-locked exact original giant 2022 algae FIDs **37 and 2166**, their source 2024 three-class union, and original 2024 district MapServer/3. The predeclared program:

1. Revalidates original 2016/2022/2024 source geometry hashes and year-2024 district metadata/class count manifest.
2. Queries source `OBJECTID` inventories within the *two giant polygon bounding envelopes* instead of pulling a district-wide dataset.
3. Downloads exact original 2024 polygons by source OID and class, repairing invalid geometry conservatively and projecting to EPSG:6933 equal-area.
4. Splits the original 2022 giant algae polygons' **2024 hosted-three-class-unmapped** area into actual overlapping district source codes 0/5400/6510/6540/7210/9122, additional original three-code classifications, and area covered by no downloaded original 2024 code.
5. Reports full overlapping-class area separately, without a forced exclusive partition when the original source classes overlap, and stops if the code or metadata differs from the independently verified source.

GitHub Actions workflow: `.github/workflows/charlotte-2024-original-all-class-giant-overlay.yml`; **the workflow is queued as of this document**. Its outcome cannot be inferred from the mere existence of extra class codes. It is possible the original 2024 district background polygons cover most of the 222 acres, but also possible that the mapping footprint itself omits some areas. No full surveyed/photo-interpreted footprint or independent quadrat measurements have been acquired.

## What would and would not follow

If most 2024 hosted-unknown area overlaps official **7210**, that would support **reclassification as *mapped* submerged unvegetated sand**, not field-proved plant death, belowground propagule absence or algal shading. If most overlaps 5400, the source maps it as open water/nonvegetated at imagery scale; again no demographic inference. A 9122 region would preserve map-level algal substrate but require guild-specific crosswalk. If the original layer has no code covering these areas, the survey footprint/detection question remains unresolved. A mixed source would require class-specific spatial mapping, not one inferred mechanism.

Any completed field-ecological inference must still join to original 2022/2024 *Thalassia*, *Halodule* etc cover/shoot density, independent attached/drift-algal abundance, imagery acquisition and field dates, light/water clarity, and exact sampled quadrat locations. Public CHAP registered site midpoints alone are not such data.

## Additional historical constraints

Official 2018 and 2020 class-count and original source OID rosters have been independently verified in published-hours source queries (`results/charlotte_2018_2020_legacy_source_counts_verified_20261119.json` and `results/charlotte_2018_2020_original_oid_eligibility_verified_20261119.json`). However the old 2018/2020 MapServer has **no independent original acreage attribute** in those source layers, and the exact source polygon geometry/area crosswalk is not yet certified; counts cannot be used as areal history.

Source limitations are retained in the Draft PR, not the Tampa manuscript's causal or physiological mainline. A mapped seagrass/loss history does not identify ecological resilience or actual individual survival.

## COMPLETED original 2024 district all-class polygon overlay — supersedes earlier 'queued' note

The **full original district 2024 source GIS geometry overlay succeeded**, [GitHub Actions #44521549226](https://github.com/zuizui0223/Tampa/actions/runs/44521549226), from source script `analysis/126_charlotte_2024_original_classes_in_giant_unknown.py` after fixing a pinned source JSON key/STOP exception bug. The exact original-year source identities, hosted 2022/2024 area audits, 2024 full original layer metadata SHA, original source OID roster and GeoJSON feature checksum were validated. The result is now pinned with the successful Actions artifact ZIP SHA256 in `results/charlotte_2024_original_district_giant_unknown_codes_verified_20261119.json`. Source output queried **266 distinct original 2024 MapServer polygons** intersecting the two 2022 giant source patch bounding rectangles and required no invalid geometry repair.

| 2022 attached algae source patch | Previously 2024 three-class-unmapped | Original 2024 code 7210 | All other original 2024 non-three codes | Extra original 2024 9113/9116/9121 missing from hosted copy | Original layer also entirely missing |
|---|---:|---:|---:|---:|---:|
| FID 37 | 117.349861 ac | **116.943862 ac** | 0.002978 ac | 0.403021 ac | **0** |
| FID 2166 | 104.742594 ac | **104.368826 ac** | 0.160780 ac | 0.212987 ac | **0** |
| **Both FIDs** | **222.092455 ac** | **221.312688 ac (99.6489%)** | **0.163758 ac** | **0.616008 ac** | **0** |

Source-area sums may differ by <=0.000001 acre due to rounding. The original source 2024 GIS maps **all 222.092455 acres to one of its nine original FLUCCS codes**. The dominant **code 7210** maps to SWFWMD's *Sand Other Than Beaches – Submerged*, i.e. photo-interpreted submerged nonvegetated sand. This is a strong **mapped category transition** from 2022 attached macroalgae to 2024 original submerged sand, not evidence that any observed plant died or was absent in a field quadrat. It explicitly resolves the former ambiguity between 'outside mapped area' and 'mapped but to a category omitted by the hosted three-class service' **for these two source polygons**.

The 2024 original district MapServer/3 includes a numeric `Shape.STArea()` field but no independently audited source `ACRES` attribute; thus this *new* result inherits original source OID, geometry and code hash, and the already independently source-acred 2022/hosted 2024 map, **not an independent acre-attribute validation of the district background code polygons**. A second full source-geometry implementation/photogrammetric validation is not claimed. The original source `FLUCCSDESC` field is requested, and a follow-up script revision will explicitly emit the observed labels instead of relying on earlier reference-only codebooks.

**Ecological implications, bounded:** 2016 map was almost fully sea-positive here, 2022 source map showed extensive attached algae, 2024 district original map interpreted most of the missing area as submerged unvegetated sand. This three-map sequence is consistent with an unstable vegetated/algal benthic mosaic but does **not** establish biologic recolonization, time of loss, algal causation, alternative stable-state hysteresis, rhizome survival or a transplantation target. A survey of actual shoot density, underwater photos, attached/drift algal cover, benthic light and original seasonal photo dates remains required. The two giant polygons are nearby and do not provide independent landscape replication.

**Next sensitivity under CI:** `analysis/126_charlotte_2024_original_classes_in_giant_unknown.py` now also computes 25m and 50m distance-inside original code 7210 and the 2022 giant source boundaries, outside hosted 2024 vegetation codes; outputs a verified GIS verification candidate GeoJSON for sampled sea/sand accuracy. Do not describe the new 25m/50m sand-core values as confirmed before the amended workflow passes.
