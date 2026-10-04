# DEPRECATED — superseded pilot design record

**Do not use this document to make current TNC-v2 method decisions.**

This is retained only for provenance. The authoritative response-independent method/field pilot is now:

- `docs/TNC_V2_METHOD_FIELD_PILOT_V1.md`
- `field/tnc_v2_method_pilot.json`
- `validation/build_tnc_v2_method_pilot_summary.py`
- `validation/validate_tnc_v2_method_pilot.py`
- `analysis/69_apply_tnc_v2_method_pilot.py`
- `field/tnc_v2_precollection_freeze.json`

The legacy `field/tnc_v2_pilot_freeze.json` and `field/tnc_v2_pilot_manifest.csv` must not be used for outcome-bearing protocol decisions.

---

# Tampa TNC response-independent pilot v1

## Purpose

This pilot freezes the Thalassia testudinum field/laboratory method before any future meadow response exists.

It is not an ecological test and it must never inspect future frequency, Braun-Blanquet state, blade length, shoot density, decline class, or any other future response.

The pilot answers four technical questions:

1. which single horizontal-rhizome tissue rule can be harvested consistently;
2. what is the smallest practical core geometry that reliably supplies enough dry tissue;
3. which soluble-NSC extraction solvent is technically suitable for Thalassia under the frozen HPLC workflow;
4. what collection-to-preservation delay can be tolerated under a predeclared technical-bias rule.

Once frozen, these choices cannot be changed because of a future ecological result.

## Literature basis

Analytical backbone:

Sørensen et al. 2018, Aquatic Botany 151:71-79, DOI 10.1016/j.aquabot.2018.08.006.

The study showed that HPLC estimates were substantially more accurate/precise than the tested colorimetric assay, and that extraction solvent and starch gelatinization materially change NSC estimates. It also recommends a preliminary solvent test when transferring the workflow to a seagrass species other than Zostera muelleri.

The Tampa pilot therefore freezes HPLC as the analytical principle and allows one response-independent Thalassia pooled-matrix comparison of exactly three published soluble-NSC solvent classes:

- water;
- ethanol/water;
- methanol/water.

No fourth solvent may be introduced after results are inspected.

Older Florida work shows strong seasonal variation in Thalassia rhizome carbohydrate, so the prospective <=28-day campaign remains unchanged.

## Pilot specimens must be outside the future-response cohort

Pilot donor tissue must come from non-primary donor patches or sacrificial locations permanently excluded from the future four-bay inferential cohort before pilot collection.

A pilot donor location can never later become a confirmatory future-response node.

## Phase P0 — pre-pilot freeze

Before the first pilot core, fill every required field in:

field/tnc_v2_pilot_freeze.json

The pilot validator stops while any required field is missing.

Pre-pilot items include:

- one exact horizontal-rhizome tissue rule;
- candidate core geometries actually available in the field;
- minimum dry mass required by the receiving HPLC laboratory for soluble NSC + starch + archive/QC aliquot;
- candidate preservation workflows feasible in Tampa;
- candidate collection-to-preservation delays;
- calibration / accuracy / precision limits supplied by the analytical laboratory;
- solvent-selection rule;
- core-geometry selection rule;
- preservation-delay selection rule.

### Tissue rule is not optimized on concentration

The exact tissue class is chosen before pilot chemistry.

If that tissue class proves technically infeasible, close pilot v1 and create a versioned pilot v2. Do not compare multiple ontogenetic tissue classes and choose whichever yields the strongest or most variable TNC signal.

## Phase P1 — field mass/geometry pilot

Use donor points only.

For every candidate geometry, record:

- horizontal-rhizome wet and dry mass;
- whether the tissue rule was unambiguous;
- processing time;
- disturbed sediment volume.

Do not use measured TNC concentration to select diameter or depth.

### Geometry decision

A geometry must reach the predeclared dry-mass sufficiency proportion.

Among passing geometries, select the smallest disturbed sediment volume.

Tie-break:

1. smaller diameter;
2. shallower depth;
3. shorter median processing time.

If none pass, stop.

## Phase P2 — Thalassia HPLC matrix pilot

Create homogenized pooled rhizome matrices from donor tissue, then split each matrix into technical aliquots so solvent comparisons are not confounded with biological variation.

Compare only:

- water;
- ethanol/water;
- methanol/water.

For each solvent record:

- calibration QC;
- spike/reference recovery;
- replicate precision;
- soluble NSC yield;
- chromatographic interference;
- analyst/instrument failures.

Only solvents passing all predeclared analytical QC limits are eligible.

Default frozen selection logic:

among QC-passing solvents, choose the highest mean soluble-NSC extraction yield from the same pooled matrices; if differences fall inside the predeclared equivalence tolerance, apply the predeclared workflow/safety tie-break.

This is an extraction-efficiency decision, not an ecological association test.

## Phase P3 — preservation-delay pilot

Use a homogenized donor-tissue batch assigned to the predeclared preservation workflows and delays.

Compare every delayed aliquot with the predeclared immediate/reference workflow under the same final HPLC method.

Freeze the longest operationally useful delay whose TNC bias remains inside the predeclared tolerance and whose analytical QC passes.

If no field-feasible delay passes, use the immediate reference workflow or redesign under a new pilot version.

## Phase P4 — generate the precollection freeze

After a passing pilot, write:

results/tnc_v2_pilot_decision.json

It must contain one final value for:

- horizontal rhizome tissue class;
- core diameter and depth;
- minimum transect offset;
- preservation workflow;
- maximum collection-to-preservation delay;
- soluble-NSC solvent;
- starch workflow;
- HPLC QC criteria;
- assay-batch randomization rule.

Copy those values verbatim into:

field/tnc_v2_precollection_freeze.json

Only after that file is complete may validation/validate_tnc_v2_baseline.py accept outcome-bearing baseline cores.

## Hard failure rules

Pilot v1 fails if:

- pilot tissue comes from future-response nodes;
- tissue class changes after TNC concentrations are seen;
- a fourth solvent is introduced after results;
- analytical QC limits are written after pilot results;
- no core geometry supplies adequate dry mass under the frozen pass rate;
- no preservation delay/workflow passes;
- future meadow-response information enters any pilot decision.

A failure triggers a versioned redesign, not a within-v1 rescue.

## Interpretation boundary

Passing this pilot means only that the Thalassia TNC measurement is technically standardized enough to begin the prospective ecological test.

It says nothing about whether TNC predicts future meadow persistence.
