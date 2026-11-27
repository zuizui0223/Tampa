# Cross-region meadow identity and conditional compositional reference (2026-11-27)

## Executed result
Reaggregated exact source summaries at 19e659ca8d9527fc48b0dccebdda34ee7a6c1835, with Git blob verification, in JS. The function was executed on the fetched bytes' decoded text in the connector runtime; the offline Node wrapper and the new raw-source workflow have not yet been independently replayed. No new independent raw survey was obtained in this step.

| Panel | Prior taxon not recorded later | Another seagrass recorded | Conditional masking fraction |
|---|---:|---:|---:|
| Tampa, Thalassia, 1-year, target years 2016–2025 | 370 | 302 | 81.62% |
| Torres lobster survey, 1-year, all prior taxa | 583 | 446 | 76.50% |
| Torres cucumber survey, 2-year, all prior taxa | 39 | 36 | 92.31% |

Torres lobster has 1,375 prior-taxon × station-year-pair incidences, 792 reobserved, 137 with all grass not recorded and 446 selective non-recordings. Nine taxa: leaving each taxon out gives 74.70–80.76%; equal weighting of nine taxa 80.27%. Cucumber has 220 incidences, 181 reobserved, 3 all-grass non-recordings, 36 selective non-recordings; small denominators. These are conditional on focal non-recording, not true loss or region/lag effect estimates. Meter marks and survey coordinates differ; pooled incidences are dependent. The repeated-survey labels do not denote animal treatments. Presence and taxon re-observation are nested algebraically; do not infer biological mechanism from the observed masking alone.

## Next actual data test
Define a separate diagnostic for Torres already opened raw source, not new Tampa retrospective mechanism mining. In both-positive transitions, compare species overlap with shuffled target assemblages, preserving target year, exact initial and later richness and 2-m depth bins (1-m, 5-m, no-depth sensitivity). Exclude strata with no alternative target composition and report coverage. Compute exact expected retention/Jaccard/no-overlap and shuffled reference ranges; no p-value due repeated station dependence and spatial exchangeability limits. A difference from this reference would test compositional specificity beyond these measured margins, not establish true mortality, competition, or ecosystem functions. All choices response-open, no claim of preregistration or new holdout. Source archive pinned and workflow fail-closed; no raw-result claim until successful execution.

## Boundaries
This is a small cross-region synthesis plus a new executable reference diagnostic, not a completed macroecological theory or independent meta-analysis. Main manuscript and TNC protocol unchanged. Source: Carter et al. DOI 10.26274/2CR2-JK51; TBEP pinned occurrence and event. 

## Executed raw-source result
GitHub Actions run 45981390619, job 140445885799, artifact 15190135356, digest sha256:bc4dcceedafd4e36ede7a811f0449067ca01b9b8b77a9b75abe47e1ae359462a; all identity job steps passed. Prior summary exact replay, archive and inner checks, synthetic check and real original-row analysis passed. Full output recovered from job log JSON and stored with provenance in results/meadow_richness_reference_verified_20261127.json.

| Water depth matching | Lobster 1y movable/416 | Observed/expected prior-taxon retention | Difference pp | Cucumber 2y movable/98 | Observed/expected | Difference pp |
|---|---:|---:|---:|---:|---:|---:|
| 2 m (primary) | 46 | 59.89/58.52% | +1.37 | 50 | 85.67/86.68% | -1.01 |
| 1 m | 26 | 55.26/56.06% | -0.80 | 43 | 83.33/84.86% | -1.53 |
| 5 m | 109 | 60.86/54.91% | +5.94 | 61 | 88.25/88.66% | -0.41 |
| No depth | 267 | 62.73/55.61% | +7.13 | 75 | 90.00/90.14% | -0.14 |

Strict 2m reference: both panels inside their simulated reference ranges. Coarse/no-depth lobster excess outside descriptive shuffle ranges; no consistent excess at finer depth matching and markedly different eligible subsets (11.1% at primary vs 64.2% no depth). Cannot infer that depth causes or explains the difference; not an inferential null test and not evidence of universal species-specific memory. Hypothesis: composition memory beyond measurable habitat sorting, if present, may depend on environmental heterogeneity and study grain; require independent comparable monitoring, explicit observation process and matched coverage. Do not conflate this with previous focal loss conditional masking. No new Tampa fits, manuscript or protected TNC changes.
