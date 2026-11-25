# Posidonia australis: marker-profile richness is not allele richness (2026-11-24)

## Source and scope
Kendrick et al. 2023, DOI 10.1002/ece3.10456; genetic dataset Dryad DOI 10.5061/dryad.dfn2z3577. Original CSV PaustralisRIpopgeneticsRawdata.csv SHA256 3081acdbd8b7bc330851ebf2057a4d4a7f279d8c3484e2c38f7c78494d6aca9d, from source artifact 14912352573. Original article already studied clonal diversity and recruitment and reported mostly unique seedling MLGs. The present post-outcome descriptive diagnostic separates sample-standardized exact marker-profile richness from locus-specific allele presence and tests sensitivity to repeated profiles. It is not a new parentage assignment or direct measurement of gene transmission.

381 unique sample codes: 199 adults (4 meadows), 182 seedlings (3 meadows x 2 source-labelled cohorts). 14 samples have one locus missing (0,0), leaving 367 complete marker records (188 adults and 179 seedlings). Two recorded allele columns per locus; README states that triploids occur but supplies no per-sample ploidy flag. Therefore use unordered recorded marker pairs, not diploid allele dosage, HWE, expected heterozygosity, clone identity reconciliation or population-genetic mating simulations. Source adult labels: Parker Point 2009, Nancy Cove/Stark Bay/Thompson Bay 2015; seedling labels 2013 and 2014. Do not reinterpret these as directly sampled parents and offspring. Source spelling Thompson Bay retained (article Thomson Bay). All four meadows included in source audit; Nancy Cove has no seedling cohort.

## Exact individual-based rarefaction
At common n=27 complete samples, expected profile richness = sum over profiles of 1-C(N-k,n)/C(N,n). Expected marker-allele richness uses the same formula, where k counts sampled individuals carrying a locus-specific recorded allele (once per individual irrespective of dosage). Sum over seven loci. Not standard gene-copy rarefaction or a confidence interval.

| Site | Adult N complete | Adult exact profiles | Adult E profiles n27 | Seedling E profiles both years n27 | Adult E alleles n27 | Seedling 2013 | Seedling 2014 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Parker Point |44|11|8.815895|27|19.443150|24.000000|23.353027|
| Stark Bay |50|38|23.149745|27|30.523726|27.000000|29.379310|
| Thompson Bay |48|32|20.272761|27|29.720994|32.425807|33.178818|

Six of six seedling cohorts have greater sample-standardized exact profile richness; four of six have greater marker-allele richness. All 179 complete seedlings have unique exact profiles within each cohort (177 different profiles pooled over six cohorts); 177/179 have profiles not observed in the complete local adult sample. New exact profiles relative to samples are not proof of new genets or immigration. Exact adult profile counts are not expected to reproduce all published GenAlEx clone reconciliations; missing data, P_ID and genotype error handling differ.

## Repeated-profile sensitivity
Collapse identical complete recorded profiles within each group to one representative and standardize to 11 profiles (minimum complete profile count). Seedling minus adult expected allele richness:
- Parker Point 2013 -1.779025, 2014 -1.033940.
- Stark Bay 2013 -2.641986, 2014 -1.380519.
- Thompson Bay 2013 +0.569308, 2014 +1.445317.

Only 2/6 positive after profile-equal standardization, compared to 4/6 at 27 individuals. Parker Point reverses for both cohorts: its observed repeated adult profiles explain part of the individual-based comparison. This is a change in sampling estimand, not statistical adjustment for a causal effect of clonality. Across all feasible rarefaction sample sizes 2..min(group sizes), profile-equal contrasts stay negative in Parker Point and Stark Bay; Thompson 2014 stays positive, 2013 changes sign at larger n (26 positive sizes, 5 negative). No threshold selected retrospectively to claim generality.

## Marker allele coverage
Presence/absence uses all available nonzero calls, including incomplete records. Each of six cohorts has alleles not observed in the corresponding sampled adults (counts 9,9,2,1,6,7 in chronological order within Parker, Stark, Thompson respectively). Of these, 3,2,0,1,2,5 locus-specific alleles are not found in any of the four adult samples. Adult sampling is limited, spatially nonidentical and noncontemporaneous, and markers may have error; these are coverage differences, not verified immigrant or novel alleles. No genetic source assignment from absence alone.

## Ecological interpretation
Sexual recruits can be rich in combinations without higher marker-allele richness. Apparent gain in allele richness relative to ramet sampling depends on repeated adult marker profiles and sampling scale. This is consistent with genetic recombination and cohort-specific sampling of standing variation, not identification of the mechanism (mating, dispersal or post-settlement selection). The two cohorts per site share the same adult reference; only three paired meadows, not six independent replicates. No universal trend or inferential p-values. Source study already describes sexual recruitment and clonal diversity; the narrow new diagnostic is the contrast of two rarefaction estimands and their sensitivity.

## Reproduction
analysis/146_posidonia_stage_marker_diversity.py on original source member with checksum. Source extraction via analysis/144_external_seagrass_genetic_source_gate.py. Computation executed locally; new independent CI must be checked. Keep original Paper A and TNC unchanged. Draft/unmerged.
