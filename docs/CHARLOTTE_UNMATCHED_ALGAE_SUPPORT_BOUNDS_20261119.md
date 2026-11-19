# Charlotte Harbor — unmatched-algae common-support sensitivity
Source-pinned descriptive GIS analysis, 2026-11-19. This is NOT a causal effect or confidence interval.

## Starting evidence

The observed 2022→2024 official map has 90.266% broad-class retention of mapped seagrass source area and 36.364% mapped attached algae source area, a +53.902 percentage-point difference. In the audited joint patch-size × 5km strata, the conditional mapped sea-vs-algae gap is only +8.020 percentage points, and just 47.288% of mapped 2022 algae area is included. The other 52.712% is outside qualifying comparative class support.

Full frozen outcome and source-provenance evidence: results/charlotte_patch_size_spatial_support_verified_20261119.json; GitHub Actions #44455648817, https://github.com/zuizui0223/Tampa/actions/runs/44455648817 . The original GIS archive is the SHA256-pinned successful run #44446913647, artifact #14494425181. No biological response or new source geometry is opened in this follow-up.

## Mathematical sensitivity bounds

Define the hypothetical algae-area-weighted whole-source map-class difference as the sum, over all 2022 algae-source strata, of algae area times (same-stratum 2024 sea map retention minus actual 2024 algae map retention), divided by total original mapped algae area.

Within matched strata, both rates are observed. In unmatched strata, algae retention is observed, but there is no source-comparable sea reference. For each such stratum, let the unknown seagrass reference rate range from 0% to 100% with no favorable assumptions. **Do not** set the observed algae retention to zero.

Using A as all 2022 mapped algae area; B as source-area-weighted matched (sea minus algae) contribution; U as total unsupported algae area; R as *observed* retained algae area within unsupported strata:

- Minimal hypothetical difference = 100 × (B − R) / A.
- Maximal hypothetical difference = 100 × (B + U − R) / A.

These are deterministic possible values of a hypothetical extrapolation under missing class support, NOT a confidence interval or an identified biological treatment effect.

| Conditioning | Comparable algae source area | Conditional reported gap | Hypothetical whole-source feasible gap |
|---|---:|---:|---:|
| Original source-size bins | 53.651% | +27.186 pp | **+6.930 to +53.279 pp** |
| Source-size bins and 5km grid | 47.288% | +8.020 pp | **−7.111 to +45.601 pp** |

Therefore the sign of the *jointly matched hypothetical whole-area gap* is not fixed by currently supported source class comparisons. For size-only bins the algebraic lower bound is positive, but geography and classification/detectability differences remain uncontrolled.

The five-kilometre-only comparison has full algae area support and +42.380 pp, but it does not match patch size, which is a dominant source confounder.

## Spatial influence and effective support

The matched joint size×grid area includes 18 strata from 7 distinct 5km grid IDs. Within those 18 strata, 3 are locally reversed (attached algae maps as more persistent than seagrass) and represent 31.248% of matched algae source area. Due to unequal area weights, the effective weighted number of strata is about 7.53, not 18.

Deleting one matched *size×grid stratum* at a time gives conditional gaps in roughly +4.61 to +16.41 pp. However, strata in the same 5km grid share a spatial support unit. Deleting one **entire** 5km grid at a time yields a range of about **−0.224 to +17.225 pp**: one grid omission can reverse the conditional sign. Neither diagnostic is a p-value or biological replication.

The code and complete source-grounded values are in analysis/108_charlotte_unmatched_algae_support_bounds.py and its tests.

## Existing negative and non-estimable cases

- Earlier "algae specifically overlaps historic seagrass" interpretation is contradicted by the same-map reference: 2022 algae overlap 2016 seagrass-positive area at 92.979%, whereas contemporary 2022 seagrass overlaps it at 96.945%.
- Two preselected comparator areas, Lemon Bay and Dona–Roberts Bays, had zero 2022 mapped attached-algae features (PR #165). Geographic algae→seagrass class conversion is non-estimable there; zero mapped polygons are not verified biological absence.
- Internal 2022–2024 source class maps and the 2016 positive-history overlay remain outcome-context-exposed descriptions, not controlled measurement of biological survival, plant recruitment or algae shading.

## Scientific and conservation conclusion

The map categories differ substantially in observed same-class persistence, but the apparent stability gap depends on source patch area, spatial composition and unmatched reference support. The raw +53.9 pp should **not** be claimed as a taxon-intrinsic lifespan difference or long-term rhizome buffering. A site- and season-matched repeated field protocol is needed to distinguish image interpretation and detection errors from actual *Thalassia* and *Halodule* survival, attached/drift algae cover and subsequent growth.

The GIS candidate areas remain useful for *verification sampling*, not site risk rankings, algae-removal advice, restoration permission or causal forecasting. Do not merge a new biological mechanism claim from these map data alone.
