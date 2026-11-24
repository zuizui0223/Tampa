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

## Hard limitations

- Hovel 2021 already tested the edge × shoot thinning interaction. This is a reanalysis, not an independent new positive ecological finding.
- 2014, 2015 and 2011 source cohorts are distinct; combining plots from different years as if simultaneous is pseudoreplication.
- 2015 tethering records available prey consumption risk, not predator identity and not an ecosystem ecosystem-level resilience endpoint.
- If edge has lower predation than interior despite lower eelgrass density, the simple “more shoots = more consumer refuge everywhere” explanation is falsified at the scope of this design. Do not imply that patches are all harmful.
- No carbonate, TNC, plant survival, long-term meadow collapse or interspecific facilitation necessarily follows.
