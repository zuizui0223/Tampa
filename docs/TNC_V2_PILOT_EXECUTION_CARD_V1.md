# Tampa TNC-v2 method pilot — execution card

This is the shortest operational path from the current
`STOP_RESOURCE_FREEZE_INCOMPLETE` state to a completed
response-independent TNC method freeze.

This card does **not** replace `docs/TNC_V2_METHOD_FIELD_PILOT_V1.md`.
It only lists the minimum actions and pass gates in execution order.

## 1. Pilot material

Use only non-outcome-bearing donor material.

Minimum raw pilot inventory:

- **>=8 independent rhizome specimens**;
- **>=2 collection locations or collection batches**;
- **>=10 field core attempts**.

Record these in:

- `field/tnc_v2_raw_pilot_metadata.json`.

Future meadow response must remain inaccessible.

## 2. Tissue-class pilot

Candidate order is frozen:

1. live horizontal rhizome, proximal **3 cm** from a living short shoot;
2. same definition using **4 cm**.

For each candidate/specimen fill:

- classification_unambiguous;
- dry_mass_sufficient;
- destructive_guardrail_pass.

File:

- `field/tnc_v2_tissue_class_pilot.csv`.

PASS for a candidate:

- >=8 complete specimens;
- >=90% unambiguous classification;
- >=90% sufficient dry mass;
- all destructive guardrails pass.

Choose the first passing candidate under the frozen order.

Do **not** use TNC concentration to choose the tissue class.

## 3. Core-geometry pilot

Frozen least-destructive-first order:

1. 9 cm diameter x 15 cm depth
2. 9 x 20 cm
3. 15 x 15 cm
4. 15 x 20 cm
5. 15 x 25 cm

For each attempted core fill:

- live_horizontal_rhizome_recovered;
- dry_mass_sufficient;
- guardrail_pass;
- three_anchor_feasible.

File:

- `field/tnc_v2_core_geometry_pilot.csv`.

PASS for a geometry:

- >=10 complete attempts;
- >=9/10 recover target live horizontal rhizome;
- >=9/10 provide sufficient dry mass;
- all guardrails pass;
- q25/q50/q75 three-anchor design remains feasible.

Select the **first passing geometry**.

## 4. Permanent-transect offset

Obtain the monitoring authority's physical no-disturbance/access boundary.

For each tested offset, include at least one complete representative placement for **each frozen anchor class**:

- q25;
- q50;
- q75.

For every placement record fill:

- anchor_class;
- permit_boundary_pass;
- permanent_transect_protected;
- placement_reproducible;
- restoration_workspace_pass.

File:

- `field/tnc_v2_offset_pilot.csv`.

Select the smallest positive offset only when q25, q50 and q75 are all represented and **every declared placement passes**. One successful placement is not sufficient.

## 5. HPLC matrix QC

Populate:

- `field/tnc_v2_hplc_matrix_pilot.json`.

Required PASS gates:

- calibration/analyte identity unambiguous;
- standard-mixture mean recovery **95–105%**;
- matrix-spike mean and every matrix spike **85–115%**;
- technical-duplicate median CV **<=10%**;
- <=10% of duplicate pairs have CV >15%;
- >=90% of pilot extracts inside calibration range;
- analytical blank below LOQ;
- post-high-standard carryover below LOQ.

These are method QC criteria, not ecological thresholds.

## 6. Preservation-delay pilot

Frozen candidate methods:

1. immediate liquid-nitrogen flash freeze;
2. rapid direct dry-ice freeze.

For every tested positive delay record paired immediate/delayed TNC from the
same specimen in:

- `field/tnc_v2_preservation_pilot.csv`.

For any method that could be selected:

- test **>=3 distinct positive delay levels**;
- each candidate selected delay needs **>=6 paired independent specimens**.

A delay passes when:

- median absolute relative TNC difference <=10%;
- 90th percentile absolute relative difference <=15%;
- no monotonic signed TNC drift across delays;
- samples remain physically suitable.

The builder derives the directional-drift gate automatically.

## 7. Build, validate, apply

After raw pilot files are populated:

~~~bash
python validation/build_tnc_v2_method_pilot_summary.py
python validation/validate_tnc_v2_method_pilot.py   --pilot field/tnc_v2_method_pilot_candidate.json   --out results/tnc_v2_method_pilot_validation.json
~~~

Only if status is:

~~~text
PASS_METHOD_PILOT
~~~

apply the six selected method values mechanically:

~~~bash
python analysis/69_apply_tnc_v2_method_pilot.py   --validation results/tnc_v2_method_pilot_validation.json   --out field/tnc_v2_precollection_freeze_candidate.json
~~~

Do not hand-copy or reinterpret failed/pending values.

## 8. What still remains after method PASS

Method PASS resolves:

- rhizome tissue class;
- core diameter;
- core depth;
- minimum transect offset;
- preservation method;
- maximum preservation delay.

It does **not** resolve:

- campaign start/end dates;
- final four-bay node registry;
- final TNC-baseline calendar;
- baseline-transect calendar;
- HPLC total capacity;
- preservation total capacity;
- event module intent;
- optical module intent;
- optical-attribution intent.

Those are the remaining logistics/resource freezes in
`field/integrated_campaign_resource_freeze.json`.

## Hard boundary

No outcome-bearing TNC core may be collected while the integrated readiness status is:

~~~text
STOP_RESOURCE_FREEZE_INCOMPLETE
~~~

A pilot failure triggers a versioned method redesign. It never licenses
post-hoc threshold relaxation.
