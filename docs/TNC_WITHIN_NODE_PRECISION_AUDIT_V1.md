# Tampa within-node TNC decisive-primary precision audit v1

## Purpose

The paper-level decisive prospective TNC test is no longer the older four-bay cross-node model. It is the frozen within-meadow state-augmentation model:

~~~text
future_BB_anchor
  ~ baseline_BB_anchor
  + within_node_centered_anchor_TNC
  + node_fixed_effect
~~~

with exactly three frozen anchors per complete node.

This response-free audit asks a narrow design question before any TNC or future outcome is opened:

> **what effect scale can the 38-node × 3-anchor design reasonably resolve, and what size of unsupported effect must remain biologically unresolved?**

This document does not change the primary estimator, support rule, sampling geometry or replication gate.

## Frozen design used for the benchmark

Current response-independent preflight:

- complete three-anchor nodes: **38**;
- anchors per node: **3**;
- anchor rows if all remain complete: **114**;
- water bodies: Old 8, Middle 10, Lower 12, Boca Ciega 8;
- decisive gate: >=36 complete nodes and >=6 per bay.

At the 38-node planning value, the fixed-effect model has approximately:

- 114 anchor observations;
- 38 node intercepts in total;
- baseline local Braun-Blanquet;
- within-node centered TNC.

This leaves about **74 residual degrees of freedom** under the simple Gaussian benchmark.

## Analytic resolution benchmark

Under an ordinary Gaussian partial-correlation approximation with two-sided alpha 0.05 and 80% power, residual df ≈74 corresponds to a detectable partial correlation of approximately:

> **|partial r| ≈ 0.32**

This is only a mathematical reference point.

The actual frozen inference uses a water-body-stratified **stable-node cluster bootstrap**, not an iid t test, so the 0.32 value must not be reported as formal study power.

## Response-free cluster-bootstrap simulation benchmark

A synthetic design replay was run without empirical TNC or future outcome values.

Simulation structure:

- 38 independent nodes;
- three anchors per node;
- predictor centered within node;
- one baseline local-state covariate;
- node means absorbed by node fixed effects;
- one standardized future residual scale;
- whole nodes resampled in the bootstrap;
- no outcome-dependent node/anchor selection.

The simulation expresses the focal effect as:

> future within-node state difference in residual SD units per 1 SD of **measured within-node TNC**.

Under moderate baseline-state/TNC collinearity (approximately r = 0.3), the design reached about 80% directional support at roughly:

- **beta ≈ 0.34 residual SD per measured-TNC SD** for the ordinary two-sided 95% interval;
- **beta ≈ 0.38 residual SD per measured-TNC SD** for the two-member-family 97.5% interval.

Under deliberately stronger baseline-state/TNC collinearity (approximately r = 0.6), the family-corrected 80%-resolution scale moved toward approximately:

- **beta ≈ 0.45 residual SD per measured-TNC SD**.

These are resolution benchmarks, not biological effect predictions.

## Interpretation boundary

The decisive test is therefore not restricted only to enormous effects, but it is also not a high-resolution small-effect study.

A useful pre-outcome interpretation rule is:

> **the within-node design is mainly capable of resolving moderate local state-augmentation effects.**

If the decisive interval overlaps zero:

- do **not** write that rhizome reserve has no effect;
- do write that the study did not support a moderate within-meadow effect at the designed measurement/reliability scale;
- keep smaller state-augmentation effects unresolved;
- do not use a positive network-scale cross-node association to rescue the decisive primary.

## Measurement reliability matters

The benchmark is defined per SD of **measured** within-node TNC.

Laboratory error, tissue heterogeneity or poor spatial correspondence between the adjacent core and permanent meter mark will attenuate the observable coefficient.

Therefore the response-independent HPLC/tissue/offset pilot is not merely logistical. It determines whether the biological signal entering the decisive model has enough reliability for the above resolution benchmark to be meaningful.

This strengthens the existing rule that all three anchors must pass the authoritative TNC analytical QC and that failed anchors cannot be replaced after future outcomes are seen.

## Why this matters for novelty

The literature already contains seagrass reserve -> later growth/cover relationships.

The Tampa decisive test is harder:

> **within the same long-monitored meadow, after current local above-ground state and stable node identity are represented, does measured reserve heterogeneity forecast which local patch retains more Thalassia?**

The present precision audit shows that this question has a realistic chance of resolving a moderate effect rather than functioning only as a symbolic prospective add-on.

## Status

**PASS_RESPONSE_FREE_PRECISION_AUDIT_WITH_MODERATE_EFFECT_BOUNDARY**

No outcome-bearing data were used.
