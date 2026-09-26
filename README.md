# Tampa — ecological memory and cryptic state degradation in Tampa Bay seagrass

This repository develops a biological analysis of long-term fixed-transect seagrass monitoring in Tampa Bay. It is intentionally separate from the EOG method-validation endpoint that motivated the question.

## Scientific mainline

The working question is now:

> **Can a foundation species remain recorded across fixed transects while its quantitative meadow state degrades or reorganizes?**

The analysis distinguishes four state dimensions for *Thalassia testudinum*:

1. recorded presence at a transect;
2. frequency occurrence across sampled meter marks;
3. Braun-Blanquet abundance/cover index;
4. plant condition variables (blade length and short-shoot density).

This matters because a stable presence map can hide thinning, reduced stature, reduced density, or community reorganization.

## Frozen source

The primary biological source is pinned to:

- repository: `tbep-tech/obis-example`
- commit: `6c567beff95ea04f0e397101befb49d5233ace8f`
- years: 1997–2025
- eligible transect visits: 1,497
- stable transect nodes: 71
- focal taxon: *Thalassia testudinum*

The scripts verify exact byte sizes and Git blob identities for Event, Occurrence and eMoF before analysis.

The reconstructed frequency-occurrence and Braun-Blanquet abundance definitions follow the TBEP/tbeptools convention: species observations divided by sampled placements, and species-specific Braun-Blanquet scores averaged over sampled placements.

## Current reproducible result

### 1. Strong temporal memory, but not a 3.5-year result

Annualization yields 1,480 transect-years and 1,176 consecutive-year transitions.

In strict walk-forward prediction on identical rows:

- space/time baseline mean log loss: **0.3312**
- + previous-year state: **0.1701**
- + exponentially weighted earlier history: **0.1395**
- best tested decay scale: **10 years**
- long-history model beats lag-1 in **14/22** target years

The earlier exploratory 3.5-year memory claim is superseded. The supported result is **strong immediate state dependence plus additional long-lived site-history information**; the memory horizon is not sharply identified.

### 2. Presence and quantitative condition decouple after 2016

For 2016–2025, within-transect models include node fixed effects and adjust for cyclic survey date and sampled-point count. Cluster bootstrap resamples transects.

**Old Tampa Bay**

- recorded detection slope: -0.0215 yr⁻¹, 95% bootstrap interval [-0.0582, 0]
- blade length: **-1.09 mm yr⁻¹**, [-1.69, -0.68]
- shoot density: **-38.3 shoots m⁻² yr⁻¹**, [-49.8, -21.9]

**Middle Tampa Bay**

- recorded detection: +0.0231 yr⁻¹, interval overlaps zero
- blade length: **-0.405 mm yr⁻¹**, [-0.908, -0.222]

**Lower Tampa Bay**

- recorded detection: -0.0053 yr⁻¹, interval includes zero
- focal frequency occurrence: **-0.0128 yr⁻¹**, [-0.0240, -0.00367]

**Boca Ciega Bay** does not show the same clear pattern.

The current biological interpretation is therefore:

> **A stable or recovering binary occurrence state can coexist with deterioration of spatial occupancy within a transect, plant stature, or shoot density.**

This is treated as a candidate **cryptic degradation / ecological-state decoupling** result, not yet as a climate-causal result.

### 3. Community reorganization is bay-specific

The same fixed-transect panel was expanded to *Halodule wrightii*, *Syringodium filiforme* and *Ruppia maritima*.

**Lower Tampa Bay** shows the clearest compositional reorganization from 2016–2025:

- *Thalassia* frequency: **-0.0126 yr⁻¹**, bootstrap interval [-0.0247, -0.00366]
- *Thalassia* Braun-Blanquet index: **-0.0412 yr⁻¹**, [-0.0785, -0.00028]
- *Halodule* frequency: **+0.0108 yr⁻¹**, [+0.000045, +0.0180]
- *Syringodium* frequency: **-0.00526 yr⁻¹**, [-0.0126, -0.00024]

This is consistent with a shift toward more frequent *Halodule* while *Thalassia* and *Syringodium* decline quantitatively. It does **not** by itself demonstrate competition or a replacement mechanism.

Old Tampa Bay shows a different degradation mode: the stronger signal is declining *Thalassia* blade length and shoot density rather than a monotone alternative-species replacement. Middle Tampa Bay likewise shows declining *Thalassia* blade length, while *Thalassia* and *Syringodium* year-to-year frequency changes tend to move together rather than compensate.

The stronger cross-bay result is therefore **heterogeneity in degradation mode**, not one bay-wide decline process.

### 4. The 2016 loss / 2017 return pulse is not the main result

Five transects lost recorded *Thalassia* in 2016 and all five recorded it again in 2017. However, this pulse is protocol-sensitive:

- 24/47 eligible 2016 visits use 25 December as the parent date;
- four of the five pulse transects use that date;
- sampled-point counts changed strongly at several pulse transects;
- the pinned OBIS conversion uses the **minimum** date within a multi-day transect ID, while current `tbeptools::read_formtransect()` uses the **maximum** date because some transects are sampled over more than one day.

Therefore the pulse remains exploratory and is **not** interpreted as confirmed extinction/recolonization or a discrete environmental disturbance.

Where quantitative data are available, the 2017 return was often incomplete: across the five pulse nodes, median 2017 frequency was about 55% of its 2015 value and median Braun-Blanquet index about 26%.

## Water-quality screen

A separate response-independent screen uses the pinned TBEP/EPCHC long-term water-quality archive. It summarizes salinity, temperature, chlorophyll, total nitrogen, Secchi depth and turbidity by bay segment/year.

No single 2016 annual anomaly explains the protocol-sensitive pulse. A second conservative coupling screen averages ecological state change to the same **bay-segment × year** scale as the environmental exposure, avoiding pseudo-replication of one annual water-quality value across many transects. Across declared post-2016 *Thalassia*, *Halodule* and *Syringodium* state-change outcomes, **0 associations survive FDR < 0.05 and 0 fall in 0.05–0.10**.

This is a useful negative result: **no simple annual water-quality variable currently explains the post-2016 state changes at this aggregation scale**. It does not reject temperature, salinity, hydrologic pulses or other mechanisms operating at finer temporal or spatial scales, and it does not support climate-causal attribution.

## Reproduce

```bash
python -m pip install -r requirements.txt
python analysis/01_transition_memory.py --out results/generated
python analysis/02_water_quality_screen.py --out results/generated
python analysis/03_quantitative_state.py --out results/generated
python analysis/04_state_change_validation.py --out results/generated
python analysis/05_community_compensation.py --out results/generated
python analysis/06_source_protocol_audit.py --out results/generated
python analysis/07_environmental_coupling.py --input results/generated --out results/generated
```

CI reruns all seven analyses from pinned public sources.

Canonical current boundary: `results/current_validation_v2.json`.

`results/initial_validation.json` is retained as historical provenance and contains superseded early exploratory wording.

## Claim boundary

Supported now:

- annual recorded *Thalassia* state has strong temporal memory;
- earlier site history adds information beyond previous-year state;
- multiple quantitative state dimensions can trend differently from binary detection;
- Old Tampa Bay, Middle Tampa Bay and Lower Tampa Bay show different forms of state decoupling after 2016;
- Lower Tampa Bay shows a reproducible compositional signal: declining *Thalassia* and *Syringodium* with increasing *Halodule* frequency;
- no declared simple annual water-quality coupling survives the post-2016 multiplicity-controlled segment-year screen.

Not supported now:

- demographic extinction/recolonization from recorded absence/presence;
- a causal temperature, salinity or nutrient mechanism;
- a confirmed ecological interpretation of the 2016/2017 pulse;
- a universal 10-year biological memory constant;
- equivalence between fixed-transect condition and bay-wide mapped acreage.

## Next scientific gate

The broad annual environmental screen is now closed as a negative result. The next ecological gate should test **mechanism at the temporal scale on which stress actually acts**, without reviving the protocol-sensitive 2016 pulse as a primary endpoint:

1. build seasonal/event-scale exposure histories where defensible (heat, low salinity, turbidity/hydrologic pulses);
2. test whether those exposures predict **which degradation mode** a transect enters: condition loss, within-transect frequency loss, or community reorganization;
3. preserve bay-segment heterogeneity rather than forcing a single Tampa-wide slope or cause.

Until that gate passes, the manuscript-level ecological claim is state decoupling and spatially heterogeneous degradation, not a climate mechanism.
