# Biotic transmission: realized grazer reduction, otter pathways and reproductive opportunity (2026-11-24)

## New computation on already source-verified ZEN data

Input: exact frozen ledger Git blob ca992c835cf369f9a69689382f6969a06eadec16 (original BCO-DMO 659737). Pair 15 site-level D+/D- contrasts for grazer biomass and epiphyte chl a. D+ is deterrent; x is negative mean log cell contrast for grazer biomass, y positive mean log cell contrast for epiphyte chl a. Equal weighting of both nutrient arms. No new raw download or site selection.

- Pearson r=.41677, exploratory two-sided site-label permutation p=.12109 (20,000 permutations).
- Spearman rho=.46071, sensitivity p=.08830.
- Descriptive paired-site percentile bootstrap r interval [.05817,.73567]; leave-one-site-out r range [.36133,.50396]. Do not select favorable bootstrap over permutation; small sample, site dependence and uncertain within-site effect precision remain.
- Of 10 sites with reduced measured grazer biomass, 9 had increased epiphyte chl a; of 5 without measured reduction, 3 also increased. Aggregate treatment effects remain verified, but cross-site effect transmission is unresolved. Not causal mediation or evidence of changed plant state.

Reproduce: python analysis/135_zen_realized_grazer_epiphyte_coupling.py. The above calculation was executed in-session from the pinned ledger; independent CI execution of the new repository script has not yet been verified.

## Literature-based contrasts, not novel discoveries

- Hughes et al. 2013 DOI 10.1073/pnas.1302805110: 30-day mesocosm and field cage experiments measured intermediate consumers, epiphytes, and plant biomass. The California cascade is already established.
- Raymond et al. 2021 DOI 10.1111/oik.07681: 21 Alaska sites, sea otter index -> crab biomass negative (estimate -.632, SE .178, p=.002); crab biomass -> epifauna load not supported (.269, SE .202, p=.215). Published model coefficients, not a newly fitted model. Original data and R code DOI 10.5063/V986FN; direct access failed in this session. Audit denominator effects and spatial confounding; do not multiply model-averaged coefficients to claim a causal indirect effect.
- Foster et al. 2021 DOI 10.1126/science.abf2343: established otters associated with allelic richness (+30%) and genotypic diversity (+6%). Original dataset DOI 10.5061/dryad.ns1rn8pt4; not acquired. Flowering was not directly measured across meadows. Genetic diversity is not observed seed recruitment.
- van Tussenbroek et al. 2016 DOI 10.1038/ncomms12980: animal-mediated pollen transfer and pollen tubes in still-water Thalassia mesocosms established. Field contribution relative to hydrophily, fruit set and recruitment distinct; no evidence for otter pollination.
- Donaher & Gittman 2021 Dryad DOI 10.5061/dryad.9cnp5hqh7: lists epiphyte, growth, biomass and regrowth workbooks in two distinct field experiments. Candidate for matched endpoints; confirm plot and experiment keys before joins.
- Ruesink 2016 DOI 10.1016/j.jembe.2016.03.022: prior experimental evidence of epiphyte-host decoupling under low eutrophication risk. No novelty claim for generic process/plant separation.

## Next hypothesis and test

Separate maintenance of established clones (food-web/light/biomass channel) from sexual recruitment and future genetic composition (disturbance/seed/pollination channel). Hypothesis: gaps can provide establishment opportunities but reduce mate availability; test absolute reproductive shoot density, fertilization, seedlings per area, gap size and prior clone structure. Do not join unlinked Alaska, BC and tropical experiments as one measured chain. Match experimental units and report missing links. Tampa Paper A and registered TNC unchanged.
