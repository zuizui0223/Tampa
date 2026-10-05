# Tampa optical pilot raw-data entry and validation v1

## Purpose

This layer operationalizes the response-independent optical method pilot in:

- `docs/OPTICAL_PAR_METHOD_PILOT_V1.md`
- `results/optical_pilot_acceptance_v1_contract.json`

It does **not** change the ecological hypothesis and does not read TNC or any future meadow response.

The canonical handoff is:

```text
standardized pilot records
  -> field/optical_pilot_candidate.json
  -> results/optical_method_pilot_validation.json
  -> proposed READY optical freeze
  -> field/optical_pilot_freeze.json only after review
```

The raw/standardized source files are the source of truth. Do not type aggregate PASS metrics directly into the authoritative freeze.

## Hard prohibition

The builder rejects obvious future-response tokens. These pilot inputs must not contain:

- future focal-frequency change;
- future Braun-Blanquet response;
- future shoot density / blade length;
- pre/post TNC values;
- any ecological outcome used to choose a sensor, height, cleaning interval or node.

PAR-only method data are allowed.

## 1. Pilot metadata

File:

- `field/optical_raw_pilot_metadata.json`

Freeze before building the candidate:

- optical sensor model;
- `primary_angular_response_class` = `2pi_cosine_ppfd` or `4pi_scalar_ppffr`;
- calibrated underwater quantum reference identity/provenance;
- `reference_angular_response_class`, which must exactly match the primary class;
- exact IDs of every sensor/channel intended for outcome-bearing use;
- response-independent expected maximum field photon rate for the chosen quantity;
- mounting geometry description;
- optical attribution intent: `confirmatory` or `disabled`;
- above-canopy clearance rule if attribution is confirmatory;
- raw logger / calibration artifact hashes or manifest entries when available.

The declared outcome-bearing sensor list is important: calibration and side-by-side gates are evaluated against **every declared channel**, not merely channels that happen to appear in a passing subset.

## 2. In-water calibration records

File:

- `field/optical_calibration_pilot.csv`

Columns:

- `sensor_id`
- `irradiance_level_id`
- `reference_photon_rate_umol_m2_s`
- `sensor_raw_photon_rate_umol_m2_s`
- `dark`
- `saturated`

For each sensor, the builder fits:

```text
reference_primary_photon_rate = intercept + slope * raw_sensor_photon_rate
```

using the response-independent pilot observations.

The numeric calibration columns are intentionally angular-neutral. Their scientific meaning is supplied by the frozen metadata class. Do not write scalar PPFFR measurements into a field labelled PPFD, and do not mix scalar and cosine channels in the same primary.

The calibration gate requires:

- >=50 complete paired observations per outcome-bearing sensor/channel;
- >=5 non-dark irradiance levels;
- >=5 qualifying dark observations;
- calibration range reaching the predeclared expected field photon-rate maximum for the frozen angular-response quantity;
- R² >=0.995;
- median absolute relative error <=5%;
- p95 absolute relative error <=10%;
- absolute calibrated dark offset <=1 µmol m-2 s-1;
- no saturation.

### Relative-error definition

The frozen relative error is:

```text
abs(calibrated_primary_photon_rate - reference_primary_photon_rate)
------------------------------------
max(abs(reference_primary_photon_rate), 10)
```

The fixed 10 µmol m-2 s-1 denominator floor prevents percentage error from becoming undefined near zero. Dark performance is evaluated separately with the dark-offset gate.

A row counts as a qualifying dark observation when the pilot marks it `dark=true` and reference photon rate is <=1 µmol m-2 s-1.

## 3. Side-by-side integrated-light check

File:

- `field/optical_side_by_side_dli_pilot.csv`

Columns:

- `check_id`
- `sensor_id`
- `dli_mol_m2`
- `underwater_hours`

Each eligible check must:

- contain **all** declared outcome-bearing sensors;
- represent >=6 underwater hours.

For each check, between-sensor CV is:

```text
sample SD(sensor integrated light)
----------------------------------
mean(sensor integrated light)
```

The maximum CV among eligible checks must be <=5%.

The DLI values entered here are method-pilot integrated-light outputs. Preserve the corresponding source logger exports in the metadata artifact manifest.

## 4. Vertical-profile representativeness

File:

- `field/optical_vertical_profile_pilot.csv`

Columns:

- `node_id`
- `water_body`
- `date`
- `canopy_height_m`
- `canopy_height_class` = `low`, `middle`, or `high`
- `dli_25`
- `dli_50`
- `dli_75`
- `dli_above`
- `daylight_coverage_fraction`
- `max_daylight_gap_minutes`

Only node-days satisfying the already frozen DLI QC are retained:

- daylight coverage >=90%;
- maximum daylight gap <=30 min.

The pilot must include:

- >=12 nodes;
- >=3 nodes per Old / Middle / Lower Tampa Bay;
- >=2 valid node-days per node;
- >=3 nodes in each pre-frozen canopy-height class.

The canopy-height class must be assigned from baseline structure **before pilot PAR is inspected**.

For every valid node-day:

```text
profile_reference_DLI = mean(DLI_25, DLI_50, DLI_75)
```

This is an equal-weight **geometric three-level optical reference** for method selection. It is not a leaf-area-weighted absorbed-photon estimate and should not be interpreted as whole-canopy photosynthesis.

The builder chooses the proportional height with smallest median absolute relative error to this profile reference. Tie rule:

1. 50%;
2. 25%;
3. 75%.

The selected one-height design passes only if it meets the frozen median-error, node-day agreement and bay-bias gates.

## 5. Placement repeatability

File:

- `field/optical_placement_pilot.csv`

Columns:

- `node_id`
- `water_body`
- `replicate_id`
- `canopy_height_m`
- `achieved_height_m`

Use the same pilot nodes as the vertical-profile experiment.

The builder evaluates the height selected by the profile pilot.

A mock placement passes when:

```text
abs(achieved_height - selected_fraction * canopy_height)
    <= max(0.02 m, 0.10 * canopy_height)
```

Requirements:

- all vertical-profile pilot nodes are represented;
- >=3 mock placements per node;
- >=90% of placements pass.

## 6. Fouling / maintenance records

File:

- `field/optical_fouling_pilot.csv`

Columns:

- `location_id`
- `water_body`
- `maintenance_mode` = `manual` or `active_antifouling`
- `service_interval_days`
- `pilot_day`
- `check_id`
- `pre_clean_photon_rate_umol_m2_s`
- `post_clean_photon_rate_umol_m2_s`

For manual maintenance, candidate intervals remain frozen in order:

1. 14 days;
2. 7 days;
3. 3 days.

For a candidate configuration to count:

- >=6 locations;
- >=2 locations per core bay;
- each counted location documented through >=14 submerged pilot days.

Relative cleaning change is:

```text
abs(pre_clean_primary_photon_rate - post_clean_primary_photon_rate)
-------------------------------------
max(abs(post_clean_primary_photon_rate), 10)
```

Pass:

- median absolute change <=5%;
- p90 <=10%.

The builder selects the **longest passing manual interval**.

If none passes, an `active_antifouling` configuration may pass the same 14-day, 6-location, 2-per-bay and response-change gates. Its manual interval is frozen as the explicit token:

- `NOT_APPLICABLE_ACTIVE_ANTIFOULING`

## 7. Above-canopy attribution

The paired above-canopy module is secondary.

If `optical_attribution_intent=confirmatory`, metadata must contain a frozen above-canopy clearance tolerance rule.

If `optical_attribution_intent=disabled`, the handoff writes:

- `NOT_APPLICABLE_ATTRIBUTION_DISABLED`

This prevents a disabled secondary attribution module from blocking an otherwise valid within-canopy optical primary.

## Run the pipeline

Build the candidate:

```bash
python validation/build_optical_pilot_summary.py
```

Validate against the frozen acceptance contract:

```bash
python validation/validate_optical_method_pilot.py
```

Possible statuses:

- `STOP_PILOT_INCOMPLETE`
- `STOP_PILOT_QC_FAILED`
- `PASS_OPTICAL_PILOT`

A PASS result contains the exact values eligible for copying into the optical freeze.

Create a proposed READY freeze:

```bash
python analysis/72_apply_optical_method_pilot.py \
  --validation results/optical_method_pilot_validation.json \
  --out field/optical_pilot_freeze_ready_candidate.json
```

Then audit it:

```bash
python validation/validate_optical_pilot_readiness.py \
  --freeze field/optical_pilot_freeze_ready_candidate.json \
  --strict
```

The scripts do not automatically overwrite `field/optical_pilot_freeze.json`.

## Provenance

The builder records SHA-256 and byte size for every standardized pilot input. The validator carries this provenance into the PASS result, and the handoff carries it into the proposed READY freeze.

The integrated field-campaign validator requires:

- optical freeze status `READY`;
- `PASS_OPTICAL_PILOT` provenance;
- candidate digest;
- raw-pilot provenance.

Therefore a hand-edited `READY` token is insufficient.

## Interpretation boundary

Passing the pipeline establishes only that the optical measurement system is sufficiently calibrated, vertically representative, repeatable and maintainable for the frozen prospective test.

It is **not evidence** that:

- low light reduces TNC;
- one canopy height is biologically optimal;
- epiphytes cause low light;
- any ecological DLI threshold exists.
