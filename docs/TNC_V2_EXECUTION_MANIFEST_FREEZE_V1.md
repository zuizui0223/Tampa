# Four-bay TNC execution-manifest freeze v1

## Purpose

The historical planning frame of 41 nodes is **not** the final outcome-bearing registry. Final eligibility must be rechecked from the contemporaneous baseline state.

Use:

```text
analysis/70_freeze_tnc_v2_execution_manifest.py
```

with a CSV containing only:

- `node_id`
- `water_body`
- `thalassia_positive`
- `tnc_date`
- `baseline_survey_date`

A blank template is stored at:

- `field/tnc_v2_execution_manifest_template.csv`

The utility refuses future/outcome columns.

## Pass conditions

It mechanically enforces the authoritative v2 rules:

- baseline *Thalassia*-positive nodes only;
- four prespecified bays;
- >=36 eligible nodes total;
- >=6 per bay;
- all TNC dates span <=28 days;
- each fixed-transect baseline survey is within +/-14 days of its TNC collection;
- no duplicate node IDs.

A passing result emits the exact payload needed to populate:

- `final_four_bay_tnc_nodes_by_bay`;
- `four_bay_authoritative_tnc_baseline_calendar`;
- `four_bay_baseline_transect_calendar`;
- TNC-v2 campaign start/end dates.

The script validates; it does **not** choose nodes. If too few nodes pass, the study falls below the frozen gate rather than changing the criterion.

## Why this matters

The present 41-node count is useful planning context, but copying it into the final freeze before the contemporaneous baseline would turn an old state snapshot into a future eligibility decision.

This bridge keeps the final registry response-independent while avoiding manual transcription errors.
