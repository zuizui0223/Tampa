# Water, phenology, and pollinator composition transfer (2026-11-25)

## Scope
Gallagher & Campbell 2021, DOI 10.3389/fevo.2021.641693, Dryad 10.7280/D16D7Z. The paper already reports that flowering time affects visitation more strongly than water supply, whereas seed production responds more strongly to water supply. This posthoc diagnostic evaluates whether observed visit rate and taxonomic composition add predictive information for seed production in held-out experimental arrays versus held-out flowering weeks. It is not a causal mediation analysis, a test of general pollinator importance, or a novel claim of phenology-dependent facilitation.

Source artifact 14925937983, ZIP SHA256 5f0bdb9f65d277e3e0e52fd4d680893090bfb91a51ff9e742f750992c1b18117 independently verified this turn. Member hashes fixed in analysis/169. Source author aggregate table has 115 unique plants in 20 week-by-array blocks, four weeks, three randomized water treatments (A wet, C control, D dry). Exclude one missing seed outcome and one mismatched total/classified visitor count; primary n=113. 1,210 raw observation rows (64 blank metadata rows excluded), 115 observed plant IDs; 5 plants' simple raw summed visit counts differ from at least one deposited aggregate count; 21 plants' simple mean raw seed counts differ from author aggregate seed per flower. These may reflect source filtering/measurement definitions; do not assume raw means are correct or replace authors' values. Restrict to agreement as a post-outcome sensitivity, n=88. 2015 workbook has 40 unique IDs, 31 also in 2016; not independent study replication. No cross-year joins.

## Descriptive endpoint contrasts
|week|n|mean deposited visit rate|pooled Bombus share of classified observed visits|mean seeds per flower|
|---:|---:|---:|---:|---:|
|1|28|.785306145|.549763033|1.404672453|
|2|27|.176154068|.888888889|1.767404130|
|3|30|.102053111|.870967742|1.150336435|
|4|28|.092848639|.862068966|.693469054|

Visit rate and composition are observation-window measurements. 35 plants have zero observed visitors, of which 19 have positive seed counts per flower. This is incomplete observation of the pollination period, not evidence of pollinator-independent seed production. No assumption that unobserved visits equal zero actual visits. Week 1 to week 2 visit rate decreases 77.57%, mean seed production increases 25.82%; by week 4 seed production falls despite high observed Bombus share. The original paper already reports changes in visits and seed set; these are descriptive source calculations not new proof of compensation.

## Diagnostic
Ridge regression, endpoint author mean mature seeds per flower, RMSE in original units. Context: water assignment indicators, log1p flower count, flowering week. Week-array holdout uses fixed week indicators (20 folds); week holdout uses continuous week rather than an unseen category (4 folds). Then add log1p author visit rate and any-visitor indicator; then add Bombus/total observed visits, coded zero only at zero observed visitors with indicator in both visit models. Continuous variables scaled within training folds, penalty alpha .1/1/10 as sensitivity. Measured-water sensitivity adds VWC to every model, no independent future prediction. Use same plants across nested models. No tuning. Whole arrays/weeks held out, but models not identical across split definitions; cannot attribute all difference to temporal scale alone.

Primary, assigned-water context, alpha=1:
|panel|split|context RMSE|+visit rate|+composition|
|---|---|---:|---:|---:|
|113|array|.834564|.882215|.832909|
|113|week|1.225831|1.021539|1.203983|
|88|array|.900837|.944864|.896066|
|88|week|1.332608|1.072565|1.304477|

In both panels, all three penalties and both water specifications, adding composition to visit model improves array RMSE, but context-only or context+composition is similar. Adding composition to visit model worsens week RMSE in all twelve combinations (two panels x two water specifications x three penalties). At alpha=1 primary week comparison, rate improves context by ~16.7%, composition raises RMSE ~17.9% relative to rate. This indicates nontransferability of incremental taxonomic composition in this specific four-week experiment, conditional on the model definitions, not a general biological absence or causal statement. Under array holdout, added rate by itself worsens baseline; added composition recovers that loss but hardly improves baseline (0.2%). Temporal split tests extrapolation to held-out weeks under a linear week term; with only four weeks there is no estimate of independent seasonal/site generality. No p-values, no assertion of significance or superiority across species. The 2020 Davis data and this experiment have different endpoints (yield vs seeds/flower), split units and composition resolutions; do not pool RMSE ratios as common causal effect sizes.

## Reproduction and status
analysis/169_gallagher_water_phenology_composition.py executed locally on exact source files before commit, all models completed. Independent CI pending. Latest prior head 185a062565be28bbee2ff704e7f88df128ce6cff: first page of 21 CI runs returned, cross-system source/screen reported failure (previous known API rate-limit failure not assumed to recur without logs), other displayed jobs success/in progress. Prior new composition and pollen-tube workflows not on returned first page, not confirmed. No new otter raw data in this turn. No merge, submission, Paper A or frozen TNC modifications. Next useful step: independent study with matched visitor behavior, taxon, and reproductive response, then examine how observation effort and plant resource conditions affect incremental prediction. Avoid claiming universal functional superiority from two small within-study CV exercises.