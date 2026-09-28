# Tampa ecology manuscript — Methods draft v1

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
