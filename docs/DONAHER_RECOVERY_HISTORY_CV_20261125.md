# Disturbance-history prediction of spring cover (2026-11-25)

## Scope and source
Follow-up to 173, Donaher et al. (2021), DOI 10.1002/ecs2.3804, Dryad 10.5061/dryad.9cnp5hqh7. Original Exp2_Regrowth_All.xlsx SHA256 290285c4d1f3d3e93d75f648a6ecbece0cc28eb77d44370622f243ed842589e4 verified from previously downloaded artifact 14924199338. Script 175 executed locally on actual bytes (Python 3.13, numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0). No new independent study, no causal effect estimate. The original authors already report disturbance timing effects; incremental held-out prediction is the new diagnostic.

Public PANGAEA accession metadata for Cimon et al. (2021) 931121 (T2 leaf and root-rhizome carbohydrates) and 931119 (T0/T2/T3 shoot densities) inspected; public HTML/textfile requests failed and local DNS failed. PDF screenshot unavailable. Previous 174 inventory job not visible in first-page workflow listing at head 250f2f482511cf6275ab8235defe96033d5f9776. No claim of new raw carbohydrate acquisition. No numerical carbon-reserve fit or inferred plot-level carbohydrate values.

## Source keys and limits
32 plots, 374 cover rows, remove two unlabeled-color rows as in 173. Non-disturbed C/S plots separate from D/CD plots; there is NO within-plot undisturbed reference in the deposited cover records. Plot 15 (C) elevation changes from -0.5850 to -0.6095 between fall and spring; do not silently reconcile. It is outside primary disturbed-plot analysis, and all 16 disturbed plots have constant elevation. Pivot by source plot/color/treatment/month/elevation within D/CD only (48 keys), require paired observed POST and SPRING values (42 color records); average jointly observed colors within plot/month, yielding 36 records, 16 plots (11 April,13 May,12 June). No missing-to-zero imputation. Source month labels differ from the published April/June two-subplot design, as recorded in 173. Sensitivity uses only source labels matching the dominant color-month mapping BLUE=JUNE, ORANGE=MAY, PINK=APRIL; never reassigns other records (35 records/16 plots). This is not a verified treatment-timing design. Elevation as depth proxy. POST is after Hurricane Dorian and excavation, not pre-excavation cover. Spring includes mixed species while fall was Halodule, so predicts total cover, not individual or species-specific recovery.

## Analysis
Equal plot weights, each plot-month has inverse number of available plot-months within that plot. Leave whole plot out (16 folds), standardize continuous predictors using training rows/weights only; ridge fixed alpha .1/1/10. All models use identical rows per panel. Indicators for May/June (April reference), CD vs D; compare separate additions and exploratory interaction. Outcome raw percent cover, no bounded prediction transform or tuning. RMSE in percentage points; fold-wise MSE retained. The comparison is descriptive and posthoc, conditional on complete observed cover and this one site/season. No significance claims, no cross-year/site validation.

| panel/alpha | elevation | state (+POST) | history (elev+month+clam) | state+month | state+clam | state+both | state+both+interaction |
|---|---:|---:|---:|---:|---:|---:|---:|
|source/.1|23.662362|21.975468|19.441151|18.678702|22.643923|19.080464|18.596437|
|source/1|23.569942|21.811402|19.461968|18.652393|22.309200|18.981178|18.964936|
|source/10|23.242075|21.428008|21.257424|19.728093|21.545003|19.821834|19.886645|
|agreement/.1|23.847355|23.562040|19.584832|19.544099|24.429724|19.283491|19.222221|
|agreement/1|23.780398|23.373525|19.611103|19.310316|24.019139|19.285792|19.515497|
|agreement/10|23.502720|22.675324|21.613831|20.704341|22.821649|20.769590|20.849178|

At primary alpha=1, state+month improves state RMSE by 14.48%, state+both by 12.98%; state+clam worsens by 2.28%. In both panels and all three penalties, adding month or both improves state; adding clam alone worsens state. Adding clam after month does not consistently improve; primary all three penalties worsen month model. Full interaction sometimes marginally helps but not robust. State+both improves on state in 11/16 plot folds at alpha=1 in each panel. Do not interpret absence of predictive improvement as biological equivalence or no treatment effect. Note conditional association on post-treatment state and incomplete sampling; no causal conditioning argument. Current cover+depth is not complete ecological state, so history increment is NOT proof of hysteresis, reserves, seed-bank mechanism or ecological memory. Autumn label reflects disturbance timing and time available for regrowth, plus potential source coding differences. All results specific to this source.

## Conservation relevance
Record disturbance date and season, not just contemporary cover; check whether adding carbohydrate and reproductive/vegetative propagule indicators improves out-of-study recovery predictions. The prior raw source acquisition remains a blocker. No new claim about bivalve treatment benefit, no meta-analysis. Draft PR #170 only; no merge/submission or Paper A/TNC changes. New independent CI pending.
