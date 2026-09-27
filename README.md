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

### 2b. External NPS panel reproduces binary–quantitative state decoupling

A separate post-hoc ecological analysis uses the National Park Service Northeast Coastal and Barrier Network Tier-3 *Zostera marina* panel (2003–2025). This analysis is explicitly **not** a rescue or rerun of the frozen external early-warning endpoint: that endpoint terminated non-estimable because it contained zero recorded-loss transitions.

Across the NPS panel:

- **240/240** eligible annual transect units retained recorded *Zostera* presence;
- focal frequency was **1.0 in every eligible unit**;
- quantitative cover nevertheless ranged from **0 to 99.2%**;
- the median within-transect cover range was **58.1 percentage points**;
- **11/15** repeatedly sampled transects had negative cover slopes;
- pooled within-transect cover slope was **−1.52 percentage points yr⁻¹**;
- node-bootstrap 95% interval: **−2.45 to −0.60 percentage points yr⁻¹**.

The direction is spatially heterogeneous: Duck Harbor Beach, Fire Island and Tingles Island declined; Moriches Bay increased; Pleasant Bay was uncertain. The useful cross-system result is therefore not a universal decline rate. It is:

> **A saturated binary presence state can coexist with large and directionally heterogeneous quantitative change in a foundation seagrass.**

This reproduces the **state-decoupling** pattern in a different species (*Zostera marina*) and monitoring network. Because the response had already been opened by the frozen NPS estimability test, this is post-hoc external ecological replication, not untouched predictive confirmation.

Sensitivity analysis supports that interpretation:

- removing each monitored location in turn leaves the pooled within-transect cover slope negative (**−1.82 to −0.90 percentage points yr⁻¹**);
- equal-node mean slope is **−0.70** and median node slope **−0.51 percentage points yr⁻¹**;
- **12/15** repeated transects decline from their first to last eligible year;
- three 2022 Tingles Island identities (`A::MD12.2`, `B::MD12.2`, `C::MD12.2`) are reverse-ID candidates relative to the long-term IDs. They are **not repaired**; because each occurs in only one year, they do not enter repeated-transect slopes.

Thus the external result is not driven by a single declining location or by silently repairing source identity. Moriches Bay remains a genuine positive-trend counterexample, so the claim is **state decoupling with spatially heterogeneous quantitative trajectories**, not universal decline.



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

### 4. Quantitative degradation predicts next-year recorded loss

The state-decoupling result was then converted into a forward-looking ecological question:

> **Among transects where *Thalassia* is still recorded, does quantitative meadow condition contain information about whether it will be unrecorded the following year?**

The endpoint is strictly **next-year recorded loss**, not demographic extinction. Across 688 consecutive source-positive transitions, 24 were followed by recorded loss and 664 by recorded persistence.

Before a recorded loss, source-year state was already much weaker:

- frequency median: **0.0627** before loss vs **0.302** before persistence;
- Braun-Blanquet all-point index median: **0.0495** vs **0.713**.

A strict walk-forward comparison trained only on earlier target years. The baseline used year, geography, bay segment, cyclic survey timing and sampled-point effort. The augmented model added only source-year *Thalassia* frequency and Braun-Blanquet state.

Across 23 scored target years (2003–2025):

- baseline macro log loss: **0.1556**
- + quantitative state: **0.1465**
- quantitative arm better in **17/23** years
- paired one-sided Wilcoxon: **p = 0.00271**
- pooled AUC: **0.636 → 0.739**

Crucially, target year **2016 is retained in the primary result and is strongly adverse** for the quantitative arm (log loss 0.935 vs 1.223). Excluding 2016 only as a declared sensitivity strengthens the overall contrast, but does not replace the primary result.

This converts cryptic degradation from a descriptive mismatch into an **early-warning hypothesis**:

> **A transect can remain recorded-positive while its quantitative meadow state already contains information about instability in the following year.**

Because this hypothesis was motivated after inspecting the broader Tampa state-decoupling result, the current evidence is an **exploratory strict walk-forward validation**, not an untouched prospective or external replication.

### 5. The 2016 loss / 2017 return pulse is not the main result

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

This is a useful negative result: **no simple annual water-quality variable currently explains the post-2016 state changes at this aggregation scale**.

A narrower seasonal screen then aligned water quality to each target survey month and tested only an a priori 8-test family: *Thalassia* frequency/cover change against the hottest monthly mean temperature and freshest monthly mean salinity in the preceding 3- and 6-month windows. This also returned no support:

- primary 2017–2025 exposure units: **94**
- FDR < 0.05: **0/8**
- FDR 0.05–0.10: **0/8**
- smallest primary nominal test: minimum 3-month salinity vs *Thalassia* Braun-Blanquet change, `rho=0.126`, `p=0.225`, `q=0.918`
- excluding target year 2017 gives the same conclusion; best `q=0.773`

Thus the simple **seasonal hot/fresh** explanation is also unsupported at segment-month resolution. This does not reject acute daily extremes, local hydrodynamics, within-segment gradients or other mechanisms, and it does not support climate-causal attribution.

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
python analysis/08_seasonal_stress_screen.py --input results/generated --out results/generated
python analysis/09_quantitative_early_warning.py --input results/generated --out results/generated
python analysis/11_nps_persistent_cover.py --out results/generated_nps_posthoc
python analysis/12_nps_persistent_cover_sensitivity.py --input results/generated_nps_posthoc --out results/generated_nps_posthoc
```

CI reruns the Tampa analyses from pinned public sources; the NPS post-hoc workflow separately rebuilds the external persistent-cover analysis.

Canonical current boundary: `results/current_validation_v2.json`.

`results/initial_validation.json` is retained as historical provenance and contains superseded early exploratory wording.

## Claim boundary

Supported now:

- annual recorded *Thalassia* state has strong temporal memory;
- earlier site history adds information beyond previous-year state;
- multiple quantitative state dimensions can trend differently from binary detection;
- Old Tampa Bay, Middle Tampa Bay and Lower Tampa Bay show different forms of state decoupling after 2016;
- Lower Tampa Bay shows a reproducible compositional signal: declining *Thalassia* and *Syringodium* with increasing *Halodule* frequency;
- no declared simple annual water-quality coupling survives the post-2016 multiplicity-controlled segment-year screen;
- aligning temperature and salinity to 3- and 6-month pre-survey windows still yields no multiplicity-controlled seasonal hot/fresh association;
- source-year *Thalassia* frequency and Braun-Blanquet state add strict out-of-time information about next-year **recorded loss** beyond space, time, survey timing and effort;
- in the independent NPS Tier-3 *Zostera* panel, recorded presence and focal frequency are completely saturated while quantitative cover varies widely and declines on average within repeated transects, reproducing the binary–quantitative **state-decoupling** pattern post hoc.

Not supported now:

- demographic extinction/recolonization from recorded absence/presence;
- a causal temperature, salinity or nutrient mechanism;
- a confirmed ecological interpretation of the 2016/2017 pulse;
- a universal 10-year biological memory constant;
- equivalence between fixed-transect condition and bay-wide mapped acreage;
- demographic extinction risk or causal collapse mechanism from the early-warning endpoint;
- untouched prospective or external confirmation of the early-warning hypothesis.

## Independent validation ledger

### Caribbean SeagrassNet v1 — terminal protocol/schema STOP

The first untouched external test was frozen before opening PANGAEA dataset `10.1594/PANGAEA.994149` (27 Caribbean locations, 2000–2017). The contract fixed *Thalassia testudinum*, annual station-state construction, next-year recorded loss, the space/time/effort baseline, the two quantitative augmentation features, estimability minima and terminal decision rules before response access.

The one-shot workflow reached a terminal **protocol/schema STOP** before model fitting:

- workflow: `36272071012`
- terminal: `invalid_numeric:focal_percent_cover:`
- model fits: **0**
- predictive scores: **0**
- counts as external predictive evidence: **false**

At least one row matched the frozen *Thalassia* identity while its percent-cover field was empty, violating the predeclared parser contract. Per the no-rescue rule, v1 is **not repaired or rerun** and the already-opened Caribbean dataset is not promoted as a fresh independent confirmation under a new parser.

This STOP narrows the next step: use a different, response-unopened monitoring dataset with quantitative species cover and freeze its data semantics before outcome access.

### NPS Tier-3 *Zostera marina* v2 — terminal non-estimable endpoint

A second frozen external attempt used the 2025 NPS Tier-3 seagrass data package. Official EML metadata established permanent quadrats, an explicit 0–100% cover scale and separate NA semantics before response access. The once-only endpoint then opened the CSV exactly once.

The frozen endpoint yielded:

- eligible annual units: **240**;
- stable transects: **18**;
- source-positive consecutive transitions: **204**;
- recorded persistence transitions: **204**;
- recorded-loss transitions: **0**;
- model fits: **0**;
- predictive scores: **0**;
- counts as external predictive evidence: **false**.

Thus NPS v2 is **non-estimable**, not an adverse early-warning result. Its zero-loss structure motivated the explicitly post-hoc persistent-cover analysis above, which is useful ecological replication but cannot be relabeled prospective predictive evidence.


## Next scientific gate

The primary next gate remains **independent validation of the quantitative early-warning hypothesis**, not further retrospective cause hunting. Caribbean SeagrassNet v1 stopped at its frozen schema gate and NPS Tier-3 v2 stopped as non-estimable because it contained zero recorded-loss transitions. Neither supplies an external predictive sign.

1. freeze the two quantitative predictors (frequency + Braun-Blanquet state), endpoint semantics and scoring rule before opening a new system or later held-out period;
2. test whether quantitative degradation predicts future recorded-state instability in an independent seagrass dataset, bay, or genuinely future Tampa survey;
3. keep the 2016 Tampa failure as part of the evidence rather than tuning it away.

Environmental attribution is secondary. Both annual and pre-survey 3/6-month hot-fresh screens are negative; finer event-scale exposure should be pursued only if it can be reconstructed defensibly without retrospective window hunting.

The manuscript-level ecological center is therefore: **binary persistence can conceal substantial quantitative degradation across independent seagrass monitoring systems; degradation mode is spatially heterogeneous, and Tampa additionally suggests that quantitative state may provide early warning of later recorded-state instability.**
