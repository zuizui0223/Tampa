# Tampa–Charlotte biological validation: incompatible algae observation types
Source-identified design amendment, 2026-11-19. No new quadrat outcomes were observed.

## Four different states that must NOT be collapsed

| Observation source | Variable | What it measures | What missing / zero means |
|---|---|---|---|
| SWFWMD Suncoast aerial interpretation 2022/2024 | FLUCCSCODE 9121 | Polygons classified **attached macroalgae** | No map polygon is **not** measured algal absence, bare bottom or photo-coverage confirmation |
| CHAP seagrass quadrat dataset (Program 570) | Drift algae Braun–Blanquet score | **Drift/free** macroalgae on the sampling date, according to original export and protocol | May have source missing fields that older analyses converted to 0, not necessarily independently observed non-detection |
| CHAP program 570 | Epiphyte loading on seagrass blades | Epiphyte load on host plant material | Not equal to attached benthic algal beds or drift macroalgae |
| CHAP program 570 | Thalassia/Halodule/Syringodium species BB, shoot density, blade length | Living focal seagrass community and quantitative condition at sampled sites | An unsampled quadrat is NOT 0 or verified absent |

**Exact source evidence:** The FDEP/Janicki Environmental 2022 final report *Identifying Potential Drivers of Change in Seagrass and Algal Community Composition in SWFL Aquatic Preserves*, sections Data Collection (p. 6) and Macroalgae/Drift Algal Occurrence and Abundance (p. 29), explicitly distinguishes species-specific seagrass scores from drift algae BB and epiphytic cover, and states that absent drift algae abundance **fields** were treated as zeros for its analysis. Source: https://floridadep.gov/sites/default/files/Southwest-FL-Seagrasses-Report-2022.pdf . This analysis practice belongs to that older publication; we have NOT audited its underlying missing-code conventions in original station workbooks. Do not accuse the field program of having no true absence data or infer how many entries were affected without retrieving original tables.

SEACAR 570 programme record: https://data.florida-seacar.org/programs/details/570 . It specifically notes complicated joins, repeat quadrats versus start/end of bed, including other estuary program records, some excluded sites, and that transect **midpoints**, not exact quadrat coordinates, are the published point location representation. Independent site and annual-visit flags require verification before alignment with aerial imagery.

## Why this matters for the biological hypothesis

The category-swapping model and giant algae interior GIS result are **cartographic** events, not proof of plant competition or ecological hysteresis. A map class 9121 can rise while field **drift algae** does not; different algal growth forms and measurement support mean this is not biological disagreement unless both are measured comparably. Similarly, epiphyte loading is a distinct local light/condition variable.

The 2022 FDEP prior report did observe that drift algae occurrence increased across multiple locations, but notes that an Estero Bay monitoring change from 2016 onwards may contribute to apparent increases. This is an observation-protocol concern in *published* evidence, not a newly discovered dataset-level mechanism.

The field monitor reportedly samples after the summer growing season (August–October), while SWFWMD Suncoast aerial-photo map images are acquired principally in winter (December–March), meaning a direct same-calendar-year map-vs-field comparison can be seasonal mismatch rather than detection failure. Both actual original image acquisition date and site-field dates must be joined.

## Precommitted validation checks when actual CHAP 1999–2025 workbook becomes available

1. Identify original record grain (transect, station along transect, repeat 1m² quadrat, site, year/date) and exact zero/non-detect/unvisited/missing conventions separately for sea species, drift algae and epiphytes.
2. Verify sampling-year site rosters (2022 and 2024) and exclude site IDs explicitly excluded by the source SEACAR programme, *before* comparing to 2022/2024 aerial maps; the public 63-point registry is not a 63-visit annual response dataset.
3. Create **three observation models**, not one algae index: a) registered mapped attached-benthic macroalgae polygons, b) field drift algae BB, c) leaf epiphyte load; never assume convertibility without crosswalk/training field samples.
4. Compare within year only when exact field date/flight windows permit; explicitly label time lag and whether each measured quadrat is in original mapped imagery footprint; lack of a map polygon is unknown, not field absence.
5. In the biologically predictive test use **prior independent station-level sea cover/shoot density or blade condition** to predict future repeated same-site state; compare site-only and observation-process-aware models under temporal holdout, recording all failures.
6. For proposed algal shading, measure independently attached algae, field benthic PAR above/below canopy and water-column attenuation; require correct temporal ordering prior to testing next-visit seagrass change.

**Status:** original 1999–2025 CHAP workbook and exact 2022/2024 field visit/quadrat rows were NOT accessed. Public SEACAR point registry source identity/count of 63 was CI-verified, with independent geometry-to-giant map proximity being attempted in a separate CI; no biological site outcome or mapping accuracy estimate exists from these currently registered point positions.

**Inference:** measurement support must be harmonized before using the Charlotte external field monitoring as a test of the original Tampa 'coarse occupancy remains while meadow condition declines' hypothesis. This correction is not a negative test of the hypothesis; it protects it from invalid data joins.
