# Tampa ecological mechanism boundary v2

## Purpose

This file records what the current Tampa dataset supports, which retrospective mechanism explanations have already been tested, and what evidence is required before another mechanism claim is allowed.

The purpose is to prevent repeated rescue attempts on the same annual observation-state table.

## Supported ecological pattern

The robust ecological center is **state decoupling under persistent occurrence**.

- stable transect identity strongly structures recorded detection, focal frequency and Braun–Blanquet abundance;
- blade length and shoot density are substantially more temporally labile;
- Old, Middle and Lower Tampa Bay express different degradation modes;
- Lower Tampa Bay shows compositional reorganization with declining *Thalassia* and *Syringodium* and increasing *Halodule* frequency;
- local quantitative state contains internal out-of-time information about next-year recorded-state loss;
- pre-existing mixed-species exact points are less likely to become completely seagrass-bare after *Thalassia* loss.

These are ecological state results. They do not by themselves identify the causal mechanism.

## Observation-state terminology

A point or transect that is unrecorded and later recorded again is described as **re-recorded**, **reappearing in the observation record**, or **recorded-state return** where a compact variable label is unavoidable.

Do **not** call binary reappearance:

- ecological recovery;
- demographic recovery;
- recolonization;
- clonal recovery;
- physiological recovery.

Legacy analysis filenames and schema names containing `recovery` remain unchanged for provenance and reproducibility. Their names are not evidence that recovery occurred.

## Mechanism / alternative-explanation ledger

| Candidate explanation | Test | Result | Interpretation boundary |
|---|---|---|---|
| Long biological memory | Stable-node reference saturation | Older-history support disappears for all tested state variables after adding node identity | History partly carries persistent site heterogeneity; no clean long-memory claim |
| Static regional accessibility / EOG geometry | Frozen EOG Tampa endpoint + geometry audit | Predictively adverse; all worlds survived and Layer B became a static node signature | Static geometry is not the changing annual biological state |
| Annually refreshed neighborhood accessibility | Four frozen EOG radii | No added mean heldout value | Simple neighbor propagation does not explain annual response |
| Shared bay-segment state | Leave-one-node-out previous-year segment mean | Unsupported for frequency and Braun–Blanquet | No simple one-year segment synchrony beyond own state |
| Local neighborhood deviation | Segment-residual neighborhood state at four radii | 0/4 radii supported | No simple local spatial propagation at tested scales |
| Simple thresholding / first-order hidden-state simulations | Three frozen known-truth families | All fail global sufficiency rules | Do not infer a mechanism from coarse-state memory |
| Depth + sediment site template | Response-independent physical preflight + held-out-node test | 0/3 primary occurrence/abundance outcomes supported | Stable node effect is not reducible to simple bathymetry/sediment class |
| Bulk benthic light | 6-month Secchi-derived Kd × visit depth, strong reference | Blade length and shoot density unsupported; 3-month sensitivity also null | Does not reject light biology; rejects this coarse segment-light proxy |
| Simple annual/seasonal temperature or salinity | Annual and frozen 3/6-month hot/fresh screens | No multiplicity-controlled association | Do not retune windows |
| Published 30 °C / 25 ppt compound stress | Exact Beck et al. daily-GAM stress artifact; joint run tested beyond marginal hot and fresh runs | Blade length and shoot density unsupported | Joint threshold duration does not rescue the climate-stress mechanism |
| Simple condition → thinning cascade | Source blade length + shoot density added beyond current frequency/BB and stable node identity in strict walk-forward prediction | Primary frequency and secondary Braun–Blanquet targets both unsupported | Faster condition dynamics do not establish that plant-condition decline is a one-year precursor of thinning |
| Qualitative annual epiphyte burden | Within-transect next-year retention model, node/year FE and baseline BB/depth/season controls | Primary coefficient positive (+0.118, 95% bootstrap CI 0.019 to 0.223); target-2016 sensitivity overlaps zero | Reject a simple annual epiphyte-stress reading; qualitative load may mark mature canopy/microsite state. Any shading mechanism requires direct biomass/optical measurement |
| TBOFS near-bottom current as meadow exposure | Response-blind grid mapping + physical point-depth relevance audit | All-network distance gate failed; tri-bay grid proximity was good but model bathymetry was systematically too deep for literal shallow-meadow interpretation | Retain TBOFS as regional context; do not use model bottom sigma velocity as the primary canopy-scale predictor |
| Exact-point reappearance decomposition | Multiple post-hoc observation-state audits | Useful state-history and community-continuity associations, but still observational and increasingly reference-sensitive | Do not promote another annual-state decomposition into a mechanism claim |

## Current ecological model

The current data favor **multiple partially independent state axes**, not one proven serial degradation cascade.

```text
                 persistent local meadow template
                         /          \
                        /            \
        occupancy / abundance      plant condition
        (strong site anchoring)    (more temporally labile)
                 \                  /
                  \                /
                   community context
                        |
              coarse recorded state
```

Important implications:

- plant condition can change while occurrence/abundance remain comparatively stable;
- within-meadow abundance can decline without a demonstrated preceding blade/shoot signal;
- community composition can change while any-seagrass occupancy is retained;
- multiple state axes can converge on recorded-state instability without having a single demonstrated order.

The current annual table does **not** identify the persistent local template or short-timescale stress.

## Hypothesis triage after the current mechanism tests

### 1. Simple condition -> thinning -> loss cascade: **not supported**

The frozen cross-lag test asked whether source-year blade length and shoot density improve strict year-ahead prediction of next-year focal frequency or Braun-Blanquet state beyond current quantitative state and stable node identity.

For focal frequency, the condition model was worse on average than the baseline (mean MAE 0.06862 versus 0.06691), winning 6 of 17 scored target years. Braun-Blanquet showed the same direction of failure.

Therefore:

- faster plant-condition dynamics are real descriptive axes;
- they are **not** validated as a one-year leading stage of thinning;
- the manuscript must not present one universal serial degradation cascade.

### 2. Clonal / below-ground buffering: **plausible but unresolved**

Two pieces of retrospective evidence are relevant but insufficient.

- Formal older-history support disappears after stable node identity is added, so generic long-memory inference is reference-sensitive.
- Exact-point focal *Thalassia* history can retain information beyond generic vegetated-habitat history, but the bare-loss subgroup and history-by-continuity results do not support a simple autonomous residual-rhizome story.

Therefore the only decisive next test is a genuinely new below-ground state measured before a future quantitative outcome. Rhizome TNC remains the frozen primary prospective predictor.

### 3. Successional reset / pioneer replacement: **composition shift supported; mechanism not supported**

Lower Tampa Bay shows a real directional community reorganization over 2016–2025:

- *Thalassia* frequency declines;
- *Thalassia* Braun-Blanquet state declines;
- *Syringodium* declines;
- *Halodule* frequency increases.

That is sufficient for **community reorganization**.

It is not sufficient for a successional-reset or pioneer-replacement mechanism. Exact-point analyses show that much alternative-species occupancy after focal loss reflects persistence of species already present before focal loss; among focal-loss points remaining seagrass-occupied, 71.2% retained at least one pre-existing alternative species. Thus post-loss *Halodule* cannot be assumed to be new colonization.

### 4. Canopy hydrodynamic self-buffering: **open; direct prospective design frozen**

The annual table cannot identify a critical density threshold without post-hoc retuning, and threshold rescue on the same table is prohibited.

NOAA TBOFS was tested as a genuinely independent physical source before biological linkage. The result was useful but negative for the intended meadow-scale interpretation.

- all 71 stable nodes could be mapped to valid current-support cells, but two Boca Ciega Bay nodes exceeded the frozen 2-km maximum-distance rule;
- Old + Middle + Lower Tampa Bay were geometrically well covered (47/47 within 2 km);
- however, physical point depths in that core had a median of about 0.90 m while mapped TBOFS bathymetry had a median of 2.00 m;
- TBOFS bathymetry was deeper at all 47 core nodes and 40/47 mapped cells were exactly 2.0 m;
- the node-level depth correlation was weak (about 0.16).

Therefore model bottom-sigma velocity is not accepted as literal canopy/near-bed exposure for these shallow meadows.

The hydrodynamic hypothesis is retained in a stronger form using **direct paired velocity measurements**:

```text
attenuation_p90
  = 1 - p90(U_inside_canopy) / p90(U_above_canopy)
```

followed prospectively by:

```text
future_delta_frequency
  ~ baseline_frequency
  + ambient_p90
  + attenuation_p90
  + water_body
```

The key prediction is that stronger measured canopy attenuation is associated with less subsequent quantitative decline. This tests ecosystem engineering directly rather than assuming shoot density or model current equals physical buffering.

The frozen design is in `docs/DIRECT_HYDRODYNAMIC_SAMPLING_PROTOCOL_V1.md` and `results/direct_hydrodynamic_prospective_v1_contract.json`.

### 5. Qualitative epiphyte burden as annual stress: **not supported**

The existing qualitative epiphyte-density layer was evaluated separately because epiphytes are a plausible leaf-scale shading mechanism that is not represented by bulk Secchi × depth.

The adjusted within-transect primary coefficient was **positive**, not negative (+0.118; 95% node-bootstrap interval 0.019 to 0.223; 4,189 complete transitions across 49 nodes). Restoring the protocol-sensitive target year 2016 weakened the coefficient to +0.085 with an interval spanning zero (-0.012 to 0.193).

Therefore:

- the current ordinal `Clean / Light / Moderate / Heavy` field does **not** support a simple annual epiphyte-stress interpretation;
- the positive direction must not be described as a beneficial epiphyte effect;
- qualitative epiphyte load may instead track mature/long-lived leaves, persistent favorable meadow state, hydrodynamic environment, grazing regime or another canopy property;
- no further category/type/lag mining is authorized from this field;
- an epiphyte-light mechanism remains open only through new direct measurements such as epiphyte biomass plus leaf/canopy optical attenuation.

### 6. Event-scale physiological debt: **open, but only at a new temporal resolution**

Annual water quality, frozen 3/6-month hot/fresh summaries, and the published 30 C / 25 ppt compound-stress test did not support a common mechanism.

This rules against the tested coarse summaries, not against short stress pulses. The remaining version of the hypothesis requires high-frequency node-scale temperature, salinity and/or PAR measured before a future response.

### Current mechanistic ranking

The data therefore favor neither a single serial cascade nor a demonstrated long-memory mechanism.

The strongest unresolved mechanism questions are now:

1. does below-ground reserve explain persistence beyond current above-ground state?
2. does short-timescale physical stress explain future quantitative change?
3. does directly measured canopy attenuation buffer local hydrodynamic exposure and predict future quantitative persistence?

The existing qualitative epiphyte layer is no longer a leading mechanism candidate; only a genuinely new biomass/optical epiphyte layer could reopen that pathway.

All three require a new measurement layer.

## Community-continuity results are state ecology, not mechanism identification

The exact-point community analyses show that pre-existing mixed-species points are more likely to remain seagrass-occupied after focal *Thalassia* loss and that many later alternative-species records represent persistence of species already present before focal loss.

Later re-recording of *Thalassia* is an observation-state event. It is not a recovery endpoint.

These exact-point results motivate new measurement hypotheses such as below-ground persistence and microsite physical quality, but further decomposition of the same annual observation record is not the preferred mechanism path.

## New-measurement priority

The mechanism program now follows `docs/NEXT_MEASUREMENT_LAYER_PROGRAM_V1.md`.

Priority order:

1. **Below-ground reserve / clonal state**
2. **Node-scale high-frequency temperature, salinity and PAR**
3. **Hydrodynamic exposure / residence time**
4. **Canopy / epiphyte light microenvironment**
5. **Acute disturbance / disease**

The open prospective Old Tampa Bay continuous-temperature branch is allowed because it freezes a future 2027 biological endpoint before that response exists.

## Scientific stopping rule

Do **not** add another retrospective decomposition of the current annual/exact-point biological archive to improve the mechanism story.

This includes another:

- binary reappearance / loss / reloss subgroup;
- local-history split;
- lag window;
- threshold;
- state-transition subclass;
- richness subgroup;
- temperature or salinity threshold;
- distance radius;
- generic connectivity index;
- hidden-state simulation family;
- depth/sediment transformation;
- bulk-light formula.

A new mechanism branch is allowed only when it introduces at least one of:

1. a genuinely new biological measurement state;
2. a substantially finer temporal or spatial physical measurement layer;
3. a future response frozen before access;
4. a response-unopened external dataset under a frozen schema.

## Manuscript consequence

The paper should lead with:

> **Persistent occurrence can conceal spatially heterogeneous quantitative degradation in a foundation species.**

Mechanism remains secondary and deliberately unresolved.

Observation-state reappearance is not ecological recovery.

The next mechanism advance should come from new measurement, not further mining of the same annual state table.
