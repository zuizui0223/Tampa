# Reproductive interaction gates: animal pollen transport, consumer release and genetic renewal

2026-11-24 | Response-open exploratory arithmetic and source audit; NOT independent validation, NOT a meta-analysis, NOT evidence of an otter-to-pollinator chain.

## Three separate empirical systems

1. **Thalassia testudinum, Mexican Caribbean:** van Tussenbroek et al. 2010 (10.3354/meps08870) manipulated male flowers and pollen supply in the field at Puerto Morelos. In 2008, ~50% male removal reduced fruit set from 0.86 to 0.60 (two removal and two control plots). In 2009, pollen addition increased fruit set from 0.65 to 0.91 (two plots, treatment/control flowers within plots). Fresh male flower density per 4 m2 was 15.0 in 2008 and 8.2 in 2009. Counts are published rounded means/proportions, not independent flower-level observations. 2012 (10.3354/meps10072) documents visits and pollen/mucilage consumption; 2016 (10.1038/ncomms12980) demonstrates pollen transfer and pollen tube formation in fauna-present still-water tanks. No matched field factorial of flow × fauna × fruit set identified. The 2016 paper already proposed reproductive assurance and longer effective dispersal; do not claim that idea as new.
2. **Zostera marina, California / Alaska:** Hughes et al. 2013 (10.1073/pnas.1302805110) documented an otter–crab–mesograzer–epiphyte–eelgrass cascade. Raymond et al. 2021 (10.1111/oik.07681) did not support crab–epifauna coupling across 21 southeast Alaska sites; a full cascade is not universal. Neither study established animal pollination of Zostera.
3. **Z. marina, British Columbia:** Foster et al. 2021 (10.1126/science.abf2343) reports allelic richness +30% and genotypic diversity +6% at meadows occupied by otters for 20–30 yr vs absent/recently occupied. Digging/disturbance and sexual recruitment are the proposed mechanism; no animal pollen-transport evidence. Gross et al. 2024 (10.1111/geb.13918) reports that eelgrass allelic richness is positively associated with peracarid relative dominance vs gastropods in a separate 49-site survey (50 surveyed). The additive allelic-richness + ocean-basin model has R2=0.36; association is not causal and cannot be multiplied by Foster effects to derive a mediated effect.

## Executed arithmetic from published aggregates

For an illustrative independent encounter model assume fruit set F = 1-exp(-lambda), common non-pollen ceiling 1, and lambda proportional to male flower density at constant transport. Calibrate lambda_2008 = -log(1-0.86). With removal fraction r=0.50, F_pred=1-exp(-lambda_2008*(1-r)). With natural male density ratio q=8.2/15.0, use F_pred=1-exp(-lambda_2008*q). These assumptions are not estimated from independent data; no inference/CI, no proof of density-only causality, no claim that shoots map one-to-one onto flowers.

| Contrast | Published observed | Recomputed descriptive result |
| --- | --- | --- |
| 2008 male removal | 0.86 -> 0.60 | RR 0.697674; -26 pp; implied lambda ratio 0.466042; density-only prediction 0.625834; observed minus predicted -0.025834 |
| 2009 supplemental pollen | 0.65 -> 0.91 | RR 1.4; +26 pp; proportional deficit 1-0.65/0.91 = 0.285714 |
| 2009 control vs 2008 control | 0.65 vs 0.86 | density ratio 0.546667; implied lambda ratio 0.533958; density-only predicted 0.658637 |
| 2012 Fig. 2 visits on 11 May 2009, single paired male-flower recording | crustaceans 557 vs 113; polychaetes 94 vs 71 | ratios 4.9292 and 1.3239, ratio-of-ratios 3.7231; no inferential test, repeated visits not independent individuals |

The 2008 and 2009 manipulations are different designs in different years, and seed set is a distinct outcome. The 2009 density calculation is an illustrative cross-year check only: density of female flowers, hydrodynamics, resources and anthesis can differ. Any residual is uninterpretable as an animal contribution.

## New cross-layer hypothesis: guild-dependent reproductive renewal

Distinguish three gates: (i) flower supply and pollen delivery, (ii) establishment microsites/seed recruitment, (iii) genetic retention and demographic persistence. A consumer can modify one gate without modifying others. For Thalassia, test whether animal transport adds to or compensates for hydrodynamic delivery across flow and floral density, using actual fruit/seed set. For Zostera, test whether predator disturbance affects sexual recruitment independently of epiphyte control, and whether genetic diversity predicts particular epifaunal traits after geography and plant structure are controlled. No single causal chain assumed across species or oceans.

A second hypothesis is temporal interaction partitioning: diurnal florivorous fish and nocturnally active small invertebrates may impose opposing fitness consequences on floral timing. Night opening and fish avoidance were already discussed in 10.3354/meps08870 and 10.1007/s10682-012-9600-4, and nocturnal animal pollination was proposed in 10.1038/ncomms12980. New estimand: incremental fitness benefit of nocturnal vs daytime release under independently manipulated fish access and small-fauna access, conditional on flow, pollen viability and equal pollen supply. No evidence of selection on timing from observational visitation alone.

## Prospective analysis contracts

- **Pollen experiment:** blocked independent tanks or plots; factorial fauna access × measured flow regime × male-flower density. Primary endpoint fruit set per eligible female flower (binomial mixed model with tank/plot as experimental unit). Secondary pollen tube count, seed set, pollen origin/paternity. Pre-specify risk-difference interaction between fauna access and flow, distinguishing absolute effect from relative effect under near-zero baseline. Include sham mesh/flow and pollen viability controls. Track direct flower/seed consumption.
- **Functional overlap:** obtain the 2012 flower-visitor species list and 2016 pollen-carrier records; match accepted species names via WoRMS against geographically relevant epifaunal trait tables (exact species only for confirmed functional overlap; genus/family match = candidate). Separate visitation, pollen attachment, effective pollen transport and algal consumption. Compare trait distributions vs the local available animal pool; no shared genera -> direct claim. Northern Zostera assemblages are comparison/trait priors only, not a local Thalassia pool.
- **Otter analysis:** raw site-level genotype and occupancy data; compute sample-size-standardized allelic richness and clone-corrected genotypic richness. Compare absent/recent/established occupancy within geographic regions; account for depth, meadow size, temperature, latitude and spatial nonindependence. Disturbance/pit density and seedling recruitment measured at same site/time are required for mediation. Explicitly distinguish allele vs genotype renewal; only occupancy categories cannot establish a continuous dose-response.
- **Gross 2024 extension:** use trait and site files to test whether plant genetic diversity is associated with abundance-weighted mobility/feeding traits within peracarids (not merely peracarid vs gastropod replacement), accounting for basin, latitude, habitat structure and trait-data coverage. Compare geographic block CV; test genus/family and species-level sensitivity. No pollen function coding unless species-specific direct evidence. The published taxonomic association is not new.
- **Tampa:** no reproductive or animal data; existing 15-site ZEN manipulation estimates epiphyte/grazer effects, not seedling recruitment. Do not merge unrelated sites or infer reproductive failure from shoot density.

## Original-data acquisition gates (not fitted this turn)

| Source | DOI / locator | status |
| --- | --- | --- |
| Foster | 10.5061/dryad.ns1rn8pt4 | Dryad metadata confirms microsatellite, occupancy and environment data; file listing returned no displayable files; runtime DNS unavailable; no raw-data fit |
| Gross | 10.5061/dryad.np5hqc00p | Dryad lists Code_and_data.zip and README.md, with peracarid feeding and development traits, site abundance and environment; runtime DNS unavailable; no raw-data fit |
| 2012 flower visitors | 10.3354/meps10072 | original article/abstract available; supplementary list not retrieved; no overlap estimate |
| 2016 mesocosms | 10.1038/ncomms12980 | published endpoint and design available; no raw tank-level count table verified |
| 2010 field experiment | 10.3354/meps08870 | published design and aggregate proportions inspected; PDF screenshot retrieval failed; no plot-level reanalysis |

Next executable priority: obtain Gross raw zip, validate schemas and site/trait IDs, then within-peracarid trait analysis. In parallel obtain Foster raw files and Caribbean species list. Do not interpret inaccessible data as null effects.
