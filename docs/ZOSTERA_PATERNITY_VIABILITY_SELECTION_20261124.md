# Zostera realized paternity is conditional on viability and genotyping coverage

## Original sources and scope
Sgambelluri et al. 2024, DOI 10.1002/ece3.11608; Dryad 10.5061/dryad.dfn2z358x. Original CSVs from verified artifact 14912352573. This is a post-outcome coverage diagnostic, not a refit of COLONY or a claim the published mating-system analysis is invalid. The article explicitly describes removal of low-genotyping-coverage spathes and uses a broader viability analysis. Viability is assessed seed viability in source data, not later seedling survival.

Exact join on Site, Maternal ID, Rhipidium, Spathe: 219 viability rows / 26 shoots, 162 published paternity rows, 136 high-locus rows. Unique keys; each paternity key is present in viability data, total seed denominators agree. All viability summaries use Slim_viability_by_spathe.csv without silently reconciling conflicts. Published matching rows differ in viable count in 22/162 cases (high-locus 17/136); genotyped count exceeds viable count in 5/162 in viability table and 3/162 in paternity table. Source definitions/count discrepancies require review before interpreting individual genotyping or seed fates.

## Actual source-derived results (local calculation)
| group | spathes | total seeds | viable | nonviable | mean spathe viability |
|---|---:|---:|---:|---:|---:|
| Full viability frame |219|1427|1036|391|0.776057|
| Published paternity included |162|995|942|53|0.949096|
| Published paternity excluded |57|432|94|338|0.284262|
| High-locus included |136|846|811|35|0.960539|
| High-locus excluded |83|581|225|356|0.473773|

All 23 spathes with zero viable seeds excluded in both. Published excluded spathes contain 338/391 (86.445%) of nonviable seeds. 22/26 mothers have both included and excluded spathes, and every one has higher mean viability in included group. Equal-mother mean difference +0.67705; median +0.69427. No independence assumption or p-value. At viability <=0.5, 0/44 included; viability=1, 119/123 included. Included counts by spathe position 71/83,52/66,31/42,8/28. Full viability means by position .863977,.784451,.759609,.520321; selected means .948323,.947252,.940822,1.0. Thus selection strongly changes the observed position gradient; not a new test of flowering order, which original paper already tested. High-locus cohort overlaps published cohort, not replication.

## Interpretation
Realized paternal richness is observed conditional on successful genotyping and viability-related selection. No paternity assigned to nonviable ungenotyped seeds. Do not treat unobserved fathers as zero, model paternity as a causal predictor of viability, or infer an effect of mate availability from this comparison. Collect paternity at an earlier reproductive stage, including failed seeds if technically possible, then follow individually linked fates. A joint selection/observation model alone cannot recover unidentified parentage. This is a concrete measurement requirement for connecting genetic neighbourhood, mating network, viable seed and recruit endpoints.

## Otter source correction
Wasson et al. Dryad 10.7291/D1FX0Z consists mainly of otter counts/foraging/within- versus outside-eelgrass habitat use, NOT a long-term eelgrass extent series. Official metadata checked. No analysis of effects on area until independent plant time series matched. Foster 10.5061/dryad.ns1rn8pt4 public page lists no available files; source audit pending. No new otter genetic or area effect established.

Reproduction: analysis/149_zostera_paternity_viability_selection.py. Source hashes verified in local computation. Dedicated CI added separately; pending. No Tampa Paper A or TNC changes, draft/unmerged.
