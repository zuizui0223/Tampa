# Tampa mechanism interpretation ladder: persistent site-template alternative

## Purpose

The Tampa retrospective record is strongly structured by stable transect identity.

That creates a serious alternative explanation for every prospective cross-node mechanism result:

> some persistent, incompletely measured site property may make a node simultaneously high in TNC, strong in canopy attenuation, compositionally diverse, and more stable in the future.

A prospective association is stronger than retrospective relabelling, but **prospective does not automatically mean causal**.

This document freezes the interpretation ladder before the new biological responses exist.

## The common-cause alternative

Call the unresolved alternative the **persistent site-template hypothesis**.

It does not assert one specific hidden variable.

Candidate contributors could include stable or slowly varying combinations of:

- sediment and bathymetric microstructure not captured by the existing coarse template;
- local exposure geometry;
- long-term nutrient regime;
- chronic light microenvironment;
- meadow age / developmental history;
- unmeasured disturbance history;
- other persistent microsite properties.

The current data do not identify a single site-template variable.

Therefore the phrase is a **causal boundary**, not a new mechanism claim.

## Evidence level 1 — prospective state association

Examples:

~~~text
future_delta_frequency
  ~ baseline_frequency
  + baseline_Braun_Blanquet
  + rhizome_TNC
  + water_body
~~~

or

~~~text
future_delta_frequency
  ~ baseline_frequency
  + ambient_p90
  + attenuation_p90
  + water_body
~~~

If the focal coefficient is supported under its frozen gate:

> the measured buffer state contains prospective information about the future quantitative trajectory beyond current above-ground state and bay.

This is useful ecology.

It is **not sufficient** to say that the measured buffer causally created the future stability, because persistent site quality could generate both the buffer and the future outcome.

## Evidence level 2 — mechanism-specific process link

Each proposed buffer has a separate process-level gate that makes the common-site explanation less complete.

### Internal reserve

The event-stress programme measures TNC twice.

Frozen process link:

> node-scale event exposure -> change in TNC conditional on pre-exposure TNC.

A supported within-node reserve depletion result shows that TNC is dynamically responsive to an independently measured forcing, rather than only a static site label.

It still does not prove that TNC itself causes later meadow persistence.

### Canopy engineering

The matched bare-bed counterfactual asks:

> does vegetation produce excess flow attenuation beyond the ordinary seabed vertical velocity gradient?

A supported physical gate identifies a vegetation-associated engineering effect.

It still does not prove that the engineered state is the sole cause of future persistence.

### Community functional continuity

The community test asks whether composition explains measured physical function after total vegetation structure is represented.

This distinguishes occupancy continuity from measured functional continuity.

It remains observational with respect to why a particular community occupies a site.

## Evidence level 3 — mechanism-to-future link

The strongest currently frozen pathway requires both a process link and a future-state link.

### Reserve pathway

1. event-scale forcing predicts reserve depletion;
2. reserve state predicts future quantitative *Thalassia* change.

Both supported:

> consistent with a forcing -> reserve-state -> future-persistence pathway.

Do not call this formal mediation because the programme was not powered or randomized as a mediation experiment.

### Engineering pathway

1. vegetation produces excess attenuation relative to matched bare bed;
2. attenuation predicts future quantitative *Thalassia* change.

Both supported:

> consistent with canopy-mediated hydrodynamic self-facilitation.

Again, this remains an observational meadow-scale feedback test.

## What counts as evidence for multiple buffers

The phrase **multiple supported buffer mechanisms** is allowed only when more than one mechanism independently passes its own frozen process/future gates.

Examples:

- TNC future association alone + attenuation future association alone:
  **two prospective state predictors**, not yet two identified mechanisms.

- reserve process gate + reserve future gate:
  **supported measured reserve pathway**.

- engineering physical gate + engineering future gate:
  **supported measured engineering pathway**.

- both complete pathways:
  **consistent with multiple buffering mechanisms operating in the same foundation-species system**.

Even in the last case, do not claim statistically independent or additive causal effects unless a separately powered joint analysis was frozen before future response access.

## Why no confirmatory joint TNC + attenuation model is added now

The realistic common-node sample is approximately 30–33.

A joint model such as

~~~text
future_delta_frequency
  ~ baseline state
  + TNC
  + attenuation
  + water body
~~~

would have limited resolution for two correlated focal predictors.

More importantly, adding it only after both single-buffer results are known would create a new rescue/competition analysis.

Therefore:

- no confirmatory multibuffer additive model is currently authorized;
- no TNC x attenuation interaction is authorized;
- no post-hoc composite "buffer score" is authorized.

A future joint model requires a separately frozen design and precision analysis before the future response is opened.

## Response-independent cross-buffer diagnostics

If TNC and hydrodynamic attenuation are measured at the same nodes before the future biological response exists, the following descriptive diagnostics are allowed:

- node-level scatterplot of TNC versus attenuation;
- Spearman correlation with two-sided bootstrap interval;
- distributions by water body;
- correlation of each buffer with contemporaneous baseline quantitative state.

These diagnostics describe whether buffer states co-vary.

They do **not** decide which buffer is causal and cannot be used to choose, drop or reweight a primary mechanism test.

No correlation threshold is declared as a pass/fail rule.

## Interpretation matrix

| Result | Allowed interpretation |
|---|---|
| TNC predicts future state; event -> TNC unsupported/non-estimable | reserve state is a prospective predictor; source of reserve variation unresolved |
| event -> TNC supported; TNC -> future unsupported | tested events alter reserve, but reserve is not shown to forecast later meadow stability |
| both reserve links supported | consistent with a stress -> reserve depletion -> future-state pathway |
| bare-bed engineering gate supported; attenuation -> future unsupported | canopy modifies flow, but no supported stabilizing future link |
| attenuation -> future supported; engineering gate unsupported | hydrodynamic state predicts future change; canopy causation unresolved |
| both engineering links supported | consistent with hydrodynamic self-facilitation |
| complete reserve + complete engineering pathways supported | consistent with multiple measured buffering mechanisms; independent causal contributions still not demonstrated |
| all prospective buffer-to-future tests unsupported at adequate precision | buffered-persistence mechanism programme weakens; do not rescue it from retrospective state decoupling |

## Relationship to the frozen TNC inference hierarchy

Boca Ciega Bay was prospectively incorporated before outcome-bearing TNC sampling and remains part of the authoritative four-bay sampling frame together with Old, Middle and Lower Tampa Bay.

The **paper-level decisive primary** is now the within-meadow state-augmentation test frozen in `results/clonal_state_inference_hierarchy_v1.json`:

~~~text
future_BB_anchor
  ~ baseline_BB_anchor
  + within_node_centered_anchor_TNC
  + node_fixed_effect
~~~

This comparison removes stable transect-level differences and asks whether local reserve heterogeneity within the same meadow predicts future local divergence after current local above-ground state is represented.

The four-bay cross-node model remains a **supportive network-scale generality test**:

~~~text
future_delta_frequency
  ~ baseline_frequency
  + baseline_Braun_Blanquet
  + rhizome_TNC
  + water_body
~~~

A positive cross-node result cannot rescue an unsupported or non-estimable within-node decisive primary.

The within-node design weakens the persistent transect-template alternative, but it still does not eliminate persistent meter-mark microhabitat or time-varying local common causes. Stronger mechanism interpretation therefore still depends on the separately frozen temporal/process diagnostics: event -> TNC change and matched-anchor reserve trajectory -> future state.

Therefore:

- within-node support is the decisive evidence for measured state augmentation;
- four-bay cross-node support strengthens transportability/generalization;
- neither is randomized causal evidence;
- complete process chains are required for stronger claims about how buffering occurs.

## General ecological claim boundary

The retrospective Tampa result already supports:

> coarse occurrence and quantitative condition are distinct ecological states.

The prospective programme may support:

> persistence is associated with identifiable biological, engineered or community buffer states.

Only mechanism-specific process gates allow stronger wording about **how** buffering occurs.

The common-site alternative must remain visible whenever the evidence is a cross-node state association alone.


## History-linked community-function evidence

The community branch now has a stronger paper-level hierarchy frozen before hydrodynamic outcomes.

The decisive physical comparison is not the cross-sectional `thalassia_fraction` coefficient. It is the matched history-linked contrast in `results/functional_insurance_inference_hierarchy_v1.json`:

```text
same stable node

loss-legacy alternative-seagrass point
        versus
>=3-year persistent-Thalassia point
```

with both states measured simultaneously under the same frozen velocity protocol.

This comparison weakens broad site-template confounding because both functional states occur inside the same long-monitored meadow. It still does not eliminate meter-mark microhabitat differences or prove that the historical loss caused any measured physical difference.

The cross-sectional composition model remains supportive mechanism context. A positive cross-sectional composition coefficient cannot rescue an unresolved history-linked matched test.

An unresolved matched difference is not evidence of functional redundancy. The present design contains no post-outcome equivalence margin.

If the matched physical difference is resolved and the independently frozen bare-bed attribution gate passes, the result may be described as a difference in canopy ecosystem-engineering function associated with documented community turnover. If the bare-bed gate fails, retain the narrower wording of a difference in measured vertical velocity attenuation.
