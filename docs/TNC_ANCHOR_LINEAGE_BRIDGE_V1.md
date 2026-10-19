# Tampa TNC: sample-to-fixed-meter-mark lineage before ecological inference

Status: response-free implementation, synthetic regression tests; no real contemporary TNC or next-survey BB has been collected or accessed.

## What this protects

The decisive prospective hypothesis is that local rhizome TNC predicts **future Braun–Blanquet state at the same permanent mark** after the baseline BB and fixed transect node identity are controlled.

The frozen statistical script 72 takes only seven columns. It does not itself check official point-location IDs. The preceding lineage gate (analysis/85_tnc_anchor_lineage.py) matches four independently maintained source tables by the **exact frozen q25/q50/q75 node and point IDs** before generating those seven original columns. The existing model, effect support rules, 10,000 bootstraps, 36-node total / 6-per-bay gates remain unchanged.

## Required sources and blank templates

**Candidate records**: generated from the original contemporaneous node/date roster plus all sampled current meter marks by analysis/84_tnc_current_anchor_candidate.py (PR #160). Every candidate explicitly says CURRENT_BASELINE_INPUT_ONLY and NOT_AUTHORIZED, so the candidate is not permission to collect a core.

1. **External field-approval record**: field/tnc_approved_anchor_template.csv. Fields are node_id, water_body, anchor_id, point_location_id, approval_reference_id, approved_before_collection, anchor_freeze_date. A genuine monitoring-authority signoff, non-disturbance access conditions and permit review must occur externally before sampling. The code cannot authenticate the signer's authority or the physical no-disturbance zone.
2. **Actual core/HPLC/QC record**: field/tnc_core_mark_linkage_template.csv. Fields are node_id, water_body, anchor_id, point_location_id, core_id, core_collection_date, anchor_tnc, anchor_tnc_qc_pass. The sample must cite the same fixed mark and its unique actual core ID. A failed core makes its entire original three-anchor node incomplete.
3. **Actual later fixed-transect record**: field/tnc_future_same_mark_bb_template.csv. Fields are node_id, water_body, point_location_id, future_survey_date, future_bb_anchor. Each point must appear at the same later survey visit for its node. Sampled focal absence can equal numeric 0; missing, unvisited, or nonnumeric Reported is **not** coded as zero and cannot be rescued with another location.

All four source tables must be genuine and independently reviewed. The tool cannot establish that the external follow-up file is the *next complete eligible visit*: cross-check against the monitoring program's complete future point-event ledger separately.

## Run only when measurements genuinely exist

~~~bash
python analysis/85_tnc_anchor_lineage.py \
  --candidate actual_current_candidate_triplets.csv \
  --approval externally_approved_exact_mark_registry.csv \
  --tnc actual_frozen_core_HPLC_QC.csv \
  --future actual_next_transect_mark_BB.csv \
  --report source_mark_lineage.json \
  --primary-input versioned_frozen_anchor_primary.csv
~~~

Input CSV contents are checked against exact schemas (no extra/future columns in candidate/approval). The tool:
- rejects unauthorized/late-approved, duplicate, unknown or swapped core/mark identity records;
- rejects unlinked future observations and mismatched nodes, dates or official location IDs;
- maintains a row-level audited link (node, q25/q50/q75, point_location_id, core_id, source dates, QC state) without placing numeric future outcomes or TNC values in the public audit log;
- records one SHA-256 hash for each distinct semantic source role;
- drops the **whole original triplet** if any one q25/q50/q75 chemistry or future-BB mark is missing/nonnumeric, with no replacement or imputation.

Outputs:

- PASS_LINEAGE_FOR_FROZEN_PRIMARY_INPUT: at least 36 complete triplet nodes and >=6 in each bay, and every ID joins uniquely; produces seven-column input for the **unchanged** original frozen statistical model.
- STOP_COMPLETE_TRIPLET_GATE: not enough complete original triplets; no new frozen-model input is exported.
- Malformed/duplicate/swapped/late-approved input: the program errors rather than reporting an ecological coefficient.

A PASS is **not** field collection authorization, verified human signoff, independent measurement reliability, a result of the biological primary test, or an inference of clonal carbohydrate buffering. Do not publish sensitive real HPLC/future response rows to this public repository by default.

## Scientific scope

This prospective analysis is conditional on nodes currently possessing at least three quantitative Thalassia-positive meter marks. It may identify whether reserve state predicts subsequent local patch divergence beyond present visible state; it cannot automatically explain mortality, near-extinct meadow rescue, physiological integration, or whole-ecosystem recovery. The archival 2023–2025 mark reference (PR #159) is **not** current anchor authority.

PR #158 separately guards rank-deficient TNC regression designs; neither a correct regression nor the present exact-mark join eliminates unmeasured meter-mark microhabitat differences, observer BB variability, future-survey eligibility uncertainty, or time-varying common causes.

## Verification only with synthetic records

validation/test_tnc_anchor_lineage.py tests 36 synthetic four-bay nodes / 108 genuine-in-toy original q25/q50/q75 marks, a swapped core ID, a wrong next-survey point, duplicate visits, a missing future BB coded Reported, a legitimate observed BB zero, core QC loss of one entire node, late approval, CSV output and four source hashes. These are code/test cases, **not measured Tampa plants**.

Existing field pilot inputs remain blank; authoritative TNC field collection is still stopped pending actual permit, method pilot, contemporary baseline, HPLC and preservation resources.
