# Supplementary Information

## Persistent occurrence conceals spatially heterogeneous degradation in a seagrass foundation species

This Supplement documents source reconstruction, sensitivity analyses, temporal-state diagnostics, bounded mechanism tests, and external-validation attempts supporting the claim boundaries in the main manuscript. The ordering follows the analysis history and does not select a retrospective “best” mechanism after observing outcomes.

# Supplementary Methods S1. Source reconstruction and identity checks

## Pinned biological source

The Tampa analyses use an immutable snapshot of the public TBEP Darwin Core conversion in the tbep-tech/obis-example repository, commit 6c567beff95ea04f0e397101befb49d5233ace8f. The analysis scripts retrieve Event, Occurrence, and Extended Measurement or Fact (eMoF) files from that snapshot and verify expected byte sizes and Git blob identities before parsing. A source mismatch causes the analysis to stop rather than silently consume a newer upstream version.

The Event table provides the hierarchy between parent transect visits and point-level child sampling events, along with survey date, coordinates, water body, stable location identifier, and point-depth information. Occurrence records provide taxonomic presence at point events. eMoF records provide quantitative measurements, including Braun–Blanquet scores, blade length, shoot density, and sediment type where available.

## Eligible visits and stable transects

A parent transect visit was eligible when it contained at least three sampled point events. This rule was applied before focal-species response reconstruction. The resulting Tampa registry contains 1,497 eligible transect visits between 1997 and 2025. Stable transect identity is represented by the source locationID field and yielded 71 repeated nodes.

The stable node identifier is treated as a repeated-site reference, not as an ecological mechanism. It can absorb persistent differences among transects that are not explicitly measured, including habitat, meadow history, and observation characteristics.

## Recorded presence and within-transect frequency

For each eligible visit, *Thalassia testudinum* recorded presence was coded as positive when the focal species occurred in at least one eligible point event. Focal frequency was the number of sampled point events recording *Thalassia* divided by the total eligible sampled point count.

When a transect had more than one eligible visit in a calendar year, visit-level state was annualized at the stable-node level. Annualization yielded 1,480 node-years and preserved the same stable spatial registry used by the repeated-site analyses.

## Braun–Blanquet abundance index

Species-specific Braun–Blanquet measurements were parsed from eMoF records. Focal-absent sampled points contributed zero to the all-point index. Numeric focal Braun–Blanquet values were averaged over sampled points. Text values such as “Reported” were not converted to invented numeric scores. The resulting variable is an ordinal abundance index and is never interpreted as percentage cover.

## Plant-condition variables

Blade length and short-shoot density were parsed from numeric focal-species eMoF records. Because these measurements were not collected in every eligible transect-year, plant-condition analyses use the available quantitative records and report their lower coverage explicitly. Missing condition data were not imputed from occurrence or abundance.

## Survey timing and effort

Survey date was converted to cyclic day-of-year terms so that seasonal timing could be included without imposing a linear January-to-December effect. Sampled-point effort was represented by the number of eligible child point events and, where used predictively, its log transform. These variables were included because visit timing and point effort varied through the monitoring record and could otherwise create apparent ecological change.

## Protocol audit of the 2016/2017 pulse

The source record shows an unusual survey-calendar concentration in 2016 and changes in sampled-point effort at several transects participating in the apparent 2016 recorded-loss / 2017 return pulse. The OBIS conversion and current tbeptools processing also differ in how dates from multi-day transect identifiers are reduced. Because of this protocol sensitivity, the pulse is retained as provenance but is not interpreted as confirmed demographic extinction and recolonization.

# Supplementary Methods S2. Post-2016 within-transect trend models

The primary state-decoupling analysis focused on 2016–2025, when several quantitative Tampa trajectories visibly changed. For each state dimension, temporal change was estimated within stable transects rather than from cross-sectional differences among sites.

Models included stable node effects, linear year, cyclic survey-date terms, and sampled-point effort. The coefficient on year therefore describes the average within-node temporal direction over the post-2016 interval while controlling for persistent mean differences among transects and survey context.

Uncertainty was estimated by a cluster bootstrap that resampled stable transects with replacement. All observations belonging to a selected transect were resampled together, preserving within-node temporal dependence. Reported 95% intervals are empirical bootstrap quantiles.

Recorded detection, focal frequency, and Braun–Blanquet state were available broadly across the panel. Blade length and shoot density were treated as secondary condition variables because coverage was incomplete. A segment was not classified as showing condition decline merely because one point estimate was negative; interpretation used the estimated effect, its bootstrap interval, and agreement with other state dimensions.

The main manuscript emphasizes Old, Middle, and Lower Tampa Bay because they display contrasting state-decoupling patterns. Boca Ciega Bay is retained as a spatial counterexample rather than being excluded for lack of a matching decline pattern.

# Supplementary Methods S3. Community reorganization analysis

Community analyses reconstructed the same visit and annual sampling units for four seagrasses: *Thalassia testudinum*, *Halodule wrightii*, *Syringodium filiforme*, and *Ruppia maritima*. Species-specific frequency and all-point Braun–Blanquet indices were computed using the same eligible point denominator and abundance rules as for the focal species.

For each bay segment, post-2016 within-node slopes were estimated for each species and state dimension with survey timing and point effort included. In addition, consecutive-year node-level changes were calculated so that change in *Thalassia* could be compared with simultaneous change in alternative species.

Opposing focal and alternative-species trajectories are interpreted as compositional reorganization or compensation signals. They do not identify direct competition, release from competition, or deterministic replacement. This boundary is especially important in Lower Tampa Bay, where declining *Thalassia* and *Syringodium* frequency coincided with increasing *Halodule* frequency.

# Supplementary Methods S4. External NPS Zostera state-decoupling analysis

The external ecological comparison uses the National Park Service Northeast Coastal and Barrier Network Tier-3 seagrass monitoring package. This source was originally opened under a frozen next-year recorded-loss validation contract. That endpoint terminated as non-estimable because all eligible source-positive transitions retained recorded *Zostera marina* presence.

Because the response had already been opened, subsequent analyses are explicitly post hoc. They test a separate ecological proposition: whether saturated recorded presence can coexist with substantial quantitative cover dynamics.

The reconstructed NPS panel contains 240 eligible annual transect units from 18 source identities between 2003 and 2025. Recorded *Zostera* presence was positive in every eligible unit, and focal frequency was 1.0 throughout the eligible panel. Quantitative cover nevertheless varied from 0 to nearly the full recorded scale.

For nodes with at least two annual cover observations, a within-node slope was calculated from centered year and cover values. The pooled trend was calculated from summed within-node cross-products, preventing nodes with different mean cover levels from dominating the temporal contrast. Uncertainty was estimated by bootstrap resampling repeated nodes.

Location-level pooled slopes were reported to expose spatial heterogeneity rather than imply a universal network-wide decline. Moriches Bay provides an important positive-trend counterexample.

Three single-year 2022 Tingles Island identities were flagged as possible reversed identifiers relative to the long-term naming pattern. They were not repaired. Because each appeared in only one year, they do not enter repeated-node slopes. Leave-one-location-out and equal-node sensitivity analyses are reported separately.

# Supplementary Methods S5. Next-year recorded-state instability

The exploratory early-warning analysis was motivated only after the Tampa state-decoupling pattern had been established. The endpoint is therefore internal strict walk-forward validation, not untouched prospective prediction.

Consecutive annual transitions were formed within stable Tampa nodes. A transition was eligible only when the focal species was recorded in the source year. The outcome was next-year recorded loss, defined as the focal species being unrecorded at the same node in the immediately following year. Recorded loss is an observation-state endpoint and is not equated with demographic extinction.

The final registry contained 688 source-positive consecutive transitions: 24 next-year recorded losses and 664 recorded persistences.

Two logistic-regression arms were compared. The baseline included target year, geographic coordinates, water-body identity, cyclic source-survey timing, and sampled-point effort. The quantitative arm added source-year focal frequency and all-point Braun–Blanquet state.

Evaluation was strictly walk-forward by target year. For each target year, training data contained only earlier target years. A training gate required sufficient prior recorded losses and persistences before a target year could be scored. Performance was calculated independently for each target year and summarized by macro mean log loss and Brier score. Pooled AUC is reported descriptively.

Target year 2016 remained in the primary score even though the quantitative model was strongly adverse in that year. A declared sensitivity excludes 2016 because the 2016/2017 recorded-state pulse has independent protocol concerns; that sensitivity does not replace the primary result.

# Supplementary Methods S6. Temporal-state diagnostics

## Matched Tampa quantitative state

To test quantitative temporal dependence without confounding it with local disappearance, the matched primary quantitative panel retained consecutive transect-years in which *Thalassia* was recorded in both source and target years. Frequency and Braun–Blanquet analyses used the same stable nodes and target-year walk-forward structure.

All quantitative models contained water-body identity, stable node identity, and target year. The baseline contained no previous focal state. The lag-1 arm added the immediately previous-year quantitative state. Older-history arms added information from observations preceding the source year.

## Transfer of the binary exponential-memory operator

An alternative explanation for the original binary–quantitative contrast was that the state dimensions used different history summaries. To test this, the exact exponential all-prior-state representation family used in the earlier binary analysis was transferred to focal frequency and Braun–Blanquet state.

The primary decay scale was fixed at tau = 10 years because that value had already been selected in the earlier binary analysis before the quantitative replay was opened. A broader historical tau grid was retained as a descriptive audit and could not replace an adverse primary result.

## Conditioning audit

The quantitative analysis was repeated without restricting to source–target persistent-presence transitions. This tested whether conditioning on persistence had artificially removed older-history information. Removing the restriction did not restore formal older-history support.

## Stable-site reference saturation

The most important reference audit added stable node identity to both lag-1 and older-history models while holding state representation, target years, learner family, and loss fixed. Under the original geography/bay reference, older history was formally supported for binary recorded state and frequency. Once stable node identity was saturated, no tested state dimension retained a supported tau value.

This audit changed the manuscript interpretation. Earlier history is treated as carrying persistent site-specific information as well as temporal information, rather than as a direct estimate of a long biological-memory horizon.

# Supplementary Methods S7. Response-free known-truth mechanism tests

Three simulation families were developed with their parameter grids and global decision rules frozen before outcome inspection. Their purpose was sufficiency testing: could a simple known mechanism generate the qualitative Tampa pattern under controlled truth?

## Thresholding-only known truth

The latent ecological process was strictly first-order. A single binomial point sample generated both quantitative sampled frequency and coarse detection, so the only state-dimension difference was lossy thresholding. Both responses used the same sites, years, learner, loss, and exponential-history operator.

The frozen global rule required the predicted binary-over-quantitative older-history amplification across most parameter cells and persistence levels. The rule failed strongly. Simple thresholding was therefore insufficient under the tested design.

## Slow latent suitability plus faster condition

A second family combined a slowly autocorrelated latent suitability/persistence process with a faster condition process. Both components remained first-order. The complete target pattern was rare and no frozen slow-persistence level was robust, so this two-timescale AR(1) construction also failed the global sufficiency rule.

## Persistent occupancy plus imperfect detection

A third family used a first-order occupied/unoccupied latent state, faster conditional meadow condition, and finite point sampling that created imperfect detection. This model produced more binary-biased older-history behavior than the first two families, especially at very high occupancy persistence, but only a small fraction of parameter cells reproduced the complete target pattern. The frozen global mechanism criterion again failed.

Per the predeclared hard stop, no additional response-free hidden-state simulation family was added to rescue the memory mechanism.

# Supplementary Methods S8. Environmental screens

## Response-independent water-quality source

Long-term Tampa Bay water-quality data were pinned to an immutable tbep-tech/wq-static snapshot. The upstream file contains routine monitoring observations for stations mapped to Old Tampa Bay, Hillsborough Bay, Middle Tampa Bay, and Lower Tampa Bay.

Selected variables were salinity, water temperature, chlorophyll a, total nitrogen, Secchi depth, and turbidity. Secchi observations flagged as greater-than values or effectively bottom-limited were excluded using the source-processing convention.

To prevent months or stations with more raw samples from receiving disproportionate weight, data were averaged to station-month first, then to bay-segment month, and finally to bay-segment year. Middle Tampa Bay used the declared subsegment area weighting from the source tools.

## Annual ecological coupling

Post-2016 ecological changes were aggregated to the same bay-segment × year scale as environmental exposure before testing associations. This avoids pseudo-replicating one segment-year environmental value across many transects.

The declared outcome/exposure family was corrected for multiple testing. No post-2016 association survived the familywise false-discovery criterion, and no result fell into the prespecified suggestive range.

## Seasonal hot/fresh screen

A narrower follow-up aligned monthly water quality to the target survey month. The a priori family crossed two focal quantitative outcomes, two stress summaries, and two windows. Hot exposure was maximum monthly mean temperature and fresh exposure was minimum monthly mean salinity in the preceding 3- or 6-month window.

The full eight-test family was adjusted together. Excluding target year 2017 was reported only as a protocol-motivated sensitivity. No alternative window was selected after seeing the results.

# Supplementary Methods S9. EOG-to-ecology spatial translation

The EOG Tampa endpoint was consumed before the present ecological analyses. Its prediction-facing structural block was adverse and, after all declared worlds remained viable, effectively behaved as a static node-specific geometry signature repeated across years.

The ecological translation asked two response-constrained questions rather than attempting to repair EOG.

First, the fraction of state-level variation descriptively associated with stable node identity was calculated for detection, frequency, Braun–Blanquet state, blade length, and shoot density. Occurrence and abundance levels were strongly site-anchored, whereas plant-condition variables were much less site-saturated.

Second, spatial context was made genuinely dynamic by recomputing previous-year state of surrounding transects at the four frozen EOG radii. These features were added to references that already contained stable node identity and the focal transect’s own previous-year state. The dynamic neighborhood features did not improve mean held-out prediction for binary detection or focal frequency.

A frozen follow-up decomposed spatial context into the leave-one-node-out previous-year mean within the same water body and a local-neighborhood deviation from that segment mean. The primary radius was the frozen EOG median-distance threshold, with the other radii retained as sensitivity checks. Neither segment-wide nor local-neighborhood increments passed the support rule for frequency or Braun–Blanquet state at any tested radius.

These tests rule out the simple interpretation that annual state change is primarily a one-year propagation process among monitored neighboring transects. They do not establish ecological independence or exclude spatially structured environmental forcing at other scales.

# Supplementary Methods S10. Measured persistent-site components

A response-independent physical preflight extracted point-event depth and sediment measurements before reopening focal outcomes.

Depth information was available at all 71 stable Tampa nodes and was summarized by the median and interquartile range of eligible point depths. Sediment labels were normalized across eMoF records. Point events with conflicting sediment labels were excluded rather than adjudicated. Five normalized categories were retained: mud, muddy sand, oyster, sand, and shelly sand. Sediment information was available at all 71 stable nodes.

The outcome test aggregated each focal state to a long-run node-level mean and used leave-one-node-out validation. The spatial reference contained water-body identity and geographic coordinates. Candidate physical-template models added depth, sediment, or both.

The combined depth/sediment template did not pass the frozen support rule for detection prevalence, focal frequency, or Braun–Blanquet state. The strong stable-node effect therefore cannot be reduced to these simple bathymetric and sediment-class summaries.

# Supplementary Methods S11. Benthic-light proxy

Because underwater light is a biologically plausible control on *Thalassia* condition, a response-independent exposure preflight combined visit-specific point depth with segment-level monthly Secchi depth.

For each eligible visit in the four water-quality-mapped bay segments, median point depth was calculated. Secchi depth was converted to an attenuation coefficient using the fixed relation Kd = 1.7 / Secchi. The simplified benthic-light fraction was exp(-Kd × depth). The primary exposure was the mean fraction across the six complete calendar months preceding the survey month. A three-month window was frozen as sensitivity only.

The preflight produced six-month exposure for 1,236 visits across 57 stable nodes from 1998–2025, with substantial exposure variation.

The plant-condition test used strict target-year walk-forward validation. The reference already included stable node identity, water body, year, cyclic survey timing, effort, visit depth, and the corresponding mean Secchi value. The augmented model added only the nonlinear benthic-light fraction. This design asked whether the light-at-depth interaction carried information beyond depth and bulk clarity separately.

Neither blade length nor shoot density passed the frozen primary support rule. Frequency and Braun–Blanquet state were also unsupported, and the three-month sensitivity did not change the conclusion. This result rejects the tested coarse segment-Secchi × depth proxy as an incremental annual predictor; it does not reject local optical or physiological light mechanisms.

# Supplementary Methods S12. Published compound hot–fresh stress

The final retrospective climate-stress test reused the exact published Tampa Bay reconstruction from Beck et al. rather than inventing a new threshold metric.

The pinned source artifact contains station-specific daily generalized additive model predictions derived from routine bottom temperature and salinity observations and aligned to seagrass transect intervals. Published stress thresholds were temperature at or above 30 °C and salinity at or below 25 ppt.

For each station and transect interval, maximum consecutive run length was calculated for hot days, fresh days, and days satisfying both thresholds simultaneously. Station values were summarized to bay-segment × transect-year exposure.

The focal test compared models containing stable node identity, water body, previous-year focal state, target year, marginal hot-run duration, and marginal fresh-run duration with an augmented model adding simultaneous hot–fresh run duration. The two primary plant-condition outcomes were blade length and shoot density, with a familywise primary rule fixed before opening focal responses.

The joint metric did not add supported predictive information for either primary outcome. Frequency and Braun–Blanquet secondary outcomes were also unsupported. This closed the retrospective temperature/salinity rescue line: no new threshold, lag window, or compound formula was added after this result.

# Supplementary Methods S13. External early-warning validation ledger

Two response-unopened external attempts were prospectively contracted before the current post-hoc NPS ecological comparison.

## Caribbean SeagrassNet v1

The first endpoint targeted annual *Thalassia testudinum* station state and next-year recorded loss in a Caribbean SeagrassNet dataset. Parsing stopped before model fitting because a row matching the frozen focal identity contained an empty percent-cover field that violated the predeclared numeric schema. Under the no-rescue rule, the opened dataset was not repaired and rerun as fresh validation. Model fits and predictive scores remained zero.

## NPS Tier-3 v2

The second endpoint used official NPS Tier-3 metadata to freeze permanent-quadrat identity, cover scale, missing-value semantics, and next-year recorded-loss estimability before response opening. The opened endpoint contained 240 eligible annual units and 204 source-positive consecutive transitions but zero recorded-loss events. No predictive model was fit and no predictive score was produced.

The zero-loss structure motivated the explicitly post-hoc persistent-cover analysis described in Supplementary Methods S4. That ecological comparison cannot be relabeled as prospective predictive evidence.

Together, these terminal attempts explain why the Tampa early-warning result remains exploratory despite strict internal walk-forward evaluation.

# Supplementary Methods S14. Reproducibility and claim boundary

The repository contains several machine-readable layers that define which results are current and how they can be described.

The canonical validation ledger records headline values and claim boundaries for Tampa, NPS, temporal-state audits, spatial translations, and environmental/mechanistic tests. The ecological mechanism boundary records the hard stop against additional retrospective threshold, lag, radius, hidden-state, depth/sediment, or bulk-light transformations.

The manuscript claim–evidence map links each paper-level claim to its evidence class, canonical result, display figure, and prohibited over-interpretations. The main Tampa figure-data builder runs inside the primary ecological reproducibility workflow. The external NPS figure sidecar is generated separately to preserve its post-hoc evidence status.

A manuscript-integrity workflow rebuilds the single-file manuscript from section sources and audits high-risk wording. A journal-specific *Estuaries and Coasts* workflow additionally checks Abstract length, keyword count, author–year citation punctuation, caption format, and bibliography ordering. Journal-specific figure rendering rebuilds primary and external figure data before producing EPS and 600-dpi TIFF submission files.

The repository-level stopping rule is part of the analysis rather than a housekeeping note. The initial manuscript is considered scientifically complete without identifying a new causal mechanism. A future mechanism claim requires genuinely new state information, a future monitoring wave, or a response-unopened and pre-authorized external source.

# Supplementary display inventory

**Table S1** Post-2016 within-transect state slopes and bootstrap intervals by bay segment  
**Figure S1** Full community frequency and Braun–Blanquet trajectories by bay segment  
**Table S2** Repeated NPS node cover slopes and location-level pooled trends  
**Figure S2** Target-year baseline and quantitative early-warning scores  
**Table S3** Early-warning target-year registry and model scores  
**Figure S3** Lag-1 and older-history increments with and without stable-node saturation  
**Table S4** Tau-grid support outcomes by state dimension and reference  
**Figure S4** Known-truth mechanism support frequencies across frozen simulation families  
**Table S5** Known-truth grids and global mechanism decisions  
**Figure S5** Declared post-2016 environmental association screen  
**Figure S6** Dynamic neighborhood predictive increments across frozen EOG radii  
**Table S6** Held-out-node physical site-template scores  
**Table S7** Benthic-light plant-condition predictive comparisons  
**Figure S7** Published marginal and compound hot–fresh exposure through time  
**Table S8** Published joint-stress plant-condition predictive comparisons  
**Table S9** External early-warning validation terminal ledger

# Supplementary display captions

## Supplementary Figures

**Fig. S1** Full seagrass community trajectories by Tampa Bay segment. Annual segment means are shown for frequency (**a**, left column) and the all-point Braun–Blanquet ordinal abundance index (**b**, right column) for *Thalassia testudinum*, *Halodule wrightii*, *Syringodium filiforme*, and *Ruppia maritima*. The complete trajectories provide context for the post-2016 Lower Tampa Bay compositional reorganization highlighted in the main text. Braun–Blanquet values are ordinal indices, not percent cover.

**Fig. S2** Target-year performance and event counts for the exploratory next-year recorded-state analysis. **a** Log loss of the space/time/survey-effort baseline and the model augmented with source-year focal frequency and Braun–Blanquet state under strict walk-forward evaluation. **b** Number of next-year recorded losses in each scored target year. The vertical reference marks target year 2016, which is retained in the primary analysis despite being strongly adverse for the quantitative arm. Recorded loss is an observation-state endpoint, not demographic extinction.

**Fig. S3** Effect of stable transect identity on apparent older-history value. Mean target-year score difference between the older-history and lag-1 models is shown across the frozen exponential-memory decay grid for recorded detection, focal frequency, and Braun–Blanquet state. Negative values favor older history. **a** Reference without stable node identity. **b** Same state-specific comparison after adding stable node identity. Open highlighted points denote decay values passing the frozen state-specific support rule. No state dimension retains a supported decay value once stable node identity is included; the figure therefore documents reference-sensitive historical information rather than a biological memory timescale.

**Fig. S4** Global decisions from three response-free known-truth mechanism families. Bars show the fraction of frozen parameter cells reproducing each family’s complete support pattern and the predeclared fraction required for global mechanism support. Thresholding alone, slow latent suitability plus faster condition, and persistent latent occupancy with imperfect detection all failed their global sufficiency rules. These simulations constrain simple explanations of the earlier state-history contrast; they do not identify the field mechanism.

**Fig. S5** Complete declared environmental association screens. **a** False-discovery-adjusted q values for all post-2016 annual segment-year ecological–water-quality tests across declared outcomes, exposure modes, and environmental variables. **b** Family-adjusted q values for the full eight-test pre-survey seasonal hot/fresh family. The dashed reference corresponds to q = 0.05. No displayed test crosses the declared multiplicity-controlled support threshold. The panels intentionally show the complete tested families rather than selecting the smallest nominal association.

**Fig. S6** Predictive increments from dynamic spatial context across all four frozen EOG distance radii. Mean target-year MAE increments are shown for adding previous-year water-body-wide state and for adding the finer local-neighborhood residual after segment state, separately for **a** focal frequency and **b** Braun–Blanquet state. Positive values indicate worse prediction. No segment or local-neighborhood increment passed the frozen support rule at any tested radius. The result rules out the tested one-year spatial-propagation summaries, not all forms of spatial environmental dependence.

**Fig. S7** Published Tampa Bay temperature, salinity, and joint hot–fresh stress reconstructions used in the final retrospective climate-stress test. Lines show bay-segment means of station-level maximum consecutive runs for temperature ≥ 30 °C, salinity ≤ 25 ppt, and both conditions simultaneously, using the pinned Beck et al. published daily-GAM reconstruction. The environmental sequences are shown without selecting years based on *Thalassia* responses. The downstream species-state test asked whether joint duration added information beyond marginal hot and fresh durations and found no supported plant-condition increment.

## Supplementary Tables

**Table S1** Post-2016 within-transect slopes, node counts, row counts, and node-bootstrap 95% intervals for Tampa state dimensions by bay segment after adjustment for cyclic survey timing and sampled-point effort.

**Table S2** Repeated-node and location-level *Zostera marina* cover slopes in the post-hoc NPS Tier-3 external ecological comparison. Location-level rows include node-bootstrap intervals; node-level rows expose the heterogeneous trajectories entering the pooled analysis.

**Table S3** Target-year registry and model scores for the exploratory Tampa next-year recorded-state analysis, including test-set size, recorded losses, training-set size and prior losses, baseline and quantitative log loss/Brier score, and the quantitative-minus-baseline log-loss difference.

**Table S4** Complete 16-value exponential-history decay grid for recorded detection, focal frequency, and Braun–Blanquet state under references with and without stable transect identity. The table reports state-specific scores, paired deltas, target-year wins, sign-flip p values, and frozen support-rule outcomes.

**Table S5** Frozen parameter-cell counts, replicate counts, required global thresholds, observed pattern fractions, robustness counts, and final support decisions for the three known-truth mechanism families.

**Table S6** Leave-one-node-out predictive scores for the measured depth/sediment site-template analysis. The table compares the spatial reference with the combined measured physical template for detection prevalence, focal frequency, and Braun–Blanquet state.

**Table S7** Six-month benthic-light predictive comparison for blade length, shoot density, focal frequency, and Braun–Blanquet state, with predeclared three-month sensitivity p values.

**Table S8** Predictive comparison for the exact published 30 °C / 25 ppt joint hot–fresh duration beyond marginal hot/fresh duration and local previous-year state. Primary plant-condition and secondary quantitative-state outcomes are shown together with their frozen evidence class.

**Table S9** Terminal ledger for the two response-opened external early-warning attempts discussed in the manuscript: Caribbean SeagrassNet v1 and NPS Tier-3 v2. The table records terminal status, reason, estimability where applicable, model fits, predictive scores, and whether the endpoint counts as external predictive evidence.
