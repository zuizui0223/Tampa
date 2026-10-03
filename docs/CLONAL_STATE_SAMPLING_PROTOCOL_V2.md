# Tampa clonal / below-ground measurement protocol v2

## Authority

This is the **authoritative outcome-bearing TNC field protocol**.

Primary contract:

- `results/clonal_state_prospective_v2_contract.json`

Historical design record:

- `results/clonal_state_prospective_v1_contract.json`
- `docs/CLONAL_STATE_SAMPLING_PROTOCOL_V1.md`

The v1 three-bay design is retained for provenance. It was prospectively superseded on 2026-10-01, before the first future outcome-bearing TNC core and before future meadow-response access.

Do not choose between v1 and v2 after outcomes are known.

## v2 primary geography

The primary prospective TNC test is fixed to four bays:

- Old Tampa Bay;
- Middle Tampa Bay;
- Lower Tampa Bay;
- Boca Ciega Bay.

Historical planning frame:

- Old: 8 recent *Thalassia*-positive stable nodes;
- Middle: 11;
- Lower: 14;
- Boca Ciega: 8;
- total: 41.

Attempt census-oriented sampling of every contemporaneously eligible node.

Primary confirmation requires:

- >=36 analyzable nodes total;
- >=6 analyzable nodes in **each** of the four bays.

With baseline frequency, baseline Braun-Blanquet state and a four-level water-body factor, the approximate two-sided 80%-power detectable partial correlation for TNC is about:

- n=36: |partial r| ≈ 0.474;
- n=40: ≈0.449;
- n=41: ≈0.443.

This remains a moderate-to-large-effect design.

If the replication gate fails, report the frozen estimate/interval as pilot or sensitivity evidence. Do not interpret a null as rejection of reserve buffering.

## What v2 changes

Only the prospective geography / sample-size planning is promoted from the historical v1 design.

The following remain frozen from the established TNC programme:

- primary predictor = rhizome TNC = soluble NSC + starch;
- one HPLC-based analytical workflow;
- one frozen horizontal-rhizome tissue class;
- >=3 spatially distributed cores per node;
- q25/q50/q75 anchor logic where >=3 positive marks exist;
- sparse-node fallback geometry;
- one <=28-day outcome-bearing TNC campaign;
- TNC within +/-14 days of the paired fixed-transect baseline survey;
- leaf N/P nutrient-state diagnostic;
- genet-identity diagnostic as secondary interpretation only;
- destructive-sampling guardrail;
- continuous future quantitative endpoint;
- binary re-recording is not recovery.

Where this v2 overlay does not explicitly change a procedure, the technical procedure in `docs/CLONAL_STATE_SAMPLING_PROTOCOL_V1.md` remains the frozen implementation basis.

## Primary model

```text
future_delta_frequency
  ~ baseline_frequency
  + baseline_Braun_Blanquet
  + rhizome_TNC
  + water_body
```

`water_body` is a **four-level factor**, requiring three indicator degrees of freedom.

Directional hypothesis:

> higher baseline rhizome TNC predicts more positive / less negative future quantitative *Thalassia* change.

Support is based on the frozen two-sided 95% interval.

Do not change to a three-bay model, one-sided test, alternative reserve variable or favorable subgroup after outcome access.

## Four-bay field synchronization

The timing requirement becomes more important, not less, after adding Boca Ciega.

All primary nodes must still satisfy:

- one <=28-day TNC campaign;
- same-day baseline fixed-transect survey preferred;
- hard TNC-to-baseline alignment <=14 days;
- same tissue/assay/preservation rules.

If routine monitoring cannot fit the window, perform the already-authorized dedicated quantitative baseline survey rather than widening the TNC season.

Boca Ciega may not be sampled under a different seasonal or laboratory regime merely to preserve n.

## Spatial core design

Use the frozen q25/q50/q75 anchor logic.

The historical three-bay preflight showed:

- 30 nodes with >=3 positive marks;
- 3 sparse fallback nodes.

The Boca Ciega design preflight showed:

- 8 recent *Thalassia*-positive nodes;
- all 8 with >=3 positive marks.

Therefore the standard three-distinct-anchor design is expected to apply directly in Boca Ciega, subject to contemporaneous eligibility.

## Four-bay within-transect site-template diagnostic

A separate baseline-only preflight was frozen before inspection and has now passed:

- `analysis/62_tnc_anchor_bb_four_bay_preflight.py`
- canonical result: `results/tnc_anchor_bb_four_bay_preflight_v1.json`
- frozen minimum: >=36 nodes with three distinct quantitative anchors;
- frozen minimum: >=6 nodes per bay;
- observed eligible nodes: **38**;
- observed by bay: Old 8, Middle 10, Lower 12, Boca Ciega 8.

This establishes design feasibility only; it is not evidence that TNC predicts a future response.

The secondary spatial diagnostic is:

```text
future_BB_anchor
  ~ baseline_BB_anchor
  + within_node_centered_anchor_TNC
  + node_fixed_effect
```

This asks whether local TNC differences predict local future quantitative state after stable transect identity is removed.

It cannot replace or rescue the node-level four-bay TNC primary.

The four-bay feasibility gate passed before future outcome access. Do not change anchor eligibility, geography, or the 36-total / 6-per-bay gate after TNC or future outcomes are observed.

## Dynamic reserve trajectory

The separately frozen pre/post TNC programme provides a temporal site-template-resistant diagnostic:

```text
delta_tnc_42d = tnc_post - tnc_pre

future_delta_frequency
  ~ baseline_frequency_post
  + tnc_post
  + delta_tnc_42d
  + water_body
```

The current reserve level (`tnc_post`) remains in the model. The focal question is whether recent reserve trajectory adds information beyond current reserve state.

This is secondary. It cannot rescue a null four-bay static TNC primary.

## Regenerative-capacity measurement

TNC and meristem state are deliberately distinct.

- TNC: energetic resistance / stored reserve.
- rhizome meristem or apex density: regenerative capacity.

Meristem/apex density remains a corrected secondary family unless a separately powered recovery-capacity study is frozen.

A positive meristem result does not convert a null TNC result into support for carbohydrate buffering.

## Genet boundary

DNA-quality tissue may be preserved from each TNC anchor.

Repeated multilocus genotypes can establish genet identity across sampled anchors.

They do **not** establish:

- an intact contemporary rhizome connection;
- active physiological integration;
- resource translocation.

TNC is therefore a reserve-state measurement, not a direct clonal-integration measurement.

## Precollection fail-closed system

The v2 baseline is governed by:

- `field/tnc_v2_precollection_freeze.json`
- `validation/validate_tnc_v2_baseline.py`

No outcome-bearing core is accepted until every response-independent field in the precollection freeze is completed.

The baseline manifest must contain no future-response columns.

## No-reversion rule

After the first outcome-bearing v2 core or any future response access:

- do not revert to the v1 three-bay primary;
- do not remove Boca Ciega because its future result is inconvenient;
- do not add another bay to rescue a null;
- do not change the >=36 / >=6-per-bay confirmatory gate;
- do not change timing, HPLC, tissue, core geometry or future endpoint.

The purpose of v2 is a single prospective four-bay test whose null is scientifically interpretable.
