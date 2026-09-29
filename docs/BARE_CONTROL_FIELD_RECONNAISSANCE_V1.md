# Tampa bare-control field reconnaissance protocol v1

## Purpose

The strict 2024 GIS preflight did **not** pass the frozen bare-control feasibility rule.

The result was:

- 13 mapped-edge candidates overall;
- Old Tampa Bay: 5;
- Middle Tampa Bay: 7;
- Lower Tampa Bay: 1;
- required: at least 12 overall and at least 3 in each bay.

The failure was driven by Lower Tampa Bay and by a strong mismatch between point-monitoring state and public mapped polygons: only 13 of 40 recently vegetated monitoring nodes fell inside the polygon union.

Therefore the GIS result is **not** used to relax any criterion and is **not** interpreted as evidence that bare habitat is absent.

The next allowed step is a response-independent field/imagery reconnaissance using the same frozen spatial and physical criteria.

## Scientific role

This reconnaissance qualifies nodes for the nested **canopy counterfactual physical-attribution gate**.

It does not select nodes using a future *Thalassia* response and does not alter the primary direct-hydrodynamic persistence cohort.

A node can remain in the main prospective hydrodynamic study even if it fails the bare-control reconnaissance. It simply cannot contribute to canopy-specific attribution.

## Candidate search frame

Start from the contemporaneous baseline-vegetated stable nodes in:

- Old Tampa Bay;
- Middle Tampa Bay;
- Lower Tampa Bay.

For each node, search for a candidate bare or effectively canopy-free seabed patch within a **100 m radius** of the fixed monitoring location.

The 100 m threshold is unchanged from the failed GIS preflight.

Do not extend the search radius after seeing reconnaissance yield.

## Stage 1 — imagery reconnaissance

Before field deployment, inspect the most recent available orthophoto / aerial imagery and authoritative seagrass mapping without using any future biological response.

Record for every candidate node:

- imagery date and source;
- candidate bare-patch coordinates;
- straight-line distance from fixed node;
- apparent patch width / area;
- surrounding vegetation configuration;
- distance and bearing to nearest visible vegetation edge;
- access / navigation constraints;
- confidence category: high / uncertain / no candidate.

Imagery is a planning layer only. It cannot certify the control.

## Stage 2 — field qualification

At the contemporaneous baseline visit, a bare control is accepted only if all conditions below are satisfied.

### A. Distance

- control sampling volume <= 100 m from the fixed monitoring node.

### B. Vegetation state

At the velocity-control footprint:

- no rooted seagrass canopy intersects the near-bed sampling volume;
- no rooted seagrass is present inside the frozen local control quadrat;
- record macroalgal or other structural vegetation separately rather than silently calling it bare.

A small unvegetated gap inside a larger meadow is allowed only if it satisfies the wake/context requirements below.

### C. Depth match

Compare contemporaneous water depth at the vegetated and bare sampling volumes.

- target absolute difference <= 0.15 m;
- hard maximum absolute difference <= 0.30 m.

A candidate beyond 0.30 m is rejected rather than adjusted statistically back into eligibility.

### D. Physical-context screen

Reject a control with an obvious discontinuity in forcing relative to the meadow node, including:

- channel or dredged-edge transition;
- inlet jet;
- shoreline / seawall shelter;
- bridge / piling / structure wake;
- boat channel;
- conspicuous bedform or scoured depression indicating a different flow regime.

Record substrate class and local bedform state at both vegetated and bare footprints.

### E. Vegetation-wake metadata

A bare patch can still be hydrodynamically influenced by adjacent vegetation.

Record:

- nearest canopy-edge distance;
- edge bearing;
- local canopy height;
- local patch geometry;
- velocity direction through time relative to the edge.

The confirmatory counterfactual comparison requires simultaneous vegetated and bare measurements.

If the bare sensor is repeatedly embedded in an obvious vegetation wake under the retained flow directions, the node remains descriptive but is not counted toward the confirmatory canopy-attribution minimum.

This rule is conservative: wake contamination can make a bare patch partly inherit the engineered flow field of nearby vegetation.

## Counterfactual sampling target

Planning target:

- 18 qualified nodes.

Minimum confirmatory physical-attribution set:

- 12 qualified nodes total;
- >=3 qualified nodes in each of Old, Middle and Lower Tampa Bay.

The failed GIS counts do not reduce these minima.

If the field-qualified set is below 12 or any bay contributes fewer than 3:

> do not claim canopy-specific ecosystem engineering from the vertical velocity contrast.

The primary prospective attenuation-to-future-*Thalassia* model may still proceed, but its interpretation is hydrodynamic-state association rather than demonstrated canopy self-facilitation.

## Simultaneous measurement requirement

For a confirmatory counterfactual node, retain simultaneous or exactly synchronized measurements of:

1. vegetated near-bed / within-canopy velocity;
2. vegetated upper reference velocity;
3. bare near-bed velocity at the matched height above sediment;
4. bare upper reference velocity at the matched upper-water-column height.

Two suitable multi-bin profilers may satisfy the four sampling volumes; four separate instruments are not intrinsically required.

If vegetated and bare deployments are staggered in time, the node is descriptive only for canopy attribution.

## Frozen canopy-attribution metric

For each qualified node:

```text
A_veg  = 1 - p90(U_veg_nearbed)  / p90(U_veg_reference)
A_bare = 1 - p90(U_bare_nearbed) / p90(U_bare_reference)

excess_canopy_attenuation_p90 = A_veg - A_bare
```

Use the same frozen velocity statistic, burst aggregation and QC on all four sampling volumes.

The physical attribution gate remains:

> the frozen node-level paired-bootstrap 95% interval for mean excess_canopy_attenuation_p90 lies above 0.

Do not substitute another percentile or control geometry after inspection.

## Interpretation boundary

Passing this field reconnaissance only establishes that a matched counterfactual measurement is feasible.

Passing the later physical attenuation gate would support canopy-associated flow engineering.

A hydrodynamic **self-facilitation** interpretation additionally requires the separate prospective ecological gate showing that stronger attenuation predicts more favorable future quantitative *Thalassia* change.

No binary re-recording endpoint is used as recovery.
