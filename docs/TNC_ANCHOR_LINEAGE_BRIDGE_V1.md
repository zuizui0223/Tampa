# Tampa TNC: sample-to-fixed-meter-mark lineage before ecological inference

Status: response-free implementation, synthetic regression tests; no real contemporary TNC or next-survey BB has been collected or accessed.

## What this protects

The decisive prospective hypothesis is that local rhizome TNC predicts **future Braun–Blanquet state at the same permanent mark** after the baseline BB and fixed transect node identity are controlled.

The frozen statistical script 72 takes only seven columns. It does not itself check official point-location IDs. The preceding lineage gate (analysis/85_tnc_anchor_lineage.py) matches **five** source tables, including the future sampled Point-event census, by the **exact frozen q25/q50/q75 node and official point IDs** before generating those seven original columns. The existing model, effect support rules, 10,000 bootstraps, 36-node total / 6-per-bay gates remain unchanged.

## Required sources and blank templates

**Candidate records**: generated from the original contemporaneous node/date roster plus all sampled current meter marks by analysis/84_tnc_current_anchor_candidate.py (PR #160). Every candidate explicitly says CURRENT_BASELINE_INPUT_ONLY and NOT_AUTHORIZED, so the candidate is not permission to collect a core.

1. **External field-approval record**: field/tnc_approved_anchor_template.csv. Fields are node_id, water_body, anchor_id, point_location_id, approval_reference_id, approved_before_collection, anchor_freeze_date. A genuine monitoring-authority signoff, non-disturbance access conditions and permit review must occur externally before sampling. The code cannot authenticate the signer's authority or the physical no-disturbance zone.
2. **Actual core/HPLC/QC record**: field/tnc_core_mark_linkage_template.csv. Fields are node_id, water_body, anchor_id, point_location_id, core_id, core_collection_date, **soluble_nsc_mg_g, starch_mg_g**, anchor_tnc_qc_pass. The sample must cite the same fixed mark and its unique actual core ID. The bridge mechanically constructs the frozen predictor **anchor_tnc = soluble_nsc_mg_g + starch_mg_g** (two nonnegative numeric HPLC components), not a hand-entered total. No conversion to another reserve proxy or secondary carbohydrate fraction is authorized. Missing either component or a failed core makes its entire original three-anchor node incomplete. Independently verify the assay/tissue/batch QC against the authoritative TNC-v2 baseline validator; this identity bridge does not replace those chemical checks.
3. **Actual later fixed-transect numeric BB report**: field/tnc_future_same_mark_bb_template.csv. Fields are node_id, water_body, point_location_id, future_survey_date, future_bb_anchor. It contains the reported quantitative future focal BB corresponding to original marks, **but its row alone cannot prove a visit occurred**.
4. **Independent actual sampled Point-event and focal occurrence evidence**: field/tnc_future_sampled_point_event_template.csv. Fields are node_id, water_body, point_location_id, future_survey_date, point_event_id, thalassia_present, raw_thalassia_bb. Supply the **actual eventID from a genuinely sampled Point visit** and focal occurrence status derived from the official raw occurrence/measurement archive, not from the BB prediction/monitoring shortlist. If the point was sampled and the focal species was not present, thalassia_present=false and raw_thalassia_bb is blank; only then may a matching separate numeric future BB=0 be accepted. If sampled focal presence is true, its raw numeric BB must match the separate future BB record. A focal-present nonnumeric Reported is quantitatively missing, **never absence**.

A mark that was **not sampled** in the actual future Point-event ledger is also missing, even if somebody entered 0 in the separately supplied future BB report. That invalidates the original node triplet instead of creating a false disappearance event. Duplicated Point eventIDs, contradictory source occurrence status and mismatched same-visit dates are rejected. Extra non-anchor Point-event rows at the same node/date may be included; **the completeness and provenance of the supplied future Point-event ledger must still be independently audited against the official monitoring archive**.

All **five** source tables must be genuine and independently reviewed. A structurally valid eventID and a user-supplied presence flag alone are **not proof** that the true raw archive supports them. The tool cannot independently establish that the supplied event census is complete or that the target is the *first eligible next survey*: verify both against the monitoring program's authoritative future Event/Occurrence/eMoF source before ecological inference.

## Run only when measurements genuinely exist

~~~bash
python analysis/85_tnc_anchor_lineage.py \
  --candidate actual_current_candidate_triplets.csv \
  --approval externally_approved_exact_mark_registry.csv \
  --tnc actual_frozen_core_HPLC_QC.csv \
  --future actual_next_transect_mark_BB.csv \
  --future-point-events official_future_sampled_point_events_and_occurrences.csv \
  --report source_mark_lineage.json \
  --primary-input versioned_frozen_anchor_primary.csv
~~~

Input CSV contents are checked against exact schemas (no extra/future columns in candidate/approval). The tool:
- rejects unauthorized/late-approved, duplicate, unknown or swapped core/mark identity records;
- rejects unlinked future observations and mismatched nodes, dates or official location IDs;
- maintains a row-level audited link (node, q25/q50/q75, point_location_id, core_id, source dates, QC state) without placing numeric future outcomes or TNC values in the public audit log;
- records one SHA-256 hash for each of the five distinct source roles, including actual future point-event evidence;
- drops the **whole original triplet** if any one q25/q50/q75 chemistry, officially sampled future mark event, or future-BB measurement is missing/nonnumeric, with no replacement or imputation.

Outputs:

- PASS_LINEAGE_FOR_FROZEN_PRIMARY_INPUT: at least 36 complete triplet nodes and >=6 in each bay, and every ID joins uniquely; produces seven-column input for the **unchanged** original frozen statistical model.
- STOP_COMPLETE_TRIPLET_GATE: not enough complete original triplets; no new frozen-model input is exported.
- Malformed/duplicate/swapped/late-approved input: the program errors rather than reporting an ecological coefficient.

A PASS is **not** field collection authorization, verified human signoff, independent measurement reliability, a result of the biological primary test, or an inference of clonal carbohydrate buffering. Do not publish sensitive real HPLC/future response rows to this public repository by default.

## Scientific scope

This prospective analysis is conditional on nodes currently possessing at least three quantitative Thalassia-positive meter marks. It may identify whether reserve state predicts subsequent local patch divergence beyond present visible state; it cannot automatically explain mortality, near-extinct meadow rescue, physiological integration, or whole-ecosystem recovery. The archival 2023–2025 mark reference (PR #159) is **not** current anchor authority.

PR #158 separately guards rank-deficient TNC regression designs; neither a correct regression nor the present exact-mark join eliminates unmeasured meter-mark microhabitat differences, observer BB variability, future-survey eligibility uncertainty, or time-varying common causes.

## Verification only with synthetic records

validation/test_tnc_anchor_lineage.py and validation/test_tnc_future_point_event_evidence.py test 36 synthetic four-bay nodes / 108 mock q25/q50/q75 marks, a swapped core ID, a wrong next-survey point, duplicate sampled eventIDs, a false BB=0 at an **unvisited** mark, contradictions between raw focal presence and entered BB, a focal-present nonnumeric Reported, a genuinely sampled BB zero, whole-node QC exclusion, late approval, CSV output and five source hashes. These are code/test cases, **not measured Tampa plants**.

Existing field pilot inputs remain blank; authoritative TNC field collection is still stopped pending actual permit, method pilot, contemporary baseline, HPLC and preservation resources.
