# Reproductive trophic cascade: prey identity, seed accessibility and dispersal gates

2026-11-24 | Published aggregate arithmetic and hypothesis refinement. No fitted otter-to-seed recruitment pathway or pooled meta-analysis.

## Species-level link newly identified

- Jeppesen et al. (Biological Invasions 27:33, 2025; online 2024-12-10), DOI 10.1007/s10530-024-03467-3, documents sea otter (Enhydra lutris nereis) consumption and suppression of Carcinus maenas in Elkhorn Slough. Approximate yearly consumption 120,000; conservative extrapolation 52,000–67,000. Long-term observations, not a direct count of annual consumption. Otter-inaccessible tidal restrictions retained high green crab abundance. Original data DOI 10.7291/D1469B (Fig3a.xlsx, Fig3b.csv, Fig3c.xlsx, Fig5.csv, README).
- Infantes et al. 2016 DOI 10.1371/journal.pone.0168128 documented seed consumption by the identical crab species, C. maenas, on Zostera marina in Sweden. In 24-h trials seed consumption was 56%, 20%, and 0% at 0, 1 and 2 cm burial. The field predator-exclusion experiment yielded 14% vs 0.5% seedling establishment after eight months, a descriptive 28-fold ratio of rounded published values. The field cages altered predator access, not a specific otter pathway. The authors already proposed direct seed predation and indirect mesograzer suppression as dual crab feedbacks, so do not claim this dual crab mechanism as new.
- Both species-level links are supported in different regions. Elkhorn Slough green crab seed consumption and recruitment mediation have NOT been measured by these two studies; local predation on seeds, prey size structure, functional response and seed availability must be checked. The classic Hughes et al. 2013 cascade concerns primarily other crab species. Do not multiply Swedish exclosure ratios by Californian CPUE differences.
- Raymond et al. 2021 (10.1111/oik.07681) found a negative sea otter–crab association in Alaska (reported coefficient -0.632, SE 0.178, p=.002) but not the expected negative crab–epifauna link or pit–host biomass association. Their pit counting criterion was diameter >~30 cm, not a measured mean pit size. A reproductive cascade may therefore be distinct from vegetative biomass response; this is not evidence for a seed cascade in Alaska.

## Independent source, microsite and accessibility evidence

Johnson et al. 2020 (10.1111/1365-2745.13362) found seed additions and local adult removal promoted establishment and survival (both original tests p<.001), with strong temporal and spatial context dependence; data DOI 10.5061/dryad.2bvq83bm5. Reusch 2006 (10.1111/j.1365-294X.2005.02779.x) found greater new-genet occurrence with gap disturbance but no detectable treatment effect on overall clonal diversity; initial diversity explained 68–91% of variation. No direct equivalence between new-genet recruitment and diversity.
Livernois et al. 2017 (10.1016/j.aquabot.2017.05.006) found fragmented beds held fewer seeds even though flowering effort did not differ detectably. Li et al. 2018 (10.1016/j.aquabot.2018.07.008) reported seed rain of 1634 inside vs 515 downstream and 203 perpendicular at 8 m away (seeds/m2). Ratios 0.315 and 0.124; if seed supply alone falls to these fractions, subsequent conversion probability must rise 3.17x or 8.05x to match the initial number of recruits. These are arithmetic thresholds for a simple product model, not causal fragmentation effects; inside is not an edge baseline.
Meysick et al. 2019 (10.1371/journal.pone.0222020) demonstrates seed retention via shoots and bivalve-induced sediment scouring under flow. Other bioturbation studies (10.1016/j.seares.2012.04.006) distinguish shallow burial from excessive burial; avoid treating deeper burial as uniformly beneficial. Carroll et al. 2019 (10.1111/1365-2745.13154) already discusses seed-predator refuge and the joint roles of patch size, cover and seed supply.

## Executed arithmetic and falsifiable interaction

For hypothetical crab predation hazard h(d)=-log(1-q(d)), assume proportional scaling by remaining crab hazard fraction c and all other hazards fixed. Conditional 24-hour seed survival is (1-q(d))^c. For the reported rounded laboratory means:

| burial cm | baseline survival | half hazard survival | gain pp | complete removal gain pp |
|---:|---:|---:|---:|---:|
| 0 | 44.0% | 66.3% | 22.3 | 56.0 |
| 1 | 80.0% | 89.4% | 9.4 | 20.0 |
| 2 | 100.0% | 100.0% | 0.0 | 0.0 |

These values are calculated scenarios, not observed otter effects. The zero observed consumption at 2 cm is not proof of zero true risk. The proportional-hazard assumption is not fitted. The 8-month field ratio is a different endpoint and scale; no pooling. Exact source summary inputs and computed output are archived; arithmetic checked independently in the current Python runtime.

Novel candidate: the *reproductive* contribution of an apex predator is gated by physical accessibility of propagules, in addition to prey identity. Shallow deposition and high local seed-predator exposure predict higher marginal benefit of predator reduction; effective burial can substitute for predator control at the seed survival stage. Severe burial, erosion or seed limitation may independently make the benefit small. Predator effects on adult growth and sexual recruitment need not covary. No claim of first discovery of burial protection, seed limitation, or context-dependent trophic cascades.

## Next empirical decision gates

1. Acquire original Infantes S1–S4 and Meysick S1, Jeppesen Dryad data and Johnson source tables. Source and schema audit only: do not assume rows are independent seeds or treat CPUE as true density.
2. Fit original factorial depth × predator identity at tank level, binomial counts with overdispersion and complete-separation handling, then quantify depth-dependent marginal risk differences. For field cages distinguish transport protection, predator access and seed burial; repeated plots not independent.
3. With Jeppesen site/year data, test within-estuary access/CPUE contrast with trap effort and tidal restriction covariates; time dependence and shared environmental changes preclude simple causal claims. This is not validation of seed fate.
4. Falsification in Elkhorn Slough: randomized seed additions × standardized burial × local crab exclosure across matched accessible and inaccessible sites. Directly measure seed fate, germination and genet recruitment, compare crab species and size classes. Use otter occupancy as observational moderator; require locally observed seed consumption before attributing otter effects to this pathway.
5. Keep the Caribbean animal-pollination branch separate from Zostera. The common principle is life-stage-specific biological interactions modified by physical access and resource supply, not an otter-to-pollination causal chain.

## Retrieval status

Direct runtime DNS failed for Dryad/Zenodo; PLOS supplement and Dryad API web fetches failed. Public file listings and source DOI links were verified; original files were not accessed locally. A branch-scoped source acquisition workflow has been defined, with HTTPS, size caps, file hashes, worksheet structure inspection and explicit stops. A workflow run and verified manifest are required before calling any raw source acquired. The prior manuscript and main branch are unchanged.
