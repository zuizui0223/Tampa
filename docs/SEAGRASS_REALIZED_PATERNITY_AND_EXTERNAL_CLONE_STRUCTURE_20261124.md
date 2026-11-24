# Realized paternity and external clonal neighbourhoods (2026-11-24)

## Source acquisition and verification
Previous head 381a39465b31df5b99f7ccfcd6e1450262c46094: 10/10 PR workflows successful. External data acquired in run 45378546297, artifact 14912352573; downloaded ZIP SHA256 c0f4a1b0b988dc4a9f678f10cd8c413b8636585c554fd81591502b4af69d7d61 matches GitHub digest. All three source datasets present. README and tabular files inspected locally; no raw data committed. Posidonia adult/seedling dataset retrieved but not analyzed in this step.

## 1. Realized paternity, Zostera marina
Sgambelluri et al. 2024, Multiple paternity, fertilization success, and male quality: Mating system variation in the eelgrass, Zostera marina. DOI 10.1002/ece3.11608, data DOI 10.5061/dryad.dfn2z358x. The paper already studied sire richness, selfing, paternity skew and reproductive structures; it reports mean 8 sires per shoot and ~70% outcrossing. The new post-hoc diagnostic conditions on all genotyped seeds outcrossed, with at least 2 genotyped seeds per spathe, distinguishing realized sire richness from outcrossing. No refit of COLONY.

| cohort | spathes | genotyped seeds | shoots | all-outcross >=2 | single inferred sire | 5 all-outcross seeds, histogram of 1..5 sires |
|---|---:|---:|---:|---:|---:|---|
| Unfiltered archive |212|972|36|83|17|2,4,8,3,4|
| Published slim |162|844|26|64|11|1,3,7,2,2|
| High-locus rerun |136|688|26|76|13|1,3,5,4,1|

The primary published cohort has single-sire full-outcross spathes in all 3 meadows: 3/17, 5/26, 3/21. These 11 spathes are from 9 of the 20 sampled mothers with any eligible all-outcross spathe. High-locus 3/20,8/32,2/24. Same five genotyped outcross seeds can represent 1 to 5 inferred sires, even in the published slim dataset. Exact identity key Site + Maternal ID + Rhipidium + Spathe. 136/136 high-locus spathes match published keys. 53 spathes have >=2 and all outcross in both; 5 have one sire in both, 7 in slim and 9 in high-locus; 37/53 have identical genotyped seed counts. This is sensitivity to a new COLONY run and sample filtering, NOT independent replication. Article Table A3 lists 135 spathes for reduced cohort, deposited CSV has 136; retain source count, no silent removal. All-outcross is restricted to genotyped seeds, not all seeds or fertilization rate. No seed-level inferred father roster in the inspected CSVs; no effective sire count, mating-distance or paternity-network fit.

All per-spathe count identities and unique keys checked. Rounded outcross ratios agree within .00501. Cross-level worksheet audit also found 6 of 36 unfiltered shoot outcross counts differ from sum of its spathes despite exact genotyped-seed count closure; 1 of 26 reduced shoots differs. Therefore don't pool hierarchy or reinterpret published shoot values using spathe summaries. Source-specific CSV cohorts only. No independent-unit p-values claimed for descriptive proportions.

## 2. Independent species, Zostera noltei
Berkovic et al. 2018 PLOS ONE DOI 10.1371/journal.pone.0199275, S1 Table DOI 10.1371/journal.pone.0199275.s004. SHA256 a5d01c36ceedf0772f2835fd4e45203cae01819b87fb46aff29da85c41560292. The original article studied clone span, pairwise clonemate probability with distance, and asexual hydrochory. It reports 803 occupied coordinates, 3212 samples before genotype filtering, 3185 analyzed ramets, 1999 MLGs. Workbook contains 797 unique plot IDs/coordinates, 794 with 4 sample units and 3 with 3; all ramet IDs unique. A sampled unit comprises a ramet with 3-4 shoots, not one shoot. Preserve source Genet labels (Psex-vetted) rather than reclassify. No inference about missing plots or plant density.

Among 794 four-sample quadrats, numbers of distinct genets 1/2/3/4 occur in 64/176/263/291. Observed mean richness 2.983627 vs exact fixed-global-roster random-label expectation 3.993019. For each focal sample, other distinct genets = richness-1, so mean 1.983627 vs 2.993019, 33.7249% deficit. All 797 quadrats pooled: 1129/4773 (23.6539%) same-genet pairs; random-label global fraction .00116990 (0.11699%), expected count 5.58393. For 794 complete quadrats, 1127 observed same-genet pairs exceed all 4999 random permutations of the global sample genotype labels (Monte Carlo p=.0002). This is a fixed global null breaking spatial autocorrelation, not a realistic dispersal null or replicated disturbance comparison. Local clonal aggregation consistent with Enhalus; original studies already report spatial clonal structure.

## 3. Does a small quadrat's genet richness indicate neighbouring sample richness?
Descriptive nearest-K occupied complete quadrats, fixed sample number 4K, focal quadrat excluded. Spherical distance using 6371008.8m radius. Plot IDs sorted for deterministic ties. Do not interpret as continuous landscape or actual donor distance. Median nearest selected radius and rank correlations:
| K | median farthest selected quadrat (m) | mean external distinct genets | mean external genets absent at focal | Spearman local count vs external count | vs external absent-at-focal |
|---|---:|---:|---:|---:|---:|
|1|72.912|2.97985|2.88287|.04877|.03958|
|5|237.655|14.33879|14.10202|.06874|.05869|
|10|402.629|28.47229|28.16625|.10820|.09691|

For K=5, focal one-genet quadrats have mean 14.046875 external genets vs 14.549828 for focal four-genet quadrats. Local richness gives little descriptive rank information on neighbouring sample richness at these scales; no inference of independence or significance because neighborhoods overlap and study area is one lagoon. 120 genets occur at >1 sampled quadrat. No sex, phenology or realized sire identities linked to spatial data.

## Next gate
Distinguish local observed genetic richness, spatially accessible flowering genets, and realized sire richness. Different species/studies cannot be joined to claim a causal linkage. No external confirmation of Enhalus disturbance-related rank reversal, no direct test of pollination distance or sea-otter reproductive pathway. New prospective target: spatially resolved flowering adult genets matched to seed parentage in the same meadow/year, including flow/phenology; compare prediction of paternal richness and outcrossing separately against source-effort-aware references. Existing paper already studies general scales; new joint test remains unperformed.

Reproducible script analysis/145_seagrass_realized_paternity_and_spatial_redundancy.py, source member SHA checks. Numerical results computed locally from downloaded source members, new CI pending. Original Paper A and TNC unchanged; Draft/unmerged.
