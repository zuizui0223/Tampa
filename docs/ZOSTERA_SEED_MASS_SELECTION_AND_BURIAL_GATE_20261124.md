# Seed mass selection sensitivity and recruitment evidence (2026-11-24)

## Actual source-backed hypothetical filtering
Source 2025 seed mass CSVs, Dryad 10.5061/dryad.6t1g1jx7p, same hashes and seed counts as analysis/153. Use observed viable-seed weights and sire labels; retain mass upper 75%, 50%, 25% separately within site, including all ties. This is deliberately hypothetical selection, not measured mortality. Statistic C = sum_g n_g(n_g-1) / [N(N-1)], probability that two distinct sampled seeds share inferred sire. Exact expected C under uniform subsampling without replacement equals original C, so unlike naive plug-in Hill2 this reference does not introduce an automatic finite-sample concentration penalty. Conditional alternative fixes actual retained count k_h in each mother x rhipidium x spathe x observed mating-status stratum, sampling uniformly without replacement within stratum. Within-stratum expected same-sire pairs scale by k_h(k_h-1)/[n_h(n_h-1)], cross-stratum expectation uses products of expected sire counts. Exact expectation, not p-value. Local script and synthetic exact checks executed successfully.

Upper-half mass selection (ties included), all seeds:
| cohort | site | retained | full C | retained C | retained/conditional C |
|---|---:|---:|---:|---:|---:|
| original |1|118|.02578|.01666|.9700|
| original |2|153|.02767|.02210|.9773|
| original |3|152|.02940|.01812|.9512|
| high locus |1|102|.02872|.02349|1.0357|
| high locus |2|130|.03050|.02123|.9347|
| high locus |3|116|.03429|.02039|.9835|

In both versions all three sites show lower C at upper half (18.2–40.5% decrease over six overlapping cells). Outcross-only upper-half also decreases at all six cells (9.9–32.6%). Relative to conditional expectation upper-half ratios .9347–1.0357 (all seeds), .9246–1.0608 (outcross-only). Not a resolved sire-specific effect beyond maternal/reproductive architecture. At upper-quarter outcross-only C increases relative to full sample in 3/6 version-site cells; monotonic selection strength does not guarantee lower concentration. Thresholds chosen for post-hoc sensitivity, no claim that mass determines survival this way. Only viable genotyped seeds observed, no new independent populations or downstream fitness.

## Independent experiment identified, not yet downloaded
Jørgensen, Labouriau & Olesen 2019, PLOS ONE 14:e0215157, DOI 10.1371/journal.pone.0215157. Official S1–S4 workbooks (suffixes .s001–.s004) report size metrics, emergence, unemerged seed fates and biomass. Published experiment: 5 outdoor tanks, 15 seeds/pot, 30 sorted pots (large/small at 2/4/6cm), 70 unsorted pots (7 depths x 2 destructive harvest cohorts). Published small/large median dry masses 2.9/4.9mg; viable unemerged fraction 23.1%/37.2%; emergence at 6cm 20.0%/29.3%; seedling biomass ~1.5 times larger from large seeds. Seed-size main effect on total emergence not significant, interaction with depth significant. Published fate percentages may not yield count closure across separate observations, so no imputation. Published values are not a new raw-data fit. Local direct download failed DNS. Source gate 155 and workflow added; independent acquisition/analysis pending.

## Interpretation
A reproductive stage's representation is a vector of probabilities, not necessarily seed mass. Large seed reserves may influence seed-bank persistence and early biomass more than emergence probability; environment modifies transitions. A seed mass threshold on the 2025 genetic dataset is only a scenario; cannot transfer the 2019 dry-weight size classes directly to the 2025 mass values or identify survival of paternal lineages. Next original-source estimand: matched tank-level differences at fixed depth for emerged fraction, viable unemerged fraction and total recovered seedling biomass per planted seed, if keys and denominators permit. Do not pool unequal harvest cohorts. Source study already reports size/depth effects, so any new descriptive decomposition should credit original work. No changes to Tampa Paper A or TNC. Draft PR #170; new CI not verified at writing.
