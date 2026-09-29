# Tampa clonal / below-ground measurement protocol v1

## Goal

Collect the new biological state needed to test whether persistent *Thalassia testudinum* meadows are buffered by below-ground reserve and clonal structure.

This protocol is paired with `results/clonal_state_prospective_v1_contract.json`.

The endpoint is **future quantitative meadow stability**, not binary reappearance.

## Sampling frame

Target the existing stable Tampa fixed-transect network in Old, Middle, and Lower Tampa Bay.

Initial target:

- 36 stable transect nodes;
- minimum analyzable set: 30 nodes;
- approximately balanced representation of:
  - quantitatively stable meadows;
  - persistent-recorded meadows with recent quantitative degradation;
  - low/unstable quantitative-state meadows.

Stratification uses only information already available before below-ground sampling.

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

The laboratory method, extraction chemistry, dry-mass basis, storage duration, and sample randomization must be fixed before the future biological outcome is opened.

Node-level primary predictor:

> median rhizome TNC across valid independent cores.

Do not switch to a different reserve metric after seeing the future outcome.

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

After accounting for baseline focal frequency, baseline Braun–Blanquet state and water body:

> higher baseline rhizome TNC predicts a more positive / less negative future change in focal frequency.

The contract defines the formal estimator and uncertainty procedure.

## Interpretation

### Supported

A supported prospective association would be consistent with below-ground reserve contributing to meadow persistence or resistance.

It would still not, by itself, prove causal clonal buffering.

### Unsupported

A null result would rule against rhizome TNC as the primary measured reserve explanation under this design. Do not rescue the hypothesis by selecting another measured clonal trait after outcome access.

## Paired environmental measurements

If resources allow, co-locate:

- temperature logger;
- salinity logger;
- PAR logger;
- simple hydrodynamic/current exposure measurement.

These should be treated as separate predeclared measurement layers, not merged into a large post-hoc predictor search.

## Field decision rule

Do not begin the outcome-bearing prospective study until the following are frozen:

- selected nodes;
- core offset rule;
- number and diameter/depth of cores;
- tissue fraction used for TNC;
- preservation procedure;
- lab assay;
- future survey window;
- primary analysis script.

The scientific value comes from measuring a new biological state **before** the future quantitative response is known.

## Node replication and synchronized timing

The inferential unit for the future primary endpoint is the stable transect node. Three cores within a node improve measurement of TNC but do not create three independent future meadow trajectories.

A response-free design-sensitivity audit therefore raises the preferred target from 24 to **36 nodes**, with **30 nodes** as the minimum analyzable set. At n = 36, the approximate 80%-power threshold for one focal TNC coefficient after the frozen baseline controls is |partial r| ≈ 0.467 (partial R² ≈ 0.218); at n = 24 it would require approximately |partial r| ≈ 0.573.

Whenever permissions allow, use the same synchronized 47-node tri-bay screening and final deployment frame as the direct hydrodynamic study. Collect TNC cores during the same predeclared seasonal baseline window. Rhizome carbohydrate is seasonally dynamic, so broad sequential sampling across seasons is not accepted as a silent design feature.

Co-location is scientifically valuable because it permits a separately frozen joint test of internal reserve and external physical buffering. The standalone TNC test remains governed by its own contract.