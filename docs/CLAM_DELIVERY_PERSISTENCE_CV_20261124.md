# Clam-assisted delivery: early establishment versus subsequent partner detection

2026-11-24 | Source-pinned original-data reanalysis; response-open internal prediction, not causal facilitation or external validation.

## New independent sources

- Lopazanski et al. 2026 (published October 14), DOI 10.3389/fmars.2026.1972882, Dryad 10.5061/dryad.cnp5hqcmx. Original author repository https://github.com/lopazanski/seed-density-clams, pinned commit 90e5e193c9db7efb75c3244f52b1585c9e93718e, data/dryad/seed-density.csv, Git blob d0f7ae365ae91641d34718c761e67ced1823032e. Source CSV fetched through GitHub and blob identity verified; 760 observations, 80 plots, 10 visits, Jan 4 only 40 plots; 9 complete visits. All ten seed densities (10–100) crossed with manual burial vs surface placement of initially live Mercenaria mercenaria, four plots per combination. The Dryad abstract incorrectly says five densities; source file, paper methods and README show ten. Seed density was assigned by row, burial by side of grid, so treatment effects are spatially confounded. Source author code already tested ever_live in final shoot count and establishment models; our additional analysis is temporal description and held-out-row forecast.
- UK study 10.1111/rec.14101 Table 1, five paired tanks with Carcinus maenas for seven days: nominal 20-mm furrow loss 0,36,18,0,62%, buried hessian bags all zero. Mean difference 23.2 pp; removing the tank with a dead crab gives 29.0 pp. Three nonzero paired differences, exact two-sided sign test .25 under exchangeability, weak precision. Original study reported 7–13-fold field shoot density with bags versus furrows, but only three plots per arm and no significant height effect. Infantes 2016 (10.1371/journal.pone.0168128) saw zero consumption at 2 cm across ten tanks in 24 h. Different duration, conditions, size, and nominal furrow versus burial prevent a pooled threshold or inference of duration causality. A 2-cm seed burial cannot be assumed universally predator-proof.
- Jørgensen et al. 2019 DOI 10.1371/journal.pone.0215157, experimental seedling emergence maximal 48.1–56.7% at 0.1–2 cm, 12% at 6 cm, 6.2% at 8 cm in Results (abstract says 5%). Existing literature explicitly describes overburial risk and shallow optimum. Source supplemental S1–S4 available; no new raw reanalysis of that study in this turn. Do not combine its emergence curve with separate predation experiments as a fitted joint model.

## Source-data results

At first four surveys 19,11,3,1 plots had L (confirmed live); shoots present in 0,0,32,38. L is detection, not survival. From four assessments, 29 plots ever L, 30 only shell fragments/empty shell (no L), 21 all N. Final shoot presence 16/29,15/30,8/21 respectively; 23/39 final-positive plots lacked L confirmation throughout the early observation window. All plots originally received a live clam, detection imperfect, no clam-free control, no equivalence test or proof of survival without the original partner. Later clam status not systematically measured. Final count 353 shoots across 80 plots, cannot equate shoots to independent sexual recruits.

At Dec 17, 38 positive plots, 30/38 positive at Apr 17 (78.9%); 42 negative plots, 9/42 positive at Apr 17 (21.4%). This is a state transition, not individual seedling survival. The experiment does not establish whether living-clam activity, passive shell structure or early seed release caused establishment.

## Held-out row forecasts

One seed-density row (8 plots) withheld at a time, ten folds. Training-only feature standardization and fixed ridge penalty 1 (sensitivity .1,10). Intercept unpenalized, count target log1p(final shoots), presence target 0/1 with clipped ridge predictions. Baseline fold training mean. Design = log(seed input) + burial; partner status = ever L and ever shell (first 2 surveys prior to emergence); early state = log1p(shoot count at Dec 17). No Jan 4 incomplete visit used. 
| Model | log-count MSE | skill | presence Brier | skill |
|---|---:|---:|---:|---:|
| Training mean |1.37626|0|.26337|0|
| Design |1.20495|.12448|.23501|.10766|
| Design + status |1.23833|.10022|.24454|.07150|
| Design + early state |.81105|.41069|.14772|.43909|
| Design + early state + status |.82152|.40308|.15126|.42568|

Status alone does not improve design-only predictions at any tested penalty. Status added to December 17 or January 17 state worsens pooled scores; at December 3, status gives modest count-score improvement (~.013 skill), not presence improvement. Four-survey status and alternative penalties recorded in JSON, not selectively chosen. For Dec17 primary, status added to early state improves 6/10 count rows and 5/10 presence rows, so a global lack of biological effect is not established. Row holdout does not create independent environments; predictor model and landmarks chosen response-open. No statistical equivalence, no causal mediation, no direct measurement of seed burial or living clam longevity.

## Ecological inference and next decisive contrast

A transient facilitation hypothesis is now better targeted than a claim of structural shell legacy: an interaction may modify a stage (early delivery/retention) and the plant's subsequent state may carry that benefit after a partner is no longer detected. The original paper already discusses this; the new quantitative result is predictive discrimination within this field experiment. This differs from persistent mutualism and from physical shell persistence. Test with equal seed input, randomized live clam vs intact empty shell vs inert geometry vs no clam, crossed with predator access; track marked seeds through real burial depths, retention, loss, emergence and later establishment. Remove living partners at prespecified times only if such a manipulation is actually feasible and ethically permitted; use direct fate tracking and randomized timing. No local otter or pollen data in this experiment. For Thalassia, fauna presence must be manipulated by tank with actual pollen transfer/fruit set, not inferred from seed-delivery effects. Keep separate endpoint families for future meta-analysis, no pooled grand effect. No main branch or manuscript modified.

Reproduce using the original public CSV and `node analysis/149_clam_delivery_persistence_cv.js seed-density.csv`. JS calculation executed in this turn via connector source; standalone Node wrapper not separately CI-run. Full fold predictions and sensitivity in results JSON.
