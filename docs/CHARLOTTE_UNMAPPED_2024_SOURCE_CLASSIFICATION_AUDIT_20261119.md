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
