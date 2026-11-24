# Water, phenology, and pollinator composition transfer (2026-11-25)

## Correction (2026-11-25)
The previous RMSE table transposed model labels. Re-execution of unchanged analysis/169 on pinned input files confirmed all numerical values but not the original labels. The corrected table and interpretation below supersede the earlier report. The previous CI expected the mislabeled directions; fix the assertions, not the estimators.

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
|113|array|.882215|.832909|.834564|
|113|week|1.021539|1.203983|1.225831|
|88|array|.944864|.896066|.900837|
|88|week|1.072565|1.304477|1.332608|

Across both panels, three penalties, and two water specifications, unweighted visitation improves context-only array holdout in all 12 comparisons but worsens context-only week holdout in all 12. Adding composition to visitation improves array holdout in only 2/12 comparisons and week holdout in only 1/12; this is not consistent incremental predictive value. At alpha=1 for the 113-plant panel, visitation reduces array RMSE by 5.59%, but increases week RMSE by 17.86%; composition increases RMSE relative to visitation by 0.20% (array) and 1.81% (week). Thus the prior claim that visitation improved week holdout is withdrawn. Temporal split used a linear week term while array split used week indicators; analysis/170 adds a common linear-week design to both splits and fixed functional weights from the separate single-visit experiment. Small within-study diagnostics, not prospective/external validation or causal estimates; do not pool RMSE ratios across studies with different outcomes/designs.

## Reproduction and status
analysis/169_gallagher_water_phenology_composition.py executed locally on exact source files before commit, all models completed. Independent CI pending. Latest prior head 185a062565be28bbee2ff704e7f88df128ce6cff: first page of 21 CI runs returned, cross-system source/screen reported failure (previous known API rate-limit failure not assumed to recur without logs), other displayed jobs success/in progress. Prior new composition and pollen-tube workflows not on returned first page, not confirmed. No new otter raw data in this turn. No merge, submission, Paper A or frozen TNC modifications. Next useful step: independent study with matched visitor behavior, taxon, and reproductive response, then examine how observation effort and plant resource conditions affect incremental prediction. Avoid claiming universal functional superiority from two small within-study CV exercises.