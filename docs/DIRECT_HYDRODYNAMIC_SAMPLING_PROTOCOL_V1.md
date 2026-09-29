# Tampa direct shallow-water hydrodynamic sampling protocol v1

## Goal

Directly test whether an established *Thalassia testudinum* canopy buffers local hydrodynamic exposure and whether stronger measured buffering predicts greater future quantitative meadow stability.

This protocol replaces TBOFS near-bottom velocity as the preferred meadow-scale hydrodynamic layer. The TBOFS response-blind preflight found geographically close grid cells for most transects, but model bathymetry was systematically deeper than the shallow physical transect record. TBOFS therefore remains useful as regional circulation context, not as literal canopy-scale near-bed flow.

Paired current measurements are a genuinely new physical layer. They are not derived from the annual biological state table.

## Ecological hypothesis

### Canopy hydrodynamic buffering hypothesis

Established seagrass canopies alter their own physical environment.

The primary mechanistic prediction is:

> water motion measured inside the canopy is attenuated relative to simultaneous local ambient water motion, and transects with stronger measured attenuation experience less subsequent decline in *Thalassia* quantitative state after baseline meadow state and ambient forcing are represented.

This is an ecosystem-engineering hypothesis, not simply a prediction that high flow is harmful.

Published field and flume work motivates direct within-canopy measurement because seagrass canopies can reduce near-bed velocity and shear, while sparse/flexible canopies can also generate complex turbulence and wave penetration. Therefore shoot density alone is not treated as a hydrodynamic proxy.

## Prior evidence and novelty boundary

The basic statement that seagrass canopies alter hydrodynamics is **not** the novel Tampa claim.

Relevant prior work already shows that:

- *Thalassia testudinum* canopies reduce near-bed velocity and shear relative to nearby unvegetated habitat;
- sparse and dense *Thalassia* canopies differ in turbulence and exchange;
- vertical canopy structure and secondary species can materially alter near-bed attenuation.

Key references include:

- Hansen & Reidenbach (2017), *Advances in Water Resources* 108:205–215, DOI 10.1016/j.advwatres.2017.08.001;
- Weitzman et al. (2015), *Limnology and Oceanography* 60:1855–1874, DOI 10.1002/lno.10121;
- Kaack, Fugate & Thomas (2024), *All Earth* 36, DOI 10.1080/27669645.2024.2419236; raw archive DOI 10.1594/PANGAEA.967585.

The Tampa advance is prospective coupling:

> does measured canopy-scale physical buffering explain which long-monitored meadows subsequently maintain versus lose quantitative *Thalassia* state?

A second Tampa-specific question is whether **community occupancy insurance is also functional insurance**. Existing exact-point results show that alternative seagrasses often persist when *Thalassia* is no longer recorded, but persistence of vegetation does not establish equivalent ecosystem engineering.

## Secondary community-functional-insurance hypothesis

At the velocity deployment footprint, record species-specific canopy composition in addition to total cover:

- *Thalassia testudinum*;
- *Halodule wrightii*;
- *Syringodium filiforme*;
- other macrophyte/algal structure if present.

Freeze one local quadrat/photographic protocol before deployment.

Secondary question:

> after total vegetated cover and canopy height are represented, does species composition still explain measured `attenuation_p90`?

This tests whether a shift from *Thalassia*-dominated to alternative-seagrass vegetation preserves, weakens, or changes hydrodynamic engineering.

Because existing literature shows that understory and multispecies structure can alter near-bed flow, no simple direction is assumed in advance. Report the composition coefficient and uncertainty two-sided.

This is a **secondary functional test**. It cannot rescue a null primary attenuation-to-future-persistence result.

## Sampling frame

Primary geography:

- Old Tampa Bay;
- Middle Tampa Bay;
- Lower Tampa Bay.

Target:

- 24 stable fixed-transect nodes;
- approximately 8 nodes per bay where feasible;
- minimum analyzable set: 18 nodes;
- minimum 5 analyzable nodes in each of the three bays.

Stratify before deployment across the observed baseline focal-frequency range. Do not select or drop nodes using the future response.

Where feasible, co-locate this design with the clonal-state sampling program, but keep the hydrodynamic and rhizome-TNC primary tests analytically separate.

## Paired velocity design

At each node deploy two time-synchronized velocity measurements.

### A. Inside-canopy / near-bed measurement

The sampling volume should represent flow experienced close to the meadow bed.

Target sampling-volume center:

- 0.05–0.10 m above the sediment surface.

The exact height must be fixed for the instrument family before the first outcome-bearing deployment and recorded for every node.

### B. Local ambient reference

Use a simultaneous reference measurement above the canopy at the same node.

Target:

- at least 0.10 m above the measured canopy top;
- sufficiently below the water surface to remain submerged during all retained records.

If the water column cannot physically accommodate both measurement volumes under the frozen geometry, that node is ineligible for the primary paired-attenuation analysis. Do not switch individual nodes post hoc to a different reference definition.

## Instrument requirements

The protocol is instrument-agnostic, but the selected current meter / velocimeter must:

- resolve horizontal velocity magnitude at the two required vertical positions;
- support simultaneous or precisely time-aligned records;
- be suitable for the shallow deployment depth;
- document blanking distance and sampling-volume geometry;
- retain enough raw or burst-level information for quality control;
- provide an orientation/heading record or an equivalent reproducible coordinate transformation.

A standard profiler with a blanking distance that prevents measurement within the required near-bed zone is not acceptable merely because it returns a current profile.

Freeze before first deployment:

- instrument model;
- sampling frequency and burst design;
- sensor heights;
- coordinate convention;
- velocity QC;
- deployment duration;
- valid-data threshold.

## Deployment duration

Target at least 21 consecutive days per node.

Primary eligibility requires at least 15 valid days after quality control. This is intended to include at least one spring-neap-scale tidal cycle while allowing some loss of data.

Deployments should be seasonally aligned as closely as practical across nodes.

## Baseline canopy measurements

At deployment, record new local physical/structural context:

- water depth;
- canopy height;
- local shoot density in a fixed quadrat protocol;
- representative leaf length;
- representative leaf width;
- percent total canopy cover or an equivalent frozen photographic estimate;
- species-specific cover / occupancy of *Thalassia*, *Halodule*, *Syringodium* and other structural macrophytes;
- sediment surface condition;
- sensor height above bed;
- reference height above canopy.

These are mechanism-support variables. They do not replace the primary measured attenuation metric.

Because flexible seagrass canopies can change posture with flow, shoot density alone must not be interpreted as physical drag or attenuation.

## Primary hydrodynamic metric

For each sensor, calculate horizontal speed

```text
U = sqrt(u^2 + v^2)
```

from synchronized valid observations.

Aggregate raw data to the frozen short-window mean used for current exposure. The aggregation window must be fixed before future biological response access.

Primary node-level ambient forcing:

> `ambient_p90` = 90th percentile of valid reference-layer horizontal current speed.

Primary node-level ecosystem-engineering metric:

> `attenuation_p90 = 1 - p90(U_inside) / p90(U_reference)`.

Interpretation:

- positive = high-current exposure is reduced inside the canopy;
- zero = no measured attenuation;
- negative = stronger p90 velocity inside the canopy than at the reference height.

Do not truncate negative attenuation values to zero.

## Physical mechanism gate

Before using future meadow change, report the paired physical result across nodes.

Primary physical question:

> Is `attenuation_p90` positive across the sampled meadow network?

Use a node-level uncertainty procedure frozen before analysis. Report the full node distribution even if the pooled direction is null.

Secondary physical analyses may examine canopy height, shoot density and cover as predictors of attenuation, but cannot redefine the primary attenuation metric after inspection.

## Future biological endpoint

Primary:

> next fixed-transect survey focal frequency minus baseline focal frequency.

Secondary:

- next Braun-Blanquet all-point index minus baseline;
- next blade length minus baseline where available;
- next shoot density minus baseline where available.

Binary re-recording / reappearance is not a primary mechanism endpoint and must not be called recovery.

## Primary prospective ecological model

```text
future_delta_frequency
  ~ baseline_frequency
  + ambient_p90
  + attenuation_p90
  + water_body
```

Directional hypothesis:

> higher measured `attenuation_p90` predicts a more positive / less negative future change in focal frequency after baseline state and ambient forcing are represented.

The attenuation coefficient is the primary hydrodynamic mechanism test.

A null primary attenuation result cannot be rescued by selecting another current percentile, sensor height, canopy trait, wave metric or subgroup after response access.

## Secondary event pathway

If a co-located turbidity or suspended-sediment sensor is available, predeclare a secondary pathway:

```text
ambient forcing
 -> within-canopy hydrodynamic attenuation
 -> near-bed turbidity / resuspension
 -> future quantitative state
```

This is supportive only unless separately powered and frozen. It must not be retrofitted as the primary explanation.

## Relationship to clonal buffering

The hydrodynamic and clonal hypotheses are intentionally separable.

- rhizome TNC asks whether internal biological reserve predicts persistence;
- paired flow asks whether the meadow modifies external physical stress.

If both are supported prospectively, a later preregistered model may test whether biological reserve and physical self-buffering are additive or interactive.

Do not construct that combined model after inspecting the two future outcomes.

## Interpretation

### Physical attenuation supported; future association supported

Consistent with a foundation-species self-facilitation mechanism in which the established canopy reduces local physical exposure and that measured reduction is associated with later quantitative persistence.

Still not proof of causality because meadow structure and unmeasured site quality may influence both attenuation and persistence.

### Physical attenuation supported; future association null

The canopy modifies flow, but measured hydrodynamic buffering does not explain the chosen future meadow-state endpoint under this design.

### Physical attenuation null

Do not claim hydrodynamic self-facilitation from current data. Do not search alternative percentiles or density thresholds to rescue the mechanism.

## Pre-outcome freeze

Before the future outcome is opened, freeze:

- final node list;
- exact instrument and sampling geometry;
- deployment dates/window;
- minimum valid duration;
- velocity QC;
- short-window aggregation;
- `ambient_p90` calculation;
- `attenuation_p90` calculation;
- baseline survey definition;
- future survey window;
- primary model;
- uncertainty procedure;
- missing-data/exclusion rules.


## Node-level design sensitivity

The future biological endpoint is one quantitative change per stable transect, so the effective inferential replication is the number of nodes, not the number of velocity observations collected within a node.

A frozen noncentral-F design audit (two-sided alpha = 0.05; 80% power; one focal attenuation coefficient with baseline frequency, ambient p90 and two bay indicators as controls) gives approximate minimum detectable partial effects:

- n = 24: |partial r| ≈ 0.573 (partial R² ≈ 0.328);
- n = 30: |partial r| ≈ 0.512 (partial R² ≈ 0.262);
- n = 36: |partial r| ≈ 0.467 (partial R² ≈ 0.218);
- n = 42: |partial r| ≈ 0.433 (partial R² ≈ 0.187).

Therefore the preferred target is **36 nodes** (nominally 12 per bay), with **30 nodes** as the minimum analyzable set. Within each bay, target four nodes from each pre-deployment baseline focal-frequency tertile. Repeated current measurements are still important because they reduce error in attenuation estimates, but they do not substitute for node replication.

Do not reduce the node target after inspecting the future response.


## Stage 0 — synchronized tri-bay screening

Do not use the asynchronous historical 2025 coverage as the sole baseline for deployment selection. In the current archive, 2025 contains 13 Old Tampa Bay nodes, 12 Middle Tampa Bay nodes and 9 Lower Tampa Bay nodes, whereas the stable tri-bay frame contains 19, 13 and 15 nodes respectively.

Before final velocity deployment selection, screen **all 47 tri-bay stable nodes** in one predeclared baseline window.

At each node record:

- focal *Thalassia* frequency using the frozen fixed-transect rule;
- water depth and tidal-stage metadata;
- canopy height;
- whether a *Thalassia* canopy patch adjacent to the permanent line can host the inside-canopy sensor;
- whether the paired above-canopy reference geometry can remain acceptably submerged;
- species-specific local canopy composition.

Primary eligibility requires a measurable focal canopy and feasible paired-sensor geometry. A zero-frequency node can remain useful descriptive state information but cannot enter the primary *Thalassia* canopy-attenuation analysis unless a focal canopy is independently present in the frozen deployment footprint.

Among eligible nodes, stratify within bay by the synchronized baseline focal-frequency distribution into low, middle and high thirds. Select nodes using a deterministic node-ID hash order fixed before deployment, not by investigator preference. Predeclare ordered alternates within each bay × state stratum.

This screening state is the baseline used in the future-change model.

## Two-gate mechanism logic

The hydrodynamic study does not treat a single regression coefficient as proof of ecosystem engineering. The mechanism claim is deliberately split into two prospective gates.

### Gate A — physical function

Before opening the future biological response, estimate `attenuation_p90` for every analyzable node and the equal-node mean across the deployed network.

> Gate A passes only if the frozen node-bootstrap 95% interval for the equal-node mean `attenuation_p90` lies entirely above zero.

Passing Gate A means that the sampled canopies measurably reduce high-end horizontal current relative to simultaneous above-canopy forcing. It does not yet show that the effect matters for meadow persistence.

### Gate B — future ecological relevance

After the future fixed-transect response is opened, fit the frozen primary model:

```text
future_delta_frequency
  ~ baseline_frequency
  + ambient_p90
  + attenuation_p90
  + water_body
```

Gate B tests the predeclared positive effect of `attenuation_p90`.

### Claim rule

- Gate A + Gate B: consistent with **biophysical self-buffering / self-facilitation**.
- Gate A only: canopy ecosystem engineering is present, but annual quantitative persistence has not been linked to it.
- Gate B only: do not call the association hydrodynamic self-buffering because the physical-function requirement failed.
- neither gate: reject this measured hydrodynamic-buffering mechanism under the frozen design.

Canopy height, shoot density and total vegetated cover form a secondary corrected family asking what structural properties generate attenuation. They cannot rescue either primary gate.