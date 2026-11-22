# Tampa: re-recording history as a verification stratum (2026-11-22)

## Scientific scope

**Post-hoc descriptive arithmetic only.** This derives a monitoring-relevant concentration from the *already frozen* exact-point four-year return-fragility summary. It neither fits a new model nor reopens outcomes, searches for a favorable subgroup, claims a prospective alarm, or changes the ecological mechanism hard stop.

- Re-recorded group: *Thalassia* observed at t, unrecorded at t+1, recorded again at t+2; endpoint is another recorded non-detection at t+3.
- Uninterrupted group: *Thalassia* recorded at t, t+1, t+2; same next-year endpoint.
- Annual observations span 2016–2025 and require four consecutive sampled years.
- **Unit:** potentially overlapping exact-meter-mark four-year **sequences**, not independently selected sites, independent restoration outcomes or independent forecast trials.

## Existing source-derived empirical numbers

Source: results/return_fragility_v1.json (canonical summary), analysis/42_return_fragility.py.

| Group | Eligible sequences | Next-year recorded non-detections | Sequence-level rate |
| --- | ---: | ---: | ---: |
| Re-recorded | 83 | 30 | 36.14% |
| Uninterrupted | 497 | 64 | 12.88% |
| **Total** | **580** | **94** | **16.21%** |

Descriptive rate difference **+23.27 percentage points**; unadjusted relative rate **2.807**. The previously fitted *node-bootstrap* model yielded a positive coefficient **0.3198** (CI **[0.0775, 0.5688]**) on a **standardized predictor scale**. This is not an unstandardized odds ratio and is not recomputed by the new script.

The re-recorded group represents **83/580 = 14.31% of eligible sequences** but contains **30/94 = 31.91% of next-year recorded non-detections**. Concentration = 31.91/14.31 = **2.230**. This is *historical concentration*, **not prospective recall**, validated watchlist improvement, a 14.3% allocation of independent sites, or a treatment recommendation.

Separate three-year quantitative cohort: results/recovery_debt_v1.json found target-year Braun–Blanquet index **1.95** after re-recording (109 sequences) versus **2.93** with uninterrupted occurrence (592 sequences), with adjusted coefficient **−0.204** (node-bootstrap CI **[−0.302, −0.103]**). **Do not combine the different 701-sequence and 580-sequence denominators.** Re-recording can mark both a depleted quantitative state and later observational fragility, but the mediator linking them has not been demonstrated.

## Ecological and sampling boundaries

1. Non-detection and re-recording are *observation states*, not mortality, demographic recolonization or true ecological recovery. Mark identifiers, quadrat placement and observer/detection processes can change.
2. Sequences may overlap and are clustered by marks/nodes. Four-year completeness conditions on revisits and selects the evaluable population. No new confidence interval, p-value or inferential replication is supplied by an arithmetic ratio.
3. The already frozen return-quality fragility test (results/return_quality_fragility_v1.json) **did not** show that return-year abundance explains later re-loss after its controls: the CI includes zero.
4. Pooled community-mixture persistence is not a supported within-node causal community-insurance effect (results/community_insurance_node_audit_v1.json). Do not infer facilitation, functional replacement, rhizome persistence or a resilience threshold.
5. Literature already reports recovery asymmetries and history-dependent seagrass trajectories (e.g. van Katwijk et al. 2024, DOI 10.1111/1365-2664.14704; Kendrick et al. 2025, DOI 10.1111/rec.70040). Tampa does not establish the first existence of hysteresis.

**Management-level interpretation:** A newly re-recorded positive mark should be *reverified* with source mark identity, sampled footprint, effort and quantitative abundance before it is treated like uninterrupted occupied habitat. A field programme could stratify rechecks by recorded-history category, but effectiveness and cost relative to current abundance/frequency or random node-level follow-up require an independently specified future audit. Do not promote this to an operational alarm.

## Reproduction

The pure-standard-library script reads the exact existing result summary and fails closed on schema/status/count inconsistency. Four no-network unit tests cover expected arithmetic, incoherent total, rounded probabilities, and invalid authority status.

~~~bash
python -m unittest discover -s validation -p 'test_return_history_monitoring_arithmetic.py' -v
python analysis/109_return_history_monitoring_arithmetic.py \
  --source results/return_fragility_v1.json \
  --out /tmp/tampa_return_history_monitoring_arithmetic.json
~~~

Keep this descriptive monitoring addendum *outside the causal-mechanism Results* until author review. The prospective below-ground TNC / near-canopy measurement priorities in docs/ECOLOGICAL_MECHANISM_BOUNDARY_V1.md remain unchanged.
