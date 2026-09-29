# Tampa hydrodynamic exposure source preflight v2

## Purpose

Define what counts as a genuinely new hydrodynamic measurement layer for the Tampa mechanism program before any biological response is linked to it.

The goal is to avoid replacing the retired generic connectivity proxies with another arbitrary spatial index.

## Updated decision

A credible network-scale candidate has now been identified:

> **NOAA Tampa Bay Operational Forecast System (TBOFS) gridded 3-D ROMS output.**

Official NOAA documentation states that TBOFS covers the whole of Tampa Bay, resolves horizontal grid spacing of roughly 100 m to 1.2 km, uses 11 terrain-following vertical levels, and outputs currents, temperature, salinity and water level in NetCDF.

Relevant public provenance:

- TBOFS system page: https://tidesandcurrents.noaa.gov/ofs/tbofs/tbofs.html
- TBOFS information / grid description: https://tidesandcurrents.noaa.gov/ofs/tbofs/tbofs_info.html
- NOAA/NCEI dataset: Regional Hydrodynamic Model Outputs of the NOAA Tampa Bay Operational Forecast System (TBOFS)
- NCEI DOI: https://doi.org/10.25921/fztr-mf31
- NCEI THREDDS model archive: https://www.ncei.noaa.gov/thredds/catalog/model/model.html
- Current NOMADS production files: https://nomads.ncep.noaa.gov/pub/data/nccf/com/nosofs/prod/

This changes the previous preflight conclusion. A gridded current field with archived provenance exists and is physically much closer to the required new measurement layer than HF-radar surface currents or buoy water-quality data.

It is **not yet accepted as meadow-scale near-bed exposure**. The next gate is response-blind grid/depth relevance and node coverage.

## Other public sources retained as context

### Ft. De Soto continuous buoy programme

Public repository:

- https://github.com/tbep-tech/desoto-buoy

The repository documents two Ft. De Soto buoys with approximately 15-minute observations of temperature, conductivity, salinity, pH, chlorophyll-a, pheophytin and dissolved oxygen beginning in 2019.

These observations were collected partly to support / validate a local hydrodynamic model.

**Boundary:** these buoy data are not themselves current velocity or residence time and cover only two local sites. They must not be relabelled as hydrodynamic exposure for the Tampa transect network.

### USF/CMS Ft. De Soto WERA HF radar

Public information:

- https://ocl.marine.usf.edu/hfradar/wera/notes/ftdesoto_wera_notes.html

The Ft. De Soto WERA site reports hourly offshore sea-surface radial current speed/direction products and has operated since 2010.

**Boundary:** HF-radar surface currents are not automatically equivalent to near-bed meadow exposure, especially for shallow fixed seagrass transects.

## Frozen response-blind TBOFS preflight

Before any Tampa biological outcome is linked to TBOFS, perform only the following physical/source audit.

### 1. Grid and variable audit

Use one recent TBOFS gridded field file solely to identify:

- horizontal longitude/latitude grids;
- wet/dry or mask information;
- vertical coordinate and ordering;
- eastward/northward or ROMS u/v current components;
- whether the lowest valid model level can be interpreted reproducibly as the near-bed level;
- units and missing-value conventions.

Do not inspect any seagrass response while choosing the current variable or vertical level.

### 2. Stable-node spatial coverage

Construct a coordinates-only table containing:

- node_id;
- water_body;
- longitude;
- latitude.

Do not carry focal frequency, Braun-Blanquet, blade length, shoot density, loss, or re-recording columns into this step.

Map every stable node to the nearest valid wet TBOFS current cell under one fixed geodesic rule.

Report:

- number and proportion of 71 stable nodes with a valid mapping;
- nearest-cell distance distribution;
- coverage by water body;
- number of nodes for which the nearest valid current cell is clearly outside the shallow meadow setting.

### 3. Network-use gate

TBOFS may advance to a network-scale hydrodynamic test only if:

- at least 30 stable nodes map to valid current cells;
- mapped nodes span Old, Middle and Lower Tampa Bay;
- the median node-to-valid-cell distance is <= 1 km;
- no mapped node used in the primary set is > 2 km from its assigned cell;
- the selected vertical current variable has an explicit reproducible near-bed interpretation.

If this fails, retain TBOFS only as broad physical context and move to direct local current measurements / ADCP deployment.

These thresholds are frozen before any hydrodynamic–seagrass association is calculated.

## Candidate prospective mechanism test

If the source gate passes, use the hydrodynamic layer prospectively rather than mining another historical transition subclass.

### Primary physical exposure

Node-level high-current exposure:

> 90th percentile of near-bed current speed, where speed = sqrt(u^2 + v^2), over the frozen exposure window.

Secondary descriptive physical summaries may include:

- median near-bed current speed;
- current-speed coefficient of variation;
- duration above an externally fixed high-current threshold;
- directional persistence.

Secondary summaries cannot replace a null primary p90-current result.

### Biological hypothesis

The ecological target is not simply "more current is bad".

The discriminating hypothesis is **meadow-state buffering of physical exposure**:

> hydrodynamic exposure has a more negative association with future quantitative state when the current meadow is sparse, whereas denser established meadow state partly buffers that exposure.

This is the physically testable version of the proposed self-facilitation / exposure-buffering idea.

### Primary future model

For a genuinely future fixed-transect response:

```text
future_delta_frequency
  ~ baseline_frequency
  + p90_nearbed_current
  + baseline_frequency × p90_nearbed_current
  + water_body
```

Directional prediction:

- p90 current main effect: non-positive;
- baseline-frequency × p90-current interaction: positive if denser meadows buffer hydrodynamic exposure.

The primary endpoint is continuous change in focal frequency, not binary reappearance.

The exposure window, interpolation rule, vertical level, feature definition, future survey window and uncertainty procedure must be frozen before the future response is opened.

## Acceptance criteria for any hydrodynamic mechanism layer

A candidate hydrodynamic source is accepted for biological testing only if it supplies at least one physically interpretable field such as:

- current speed;
- current direction / vector components;
- near-bed shear stress;
- wave orbital velocity;
- residence time;
- flushing time;
- freshwater-plume exposure;
- time-varying transport/connectivity derived from a validated flow field.

The source must also pass all of:

1. independent of the focal biological response;
2. stable public or archived provenance;
3. sufficient temporal coverage for a predefined biological period or future response;
4. geospatial precision adequate to map exposure to fixed transects;
5. physical relevance to the seagrass canopy / near-bed environment;
6. no tuning of spatial scale or exposure summary after biological outcome access.

## Current decision

**TBOFS is promoted from “source not yet identified” to “candidate identified; response-blind spatial/depth preflight required.”**

Do not yet call TBOFS current a validated meadow exposure layer.

The immediate next action is to run the coordinates-only grid/depth coverage audit. If that passes, freeze the prospective p90 near-bed-current test against a future quantitative Tampa response.
