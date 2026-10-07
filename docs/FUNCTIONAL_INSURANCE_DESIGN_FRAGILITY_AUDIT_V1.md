# Tampa functional-insurance design fragility audit v1

## Purpose

This is a **response-independent pre-outcome design audit** of the frozen
history-linked functional-insurance cohort.

It does not use hydrodynamic outcomes and does not change the primary contract.
Its purpose is to document how strongly the confirmatory replication gate
depends on the already-frozen comparator-history and pair-distance rules.

Parent:
- `results/functional_insurance_loss_legacy_preflight_v1.json`
- `results/functional_insurance_loss_legacy_primary_v1_contract.json`

Frozen primary frame:
- Old Tampa Bay + Middle Tampa Bay;
- 18 planning pairs;
- confirmatory gate >=16 complete pairs total and >=6 per bay;
- persistent-Thalassia comparator run >=3 years;
- pair separation <=100 m.

The current 18 pairs have maximum separation 75 m, so the effective historical
distance support is 0-75 m even though the contractual ceiling is 100 m.

## Threshold sensitivity using the 18 pre-outcome pairs

The table below asks how many of the already selected pairs would survive
stricter **descriptive** history/distance requirements. These are not alternative
primary analyses and cannot be chosen after physical outcomes are observed.

| Maximum pair separation | Minimum comparator run | Total pairs | Old | Middle | Frozen replication gate |
|---:|---:|---:|---:|---:|---|
| 25 m | 3 y | 11 | 4 | 7 | FAIL |
| 50 m | 3 y | 15 | 7 | 8 | FAIL |
| 75 m | 3 y | 18 | 8 | 10 | PASS |
| 100 m | 3 y | 18 | 8 | 10 | PASS |
| 75 m | 4 y | 13 | 5 | 8 | FAIL |
| 75 m | 5 y | 12 | 5 | 7 | FAIL |
| 75 m | 6 y | 11 | 4 | 7 | FAIL |
| 100 m | 4 y | 13 | 5 | 8 | FAIL |
| 100 m | 5 y | 12 | 5 | 7 | FAIL |
| 100 m | 6 y | 11 | 4 | 7 | FAIL |

## Interpretation

The prospective question is feasible under the frozen v1 design, but the
confirmatory cohort is **not redundant to stricter design choices**.

Two facts matter:

1. the >=16-pair gate requires accepting pairs out to 75 m; restricting the
   historical cohort to <=50 m leaves 15 pairs;
2. the gate requires the >=3-year persistent-Thalassia comparator definition;
   requiring >=4 continuous years leaves 13 pairs and only 5 Old Tampa Bay
   pairs.

Therefore a future unresolved result must not be written as a broadly precise
test of all possible definitions of "nearby" or "long-term persistent
Thalassia". It is a test of the **prospectively frozen v1 state contrast**.

This does not invalidate the design. Pairing remains within stable transect
nodes, all historical pairs are <=75 m, state definitions were set before
velocity outcomes, and the physical measurements are simultaneous. But the
effective replication margin is small.

## Field-attrition consequence

The planning frame contains 18 pairs and the confirmatory minimum is 16.
Therefore only two complete-pair losses can occur before the total replication
gate fails, and per-bay attrition can fail the design earlier if Old Tampa Bay
drops below six complete pairs.

Before deployment:

- apply the frozen contemporaneous state recheck;
- enumerate the complete eligible pair set under the existing deterministic
  nearest-pair algorithm;
- do not retain a historically planned pair if its state definition no longer
  holds;
- do not relax the 3-year comparator rule, 100 m ceiling, or 6-per-bay gate to
  recover sample size;
- if fewer than 16 / 6-per-bay remain, classify the branch as pilot-scale
  before collecting/interpreting the physical outcome.

## Claim boundary

If the confirmatory gate passes, the allowed question remains:

> Does the frozen loss-legacy alternative state differ in measured
> hydrodynamic attenuation from the frozen nearby >=3-year persistent-Thalassia
> comparator state?

Do not generalize a null result to:
- equivalence of all alternative-seagrass and Thalassia meadows;
- equivalence under stricter >=4/5/6-year persistence definitions;
- equivalence at shorter spatial matching scales.

No equivalence margin is defined in v1.
