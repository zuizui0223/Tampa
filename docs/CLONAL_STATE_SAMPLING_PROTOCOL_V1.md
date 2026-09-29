# Tampa clonal / below-ground measurement protocol v1

## Goal

Collect the new biological state needed to test whether persistent *Thalassia testudinum* meadows are buffered by below-ground reserve and clonal structure.

This protocol is paired with `results/clonal_state_prospective_v1_contract.json`.

The endpoint is **future quantitative meadow stability**, not binary reappearance.

## Sampling frame

Target the existing stable Tampa fixed-transect network in Old, Middle, and Lower Tampa Bay.

Use a census-oriented baseline frame rather than a 24-node subsample.

Recent 2023–2025 feasibility gives approximately:

- Old Tampa Bay: 8 *Thalassia*-positive nodes;
- Middle Tampa Bay: 11;
- Lower Tampa Bay: 14;
- total: 33.

At the actual deployment baseline, re-evaluate *Thalassia* presence and attempt to sample **all eligible baseline-*Thalassia*-positive nodes** in the three core bays.

The primary prospective TNC analysis is confirmatory only with:

- at least 30 analyzable nodes total; and
- at least 8 analyzable baseline-*Thalassia*-positive nodes in each bay.

Below that precision gate, retain the prospective estimate and uncertainty but treat it as a pilot. A null result cannot be used to reject rhizome-reserve buffering.

Do not subsample nodes after seeing the future response, and do not add alternative-seagrass-only nodes to the primary TNC cohort because they cannot supply the focal *Thalassia* rhizome measurement.

## Core placement

At each selected transect:

1. identify the permanent transect / meter-mark area;
2. place destructive cores adjacent to the monitored line or marks so the permanent observation unit is not damaged;
3. use a fixed offset rule decided before field collection;
4. collect at least 3 independent below-ground cores per node;
5. record exact GPS/location metadata, water depth at sampling, date/time, and offset from the permanent transect.

If local permitting or monitoring rules require different core placement, update the field protocol **before collecting the first core** and document the deviation.

## Primary below-ground measurement

### Rhizome total non-structural carbohydrate (TNC)

Primary mechanism predictor:

> soluble sugar + starch concentration in rhizome tissue.

The laboratory method, extraction chemistry, rhizome tissue definition, dry-mass basis, preservation delay/storage, seasonal window and sample randomization must be fixed before the future biological outcome is opened.

Node-level primary predictor:

> median rhizome TNC across valid independent cores.

Do not switch to a different reserve metric after seeing the future outcome.

## Why TNC is a reserve-state measurement

Rhizome carbohydrate is treated here as a candidate **stored reserve / buffering state**, not as an instantaneous stress sensor.

The biological prediction is therefore not that every short heat, salinity or light event immediately changes TNC. Instead, meadows with larger standardized rhizome reserves should be better able to maintain quantitative *Thalassia* state over the subsequent monitoring interval.

This interpretation also means that seasonal and tissue-position variation are measurement design problems that must be controlled before the future response exists.

## Seasonal and tissue standardization

Freeze the following before collecting the first outcome-bearing core:

- one narrow seasonal campaign, with a target of completing all primary TNC sampling within 42 consecutive days;
- a maximum allowable offset between TNC sampling and the node's contemporaneous fixed-transect baseline survey; target <=14 days in either direction where access/permits allow;
- one living rhizome tissue definition, including horizontal/vertical fraction, position relative to a living shoot, segment length and which tissues are excluded;
- one preservation method and maximum collection-to-metabolic-arrest delay;
- one allowable collection-time window, while recording exact time for every core;
- one laboratory extraction and dry-mass normalization protocol.

If logistics require a protocol change, make and document it **before** future outcome access. Do not define a season, tissue subset or preservation-delay exclusion after seeing the future response.

## Precision gate

The old 24-node design was only well positioned for very large effects. For the same approximate multiple-regression benchmark used in the hydrodynamic design (two-sided alpha 0.05; 80% power; four control degrees of freedom), approximate detectable partial correlations for the focal TNC term are:

- n = 24: about 0.57;
- n = 30: about 0.51;
- n = 33: about 0.49;
- n = 39: about 0.45;
- n = 47: about 0.41.

These are design diagnostics, not expected biological effects. The realistic 33-node frame therefore still targets moderate-to-large reserve effects, but is materially stronger than deliberately stopping at 24.

## Secondary clonal measurements

Collect when feasible:

- below-ground dry biomass per area;
- rhizome branching density;
- meristem density;
- rhizome diameter;
- internode length;
- below-ground : above-ground biomass ratio;
- shoot density in the immediately sampled patch;
- optional validated genet/clonal-continuity marker.

These are secondary and cannot replace a null primary TNC result.

## Sample handling

Minimum field metadata per core:

- node ID;
- core ID;
- date/time;
- coordinates;
- water depth;
- sampler;
- preservation start time;
- transport/storage condition;
- dry mass;
- assay batch.

For carbohydrate assays:

1. minimize time between collection and metabolic arrest/preservation;
2. use one laboratory protocol across all samples;
3. randomize samples across assay batches with respect to Tampa state class;
4. include technical standards / controls;
5. blind assay order to future outcome, which does not yet exist.

## Existing baseline state

At or near the below-ground sampling date, retain the routine fixed-transect variables:

- focal frequency;
- Braun–Blanquet all-point state;
- blade length where collected;
- shoot density where collected;
- water body;
- survey timing.

These are controls / baseline state, not new mechanism predictors.

## Future endpoint

Primary:

> next fixed-transect survey focal frequency − baseline focal frequency.

Secondary:

- next Braun–Blanquet minus baseline;
- next blade length minus baseline;
- next shoot density minus baseline.

Do not use annual binary reappearance as the primary outcome.

## Primary prediction

Under the prespecified model `future_delta_frequency ~ standardized_rhizome_TNC + baseline_frequency + baseline_Braun_Blanquet + water_body`:

> higher baseline rhizome TNC predicts a more positive / less negative future change in focal frequency.

The contract defines the formal estimator and uncertainty procedure.

## Interpretation

### Supported

A supported prospective association would be consistent with below-ground reserve contributing to meadow persistence or resistance.

It would still not, by itself, prove causal clonal buffering.

### Unsupported

A null result weakens rhizome TNC as the primary measured reserve explanation **only if** the frozen precision gate is met (>=30 analyzable nodes and >=8 per core bay).

Below that gate, report the result as a pilot estimate and do not interpret a wide/null interval as evidence against clonal buffering.

In either case, do not rescue the primary hypothesis by selecting another measured clonal trait after outcome access.

## Paired environmental measurements

If resources allow, co-locate:

- temperature logger;
- salinity logger;
- PAR logger;
- simple hydrodynamic/current exposure measurement.

These should be treated as separate predeclared measurement layers, not merged into a large post-hoc predictor search.

## Field decision rule

Do not begin the outcome-bearing prospective study until the following are frozen:

- contemporaneous baseline eligibility and final node list;
- confirmatory 30-node / 8-per-bay precision gate;
- seasonal campaign window and maximum TNC-to-baseline survey offset;
- core offset rule;
- number and diameter/depth of cores;
- tissue fraction / rhizome-position definition used for TNC;
- allowable collection-time window;
- preservation procedure and maximum collection-to-metabolic-arrest delay;
- lab assay;
- future survey window;
- primary analysis script.

The scientific value comes from measuring a new biological state **before** the future quantitative response is known.
