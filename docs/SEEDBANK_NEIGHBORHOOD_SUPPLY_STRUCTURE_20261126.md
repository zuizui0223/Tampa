# Seed supply at meadow scale versus local vegetation structure (2026-11-26 JST)

## Scope and exact provenance
Same Sotka et al. 2024 study, DOI 10.1111/mec.17565, https://onlinelibrary.wiley.com/doi/10.1111/mec.17565. New original height table and additional reanalysis, not independent replication. Source commit esotka/ZosteraSNPs bec412e35b8669b2850bf8f1d525e5c0ab850d00. The earlier Tampa result at ade9dbefbdaf309f7dcc082418f5cde55377547c, results/seedbank_spatial_supply_gate_20261126.json (blob e6c3d4578d4d9837b03f93b07a7e0541752f140d) retains the previously audited seedTF counts, 24 grids, 90 cores, 170 TRUE records; not confirmed viable seeds, original source inconsistencies unchanged. Height file data/perm.quad.veg.ht.2019.csv (blob 1b157699ab2f554c7ebbed2cb2431d3800cba671), density file data/perm.quad.density.2019.csv (blob 3a9ee3bf0c6a0be0fa2688d87a8cba6acc80f883). All three exact refs and hashes checked. June 643 valid positive height records, averaged per matched site-depth-permanent-quadrat-cattle-tag, then equal quadrat means per grid. 139 of 141 density quadrats have height records; WB|DP|1|28 and LP|DP|2|31 lack them; no imputation. All 24 grid height means available. August not used. Density means verified against previous grid ledger. Grid biomass mean uses available finite nonnegative June biomass entries; no imputation. Canopy index = mean vegetative shoot count per quadrat times mean height (cm), not LAI, drag, area coverage, measured seed retention or animal activity. All analysis functions actually executed in JS on source data, reproducible scripts stored, no independent CI replay.

## 1. Supply neighborhood and habitat comparison
The original article estimates approximately 100–200m effective dispersal using indirect genetic methods and documents depth-related phenotype differences. We do NOT identify a hydrodynamic dispersal kernel from these data. Illustrative Gaussian weighting of observed flowering counts within each six-grid meadow only; distance from recorded grid centroid, weights exp(-d^2/(2h^2)), normalized to sampled grids. No extrapolation across land/water boundaries or other meadows. Width 150m central scenario, 25,50,100,200,400m sensitivity; not inferred physical dispersal scale. At 150m average weight from target itself .2178, from opposite-depth sampled grids .3526 (range .2815–.4213); these are weights not fractions of actual immigrants. Equal mean across all six grids or same depth stratum are simpler alternative proxies. Withholding one meadow at a time removes all seed outcomes of that meadow from fitting; its observed flower and vegetation covariates are allowed. No seed counts used in smoothing. Outcome log1p(mean seedTF count/core), ridge on training-standardized features, unpenalized intercept, lambda 1 descriptive main with .1 and 10 sensitivities, nonnegative log predictions. No hyperparameter selection or independent test region.

|Model|All grid MSE|Measured-mass record subset MSE|Omit largest-count grid MSE|
|---|---:|---:|---:|
|Training mean|.776306|.668492|.491571|
|Depth + vegetative|.645035|.537061|.429610|
|Habitat = depth + vegetative + height|.510626|.449551|.439124|
|Habitat + local flowering|.389059|.320257|.358105|
|Habitat + same-depth mean flowering|.339489|.301318|.316498|
|Habitat + 150m weighted flowering|.331002|.381815|.179138|
|Habitat + whole meadow mean flowering|.304116|.318968|.201214|
|Habitat + local + other-grid 150m flowers|.297760|.344321|.196567|

Adding meadow mean flowering reduces MSE 40.44% relative to habitat on all grids at lambda1, improvement in all four held meadows and all tested penalties, positive pooled improvement also in mass-only and largest-grid omission sensitivity. The 150m smoothing does NOT consistently beat simple meadow mean or local flowers (mass-only vs local worsens). Across widths and penalties the model rankings vary; some low-penalty fits unstable, no best dispersal bandwidth claim. Full grid of 31 model specifications and penalties retained, not cherry-picked as validated model. Raw neighborhood-only predictor has positive regional rank association but poor within-stratum rank. Removing largest-count grid response-open, keeps its measured flowers available for other-grid predictor calculation (no outcome leakage), not independent data. One year/four sites, broad-scale association may reflect other habitat or flowering-density correlates rather than transport. No physical source/sink inference.

## 2. Distinct estimand: local contrast within same meadow and depth
Second script explicitly removes site-depth means from log-transformed predictors and log1p(seed count per core) in training groups, then fits slopes with no intercept, standardizes centered predictors using training only. Whole meadow held out. Center held predictor values within held group; held seed outcomes used ONLY in scoring observed pair differences. This estimates relative contrast/ranking not absolute seed density. Compare all within-stratum unordered pairs, dependent and small; 24 pairs total, 7 observed ties, 17 nontied. Null predicts zero differences; no hypothesis test. Lambda1 main:
|Predictor|Concordant|Discordant|Predicted ties among 17|Pair-difference MSE|
|---|---:|---:|---:|---:|
|Null|0|0|17|.457045|
|Local flowering|6|7|4|.436832|
|Vegetative count|12|4|1|.440300|
|Height|6|11|0|.612696|
|Vegetative count x height|14|3|0|.432762|
|Biomass|10|7|0|.453879|
|Flowering + canopy proxy|11|6|0|.432955|

Canopy proxy slope positive in each of four training folds (.226–.437 on unstandardized centered log feature). Compared with zero contrast, MSE decreases only 5.31%, despite rank agreement 14/17 (82.35%). All three penalties retain same direction. Mass-only subset 14/17 concordant, MSE .416270 vs null .437891 (4.94% lower); largest-grid exclusion 12/15, MSE .132926 vs null .149774 (11.25% lower). Vegetative density alone actually has lower MSE (.125993) than canopy proxy in largest-grid exclusion; adding height cannot be declared a distinct effect. Canopy does not improve all four meadows, and height alone worsens pooled local contrast predictions. Rank score and absolute error are distinct, pairs correlated and there is no independent statistical significance. Not proof of capture, drift or biotic mechanism. This local diagnostic is complementary to broad-scale forecast, not a validated combined spatial population model.

## 3. Implication and next tests
Within the same study, meadow-mean flowering gives information on broad stock levels while local structure proxy carries information about ordering of nearby seed-stock grids. This suggests a monitoring hypothesis: measure reproductive shoot density at meadow scale and replicate sediment cores within heterogeneous canopy conditions. Actual seed sources need release flux and verified parentage; actual recipient quality needs marked seed deposition, subsequent survival and genetic recruitment. Animal-induced changes in bed structure, burrows or predation could alter retention and survival, but none measured here. Avoid using these models to rank intervention sites or set 150m buffers, because no causal or external validation. Falsify by independent meadow-year, matched local and surrounding flower counts, hydrodynamic connectivity and measured seed fate; compare frozen simple mean and spatial kernel models. No pooled meta-analysis; same paper already registered, no increment in study count. No main/Paper A/TNC edits.

Reproduce:
node analysis/198_seedbank_neighborhood_supply_canopy.cjs prior.json perm.quad.veg.ht.2019.csv perm.quad.density.2019.csv output.json
node analysis/199_seedbank_within_depth_structure.cjs prior.json perm.quad.veg.ht.2019.csv perm.quad.density.2019.csv output.json
Offline wrappers verify Git blob hashes. Original functions executed; wrappers not independently CI-run.
