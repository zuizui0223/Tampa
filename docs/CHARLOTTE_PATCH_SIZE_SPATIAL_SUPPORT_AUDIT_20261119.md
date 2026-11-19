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
