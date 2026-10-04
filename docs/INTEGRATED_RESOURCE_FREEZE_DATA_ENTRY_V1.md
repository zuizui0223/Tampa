# Integrated Tampa resource-freeze raw-data pipeline v1

## Purpose

The authoritative campaign resource freeze is fail-closed, but it should not be populated by hand.

This layer turns response-independent field logistics into a candidate freeze:

```text
TNC execution manifest
+ resource inventory / module intent
+ forcing node/calendar manifest
+ optical method-pilot freeze
        |
        v
build_integrated_resource_freeze.py
        |
        +--> integrated_campaign_resource_freeze_candidate.json
        +--> tnc_v2_precollection_freeze_execution_candidate.json
        |
        v
validate_integrated_campaign_readiness.py
```

The builder **never overwrites**:

- `field/integrated_campaign_resource_freeze.json`;
- `field/tnc_v2_precollection_freeze.json`.

Only reviewed candidates may later replace authoritative freezes.

## Inputs

### 1. Four-bay TNC execution manifest

First run the existing response-independent TNC manifest validator:

```bash
python analysis/70_freeze_tnc_v2_execution_manifest.py \
  --manifest <contemporaneous_manifest.csv> \
  --out results/tnc_v2_execution_manifest_candidate.json
```

The builder requires:

- `status = PASS_EXECUTION_MANIFEST`;
- no future/outcome columns;
- >=36 eligible nodes;
- >=6 per bay;
- one <=28-day TNC campaign;
- baseline survey within +/-14 days.

The resource payload from this file supplies:

- final four-bay TNC node registry;
- authoritative TNC baseline dates;
- paired fixed-transect baseline dates;
- TNC-v2 campaign start/end.

### 2. Resource inputs

Copy:

- `field/integrated_resource_inputs_template.json`

to a local response-independent working file.

Freeze:

- event module = `confirmatory` or `disabled`;
- optical module = `confirmatory` or `disabled`;
- optical attribution = `confirmatory` or `disabled`;
- simultaneous system counts;
- preservation and HPLC capacities;
- event sensor/calibration rule and geometry-pilot status;
- cumulative pre/post coring geometry.

Do not infer equipment availability from the statistical design.

### 3. Forcing execution manifest

Copy:

- `field/integrated_forcing_execution_manifest_template.csv`

and supply one row per candidate core-three node used by event and/or optical modules.

Columns:

- `node_id`
- `water_body`
- `event_selected`
- `optical_selected`
- `optical_reference`
- `pre_visit_date`
- `post_visit_date`
- `logger_deployment_date`
- `logger_retrieval_date`

Allowed bays are Old, Middle and Lower Tampa Bay.

All dates are ISO `YYYY-MM-DD`.

The builder rejects headers containing future/outcome/response tokens.

If both event and optical are disabled, the manifest may contain no selected rows.

## Automatically imported states

The builder does not ask a human to retype already frozen information.

It imports:

- TNC registry/calendars from the validated execution manifest;
- TNC primary and node-level uncertainty freeze booleans from the authoritative resource skeleton;
- event/optical primary-analysis freeze booleans from the authoritative skeleton;
- forcing-family analysis freeze from the authoritative skeleton;
- optical sensor model, calibration manifest, vertical-profile readiness and above-canopy clearance from `field/optical_pilot_freeze.json` **only when that file is READY with retained pilot provenance**.

If optical is marked confirmatory while the optical method freeze is not READY, the candidate remains incomplete and the existing readiness validator stops it.

## Build

```bash
python analysis/73_build_integrated_resource_freeze.py \
  --resource-inputs <integrated_resource_inputs.json> \
  --forcing-manifest <integrated_forcing_manifest.csv> \
  --tnc-execution results/tnc_v2_execution_manifest_candidate.json \
  --resource-base field/integrated_campaign_resource_freeze.json \
  --tnc-base field/tnc_v2_precollection_freeze.json \
  --optical-freeze field/optical_pilot_freeze.json \
  --resource-out field/integrated_campaign_resource_freeze_candidate.json \
  --tnc-out field/tnc_v2_precollection_freeze_execution_candidate.json
```

## Validate

```bash
python validation/validate_integrated_campaign_readiness.py \
  --freeze field/integrated_campaign_resource_freeze_candidate.json \
  --tnc-freeze field/tnc_v2_precollection_freeze_execution_candidate.json \
  --optical-pilot-freeze field/optical_pilot_freeze.json \
  --out results/integrated_campaign_readiness_candidate.json \
  --strict
```

The validator remains authoritative for scientific readiness.

## Claim boundary

This pipeline is logistics/design infrastructure, not ecological evidence.

A passing candidate does not support TNC, optical or event-stress biology. It only demonstrates that the predeclared prospective design can be executed without silent sample-size, timing, capacity or module-intent changes.
