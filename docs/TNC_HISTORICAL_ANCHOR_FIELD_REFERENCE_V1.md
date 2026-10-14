# Historical four-bay *Thalassia* anchor field-reference crosswalk

**Evidence status:** `HISTORICAL_REFERENCE_NOT_A_FROZEN_FUTURE_ANCHOR_MANIFEST`  
**Source period:** 2023–2025 (latest eligible observed year at each stable transect)  
**Source:** `analysis/62_tnc_anchor_bb_four_bay_preflight.py`, using `tbep-tech/obis-example` pinned commit `6c567beff95ea04f0e397101befb49d5233ace8f`.  
**Verifiable historical artifact:** GitHub Actions run [#36809312012](https://github.com/zuizui0223/Tampa/actions/runs/36809312012), artifact `11139536974`, ZIP SHA256 `f47bfffafec51afb689ed53a42394cb8c69288f2ecccafa0da75df67343f4289`.

## What the source actually supports

The original preflight identifies 41 recently *Thalassia*-positive fixed transects, **38** with three distinct positive q25/q50/q75 marks and numeric baseline Braun–Blanquet (BB) at those marks. The former-positive marks are not invented or inferred from a percentage: the source uses the fixed point locationID, selects three distinct marks near the quartiles of the latest positive marks, and matches to their quantitative BB observations.

| Bay | Historical positive nodes | Historical three-mark quantitative candidates |
|---|---:|---:|
| Old Tampa Bay | 8 | 8 |
| Middle Tampa Bay | 11 | 10 |
| Lower Tampa Bay | 14 | 12 |
| Boca Ciega Bay | 8 | 8 |
| **All four bays** | **41** | **38** |

Exactly **114 archival anchors** therefore have unique (node ID, metre mark) combinations.

The three historical nodes *without* a three-mark quantitative candidate are:

- Middle Tampa Bay `TBEP:seagrass:loc:S3T1`: one positive mark;
- Lower Tampa Bay `TBEP:seagrass:loc:S4T9`: two positive marks;
- Lower Tampa Bay `TBEP:seagrass:loc:S4T13`: one positive mark.

These are **historical records**, not permanent exclusions from a newly surveyed four-bay frame. The raw latest-year references are from 2024 or 2025 and must not be called 2026/2027 physiological measurements.

## Output and reproducibility

`analysis/83_export_tnc_historical_anchor_reference.py` consumes the unchanged preflight JSON and writes:

- `historical_tnc_anchor_marks_2023_2025.csv`: all 114 archival selected anchor records with fixed node ID, bay, latest historical year, q25/q50/q75 class, exact historical metre mark, historical mean BB, and explicit **Not checked** present-day status;
- `historical_tnc_candidate_nodes_2023_2025.csv`: all 41 archival nodes including three sparse nodes, again labelled as **Not checked** for contemporary eligibility;
- `historical_tnc_anchor_reference_v1.json`: source-period/commit provenance, counts and interpretation restrictions.

These are produced under `results/generated_tnc_anchor_bb_four_bay/` and archived by the existing [TNC four-bay preflight workflow](../.github/workflows/tnc-anchor-bb-four-bay-preflight.yml), **without changing the original preflight** or the frozen TNC inferential models.

Run after the original preflight:

```bash
python analysis/83_export_tnc_historical_anchor_reference.py --self-test
python analysis/62_tnc_anchor_bb_four_bay_preflight.py \
  --out results/generated_tnc_anchor_bb_four_bay/tnc_anchor_bb_four_bay_preflight_v1.json
python analysis/83_export_tnc_historical_anchor_reference.py
```

The source's exact original 2023–2025 quantitative marks, not a newly optimized selection, determine the map.

## Critical prospective boundary

**Do not core from this archival crosswalk.** It is a reconnaissance/reference map to facilitate field confirmation, not a substitute for the **authoritative response-independent contemporaneous** node/date/anchor registry or the conservation authority's no-disturbance permit conditions.

Before any outcome-bearing core:

1. Re-survey present *Thalassia* and local quantitative BB at each contemporary candidate mark; preserve the source locationID, real metre-mark identity and q25/q50/q75 correspondence.
2. Confirm three unique spatial anchors, site permissions, selected core offset and non-disturbance of permanent monitoring microquadrats. Do not assume the historical q25/q50/q75 marks are still eligible or select alternatives based on later TNC/future response.
3. Populate the existing `field/tnc_v2_execution_manifest_template.csv` with real node/date values and run `analysis/70_freeze_tnc_v2_execution_manifest.py`. The node/date manifest is **not** an anchor-identity freeze; maintain the separate location-level provenance before first outcome-bearing sample.
4. Retain the frozen prospective gate: **>=36 complete three-anchor nodes total and >=6 per bay**. Four-bay node-level cross-node prediction is supportive and cannot rescue an inestimable decisive within-meadow comparison.

Any single corrupted or unmatched anchor makes that node unusable for the future three-anchor primary under the frozen contract. Archive historical BB values for provenance only—**never silently substitute them for the contemporary baseline BB**.

No future response, TNC concentration, survival, reserve buffering mechanism, or treatment effect has been measured by this crosswalk.
