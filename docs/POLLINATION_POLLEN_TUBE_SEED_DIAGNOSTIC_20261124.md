# Original-source apple and Mertensia pollen-stage diagnostics (2026-11-24)

## Source provenance and scope
Cross-system source gate run 45408641314 completed; downloaded artifact 14925937983, ZIP SHA256 5f0bdb9f65d277e3e0e52fd4d680893090bfb91a51ff9e742f750992c1b18117 independently verified. Six of seven acquisition targets succeeded (Gallagher 2020/2021, Stavert apple 2020, Clarkia, herbivory/pollination, Penstemon). Raymond KNB 10.5063/V986FN failed at DataONE resolver ("no public object locations"); public DOI/DataCite lookups also unavailable during this turn. No invented raw otter results. The original Raymond 2021 Oikos 10.1111/oik.07681 reports the absent crab–epifauna relationship in its observational 21-site survey. No experimental otter causal effect inferred.

## Apple: Stavert et al. (2020), DOI 10.1038/s41598-020-73637-5
Data DOI 10.6084/m9.figshare.13023224.v1. Source files and hashes in analysis/167. Actual microscopy table 1948 rows, four measured spatial count types per style. Composite key year, farm, flower stigma, stigma ID, treatment, number of visits yields 487 complete styles. Flower-number-only join invalid (number reused across contexts); composite flower context count 105. Recorded style counts per flower: 2 (2 flowers), 3 (6), 4 (27), 5 (63), 6 (7). Six-style records are retained as deposited, not assumed six anatomical stigmas. The paper describes five stigmas for Pink Lady. There are 18 styles with a nonmonotone adjacent count and three flower contexts with positive base count but zero middle count. Spatial snapshot counts are not individual tracked pollen-grain survival histories. Do not force nesting or discard nonmonotone records. The one-visit microscopy rows show 14 flower contexts, 11 pollen-positive, 8 upper-positive, 4 middle-positive, 2 base-positive. The original paper's main results note ~3% of stigmas with base tubes after one visit, while a discussion sentence states none reached base; report original deposited counts with explicit flower-level denominator, do not reconcile these statements silently.

Among all 65 visited flower contexts: 61 with observed pollen, 14 with base tubes, 47 pollen-positive but no base tubes. Pollen threshold sensitivity (flower-level sum across observed styles):
|minimum counted pollen grains|flowers|base-zero flowers|
|---:|---:|---:|
|1|61|47|
|10|56|42|
|50|45|31|
|100|42|28|
|200|36|23|
|500|23|13|
|1000|10|3|
Thresholds are posthoc descriptive; no biological minimum implied. At >=100 grains, exactly five recorded styles sensitivity 17/27 base-zero; year splits 6/8 (2017), 22/34 (2018). Observed pollen is not the same as compatible pollen. Control 14/17 pollen-positive and 1/17 base-positive; background/contamination cannot be assumed zero. Do not classify absent tubes as certain failure to fertilize or assign compatibility from counts. Original study already showed quality limitation, and its primary GLMM/Cox analyses remain the reference. New diagnostic: flower-level joint presence and threshold sensitivity, not a new claim that pollen quantity and reproduction differ.

Fruit table 1357 rows; one-visit 58 rows, 0 initial/0 final fruit. Seed table 1646 rows; one-visit 58 rows, all zero seeds. Microscopy and fruit/seed measurement flowers explicitly separate in methods. No individual keys joining these tables. Do not assume 58 identical rows across tables or use to estimate transitions. Twenty fruit-table records final=1 and initial=0; two seed records >10 despite paper's stated nominal ten ovules. These are source audit flags, not silently altered. No survival curve, seed per fruit calculation or actual full-chain covariance across separate cohorts.

## Mertensia ciliata: Gallagher & Campbell (2020), DOI 10.1002/ajb2.1439
Data DOI 10.7280/D19X0D; pollinator effectiveness workbook SHA256 bbfcbbaf43b53b0ef835b891bd8932ae3761a383e4ecb1f38440a4ba9d477c38. Sheet row counts 232 combined, 62 pollen, 232 seed; plantID unique in each. All 62 pollen records match on plantID/week/site/treatment/visitor, both pollen counts identical. Seed sheet matches all 232 on plantID, with no seed count/per-flower seed, site/week/treatment or denominator discrepancies. 43 Muscoidea/Muscid labels and one Hoverfly/hoverfly differ, retain combined sheet labels. 138 missing visited-flower counts correspond to source 999999 sentinel in seed sheet. One bagged zero-flower record excluded from visit comparisons; all 94 visited ramets have positive noFlrs and seedCnt/noFlrs closes to seedPerFlr. Article/sheet identify 2016 experiment but combined colDate.PolObs year labels 2017; no year-based inference. 
Of 94 visited ramets, 47 have pollen and seed data (20 Bombus,21 Muscoidea,6 Osmia; one Hoverfly has no pollen data). All 47 positive conspecific pollen, 20 zero seed. The original methods use marked flowers on ramets, sometimes more than one flower per ramet; ramet means, not individual pollen grain or flower fate. Group means:
|site|visitor|n|pollen mean|seeds/flower mean|zero-seed ramets|
|---|---|---:|---:|---:|---:|
|RG|Bombus|10|663.5|1.386667|1|
|RG|Muscoidea|9|457.444444|.682540|7|
|RG|Osmia|6|646.333333|1.5|2|
|SP|Bombus|10|1397.5|.905238|3|
|SP|Muscoidea|12|826.083333|.4875|7|
Bombus > Muscoidea on both measures in both sites, descriptive matched-subset means. Larger Bombus pollen at SP than RG despite lower seeds/flower, not causal location effect. Osmia only RG, small n. Within-site-by-visitor rank diagnostic: rank both measures within each of five strata, center ranks, pool cross-products with common normalization. Observed -0.0947164. 9999 permutations of seed ranks within strata (numpy RNG seed 20261124), two-sided plus-one p=.5627, empirical null quantiles -.31108,.31949. No support for a monotone within-stratum association in this small observed subset; not evidence of absence, not a test of causal pollen effect. No adjustment for maternal state, observation time or pollen quality. Pollinator guilds not randomized. Original paper already evaluated taxon-specific effectiveness and seasonal composition. This calculation compares joint measurements and separates between-visitor differences from within-guild associations.

## Status and next steps
Prior branch b6455bbe135562862cc2cb5326a0f096d450b817 first 21 returned PR workflows all successful; previous diel screen explicitly verified by CI. The earlier three lucinid workflows were not in this returned first page, so do not infer their status from this list. Actual calculations independently executed in-session in Python on downloaded verified sources; new reproducer analysis/167 and dedicated CI added, not yet verified as an independent run. The two new studies have measured proximal and downstream endpoints, but apple fruit cohort is separate and cannot support full-chain matched covariance. No cross-study pooled transmission effect, no generalization to seagrass or otter mechanism. Next prioritize original otter trophic-cascade manipulation data, and estimate comparable paired-stage effects with independent experimental units before any pooled model. Draft PR #170; no merge, submission, changes to Paper A or frozen TNC.
