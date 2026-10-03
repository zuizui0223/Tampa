# Tampa integrated prospective field campaign v1

## Purpose

This document coordinates the already-frozen prospective Tampa mechanism tests so they can share field visits and TNC cores **without changing their scientific contracts**.

The integrated campaign does not create a new pooled mechanism model. The authoritative primary tests remain separate:

1. four-bay rhizome TNC -> future quantitative *Thalassia* change;
2. three-bay event-scale hot-fresh exposure -> short-term TNC change;
3. three-bay within-canopy DLI -> short-term TNC change;
4. direct hydrodynamic buffering under its own separate field design.

The orchestration contract is:

- `results/integrated_field_campaign_v1_contract.json`
- resource freeze: `field/integrated_campaign_resource_freeze.json`

## Core shared calendar

### Late-July pre-exposure round — core three bays only

Frozen environmental window begins **July 24**.

For final eligible event and/or optical nodes in Old, Middle and Lower Tampa Bay:

- collect pre-exposure TNC within 3 days of logger deployment;
- deploy temperature/salinity systems;
- deploy within-canopy PAR systems;
- deploy paired above-canopy PAR only on the predeclared optical-attribution subset;
- use the already frozen TNC tissue, HPLC, spatial-anchor and destructive-sampling rules.

The pre-TNC round is not the authoritative four-bay TNC baseline. It exists to measure reserve change over the 42-day exposure interval.

### July 24–September 3 exposure window

Event and optical primary exposures share the same biological interval.

Event-stress remains:

```text
joint_hot_fresh_hours_30_25
```

with all existing variation/identifiability rules.

Optical stress remains:

```text
mean_daily_within_canopy_dli
```

with its daylight-specific DLI QC.

Sharing dates does not authorize adding PAR to the hot-fresh primary model or temperature/salinity to the optical primary model.

### Early-September post-exposure / authoritative baseline round

Around the frozen **September 3** endpoint:

For core-three nodes:

- retrieve event/optical loggers;
- collect post-exposure TNC within 3 days of retrieval;
- maintain the frozen **39–45 day** pre/post TNC interval;
- use this valid post-exposure TNC as the preferred authoritative v2 baseline TNC measurement.

For Boca Ciega Bay:

- collect one authoritative baseline TNC round during the same late-summer baseline campaign;
- use the same tissue, HPLC, q25/q50/q75, nutrient and genet-diagnostic rules;
- do **not** add a sham pre-coring round solely to imitate the event-study disturbance.

Across all four bays:

- pair the quantitative fixed-transect baseline survey to baseline TNC within +/-14 days, preferably on the same node visit;
- complete authoritative v2 baseline TNC collection within one <=28-day campaign.

The next prespecified fixed-transect survey supplies the future v2 response.

## Shared TNC rounds

The design minimizes destructive sampling.

Let:

- (E) = final event-stress node set;
- (O) = final optical-primary node set;
- (T) = final authoritative four-bay TNC node set.

Then:

- nodes in (E \cup O): 3 pre + 3 post cores;
- nodes in (T \setminus (E \cup O)): 3 baseline cores only.

Minimum planned core count before replacements:

```text
6 * n(E union O) + 3 * n(T outside E union O)
```

Under the current full planning frame, if event and optical both use the same 33 core-three nodes and v2 uses all 41 four-bay nodes:

```text
33 * 6 + 8 * 3 = 222 outcome-bearing cores
```

The post round in the core three bays is already the v2 baseline. **A third redundant TNC round is prohibited.**

## Destructive-sampling asymmetry

The core three bays receive an earlier pre-exposure coring round; Boca Ciega does not.

Do not create unnecessary Boca Ciega damage just to make the field history visually symmetric.

Instead:

- record the prior pre-coring date and offsets for every core-three baseline node;
- use the frozen distinct pre/post offset geometry and cumulative footprint limit;
- before deployment, freeze a numeric minimum pre/post core-center separation and a numeric maximum cumulative disturbed area per node across all attempted pre/post cores;
- require the frozen minimum center separation to be at least one core diameter so pre/post core footprints cannot physically overlap;
- keep all coring outside the permanent monitoring footprint;
- retain the future point-level disturbance sensitivity around TNC anchor neighborhoods;
- keep the authoritative water-body factor.

Because prior pre-coring is geographically structured, it cannot be independently identified by adding a post-hoc "prior coring" covariate. Cross-bay mean differences therefore cannot be interpreted as proof of either coring effects or ecological effects. The primary TNC coefficient remains the predeclared within-four-bay reserve-state association conditional on baseline state and water body.

If visible pre-coring disturbance compromises a planned post-TNC anchor or monitoring neighborhood, apply the predeclared intervention/QC rule rather than silently retaining the point.

## Resource feasibility is a scientific gate

The current repository freezes statistical sample sizes but does not yet contain an instrument inventory.

Before the first outcome-bearing core/logger deployment, complete:

`field/integrated_campaign_resource_freeze.json`

### Event-stress primary

Confirmatory minimum remains:

- >=30 analyzable nodes;
- >=8 in each of Old, Middle and Lower Tampa Bay.

Every selected node needs a complete synchronized temperature+salinity system over the same calendar window.

Sequentially rotating a smaller logger pool across different weather windows **cannot** manufacture confirmatory n.

### Optical primary

Confirmatory minimum remains:

- >=30 analyzable nodes;
- >=8 in each core bay.

Every selected node needs a valid within-canopy PAR system over the same common interval.

For canopy optical attribution:

- target 18 paired above-canopy references;
- minimum 12;
- >=3 per core bay.

Under the full planning target, this corresponds to 33 within-canopy PAR sampling volumes plus 18 simultaneous above-canopy reference volumes. These are **sampling volumes/node systems**, not necessarily 51 separate logger boxes if validated multi-channel hardware can record synchronized volumes.

### TNC v2 primary

Authoritative four-bay gate remains:

- planning frame about 41 nodes;
- >=36 analyzable nodes;
- >=6 per bay.

Event or optical hardware shortage cannot change the v2 geography or TNC gate. TNC-only baseline nodes may remain valid if they satisfy the v2 field/assay rules.

### Hydrodynamic programme

Hydrodynamic measurement is not a prerequisite for this integrated campaign.

Run it in parallel only if it has independent instrument and crew capacity. It must not reduce compliance with the TNC, event or optical programmes.

Otherwise schedule direct velocity work separately under its existing 21-day, bare-control and counterfactual rules.

## Capacity failure rule

The four-bay TNC v2 primary is protected first.

Before the first outcome-bearing pre-TNC core, freeze each optional forcing module as either:

- **confirmatory**, or
- **disabled**.

If response-independent inventory/logistics cannot meet the full frozen event or optical confirmatory frame:

> disable that outcome-bearing module for this campaign.

A disabled module may still run response-independent sensor, calibration or geometry pilots, but it does **not** justify an extra pre-exposure TNC round or an underpowered biological mechanism test.

Do not:

- rotate instruments into non-overlapping weather windows and combine them as if simultaneous;
- run a small outcome-bearing forcing pilot that adds destructive pre-coring merely because full confirmatory capacity is unavailable;
- drop a difficult bay after exposure is seen;
- change July 24–September 3;
- retune hot/fresh thresholds;
- add a third TNC round;
- sacrifice the authoritative four-bay TNC design to rescue another mechanism.

Paired above-canopy PAR is different: it is a **secondary optical-attribution diagnostic**. If the 12-total / 3-per-bay reference subset cannot be met, disable that attribution layer only. The within-canopy DLI primary may remain confirmatory if its own 30-total / 8-per-bay and QC gates pass.

## Fail-closed field readiness

The integrated resource freeze is not just an inventory sheet.

Before any outcome-bearing collection, the readiness audit must verify:

- the separate authoritative TNC-v2 precollection freeze is complete;
- the final four-bay TNC node registry meets >=36 total and >=6 per bay;
- the authoritative TNC baseline dates fit one <=28-day campaign;
- every baseline fixed-transect survey lies within +/-14 days of its TNC baseline;
- TNC-v2 primary analysis and node-level uncertainty code are frozen;
- confirmatory event/optical modules have enough simultaneous node systems and their primary analysis code frozen;
- logger deployment/retrieval calendars preserve the frozen July 24-September 3 design and >=35-day common overlap;
- pre/post TNC visits are within 3 days of deployment/retrieval and 39-45 days apart;
- core-three post-TNC dates are the authoritative baseline TNC dates, so no third TNC round is silently introduced;
- preservation capacity covers the full planned core count;
- the frozen primary HPLC workflow has assay capacity for at least the same planned core count.

A complete but insufficient freeze is a **STOP**, not a reason to reinterpret the study after fieldwork.

## Integrated forcing-family inference

Event-stress and optical DLI remain separate mechanism contracts.

If both are confirmatory and estimable in the same campaign:

- retain each contract's own frozen two-sided 95% interval and standalone support status;
- for any paper-level statement that **measured environmental forcing predicts reserve change**, treat the two forcing primaries as one family;
- use Bonferroni-adjusted **two-sided 97.5% intervals** from the same frozen node-level resampling procedure for that family-level claim;
- report the pre-response node-level correlation between hot-fresh exposure and within-canopy DLI;
- do not rank the two mechanisms by p-value, CI width or standardized coefficient;
- if both support individually, do not call them statistically independent effects without a separately frozen joint model.

This family-level rule does not change either individual contract. It controls the broader integrated-campaign claim.

## What integration buys biologically

This design aligns several measurements on the same reserve trajectory.

For the core three bays:

```text
pre-TNC
   |
42-day measured forcing
   |-- hot-fresh exposure
   |-- actual within-canopy light
   v
post-TNC = authoritative baseline reserve
   |
future quantitative Thalassia state
```

This allows three distinct questions without post-hoc predictor fishing:

1. does hot-fresh event exposure deplete reserve?
2. does actual light predict reserve maintenance?
3. does the resulting reserve state predict future meadow persistence?

Hydrodynamic buffering and community functional insurance remain separate organizational-level tests.

Even if all links support the proposed directions, the design remains observational and does not become formal mediation or experimental causal proof.
