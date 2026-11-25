# Zostera: flowering order and diversity conditional on nonselfed offspring (2026-11-25)

## Question and data identity gate
Follow-up to analysis/180. Do later spathes have lower diversity even among offspring classified as outcrossed? Sgambelluri et al. 2024 DOI 10.1002/ece3.11608, Dryad 10.5061/dryad.dfn2z358x, already reports declining outcrossing and viability by spathe rank; its unstandardized sire-number position test was nonsignificant. Sgambelluri et al. 2025 DOI 10.1093/evolut/qpaf111, Dryad 10.5061/dryad.6t1g1jx7p, provides seed-level COLONY self/outcross and paternal labels, and already reports outcrossed seeds heavier than selfed. The new diagnostic standardizes offspring sample size and compares paternal-label diversity within the outcross-classified subset. It is not an independent study replication.

Original archives 14912352573 and 14916683079, SHA256 c0f4a1b0b988dc4a9f678f10cd8c413b8636585c554fd81591502b4af69d7d61 and 2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8, verified locally; all six member hashes pinned in analysis/181. Both main individual tables have 844 rows but maternal identifiers and seed identifier definitions differ: 2024 raw genotype table 26 shoots, 162 spathes, globally unique Offspring Number; 2025 mass table 35 shoots, 165 spathes, seed position within spathe. Exact site/mother key overlap 5, spathe key overlap 10, full nominal seed key overlap ZERO. The 2024 slim per-spathe summary also has a different numbering system from its raw genotype table: 3 common site/mother keys, 7 common spathe keys, only 2 agree in genotyped seed count. These are identity/mapping issues, not evidence of unrelated specimens or source error. No validated crosswalk, so no direct join, no row-order alignment or speculative renumbering. Potentially overlapping original study samples; never count the two publications or mass/area/reduced panels as independent replications. 2024 raw maternal genotype table does match the raw offspring mother keys (26/26).

## Estimand
First and last observed spathe within the same rhipidium, defined before outcome eligibility filtering in each deposited panel. Position is proxy for timing, not measured calendar date. Rarefy k=2 or 3 whole observed seeds without replacement: for an allele/label present in c of n seeds, expected contribution to richness is 1-choose(n-c,k)/choose(n,k). Average paired differences within each mother, then weight mothers equally. Bootstrap 20,000 draws of maternal shoots stratified by the three observed sites, seed 20261125. Intervals conditional on those sites and selected data, not independent population inference or confirmatory p-values. All analyses posthoc.

## 2025 directly deposited self/outcross classes and sire labels
Mass table: 844 observed seeds, 35 shoots, 165 spathes, 607 outcross-classified and 237 self-classified. Within 48 first-last pairs (24 mothers), mean outcross proportions .823371 -> .626108, difference -.197264, conditional bootstrap [-.31402,-.08791]. Equal-mother mean fraction of sampled endpoint spathes with zero outcross seeds 0 -> .20833 (8/48 last spathes, no first spathes; 7 mothers contribute increases). These are available viable/genotyped seed records, not flower failure or absence of pollen. Rarefied sire-label richness among all seeds (k=2, same 48 pairs) 1.783565 -> 1.472421, diff -.311144 [-.45122,-.15805]; k=3 (44 pairs/23 mothers) 2.389777 -> 1.846739, diff -.543038 [-.81504,-.24891].

Outcross-only diagnostic, all-seed contrast restricted to identical eligible pairs:
| panel | k | pairs / mothers | all-seed difference on same pairs | outcross first | outcross last | outcross difference | conditional 95% |
|---|---:|---|---:|---:|---:|---:|---|
| Mass | 2 | 33/19 | -.12216 | 1.720238 | 1.603383 | -.116855 | [-.30132,.06418] |
| Mass | 3 | 23/14 | -.30247 | 2.245408 | 1.856037 | -.389371 | [-.71964,-.06266] |
| Reduced mass | 2 | 31/17 | -.12014 | 1.721615 | 1.605462 | -.116153 | [-.32283,.09043] |
| Reduced mass | 3 | 23/13 | -.27285 | 2.268040 | 1.926648 | -.341392 | [-.68462,-.00211] |
| Area | 2 | 33/19 | -.11481 | 1.716729 | 1.605138 | -.111592 | [-.30242,.07832] |
| Area | 3 | 24/14 | -.28295 | 2.245536 | 1.884609 | -.360927 | [-.71352,-.00314] |

Reduced panel 693 seeds/34 shoots; two site-sire labels contain both deposited self/outcross classes, retained as recorded. Area panel 873 seeds/35 shoots. Do not regard overlapping panels as independent. Main k3 outcross site means +.07649 (4 mothers), -.31726 (6), -.96339 (4); leaving out site 3 gives -.15976, leaving out either other site -.57571 or -.44345. Difference of all versus outcross-only contrast in same eligible k3 pairs -.08690, not causal decomposition. Selection for at least 3 outcross seeds excludes many later low-outcross spathes; in these 14 mothers observed outcross proportion .9270 -> .9152, so comparison is of high-outcross subset, not population mean. No percentage of total diversity decline attributable to selfing. Father labels reconstructed by COLONY, not independently observed individual identities.

## 2024 direct offspring allele check (conditional nonself-compatible subset)
674 complete ten-locus seed records from the 844 raw genotypes. For each seed and corresponding reconstructed maternal genotype, include if at least one locus at or above confidence threshold contains exactly one nonmaternal allele, and no such locus contains two nonmaternal alleles. Conditional on correct maternal/offspring calls this is consistent with nonselfing; ambiguous seeds are NOT assigned selfing. Maternal calls were reconstructed from these same offspring and are not independent. Confidence 1 is recorded value, not certainty. Retain no father labels. At .925, 479 compatible-nonself seeds and 65 with incompatible calls (remaining ambiguous); .99:461/63; 1:406/60. Different subsets are selected, not independent error validation. Expected distinct alleles per locus after whole-seed rarefaction, average ten loci.

| threshold | k | matched pairs/mothers | all-seed diff on same pairs | conditional nonself first | last | difference | conditional 95% |
|---|---:|---|---:|---:|---:|---:|---|
| .925 |2|25/17|-.11858|1.751193|1.634566|-.116627|[-.22058,-.00464]|
| .925 |3|16/11|-.16550|1.928718|1.728279|-.200438|[-.35359,-.04135]|
| .99 |2|23/15|-.09794|1.738685|1.636952|-.101733|[-.21560,.02199]|
| .99 |3|15/10|-.15655|1.928589|1.721107|-.207482|[-.37711,-.03000]|
| 1.0 |2|19/13|-.09517|1.754252|1.644103|-.110150|[-.20116,-.01563]|
| 1.0 |3|13/9|-.10327|1.914821|1.754405|-.160417|[-.31931,.01363]|

The unconditioned k3 panel exactly reproduces prior 180 (27 pairs/16 mothers; 1.954330 -> 1.672184; difference -.282147). Within matched conditional subset, decline direction persists across all six threshold/k combinations, but intervals and site patterns vary. These are allele-richness measures, not sire richness or truly independent validation. No inferred cross-archive seed matching. Direct causal decomposition of selfing versus paternal diversity requires verified crosswalk and parentage, viable/nonviable sampling, measured flowering timing and donor availability.

## Implications and status
Stage-specific risk hypothesis: fewer realized outcrossed seeds AND reduced diversity among those that remain may accompany later reproductive positions. The evidence is conditional/exploratory; not proof of seasonal pollen-source exhaustion, spatial isolation, reduced germination, or general marine pattern. Distinguish these candidate mechanisms from selective maturation and assignment error. No new flow/donor-coordinate data, no meta-analysis. Local executed code exact Git blob 9bb52e98ec77ad0cdfcc3514337e0a427de4a1b4 matches committed script; result JSON SHA256 8aef967cdd4682d8fe9f5eac0596acc01fa9cdf3cb36a3e86c41a396bea07b68. Independent CI not run. Reproduce: python analysis/181_zostera_flowering_order_outcross_diversity.py <2024 verified archive> <2025 verified archive> --out results.json. Draft exploratory reproductive-interaction branch only; no merge, submission or Paper A/TNC changes.
