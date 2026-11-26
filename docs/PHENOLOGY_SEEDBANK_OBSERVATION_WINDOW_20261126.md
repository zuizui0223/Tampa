# Reproductive phenology, local supply and open seed-bank accounting (2026-11-26 JST)

## Sources and execution boundary
Vercaemer, Scarrow, Roethlisberger, Krumhansl & Wong (2021), Aquatic Botany 175, 103444, DOI 10.1016/j.aquabot.2021.103444. Primary article Tables 2 and 3, Methods 2.4 and Results 3.3–3.5 checked via author-uploaded full-text HTML extraction: https://www.researchgate.net/publication/354307476_Reproductive_ecology_of_Zostera_marina_L_eelgrass_across_varying_environmental_conditions . Publisher landing page https://www.sciencedirect.com/science/article/pii/S0304377021000930 . Government source https://open.canada.ca/data/en/dataset/56cfea6f-aeca-47ed-94ab-c519d9e63c91 lists an XLSX and ESRI REST service; direct government page fetch failed 403 in current runtime; no original workbook or replicate-level data retrieved. New calculations executed on explicitly transcribed published values, not a new raw-data meta-analysis. Six sites in four bays, one reproductive season (2018) and winter seed-bank sampling. No animal identity or experimental access manipulation.

The previously registered Murphy & Stachowicz (2026), 10.1002/ecy.70401, remains a candidate. The exact published Methods at https://esajournals.onlinelibrary.wiley.com/doi/10.1002/ecy.70401 state April 2022 to March 2023 (16 deployments at six sites; 5,840 recovered tethers). Corrected the registry date that had been incorrectly recorded as 2023–24 in the prior memo; the old memo is retained as historical record. Dryad 10.5061/dryad.0000000d5 and Zenodo 10.5281/zenodo.14156805 were rechecked; metadata confirms original files, but direct API/download failed in this runtime (DNS/cache access failure). No new tether observations, seasonal overlap estimate, or fitted effect obtained. A. valida only tethered in Tomales Bay; no matched plant reproduction series. Their published species-specific and habitat-associated seasonal predation differences are prior art.

## Stock and timing comparison
Use source Table 2 potential seed density (peak reproductive shoot density × mean pistils per shoot × fertilization rate; not measured integrated seed release) and Table 3 winter sediment seed count. The product of displayed rounded components closely recovers the reported potential; use source-reported value unchanged. Peak date is peak *reproductive shoot density*, NOT first flowering, peak anthesis, or actual seed release. The original paper already reports seed-bank variation, PH-1 excess over potential, and proposes immigration; new work is stock ratio decomposition, observation-window contrasts and conditional predictive stress tests.

|Site|Peak date|Winter date|Lag days|Potential/m2|Winter bank/m2|Bank / potential|
|---|---|---|---:|---:|---:|---:|
|L3F|2018-07-09|2018-11-28|142|22913|1546.4|0.06749|
|PH-1|2018-07-12|2018-12-06|147|67|218.3|3.25821|
|TH shallow|2018-08-02|2018-12-10|130|540|18.2|0.03370|
|TH deep|2018-08-02|2018-12-10|130|306|36.4|0.11895|
|Sambro shallow|2018-08-09|2018-12-20|133|1920|121.3|0.06318|
|Sambro deep|2018-09-17|2018-12-11|85|1020|236.5|0.23186|

The peak dates of L3F and PH-1 differ by 3 days, whereas potential densities differ 342-fold and winter stock only 7.08-fold. Reported potential is not a true annual upper bound. PH-1 contains 151.3 seeds/m2 more than the potential proxy. IF the proxy were an exact upper bound on new local seed input, at least 69.31% of the winter stock would be unaccounted for by that source; at 2x and 3x proxy, corresponding conditional excesses 38.62% and 7.92%; at 4x no necessary excess. Cannot assign this residual to immigration rather than older seed bank or underestimated local production. No direct connectivity measured.

Within parent bays, log(B_deep/B_shallow) = log(P_deep/P_shallow) + log((B/P)_deep/(B/P)_shallow). TH: P ratio .567, B/P ratio 3.529, B ratio 2.000 with identical peak and winter dates; Sambro: P ratio .531, B/P ratio 3.670, B ratio 1.950; deep peak 39 days later and peak-to-winter lag 48 days shorter. A simple common exponential decline with equal initial ratio would require an illustrative 0.02709/day loss hazard (half-life 25.59 days) to explain Sambro's ratio difference. The same timing-only model cannot explain TH with zero lag difference. Neither is a measured seed loss hazard. Both paired depth contrasts also differ in reported herbivory (+2.52 and +2.17 percentage points), so greater recorded spathe damage does not imply smaller subsequent stock in these aggregate comparisons. No paired causal effect or statistical significance inferred. Winter stock is open; seed coats do not identify current-season seed predation. Spring germination estimates use separate samples, three pooled; no multiplication by winter stock to estimate actual recruitment.

## Exploratory out-of-group stress test
Response log(winter bank / reported potential). Compare offset-log-potential model with common intercept, addition of observed peak-to-winter lag (unconstrained and nonpositive slope), or observed spathe herbivory fraction, with leave-site-out and leave-parent-bay-out fits. The predicted quantity is log winter bank given observed potential. All six means, response-open diagnostic only; train as few as four sites per fold, no external validation. Omit PH-1 (response-selected ratio >1) only as sensitivity, not primary.

| Model | All six leave-bay RMSE (log) | Five excluding PH-1 leave-bay RMSE (log) |
|---|---:|---:|
|Common B/P ratio|1.81794|0.76212|
|Peak-to-winter lag|4.32237|0.82380|
|Nonpositive lag slope|2.01389|0.72942|
|Spathe herbivory|0.36999|0.47286|

Full-sample unconstrained lag slope is POSITIVE (+.00854/day), opposite simple loss hypothesis, and becomes -.02477/day when PH-1 omitted; unstable. Herbivory predictor's lower error is a positive association with B/P in a tiny post-hoc site panel, not proof of beneficial seed predation or generalizable prediction. Shared denominator can induce association because potential production itself covaries with herbivory, e.g. PH-1 has largest herbivory (12.34%) and smallest potential proxy. Different cohort/phenological observations, source-size contrasts, local habitat and unmeasured seed transport all confound interpretation. Do not interpret B/P as survival, run across-study pool, or use these model scores as independent support of an ecological mechanism.

## Scientific consequence
A time-only alignment of epifaunal predation to flowering is insufficient. Need local seed-release flux, immigrant seeds, viable prior stock, retained/lost seeds and repeated cohort identity measured jointly. Reproductive shoot count and fertilized pistil stock are candidate upstream states, not full demographic production. For a next empirical stage, acquire original government workbook, check observation dates, spatial sampling grain, plant phenophase, seed-bank and herbivory variable definitions, then fit an observation-aware seasonal model. Only pair animal abundance/risk with truly matched place, time, host, taxa and biological stage. No new otter evidence or pooled effect. No main/Paper A/TNC changes.

Reproduce: node analysis/195_phenology_seedbank_observation_window.cjs output.json . Calculation actually executed in JS, saved standalone wrapper not independently CI-run. Registry 68→69 and eligibility 18→19 (new stock-accounting context record, not a new independent meta-analytic effect).
