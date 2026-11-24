# Global eelgrass foundation–consumer reciprocity: independent source and hypothesis gate

Date: 2026-11-24. Status: **original-data exploratory reanalysis; not a novel causal feedback or independent study replication**.

## An empirically tractable twist

PR #170 reaggregated a 2011 ZEN experiment at 15 eelgrass sites: grazer deterrence reduced the measured grazers and increased epiphyte chlorophyll-a. An alternative interaction direction is that eelgrass habitat structure itself modifies the exposure of those same functional-guild mesograzers to predators. That makes a proposed **two-way ecological association**: mesograzers remove epiphytes on eelgrass, while standing eelgrass modifies the grazers' predation risk.

**These are two distinct published experimental years and cannot demonstrate a reciprocal feedback loop or an actual long-term population dynamic** unless co-located and experimentally linked partner/plant time-series are acquired.

## Sources and existing novelty boundary

- **2011 ZEN** (already reaggregated in PR #170): [BCO-DMO 659737](https://www.bco-dmo.org/dataset/659737), published Duffy et al. 2015 DOI [10.1111/ele.12448](https://doi.org/10.1111/ele.12448). Original 15 sites x 40 grazer-deterrent × nutrient plots = 600.
- **2015 ZEN2 consumer protection**: [BCO-DMO 724015](https://www.bco-dmo.org/dataset/724015), [dataset DOI 10.26008/1912/bco-dmo.724015.2](https://doi.org/10.26008/1912/bco-dmo.724015.2), directly downloadable original `crustacean_survival.csv`. Experiment: **17** biogeographic sites, eelgrass patch edge vs interior crossed with shoot reduction **ambient / 50% / 80%**; four 24-hour tethering rounds; locally collected amphipods/isopods. Original records include a binary Status (0 alive, 1 eaten), shoot density, epibiont and consumer biomass.
- **Published conclusion, not novel:** Hovel et al. 2021, *Ecology* [10.1002/ecy.3316](https://doi.org/10.1002/ecy.3316) already reported that patch edges were generally **less risky**, not more risky, than interiors; shoot thinning did not robustly modify this edge effect. It is a direct negative control on any tempting new general claim that removing eelgrass must always increase consumer predation. Do not override its inferential results by mining subgroups until a favorable effect appears.
- **2014 ZEN2 50-site meadow structure snapshot**: [BCO-DMO 712069](https://www.bco-dmo.org/dataset/712069), [DOI 10.26008/1912/bco-dmo.712069.1](https://doi.org/10.26008/1912/bco-dmo.712069.1), same network but different times, units and observational design. Contains eelgrass shoot density, above/below dry biomass, epifaunal community and environmental conditions. Not a 2015 experimental host outcome.

## Fixed pre-analysis priorities

**Primary 2015 *descriptive replication*, no reranking or exploratory treatment rescue:**
1. Inventory exact 17-site source headers, status and treatment conventions, plot/trial duplicates, missing values, and source SHA.
2. Reconstruct **six full factorial cells per site**: edge/interior × ambient/fifty/eighty. The analysis unit for global summary is site, not a tethered individual (tethers may share the same physical plot).
3. Calculate standardized 24-hour consumer **predation risk** as per-site cell frequencies from Status 0/1, and equal-site **edge−interior**, **50%−ambient**, **80%−ambient**, and edge × thinning difference-in-differences. Report raw uncertainty, leave-one-site-out bounds and *both* positive/negative site counts. No interpretation as free-ranging consumer survival.
4. If any source has unrecognized statuses, plot/trial dependence, absent six cells, or insufficient per-cell sample sizes, fail closed. Only use declared original cohort and no post-outcome recoding.

**Independent 2014 snapshot**: determine exact measured columns for same-row seagrass above+below dry biomass, grazer diversity/biomass, epibionts and environment. If present, record within-site observational plant–consumer association, without claiming host→consumer protection or experimental causation.

**Optional response-open ecological question**: 2011 ZEN grazer suppression of epiphytes and 2015 ZEN2 predation data might have overlapping site codes, but 4-year separation, different plots, and guild/campaign differences mean no reciprocal causal feedback identification. First compute the code overlap and environment comparability; don't link by plot IDs across years.

## Source-verified result: 2015 ZEN2 17-site predation experiment

**Authoritative reaggregation:** [Actions run #45328106589](https://github.com/zuizui0223/Tampa/actions/runs/45328106589), original BCO-DMO CSV SHA256 `3de12972e709f6a856e60e6d8cbf6fd81cf824edb7d907c453301e3e42d596fb`, 2,666 tethered prey, 17 sites, **2,002 recorded consumed**, 664 alive. The six edge/interior × ambient/50/80% thinning cells were present and had >=5 original trial records in every site. Trial and plot nesting are not independently identifiable from the fields and should not be fitted as 2,666 independent meadows.

The *site-equal* contrasts (each of 17 sites has one contrast) are percentages of **recorded tethered predation**; bootstrap intervals are 5000 site-resample percentile intervals, exploratory, not the original Hovel et al. 2021 adjusted model.

| Contrast (all 17 sites; mean site risk difference) | Estimate pp | 95% site bootstrap pp | Negative/positive/zero sites |
| --- | ---: | ---: | --- |
| 50% shoot removal minus ambient | +0.34 | −2.51 to +3.06 | 7 / 6 / 4 |
| 80% shoot removal minus ambient | **−1.54** | −5.14 to +1.71 | 7 / 6 / 4 |
| Edge minus patch interior, average thinning levels | **+1.06** | −1.18 to +3.33 | 6 / 8 / 3 |
| Edge × 80% thinning difference-in-differences | **−0.73** | −5.36 to +3.30 | 6 / 7 / 4 |

Three sites (CR, FR, NC) had **100%** recorded predation in this 24-hour tether assay, which causes saturation and limits treatment discrimination. At such sites a zero difference is not evidence for a biological null mechanism. Note that the published Hovel et al. 2021 model estimated *adjusted* edge effects, and the authors reported lower predation at edges in most sites; the unadjusted equal-site summary does not recover a robust general edge effect. It must not be described as a contradiction or new discovery.

The direct ecological constraint is that **heavy experimental shoot thinning did not consistently increase the 24-hour observed prey predation endpoint across this already-published network**. Eelgrass shoot quantity alone cannot be asserted to universally protect mesograzers; patch position, predator identity, local physical architecture and epibionts may matter but the present descriptive contrasts do not isolate them. This study does **not** show that consumers have no benefit from seagrass.

## Source-verified result: 2014 25 region-code paired-subsite observational data

An independent original source [BCO-DMO 712069](https://www.bco-dmo.org/dataset/712069) has 50 subsite records, exactly 2 within each of 25 region/site codes (not 50 independent estuaries). Original CSV SHA256 `c2af785e48aa76f88834e6c96ab69f49f85feb0918a89f9ec0585680cb170034`. Both Zostera above/below biomass, shoot density, epiphyton load, and original count and standardized mesograzer indices are observed. Cross-subsite differences were calculated for each region-code A/B pair, using log(1+x) within metrics. N=25 paired region-code contrasts, except epiphyton N=24.

| Correlation of within-code **aboveground Zostera biomass difference** with consumer/epiphyton difference | Pearson r | 5000 pair-bootstrap 95% |
| --- | ---: | ---: |
| **Standardized** grazer abundance (`Mean_Std_Total_Abund_Mesograzers`) | −0.544 | −0.776 to −0.157 |
| **Unstandardized** grazer counts (`Mean_Total_Abund_Mesograzers`) | −0.199 | −0.569 to +0.328 |
| Mesograzer richness | −0.145 | −0.626 to +0.297 |
| Epiphyton index | −0.048 | −0.411 to +0.273 |

**Important denominator robustness gate:** the strong negative plant–grazer correlation is present only for the **standardized** abundance indicator. If this index is normalized by eelgrass biomass (as the original sampling methods suggest), it can display an artifactual negative association when compared against host biomass by construction. The effect shrinks when switching to the source's unstandardized grazer count and its exploratory interval overlaps zero. **Not proof that the standardized trend is 100% an artifact, but no evidence of a causal plant→grazer negative interaction**. The choice of the unstandardized metric as a negative control was made **after** seeing this surprising negative association, so it is post-hoc. The 2014 surveys are observational and cannot be used to infer reciprocal feedback dynamics or true rhizome buffering.

Pinned exact results (including per-site records, every pair contrast and source-provenance): `results/zen2_2015_site_predation_source_verified_20261124.json`, `results/zen2_2014_25region_state_consumer_source_verified_20261124.json`. The workflow re-fetches both public sources and compares all numerical outputs exactly to these pinned ledgers.

## Ecological synthesis: candidate asymmetry, not an identified feedback

- **2011 ZEN grazer manipulation (PR #170):** reducing grazer access increases epiphytic chlorophyll on eelgrass; a direct grazer→epiphyte process effect.
- **2015 ZEN2 habitat manipulation (this PR):** reducing eelgrass shoot density does not monotonically increase tethered grazer predation, so an equally strong *plant biomass→grazer protection* return path is not identified from this endpoint.
- **2014 separate observation (this PR):** simply normalizing consumer counts by host biomass can change qualitative abundance relations; this demands explicit denominators before any cross-year feedback comparison.
- **None of the two experiments measures the other direction at the same plots/time.** Thus a two-way positive feedback, net balance, hysteresis or conservation restoration benefit is still not proved.

An ecologically meaningful experiment for the remaining hypothesis would cross **measured grazer-access changes with permanent eelgrass canopy complexity** at independent matched plots, measure epiphyte load, free-living grazer population fate and host growth together, and replicate that interaction across independent seagrass habitats. The requirement is not merely another weather correlation or more historical non-detection decompositions.

## Hard limitations

- Hovel 2021 already tested the edge × shoot thinning interaction. This is a reanalysis, not an independent new positive ecological finding.
- 2014, 2015 and 2011 source cohorts are distinct; combining plots from different years as if simultaneous is pseudoreplication.
- 2015 tethering records available prey consumption risk, not predator identity and not an ecosystem ecosystem-level resilience endpoint.
- If edge has lower predation than interior despite lower eelgrass density, the simple “more shoots = more consumer refuge everywhere” explanation is falsified at the scope of this design. Do not imply that patches are all harmful.
- No carbonate, TNC, plant survival, long-term meadow collapse or interspecific facilitation necessarily follows.
