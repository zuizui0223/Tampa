# Pollinator composition versus observed behavior: held-out-block diagnostic (2026-11-25)

Davis et al. (2026), Oikos e11650, DOI 10.1002/oik.11650; Dryad 10.5061/dryad.xpnvx0kvp. The original article already reports taxon-specific changes in pollinator importance and associations of nectar foraging with fruit set. Here test incremental held-out-block predictive value, not rediscover those results or claim causal superiority of behavior. Original artifact 14925937983 SHA256 5f0bdb9f65d277e3e0e52fd4d680893090bfb91a51ff9e742f750992c1b18117 verified in current container. Five member hashes pinned in analysis/168. Executed locally Python 3.13.5, numpy 2.3.5, pandas 2.2.3, sklearn 1.8.0, scipy 1.17.0.

## 2020: plant-scale yield
Exact one-to-one join of total abundance, four deposited focal taxon counts, and yield (92 plants; 3 spatial blocks). One missing flower count excluded, n=91; all visit totals and yields positive, focal counts never exceed total. Context = herbivory/JA treatment indicators, log1p total flowers counted and number of observation dates. Then add log1p total visitors; then four focal shares of total visitors (implicit other group). Endpoint natural log total yield grams, not per-visit pollination or intrinsic fitness. Ridge with continuous features standardized within training fold. Entire block held out, no hyperparameter tuning, same rows in all models.
|alpha|context RMSE|+total visitors|+composition|
|---:|---:|---:|---:|
|.1|.7719266622|.7413615864|.7659430822|
|1|.7704733860|.7406422957|.7630549800|
|10|.7640798824|.7385795014|.7501115092|
Alpha=1 block A/B/C RMSE context .779573/.679989/.838981; total .727298/.663050/.817565; composition .837858/.671624/.772466. Total visits improves all three blocks; composition improves only C relative to total. Small single-site study with three blocks, no independent year or region test. All model fits exploratory and after source opening; penalty choices not preregistered.

## 2021: single-visit fruit set
1034 rows across 74 plants and 6 blocks, 181 fruits. Stable treatment and block per plant. Crude fruit counts/visits: Apis 25/185; Augo 17/111; Bombus 83/413; Colletes 23/76; Lasioglossum 33/249. Taxon identity is observed, not assigned. Use ridge logistic regression with treatment indicators + Julian day (standardized using training fold), add taxon indicators, then taxon x treatment. Equal-visit log loss and Brier scoring with entire spatial block/its plants held out. Complete behavior subset n=956, three categories pollen/nectar/both, no missing imputation. Main C=1:
|model|all visit log loss|complete behavior subset log loss|
|---|---:|---:|
|context|.47150|.45005|
|taxon|.46999|.44828|
|taxon x treatment|.47727|.45339|
|behavior|NA|.44430|
|taxon + behavior|NA|.44479|
|taxon x treatment + behavior|NA|.44890|
At C=.1/10 on complete subset, context log loss .44831/.45035, taxon .44534/.44903, behavior .44339/.44471, taxon+behavior .44266/.44566. Behavior-only improves context in 5/6 blocks at C=1; small increment. Taxon-by-treatment interaction does not improve predictive skill consistently. No claim of biological absence of taxon/context effects, nor equivalence. Complete behavior cases may be selected. Two annual experiments separate, no cross-year joining or transfer estimate. The 2021 importance table (370 plant-taxon rows) contains derived fruit outcomes, 12 missing importance values, and focal sums exceeding reported total visitors in 4 plants; no use as a predictor or denominator adjustment. Original paper/readme distinguish visitation counts, observed behavior, fruit-set probability and fruit weight.

## Status
Analysis executed locally from exact source bytes. CI added for independent verification; not yet confirmed. Previous global diel screen run 45412916640 failed in diel_screen at unauthenticated GitHub API HTTP 403 rate limit (original_sources job successful), not a new numerical contradiction. Earlier successful run 45408641314 remains evidence of reproduction. No new raw otter data this turn. Preserve draft PR, Paper A and TNC. No pooled cross-study effect or mechanistic identification. Next: use matched multi-stage studies to estimate context-specific transition or outcome effects, compare behavioral/functional traits against taxonomic abundance in genuinely independent systems, and prioritize held-out study validation.