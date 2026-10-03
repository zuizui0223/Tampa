# Tampa TNC-v2 pilot data-entry and validation

## Purpose

This layer operationalizes the already-frozen response-independent pilot in `docs/TNC_V2_METHOD_FIELD_PILOT_V1.md`.

It does **not** change the scientific thresholds. It only converts them into machine-checkable input schemas.

## Input files

### HPLC matrix pilot

`field/tnc_v2_hplc_matrix_pilot.json`

Enter:

- calibration identity pass/fail;
- analytical blank pass/fail;
- post-high-standard carryover pass/fail;
- standard recovery percentages;
- pooled-Thalassia matrix-spike recovery percentages;
- technical duplicate TNC pairs;
- whether every required primary analyte falls inside the frozen calibration range for each pilot extract.

The validator applies the frozen rules:

- mean standard recovery 95–105%;
- every matrix-spike recovery 85–115%;
- median technical-duplicate CV <=10%;
- <=10% of duplicate pairs have CV >15%;
- >=90% of extracts inside calibration range;
- calibration, blank and carryover checks must all pass.

### Tissue-class pilot

`field/tnc_v2_tissue_class_pilot.csv`

Each candidate class must have at least 8 pilot specimens.

Pass:

- >=90% unambiguous classification;
- >=90% sufficient dry material;
- all retained attempts pass the destructive-sampling guardrail.

The first passing candidate in the predeclared order is selected.

### Core-geometry pilot

`field/tnc_v2_core_geometry_pilot.csv`

Each geometry must contain at least 10 attempts.

Pass:

- >=9/10 recover the frozen tissue class;
- >=9/10 yield sufficient dry mass;
- all retained attempts pass the destructive guardrail;
- all retained attempts preserve three-anchor feasibility.

The first passing geometry in the predeclared least-destructive order is selected.

### Preservation pilot

`field/tnc_v2_preservation_pilot.csv`

For each method × tested delay:

- at least 6 independent specimens;
- median absolute relative TNC difference <=10%;
- 90th percentile absolute relative difference <=15%;
- all aliquots physically suitable.

The numeric gate is machine checked.

The protocol's separate condition **"no monotonic directional drift across the tested delay sequence"** remains a response-independent review gate. The validator reports signed median difference by delay and returns `REVIEW_DIRECTIONAL_DRIFT` until `--drift-reviewed-pass` is explicitly supplied after reviewing the pilot-only diagnostic.

When drift review passes, choose:

1. the shortest operationally feasible passing preservation method in the predeclared method order;
2. the longest tested delay that passes for that method.

### Transect-offset pilot

`field/tnc_v2_offset_pilot.csv`

A candidate offset passes only if every tested placement satisfies:

- permit/no-disturbance boundary;
- permanent-transect protection;
- reproducible placement;
- restoration workspace.

The minimum passing offset is selected.

## Run

~~~bash
python validation/validate_tnc_v2_method_pilot.py
~~~

After response-independent directional-drift review:

~~~bash
python validation/validate_tnc_v2_method_pilot.py --drift-reviewed-pass
~~~

## Outputs

- `results/tnc_v2_method_pilot_validation.json`
- `field/tnc_v2_precollection_freeze_method_patch.json` only when every method/field gate passes.

The patch is **not automatically merged** into the authoritative precollection freeze. Review the pilot provenance, then copy the selected values once.

## Hard boundary

None of these input files may contain:

- future focal-frequency change;
- future Braun–Blanquet state;
- future blade length;
- future shoot density;
- any ecological outcome used to choose a method.

The validator rejects files containing obvious future-response columns/keys.
