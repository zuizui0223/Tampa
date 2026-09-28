# Persistent occurrence conceals spatially heterogeneous degradation in a seagrass foundation species

## Abstract

Monitoring of foundation species often emphasizes distribution or presence, yet ecological condition can change substantially before local disappearance. We tested whether persistent recorded occurrence concealed quantitative degradation in 1997–2025 fixed-transect monitoring of *Thalassia testudinum* in Tampa Bay, Florida. The reconstructed panel comprised 1,497 eligible visits and 1,480 annual transect-years at 71 stable transects, resolving recorded presence, within-transect frequency, Braun–Blanquet abundance, blade length, and shoot density.

After 2016, recorded *Thalassia* occurrence changed weakly in several bay segments while quantitative state deteriorated through different pathways. In Old Tampa Bay, blade length declined by approximately 1.09 mm yr⁻¹ and shoot density by 38.3 shoots m⁻² yr⁻¹. In Middle Tampa Bay, blade length declined by approximately 0.405 mm yr⁻¹. In Lower Tampa Bay, *Thalassia* frequency and Braun–Blanquet abundance declined while *Halodule wrightii* increased and *Syringodium filiforme* decreased, consistent with compositional reorganization. A post-hoc external *Zostera marina* panel showed the same general state-decoupling pattern: recorded presence and focal frequency were saturated while quantitative cover varied widely.

Within Tampa, low source-year frequency and Braun–Blanquet state improved strict out-of-time prediction of next-year recorded-state loss, supporting an exploratory early-warning hypothesis. However, bounded spatial, environmental, and hidden-state tests did not identify a single mechanism for recent degradation. Persistent occurrence is therefore not equivalent to persistent ecological condition, and presence-only monitoring can detect foundation-species degradation late while obscuring distinct degradation pathways.

## Keywords

foundation species; seagrass; long-term monitoring; ecological condition; state decoupling; Tampa Bay

# Introduction

Foundation species create habitat, alter local physical conditions and support diverse ecological communities, so their loss can reorganize ecosystem structure and function (Ellison et al., 2005). Because distributions and mapped extent are often monitored over large areas and long periods, occurrence is a natural indicator of ecosystem status. Yet the ecological state of an occupied site is multidimensional. A species can remain detectable while local abundance declines, occupied area within a sampling unit contracts, individual condition deteriorates, or community composition changes. When these dimensions respond at different rates, persistence of a coarse occurrence state can give an incomplete picture of ecological degradation.

This problem is especially relevant for long-lived clonal habitat-forming plants. Their presence at a site can be buffered by persistent below-ground structures, established meadow architecture or favorable local habitat even while above-ground condition varies from year to year. Conversely, losses in density, stature or within-site occupancy can reduce ecological function before complete local disappearance. Seagrass indicator reviews emphasize that different structural and physiological metrics have different sensitivities and response times to stress (Roca et al., 2016). Monitoring programs that record both occurrence and quantitative state therefore provide an opportunity to ask not simply whether a foundation species is present, but whether different dimensions of its state remain coupled through time.

Seagrasses are a useful system for testing this distinction. Seagrass meadows provide major habitat and ecosystem functions but have experienced widespread historical losses and remain exposed to multiple interacting pressures (Orth et al., 2006; Waycott et al., 2009; Unsworth et al., 2019). Monitoring commonly includes broad distribution or presence alongside finer measures such as cover, shoot density, morphology and species composition. These variables capture different aspects of meadow state and need not respond synchronously to stress (Roca et al., 2016). A 2026 synthesis of 500 monitoring studies and an expert survey likewise found that distribution, species composition and cover are widely prioritized, whereas physiological- and organism-level methods remain comparatively underused; the authors recommend integrating metrics across biological levels (Rising et al., 2026). What remains less resolved is how those levels diverge through time when measured repeatedly at the same sites. Large-scale analyses of eelgrass further illustrate how multiple stressors can combine across long monitoring records (Lefcheck et al., 2017). A stable distributional footprint should therefore not automatically be interpreted as stable meadow condition.

Tampa Bay, Florida, provides an unusually long repeated-site record for evaluating this issue. Fixed-transect monitoring has tracked seagrass occurrence and condition across multiple bay segments for decades. The same sampling system contains nested information on *Thalassia testudinum*: whether the species is recorded at a transect, how frequently it occurs across sampled meter marks, its Braun–Blanquet abundance state, and plant-condition measurements including blade length and shoot density. The estuary also contains co-occurring seagrasses, allowing focal-state changes to be evaluated in a community context. This combination makes it possible to distinguish persistent differences among transects from changes occurring within the same monitored meadow.

Our initial analyses were motivated by temporal persistence in recorded *Thalassia* occurrence. However, subsequent reference-saturation tests showed that the apparent value of older history was strongly dependent on whether stable transect identity was already represented. We therefore treat temporal memory as a secondary diagnostic rather than the ecological center of the study. The primary question is more direct: **can a foundation species remain recorded at long-monitored sites while its quantitative meadow condition deteriorates?**

We address four ordered questions. First, we test whether post-2016 changes in recorded *Thalassia* occurrence are congruent with changes in within-transect frequency, Braun–Blanquet abundance, blade length and shoot density. Second, we ask whether the form of degradation is spatially consistent across Tampa Bay or whether different bay segments deteriorate through different state dimensions and community trajectories. Third, using an already-opened National Park Service *Zostera marina* panel, we ask whether saturated binary presence can coexist with substantial quantitative change in a second seagrass monitoring system. This external comparison is explicitly post hoc and is not treated as prospective predictive validation. Fourth, within Tampa, we test whether quantitative state contains out-of-time information about next-year instability of the coarse recorded state.

Mechanistic attribution is deliberately secondary. After establishing the state-decoupling pattern, we evaluated a bounded sequence of alternative explanations involving spatial accessibility, neighboring-meadow state, depth and sediment, light exposure, simple temperature and salinity summaries, published compound hot–fresh stress metrics, and several known-truth hidden-state models. These tests constrain interpretation but do not identify a single causal driver. The manuscript therefore focuses on the ecological information lost when persistent occurrence is treated as equivalent to persistent condition.

We expected that if occurrence were an adequate summary of meadow condition, temporal changes in binary detection and quantitative state would be broadly congruent within bay segments. In contrast, state decoupling predicts that binary occurrence can remain stable while one or more quantitative dimensions decline. We further expected that if this phenomenon reflects a broader monitoring property rather than a uniquely Tampa-specific trajectory, an external seagrass panel could show large quantitative change despite saturated recorded presence. Finally, if quantitative degradation often precedes change in the coarse state, source-year abundance measures should contain information about next-year recorded-state loss beyond space, time and survey-effort covariates.

# Methods

## Study system and source data

We analyzed long-term fixed-transect seagrass monitoring from Tampa Bay, Florida. The primary biological source was pinned to commit `6c567beff95ea04f0e397101befb49d5233ace8f` of the public `tbep-tech/obis-example` repository. Analyses used the Darwin Core Event, Occurrence and Extended Measurement or Fact tables from that immutable snapshot. Before biological reconstruction, scripts verified expected byte sizes and Git blob identities for all source files.

Transect visits were eligible when the parent event contained at least three sampled point events. The resulting panel contained 1,497 eligible visits from 71 stable transect locations spanning 1997–2025. Repeated visits within a calendar year were annualized at the stable transect level, yielding 1,480 annual transect-years.

The focal foundation species was *Thalassia testudinum*. Bay-segment identity and fixed transect coordinates were retained from the source Event table.

## Ecological state variables

We represented focal state using nested monitoring dimensions.

**Recorded presence.** A transect-year was coded as recorded-positive when *Thalassia* occurred at one or more eligible sampled points.

**Within-transect frequency.** For each visit, focal frequency was the number of sampled point events recording *Thalassia* divided by the total number of eligible sampled points. Annual frequency was the mean across visits when a transect was sampled more than once in a year.

**Braun–Blanquet abundance index.** Species-specific Braun–Blanquet values were parsed from the eMoF table. Points without focal occurrence contributed zero; points where the focal species was reported but no numeric Braun–Blanquet estimate was available remained missing for the numeric index. The resulting all-point mean is an ordinal abundance index and is not interpreted as percent cover.

**Plant condition.** Blade length and shoot density were summarized from numeric focal-species eMoF measurements. These variables were treated as plant-condition dimensions and had lower measurement coverage than occurrence, frequency and Braun–Blanquet state.

## Post-2016 within-transect state change

We evaluated state trajectories over 2016–2025 using within-transect models so that estimated temporal changes were not driven by changing composition of sampled sites. Models included stable transect fixed effects and adjusted for cyclic survey timing and sampled-point effort. Uncertainty was estimated by resampling transects in a node-cluster bootstrap.

For each bay segment we estimated slopes for recorded detection and available quantitative state variables. We interpreted a candidate state-decoupling pattern when a quantitative dimension showed a supported temporal decline while recorded detection changed weakly or its uncertainty overlapped zero. These models are descriptive temporal contrasts and do not identify environmental causes.

The 2016/2017 recorded-state pulse was retained only as exploratory context because survey-date and effort audits showed protocol sensitivity. It was not used as a headline disturbance event or interpreted as demographic extinction and recolonization.

## Community reorganization

To place focal changes in a community context, we reconstructed annual within-transect frequency and Braun–Blanquet state for *Thalassia testudinum*, *Halodule wrightii*, *Syringodium filiforme* and *Ruppia maritima*. Post-2016 within-transect slopes were estimated with the same general survey-timing and effort controls used for focal-state trends.

We additionally summarized consecutive-year changes among species within each bay segment. Opposing trends were interpreted as compositional reorganization or compensation signals, not as evidence of direct competition.

## External *Zostera marina* state-decoupling comparison

We used the already-opened National Park Service Northeast Coastal and Barrier Network Tier-3 seagrass panel as a post-hoc external ecological comparison. This dataset had previously been evaluated under a frozen next-year-loss endpoint but was non-estimable because all source-positive transitions retained recorded *Zostera marina* presence.

The post-hoc state-decoupling analysis included 240 eligible annual transect units from 2003–2025. Recorded presence and focal frequency were saturated across eligible units. We therefore analyzed quantitative cover trajectories among repeatedly sampled transects.

For each repeated transect with at least two annual observations, we estimated its within-transect cover slope. A pooled slope was calculated from the summed within-node cross-products, and uncertainty was estimated by bootstrap resampling repeated transects. Location-specific slopes were reported descriptively. Sensitivity analyses retained source identity anomalies rather than silently repairing them; single-year identities did not contribute to repeated-transect slopes.

Because the NPS response had already been opened during the earlier estimability test, this analysis is external ecological replication of state decoupling but not untouched predictive confirmation.

## Quantitative state and next-year recorded-state instability

We constructed consecutive annual transitions for stable Tampa transects. The source year was required to record *Thalassia* presence. The endpoint was next-year recorded loss, defined as the focal species being unrecorded at the same transect in the immediately following year. This endpoint describes observation-state instability and is not equated with demographic extinction.

The transition registry contained 688 source-positive consecutive transitions, of which 24 were followed by recorded loss and 664 by recorded persistence.

We compared two logistic-regression arms under strict target-year walk-forward validation. For each scored target year, models were trained only on transitions from earlier target years.

The baseline contained source year, longitude, latitude, bay-segment identity, cyclic survey-date terms and log sampled-point effort. The quantitative augmentation added source-year focal frequency and Braun–Blanquet all-point state. Model regularization and training gates were fixed in the analysis script before the scored comparison.

Performance was summarized by target-year log loss and Brier score, macro-averaged across scored target years. We also reported pooled AUC descriptively. Target year 2016 was retained in the primary analysis even though the quantitative arm performed substantially worse in that year. Exclusion of 2016 was reported only as a declared sensitivity because the 2016/2017 pulse had independent protocol concerns.

Because this endpoint was formulated after observing Tampa state decoupling, we classify it as exploratory strict walk-forward internal validation.

## Temporal-state diagnostics

We used temporal prediction analyses to characterize state dependence but not as the manuscript's primary ecological endpoint.

Recorded-state models compared a space/time reference, a model adding immediately previous-year state, and models adding summaries of earlier history. Later reference-saturation audits added stable transect identity to determine whether older-history value persisted after repeated-site heterogeneity was represented directly.

Matched quantitative analyses of focal frequency and Braun–Blanquet state used the same stable transects and target years, with site identity represented in all model arms. Additional analyses transferred the same exponential-history operator used for binary state to quantitative outcomes.

The robust interpretation criterion was deliberately conservative: older-history evidence was not treated as a biological-memory claim when formal support disappeared after adding stable transect identity.

## Bounded mechanism and alternative-explanation tests

After the main ecological pattern was established, we evaluated a bounded set of candidate explanations. These tests were not used to choose the main result and were stopped prospectively within each development line when their frozen support criteria failed.

The tested classes included:

- static EOG regional geometry and response-independent reconstruction of its prediction-facing state;
- annually refreshed neighboring-transect state at four frozen spatial radii;
- decomposition into previous-year bay-segment state and finer local-neighborhood deviation;
- known-truth thresholding and hidden-state simulations;
- response-independent depth and sediment summaries followed by leave-one-node-out state prediction;
- a pre-survey benthic-light proxy derived from segment-level Secchi and visit depth;
- annual environmental associations and predeclared 3/6-month temperature/salinity windows;
- the exact published Tampa Bay 30 °C / 25 ppt compound hot–fresh stress reconstruction.

The purpose of this sequence was to constrain causal interpretation, not to identify a best retrospective predictor. Per the final mechanism boundary, no additional temperature threshold, salinity threshold, lag window, spatial radius, generic connectivity index, hidden-state simulation family, depth/sediment transformation or bulk-light formula is selected after the observed results.

## AI-assisted research and manuscript development

ChatGPT (OpenAI) was used interactively during development of the analysis repository to assist with code drafting, reproducibility auditing, alternative-explanation test design, and manuscript drafting and editing. All scientific questions, frozen decision rules, source selections, analyses, interpretations, code changes, and final manuscript text were reviewed and approved by the human author(s), who take responsibility for the work. The AI system is not listed as an author.

## Reproducibility and figure data

Primary analyses rebuild from pinned public sources in GitHub Actions. Canonical result boundaries are recorded in `results/current_validation_v2.json`. The current ecological mechanism stopping rule is recorded in `docs/ECOLOGICAL_MECHANISM_BOUNDARY_V1.md`.

Manuscript-facing Figure 1, Figure 2, the Tampa component of Figure 3 and Figure 4 are generated from frozen figure-data tables built inside the primary ecological reproducibility workflow. The external NPS component of Figure 3 is generated separately from the post-hoc NPS source pipeline so that its evidentiary status is not conflated with the Tampa primary analysis.

# Results

## Long-term monitoring resolves multiple dimensions of *Thalassia* state

The reconstructed Tampa Bay panel contained 1,497 eligible fixed-transect visits from 71 stable transects between 1997 and 2025, yielding 1,480 annual transect-years. We represented *Thalassia testudinum* state at four nested levels: recorded presence, frequency of occurrence across sampled meter marks, Braun–Blanquet abundance index, and plant-condition measurements including blade length and shoot density. These variables were not temporally equivalent. Recorded presence, focal frequency and Braun–Blanquet state were strongly structured by persistent differences among transects, whereas blade length and shoot density varied much more within transects through time. Stable transect identity alone descriptively accounted for 0.823 of the level variation in recorded detection, 0.874 in focal frequency and 0.862 in Braun–Blanquet state, compared with 0.259 for blade length and 0.232 for shoot density. These quantities are descriptive rather than causal variance partitions, but they establish a clear state hierarchy: long-run occurrence and abundance are strongly site-anchored, whereas plant condition is substantially more temporally labile.

## Persistent occurrence coexisted with declining quantitative condition after 2016

Post-2016 trajectories differed among bay segments even after comparing changes within the same transects and adjusting for survey timing and sampled-point effort.

In Old Tampa Bay, recorded detection changed only weakly, with an estimated slope of -0.0215 yr⁻¹ and a bootstrap interval reaching zero. In contrast, blade length declined by 1.09 mm yr⁻¹ (95% bootstrap interval approximately -1.69 to -0.68 mm yr⁻¹), and shoot density declined by 38.3 shoots m⁻² yr⁻¹ (approximately -49.8 to -21.9 shoots m⁻² yr⁻¹). Thus, the clearest recent change in Old Tampa Bay occurred within the condition of recorded *Thalassia* rather than in its binary detection state.

Middle Tampa Bay showed a related but narrower form of decoupling. Recorded detection was stable to weakly increasing, whereas blade length declined by approximately 0.405 mm yr⁻¹, with a bootstrap interval of about -0.908 to -0.222 mm yr⁻¹. This pattern again indicated deterioration of a plant-condition dimension without a corresponding decline in the coarse occurrence endpoint.

Lower Tampa Bay differed from both upper segments. Recorded detection changed weakly, but within-transect focal frequency declined by approximately 0.0128 yr⁻¹ (bootstrap interval about -0.0240 to -0.00367 yr⁻¹), and Braun–Blanquet abundance also declined. The dominant degradation signal in Lower Tampa Bay was therefore contraction of within-transect occupancy and abundance rather than primarily reduced plant stature.

Boca Ciega Bay did not exhibit the same clear combination of persistent recorded occurrence and declining quantitative state. The spatial counterexample is important: the post-2016 pattern was not a uniform Tampa-wide decline detectable in every state dimension. Instead, similar coarse occurrence states concealed different quantitative trajectories among bay segments.

## Lower Tampa Bay also showed compositional reorganization

The Lower Tampa Bay decline in focal *Thalassia* state coincided with changes in other seagrasses. From 2016 to 2025, *Thalassia* frequency decreased, *Syringodium filiforme* frequency also decreased, and *Halodule wrightii* frequency increased. Old Tampa Bay did not show the same monotonic alternative-species pattern, and Middle Tampa Bay was likewise better characterized by declining *Thalassia* blade length than by compensatory species change.

The Lower Tampa Bay pattern is therefore consistent with community reorganization toward greater relative prominence of *Halodule* while *Thalassia* and *Syringodium* decline quantitatively. The observational data do not identify competition or direct replacement, so we use compositional reorganization rather than competitive displacement as the ecological interpretation.

Together, the segment results identify at least two distinct pathways beneath persistent occurrence: deterioration of plant condition within established *Thalassia* meadows and contraction/reorganization of local meadow composition. These pathways can produce the same coarse outcome—continued recorded presence of the focal foundation species.

## Pre-existing mixed-species patches buffered seagrass occupancy after exact-point *Thalassia* loss

The community trajectories motivated a post-hoc exact-point test of whether species diversity buffered the habitat state when focal *Thalassia* disappeared from a meter mark. Across 370 consecutive post-2016 meter-mark transitions in which *Thalassia* was present in the source year and absent the following year, source points that already contained another seagrass species were more likely to remain seagrass-occupied after focal loss than source points containing *Thalassia* alone. Target-year seagrass occupancy was 85.1% among 281 source-mixed transitions versus 70.8% among 89 *Thalassia*-only transitions, a difference of 14.3 percentage points (node-cluster bootstrap 95% interval 4.45–26.72 percentage points).

The persistence of the habitat state was primarily associated with community members that were already present before focal loss rather than with exclusively new alternative-species appearance. Among 302 focal-loss points that remained seagrass-occupied, 71.2% retained at least one alternative species already recorded in the source year (bootstrap 95% interval 59.2–82.7%); only 28.8% were occupied exclusively by alternative species not recorded at the source point.

These exact-point results support a **community-insurance pattern**: pre-existing mixed-species patches were less likely to become seagrass-bare when *Thalassia* was lost. They do not identify facilitation because multispecies points may also represent persistently favorable habitat, and continued occupancy by another seagrass does not imply functional equivalence to *Thalassia*.

## A second seagrass monitoring system reproduced binary–quantitative state decoupling

We next asked whether a saturated occurrence state could coexist with large quantitative trajectories outside Tampa. The already-opened National Park Service Tier-3 *Zostera marina* panel contained 240 eligible annual transect units from 2003 to 2025. Recorded *Zostera* presence was retained in all 240 units, and focal frequency was 1.0 throughout the eligible panel. Quantitative cover nevertheless ranged from 0 to 99.2%.

Among 15 repeatedly sampled transects, the median within-transect cover range was 58.1 percentage points. Eleven of the 15 transects had negative cover slopes and four had positive slopes. The pooled within-transect cover slope was approximately -1.52 percentage points yr⁻¹, with a node-bootstrap interval of about -2.45 to -0.60 percentage points yr⁻¹. Direction varied among locations: Duck Harbor Beach, Fire Island and Tingles Island declined; Moriches Bay increased; Pleasant Bay was uncertain.

This panel therefore does not support a universal seagrass decline. Instead, it reproduces the broader state-decoupling proposition in a different species and monitoring network: a binary presence state can be saturated while quantitative meadow state changes substantially and heterogeneously. Because this analysis followed an earlier opening of the NPS response during an estimability test, it is a post-hoc external ecological comparison rather than untouched predictive replication.

## Low quantitative state preceded some next-year recorded losses within Tampa

The state-decoupling result motivated a forward-looking question within Tampa: among transects where *Thalassia* was still recorded, did quantitative meadow state contain information about whether the focal species would be unrecorded the following year?

Across 688 consecutive source-positive transitions, 24 were followed by next-year recorded loss and 664 by recorded persistence. Source-year quantitative state was substantially lower before recorded loss. Median focal frequency was 0.0627 before loss compared with 0.302 before persistence, and median Braun–Blanquet all-point index was 0.0495 before loss compared with 0.713 before persistence.

A strict walk-forward comparison trained only on earlier target years. A baseline model containing year, geography, bay segment, survey timing and sampled-point effort achieved a macro mean log loss of 0.1556. Adding source-year focal frequency and Braun–Blanquet state reduced macro mean log loss to 0.1465. The quantitative-state model performed better in 17 of 23 target years, with a one-sided paired Wilcoxon p-value of 0.00271; pooled AUC increased from 0.636 to 0.739.

Target year 2016 was strongly adverse for the quantitative-state model and was retained in the primary analysis. Its presence shows that low current quantitative state is not a deterministic precursor of next-year recorded loss. The result instead supports a narrower hypothesis: quantitative degradation can contain information about instability of the subsequent recorded state before the focal species becomes unrecorded. Because this question was formulated after observing the broader Tampa state-decoupling pattern, it remains an exploratory internally walk-forward-validated result rather than prospective confirmation.

## Immediate local state was strongly informative, whereas older-history value was reference-dependent

Annual recorded *Thalassia* state showed strong immediate dependence on the previous year. Under the original spatial reference, adding lag-1 recorded state reduced mean log loss from 0.331 to 0.170, and adding exponentially weighted earlier history reduced it further to 0.139. However, the interpretation changed when persistent transect identity was added to the reference. At the transferred 10-year memory scale, the older-history increment no longer passed the frozen support rule, and none of 16 tested history scales was supported once stable node identity was included.

Focal frequency showed the same reference-saturation pattern: older history was supported under a geography/bay reference but lost formal support once stable transect identity was present. Braun–Blanquet state likewise retained no supported older-history scale after stable site identity was added. The robust temporal result is therefore strong recent-state dependence embedded within persistent among-transect heterogeneity, not a clean estimate of a long biological-memory constant.

This interpretation is also consistent with the external NPS panel, where previous-year quantitative cover improved out-of-time prediction beyond site identity in 11 of 14 target years, whereas older quantitative history did not add a robust increment beyond lag-1.

## No simple common mechanism was identified by the retrospective environmental and structural tests

We tested a bounded set of alternative explanations after the main state-decoupling pattern had been established. None supplied a general mechanism for the post-2016 quantitative changes.

Static EOG geometry was predictively adverse in the original Tampa endpoint and, after response-independent reconstruction, was shown to behave mainly as a fixed node-level spatial signature when all declared worlds survived. Replacing that static representation with annually refreshed neighboring-meadow state did not improve prediction. Decomposing spatial context into previous-year bay-segment state and finer local neighborhood deviation likewise produced no supported increment beyond stable node identity and the focal transect's own recent state at any of the four frozen spatial radii.

Measured depth and sediment were available across all 71 stable nodes, but a frozen leave-one-node-out test found no supported incremental value for long-run detection prevalence, focal frequency or Braun–Blanquet state beyond water-body identity and coordinates. A separate benthic-light proxy derived from segment-level Secchi and visit depth also failed to add robust held-out information for blade length or shoot density after controlling for persistent node identity, survey context, depth and bulk water clarity.

Annual water-quality associations and predeclared 3- and 6-month temperature/salinity screens yielded no multiplicity-controlled associations with the post-2016 state changes. Finally, the exact published Tampa Bay 30 °C / 25 ppt compound hot–fresh stress reconstruction did not add supported plant-condition information beyond marginal hot and fresh stress durations plus local previous-year state. For blade length, the compound model increased mean absolute error from approximately 6.33 to 6.43 mm and won 5 of 19 target years; for shoot density, error increased from approximately 186.3 to 188.7 shoots m⁻² and the compound arm won 7 of 19 target years.

These negative results do not imply that space, light, temperature, salinity, sediment or hydrodynamics are biologically irrelevant. They establish a narrower boundary: the available retrospective measurements and tested summaries do not identify one simple mechanism that explains the spatially heterogeneous degradation modes observed in Tampa.

---

# Discussion

## Persistent occurrence was a coarse and potentially lagging indicator of meadow condition

The central result is a decoupling between whether a foundation species remains recorded and how the meadow is changing internally. Across Tampa Bay, *Thalassia testudinum* could remain detectable at long-monitored transects while local frequency, ordinal abundance, blade length or shoot density deteriorated. The same coarse endpoint—recorded presence—therefore corresponded to markedly different quantitative ecological states.

This distinction matters because occurrence is often the most spatially complete and easily communicated component of monitoring. A distribution map can remain visually stable even when the structure of occupied habitat is changing. In the Tampa data, plant-condition traits were substantially more temporally labile than occurrence and abundance levels, and the segment-specific analyses showed that deterioration could proceed for years without a commensurate binary decline. Presence is therefore informative but incomplete: it is the coarsest member of a state hierarchy rather than a sufficient description of meadow condition.

## Different bay segments reached degradation through different state dimensions

The Tampa pattern is not well described by a single estuary-wide decline process. Old Tampa Bay was dominated by declining plant stature and shoot density. Middle Tampa Bay showed a more limited blade-length decline. Lower Tampa Bay instead lost within-transect *Thalassia* frequency and abundance while its community composition shifted toward greater *Halodule* frequency and lower *Syringodium* frequency.

This heterogeneity is not a nuisance to be averaged away; it is part of the ecological result. Different stress histories, habitat templates or demographic pathways can converge on the same binary state. A transect recorded as “present” may contain a dense but short-stature meadow, a sparse meadow near a detection threshold, or a community in which the focal species is becoming less prominent. A binary occurrence endpoint cannot distinguish among those trajectories.

The Lower Tampa Bay pattern is particularly useful because it illustrates that degradation of a focal foundation species need not occur in isolation. At the same time, the data do not establish direct competitive replacement by *Halodule*. The appropriate interpretation is community reorganization, with mechanism left open.

## Community insurance separates foundation-species loss from immediate habitat vacancy

The exact-point analysis adds a second form of state decoupling. Loss of the focal foundation species did not necessarily mean immediate loss of the broader seagrass habitat state. Pre-existing mixed-species points were more likely to remain vegetated after *Thalassia* loss, and most target alternative occupancy represented persistence of community members already present before focal disappearance.

This pattern resembles a biodiversity-insurance process at the level of habitat occupancy. Experimental seagrass restoration has shown that multispecies plantings can increase survival and cover relative to less diverse plantings (Williams et al., 2017), demonstrating that seagrass diversity can influence restoration trajectories. Our observational result asks a different question: in an established natural monitoring network, does pre-existing community mixture alter the fate of a meter mark when one foundation species is lost? The positive association is consistent with insurance, but not with a demonstrated facilitative mechanism.

The distinction matters for conservation. A meadow can retain seagrass occupancy while losing *Thalassia* identity, so “vegetated versus bare” and “which foundation species remains” are separate ecological endpoints. Community persistence may buffer some structural habitat continuity while still changing canopy architecture, below-ground structure, productivity, food-web support, and other functions. Functional consequences therefore require direct measurement rather than assuming that one seagrass species substitutes equivalently for another.

## External *Zostera* trajectories support the broader monitoring principle

The NPS *Zostera marina* panel provides a useful comparison because its binary state is even more saturated than Tampa's. Recorded presence and focal frequency were effectively constant, yet quantitative cover varied across nearly the full observed scale and showed both strong declines and increases among repeated transects.

The external panel therefore strengthens a general monitoring proposition rather than a species-specific decline claim: **binary persistence can coexist with large quantitative change**. The spatial heterogeneity in the NPS panel, including the positive Moriches Bay trend, is an important boundary. The result is not that seagrass cover must decline wherever presence remains stable, but that persistence of the binary endpoint does not determine either the magnitude or direction of quantitative change.

This distinction should be relevant beyond seagrasses wherever monitoring compresses a continuously varying foundation-species state into occupied/unoccupied habitat. More broadly, the foundation-species concept emphasizes that structural persistence and ecosystem function need not be interchangeable properties (Ellison et al., 2005).

## Quantitative state may provide earlier warning than recorded loss

Within Tampa, low focal frequency and low Braun–Blanquet state preceded a subset of next-year recorded losses and improved strict walk-forward prediction beyond space, time and survey-effort covariates. This provides a plausible operational consequence of state decoupling: quantitative degradation can become detectable before the coarse recorded state changes.

The endpoint must be interpreted carefully. A recorded loss is not demographic extinction, and a subsequent return is not necessarily recolonization. Detection, within-transect patchiness and protocol differences can all affect the recorded state. The strongly adverse 2016 target year also demonstrates that quantitative state is not a universal early-warning rule. We therefore treat the analysis as evidence that quantitative state contains information about **recorded-state instability**, not as a validated collapse predictor.

Prospective use would require freezing the model before a genuinely future monitoring wave or applying the same contract to a response-unopened external dataset with explicit zero-versus-missing semantics. The current result is best viewed as a testable monitoring hypothesis generated by the Tampa state hierarchy.

## The temporal signal is better described as recent local state plus persistent site heterogeneity than as long memory

The initial Tampa analysis suggested that earlier recorded history improved prediction beyond the immediately previous year. However, stable-site saturation changed the interpretation: once transect identity was represented directly, formal older-history support disappeared across the tested state dimensions and memory scales.

This does not mean that ecological history is irrelevant. Rather, repeated historical observations appear to carry information about persistent transect-specific quality that latitude, longitude and broad bay segment do not fully encode. In that sense, long history can act as a proxy for an unmeasured site template. But the current data cannot separate habitat legacy, clonal history, persistent environmental differences or other stable attributes well enough to call the residual signal a biological memory timescale.

The strong and reproducible temporal result is simpler: recent local state matters. Previous-year state was highly informative for Tampa quantitative condition and for quantitative cover in the NPS panel. That short-term dependence is consistent with ecological inertia of established meadows without requiring an inferred 10-year biological memory constant.

## A sequence of negative mechanism tests narrowed the question without identifying the answer

A common temptation after observing state decoupling would be to select the environmental variable, lag window or connectivity representation that best aligns with the observed decline. We instead retained a bounded sequence of tests and stopped when the predeclared alternatives failed.

The resulting mechanism ledger is scientifically useful even though it is mostly negative. Static regional geometry, simple annual spatial propagation, depth/sediment summaries, coarse benthic-light exposure, simple annual or seasonal water-quality metrics and the published compound hot–fresh duration did not supply a robust common explanation. The known-truth simulations likewise showed that several simple thresholding and hidden-state constructions were insufficient to reproduce the earlier apparent memory contrast.

These results should not be presented as evidence that Tampa seagrass degradation lacks environmental causes. Experimental and event-based work on *Thalassia testudinum* has shown that plant-condition and below-ground reserve metrics can respond strongly to environmental deterioration before complete meadow loss. In situ light reduction altered blade traits, production, shoot density and rhizome carbohydrate stores (Lee & Dunton, 1997), while an El Niño-associated water-quality perturbation in Florida identified shoot density, blade morphology and rhizome carbohydrates as responsive indicators (Carlson et al., 2003). These studies make our plant-condition dimensions biologically plausible early-response variables even though the coarse segment-level light proxy was unsupported here.

Beck et al. (2024) documented long-term warming and freshening of Tampa Bay and developed threshold-based stress indices as a weight-of-evidence climate-stress assessment. Our question was narrower and more incremental: within the fixed-transect *Thalassia* panel, did the published joint-stress duration add plant-condition information beyond marginal hot/fresh duration and local previous-year state? It did not. The two results are therefore not logically contradictory; they operate at different response scales and ask different inferential questions.

The current analyses show that **the information available at these spatial and temporal resolutions is insufficient to identify one general driver** of the observed state decoupling. That conclusion is compatible with several biologically plausible mechanisms that require genuinely new measurements rather than further transformations of the same retrospective variables.

Particularly informative future states include meadow-scale high-frequency temperature, salinity and photosynthetically active radiation; canopy and epiphyte light microenvironment; hydrodynamic exposure and residence time; below-ground biomass and carbohydrate reserves; clonal or rhizome architecture; and acute disturbance or disease indicators. These measurements could test whether the persistent site effect reflects local physical exposure, meadow legacy, physiological buffering, or interactions among them.

## Monitoring foundation species as a state hierarchy

The practical implication is not to abandon occurrence monitoring. Presence remains valuable for broad distribution, persistence and range surveillance. Rather, the Tampa results argue for explicit separation of state dimensions. This interpretation aligns with recent monitoring synthesis showing broad agreement on core distribution, composition and cover metrics but comparatively limited use of physiological- and organism-level measures, and recommending integrated monitoring across biological levels (Rising et al., 2026). The contribution here is empirical rather than prescriptive: the same repeated-site record shows that those monitoring levels can diverge for years and that the dimension of degradation differs spatially within one estuary.

For long-lived foundation species, a useful monitoring hierarchy is:

1. recorded presence;
2. local frequency or occupied fraction;
3. abundance or cover;
4. morphology and density;
5. community context.

Each level answers a different ecological question and can change on a different timescale. Collapsing them into a single “present” state sacrifices information precisely when degradation is developing inside still-occupied habitat.

In Tampa Bay, the consequence of that compression was visible across multiple pathways: plant-condition decline in Old and Middle Tampa Bay, occupancy/abundance contraction and community reorganization in Lower Tampa Bay, and quantitative weakening before some subsequent recorded losses. The external *Zostera* comparison showed that this decoupling is not unique to one focal species or one monitoring programme.

## Conservation implication: separate extent recovery from meadow-condition recovery

This distinction is directly compatible with existing Tampa Bay management infrastructure. The Tampa Bay Estuary Program already combines approximately biennial aerial seagrass-coverage mapping with annual transect monitoring at more than 60 locations, using the two data streams to assess broad habitat extent and within-bay status (Tampa Bay Estuary Program, n.d.). Our results suggest that those monitoring levels should be interpreted as complementary rather than interchangeable. Stable or increasing mapped extent should not by itself close concern if species-specific frequency, abundance, blade length, or shoot density is declining at repeatedly monitored meadows.

A practical use is therefore a **trajectory-based warning hierarchy** rather than a new hard threshold. Stable extent together with declining plant-condition state indicates hidden degradation within occupied habitat; declining focal frequency or abundance indicates meadow thinning; simultaneous focal decline and alternative-species change indicates community reorganization; and a recorded loss should trigger confirmation of sampling continuity before demographic interpretation. Sites with low or declining quantitative state can be prioritized for near-term resampling or local instrumentation, but the present early-warning analysis does not validate an intervention threshold or collapse forecast. Because focal frequency and Braun–Blanquet state have broad network coverage while blade length and shoot density are more temporally labile but less completely measured, a two-tier design is especially practical: use frequency/abundance for broad annual screening and deploy condition, below-ground, and high-frequency environmental measurements at flagged and matched reference meadows.

This framework changes the conservation question from “Is seagrass still present?” to “Which component of meadow state is changing while seagrass is still present?” That distinction is particularly important for clonal foundation species, for which established local structure can plausibly maintain a coarse occupancy state while plant condition changes more rapidly. The present study therefore supports earlier and more biologically resolved diagnosis, while leaving causal prescription to future measurements of local optical conditions, high-frequency temperature and salinity, hydrodynamics, epiphytes, disease, and below-ground meadow reserves.

## Conclusion

Long-term persistence of a foundation species does not imply persistence of meadow condition. Across Tampa Bay, *Thalassia testudinum* often remained recorded while different bay segments lost plant stature, shoot density, local occupancy or abundance, and Lower Tampa Bay reorganized compositionally. A second seagrass monitoring system reproduced the broader decoupling between saturated presence and quantitative change.

The mechanism of Tampa's recent degradation remains unresolved. That uncertainty does not weaken the principal ecological result; it defines its scope. Presence-only monitoring can detect foundation-species degradation late and cannot distinguish the pathways by which still-occupied habitat deteriorates.

# Figure captions

**Fig. 1** Tampa Bay monitoring resolves a hierarchy of seagrass states. **a** Locations of the 71 stable fixed transects included in the 1997–2025 analysis, grouped by monitored water body. **b** Descriptive fraction of level variation associated with stable transect identity versus year for five *Thalassia testudinum* state dimensions. Recorded detection, within-transect focal frequency, and the all-point Braun–Blanquet abundance index were strongly site-anchored, whereas blade length and shoot density were substantially more temporally labile. These descriptive (R^2) values are not causal variance partitions. Braun–Blanquet values are ordinal abundance classes, not percent cover

**Fig. 2** Persistent occurrence conceals bay-specific quantitative degradation. Post-2016 within-transect slopes and node-bootstrap 95% intervals for state dimensions defining contrasting Tampa Bay degradation pathways. **a** Recorded detection changed weakly in Old, Middle, and Lower Tampa Bay. **b** Blade length declined in Old and Middle Tampa Bay. **c** Shoot density declined strongly in Old Tampa Bay. **d** Within-transect focal frequency declined in Lower Tampa Bay. Models compare change within stable transects while accounting for survey timing and sampled-point effort. Similar coarse occurrence states therefore coexist with degradation in different quantitative dimensions

**Fig. 3** Quantitative change occurs beneath persistent recorded presence. **a** Mean annual within-transect frequency of *Thalassia testudinum*, *Syringodium filiforme*, and *Halodule wrightii* in Lower Tampa Bay during 2016–2025. Declining *Thalassia* and *Syringodium* alongside increasing *Halodule* are interpreted as compositional reorganization, not evidence of direct competitive replacement. **b** Location-level mean quantitative *Zostera marina* cover trajectories in the post-hoc National Park Service Tier-3 comparison. All 240 eligible NPS annual units retained recorded *Zostera* presence and focal frequency was 1.0 throughout, despite large and spatially heterogeneous quantitative cover trajectories. The NPS panel is post-hoc external ecological replication of state decoupling and is not untouched predictive confirmation of the Tampa early-warning result

**Fig. 4** Quantitative degradation can precede recorded-state instability. Source-year *Thalassia testudinum* state among 688 consecutive transitions in which the species was still recorded in the source year. **a** Focal frequency and **b** all-point Braun–Blanquet abundance index before next-year recorded persistence (n = 664) versus recorded loss (n = 24). **c** Target-year difference in log loss between the quantitative-state model and the space/time/survey-effort baseline under strict walk-forward evaluation; negative values indicate better performance after adding source-year frequency and Braun–Blanquet state. Target year 2016, in which the quantitative arm was strongly adverse, is retained and labelled in the primary result. Recorded loss is an observation-state endpoint and is not interpreted as demographic extinction

# References

This list contains every work currently cited in the manuscript and is ordered alphabetically following the journal's author–year / APA-style guidance.

Beck, M. W., Flaherty-Walia, K., Scolaro, S., Burke, M. C., Furman, B. T., Karlen, D. J., Pratt, C., Anastasiou, C. J., & Sherwood, E. T. (2024). Hot and fresh: Evidence of climate-related suboptimal water conditions for seagrass in a large Gulf coast estuary. *Estuaries and Coasts, 47*, 1475–1497. https://doi.org/10.1007/s12237-024-01385-0

Carlson, P. R., Jr., Yarbro, L. A., Madley, K., Arnold, H., Merello, M., Vanderbloemen, L., McRae, G., & Durako, M. J. (2003). Effect of El Niño on demographic, morphological, and chemical parameters in turtle-grass (*Thalassia testudinum*): An unexpected test of indicators. *Environmental Monitoring and Assessment, 81*, 393–408. https://doi.org/10.1023/A:1021322301725

Ellison, A. M., Bank, M. S., Clinton, B. D., Colburn, E. A., Elliott, K., Miniat, C. F., Foster, D. R., Kloeppel, B. D., Knoepp, J. D., Lovett, G. M., Mohan, J., Orwig, D. A., Rodenhouse, N. L., Sobczak, W. V., Stinson, K. A., Stone, J. K., Swan, C. M., Thompson, J., Von Holle, B., & Webster, J. R. (2005). Loss of foundation species: Consequences for the structure and dynamics of forested ecosystems. *Frontiers in Ecology and the Environment, 3*, 479–486. https://doi.org/10.1890/1540-9295(2005)003[0479:LOFSCF]2.0.CO;2

Lee, K.-S., & Dunton, K. H. (1997). Effect of in situ light reduction on the maintenance, growth and partitioning of carbon resources in *Thalassia testudinum* Banks ex König. *Journal of Experimental Marine Biology and Ecology, 210*, 53–73. https://doi.org/10.1016/S0022-0981(96)02720-7

Lefcheck, J. S., Wilcox, D. J., Murphy, R. R., Marion, S. R., & Orth, R. J. (2017). Multiple stressors threaten the imperiled coastal foundation species eelgrass (*Zostera marina*) in Chesapeake Bay, USA. *Global Change Biology, 23*, 3474–3483. https://doi.org/10.1111/gcb.13623

Orth, R. J., Carruthers, T. J. B., Dennison, W. C., Duarte, C. M., Fourqurean, J. W., Heck, K. L., Jr., Hughes, A. R., Kendrick, G. A., Kenworthy, W. J., Olyarnik, S., Short, F. T., Waycott, M., & Williams, S. L. (2006). A global crisis for seagrass ecosystems. *BioScience, 56*, 987–996. https://doi.org/10.1641/0006-3568(2006)56[987:AGCFSE]2.0.CO;2

Rising, K., Bulling, M., & Sweet, M. (2026). Seagrass monitoring methods: Aligning expert opinion with practice. *iScience, 29*, 114871. https://doi.org/10.1016/j.isci.2026.114871

Roca, G., Alcoverro, T., Krause-Jensen, D., Balsby, T. J. S., van Katwijk, M. M., Marbà, N., Santos, R., Arthur, R., Mascaró, O., Fernández-Torquemada, Y., Pérez, M., Duarte, C. M., & Romero, J. (2016). Response of seagrass indicators to shifts in environmental stressors: A global review and management synthesis. *Ecological Indicators, 63*, 310–323. https://doi.org/10.1016/j.ecolind.2015.12.007

Tampa Bay Estuary Program. (n.d.). Seagrass assessment. Retrieved September 28, 2026, from https://tbep.org/seagrass-assessment/

Unsworth, R. K. F., McKenzie, L. J., Collier, C. J., Cullen-Unsworth, L. C., Duarte, C. M., Eklöf, J. S., Jarvis, J. C., Jones, B. L., & Nordlund, L. M. (2019). Global challenges for seagrass conservation. *Ambio, 48*, 801–815. https://doi.org/10.1007/s13280-018-1115-y

Waycott, M., Duarte, C. M., Carruthers, T. J. B., Orth, R. J., Dennison, W. C., Olyarnik, S., Calladine, A., Fourqurean, J. W., Heck, K. L., Jr., Hughes, A. R., Kendrick, G. A., Kenworthy, W. J., Short, F. T., & Williams, S. L. (2009). Accelerating loss of seagrasses across the globe threatens coastal ecosystems. *Proceedings of the National Academy of Sciences of the United States of America, 106*, 12377–12381. https://doi.org/10.1073/pnas.0905620106

Williams, S. L., Ambo-Rappe, R., Sur, C., Abbott, J. M., & Limbong, S. R. (2017). Species richness accelerates marine ecosystem restoration in the Coral Triangle. *Proceedings of the National Academy of Sciences of the United States of America, 114*, 11986–11991. https://doi.org/10.1073/pnas.1707962114
