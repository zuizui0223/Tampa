# Pre-outcome numerical identifiability erratum — Tampa TNC models

**Date:** 2026-10-13  
**Status:** Response-free known-truth regression checks passed; draft PR, not merged.

## Scientific issue

The paper-level decisive TNC experiment asks whether measured within-node differences in rhizome carbohydrates predict future *Thalassia* Braun–Blanquet state beyond measured current local BB and stable node fixed effects. The adjacent depth-adjusted sensitivity and the three-bay 42-day reserve-trajectory diagnostic ask related, separate questions.

The pre-existing least-squares code accepted a **rank-deficient** design matrix. `numpy.linalg.lstsq` solves singular problems using a minimum-norm pseudoinverse; it can therefore return a *finite, positive* TNC coefficient even when the data **cannot uniquely separate that coefficient** from another predictor. Such a number is not a biologically interpretable association and must not enter a bootstrap confidence interval.

In a 36-node × 3-anchor synthetic known-truth example with future BB generated from baseline BB alone, and TNC exactly equal to a shifted baseline BB, the original code returned a positive TNC coefficient of approximately **0.667**, although model-matrix rank was **37 of 38 columns**. This number is **synthetic regression aliasing**, not an observed Tampa effect.

The companion risks are:
- local TNC contrasts exactly aliased with local baseline depth in the depth-adjusted sensitivity;
- reserve change exactly aliased with current TNC stock in the three-bay 42-day reserve-trajectory diagnostic.

## Narrow correction

Each of these three existing models now reads `rank` directly from its **unchanged `np.linalg.lstsq` decomposition**. If `rank < number_of_model_columns`, it rejects the coefficient with `np.linalg.LinAlgError` rather than reporting a pseudocoefficient.

On a rank-deficient **full-sample** design, the existing program outputs:
- `status = NONESTIMABLE_DESIGN_RANK`;
- `classification = nonestimable`;
- no focal point estimate or confidence interval.

On rank-deficient **bootstrap** draws, the existing try/catch skips invalid draws. The original **at least 95% valid replicates** requirement still governs whether the whole interval is estimable.

No predictor, biological endpoint, rank-based sample subset, model formula, time window, sample gate, bootstrap count/seed, confidence interval cutoff or sign rule was changed. No response-adaptive rescue is introduced.

## Frozen code provenance

Only three code files and their hash-pinned pre-outcome freeze records were amended:

| Frozen model | Code | Before blob SHA-1 | After blob SHA-1 |
|---|---|---|---|
| Paper-level decisive anchored TNC | `analysis/72_anchor_tnc_future_bb_diagnostic.py` | `d77bf90fe4ee17d4d81379b822aa39c3beef9852` | `2770e83607088b18c077c8bb0ce4a6aeaa6af9d4` |
| Local-depth sensitivity | `analysis/76_anchor_tnc_future_bb_depth_sensitivity.py` | `c5a332ba8f35a624a61145775fd4f33075285bdf` | `54f53858ba4b232701b71c978c50d95a54f0bfee` |
| Three-bay dynamic reserve trajectory | `analysis/71_dynamic_reserve_future_diagnostic.py` | `b32151c93a8c9c804b159c3295c3b03469b6a2e3` | `ad3b626df09af85a2470f41f94bd3045e836e9b3` |

Each freeze JSON retains the original blob hash in a `pre_outcome_identifiability_erratum` field. The scientific hierarchy remains `results/clonal_state_inference_hierarchy_v1.json`: decisive local anchored TNC, supportive four-bay network test; depth and dynamic trajectories cannot rescue an unsupported primary.

## Regression evidence

The test `validation/test_anchor_tnc_rank_identifiability.py` uses **synthetic only** input satisfying existing nominal sample gates, including 36 independent nominal nodes across four bays for the local spatial models and 30 across three bays for the dynamic model.

- **RED** on the previous decisive code: [Actions #38410314246](https://github.com/zuizui0223/Tampa/actions/runs/38410314246), false nonidentifiable TNC coefficient returned.
- **RED** on the prior depth code: [Actions #38410956741](https://github.com/zuizui0223/Tampa/actions/runs/38410956741), false nonidentifiable TNC/depth coefficient returned.
- **RED** on the prior dynamic code: [Actions #38411144319](https://github.com/zuizui0223/Tampa/actions/runs/38411144319), false nonidentifiable reserve-stock/trajectory coefficient returned.
- **GREEN** with all three rank checks and frozen-hash tests: [Actions #38411363513](https://github.com/zuizui0223/Tampa/actions/runs/38411363513). The full-rank positive-control primary simulation also remains estimable.

No primary ecological, physiological or HPLC outcome was opened or created for this test. The prior method-pilot input fields remain blank; the true field/laboratory readiness status is still `STOP_RESOURCE_FREEZE_INCOMPLETE`.

## Ecological interpretation boundary

This repair prevents **non-identifiability from being mislabelled as reserve evidence or a null result**. It does not prove that future TNC association is causal buffering. Even a full-rank fitted model can remain confounded by unmeasured current local state, meter-mark microhabitat, assay measurement error and time-varying conditions. The source-authoritative fixed design and original hypothesis labels must not be changed based on future outcomes.

PR review should verify that the amendment is adopted **before any outcome-bearing TNC or future meadow response is opened**. If outcome data have already been seen elsewhere, do not retrospectively label this amendment preregistered.
