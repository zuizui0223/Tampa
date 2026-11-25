# Predator-stage feeding incidence and conditional intensity (2026-11-26 JST)

## Scope and primary sources
New executed published-table arithmetic, not raw-data acquisition. Holbrook et al. 2000 (Marine Biology 136:739–747, DOI 10.1007/s002270050733) primary PDF Table 2 p744 https://blanchet.grit.ucsb.edu/pdfs/holbrook-etal00.pdf ; independently crosschecked author-uploaded primary text https://www.researchgate.net/publication/225538949_Spatial_and_temporal_patterns_of_predation_on_seeds_of_surfgrass_Phyllospadix_torreyi . PDF screenshot attempted and cache miss; 2003 report reprint Table2 extraction gives .99 vs .90 conditional mean for attached Pugettia, whereas original article text, author-uploaded text and accompanying narrative (~85% unconditional) support .90. No visual resolution of reprint discrepancy; do not treat reprint as independent study. Primary conditional mean SD for released fruits Pugettia .96 (.24) reproduced in both text copies but fails necessary bounded-sample variance check. Do not manufacture or correct SD.

Four-day trials with predators individually offered spadices (two, varying fruits), dehisced fruits (eight), or seedlings (eight); measure seed consumption from seedlings, not seedling death. 225 animal-trial records across nine cells; not necessarily unique individual animals across stage experiments. Original paper already explicitly distinguished feeding occurrence and conditional magnitude. New calculation decomposes stage changes, audits aggregate variance, and standardizes denominator. No causal stage mediation, choice preference, recruitment or new independent meta-effect.

- Idotea resecata / attached: 6/28 active, conditional 0.06, unconditional 1.29%, passes necessary bound only.
- Pugettia producta / attached: 17/18 active, conditional 0.9, unconditional 85.00%, passes necessary bound only.
- Pachygrapsus crassipes / attached: 9/24 active, conditional 0.1, unconditional 3.75%, passes necessary bound only.
- Idotea resecata / released: 0/28 active, conditional undefined, unconditional 0.00%, no active feeders.
- Pugettia producta / released: 13/26 active, conditional 0.96, unconditional 48.00%, incompatible with [0,1] active sample even after rounding.
- Pachygrapsus crassipes / released: 9/25 active, conditional 0.69, unconditional 24.84%, passes necessary bound only.
- Idotea resecata / seedling: 0/25 active, conditional undefined, unconditional 0.00%, no active feeders.
- Pugettia producta / seedling: 20/24 active, conditional 0.96, unconditional 80.00%, passes necessary bound only.
- Pachygrapsus crassipes / seedling: 24/27 active, conditional 0.96, unconditional 85.33%, passes necessary bound only.

The displayed two-decimal active proportions uniquely recover integer active counts; 0.375 rounds to 0.38. Product uses exact active count/N times rounded conditional mean, rather than multiplying two rounded values. Zero active means unconditional observed zero and conditional mean undefined. For any bounded active sample x in [0,1], sample SD <= sqrt(k/(k-1)*m*(1-m)). For released Pugettia k=13, m=.96, sd=.24; even allowing half-hundredth rounding, maximal feasible SD 0.2158. The primary table reports conditional SD, but we cannot resolve this inconsistency (rounding alone insufficient). Exclude this variance from uncertainty weighting. For other cells report approximate unconditional SE only if necessary bound passes, no independent stage test. Stage-specific cohorts and covariance unresolved.

## Decomposition
For mean consumption = p(active)*m(active), symmetric accounting of change is (p1-p0)*(m0+m1)/2 plus (m1-m0)*(p0+p1)/2. No decomposition when conditional mean undefined.

- Pugettia producta, attached to released: delta -37.00 pp; incidence -41.33 pp; conditional amount 4.33 pp.
- Pugettia producta, released to seedling: delta 32.00 pp; incidence 32.00 pp; conditional amount 0.00 pp.
- Pugettia producta, attached to seedling: delta -5.00 pp; incidence -10.33 pp; conditional amount 5.33 pp.
- Pachygrapsus crassipes, attached to released: delta 21.09 pp; incidence -0.59 pp; conditional amount 21.68 pp.
- Pachygrapsus crassipes, released to seedling: delta 60.49 pp; incidence 43.63 pp; conditional amount 16.86 pp.
- Pachygrapsus crassipes, attached to seedling: delta 81.58 pp; incidence 27.24 pp; conditional amount 54.35 pp.

In both crabs, released-to-seedling consumption increase dominated by feeding incidence (Pugettia 100% of displayed arithmetic difference; Pachygrapsus ~73%). Not proof of increased natural attack rate, and no individual longitudinal records. The two crabs change relative mean order across stages, original article documents this; point estimates not statistically established rank reversal.

## Independent evidence on physical accessibility
Castejón-Silvo et al. 2019 DOI 10.3989/scimar.04892.06B, primary PDF pp351–354 https://imedea.uib-csic.es/damiajaume/DamiaJaumewebpage_archivos/PDFs/Sci%20Mar-Terrados.pdf . Web screenshot cache miss; numerical text only. Nonchoice containers 5–12 amphipods, endpoint first visible consumption or six days, minimum 21h. Open = seed cut from seedling; sealed = same type of cut surface sealed with beeswax, not literally unmanipulated intact seed. 43 tests: A ramondi 16 seed tests (combined) and 4 leaves; G fucicola 14 seed tests (combined) and 9 leaves. Split seed-treatment n not reported in text; do not infer counts from rounded percentages. Reported open vs sealed bite incidence .80/.60 and 1.00/.60, +20 and +40 pp, ratio 1.33/1.67. Separate choice tests only exclusive-feeding trials retained, so no unconditional preference probability or pooling. Published puncture means leaf .94, open 1.88, coated 2.21 N/mm2; open vs coated -14.9%, seed N 1.86 vs leaf 1.14% DW. These different assays do not identify nutrient or mechanical mediation. Already known that coat damage changes preference. No raw data, no field seedling survival.

## Comparative seed-predation bounds
Carroll et al. 2019 DOI 10.1111/1365-2745.13154, Results 3.2: surviving mud crab trials 18, 13 positive, 5 all ten; hermit crab trials 20, 4 positive, 3 all ten. For positive but not complete trials, 1–9 of ten eaten. Exact compatible conditional mean bounds: mud crab 0.446–0.938, hermit 0.775–0.975. For all trials mean bounds 0.322–0.678 vs 0.155–0.195. Feeding incidence ordering (13/18 vs4/20) differs from conditional intensity bounds (overlap; no established conditional rank). Prior analysis 170 tested total-loss clustering, not this full compatible conditional-magnitude interval. No new raw counts. Compare to Holbrook and Infantes only as different study-level mechanisms, no shared cohort or common dose/duration.

## Meta-analysis status
Registry expanded from 54 to 58 targeted records; multistage ledger from 11 to 14. Neither is a systematic search. Fishman & Orth 1996 primary abstract supports cage and crab effects but no complete numeric table obtained; Wigand & Churchill 1988 primary full table unavailable; Orth et al. 2002 habitat comparison is not a randomized animal treatment. No pooled coefficient. The new direction is joint measurement of predator feeding incidence and conditional intensity at each stage, with accessibility and alternative prey as moderators, not simply total predator abundance. Need harmonized randomized trial data, exposure length, tested food units, alternative food, predator body sizes, stage and sampling covariance. No main/Paper A/TNC changes.

Reproduce: node analysis/191_predator_stage_incidence.cjs output.json . Calculation executed in JS; standalone wrapper not independently CI-run.
