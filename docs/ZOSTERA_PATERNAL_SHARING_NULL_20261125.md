# Conditional paternal sharing reference in Zostera marina (2026-11-25)

## Actual data and source boundaries
Sgambelluri, Jarvis & Kamel (2024), Ecology and Evolution, DOI 10.1002/ece3.11608; Dryad 10.5061/dryad.dfn2z358x. Archive 14912352573 SHA256 c0f4a1b0b988dc4a9f678f10cd8c413b8636585c554fd81591502b4af69d7d61 verified locally. Five exact member hashes in analysis/178_paternal_sharing_null.py. The original article already reported multiple sires per maternal shoot but virtually no sire sharing between shoots. This step quantifies that published pattern against a new conditional mixing reference; it does not claim discovery of low sharing, actual father locations or a new ecological cause.

The deposited sire and maternal-shoot tables give margins and the number of shoots fertilized per sire, not the full seed-to-father network with coordinates. Match sire count table to deposited reproductive-strategy and heterozygosity table by site/sire, with exact one-to-one count agreement. The label Outcrossing is a sire-level deposited classification; the maternal table counts outcrossed seeds. Equality of margins is a necessary check, not proof of individual seed-level agreement. Only sites passing margin closure used for the exact reference. The high-locus panel contains 180 sire labels/26 maternal shoots/688 genotyped seeds. Its total male and maternal seed counts agree within every site, but the outcross-classified counts differ by one in site 1. The slim panel contains 208 sire labels/26 maternal shoots, with sire and maternal counts 852 vs 844; its site 2 totals differ by 8. Do not silently repair or treat the panels as independent.

## Conditional reference
Within each eligible site, distribute the deposited sire-label counts uniformly among the maternal outcross seed slots, keeping both margins fixed. For sire j with m_j seeds among N slots, and mother i with n_i slots, the probability of being confined to one mother is sum_i choose(n_i,m_j)/choose(N,m_j). Expected number of shared sire labels = sum_j [1 - that probability]. Verify this analytic expectation against 20,000 random permutations of the complete label vector (numpy RNG seed 20261125+site). Shared means present on >=2 maternal shoots. Null intervals describe this hypothetical uniform-mixing reference, not field uncertainty.

| panel | site | mother shoots | sire labels classified outcrossing | sire-side outcross seeds | maternal-side outcross seeds | observed shared labels | expected shared | null 2.5%-97.5% |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| high locus | 1 | 7 | 46 | 124 | 125 | 4 | STOP | STOP |
| high locus | 2 | 11 | 63 | 234 | 234 | 1 | 39.403248 | 37-41 |
| high locus | 3 | 8 | 57 | 164 | 164 | 0 | 31.310093 | 28-34 |
| slim | 1 | 7 | 55 | 146 | 148 | 0 | STOP | STOP |
| slim | 2 | 11 | 75 | 257 | 253 | 0 | STOP | STOP |
| slim | 3 | 8 | 58 | 198 | 198 | 0 | 38.292578 | 35-41 |

Simulated means 39.39525,31.30245,38.29945 for eligible rows respectively. Zero permutations at or below the observed number in each 20,000-run comparison; lower-tail plus-one Monte Carlo reference probability 1/20001. This is not a p-value for a spatial ecological mechanism, independent replicate, or a validation of inferred fathers. High-locus site 1 hypothetical removal of one maternal slot in turn yields expectation 24.918966-24.979876 for the existing 124 sire-side slots. This is only sensitivity; no change to the source records and no exact test at site 1. Slim site 3 overlaps the high-locus cohort and is a sensitivity, not an additional independent site. No pooling.

## Genotype ambiguity audit
Parent_Genotypes.xlsx Reduced Data, match exact sire/site to outcrossing labels. Compare unordered allele pairs at jointly reconstructed loci (probability >=.925, verify counts against supplied number reconstructed). No conflicting jointly high-confidence locus does not mean the pair is the same actual sire; no arbitrary merging. This audit covers all pairs of sire labels, not specifically pairs that are assigned to different mothers (the mother-by-sire matrix is unavailable).

| site | pairs with >=5 jointly high-confidence loci | pairs with no conflict | pairs with >=8 jointly high-confidence loci | pairs with no conflict |
|---|---:|---:|---:|---:|
| 1 | 426 | 89 | 19 | 0 |
| 2 | 961 | 88 | 79 | 0 |
| 3 | 319 | 25 | 9 | 0 |

Some reconstructed labels may be incompletely distinguishable. The small number of >=8-locus comparable pairs means the zero conflicting-free count in that subset does not exclude label splitting among all other pairs. No re-fit COLONY, no correction to sharing or assignment-error estimate. Unmeasured phenology, hydrodynamics, donor positions, offspring viability and parent reconstruction could all contribute to low observed sharing. Complete exchangeability is a deliberately strong reference, not the actual null of any one process.

## Connection to spatial geometry and next gate
The Enhalus map from Yu et al. 2019 lacks sexes and flowering. Enhalus uses detached floating male flowers at the water surface, unlike submerged Zostera pollen (Yu et al. 2019 DOI 10.1002/ece3.5106). Do not transfer Zostera pollen distances or dispersal kernels to Enhalus. Zipperle et al. 2011 (Annals of Botany 107:127–133, https://pmc.ncbi.nlm.nih.gov/articles/PMC3002472/) reported Zostera noltii median distances 1.84-3.22 m depending on CERVUS sampling assumptions, with only a subset assigned fathers. Sinclair et al. 2014 DOI 10.1093/aob/mcu048 reports tens of metres in Posidonia australis; limited assigned-father coverage prevents interpreting these as universal cutoffs. The present Zostera marina data do not contain the geographic parent coordinates needed to calibrate the earlier geometry model. Next require a species-matched geographic mother/father dataset or mapped flowering genets and flow trajectories, then compare spatially/phenologically constrained nulls with an identical sampling frame. No spatial reproductive bottleneck or biological mechanism established.

Local exact-source computation completed (script 178 and results JSON). Independent CI not yet run. Existing reproductive-interaction-gates branch only, no merge, submission, Paper A or TNC modifications.
