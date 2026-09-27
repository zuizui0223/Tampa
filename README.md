# Tampa — ecological memory and cryptic state degradation in Tampa Bay seagrass

This repository develops a biological analysis of long-term fixed-transect seagrass monitoring in Tampa Bay. It is intentionally separate from the EOG method-validation endpoint that motivated the question.

## Scientific mainline

The working question is now:

> **Can binary persistence conceal quantitative degradation, and do coarse and quantitative seagrass states retain ecological memory over different timescales?**

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

### 2c. External NPS panel supports short-term quantitative memory, not a general long-memory effect

The same already-opened NPS annual panel was used for a separate post-hoc ecological question: does quantitative *Zostera* cover retain temporal information beyond persistent site identity?

A strict target-year walk-forward comparison was restricted to matched same-transect transitions with at least two observations older than the source year. Every arm included location and node identity plus target year.

Across **177** matched transitions from **15** repeated transects and **14** scored target years:

- space/time/site baseline mean MAE: **11.14 percentage points**;
- + previous-year cover: **10.09**;
- previous-year cover improved **11/14** target years, baseline improved 2, with 1 tie;
- + older pre-lag history: mean MAE **9.49**, but it improved only **4/14** years relative to lag-1;
- the median older-history minus lag-1 MAE difference was **+0.091** (slightly worse);
- paired year-level sign-flip test for older history beyond lag-1: **p = 0.289**.

The supported external result is therefore **short-term quantitative state dependence**: last year's cover adds information about next year's cover even after persistent site identity is included. The NPS result does **not** support a robust increment from older history beyond the previous year.

This contrasts with Tampa's binary recorded-state model, where earlier history added information beyond lag-1. Because the systems, species, response dimensions and monitoring designs differ, this contrast does not establish a causal difference in memory horizon. It motivates a narrower hypothesis:

> **Ecological memory may be state-dimension dependent: coarse persistence states can integrate longer histories than rapidly varying quantitative condition.**

That hypothesis now requires a matched system in which binary and quantitative states can be forecast under the same sampling design.

### 2d. Within Tampa, quantitative condition has strong lag-1 memory but no older-history increment

The matched test can be done inside Tampa itself, removing the species/network confounding in the Tampa–NPS comparison. The primary panel keeps only consecutive transect-years in which *Thalassia* is recorded in **both** source and target years. Thus quantitative-memory performance cannot be explained simply by local disappearance or recolonization.

For **593** persistent-state transitions across **44** transects and **22** scored target years, every quantitative model already contained water-body identity, stable node identity and target year.

**Focal frequency**

- site/time baseline MAE: **0.0785**
- + previous-year frequency: **0.0673**
- lag-1 improves **21/22** years; paired sign-flip **p ≈ 5×10⁻⁵**
- + older history: **0.0680**
- older history improves only **10/22** years relative to lag-1
- older-history minus lag-1 median MAE delta: **+0.00102**
- sign-flip for older history beyond lag-1: **p = 0.719**

**Braun–Blanquet all-point index**

- site/time baseline MAE: **0.3057**
- + previous-year index: **0.2496**
- lag-1 improves **19/22** years; paired sign-flip **p ≈ 5×10⁻⁵**
- + older history: **0.2567**
- older history improves only **6/22** years relative to lag-1
- sign-flip for older history beyond lag-1: **p = 0.967**

Both quantitative state variables therefore reproduce the same pattern: **strong immediate state dependence, but no robust information gain from history older than the previous year**.

That differs from the frozen Tampa binary recorded-state analysis, where older history improved prediction beyond lag-1 in 14/22 target years. Effect magnitudes are not directly comparable because the response distributions, models and loss functions differ. But because the quantitative comparison is now within the **same species, transects and monitoring system**, the contrast more strongly motivates a state-dimension hypothesis:

> **Coarse persistence states may integrate longer ecological histories, whereas quantitative meadow condition is dominated by recent state.**

This is still a hypothesis about mechanism, not proof that state dimension itself causes the different memory horizon.

### 2e. The contrast survives transfer of the same exponential-memory operator

The binary and quantitative analyses initially summarized older history differently, leaving a representation-confounding alternative: perhaps quantitative long-memory failed only because its older history was encoded as a mean and trend rather than the exponential memory used for binary state.

That alternative was tested directly. The **exact exponential-memory representation family** from the binary analysis was transferred to both quantitative state variables. The primary decay scale was fixed at **τ = 10 years**, because that value had already been selected by the earlier frozen binary-state result before this replay was opened. The full historical τ grid was retained only as a descriptive audit.

For focal frequency:

- lag-1 MAE: **0.06699**
- + τ=10 exponential history: **0.06684**
- exponential arm wins **15/22** target years
- median exponential-minus-lag1 delta: **−0.00138**
- paired sign-flip: **p = 0.427**
- primary support rule: **not passed**

For the Braun–Blanquet all-point index:

- lag-1 MAE: **0.24027**
- + τ=10 exponential history: **0.25500**
- exponential arm wins only **2/22** target years
- median delta: **+0.01375**
- sign-flip: **p = 1.000**
- primary support rule: **not passed**

Across the descriptive 16-value τ grid, **no τ passed the same support rule for either quantitative metric**. The best nominal frequency result occurred at much shorter τ and still did not pass (minimum p ≈ 0.055); no Braun–Blanquet τ approached support.

Thus the current contrast is not readily explained by using different history summaries. The stronger statement remains conditional:

> **Within Tampa, coarse recorded state retains detectable information from history older than one year, whereas two quantitative condition variables do not show a robust older-history increment even when given the same exponential-memory operator.**

Different response distributions and learner families remain, so this still does not establish state dimension itself as the causal mechanism.



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
python analysis/13_nps_quantitative_memory.py --input results/generated_nps_posthoc --out results/generated_nps_posthoc
python analysis/14_tampa_matched_quantitative_memory.py --input results/generated_tampa_quant_memory --out results/generated_tampa_quant_memory
python analysis/15_tampa_cover_index_memory.py --input results/generated_tampa_quant_memory --out results/generated_tampa_quant_memory
python analysis/16_tampa_exponential_memory_replay.py --input results/generated_exp_memory --out results/generated_exp_memory
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
- in the independent NPS Tier-3 *Zostera* panel, recorded presence and focal frequency are completely saturated while quantitative cover varies widely and declines on average within repeated transects, reproducing the binary–quantitative **state-decoupling** pattern post hoc;
- in that same NPS panel, previous-year quantitative cover improves strict out-of-time next-year cover prediction beyond site identity in **11/14** target years, supporting short-term quantitative state dependence;
- within Tampa itself, when binary presence is held persistent across consecutive years, both focal frequency and Braun–Blanquet condition show strong lag-1 dependence but **no robust older-history increment**;
- transferring the **same exponential-memory representation** used by the frozen binary analysis likewise fails to produce supported older-history value for either quantitative metric, reducing history-feature choice as an alternative explanation.

Not supported now:

- demographic extinction/recolonization from recorded absence/presence;
- a causal temperature, salinity or nutrient mechanism;
- a confirmed ecological interpretation of the 2016/2017 pulse;
- a universal 10-year biological memory constant;
- equivalence between fixed-transect condition and bay-wide mapped acreage;
- demographic extinction risk or causal collapse mechanism from the early-warning endpoint;
- untouched prospective or external confirmation of the early-warning hypothesis;
- a universal long-memory effect across seagrass state variables; older NPS cover history does not robustly improve beyond lag-1;
- a causal claim that state dimension itself determines memory horizon; the binary and quantitative models use different response distributions and scoring metrics.

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

The strongest new ecological gate is now a **matched external test of state-dimension-dependent memory**: a monitoring system must contain both a variable coarse presence/persistence state and a quantitative condition state under the same repeated sampling design. The next contract must use the **same exponential all-prior-state operator and the same pre-frozen τ value(s) for both state dimensions**. The prediction is that lag-1 information should be useful for both states, while older history should satisfy the support rule for the coarse state but not for quantitative condition.

The separate predictive gate remains **independent validation of the quantitative early-warning hypothesis**, not further retrospective cause hunting. Caribbean SeagrassNet v1 stopped at its frozen schema gate and NPS Tier-3 v2 stopped as non-estimable because it contained zero recorded-loss transitions. Neither supplies an external predictive sign.

1. freeze the two quantitative predictors (frequency + Braun-Blanquet state), endpoint semantics and scoring rule before opening a new system or later held-out period;
2. test whether quantitative degradation predicts future recorded-state instability in an independent seagrass dataset, bay, or genuinely future Tampa survey;
3. keep the 2016 Tampa failure as part of the evidence rather than tuning it away.

Environmental attribution is secondary. Both annual and pre-survey 3/6-month hot-fresh screens are negative; finer event-scale exposure should be pursued only if it can be reconstructed defensibly without retrospective window hunting.

The manuscript-level ecological center is therefore: **binary persistence can conceal substantial quantitative degradation across independent seagrass monitoring systems; quantitative condition is strongly state-dependent over short timescales; and Tampa suggests that coarse persistence states may retain longer ecological histories than quantitative condition, while quantitative degradation may also provide early warning of later recorded-state instability.**
