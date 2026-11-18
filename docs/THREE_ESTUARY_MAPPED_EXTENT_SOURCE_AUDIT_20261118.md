# Three-estuary mapped-seagrass trajectory audit (public sources, 2026-11-18)

## Source status and scientific question

This is **a new descriptive source-backed cross-estuary area comparison**, not a model of original transect states, not a re-analysis of biological workbook data, and **not** a held-out confirmation of the Tampa next-year recorded-loss forecast. Data source values were visible in publicly released agency reports before the script was constructed; the computation is reproducibility/QC, not preregistration.

The ecological question is narrow:

> Was the broad 2018–2020 seagrass areal contraction shared among Tampa Bay, Charlotte Harbor and Sarasota Bay, and did their later 2022–2024 mapped extent trajectories remain aligned?

The source-consistent answer is **shared areal contraction followed by descriptively divergent changes**. This is consistent with but does not identify different recovery environments, mechanisms or buffer strengths.

## Primary public source

- **Southwest Florida Water Management District**, 2026 Board-approved *Consolidated Annual Report* (March 2026), Strategic Plan Annual Work Plan, mapped seagrass time series for Tampa Bay, Charlotte Harbor and Sarasota Bay: https://www.swfwmd.state.fl.us/sites/default/files/medias/documents/Board%20Approved%202026%20Consolidated%20Annual%20Report.pdf
- Extracted reported numeric acreage labels in \`results/regional_extent_public_sources_v1.csv\` with \`source_id=SWFWMD_2026\`. This is a common reporting organization but **not** a guarantee that estuaries have equal mapping error, identical spatial area or comparable plant functional states.
- This paper's retrospective Tampa fixed-transect biological source (1997–2025, 71 nodes, species-specific state and plant structure) is an **independent measurement layer**, not combined with these polygon-acreage totals.

### Reproducible primary contrasts (reported area, not species-specific)

| Estuary | 2016 (acres) | 2018 | 2020 | 2022 | 2024 | 2018–20 | 2022–24 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tampa Bay | 41,655 | 40,652 | 34,297 | 30,135 | 31,562 | −15.63% | +4.74% |
| Charlotte Harbor | 20,280 | 19,715 | 15,273 | 14,913 | 14,020 | −22.53% | −5.99% |
| Sarasota Bay | 13,469 | 12,853 | 10,540 | 9,963 | 11,876 | −18.00% | +19.20% |

All three 2018–2020 contrasts are negative. The 2022–2024 signs diverge (+ / − / +), **not** a universal absence of regional recovery and **not** evidence that one specific bay is resilient in a causal sense. Against 2016, all three remained smaller in 2024. The 2016-normalized acreage range among the three is only **1.63 index points** in 2022 (72.34–73.97) but **19.04 points** in 2024 (69.13–88.17). These are **descriptive** ranges from three estuaries, not independently estimated sampling confidence intervals or evidence of a universal recovery process.

### Historical report suggests a possible cross-scale lag, not validation

- The Coastal & Heartland National Estuary Partnership's *Seagrass in Charlotte Harbor* fact sheet (circa 2023, https://chnep.wateratlas.usf.edu/upload/documents/Charlotte-Harbor-Seagrass-Fact-Sheet.pdf) states that both *Thalassia testudinum* and *Halodule wrightii* declined at multiple monitoring locations from **2016–2017**, while areal mapped coverage fell sharply in **2018–2020**.
- This is independently reported chronology. It offers an observation consistent with local biological indices changing before coarse mapped extent, but is **not** a calibrated lead-time model: the published narrative does not establish that the declining transects correspond spatially to later-lost mapped polygons, nor that observation effort, detection, species differences, storms and timing were controlled.
- A separate long-term official report (Florida DEP, 1999–2016 CHAP seagrass transects) documents fixed repeat quadrats and excludes annual shifting bed-edge quadrats from comparable analyses: https://floridadep.gov/sites/default/files/CHAP-Seagrass-Report-1999-2016.pdf

## Critical official-source disagreement

A different public chart in that CHNEP fact sheet reports **Charlotte Harbor** acres as:

| Year | SWFWMD 2026 acreage | CHNEP fact sheet acreage | SWFWMD minus CHNEP |
|---|---:|---:|---:|
| 2016 | 20,280 | 17,329 | +2,951 |
| 2018 | 19,715 | 16,938 | +2,777 |
| 2020 | 15,273 | 13,355 | +1,918 |
| 2022 | 14,913 | 13,098 | +1,815 |

The exact spatial boundaries, imagery processing and revisions **have not been reconciled**. The two series must never be spliced into one estuary history or combined as duplicate independent samples. Their separately computed 2018–2020 percent changes are directionally consistent (SWFWMD **−22.53%**, CHNEP graph **−21.15%**), which supports only a **qualitative loss direction robustness check**, not identical magnitude or spatial footprint.

The CHNEP fact-sheet prose describes **3,648 acres** lost in 2018–2020, while the printed chart labels **16,938 → 13,355** imply **3,583 acres**—a **65-acre** discrepancy. Use the chart labels consistently for the plotted alternate series and disclose the difference. The SWFWMD report's Sarasota 2022 narrative mentions 9,962 acres while the mapped table displays 9,963; retain the primary table rather than selectively mix them.

## What the ecology does and does not say

**Grounded observations:**
- Cross-estuary mapped areal decline is regionally coincident in 2018–2020.
- The 2022–2024 direction differs among the three mapped estuaries.
- Published Charlotte Harbor field monitoring reports species abundance changes in 2016–2017, preceding its later mapped contraction.
- Tampa's own long-term transect panel provides separate focal-frequency, abundance, shoot density and blade-stature information; prior work found no supported universal one-year condition → thinning sequence.

**Hypotheses to test with actual linked measurements:**
- Disturbance inputs can be relatively synchronous while recovery is filtered by local meadow attributes, exposure and community composition.
- Changes in species-specific quantitative state could precede mapped area contractions, but the extent, probability and mechanisms of any lag require **same-polygon paired survey and imagery data**, detection-aware follow-up, and prospective validation.

**Not established:**
- A universal environmental forcing, taxon response, buffering mechanism, confirmed mortality, or conservation treatment benefit.
- A spatially joined species state-to-extent causal transition or a reliable early-warning lead time.
- Any standard error or inference about a population of estuaries from these three named cases.

## Separation from Charlotte Harbor registered workbook

The Program 570 SEACAR original 1999–2025 workbook **remains inaccessible without the data-portal email registration**. Public agency **aggregate outcome summaries have now been inspected**, so any later use of that workbook is **not fully response-unseen** at the study/topic level even if raw row-level data remain unopened. That limitation must be recorded in PR #162 and future publication methods. This public series analysis is independent of the frozen PR #162 field-level estimability gates and changes no prior early-warning terminal results.

## Reproduction

\`\`\`bash
python -m unittest discover -s validation -p 'test_regional_mapped_extent_public_audit.py' -v
python analysis/90_regional_mapped_extent_public_audit.py --output results/generated_regional_extent_public_audit_v1.json
\`\`\`

Inputs and precise scope registry:

- \`results/regional_extent_public_sources_v1.csv\`
- \`results/regional_extent_public_sources_v1_registry.json\`

The script **fails closed** if an anchor value or a source ID is changed, missing or duplicated. It does not fetch biological outcome data, fit a response model, or convert unvisited marks to zero.


## Mechanistic hypothesis for a distinct future study: macroalgal recovery gate

The same 2026 district report describes Charlotte Harbor's 2018–2020 losses as coincident with a major expansion of filamentous macroalgae. It also describes the **2022–2024 Sarasota Bay areal rebound** alongside improving water quality and a reduction in macroalgae. These are **agency interpretations of associations**, not a quantitative matched-site cause-and-effect test, nor evidence of a uniquely new mechanism.

A testable cross-estuary prediction follows:

> Following extensive mapped seagrass loss, *future reoccupation* of previously vegetated bottom is less likely where macroalgal cover remains high at the **start** of a recovery interval, conditional on prior seagrass history, depth, mapped habitat suitability, and bay-wide time effects.

Candidate independent analysis unit: fixed spatial cells historically classified as seagrass in 2016, then recorded without seagrass in a **consistent 2022 mapping product**, followed forward to 2024, with raw macroalgae polygons and stable mapping footprint validation. Explicitly distinguish never-vegetated habitat from previously vegetated but subsequently lost cells. Treat macroalgae observed concurrently in 2024 as a **post-outcome correlate**, never an unlagged causal predictor.

Pre-outcome exposure: fractional macroalgal cover of each cell in 2022 (or earlier), with clear distinction between *attached* and *drift* macroalgae and evidence of mapping comparability. Primary endpoint: reappearance of mapped seagrass in 2024 in the previously vegetated/lost cells. Spatial dependence, classification error and the fact that "algae" and "seagrass" may be mutually exclusive map labels must be audited; apparent anticorrelation from exclusive classification is not ecological competition. Report temporal association only, not competition or restoration effect.

For generality, require at least multiple independent estuaries, hold out an entire estuary when evaluating transportability, and show uncertainty clustered spatially rather than treating adjacent 10–30 m cells as independent replicates. **No macroalgae areas, cell transitions or coefficients were downloaded or estimated here**. This hypothesis is a proposed discriminating experiment following the source-backed descriptive contrast.
