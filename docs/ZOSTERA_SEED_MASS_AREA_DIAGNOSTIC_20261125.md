# Seed mass conditional on cross-sectional area across spathe rank (2026-11-25)

## Source and prior work
Follow-up to analysis/182. Sgambelluri, Jarvis & Kamel 2025, Evolution DOI 10.1093/evolut/qpaf111; Dryad DOI 10.5061/dryad.6t1g1jx7p. The original paper already reports position-dependent seed mass and area and discusses developmental timing and provisioning. The new diagnostic asks whether the within-branch mass contrast remains after accounting for measured area, without claiming developmental-age adjustment. All seeds collected on one date; no direct age, maturity, thickness, water content or reserve measurements. Do not infer final mature size, reserve density, or a causal maternal allocation effect.

Verified original artifact 14916683079 SHA256 2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8. Read original README and exact source tables. Mass 844 rows, area 873 rows; join one-to-one by site/maternal ID/rhipidium/spathe/seed position gives 839 rows, 35 mothers, 89 rhipidia. Selfed classification, paternal label and offspring heterozygosity agree in all 839. Maternal heterozygosity differs in 89 rows, paternal heterozygosity in 185, Seeds per Shoot in 11; exclude these fields rather than reconcile. All joined mass and area pairs also occur in the unkeyed Mass_area_comparison.csv; this is numerical corroboration, not a separate identity crosswalk. No inference about unmeasured seeds or cross-publication joins.

## Methods
Define first/last observed spathe in original mass table before restricting to joined measurements. Estimate slope of log(mass) on log(area), centering both within each spathe to avoid training exclusively on the between-spathe rank difference. For each target maternal shoot, fit slope using all other shoots. Whole-dataset within-spathe slope 1.798075; held-out-mother training slopes 1.774367 to 1.827364. Compute within-branch difference dM in mean log mass, dA in mean log area, residual contrast dR=dM-beta*dA. Alternative pooled log slope and fixed exponent 1.5 (similar-shape constant-density geometry only). This is algebraic conditional accounting, not prediction of true density or developmental age. Equal within-branch shared labels, then equal branches per mother, then equal mothers. Report 100*(exp(mean log difference)-1); not previous ratios of arithmetic means. Conditional bootstrap 20,000 maternal-shoot resamples within the three observed sites, seed 20261125, holds fitted slopes and selected pairs fixed. Intervals do not include all uncertainty of slope estimation or across-site variation. Posthoc.

## Results
|subset|branch pairs or label contrasts|mothers|area change %|mass change %|area-adjusted mass contrast %|conditional 95% interval for adjusted %|
|---|---:|---:|---:|---:|---:|---|
|All|48|24|-24.010|-49.029|-16.509|[-24.521,-8.138]|
|Outcross|40|21|-27.899|-54.988|-19.034|[-28.861,-8.716]|
|Self|25|17|-21.221|-33.251|+2.690|[-13.296,+26.064]|
|Shared outcross sire label|37|18|-22.080|-46.354|-16.123|[-28.119,-3.272]|
|Shared outcross label, >=2 seeds per endpoint|9|8|-25.163|-57.372|-28.310|[-40.458,-13.853]|
|Common observed area-range restriction|23|17|+6.782|+4.375|-7.134|[-27.874,+21.501]|

All-seed adjusted contrast negative in 18/24 maternal shoots; negative mean in all three observed sites, leave-one-site-out -18.582%, -18.031%, -12.795%. Alternative pooled exponent gives -14.817%; fixed 1.5 gives -23.053%. Self and outcross subsets differ, so not evidence for a mating-mode interaction; no test of that interaction. Shared outcross sire-label contrast particularly influenced by site 3 (leave-site-3-out -5.771%); shared labels are reconstructed. No causal genetic effect.

## Common-size sensitivity
Within each branch endpoint pair, use bipartite assignment maximizing number of matched seeds and then minimizing total absolute log area distance, with a fixed allowed ratio of larger/smaller area <=1.05, 1.10 or 1.20. No mass used for matching. Compare distinct seeds from two spathes, not longitudinal pairs. Same-class sensitivity also requires identical deposited self/outcross class. Fixed tolerance choices exploratory, no selection of a best result.

|restriction|tolerance|matched seed pairs|branches|mothers|mass change %|area-adjusted contrast %|conditional 95% for adjusted %|
|---|---:|---:|---:|---:|---:|---:|---|
|All|5%|49|22|16|-22.202|-21.281|[-35.523,-7.922]|
|All|10%|69|27|17|-21.830|-19.651|[-34.858,-4.919]|
|Same mating class|10%|56|23|15|-22.159|-20.130|[-36.419,-3.977]|
|Outcross only|10%|43|19|14|-19.972|-17.532|[-36.038,+1.778]|

All and same-class matching at all three tolerances yields negative adjusted mean; outcross-only 5% and 10% intervals cross zero. Overlap-range restriction (all seeds lying within common min/max area range rather than individual matching) yields substantially weaker adjusted result, and its leave-one-site-out range includes a positive value. Thus magnitude and robustness depend on support/selection and site. Not definitive separation of growth and maturation. Because area may be a post-treatment/mediating outcome and seed thickness, shape, coat and water content can change, adjustment/matching may introduce selection bias. No proof of lower tissue density, starch, energy storage or greater future mortality.

## Next empirical gate
Independent maturity-stage study (https://pmc.ncbi.nlm.nih.gov/articles/PMC5119234/) found color-associated changes in wet seed mass and water content; independent developmental study https://pmc.ncbi.nlm.nih.gov/articles/PMC10036900/ identifies seed maturation stage by color/texture. These support measuring maturity and water/dry mass rather than using area as a clock. No calibration to present source or assumption that regional mass values are comparable. Prospective matched-age sampling of early and late spathes (known days after fertilization), seed color, thickness/volume, wet and dry mass, carbohydrate reserve, then germination and establishment needed to distinguish timing from physiological provisioning. Do not extrapolate to recovery without outcomes.

## Reproduction and status
Local run completed on pinned source (Python 3.13, numpy 2.3.5, pandas 2.2.3); executed script blob b1dd74a36c344d1ac0b39cf034ebca5e9addce84 matches GitHub analysis/183. Output SHA256 b80bd5c387f16be050c9fa67ca8c92af42c91ab20934d64993cb17255f5c12b2. Reproduce: python analysis/183_zostera_seed_mass_area_diagnostic.py <verified archive> --out results.json. Independent CI not run. No Paper A/TNC/main changes, merge or submission.
