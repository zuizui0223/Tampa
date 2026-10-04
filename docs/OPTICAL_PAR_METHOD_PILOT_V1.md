# Tampa optical PAR method / vertical-profile pilot v1

## Purpose

Resolve the remaining **measurement-dependent** optical fields before the first outcome-bearing optical logger deployment.

This pilot is not an ecological test. It may inspect PAR measurements needed to validate sensors and geometry, but it must not use TNC, future meadow response, retrospective decline class, or any PAR–biology association to choose a protocol.

Authoritative acceptance contract:

- `results/optical_pilot_acceptance_v1_contract.json`

Primary optical mechanism contract:

- `results/optical_microenvironment_prospective_v1_contract.json`

The pilot resolves:

- PAR sensor model / calibration workflow;
- one defensible proportional within-canopy sampling height;
- practical placement tolerance and mounting geometry;
- fouling / maintenance interval;
- daylight DLI missing-data rule;
- above-canopy clearance tolerance if the attribution subset is retained.

## Literature basis

Continuous seagrass light studies have used cosine-corrected underwater PAR sensors/loggers, reference calibration and 15-minute observations integrated to daily light integral (DLI). Collier et al. (2016, *Frontiers in Marine Science* 3:106, DOI 10.3389/fmars.2016.00106) calibrated submerged irradiance loggers against a cosine-corrected underwater quantum reference and calculated DLI from 15-minute data.

Leaf-scale measurements also show that light can decline strongly from the top toward the base of a seagrass canopy, so one fixed logger height must be validated rather than assumed to represent the whole canopy.

The numerical tolerances below are **method-QC tolerances**, not ecological light thresholds.

## A. In-water sensor calibration

Every PAR sensor/channel intended for outcome-bearing deployment must be cross-calibrated **underwater** against one frozen cosine-corrected underwater quantum reference.

Use at least:

- 5 irradiance levels spanning darkness/near-zero through the expected field range;
- 50 paired observations per candidate sensor/channel;
- no saturated observations in the accepted field range.

One sensor-specific linear correction may be estimated from pilot data and then frozen.

After correction, a channel passes only if:

- R² >= 0.995 against the reference;
- median absolute relative error <=5%;
- 95th percentile absolute relative error <=10%;
- absolute dark offset <=1 µmol photons m⁻² s⁻¹;
- no saturation occurs over the expected field PPFD range.

Then run a >=6-hour underwater side-by-side check. Between-sensor CV for integrated light over that check must be <=5%.

Failing sensors are repaired/recalibrated or excluded. Do not compensate for a failing channel later using biological outcomes.

## B. Vertical-profile representativeness pilot

Minimum pilot frame:

- 12 response-independent nodes;
- >=3 nodes from each Old, Middle and Lower Tampa Bay;
- span low, middle and high baseline canopy-height classes.

At each pilot node, measure simultaneously:

1. 25% of measured canopy height;
2. 50%;
3. 75%;
4. one above-canopy reference.

Obtain at least **2 valid daylight days** per node.

For each node-day:

```text
profile_reference_DLI
  = mean(DLI_25%, DLI_50%, DLI_75%)
```

For each candidate single height (25%, 50%, 75%), calculate relative error to that profile reference.

Choose the height with the smallest median absolute relative error across all valid pilot node-days.

Tie rule:

> 50% -> 25% -> 75%.

The selected one-height design passes only if:

- median absolute relative error <=15%;
- >=80% of pilot node-days are within +/-25%;
- absolute median relative bias within each bay <=20%.

If no level passes, the **single-height optical primary is not field-ready**.

Do not choose the height that later produces the strongest TNC association. A multi-height biological design would require a separately frozen future contract.

## C. Placement repeatability

The chosen proportional height must also be reproducible in field handling.

At the same >=12 pilot nodes, perform >=3 mock placements.

A placement is within tolerance if:

```text
absolute vertical error
  <= max(2 cm, 10% of measured canopy height)
```

At least 90% of mock placements must pass.

If not, revise mounting hardware response-independently and repeat the pilot.

## D. Fouling / maintenance pilot

PAR is especially vulnerable to optical fouling, so the 42-day campaign cannot rely on an unspecified cleaning plan.

Use:

- >=14 submerged pilot days;
- >=6 pilot locations;
- >=2 locations per core bay.

Evaluate service intervals in this predeclared order:

1. 14 days;
2. 7 days;
3. 3 days.

At each service check, compare sensor response immediately before versus immediately after cleaning under colocated conditions.

An interval passes when:

- median absolute relative response change <=5%;
- 90th percentile absolute relative response change <=10%.

Choose the **longest passing interval**.

If none passes, an active antifouling/wiper solution must pass the same response gate or the optical primary is disabled for the outcome-bearing campaign.

## E. Daily DLI missing-data rule

Primary DLI integration uses the full daylight period, not merely total row coverage.

Daylight is defined astronomically from local sunrise to sunset at each node/date.

A node-day is valid only if:

- >=90% of scheduled daylight observations are present;
- no continuous daylight gap exceeds 30 min.

Only gaps <=30 min may be linearly interpolated.

A longer daylight gap invalidates the entire node-day.

The primary node exposure still requires:

- >=30 valid daily DLIs;
- >=85% overall PAR coverage;
- >=35 days of common calendar overlap.

Do not reconstruct long gaps from another node or from an above-canopy reference.

## F. Above-canopy reference geometry

If optical attribution is marked confirmatory, the reference sensors use the same calibration/QC system.

The pilot must also freeze:

- target clearance above the standing canopy;
- allowable clearance tolerance;
- mount-shadow avoidance rule;
- submergence rule.

The reference subset remains secondary physical attribution. Failure of reference capacity does not invalidate an otherwise valid within-canopy optical primary.

## Outputs copied into the field freeze

After the response-independent pilot passes, freeze:

- sensor model(s);
- sensor-specific calibration coefficients;
- reference sensor provenance;
- selected proportional height;
- vertical placement tolerance;
- mounting geometry;
- maintenance interval / antifouling rule;
- DLI valid-day coverage and gap rule;
- above-canopy clearance tolerance if applicable.

Only then may `optical_vertical_profile_pilot_complete` be set to true in the integrated campaign resource freeze.

## Authoritative raw-record pipeline

The pilot result is **not** entered into the READY freeze by hand.

Raw response-independent records are stored in:

- `field/optical_raw_pilot_metadata.json`;
- `field/optical_calibration_pilot.csv`;
- `field/optical_side_by_side_dli_pilot.csv`;
- `field/optical_vertical_profile_pilot.csv`;
- `field/optical_placement_pilot.csv`;
- `field/optical_fouling_pilot.csv`.

The authoritative pipeline is:

```text
raw pilot records
  -> validation/build_optical_pilot_summary.py
  -> field/optical_pilot_candidate.json
  -> validation/validate_optical_method_pilot.py
  -> results/optical_method_pilot_validation.json
  -> analysis/72_apply_optical_method_pilot.py
  -> field/optical_pilot_freeze.json
```

The builder computes calibration error, vertical representativeness, placement repeatability and fouling metrics from the raw records.

The validator independently rechecks the frozen selection rules:

- all candidate outcome-bearing PAR channels satisfy calibration limits;
- the selected 25/50/75% height is the minimum-error level under the frozen tie rule;
- the selected maintenance interval is the **longest passing** frozen candidate;
- all vertical-profile / placement / fouling gates pass.

Only `PASS_OPTICAL_PILOT` produces a copy payload.

The apply script refuses any non-PASS validation and refuses to overwrite a conflicting previously frozen value. It adds raw-record hashes and candidate/validation provenance before setting the optical pilot freeze to `READY`.

The integrated campaign validator independently requires this provenance-backed `READY` state whenever the optical module is labeled confirmatory. A manually set `optical_vertical_profile_pilot_complete=true` is not sufficient.

## Claim boundary

Passing this pilot means the optical exposure can be measured reproducibly enough for the prospective mechanism test.

It does **not** mean:

- low light causes TNC depletion;
- 50% canopy height is biologically optimal;
- any DLI threshold has been identified;
- epiphytes caused the measured attenuation;
- the optical mechanism is supported.
