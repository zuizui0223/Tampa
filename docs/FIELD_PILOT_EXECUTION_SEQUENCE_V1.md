# Tampa response-independent pilot execution sequence v1

## Purpose

Current campaign state: **STOP_RESOURCE_FREEZE_INCOMPLETE**.

This is the shortest valid execution order from that STOP state to field readiness. It changes no ecological estimator, endpoint, threshold, or sample-size gate.

## Protected priority

1. four-bay TNC-v2 primary
2. within-canopy optical DLI
3. joint hot-fresh event stress
4. hydrodynamics later / separate

Do not trade away the TNC-v2 primary to keep an optional forcing module alive.

## Stage 0 — response-independent inventory

Count real equipment and laboratory capacity before any outcome-bearing collection.

For TNC: confirm coring equipment, preservation supplies, HPLC capacity, and authority/permit conditions around permanent transects.

For optical: count complete matched systems separately for 4π scalar outcome channels/references and 2π cosine outcome channels/references. Scientific priority is 4π scalar PPFFR only when it can meet the full confirmatory resource/QC envelope. Use 2π cosine PPFD only as the frozen feasibility fallback. If neither can meet the full design, disable optical rather than mixing classes.

For event stress: count simultaneous temperature + conductivity/salinity node systems. Rotation across different weather windows is not equivalent to simultaneous deployment.

## Stage 1 — TNC-v2 method pilot

Use docs/TNC_V2_PILOT_EXECUTION_CARD_V1.md and the field/tnc_v2_* raw templates.

Resolve from non-outcome-bearing donor/field material:

- horizontal rhizome tissue class;
- least-destructive passing core diameter/depth;
- minimum safe/reproducible perpendicular transect offset;
- HPLC matrix QC;
- preservation method;
- maximum collection-to-preservation delay.

Build and validate the raw pilot. Proceed only on PASS_METHOD_PILOT, then mechanically generate the candidate precollection freeze with analysis/69_apply_tnc_v2_method_pilot.py.

A failed pilot causes response-independent method redesign. It never licenses relaxed QC.

## Stage 2 — optical method pilot in parallel where feasible

Before pilot interpretation freeze exactly one angular-response class: preferred 4pi_scalar_ppffr; fallback 2pi_cosine_ppfd.

Use results/optical_pilot_acceptance_v1_contract.json, docs/OPTICAL_PAR_METHOD_PILOT_V1.md, and docs/OPTICAL_PILOT_DATA_ENTRY_V1.md.

Pilot gates cover underwater calibration, side-by-side integrated-light consistency, vertical-profile representativeness, placement repeatability, fouling/maintenance, daylight DLI missingness, and matched above-canopy geometry when attribution is retained.

The handoff must be raw pilot files -> candidate -> PASS_OPTICAL_PILOT -> mechanically applied proposed optical freeze -> strict optical readiness validation.

After the response-independent pilot and equipment audit:

- optical primary may be confirmatory only if the full 30-node / 8-per-core-bay gate and all QC gates can be met;
- otherwise freeze optical as disabled;
- above-canopy attribution is separately confirmatory only with >=12 reference nodes and >=3 per bay; otherwise disable attribution without invalidating a valid within-canopy primary.

## Stage 3 — event sensor pilot

Confirm whether the system can support >=30 simultaneous analyzable nodes, >=8 per core bay, <=15-minute synchronized temperature/salinity, the fixed July 24–September 3 window, >=35 days common overlap, and >=85% paired coverage.

Freeze event as confirmatory only if those response-independent feasibility gates are realistic; otherwise disable it. A later lack of hot-fresh variation is handled by the frozen non-estimable rule, not by moving the season or thresholds.

## Stage 4 — freeze optional-module intent

Before the first outcome-bearing pre-TNC core/logger, all three fields must be non-null:

- event_module_intent = confirmatory or disabled;
- optical_module_intent = confirmatory or disabled;
- optical_attribution_intent = confirmatory or disabled.

These choices use only pilot pass/fail, equipment counts, access, and preservation/analytical capacity.

If only one forcing primary can be fully confirmatory without weakening TNC-v2, optical DLI has the frozen scientific priority over hot-fresh event stress. Event may proceed alone if optical fails its own gate.

## Stage 5 — final four-bay TNC execution frame

After TNC method PASS, build the contemporaneous four-bay baseline manifest.

Requirements remain >=36 analyzable planned nodes, >=6 per bay, one <=28-day TNC campaign, and fixed-transect baseline within +/-14 days of paired TNC baseline.

Validate it with analysis/70_freeze_tnc_v2_execution_manifest.py. Historical 41-node planning counts do not substitute for contemporaneous eligibility.

## Stage 6 — exact laboratory and preservation capacity

Compute exact planned sample load from the final union of forcing and TNC nodes:

6 × n(unique confirmatory event OR optical nodes) + 3 × n(authoritative TNC nodes outside that union).

Freeze preservation capacity, HPLC capacity, replacement-core ceiling, pre/post core geometry, and maximum cumulative disturbed area per node. Do not authorize a third redundant TNC round.

## Stage 7 — build integrated resource freeze from raw inputs

Use the validated TNC execution manifest, field/integrated_resource_inputs_template.json, field/integrated_forcing_execution_manifest_template.csv, and the READY optical freeze when optical is confirmatory.

Run analysis/73_build_integrated_resource_freeze.py to create candidate resource/TNC freezes. Derived values are generated mechanically rather than retyped.

## Stage 8 — strict readiness validation

Run validation/validate_integrated_campaign_readiness.py in strict mode.

Outcome-bearing collection begins only after strict READY.

## Failure rules

- TNC-v2 method or four-bay execution fails -> stop the outcome-bearing campaign.
- Optical fails -> freeze optical disabled; do not rotate fewer sensors across weather windows or mix angular classes.
- Event fails feasibility -> freeze event disabled; do not change calendar/thresholds.
- Above-canopy attribution fails -> disable attribution only; a valid within-canopy optical primary may proceed.

## Minimal next physical actions

1. Collect non-outcome-bearing Thalassia donor material.
2. Run TNC tissue/core/offset/preservation/HPLC matrix pilots.
3. In parallel, inventory scalar versus cosine optical systems and run response-independent optical calibration/profile/fouling pilots.
4. Record event logger system counts and response-independent method feasibility.
5. Only after these pilots, freeze optional-module intent and final campaign resources.

## Boundary

This sequence produces design readiness, not ecological evidence. No pilot pass supports TNC buffering, optical limitation, event stress, hydrodynamic self-facilitation, or community insurance.
