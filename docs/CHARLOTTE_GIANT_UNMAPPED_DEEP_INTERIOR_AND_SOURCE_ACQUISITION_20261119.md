# Charlotte Harbor giant 2022 algae patches: 2024 unclassified interiors and source acquisition

Source-verified, 2026-11-19. This is an aerial-photo mapped-class spatial audit, not a field-seagrass death or recruitment study.

## Newly verified: the 222-acre 2024 absence from three mapped vegetation codes is not just a thin boundary artifact

Using **unchanged** original 2016, 2022 and 2024 SWFWMD GIS GeoJSON (exact source checksums and official individual acreage fields), we took the original 2022 attached-algae polygons FID **37** (186.620 acres) and FID **2166** (125.857 acres). We subtracted all original mapped 2024 **9113 patchy seagrass**, **9116 continuous seagrass**, and **9121 attached macroalgae** polygons to get U, the site where none of these three categories is recorded.

Each location is tested in an equal-area CRS (EPSG:6933). At each d metres, a mapped-unclassified core must be **at least d metres inside the original 2022 algae patch AND at least d metres from ANY of the three 2024 mapped vegetation polygons**. A 2024 unmapped core may still contain real organisms or other photo-interpretation classes.

| Both-year mapped class boundary distance | FID 37 unmapped internal acres | FID 2166 unmapped internal acres | Two original giant FIDs total |
|---|---:|---:|---:|
| 0m | 117.350 | 104.743 | **222.093** |
| 5m | 100.527 | 89.756 | **190.283** |
| 10m | 85.448 | 77.030 | **162.478** |
| 25m | 52.571 | 48.368 | **100.939** |
| 50m | 18.298 | 18.964 | **37.262** |
| 100m | 0.016 | 0.261 | **0.277** |

The 25m interior retains **45.45%** of the original 2024 three-class-unmapped area; 50m retains **16.78%**. At 100m, almost none remains. Thus it is not all narrow GIS boundary slivers, but also not extensive deep >100m unmapped interiors. This says nothing about real substrate identity.

**Historical mapped state:** the exact 2016 original mapped seagrass-positive polygons intersect **222.074 of the 222.093 acres** missing from the three 2024 categories, compared with the previous more conservative inclusion–exclusion lower bound 221.566 acres. All 25m and 50m far-interior cores tested were inside 2016 mapped seagrass-positive geometry. This is a map-history statement, not a 2016–24 physiological or demographic event.

Full GitHub source and QA: `analysis/118_charlotte_giant_unmapped_core_depth.py`, `validation/test_charlotte_giant_unmapped_core_depth.py`; reproducible GitHub Actions [run #44509444813](https://github.com/zuizui0223/Tampa/actions/runs/44509444813), artifact [#14522875056](https://github.com/zuizui0223/Tampa/actions/runs/44509444813/artifacts/14522875056), ZIP SHA256 `f43571dbf529c55725420f934fde4b4743897101b953c303a3b70c7db72be802`. The ZIP includes full six-distance source ledger and **19 polygon geometry candidates across nested 25m, 50m, 100m thresholds** (minimum 0.25 acre per polygon), **not** 19 independent sampling stations, confirmed ecological absence or permitted fieldwork. Numerical release: `results/charlotte_giant_unmapped_interior_source_verified_20261119.json`.

## Crucial limits

- U means *not among the three publicly extracted SWFWMD vegetation classes in 2024*, not observed bare bottom, no seagrass, no attached algae, death, disturbance or loss of restoration opportunity.
- The apparent 2016 history is a map-positive classification. Historic 2016 presence need not mean that exact plant stems survived to 2022.
- A 25m or 50m buffer removes GIS edge and category boundaries, **not** errors in photo interpretation, visibility, mapping footprint or classification of bottom.
- Official change-layer Loss in 2022–24 is the set difference from these same three mapped classes (all six mapped class areas and locations reproduced, minimum Jaccard 0.9999944), not independent ground truth.

## Authoritative full-data route discovered; classification completeness NOT verified

The [Florida SEACAR Program 566 — SWFWMD SWIM Seagrass Mapping](https://data.florida-seacar.org/programs/details/566) documents original GIS files named **Seagrass_in_2020.zip**, **Seagrass_in_2022.zip**, **Seagrass_in_2024.zip** (added July 15 2025), plus a standardized statewide data export. The source explicitly says a **valid email address is required to download** dataset files for corrections/usage tracking. No unapproved account or fabricated contact email has been used. The program's technical contacts are listed on that official page. The same District [open-data portal](https://data-swfwmd.opendata.arcgis.com/) is another source.

**Warning:** file names alone do NOT prove the ZIP contains a full benthic-habitat classification/imagery coverage rather than the same three seagrass + attached algae categories already analyzed. Check the original FLUCCSCODE dictionary, total feature count, exact source OIDs, mapped footprint boundary, data-vintage and source layers before using it as a full-class map. A statewide FWC latest-source compilation must not be substituted for a two-date same-footprint survey; its own metadata warns against longitudinal comparisons.

Minimum required metadata/datasets for interpreting the 222 acres: original 2022+2024 *all benthic classes* (including 0, 5400, 6510, 6540, 7210 where produced and any unclassified/not-visible/photo-opacity classes), explicit surveyed orthophoto footprints and water mask, image acquisition date/time, source FLUCCS class key, observation-quality/accuracy points not used for training, and actual repeated quantitative field seagrass and algae observations with reported effort. Do not assume any one layer contains these unless verified.

## What the next complete-source test must report

Within the two FID polygons, split the currently unknown 222 acres into (a) source 2024 category known but omitted by the restricted three-class FeatureServer, (b) inside documented surveyed/photo-interpreted mask with no vegetation class, (c) outside surveyed mask/occluded and thus genuinely unobserved. These must be mutually exclusive and area-closed. Only the second case would give evidence for *mapped absence of the three classes*, not perfect biological absence. If no explicit coverage mask exists, leave (b) and (c) unresolved instead of calling it bare.

Even after this source reconciliation, seagrass persistence/death and the role of algae in future cover require independent quadrat-level field data. No ecological intervention was made.

## Original ZIP intake is now an executable, synthetic-tested gate

The new source-only program `analysis/119_swfmd_original_seagrass_zip_intake_gate.py` checks any **locally obtained, authorized** official SWFWMD/SEACAR shapefile ZIP, without submitting an email address or downloading through a restricted registration form. It inventories each original polygon shapefile's source code field, complete FLUCCSCODE value counts, possible acreage fields, projection-WKT hash, and the ZIP digest before any overlay.

Execution once authorized ZIP file is already available:

```bash
python analysis/119_swfmd_original_seagrass_zip_intake_gate.py \
  --source-zip /path/to/Seagrass_in_2024.zip \
  --out results/local_2024_original_zip_source_class_gate.json
```

**Strict semantic result:** if source code values are only `9113`, `9116`, and `9121`, the ZIP is *not* eligible to resolve 2024 target 'unmapped' bottom. If extra values are present, the archive is potentially more informative but still does not prove full photo-survey coverage. A ZIP containing only ESRI geodatabase (.gdb) rather than shapefile is explicitly STOP until a documented GIS-geodatabase parser is implemented. This prevents pretending a file-format failure is a negative biological finding.

Synthetic CI tests of three-code and background-code ZIPs, malformed member sets, unsafe relative ZIP paths and geodatabase-only inputs completed successfully in [GitHub Actions #44510315069](https://github.com/zuizui0223/Tampa/actions/runs/44510315069). **The actual original 2024 SEACAR ZIP has not been downloaded by this analysis**; its class contents and full coverage remain unknown.
