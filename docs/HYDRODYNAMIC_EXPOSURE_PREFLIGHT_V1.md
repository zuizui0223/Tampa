# Tampa hydrodynamic exposure source preflight v1

## Purpose

Define what counts as a genuinely new hydrodynamic measurement layer for the Tampa mechanism program before any biological response is linked to it.

The goal is to avoid replacing the retired generic connectivity proxies with another arbitrary spatial index.

## Public sources identified

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

**Boundary:** HF-radar surface currents are not automatically equivalent to near-bed meadow exposure, especially for shallow fixed seagrass transects. They require an explicit spatial and depth-relevance audit before use.

### Existing Tampa circulation / flushing literature

TBEP repositories and references identify existing Tampa Bay hydrodynamic/circulation work, including Old Tampa Bay flushing/circulation studies and a 2024 hydrodynamic-flushing optimization study.

**Current status:** a stable, openly retrievable gridded model product that can be mapped reproducibly to the fixed-transect network has not yet been identified in this preflight.

## Acceptance criteria for a hydrodynamic mechanism layer

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

## Preferred design

### Option A — validated model field

Use a previously validated hydrodynamic model with archived gridded output.

Response-independent preflight:

- freeze model version and forcing period;
- freeze target physical variable;
- map each fixed transect to the same spatial interpolation rule;
- quantify node coverage before biological response access.

### Option B — direct local measurement

Deploy current meters / ADCPs at a smaller matched subset of stable transects.

Co-locate, where feasible:

- near-bed current velocity;
- temperature;
- salinity;
- PAR.

This is more expensive but directly tests whether the unresolved stable-site effect reflects physical exposure.

## Primary prospective hypothesis

After controlling for baseline meadow state and water body:

> independently measured hydrodynamic exposure predicts future quantitative meadow change.

The primary biological endpoint should be continuous (for example future change in focal frequency), not binary reappearance.

## Decision from this preflight

**Do not start a Tampa-wide retrospective hydrodynamic analysis from the currently identified Ft. De Soto buoy or HF-radar products alone.**

They are useful source candidates / model-validation context but do not yet satisfy the requirements for a network-wide near-bed exposure layer.

Next action:

1. locate archived Tampa hydrodynamic model output with gridded currents/residence time, **or**
2. design a smaller direct-current measurement campaign at matched fixed transects.

This keeps hydrodynamics as a genuine new measurement layer rather than a renamed connectivity proxy.
