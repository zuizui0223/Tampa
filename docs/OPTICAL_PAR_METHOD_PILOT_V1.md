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

Continuous seagrass light studies have used cosine-corrected underwater quantum sensors/loggers, reference calibration and high-frequency observations integrated through the day. Historical Tampa work has also used scalar quantum sensors. Those two geometries are not interchangeable: a cosine collector measures hemispherical photon flux onto a plane, whereas a scalar collector integrates photons arriving from all directions.

The pilot therefore freezes **one angular-response class before method acceptance**:

- `2pi_cosine_ppfd`; or
- `4pi_scalar_ppffr`.

Every outcome-bearing within-canopy channel, every paired above-canopy channel retained for transmittance, and the calibration reference must use the same class. This v1 pilot does not authorize a scalar↔cosine transfer function.

Collier et al. (2016, *Frontiers in Marine Science* 3:106, DOI 10.3389/fmars.2016.00106) provides an example of cosine-corrected underwater irradiance used for seagrass daily light exposure. LI-COR specifications likewise distinguish the LI-192 cosine quantum sensor from the LI-193 spherical/scalar quantum sensor.

Leaf-scale measurements also show that light can decline strongly from the top toward the base of a seagrass canopy, so one fixed logger height must be validated rather than assumed to represent the whole canopy.

The numerical tolerances below are **method-QC tolerances**, not ecological light thresholds.

## A. In-water sensor calibration

Before calibration, freeze `primary_angular_response_class` and `reference_angular_response_class`. They must be identical.

Every optical sensor/channel intended for outcome-bearing deployment must then be cross-calibrated **underwater** against one frozen reference sensor of that same angular-response class.

A cosine outcome sensor calibrated against a scalar reference, or a scalar outcome sensor calibrated against a cosine reference, fails this v1 method gate even if a linear fit looks excellent. The directional light field inside a canopy can differ from the calibration field.

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
- frozen primary angular-response class;
- matched reference angular-response class;
- scientific reporting label for the chosen light quantity;
- sensor-specific calibration coefficients;
- reference sensor provenance;
- selected proportional height;
- vertical placement tolerance;
- mounting geometry;
- maintenance interval / antifouling rule;
- DLI valid-day coverage and gap rule;
- above-canopy clearance tolerance if applicable.

Only then may `optical_vertical_profile_pilot_complete` be set to true in the integrated campaign resource freeze.

## Claim boundary

Passing this pilot means the optical exposure can be measured reproducibly enough for the prospective mechanism test.

It does **not** mean:

- low light causes TNC depletion;
- 50% canopy height is biologically optimal;
- any DLI threshold has been identified;
- epiphytes caused the measured attenuation;
- the optical mechanism is supported.


## Machine-checkable raw-pilot pipeline

Pilot measurements are entered through the standardized response-independent inputs documented in:

- `docs/OPTICAL_PILOT_DATA_ENTRY_V1.md`.

The canonical pipeline is:

```bash
python validation/build_optical_pilot_summary.py
python validation/validate_optical_method_pilot.py
```

A `PASS_OPTICAL_PILOT` result may then be copied mechanically into a proposed optical freeze with:

```bash
python analysis/72_apply_optical_method_pilot.py \
  --validation results/optical_method_pilot_validation.json \
  --out field/optical_pilot_freeze_ready_candidate.json
```

and audited with:

```bash
python validation/validate_optical_pilot_readiness.py \
  --freeze field/optical_pilot_freeze_ready_candidate.json \
  --strict
```

The builder records input SHA-256 provenance. The authoritative READY freeze must retain `PASS_OPTICAL_PILOT` provenance; manually typing aggregate pilot metrics or a READY token is not an accepted handoff.

### Frozen numerical semantics added before the pilot

- Calibration relative-error denominator: `max(abs(reference PPFD), 10)`.
- Dark rows: reference PPFD <=1 µmol m-2 s-1, >=5 dark observations per outcome-bearing sensor.
- Calibration range must reach the response-independently declared expected maximum field PPFD.
- Side-by-side DLI checks must contain every declared outcome-bearing sensor/channel.
- Vertical-profile rows count only when daylight coverage is >=90% and maximum daylight gap is <=30 min.
- The vertical pilot spans pre-frozen low/middle/high canopy-height classes with >=3 nodes per class.
- Placement repeatability uses the same pilot nodes as the vertical-profile test.
- Fouling response-change denominator: `max(abs(post-clean PPFD), 10)`; counted locations must be followed through >=14 submerged days.
- If all manual service intervals fail, active antifouling must independently pass the same response-change gate.
- Disabled secondary above-canopy attribution is explicitly recorded as `NOT_APPLICABLE_ATTRIBUTION_DISABLED` and does not block the primary within-canopy method.
