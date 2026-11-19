# Charlotte Harbor: patch-size and spatial common-support audit
Source-verified GIS result, 19 November 2026. This measures **mapped classification persistence**, not biological plant survival or competition.

## Why this test was necessary

Aerial mapped seagrass occupied the same broad class in 90.266% of its 2022 area in 2024, while mapped attached macroalgae did so in only 36.364%. The original 53.902-percentage-point contrast is not a measured difference in plant lifespan. Mapped patches can be highly unequal in area and shape, and classes differ in photography interpretation and detectability. SWFWMD states that early-2024 aerial imagery precedes the 2024 hurricane season and is classified by trained interpreters with field information: https://www.swfwmd.state.fl.us/the-newsroom/seagrass-mapping-your-questions-answered

The patch audit used **the exact existing archived successful 2022/2024 original GIS**, SHA256-pinned to GitHub Actions #44446913647, artifact #14494425181. It verified original 2022 Geodesic and 2024 ACRES attributes, source geometry and source-class totals before computing per-2022-polygon overlaps. Source code: analysis/107_charlotte_patch_size_spatial_support_audit.py. Verified live computation, testing and artifact: https://github.com/zuizui0223/Tampa/actions/runs/44455648817. Full numerical evidence: results/charlotte_patch_size_spatial_support_verified_20261119.json.

## Fixed estimands

- Source features: 2,208 sea-class polygons totaling 13,097.562 acres; 95 attached-algae polygons totaling 674.188 acres.
- Source-area bins in acres: under 0.5; 0.5–2; 2–10; 10–50; at least 50. To include a bin requires three or more source patches and at least one acre of each class.
- Spatial coarse-support sensitivity: 5,000m cells based on each source polygon's internal representative point; two or more patches and at least 0.5 acre of each class required.
- Matched class rates use **2022 mapped algae area weights** over eligible bins/cells, not equal-weighted polygons. A whole-algae-area generality claim requires at least 80% of mapped algae source area within matched support.
- No independent-replicate p-values are made. Size and spatial checks are **post-hoc descriptive sensitivities**, not a causal estimate.

## Verified results

| Condition | Seagrass same broad class in 2024 | Attached algae same class | Difference (percentage points) | Algae area with matched support |
|---|---:|---:|---:|---:|
| Original full 2022 mapped area | 90.266% | 36.364% | +53.902 | 100% |
| Matched source patch-size bins | 80.694% | 53.508% | +27.186 | **53.651%** |
| 5km spatial cells | 78.744% | 36.364% | +42.380 | 100% |
| **Size bin and 5km cell** | **61.861%** | **53.841%** | **+8.020** | **47.288%** |

The last row is conditional on less than half of the original algae area. **Do not interpret 8.020 percentage points as the true whole-bay size-and-space-adjusted difference.**

### Why comparable source support is limited

The 2022 attached-algae class has only **two very large (≥50-acre) original polygons**, yet these contain **312.477 acres, 46.35%** of the total source mapped-algae area and retain the same map class in 2024 at only **16.518%**. This bin fails the required minimum three algae polygons and is excluded from source-size matching. Seagrass has 28 such large polygons (9,009.842 acres, about 68.79% of its source area), with 94.274% same broad-class retention. The two large-patch tails do not offer sufficient independent comparison in the published GIS.

Within other map-size bins, algae vs seagrass retention differs too, but differences are descriptive and not corrected for observation:
- Under 0.5 acre: sea 89.675%, algae 28.574% (1,197 versus 20 polygons).
- 0.5–2 acres: sea 86.944%, algae 36.322% (608 versus 36 polygons).
- 2–10 acres: sea 80.485%, algae 48.031% (280 versus 25 polygons).
- 10–50 acres: sea 79.318%, algae 60.650% (95 versus 12 polygons).

An additional **classification granularity** check found that sea-class retention is **78.877%** when requiring the identical 9113/9116 FLUCCS code in both years, versus **90.266%** when patchy and continuous are grouped together. The algae class is a single 9121 code. The outcome definition itself therefore changes the apparent contrast.

## Relation to other negative/limited results

- Charlotte historical source specificity: 2022 mapped algae overlaps mapped-2016 seagrass in 92.979% of its area; contemporaneous 2022 mapped seagrass overlaps the same historical map in **96.945%**. This defeats a simple algae-specific legacy preference inference; see results/charlotte_historical_overlap_reference_verified_20261119.json.
- Lemon Bay and Dona–Roberts Bays, two preselected comparator map regions, had zero mapped attached-algae features in 2022. Their mapped algae-to-seagrass transition is non-estimable, not a positive regional replication (PR #165).
- The Charlotte map, historical 3-year overlay, independent per-feature source area checks and 10m/25m field-confirmation polygon geometry remain descriptive **map products**. They cannot establish biological mortality, physical algal inhibition or restoration efficacy.

## Scientific conclusion and next ecological gate

**Supported:** 2022–2024 seagrass and attached algae have different mapped temporal persistence in the Charlotte official map, and this difference is strongly conditional on mapped patch size, geography and classification aggregation. **Not supported:** using 90% versus 36% to conclude that seagrass organisms intrinsically survive much longer than macroalgae.

The mechanistic test needs genuine repeated site/quadrat observations: actual species-specific seagrass shoot occurrence/condition, attached versus drift-algal abundance, imagery/interobserver classification uncertainty, sampling effort, season and below-canopy light. Pre-specify how to separate observation error from biological transitions, and use prospective same-mark seagrass responses. No such new biological field or carbohydrate data were acquired in this audit.

This is an outcome-context-exposed source analysis with spatial dependence and no causal effect size. The raw original class map is a categorical observation, not a 0/1 record of organisms or a verified treatment effect.


### Direction can reverse within jointly matched geographic patches

The verified source report contains 18 **size-bin × 5km representative-point grid** cells that meet both class-support gates. Their descriptive cell-level difference is not uniformly positive: 15 cells have higher seagrass same-class persistence, while **3 cells have higher algae same-class persistence**. Those 3 cells account for **31.248%** of the mapped algae area within the eligible jointly matched cells. Hence even within the partial common-support region, there are meaningful local reversals. This is not a spatial sign test, and the 18 cells are neither independent estuaries nor independent ecological experiments.

Most importantly, there is no statistical basis from this analysis to elevate the +8.020 percentage-point conditional weighted mean to a spatially universal advantage. The entire source-weight/area design and detailed cell counts remain inspectable in the verified JSON; avoid turning exploratory cell counts into p-values.

## Exact individual source polygons driving the 2022 algae contrast

A direct 95-feature 2022 algae source-polygon audit, based on the previously SHA256-pinned original 2016/2022/2024 GeoJSON and independent reported area fields, now identifies the **two source FIDs** comprising the entire 2022 algae ≥50-acre size tail. The complete FID-by-FID map area partition is frozen in `results/charlotte_giant_algae_patches_source_verified_20261119.json` and was **reproduced byte-for-byte identically at the numerical-result level in two completed successful CI runs**:

- [Original source-area and per-FID run #44464484860](https://github.com/zuizui0223/Tampa/actions/runs/44464484860)
- [Cache-optimized independent successful rerun #44464768571](https://github.com/zuizui0223/Tampa/actions/runs/44464768571)

| Original source 2022 attached-algae FID | 2022 area | 2016 mapped sea history | 2024 algae | 2024 sea | 2024 unmapped |
|---|---:|---:|---:|---:|---:|
| FID 37 | 186.620 acres | 186.616 acres | 46.588 acres | 22.683 acres | 117.350 acres |
| FID 2166 | 125.857 acres | 125.335 acres | 5.028 acres | 16.086 acres | 104.743 acres |
| **Both source giant polygons** | **312.477 acres** | **311.951 acres** | **51.616 acres** | **38.769 acres** | **222.092 acres** |
| **Remaining 93 original algae polygons** | **361.710 acres** | **314.904 acres** | **193.543 acres** | **44.664 acres** | **123.503 acres** |

The two giant source polygons account for **46.349%** of the 2022 algae mapped area. They are **71.075% unmapped in the 2024 target three vegetation classes**, versus **34.144% unmapped** for the remaining 93 original algae polygons. But their *algae→seagrass mapped-class reclassification fraction* is **12.407%**, almost identical to the remaining 93 polygons (**12.348%**). Their mapped algae self-retention is only **16.518%** versus **53.508%** for smaller polygons.

Removing the two giants from the algae source changes algae mapped-class retention from **36.364% to 53.508%** (+17.144 percentage points). Comparing this to all 2022 sea source-area retention would yield a raw, **unmatched** 90.266−53.508 = 36.758 point gap; it is NOT a size/space-matched effect and must not replace the previous gated standardization.

Crucially, the 2016 history is nearly complete **within the two giant polygons (311.951/312.477 ≈99.832%)**, but only **87.060%** in the 93 other source algae polygons. This confirms that the historical 2016 sea-map-positive signal and the low 2024 algae map-class retention are both heavily influenced by these large mapped polygons; this is an observation-geometry statement, not evidence for physiological biological legacy.

The original 2022 FID 37 and 2166 source-polygon representative points are only about **2.84 km apart geodesically** (coordinates converted from the verified EPSG:6933 representative points, not official field survey positions). This further cautions against treating these two source polygons as independent environmental replicates. The mapping points do not grant access or identify actual live algae in 2026.

**Updated ecological interpretation:** within the public Charlotte map, a large part of the apparent short-term algae instability is the conversion of two extensive formerly seagrass-mapped algae polygons into **target-year unmapped** areas, *not* an excess of algae→seagrass mapped returns. The actual substrate/vegetation state in unmapped regions, image timing, water clarity and map-footprint interpretation must be measured before concluding a biological disappearance or a restoration opportunity.
