# Reproductive original-data first results (2026-11-24)

## Source provenance
Prior inventory run 45371643990, artifact 14908723858 SHA256 e51b4262e6ad0bb05e7f68c43f1cfee358e7b9008d662c33c50e7dbb7ebf27e7.
Exact-member run 45374805601, artifact 14911175880 SHA256 b5b116221241e9e603896a9dc99f66287f4707a313c12bf83ff7dd00487dc1f2, verified downloaded artifact locally. All four sources' individual members match previous hashes, despite regenerated ZIP byte differences. Source archive is public Dryad, no raw data committed. Foster version archive failed 404, dataset route failed 401, but file listing returned the two actual file IDs 792060 (README), 792061 (data/code ZIP). No raw Foster effects. Correct Kendrick genotype dataset DOI 10.5061/dryad.dfn2z3577, version 254720; metadata only.

## Kendrick original-data exploratory stage decomposition
DOI 10.5061/dryad.vhhmgqnwz; 416 flower/fruit rows, 35 site-years of 36 possible, missing Nancy Cove 2013 (not zero), no duplicated location/year/rep keys. All flower densities positive; zero fruit retained in aggregation; all 35 group mean fruit densities positive. 19/416 source ratio values differ from fruit/flower density by >.01; density rounding or original transformations are possible. Define q as ratio of group mean fruit and flower densities; do not overwrite original ratio field. Equal site-year weighting. Exact log identity logS=logF+logq; allocate covariance contribution cov(logF,logS)/var(logS) and cov(logq,logS)/var(logS). These are descriptive covariance shares, not causal explained variance, independent predictor importance or direct pollen limitation.

- Pooled 35 site-years: 0.732399 / 0.267601.
- After subtracting site-specific means: 0.588643 / 0.411357.
- 29 adjacent-year within-site changes: 0.646358 / 0.353642.
- Leave-one-site-out within-site flower share 0.542578–0.701584, ratio share 0.298416–0.457422.
- Leave-one-year-out within-site flower share 0.544604–0.658971.

This quantifies that fruit formation per unit flower density varies appreciably among years within sites. Fertilization, abortion, resources, herbivory and measurement can contribute; not a direct animal-pollination assay. No joining separate site-year transect and recruitment samples at individual level. Kendrick et al. 2023 already described stage variation; novelty of this covariance re-expression not established.

## Johnson original-data tracked seedling experiment
DOI 10.5061/dryad.2bvq83bm5; 567 rows, 21 individual identities (Quadrant + Seedling.Cell), 27 dates, no duplicate individual-date, no treatment changes, all observed survival sequences monotonic. May 3–November 3 2017 =184 days. Source metadata explicitly states close neighbours allocated to controls, other treatment selection haphazard.

| Arm | Assigned | Alive last visit | Mean restricted alive days (interval bounds) |
|---|---:|---:|---:|
| Adult neighbours removed | 10 | 5 | 109.4–113.2 |
| Adult neighbours left | 11 | 0 | 42.45–51.91 |

All assigned seedlings retained: removed 3/10 and left 1/11 died by May 15; among survivors at May 15, 5/7 vs 0/10 alive Nov 3. This latter contrast conditions on a post-treatment variable, not an unbiased treatment effect. Interval-bound computation integrates left and right survival step functions to final visit; these are measurement-interval bounds, NOT sampling confidence intervals. All-assigned difference bounded +57.49 to +70.75 days, single nonrandomized meadow, not causal population average. The general competition result is already published. This extra calculation separates potential manipulation-associated early losses from later survival and does not silently drop early deaths.

## Yu count-derived diagnostic
Yu et al. 2019 DOI 10.1002/ece3.5106: fragmented/continuous plots 271/395 sampled ramets, 214/255 observed genets; relative R higher but raw observed genet count 16.1% lower in fragmented plot. Rarefy observed continuous sample to 271 without clone-size details: E distinct genotype count lies within 175.263–205.179 given N=395,G=255, by concavity of inclusion probability vs clone size. Fragmented observed 214 exceeds maximum *expected* count; not a significance result or true spatial density. Two confounded plots, raw genotype workbook acquired but not fitted.

Reproduce with analysis/139_enhalus_rarefaction_bound.py and analysis/140_reproductive_original_stage_decomposition.py after exact source download via 138. Numerical calculations were executed locally from exact source members; new repository scripts await independent CI. Original Tampa Paper A and TNC unchanged.
