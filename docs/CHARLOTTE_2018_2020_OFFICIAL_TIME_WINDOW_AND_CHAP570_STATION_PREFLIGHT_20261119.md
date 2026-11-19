# Charlotte Harbor: time-gated historic GIS and independent monitoring station registry
Source-verification update, 2026-11-19. No new field observations or causal seagrass mortality evidence.

## An earlier apparent GIS schema failure was access-window dependent

SWFWMD documents that its GIS Open Data portal is publicly accessible **6am to 10pm local Florida time**: https://www.swfwmd.state.fl.us/resources/data-maps/gis-maps-survey . This is the *portal* policy; it does not guarantee that every separate service is always available during those hours.

Previously the official 2018/2020 legacy SWFWMD MapServer returned a JSON status/messages object without geometry/type fields in nighttime GitHub Actions runs. We had recorded a strict source `STOP`, correctly declining to invent source polygons or biological results. The 2018 source was then rechecked at **06:14 America/New_York** and original polygon source identity, year, EPSG:2882 and FLUCCSCODE class fields became readable. Source CI passed: https://github.com/zuizui0223/Tampa/actions/runs/44512363799 .

| Historic source layer inside the fixed Charlotte 2016/22/24 envelope | All original polygons intersecting bbox | 9113 patchy sea | 9116 continuous sea | 9121 attached algae | Other original classes not yet enumerated |
|---|---:|---:|---:|---:|---:|
| **2018** | **3,429** | 897 | 429 | 0 | 2,103 |
| **2020** | **4,392** | 1,267 | 403 | **70** | 2,652 |

**Polygon counts are not area or biomass**. An absence of the 9121 map code in 2018 does not establish algal biological absence, and a 2020 code-positive count is not a comparable species abundance or independent field point.

Importantly, the historical MapServer exposes one field typed ESRI OID ('OBJECTID') but does **not** advertise `objectIdField` directly; counts are successful, while **exact-feature original OID/geometry-area certification is still unpassed**. Do not claim historical 2018/2020 spatial transitions before OID-roster, geometry, map extent, source area fields and code dictionary checks. Old yearly 'terminal STOP' documents are superseded in part by the new 06:14 source data but retain their past failure logs as evidence of restricted access.

Full source-pinned counts and original source metadata SHA: `results/charlotte_2018_2020_legacy_source_counts_verified_20261119.json`. The source script now records the 6am–10pm Eastern access window and marks out-of-window calls as `SKIP`, not as a source scientific failure. UTC↔EST and UTC↔EDT synthetic tests were added to `validation/test_charlotte_2018_2020_legacy_map_preflight.py`.

## Independent public field-monitoring station registry is accessible

SEACAR program [570](https://data.florida-seacar.org/programs/details/570) describes annual *Charlotte Harbor Seagrass Monitoring*, including 1m² quadrat Braun–Blanquet seagrass cover, blade lengths, shoots and epiphyte observations, but actual original field data are a separate workbook/dataset. Source metadata also cautions that related program 571/other exclusions and transect midpoint location records require correct joins, not blind site count comparisons.

The **public USF SEACAR GIS MapServer 179** exposes exactly **63 ProgramID=570 point records**, with a verified unique OID field OBJECTID_1 and exact OID roster. Source CI passed: https://github.com/zuizui0223/Tampa/actions/runs/44512764413 . Full metadata SHA/field dictionary and source IDs: `results/charlotte_chap570_public_stations_source_verified_20261119.json`. Its MapServer omits `objectIdField` in layer metadata but contains one field typed ESRI OID and the exact query OID field name matches; this was source-audited rather than silently assigning an ID.

**Crucial distinction:** 63 publicly registered station positions are NOT proof of 63 independent sites sampled in 2024, nor actual quadrat positions, nor a 2024 taxon observation. The next spatial audit `analysis/122_chap570_public_station_giant_proximity.py` measures distance from these registered station midpoints to the two original 2022 giant algae source polygons' 2024 three-class-unmapped cores, while keeping year-specific site visitation and real algae/seagrass measurements unknown. Its results must pass source SHA/QC before use.

### Ecological next step

The core Tampa result remains that plant condition, local frequency, density and recorded presence should not be collapsed into one persistence indicator. The Charlotte GIS anomaly remains a remote-sensing classification problem until independent 2022/24 in-situ species abundance and surveyed footprint are available. A public point registry can identify spatial monitoring overlap or gaps, but cannot establish a delayed or causal meadow state transition.

