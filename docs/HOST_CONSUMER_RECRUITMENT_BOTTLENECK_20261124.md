# Host–consumer coupling and life-stage-specific disturbance

2026-11-24 | Exploratory extension; outcomes previously opened. No new raw genetic or pollination model.

## 1. Challenge to a simple density-feedback hypothesis

From the original-source archived 2014 ZEN2 results at commit 12a5f0400fd1e857cdcfc828b9743c6e4cfd0128, retain signed log(1+x) A–B contrasts for 25 two-subsite region pairs (50 meadows). Original source DOI 10.26008/1912/bco-dmo.712069.1. Copy only the relevant numeric columns into a reproducible input. The earlier analysis reported correlations; this extension fits y=beta*x through the origin because reversing the arbitrary pair order reverses both contrasts. Use total unstandardized mesograzer count as primary, standardized count and richness as secondary. Resample region pairs 20,000 times (fixed LCG), and evaluate leave-one-region-out skill against zero difference; fixed slope 1 is an additional benchmark. Not a causal or time-series model. Log1p slope is not a true elasticity.

| Host x | Unstandardized count slope | Pair bootstrap 95% | LORO skill | Fixed slope 1 skill |
|---|---:|---:|---:|---:|
| shoots_dlog1p | 0.349 | -0.446 to 0.886 | -0.033 | -0.098 |
| above_dlog1p | -0.502 | -1.573 to 0.650 | -0.087 | -0.309 |
| below_dlog1p | 0.092 | -0.678 to 0.909 | -0.209 | -0.336 |

All primary intervals cross zero; all three LORO skills are negative. This challenges a universal proportional host-quantity proxy for **total** mesograzer counts. It cannot reject a response of resident species or pollen carriers separately. Aboveground biomass vs standardized count slope -1.371 is not evidence of negative causal coupling: the normalized outcome may include host amount in its denominator. Secondary endpoints not a multiple-testing adjusted family. Source data, analysis and result JSON included; JS executed and Python equivalent saved (Python not independently executed).

## 2. Opposing published disturbance pathways in the same host species

Foster et al. 2021 Science 10.1126/science.abf2343: established otter sites (20–30 years) had 30% more allelic richness and 6% more genotypic diversity than absent/recent contexts; foraging excavations proposed to facilitate sexual recruitment. This is a natural occupancy gradient, not randomized digging. Foster's 2021 dissertation, https://dspace.library.uvic.ca/server/api/core/bitstreams/b72a2d8b-f681-48bf-ad10-78819e5afc1d/content, is a pre-final version with different summary values; do not combine with final Science estimates. It explicitly notes flowering rates were not measured. PDF screenshot retrieval failed; no site-level extraction from ambiguous thesis tables.

Kollars & Stachowicz 2022 Ecology 10.1002/ecy.3710: replicated two-year clipping experiment simulating goose grazing. Published mean new genets/plot 1.22 (0X) vs 0.11 (2X repeated treatment), a descriptive ratio 0.0902 and relative reduction 90.98%; no significant clipping effect on extinction; at least 7 of 36 colonization events were consistent with vegetative spread/rafting. No seedlings observed in nine seed traps over 24 months. Flowering effort was reduced or delayed, but the authors also discuss alternative colonization routes. One season of severe clipping followed by a recovery year (4X) did not differ detectably from controls in final colonization, despite lower flowering; cannot treat it as a monotonic dose curve. The original study already contrasts Foster and proposes timing, facilitation and establishment mechanisms. Our novelty cannot be that disturbance has different effects on diversity.

Gross 2024 DOI 10.1111/geb.13918 describes temperate (30.4–67.3 N) ZEN site-level variation in peracarid vs gastropod dominance and traits; its 49 sites are largely the same 2014 ZEN survey, NOT independent validation. Direct development occurs also in gastropods. Taxonomic group is not a verified dispersal or host-dependence trait.

## 3. Revised stage-specific recruitment bottleneck hypothesis

Represent sexual recruitment as G_sex = (S_local + S_import) * p_retention * p_establishment * p_survival. Total genet gain also includes vegetative arrival and expansion. A gap can increase establishment while reducing local adult seed production; a leaf-only disturbance can reduce seed production without creating bare sediment. Recurrent disturbance can kill new recruits, and timing relative to flowering and establishment matters. For equal imported seed supply=0 and other probabilities unchanged, if local seed input halves, establishment probability must double to compensate; this is illustrative algebra, not a fitted threshold. With imported seeds and vegetative arrivals, even this simple product must be expanded.

A decisive experiment should cross adult canopy clipping vs substrate-gap creation independently with seed addition and time since disturbance, matching starting adult genets and controlling seed source. Measure flower/seed output, seed deposition, genotyped sexual vs vegetative recruits and genet loss. If seed supplementation rescues clipped plots, source limitation is supported; if gap creation only helps where seed input is high, establishment and source are jointly limiting. Include no-disturbance/sham control. In Thalassia, a separate flow × animal access × flower density experiment tests pollen delivery; no extrapolation of its animal pollination to Zostera.

## 4. Acquisition and evidence limits

Gross Dryad 10.5061/dryad.np5hqc00p lists Code_and_data.zip and README.md, including peracarid diet/development/size, species abundance and site environment. Foster Dryad 10.5061/dryad.ns1rn8pt4 lists no displayable files. Kollars raw data/code DOI 10.5281/zenodo.6011003. DNS in container failed; BCO CSV and Zenodo web fetches failed; no original archive read here. Use these as acquisition targets, not zero effects. No new macro causal result or meta-analysis; no manuscript changes.
