# Marine pollination: transport range, capture incidence and reproductive output (2026-11-25)

## Scope and provenance
Two new published-table recalculations, executed locally using standard-library Python with explicit arithmetic closure checks. Not individual-level raw data. No new fitted model, p-value, causal effect, meta-analytic pooled estimate, or changes to Paper A/TNC. Follow-up on analysis/175 and the animal/flow question. Original 2016 animal-pollination figure still inaccessible as an image (Nature, publisher PDF screenshot and PMC access failed; local DNS unavailable); no heatmap cells transcribed or inferred. Wiley supplement filename ece32309-sup-0001-Supinfo.docx was identified but not downloaded. Source table text crosschecked across publisher/PMC and PDF extraction. PDF screenshot requests returned cache misses.

## Thalassia testudinum: dispersal versus capture
Van Tussenbroek et al. (2016), Ecology and Evolution, DOI 10.1002/ece3.2309, Table 2, 2006 pollen trap trials. Use dates as in table (text refers to April 27 and May 11 in discussing facing direction; not silently harmonized). 120/120/100 traps, positive traps 16/17/23, captured grains 67/57/71, effort-corrected mean dispersal distances 2.02/1.15/.66 m. Back-Reef both trials use same 0.4–8 m radius design; Mid-Lagoon has different 0–2.4 m design. Trials in natural environment, daytime artificial release, not exclusion of fauna. Traps are not female flowers. Observations within trial share the release and water movement. No independent trap-level inferential tests or water-only causal interpretation.

| trial | capture-positive fraction | positive-trap mean | all-trap mean |
|---|---:|---:|---:|
| Back-Reef 26 Apr | .133333 | 4.187500 | .558333 |
| Back-Reef 10 May | .141667 | 3.352941 | .475000 |
| Mid-Lagoon 25 May | .230000 | 3.086957 | .710000 |

Same-design Back-Reef change May minus April: mean distance ratio .569307; positive incidence +.008333 (0.8333 pp); mean positive count ratio .800702; overall count ratio .850746. Exact mean count difference -.083333 grains/trap = +.031419 incidence component - .114752 positive magnitude component. Arithmetic only. Pollen neighborhood area 2.76 vs10.80 m2 is not proportional to mean distance, because source uses dispersal variance and correction factor. Do not equate spatial range, capture incidence, delivered dose, fertilization or seed production. No common-trap pairing inferred.

From aggregate G grains in K positive traps, sharp bounds for number with >=t grains are [I(G>K*(t-1)), min(K,floor((G-K)/(t-1)))]. For >=5 grains, 1–12, 0–10, 0–12 traps respectively. For >=10, 0–5, 0–4, 0–5. These are mathematical data-identification bounds, not confidence intervals, and no chosen threshold is a biological fertilization cutoff. Dose distribution not recoverable from Table 2.

## Zostera noltei: reproductive structure versus estimated output
Van Tussenbroek et al. (2016), Oecologia 182:595–609, DOI 10.1007/s00442-016-3665-7, Table 4, 10 Sep 2014. Original paper already reported lower density-dependent fruit set in a fragmented meadow and an Allee-effect interpretation. These new arithmetic ratios do not discover or prove that effect. 4 meadow contexts, 60 cores in total (10/20/10/20); three continuous meadow sections at Oostdijk, one fragmented at Goese Sas, so not independently replicated fragmentation treatments. Total spathes include decayed stages; not simultaneous open flowers. Seed production is authors' annual estimate from total spathes × seed-bearing fruits/spathe, assuming temporal constancy and negligible further spathe production, NOT directly counted annual seed yield. Ratios of reported means, not individual probabilities.

| context | reproductive biomass (g DW/m2) | reproductive shoots/m2 | total spathes/m2 | estimated annual seeds/m2 |
|---|---:|---:|---:|---:|
| Channel | 1.7 | 115 |381|167|
| Continuous |4.6|687|2934|5571|
| Elevated |2.7|586|2215|3529|
| Fragmented |4.8|662|2324|3064|

Identity for the reported meadow means: Y=R*(S/R)*(Y/S). Fragmented/continuous: Y ratio .549991, R .963610, S/R .822006, Y/S .694352. Log-ratio arithmetic shares 6.20%,32.79%,61.01%; not a causal partition or mediation estimate. Foliar shoot ratio .708106, total vegetative biomass .727623, reproductive biomass 1.043478. Estimated annual seeds/reproductive shoot ratio .570761. Channel has vegetative biomass ratio 1.026949 but estimated seed ratio .029977, showing a particularly large descriptive proxy mismatch under different tidal settings. Elevated Y ratio .633459. No significance test from marginal means/SE, no cross-study pooling or general threshold. No claim that all reduced Y/S is pollen limitation, since site/phenology/resource/other differences and author estimator remain.

## What can distinguish complementarity from substitution?
Nature Communications 2016 DOI 10.1038/ncomms12980: pollen transfer and tube assay in still water; flow-on/off assay compared female flowers with foliar shoots, recording animal contacts/visits (4 trials). Different outcomes and experiments. No full flow x fauna factorial pollen or seed endpoint. A difference in significance between the two flow contexts is not a test of their interaction. Need randomized tanks with flow x fauna, same donor abundance/recipient cohort, count opened recipient flowers and tube incidence, later fruit/seed in separate nondestructively followed cohort; distinguish no-opening and missing. Contrast animal effect at each flow level on a declared scale; because baseline ceiling can cause diminishing absolute gains, do not use one arbitrary interaction scale as biological proof. Shared tank is experimental unit. Distinguish prey/foraging/pollen removal from successful transfer. The authors already proposed reproductive assurance without flow and possible extension of range.

Illustrative donor-supply accounting from 2010 published 15 -> 8.2 male fresh flowers/buds per 4m2: to maintain a hypothetical linear density × per-donor integrated delivery index, the latter must increase 15/8.2=1.829-fold; a uniform disk-area illustration would require radius 1.353-fold, NOT an estimate of actual pollen dispersal, animal compensation or recovery target. No assumption that male flowers are spatially independent, that trap means give fertility, or that either vector supplies that increase.

Conclusion: separate transport reach, encounter incidence and successful dose, then reproductive shoot production, flowers/spathes and realized reproductive output. The positive evidence is stage mismatch in published summaries. Animal/water substitution and complementarity remain unidentified; raw original records and joint factorial design still required.
