# Tampa optional forcing-module priority v1

## Purpose

Freeze a scientific priority rule for the integrated field campaign **before** equipment availability or future biological outcomes can steer which forcing module is retained.

This document does **not** populate the resource-freeze intent fields. Actual module intent remains confirmatory or disabled only after the response-independent equipment / calibration / field-capacity audit.

The protected study is always the authoritative four-bay TNC-v2 primary.

## Priority under constrained resources

If both forcing modules can satisfy their full frozen simultaneous-sampling gates without weakening TNC-v2, run both.

If capacity supports only one confirmatory forcing module, the scientific priority is:

1. **direct within-canopy optical DLI -> TNC**
2. **joint hot-fresh event exposure -> TNC**

Paired above-canopy optical attribution is secondary to the within-canopy optical primary and cannot displace primary-node capacity.

Hydrodynamics remains a separate later mechanism programme and is not a prerequisite for the integrated TNC campaign.

## Why optical precedes hot-fresh when only one can be run

### Direct relation to the reserve mechanism

The TNC programme asks whether below-ground carbon reserve buffers future quantitative persistence.

Within-canopy DLI measures the the local within-canopy photon environment over the same reserve interval over the same 39-45 day reserve interval.

The primary optical model is continuous and direct:

    tnc_post ~ tnc_pre + mean_daily_within_canopy_dli + water_body

It does not require choosing a low-light threshold after inspection.

### Tampa-specific historical support for direct optical measurement

The priority is also consistent with earlier Tampa Bay light studies, while **not** treating those studies as validation of the present prospective mechanism.

A year-long Lower Tampa Bay study continuously measured PAR at canopy height and at an upper reference at four deep-edge *Thalassia*-dominated meadows using 15-minute averaged scalar-irradiance records. Reported annual canopy-height irradiance spanned roughly 3600–4900 E yr-1 before epiphyte losses were represented. Epiphytic material reduced plant-available light by a further approximately 32–36%, and the station with the lowest annual light showed leaf elongation and reduced shoot density.

Source:

- Dixon, L.K. & Leverone, J.R., **Annual light regime of light-limited *Thalassia testudinum* in Tampa Bay, Florida**, Tampa BASIS 3 proceedings / SWIM-supported Tampa Bay light-requirement study.
- Historical report available through the Tampa Bay / Manatee Water Atlas BASIS proceedings archive.

This historical evidence matters for **measurement choice**:

- direct canopy-level PAR has already separated meaningful light environments in Tampa Bay;
- epiphyte attenuation can be large enough that water-column clarity alone is an incomplete estimate of plant-experienced light;
- continuous optical exposure is therefore biologically closer to the proposed reserve mechanism than another segment-level Secchi proxy.

It does **not** establish that present-day Tampa reserve decline is light-driven, and it does not replace the frozen prospective within-canopy DLI -> TNC test. The historical stations were deep-edge meadows and the study belongs to a different time period and sampling frame.

### The event-stress primary has a predeclared estimability risk

The joint event metric deliberately retains the published Tampa definition:

    temperature >= 30 C AND salinity <= 25 ppt

The response-independent climatology selected July 24-September 3 but found historical non-zero station-year fractions of approximately:

- Old Tampa Bay: 0.632;
- Middle Tampa Bay: 0.363;
- Lower Tampa Bay: 0.

The event primary is therefore intentionally vulnerable to its frozen non-zero / within-bay variation gate.

That is a scientific strength of the falsifiable design, but a reason not to sacrifice a more direct optical measurement if hardware permits only one forcing module.

### Interpretation of 30 C is compound-condition, not heat injury

The event contract explicitly does not treat 30 C as a Thalassia damage threshold. The joint index is a published Tampa compound-condition definition and can also proxy a broader rainfall/runoff event complex.

Thus a supported event result is informative, but proximate attribution is less direct than a supported actual-light -> reserve relationship.

## Resource decision rule

Before the first outcome-bearing core or logger:

### A. Protect TNC-v2

If the four-bay TNC node frame, preservation, HPLC, baseline calendar or method pilot cannot satisfy the frozen v2 gates:

> **STOP the outcome-bearing campaign.**

Do not retain an optional forcing module at the expense of the four-bay TNC primary.

### B. Test optical capacity

Set optical_module_intent = confirmatory only if all frozen optical-primary requirements can be met simultaneously, including:

- >=30 analyzable core-three nodes;
- >=8 per core bay;
- simultaneous within-canopy PAR systems across the common window;
- frozen vertical-profile / sensor-geometry pilot;
- DLI daylight-coverage QC;
- frozen optical primary analysis code.

If not, set it to disabled before biological sampling.

### C. Test event capacity

If TNC-v2 remains protected, set event_module_intent = confirmatory only if all frozen event requirements can be met simultaneously, including:

- >=30 analyzable core-three nodes;
- >=8 per core bay;
- complete temperature + salinity systems;
- frozen sensor geometry / calibration;
- common-window coverage;
- frozen event primary analysis code.

If not, set it to disabled before biological sampling.

### D. Optical attribution

Set the paired above-canopy attribution subset to confirmatory only after the optical primary has full capacity.

Insufficient above-canopy reference capacity does not invalidate a confirmatory within-canopy DLI primary.

## Important boundary

Scientific priority does not override feasibility.

If optical cannot pass its full gate but event can, event may be the only confirmatory forcing module.

If event cannot pass its full gate but optical can, optical may proceed alone.

If neither can pass, run **TNC-v2 only**.

Do not run a smaller outcome-bearing logger study merely because some sensors are available. Response-independent sensor pilots may still proceed.

## Claim boundary

This priority order is a prospective resource-allocation rule, not evidence that light is already the cause of Tampa decline.

A future supported optical result would identify an standardized within-canopy photon-environment/reserve association over the frozen interval; a future supported event result would identify a hot-fresh event-complex/reserve association. Neither is assumed in advance.
