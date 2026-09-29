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
