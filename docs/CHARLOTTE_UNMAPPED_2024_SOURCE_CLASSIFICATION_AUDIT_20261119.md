# What does 2024 'unmapped' mean at Charlotte's two giant algae polygons?

Evidence-audit note, 19 November 2026. This is about **public mapped-category omission**, not proved biological disappearance.

## Why the 222.092 acres cannot be called bare bottom

The source-verified GIS transition analysis used exactly three public Charlotte Harbor FeatureServer codes: 9113 patchy seagrass; 9116 continuous seagrass; 9121 attached macroalgae. In the frozen 2022–2024 area overlay, the two original 2022 class-9121 features **FID 37 and FID 2166** together cover 312.477 acres. In the 2024 three-class target map, 51.616 acres remains class 9121, 38.769 acres becomes one of the two mapped seagrass classes, and **222.092 acres does not intersect any of those three published class polygons**.

The official full 2022 SWFWMD orthophotograph mapping was broader than this extracted three-class map: FWC's *Refining Suncoast Seagrass Maps to Identify Oyster Reefs* (Craig et al., 2024, Methods, report date 2024-09-09) describes class types continuous/patchy seagrass, attached macroalgae, oyster bars, tidal flats, submerged other than seagrass, composite colonized algae, and bays/estuaries. It cites the 2022 NV5 Geospatial photointerpretation key and 2022 original map. Full PDF source:
https://ocean.floridamarine.org/OIMMP/Resources_2024/TIGMappingReport-SWFWMD2020Review-09092024.pdf

Thus the three-class 2024 target's nonintersection may mean another substrate or habitat was originally mapped, or the area was outside the relevant imagery/mapping footprint, or source revision/classification/detection differs; we currently cannot choose among these alternatives. **The original 2022 complete classification dictionary documented by the 2024 FWC report does not, by itself, prove every one of those categories is present in the separate 2024 FeatureServer.** Original full-class 2024 data and the actual surveyed benthic footprint must be obtained to make a specific statement.

### Independent observation versus derived map

The 2022 mapping programme reportedly achieved **93% overall map accuracy** from its own randomized field-validation design (as relayed by FWC); this figure is not a validated attached-algae sensitivity/specificity, does not validate our map-class transition per FID, and does not say 2024 `unmapped` means 7% classification error.

The same 2024 FWC paper further re-evaluated 2022 code 6540 oyster maps with a *targeted nonrandom* 2024 substrate field sample. Its approximately 74.9% assessment accuracy applies to the selected oyster-refinement sample, **not** to sea/algae mapping accuracy, and should not be plugged into our statistical bounds.

## External map-class concordance source

Two separate source-controlled public CHNEP/SWFWMD map products have now been inspected, and their metadata + count audit successfully passed GitHub Actions #44475344451:

- `Seagrass_Gain_in_Charlotte_Harbor_between_2022_and_2024/FeatureServer/1` (832 mapped polygons; original `ACRES` field),
- `Seagrass_Loss_in_Charlotte_Harbor_between_2022_and_2024/FeatureServer/1` (767 mapped polygons; original `Geodesic` field).

Official service directory: https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services

These are still **mapped seagrass gain/loss**, generally derived from the same original 2022 and 2024 remote-sensing source family. We must not count them as independent field confirmation. A source-verified exact OID/area overlap audit now tests whether the 38.769-acre `2022 algae -> 2024 seagrass` mapped transition inside the two giant 2022 FIDs is included in the agency's gain layer. This can detect inconsistencies between derivative maps, but it does not identify the unknown actual substrate in the 222.092-acre unmapped part.

## Data needed to answer biological conservation questions

To distinguish map omission from real algae disappearance or *Thalassia* recolonization, the next field/source request should explicitly seek:

1. Both years' **unfiltered original full-class polygon datasets** (not only 9113/9116/9121), exact original release versions and FLUCCS lookup key.
2. Full valid **photointerpreted / imagery surveyed footprint**, water masks, imagery acquisition dates, photointerpreter corrections and source imagery classification key at the two FID geometries.
3. Actual contemporaneous in-situ focal seagrass cover/shoot counts, **attached versus drift** algal cover, benthic irradiance and observation effort, tied to real sampling positions and dates.
4. An explicitly held-out (not originally used as classification training/verification) set of the original map's field-accuracy points if available; otherwise clearly note no untouched field holdout.

Source-derived observation: 222.092 acres is absent from the **three selected map categories**, not observed to be bare; no treatment/restoration intervention or actual demographic transition is measured. Result belongs in methods limitations and a field-confirmation protocol, not in a causal abstract.

## 2026-11-19 official gain/loss map source type discovery

The CHNEP hosted mapping-derived source services for Charlotte Harbor published **832 'Seagrass Gain' polygons** and **767 'Seagrass Loss' polygons** for 2022 to 2024. Both source metadata and feature counts were verified at [CI #44475344451](https://github.com/zuizui0223/Tampa/actions/runs/44475344451), and are preserved with original layer fields and metadata SHA in `results/charlotte_official_gain_loss_source_verified_20261119.json`. The two layers' original-acre field names differ (`ACRES` for gain, `Geodesic` for loss), which is guarded during area comparison.

**A consequential schema correction:** the official service *named* `Seagrass_Gain_in_Charlotte_Harbor_between_2022_and_2024` includes at least one feature labeled **FLUCCSCODE 9121 (attached macroalgae)**. The original overlay CI [#44476173489](https://github.com/zuizui0223/Tampa/actions/runs/44476173489) deliberately stopped at `CHANGE_MAP_HAS_NON_SEAGRASS_CODE:mapped_seagrass_gain:9121`, because the code had refused to interpret any non-9113/9116 category as 'seagrass gained'. This was a correct source gate, *not* failure of an ecological hypothesis.

After documenting the source code, updated preflight logic counts 9113/9116/9121 separately **in both 'gain' and 'loss' layers** and explicitly flags any 9121 records as not-seagrass. The corrected map-concordance logic keeps separate polygon unions and reported areas by class rather than relaxing a binary seagrass-gain definition. This is a transparent, post-hoc source-format correction. Until those live source-class tests succeed, do NOT quote the nominal 832 as '832 seagrass gain features', or the nominal 767 as biological plant deaths.

Even after classification reconciliation, the mapping gain/loss source series uses the same underlying official 2022/2024 aerial imagery. Source concordance can audit whether the independently calculated mapped 38.769-acre algae→sea region inside the giant 2022 algae FIDs is reproduced by the official change map. It **cannot** independently establish true recruitment or determine the actual vegetation/substrate in the 222.092 acres absent from the three-class 2024 vegetation layer. The original complete photo interpretation categories and surveyed footprint remain necessary.

### Live audited source-code totals: not all nominal 'gain' or 'loss' features are seagrass

The completed [source-code CI #44476649845](https://github.com/zuizui0223/Tampa/actions/runs/44476649845) independently queried all three FLUCCS code counts in the official hosted change layers; no geometry and no field outcome were accessed. The revised source release with checksum and exact field dictionary is `results/charlotte_official_gain_loss_source_verified_20261119.json`.

| Nominal mapped change layer | 9113 patchy sea | 9116 continuous sea | 9121 attached algae | All original polygons |
|---|---:|---:|---:|---:|
| 'Seagrass Gain' | 513 | 187 | **132** | 832 |
| 'Seagrass Loss' | 496 | 218 | **53** | 767 |

Therefore **132/832 = 15.865%** of features in the nominal gain layer are coded attached algae and **53/767 = 6.910%** of the nominal loss features are coded attached algae. No unknown FLUCCS codes remain in either count ledger. These counts refer to original change-map polygons and do **not** measure acres or independent organisms gained/lost.

The original 2022/2024 3-class source FeatureServer contained **95 and 210** attached algae polygons, a +115 feature count change. That is **not equal** to 132 nominal gain minus 53 nominal loss (79), illustrating that patch fragmentation, source revision and/or difference-map geometry cannot be inferred from count arithmetic. Do not assert a class-change mass balance without equal-area geometry and original source masks.

The revised GIS intersection workflow explicitly keeps gain/loss code 9121 unions separate from source code 9113/9116 unions. Its exact per-feature source acreage and original archive checks must pass before quoting any areal concordance. The nominal layer names are metadata, not evidence that all features represent seagrass.

### Rigorous bound on the source-mapped 2016 history of the 222.092-acre 2024 unknown category

Based on the successful 95-source-FID areal audit in `results/charlotte_giant_algae_patches_source_verified_20261119.json`, two large 2022 algae polygons were nearly completely mapped seagrass in 2016. Without needing any new 2024 substrate classification, the within-source-polygon inclusion-exclusion inequality gives a conservative **minimum** for the historically sea-mapped subset of the 2024 target-unmapped area:

For each source polygon P, with H the 2016 sea-positive mapped subset and U the 2024 3-class-unmapped subset: `area(H ∩ U) >= max(0, area(U) - (area(P) - area(H)))`.

| Original 2022 algae FID | P source area | H 2016 sea-positive area | U 2024 target-unmapped | Guaranteed minimum H ∩ U |
|---|---:|---:|---:|---:|
| 37 | 186.620450 | 186.616124 | 117.349861 | **117.345535** |
| 2166 | 125.856861 | 125.334562 | 104.742594 | **104.220295** |
| **Combined** | 312.477311 | 311.950686 | 222.092455 | **221.565830 acres** |

Thus **at least 99.7629%** of the two giant-polygon mapped target-unmapped area lies within the 2016 source's mapped seagrass-positive polygons, subject only to the already audited original geometry and area. This is a **map history overlap lower bound**, NOT a confirmation of 2016–2024 true biological seagrass death, 2024 vegetation absence, or causal algal inhibition. It motivates historical habitat-focused field verification, not algae removal or restoration action.

## 2026-11-19 definitive source-only result: official gain/loss = three-class set difference

Full independent original 2022/2024 public GIS geometry was projected equal-area (EPSG:6933), independently source-area verified, and combined to calculate all six expected source-only map differences:

- For each of 9113/9116/9121, `gain_class = 2024_class_polygon MINUS union_of_all_2022_three_mapped_classes`.
- For each of 9113/9116/9121, `loss_class = 2022_class_polygon MINUS union_of_all_2024_three_mapped_classes`.

Separately downloaded official `Seagrass Gain` and `Seagrass Loss` layers (including original 9121 algae features, not only seagrass) were then compared with these computed polygon locations. Source archive/mapped-area checks and all six geometry comparisons **PASSED**, [GitHub Actions #44479894122](https://github.com/zuizui0223/Tampa/actions/runs/44479894122). The minimum six-class **Jaccard overlap was 0.9999944**, and every class's source/agency symmetric-difference area was <0.02 acres. Numerical release with source hashes and artifact digest: `results/charlotte_agency_change_set_difference_spatial_verified_20261119.json`.

| Mapped source class | Official Gain acreage | Official Loss acreage |
|---|---:|---:|
| 9113 patchy seagrass | 305.057 | 679.535 |
| 9116 continuous seagrass | 69.912 | 314.384 |
| **9121 attached macroalgae** | **413.285** | **345.596** |

**Important ontology correction:** a 2022 seagrass class changing to attached algae in the same mapped spatial location (or the reverse) is not 'gain' or 'loss' in the official derivative map. The mapped *coverage* did not disappear from the combined three-class universe. The 83.433 acres of 2022 algae→2024 sea category reclassification is therefore *separate* from official seagrass 'gain'. Indeed, inside giant source attached-algae FIDs 37/2166, official gain 9113+9116 overlap is zero, while their 2024 sea class area is 22.683+16.086=38.769 acres. The agency's official loss class 9121 equals the two giants' 2024 three-class-unmapped area of 117.34986+104.74259=222.09245 acres, showing the so-called *Loss* is a three-class map support loss, not a field-confirmed organism death.

Net three-class mapped area change must also reconcile: official all-class gain total 788.253 acres, loss total 1,339.515 acres, difference **−551.262 acres** (rounding). Meanwhile mapped seagrass net area is **−816.474 acres** and algae net area **+265.213 acres**; these require internal class-transition accounting beyond the agency gain/loss support polygons. Independent algebraic mass-balance QC is implemented in `analysis/117_charlotte_three_class_net_map_change_decomposition.py` and its CI, with the biological interpretation disallowed.

**Conservation inference:** 2024 'unmapped' cannot be renamed 'bare bottom', 2016-positive history does not imply 2024 mortality, and official 'gain' cannot be used as a live seagrass recovery rate. A management claim requires the original complete full-class mapping dictionary/footprint and real same-season independent field point/quadrat observations. The mapped GIS outputs are useful for targeted verification, not to recommend transplant or algal removal actions.
