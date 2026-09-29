# Tampa dual-buffer hypothesis v1

## Ecological question

The current Tampa results do not support one universal annual sequence from plant condition to thinning to disappearance. They instead leave a more mechanistic question:

> **Why can a long-lived foundation-species meadow remain locally persistent despite changing above-ground state?**

The prospective program separates two forms of buffering.

### Internal buffer — stored biological capital

*Thalassia testudinum* stores non-structural carbohydrate in rhizomes. The frozen internal-state predictor is rhizome total non-structural carbohydrate (TNC).

Prediction:

> at similar present above-ground state, higher below-ground reserve predicts a less negative future change in focal frequency.

### External buffer — ecosystem engineering

A seagrass canopy can modify the physical environment it experiences. The frozen external-state predictor is directly measured high-flow attenuation:

```text
attenuation_p90
  = 1 - p90(U_inside_canopy) / p90(U_above_canopy)
```

Prediction:

> after ambient flow and present meadow state are represented, stronger measured attenuation predicts a less negative future change in focal frequency.

## Why the combination matters

The two mechanisms are ecologically different.

- TNC is **stored internal capital** accumulated before a stress event.
- flow attenuation is **generated external buffering** produced by the existing meadow structure.

Both could create persistence lag, but they imply different dynamics and different restoration strategies.

A meadow with high TNC but weak physical engineering could persist through internal reserve use. A meadow with strong attenuation but low reserve could remain protected by its engineered local environment. A meadow with both has two independent buffers. A meadow with neither should be most vulnerable under the dual-buffer hypothesis.

The v1 study does **not** test that four-cell interaction directly; node replication is too limited for a reliable TNC × attenuation rescue analysis. Instead it asks whether the two measured buffers retain independent prospective information in one model.

## Joint prospective model

Use the same synchronized baseline and same future fixed-transect outcome.

```text
future_delta_frequency
  ~ baseline_frequency
  + baseline_BraunBlanquet
  + ambient_p90
  + TNC_z
  + attenuation_p90_z
  + water_body
```

The two predeclared directional focal coefficients are TNC and attenuation. Apply Holm correction across these two tests.

Interpretation:

- **both positive after correction** → consistent with dual internal + external buffering;
- **TNC only** → internal-reserve buffering is the supported measured mechanism;
- **attenuation only** → external physical buffering is supported, provided the independent physical attenuation Gate A also passed;
- **neither** → neither measured buffer explains future quantitative persistence under this design.

## Novelty boundary

The component ideas are not claimed as new.

Previous seagrass work already establishes carbohydrate storage/mobilization and hydrodynamic ecosystem engineering, and coupled vegetation-hydrodynamic models already contain both biological storage and physical feedback.

The Tampa contribution would be the **prospective field discrimination**:

> measure internal reserve and external physical buffering at the same long-monitored *Thalassia* nodes before the response exists, then ask whether either or both explain the same subsequent quantitative meadow trajectory.

That is a stronger ecological claim than “presence can hide decline” and more testable than a generic ecological-memory label.

## Sampling consequence

Prefer the same 36 nodes for TNC and velocity work, after synchronized screening of all 47 Old + Middle + Lower Tampa stable nodes. Minimum complete joint sample is 30 nodes.

Three cores within a node and repeated velocity measurements improve the precision of the two buffer measurements, but the node remains the independent unit for the future ecological outcome.

## What this does not claim

- binary reappearance is not recovery;
- TNC is not automatically causal clonal memory;
- attenuation is not automatically self-facilitation unless direct physical Gate A passes;
- a marginal correlation for each buffer is not enough for a dual-buffer claim;
- no TNC × attenuation interaction is permitted as a v1 rescue analysis.

## Community-level extension: occupancy insurance versus functional insurance

Tampa already shows that many exact points remain occupied by another seagrass after *Thalassia* is no longer recorded, and Lower Tampa Bay shows directional compositional reorganization. That is **occupancy insurance**, not automatically functional insurance.

The direct-velocity layer creates a new community-ecology test:

> when *Thalassia* dominance changes, does the remaining multispecies canopy preserve the physical buffering function of the meadow?

Use the frozen secondary physical model from the direct-hydrodynamic contract:

```text
attenuation_p90
  ~ total_vegetated_cover
  + canopy_height
  + thalassia_fraction
  + water_body
```

This separates **vegetation remains** from **the same ecosystem-engineering function remains**.

- a composition effect means community reorganization changes hydrodynamic function even at similar total cover/height;
- no composition effect is consistent with hydrodynamic redundancy only over the measured structural range;
- neither result proves that alternative species are equivalent across other functions such as habitat, carbon storage or food-web support.

This secondary physical analysis cannot rescue a null future-persistence result, but it links the observed Tampa community reorganization to a concrete ecosystem function.