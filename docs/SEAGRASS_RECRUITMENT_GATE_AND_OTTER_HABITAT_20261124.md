# Recruitment gates and otter habitat use (2026-11-24)

## Balestri original-source pot accounting
Balestri et al. 2021, DOI 10.1111/1365-2664.13980; Dryad 10.5061/dryad.t76hdr81n. Workbook member SHA256 cbfc07553ee6e071e83579784171c66d6dab8dcc589e2bdb92ee11d74d1aa2b1, from verified artifact 14911175880. Original paper already established density-dependent facilitation (density × Cymodocea interaction PERMANOVA p=.023). Novel scope is post-hoc descriptive decomposition of surviving seedling counts into observed fraction of pots with any survivors and conditional count. All pots in one outdoor tank; four pots/cell, six cells, initial 1/2/4 seedlings. No genetic identity or postzygotic genetic selection measured.

| initial seedlings/pot | partner | survivors / planted | pots with survivors / total | survivors per surviving pot |
|---|---|---:|---:|---:|
|1|absent|1/4|1/4|1|
|1|present|0/4|0/4|undefined|
|2|absent|1/8|1/4|1|
|2|present|5/8|4/4|1.25|
|4|absent|5/16|4/4|1.25|
|4|present|11/16|4/4|2.75|

Partner difference in mean survivors per pot: -.25, +1.0, +1.5. At density 2, symmetric product accounting attributes +.84375 (84.375%) of +1.0 to the difference in occupied-pot fraction and +.15625 to conditional count. At density 4, all +1.5 is conditional count; occupancy unchanged. This is exact arithmetic of group means, NOT causal mediation, an independent replicated general rule, or occupancy in nature. Two-sided 70 pot-label reallocations within each density under exchangeability give exploratory unadjusted p=1,.114286,.085714; do not claim new significant pairwise effects. Published factorial analysis remains the correct reference.

Germination experiment has 36 pots, 12/density, initial 1/3/6 seeds; reported means 91.6667/97.2167/94.4333%, respectively. Separate seed batches and treatments; do not multiply germination and seedling endpoints to estimate a full life cycle. Source survival/biomass positive status disagrees in low-density no-partner Excel rows 3 and 4 (0% survival but .529g; 100% survival but 0g). Use only survival column for above result, no swapping or individual biomass-survival fit. C. nodosa sheet group means biomass alone 4.254g, with low/medium/high P. oceanica density 3.111/3.09475/6.14925g. No common pot identifier joining sheets; do not infer reciprocal individual effects. Code analysis/150_balestri_recruitment_gate.py executed locally on pinned source.

## Otter source result
Run 45384552468 completed successfully, including earlier Posidonia adult reference coverage check. Artifact 14915263618 ZIP SHA256 33f33287a6e36c6fbfe8a0d27f2e60715e0ecd8625bcc8752146eff3b83dfb1f independently verified. Foster file listing returned two records (792060, 792061), neither has advertised download link, hence official access gate STOP; do not guess or bypass. Wasson/Eby data DOI 10.7291/D1FX0Z successfully acquired (four CSVs and README), not an eelgrass area time series.

Seal Bend paired habitat-use CSV SHA256 99820885ece8398dd0a438b9329c65a00404b4a55ef88d492e533711f7e70b3d; 59 unique survey dates, 2018–2020. Eelgrass density 0.9410634 vs open water .1458415 otters/ha (ratio 6.45264); higher in 52/59 dates, lower 7, ties 0. Annual ratios 4.99508 (n=5), 7.33026 (n=30), 6.11574 (n=24). Repeated observations, no independent animals or meadows, no plant response or direction of effect. Original Eby et al. 2022 already compared habitat densities. Code analysis/151_otter_habitat_use_paired_audit.py, post-hoc descriptive aggregation. Do not claim an otter-induced feedback or genetic effect.

## Genetic intermediate endpoint
Source candidate: Sgambelluri et al. 2025 Dryad DOI 10.5061/dryad.6t1g1jx7p (Maternal quality, paternal effects, and sibling interactions influence seed size in the eelgrass, Zostera marina). Public README describes seed-level mass, sire, selfing, maternal/paternal/offspring heterozygosity, structure positions; only viable seeds genotyped. This is a promising directly matched intermediate endpoint, NOT survival after germination; verify sample overlap with 2024 study and avoid treating them as independent experiments. Existing paper already models these predictors; a new diagnostic must not simply replicate the published model and call it novelty. Also Rhode & Duffy 2004 DOI 10.3732/ajb.91.2.192 found selfing increased seed production in Chesapeake Bay experimental crosses, while Hämmerli/Reusch results elsewhere differ; no assumption that outcrossing universally increases fitness.

Prioritize the seed-mass archive inventory and matched unit audit. Do not treat green inventory workflow as proof of access. No changes to Paper A, TNC, or causal claims. New CI pending; keep draft/unmerged.
