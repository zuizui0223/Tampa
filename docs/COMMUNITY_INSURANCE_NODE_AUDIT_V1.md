# Within-node audit of binary community insurance

## Question

The pooled exact-point Tampa analysis found that meter marks where another seagrass already co-occurred with *Thalassia* were more likely to remain seagrass-occupied after *Thalassia* was no longer recorded.

The pooled contrast was:

- source mixed: 85.1% target occupancy;
- *Thalassia*-only: 70.8%;
- difference: +14.3 percentage points;
- node-cluster bootstrap interval: +4.45 to +26.72 points.

That result can still arise if persistently favorable transects are both more likely to contain mixed seagrass and more likely to remain vegetated.

This audit therefore asks:

> **Does the binary mixed-versus-*Thalassia*-only association remain supported when comparison is restricted to variation within the same stable transect node?**

The design was frozen in `results/community_insurance_node_audit_v1_contract.json` before this binary within-node result was opened.

## Population

The audit uses exactly the same 370 consecutive exact-point *Thalassia*-loss transitions as the pooled analysis.

Only nodes containing both source states are informative:

- 18 stable nodes;
- 346 transitions;
- 259 source-mixed transitions;
- 87 source-*Thalassia*-only transitions.

## Model

Primary model:

```
target_any_seagrass_present
  ~ target_year
  + within-node-centered source_mixed
  + stable node fixed effects
```

Numeric predictors are standardized. The logistic learner and node-cluster bootstrap match the reference-saturation framework used for the existing diversity-insurance audit.

## Result

The centered source-mixture coefficient remained positive:

- standardized log-odds coefficient: **0.312**;
- corresponding OR per 1 SD: **1.37**;
- 95% node-cluster bootstrap interval for the coefficient: **-0.006 to 0.605**;
- OR interval: **0.994–1.83**.

The frozen support rule therefore **failed narrowly**.

Node-level directions were also heterogeneous:

- positive mixed-minus-alone occupancy difference: **9/18 nodes**;
- zero: **1/18**;
- negative: **8/18**;
- median node difference: **+4.2 percentage points**.

## Interpretation

The pooled association is real as a description of the Tampa monitoring record, but it is not robust evidence for a microsite-scale biodiversity-insurance mechanism after stable transect identity is saturated.

The safer statement is:

> **Pre-existing mixed seagrass marks are more likely to remain vegetated after focal *Thalassia* loss in the pooled record, but this advantage is not resolved within stable transects; persistent site quality remains a plausible explanation.**

This agrees with the existing within-node richness audit, whose positive coefficient also had a 95% interval overlapping zero.

## Biological consequence

This makes the prospective functional-insurance branch more—not less—important.

Retrospective composition cannot establish that alternative species locally buffer the habitat or its function. The prospective matched hydrodynamic study therefore should not be presented as confirmation of a proven biodiversity-insurance mechanism.

Instead it asks an independent historical-state question:

> **Do long-monitored meadow patches that now differ in focal foundation-species persistence also differ in directly measured physical ecosystem engineering, even when both remain vegetated?**

That question remains informative whether the physical contrast is positive, negative, or unresolved.

## Claim boundary

Do not call the pooled community-insurance pattern causal facilitation or local biodiversity insurance. Do not use a bay/species/year subset to rescue the failed within-node support rule. Continued seagrass occupancy is not evidence of functional equivalence.
