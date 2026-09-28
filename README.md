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

### 1. Strong immediate state dependence; older-history gain is reference-dependent

Annualization yields 1,480 transect-years and 1,176 consecutive-year transitions.

Under the original space/time reference, strict walk-forward prediction gave:

- space/time baseline mean log loss: **0.3312**
- + previous-year recorded state: **0.1701**
- + τ=10 exponentially weighted earlier history: **0.1395**
- long-history model beats lag-1 in **14/22** target years
- paired sign-flip **p = 0.01485**

A post-hoc reference-saturation audit then added only stable transect identity (`node_id`) to both lag-1 and long-history models. With that reference:

- lag-1 mean log loss: **0.1571**
- + τ=10 earlier history: **0.1417**
- long-history model beats lag-1 in **13/22** target years
- paired sign-flip **p = 0.0880**
- supported τ values across the 16-value grid: **0/16**, versus **6/16** without node identity.

The robust result is therefore **strong immediate state dependence**. Earlier history can improve prediction when the reference contains geography and bay segment but not stable transect identity; its formal support disappears once repeated-site identity is saturated. The older-history signal is consequently interpreted as a mixture of temporal information and persistent site-specific heterogeneity, not as a clean estimate of a long biological memory horizon.

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

### 2f. Simple thresholding does not generate the long-memory contrast under known truth

A more fundamental alternative is that the coarse binary state has no longer biological memory at all. Because annual detection is a lossy thresholding of sampled quantitative occurrence, older observations might help reconstruct hidden current intensity after information has been discarded by binarization.

That mechanism was tested in a frozen response-free known-truth experiment. The latent ecological state was constructed to be **strictly first-order Markov**. At each site-year, one Binomial point sample generated both responses:

- quantitative state = sampled frequency;
- coarse state = 1 if the same sampled count was greater than zero, otherwise 0.

The two state dimensions then used the **same Ridge learner, the same MSE/Brier loss, the same sites and years, and the same τ=10 exponential-memory operator**. The frozen grid crossed 3 persistence levels, 2 mean-state levels, 2 latent-variance levels and 2 sampling intensities, for **24 cells × 32 replicates = 768 simulations**.

The preregistered thresholding-amplification rule failed strongly:

- supporting cells: **1/24**; required **18/24**;
- replicates where older history helped binary relatively more than frequency: **30.6%**; required **70%**;
- robust φ levels: **0/3**; required **2/3**;
- global median amplification: **−0.00461**, opposite the predicted direction.

Thus simple coarse-graining was **not sufficient** to reproduce the field contrast. This is a useful mechanistic negative result:

> **The Tampa long-history signal in coarse recorded state cannot be reduced to the tested fact that frequency was thresholded into presence/non-presence.**

This does **not** prove genuine biological long-memory. It narrows the candidate mechanisms toward slower hidden ecological or observation states: persistent habitat condition, demographic legacy, unmeasured slow environmental forcing, or observation heterogeneity not represented by the simple Binomial threshold model.




### 2g. A slow latent state plus faster condition is also insufficient

A second frozen response-free known-truth test asked whether the contrast could arise from two latent timescales: a slowly autocorrelated persistence/suitability state plus faster meadow condition, observed through the same finite point sample.

Across **24 cells × 32 replicates = 768 simulations**, the complete target pattern was rare:

- supporting cells: **0/24**; required **18/24**;
- complete target-pattern fraction: **0.52%**; required **50%**;
- robust slow-persistence levels: **0/3**;
- global median binary-minus-quantitative older-history amplification: **−0.00284**;
- older-history support occurred in **0.91%** of binary replicates and **1.56%** of quantitative replicates.

Thus adding a slow AR(1) suitability/persistence process to faster condition is **not sufficient** to reproduce the Tampa contrast.

### 2h. First-order latent occupancy plus imperfect detection also fails the frozen sufficiency rule

The remaining simple hidden-state explanation was made more explicit: each patch has a persistent occupied/unoccupied state, conditional meadow condition varies faster, and finite point sampling creates imperfect detection. Binary and quantitative observations still come from the **same sampled count**, and both latent components remain first-order.

The frozen grid crossed 2 occupancy-persistence levels, 2 colonization levels, 2 fast-state autocorrelations, 2 mean-condition levels and 2 point counts, for **32 cells × 32 replicates = 1,024 simulations**.

The preregistered support rule again failed:

- supporting cells: **2/32**; required **24/32**;
- complete target-pattern fraction: **16.99%**; required **50%**;
- robust occupancy-persistence levels: **0/2**;
- global median binary-minus-quantitative older-history amplification: **+0.00142**;
- lag-1 support remained nearly universal (**99.8%** binary; **99.5%** quantitative);
- older-history support was more common for binary state (**22.75%**) than quantitative frequency (**12.30%**), but far below the frozen mechanism threshold;
- median false-negative rate among truly occupied site-years was **18.1%**.

The higher-persistence regime (`p11 = 0.98`) moved partially in the predicted direction, but only **2/16** cells supported the complete mechanism and the result was not robust.

> **Three simple response-free sufficiency explanations have now failed: thresholding alone, slow latent AR(1) suitability plus fast condition, and first-order latent occupancy persistence with imperfect detection.**

Per the prospectively frozen hard stop, this repository does **not** retune those grids or add another response-free simulation family in the same mechanism line. A later stable-site reference audit shows that formal older-history support is itself reference-dependent, so these mechanism simulations are retained as bounded diagnostics rather than evidence for a confirmed state-dimension memory mechanism.

### 2i. Stable transect identity absorbs formal older-history support

The earlier binary-versus-quantitative contrast depended on a reference asymmetry: the original binary model used coordinates and bay segment but not stable transect identity, whereas later quantitative models included `node_id`. A frozen post-hoc audit changed exactly that reference component while keeping each response's learner, loss, rows, lag-1 term, τ grid and target years fixed.

At the primary **τ = 10 years**:

- **binary recorded state:** history is supported without node identity (log loss **0.1701 → 0.1395**, 14/22 wins, **p = 0.01485**) but not with node identity (**0.1571 → 0.1417**, 13/22 wins, **p = 0.0880**);
- **focal frequency:** history is supported without node identity (MAE **0.05166 → 0.04993**, 16/22 wins, **p = 0.03505**) but not with node identity (**0.04702 → 0.04785**, 8/22 wins, **p = 0.9817**);
- **Braun–Blanquet index:** τ=10 history is unsupported both without and with node identity.

Across the full 16-value τ grid:

- binary: **6/16 → 0/16** supported τ values after adding node identity;
- frequency: **12/16 → 0/16**;
- Braun–Blanquet: **1/16 → 0/16**.

Thus no state dimension retains a formally supported older-history increment once stable transect identity is included. This weakens the earlier state-dimension-dependent memory-horizon interpretation. The more defensible ecological reading is that long history carries information about **persistent differences among transects** that coordinates and bay segment do not fully encode. Node identity itself is not a mechanism and must not be interpreted causally.

### 2j. EOG failure points toward a local site-template ecology rather than annual neighborhood accessibility

The frozen EOG Tampa endpoint was adverse because its prediction-facing structural block had become a static, node-specific geometry signature reused across repeated visits while all five declared worlds remained compatible. A post-hoc ecological translation therefore asked whether the biological state itself is mostly site-anchored and whether a genuinely dynamic neighborhood signal helps.

Stable transect identity alone descriptively accounts for:

- recorded detection: **R² = 0.823**
- focal frequency: **R² = 0.874**
- Braun–Blanquet all-point state: **R² = 0.862**
- blade length: **R² = 0.259**
- shoot density: **R² = 0.232**

Thus occurrence/abundance levels are strongly anchored to persistent site differences, whereas blade length and shoot density are much more temporally labile.

The dynamic-neighborhood audit then recomputed the previous year's state of surrounding transects inside the four frozen EOG radii (14.91, 23.93, 34.71 and 43.48 km) and added those features to a reference that already contained stable node identity, geography, year and the focal transect's own lag-1 state.

- binary detection: log loss **0.15708 → 0.16079**; mean delta **+0.00371**; neighborhood wins 12/22 years; sign-flip **p = 0.692**
- focal frequency: MAE **0.04702 → 0.04797**; mean delta **+0.000953**; neighborhood wins 7/22; **p = 0.991**

So a simple annually refreshed neighborhood-accessibility signal does not rescue the spatial story. The working ecological hypothesis is now that **persistent local site template and meadow legacy stabilize occurrence, while local plant condition can deteriorate on shorter timescales and eventually cross a recorded-state threshold**. This is a post-hoc hypothesis, not a causal identification. See `docs/EOG_ECOLOGICAL_HYPOTHESES_V1.md`.

### 2k. Segment-wide synchrony and local neighborhood both fail beyond own recent state

The first EOG ecological translation showed that adding four annually refreshed neighborhood summaries together did not improve prediction. A second frozen decomposition asked a narrower ecological question: is there useful **shared bay-segment state**, or a **finer local neighborhood deviation** after that shared state is represented?

For each consecutive annual transition, the reference already included stable transect identity and the focal transect's own previous-year state. The next model added the leave-one-node-out previous-year mean within the same water body. The final model added the previous-year neighborhood mean minus that water-body mean. The primary neighborhood radius (**23.93 km**) and three sensitivity radii were transferred unchanged from the frozen EOG Tampa world family.

At the primary radius:

- focal frequency: own-state MAE **0.04724**; + segment state **0.04763** (11/22 wins, **p = 0.927**); + local neighborhood residual **0.04843** (3/22 wins, **p = 0.9993**);
- Braun–Blanquet state: own-state MAE **0.16831**; + segment state **0.16805** (12/22 wins, **p = 0.257**); + local neighborhood residual **0.16979** (6/22 wins, **p = 0.9989**).

Neither increment passed the frozen support rule, and **0/4** tested radii supported either a segment or local-neighborhood increment for either quantitative state.

This sharpens the ecological interpretation: annual meadow state is not well described as simple spatial propagation from neighboring transects or as one-year shared segment synchrony after persistent site identity and local recent state are known. The unresolved driver appears more **site-local**. This does not exclude shared environmental forcing operating through finer event timing, nonlinear thresholds, or persistent habitat properties.

### 2l. Depth and sediment do not explain the persistent site template

The EOG-derived local-site hypothesis predicts that measured persistent habitat properties should explain some of the stable transect effect. A response-independent preflight first established that the pinned source contains usable physical covariates at all **71/71** stable nodes: point depth and five normalized sediment categories (mud, muddy sand, oyster, sand, shelly sand). Only 39 point events had conflicting sediment labels and were excluded rather than adjudicated.

A frozen leave-one-node-out analysis then predicted each transect's long-run *Thalassia* state. The reference already contained water-body identity and geographic coordinates; the measured-template model added node-level depth median/IQR plus modal sediment, modal fraction and sediment entropy.

None of the three primary occurrence/abundance states passed the support rule:

- detection prevalence: MAE **0.2174 → 0.2268**, **p = 0.731**;
- focal frequency: **0.1347 → 0.1483**, **p = 0.977**;
- Braun–Blanquet state: **0.4673 → 0.4796**, **p = 0.693**.

Primary support was therefore **0/3**. A secondary blade-length sediment contrast was directionally better but remained unsupported (**p = 0.087**) and is not promoted.

This narrows the persistent-site hypothesis: the strong node effect is **not simply depth plus sediment class**. Candidate site-template mechanisms now shift toward benthic light climate / chronic water clarity, hydrodynamic exposure or residence time, finer-scale chronic water quality, below-ground rhizome/biomass legacy, and interactions between persistent habitat and episodic stress.

### 2m. A segment-level benthic-light dose does not explain plant-condition variation

Tampa Bay seagrass management and prior experiments make underwater light at depth a biologically plausible mechanism. To test that idea without conflating light with depth itself, a response-independent preflight combined visit-specific median point depth with the pinned monthly Secchi series. Using the fixed relation `Kd = 1.7 / Secchi`, the primary exposure was mean `exp(-Kd × depth)` across the six complete months before each survey.

Coverage was strong: **1,236 visits**, **57 stable nodes**, **1998–2025**, with benthic-light fractions spanning **0.082–0.989**.

The frozen walk-forward reference already included stable node identity, water body, year, survey timing, effort, visit depth and six-month mean Secchi. Adding only the nonlinear benthic-light fraction did not pass the support rule for either primary plant-condition outcome:

- blade length: MAE **6.7684 → 6.7668 mm**, 11/22 wins, **p = 0.468**;
- shoot density: **173.86 → 175.13 shoots m⁻²**, 10/22 wins, **p = 0.945**.

Focal frequency and Braun–Blanquet state were also unsupported, and the predeclared three-month sensitivity did not change the conclusion.

This does **not** show that light is biologically irrelevant. It shows that a coarse segment-level Secchi × transect-depth proxy does not explain the remaining annual signal after strong site and survey controls. Node-scale optical variability, spectral quality, epiphyte shading and event-scale stress remain unresolved.

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
python analysis/17_threshold_induced_memory.py --out results/generated_threshold_memory
python analysis/18_tampa_quantitative_memory_conditioning_audit.py --input results/generated_conditioning_audit --out results/generated_conditioning_audit
python analysis/19_two_timescale_hidden_state_memory.py --out results/generated_two_timescale
python analysis/20_latent_occupancy_detection_memory.py --out results/generated_latent_occupancy
```

CI reruns the Tampa analyses from pinned public sources; the NPS post-hoc workflow separately rebuilds the external persistent-cover analysis.

Canonical current boundary: `results/current_validation_v2.json`.

`results/initial_validation.json` is retained as historical provenance and contains superseded early exploratory wording.

## Claim boundary

Supported now:

- annual recorded *Thalassia* state has strong immediate year-to-year dependence;
- under the original geography/bay reference, earlier history improves binary-state prediction beyond lag-1, but this formal support disappears when stable transect identity is added;
- the same site-identity saturation pattern occurs for focal frequency, and **no state dimension has any supported τ value once node identity is included**;
- long history therefore carries substantial information about persistent transect-specific heterogeneity not captured by coordinates and bay segment, although node identity is not itself an ecological mechanism;
- multiple quantitative state dimensions can trend differently from binary detection;
- Old Tampa Bay, Middle Tampa Bay and Lower Tampa Bay show different forms of state decoupling after 2016;
- Lower Tampa Bay shows a reproducible compositional signal: declining *Thalassia* and *Syringodium* with increasing *Halodule* frequency;
- no declared simple annual water-quality coupling survives the post-2016 multiplicity-controlled segment-year screen;
- aligning temperature and salinity to 3- and 6-month pre-survey windows still yields no multiplicity-controlled seasonal hot/fresh association;
- source-year *Thalassia* frequency and Braun-Blanquet state add strict out-of-time information about next-year **recorded loss** beyond space, time, survey timing and effort;
- in the independent NPS Tier-3 *Zostera* panel, recorded presence and focal frequency are completely saturated while quantitative cover varies widely and declines on average within repeated transects, reproducing the binary–quantitative **state-decoupling** pattern post hoc;
- in that same NPS panel, previous-year quantitative cover improves strict out-of-time next-year cover prediction beyond site identity in **11/14** target years, supporting short-term quantitative state dependence;
- three frozen response-free mechanism families fail their global sufficiency rules: thresholding alone, slow latent AR(1) suitability plus fast condition, and first-order latent occupancy persistence with imperfect detection.

Not supported now:

- demographic extinction/recolonization from recorded absence/presence;
- a causal temperature, salinity or nutrient mechanism;
- a confirmed ecological interpretation of the 2016/2017 pulse;
- a universal 10-year biological memory constant;
- a robust state-dimension-dependent difference in older-history horizon after stable transect identity is included;
- interpreting `node_id` as a causal habitat mechanism;
- equivalence between fixed-transect condition and bay-wide mapped acreage;
- demographic extinction risk or causal collapse mechanism from the early-warning endpoint;
- untouched prospective or external confirmation of the early-warning hypothesis;
- proof of biological long-memory or identification of its mechanism.

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

The manuscript-level ecological center is **state decoupling and spatially heterogeneous degradation**, not a long-memory or generic connectivity mechanism.

The EOG translation sharpens the next ecological question. Stable site identity dominates occurrence/frequency/abundance levels, simple annually refreshed neighborhood state adds no mean heldout value, and plant-condition variables are much more temporally labile. The highest-value next causal work is therefore to replace `node_id` with measured components of the persistent site template rather than adding more abstract memory/connectivity features.

Priority measurements or defensible historical reconstructions are:

1. depth and benthic light climate / water clarity;
2. sediment and rhizosphere properties;
3. exposure / hydrodynamic setting;
4. chronic local water-quality regime;
5. direct indicators of meadow persistence and clonal/rhizome structure where available.

The quantitative next-year-loss result remains explicitly exploratory until a genuinely future Tampa wave or pre-authorized external dataset can be scored under a frozen contract.

The manuscript-level synthesis is therefore: **binary persistence can conceal substantial, spatially heterogeneous quantitative degradation; recent local state is strongly predictive; apparent long-history gains are partly absorbed by stable transect identity; and neither static EOG geometry nor a simple annually refreshed neighborhood state explains the changing annual response.**
