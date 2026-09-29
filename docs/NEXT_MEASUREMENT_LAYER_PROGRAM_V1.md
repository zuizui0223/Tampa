# Tampa next-measurement-layer program v1

## Purpose

The retrospective annual and exact-point observation-state record is now considered **mechanistically saturated**.

The Tampa archive is still valuable for ecological pattern, observation-state transitions, state decoupling, community insurance, and claim-boundary audits. It is no longer the preferred source for generating additional mechanism claims by repeatedly decomposing annual presence, re-recording, local history, lag structure, or state-transition subgroups.

The next mechanism step must introduce a genuinely new biological or physical measurement layer.

## Terminology rule

A point that is unrecorded in year t and recorded again in year t+1 or t+2 is described as:

- **re-recording**;
- **reappearance in the observation record**;
- **recorded-state return** when necessary for a compact variable name.

Do **not** describe binary reappearance as ecological, demographic, clonal, or physiological **recovery** unless an independent biological state demonstrates recovery.

Legacy file names or schema names containing `recovery` are retained for provenance and reproducibility only. They do not determine manuscript terminology.

## Why the old measurement layer stops here

The annual observation-state archive has already been decomposed across:

- binary detection;
- within-transect frequency;
- Braun–Blanquet state;
- blade length;
- shoot density;
- community composition;
- lag-1 and older history;
- exact-point loss and re-recording;
- mixed-species occupancy;
- local continuity;
- pre-loss history;
- return fragility / quantitative state at re-recording.

These analyses are useful as descriptive ecology and boundary evidence. Repeatedly deriving another transition variable from the same annual table now has lower mechanistic value than measuring the biological state that the annual table cannot resolve.

## Priority 1 — below-ground / clonal state

Frozen future design:

- `results/clonal_state_prospective_v1_contract.json`
- `docs/CLONAL_STATE_SAMPLING_PROTOCOL_V1.md`

### Biological hypothesis

Persistent *Thalassia* occurrence is buffered by below-ground state rather than by above-ground condition alone.

Candidate mechanisms:

- rhizome biomass;
- non-structural carbohydrate reserve;
- rhizome branching / architecture;
- meristem density;
- below-ground to above-ground biomass ratio;
- genet/clonal continuity;
- meadow age or persistence proxy.

### Primary test

At fixed transects spanning stable, quantitatively declining, and recently re-recorded observation states:

1. sample below-ground state before the next annual transect outcome;
2. freeze a small set of biologically motivated clonal/reserve predictors;
3. test whether below-ground state predicts future quantitative persistence or recorded-state stability beyond current frequency/abundance and stable node identity;
4. do not use binary reappearance as proof of recovery.

### Strongest discriminating prediction

If clonal buffering is real, sites with similar current above-ground frequency/abundance but higher below-ground reserve should maintain quantitative state more strongly in the next monitoring wave.

### Required new information

This hypothesis cannot be identified from the current annual observation table.

## Priority 2 — node-scale high-frequency stress

### Biological hypothesis

The annual/monthly environmental summaries failed because biologically relevant stress occurs at diel or event scales that are erased by segment-level routine monitoring.

Priority sensors:

- temperature;
- salinity;
- PAR / benthic irradiance;
- optionally dissolved oxygen and turbidity if loggers are available.

### Prospective design

Use response-unopened logger exposure to predict a genuinely future fixed-transect outcome.

The existing open PR for Old Tampa Bay continuous temperature is consistent with this rule because it freezes a 2026 logger exposure -> 2027 *Thalassia* condition test before the 2027 focal response is opened.

Preferred exposure features should be fixed from physiology or external literature before outcome access, for example:

- cumulative heat load;
- duration above a fixed temperature threshold;
- minimum salinity event duration;
- joint heat × fresh event duration;
- daily/diel PAR deficit;
- recovery time after acute events.

Do not retrospectively tune thresholds against the Tampa biological outcome.

## Priority 3 — hydrodynamic exposure / residence time

### Biological hypothesis

Persistent among-transect differences reflect local transport and exposure regimes that coordinates, depth, sediment, and bay-level water quality do not resolve.

Candidate measurements:

- current velocity;
- wave/orbital exposure;
- residence time / flushing;
- freshwater plume exposure;
- local shear stress;
- near-bed flow variability.

### Primary discriminating prediction

After matching or controlling for present meadow state, transects with different hydrodynamic exposure should differ in future persistence, community state, or stress response.

### Preferred evidence

Use an independently validated hydrodynamic model, deployed current meters/ADCPs, or another pre-specified physical layer. Do not construct a new arbitrary connectivity proxy from the same annual biological table.

## Priority 4 — canopy / epiphyte microenvironment

This is distinct from the failed bulk Secchi × depth proxy.

Measurements:

- canopy-level PAR;
- epiphyte biomass/load;
- spectral attenuation;
- local turbidity;
- canopy self-shading.

The test should distinguish actual light experienced by leaves from bay-segment bulk clarity.

## Priority 5 — acute disturbance / disease

Candidate new observations:

- disease lesions;
- grazing or physical damage;
- storm sediment disturbance;
- burial/scour;
- boating/propeller disturbance;
- acute freshwater or heat events.

These may explain local state changes that appear unstructured in annual averages.

## Sampling strategy

Use a matched design instead of measuring everything everywhere.

### Core groups

1. quantitatively stable *Thalassia* meadows;
2. persistent-presence but quantitatively degrading meadows;
3. low-frequency / unstable recorded-state meadows;
4. observation-state re-recorded points or transects, labelled as **re-recorded**, not recovered.

### Matching variables

Match as closely as practical on:

- water body;
- present focal frequency / abundance;
- depth;
- sampling season;
- stable-transect history.

Then ask whether the new measurement layer separates future trajectories.

## Mechanism-gate rule

A new mechanism branch is allowed only if at least one of the following is true:

1. it uses a new biological state not present in the annual archive;
2. it uses a new physical measurement layer with substantially finer temporal or spatial resolution;
3. it scores a genuinely future response whose contract was frozen before response access;
4. it uses a response-unopened external dataset with a pre-authorized schema.

Otherwise it belongs to descriptive/sensitivity work, not to the mechanism program.

## Current priority ordering

1. **Below-ground / clonal state**
2. **High-frequency local temperature / salinity / PAR**
3. **Hydrodynamic exposure / residence time**
4. **Canopy / epiphyte light microenvironment**
5. **Acute disturbance / disease**

The first two have the strongest ability to discriminate between persistent meadow legacy and unresolved short-timescale stress.

## Current program status

- Annual/exact-point retrospective mechanism decomposition: **HARD STOP**
- Binary reappearance terminology: **re-recording / reappearance, not recovery**
- 2026 OTB continuous-temperature -> 2027 prospective test: **allowed new-measurement branch**
- New clonal/below-ground field layer: **highest-priority next mechanism study**
- Hydrodynamic layer: **next independent physical-template test**
