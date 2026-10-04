# Tampa field-readiness blockers — current state

## Current status

**STOP_RESOURCE_FREEZE_INCOMPLETE**

The prospective mechanism programme is scientifically frozen far enough to begin response-independent pilots, but **outcome-bearing cores/loggers are not yet authorized**.

There are **16 unconditional unresolved fields** across the integrated campaign freeze and the authoritative TNC-v2 precollection freeze.

## Protected study

The decisive primary remains:

> four-bay baseline rhizome TNC -> future quantitative *Thalassia* change

Planning frame:

- 41 nodes;
- confirmatory minimum >=36 total;
- representation floor >=6 per bay;
- Old, Middle, Lower Tampa Bay + Boca Ciega Bay.

Do not sacrifice this design to keep an optional logger module alive.

## Pilot-file authority

The authoritative method-pilot path is now singular:

```text
raw pilot records
  -> build_tnc_v2_method_pilot_summary.py
  -> tnc_v2_method_pilot candidate
  -> validate_tnc_v2_method_pilot.py
  -> PASS_METHOD_PILOT
  -> 69_apply_tnc_v2_method_pilot.py
  -> tnc_v2_precollection_freeze.json
```

Legacy `field/tnc_v2_pilot_freeze.json`, `field/tnc_v2_pilot_manifest.csv`, and `docs/TNC_RESPONSE_INDEPENDENT_PILOT_V1.md` are provenance only and must not govern outcome-bearing sampling.

## Blocker group 1 — TNC field/laboratory pilot

Eight TNC-v2 precollection items are still unresolved:

1. campaign start date;
2. campaign end date;
3. horizontal-rhizome tissue class;
4. minimum perpendicular offset from permanent transect;
5. core diameter;
6. core depth;
7. maximum collection-to-preservation time;
8. preservation method.

The assay-batch randomization rule is now frozen before HPLC results are opened.

These eight remaining items must come from response-independent field/laboratory pilot work, not from future TNC or meadow outcomes.

## Blocker group 2 — final four-bay execution freeze

Still required:

- final four-bay TNC node registry;
- authoritative TNC baseline calendar;
- paired fixed-transect baseline calendar;
- preservation capacity for the planned core count;
- HPLC primary-assay capacity for the planned core count.

The TNC-v2 primary model and water-body-stratified node-bootstrap uncertainty code are now frozen in `field/tnc_v2_primary_analysis_freeze.json`.

## Blocker group 3 — optional forcing-module decision

Before the first outcome-bearing pre-TNC core/logger, freeze:

- event-stress module = **confirmatory** or **disabled**;
- optical module = **confirmatory** or **disabled**;
- optical above-canopy attribution = **confirmatory** or **disabled**.

Do not leave these as “maybe”.

If event or optical is confirmatory, its extra simultaneous-sensor, geometry, calendar, coverage and analysis-code gates become mandatory. If capacity is insufficient, disable that module before biological sampling rather than rotating sensors through different weather windows.

If full capacity exists for only one forcing primary, the frozen scientific priority is **within-canopy optical DLI before joint hot-fresh exposure**, while TNC-v2 remains protected above both. This priority does not override feasibility: event may proceed alone if optical fails its own full gate. See `docs/OPTIONAL_FORCING_MODULE_PRIORITY_V1.md`.

## Optical pilot is now method-frozen

The optical module no longer has an open-ended "do a PAR pilot" instruction.

Response-independent acceptance criteria are frozen in:

- `results/optical_pilot_acceptance_v1_contract.json`;
- `docs/OPTICAL_PAR_METHOD_PILOT_V1.md`;
- `field/optical_pilot_freeze.json`.

The pilot must now resolve actual hardware/field outputs under fixed gates for:

- in-water sensor calibration;
- vertical-profile representativeness;
- placement repeatability;
- fouling / maintenance;
- DLI daylight missingness.

Until `field/optical_pilot_freeze.json` becomes `READY`, `optical_vertical_profile_pilot_complete` must remain false/null in the integrated resource freeze.

This changes **method readiness**, not ecological evidence.

## What can proceed now

Response-independent work can proceed immediately:

- *Thalassia* tissue/HPLC matrix pilot;
- core-size/depth/offset pilot;
- preservation-latency pilot;
- temperature/salinity sensor calibration + geometry pilot;
- PAR vertical-profile and calibration pilot;
- equipment inventory;
- field-access/permission audit;
- route/calendar planning;
- primary analysis and uncertainty code freeze.

## What cannot proceed yet

Do not begin:

- outcome-bearing TNC coring;
- confirmatory event logger deployment;
- confirmatory optical logger deployment.

The campaign becomes READY only after the fail-closed validator reports the protected four-bay TNC primary ready and every optional module is either fully confirmatory-ready or explicitly disabled.

## Scientific boundary

This STOP state says nothing about whether TNC, light, hot-fresh exposure, hydrodynamics or community buffering are biologically important.

It only prevents logistics uncertainty from being converted into post-hoc scientific flexibility.
