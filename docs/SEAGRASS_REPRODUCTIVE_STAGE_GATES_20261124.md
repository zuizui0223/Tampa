# Reproductive stage gates in clonal seagrass — 2026-11-24

## Refined question
Adult meadow structure can support pollen supply while competing with seedlings. Disturbance can create space yet remove pollen donors or kill recruits. Test timing and partner community as moderators, not a universal positive disturbance effect. Prior work already discusses temporal recruitment windows, so the proposed novelty is an explicitly stage-matched, donor–recipient scale and predator-context comparison, not the first concept of disturbance-mediated recruitment.

## Published evidence and new arithmetic
- van Tussenbroek et al. 2016 (10.1007/s00442-016-3665-7): fragmented Zostera noltei meadow had about 35% lower fruit set at similar flowering density; not a randomized otter effect.
- Johnson et al. 2020 (10.1111/1365-2745.13362): removal of adult shoots/rhizomes within 15 cm improved tagged Zostera marina seedling survival; original 10 removal / 11 neighbour-retained seedlings, haphazard assignment, one 11 m2 area. Published survival comparison chi-square 12.4, p<.001. Seed addition experiments and separate transplant gardens are distinct sampling units.
- Foster et al. 2021 (10.1126/science.abf2343): 30% higher allelic richness and 6% higher genotypic diversity in long-established otter areas. No direct flower or seedling transition measurement in these data is asserted.
- Kendrick et al. 2023 (10.1002/ece3.10456), Parker Point seed predation: greater within meadow in 2001/2004, greater on sand in 2013/2016, unresolved contrast in 2003/2014. The authors observed a shift in crab taxa. Tether versus seed-board protocols coincide with the two periods; cannot identify a causal predator-community shift independent of method.

Table 3 curve exponent b transformation for N(age)=a*age^b: N(2age)/N(age)=2^b. Parker Point .5216 (transformed exponent CI .4707–.5779), Thomson Bay .6105 (.5475–.6802), Stark Bay .7140 (.6259–.8151). Re-expression of published fit, not new data/model or annual survival probability. Age range must remain within observed model domain. Stark Bay fit pseudo-R2 .4763, so avoid strong extrapolation.

Table 4 pooled two-cohort counts (2013/2014 labels as reported): Parker Point n=60, confident local=16, nonlocal=15, unresolved=29; Stark Bay n=58, local=43, nonlocal=2, unresolved=13; Thomson Bay n=65, local=28, nonlocal=3, unresolved=34. Conditional nonlocal fraction ranges if confident assignments were all correct and unresolved labels arbitrary: Parker 25.0–73.3%, Stark 3.45–25.86%, Thomson 4.62–56.92%. Parker/Stark bounds overlap. Known-origin seeds: 8/139 Parker Point seeds assigned nonlocal, 0/110 Stark Bay, demonstrating unequal individual classification performance. These ranges are not true-migration confidence intervals; a nonlocal assignment is not evidence of observed dispersal.

Reproduce arithmetic: `python analysis/136_reproductive_stage_recruitment_audit.py`. The numerical transformations were calculated from the source tables in-session; repository Python execution has not yet been independently verified.

## Stage-specific prediction, not fitted
R = F * q * d * s, where F is absolute flowers per donor area, q mature fruit per flower, d settlement per fruit at a recipient area, and s conditional recruit survival. Separate donor and recipient geography. A 35% fall in q alone requires a downstream d*s gain >1/0.65=1.538 for equal net recruitment with F held fixed (illustrative algebra, not joint cross-species parameter estimate). Relative flowering or genotype richness cannot substitute for absolute recruits per area. Disturbance before seed production, during settlement or after establishment may have different effects, even at equal area removed.

## Original data candidates; access and keys remain gates
- Johnson et al. 2020 Dryad 10.5061/dryad.2bvq83bm5: Seedling_Competition_Exp_MASTER.csv, Meta_Data_Seedling_Competition.csv, natural seedling survey and transplant garden files. Keep tagged seedling survival and separate randomized seed-addition blocks distinct.
- Kendrick et al. 2022 Dryad 10.5061/dryad.vhhmgqnwz: flower_Fruit_and_ratio_2013-2018.csv, inflor_shoot_ReprodEffort_2013-2018.csv, Recruitment_14_18.csv and README. Flowering six locations, recruitment three adjacent sparsely vegetated areas. Audit site/year/cohort linkage, direction of seed transport and observed zeros; no same-plot chain assumed. Predation trial original raw data not confirmed in listed files.
- Foster et al. 2022 Dryad 10.5061/dryad.ns1rn8pt4: microsatellites, otter occupancy and environmental data; landing-page files not displayed. No raw genotype analysis yet.
- Balestri et al. 2021 Dryad 10.5061/dryad.t76hdr81n: early life-stage biotic interaction workbook.
- Yu et al. 2019 Dryad 10.5061/dryad.sn1h87s: Enhalus coordinates and genotypes for two plots; do not infer flower outcomes absent from workbook.

Local direct Dryad API attempts for Johnson, Kendrick and Foster failed DNS resolution in the session. No acquisition or raw effect estimate claimed. Next source-specific gate is actual archive download, checksums, documented column semantics and independent sampling units. No forced join or pooled effect across unrelated studies. Original Tampa manuscript and TNC design unchanged.
