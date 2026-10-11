# Verified warning evidence synchronization implementation plan

> Execute inline against the isolated, hash-verified PR #155 snapshot.

**Goal:** Synchronize existing fixed-mark and recorded-loss evidence into the canonical manuscript sections, the two existing manuscript outputs, and the supplement without changing any biological estimator.

**Architecture:** Preserve the existing builders and scientific checks. Apply deterministic section edits from the verified result record, then run the unchanged builders and a reporting-only verification. A one-time branch-scoped materialization job may publish the verified document changes; it must refuse a concurrent head change and must not merge the PR.

**Tech stack:** Python standard library, existing manuscript builders, Git and GitHub Actions.

**Spec:** `docs/EARLY_WARNING_FIXED_MARK_VERIFIED_V1.md` and `results/early_warning_fixed_mark_overlap_verified_v1.json`.

## Constraints

Keep the 688/24 and scored 570/19 registries, all models, C=1.0, target-year folds, 2016 inclusion, the original 10%/20% lists, and all frozen support rules unchanged. Figure 4 retains the original space/time/effort comparator. New displays are descriptive tables, not new ecological tests. Do not claim absence is mortality or certify author approval.

## Tasks and checks

- [x] Reproduce existing manuscript failure: missing `not demographic extinction`.
- [x] Add a reporting-only regression verifier; confirm it fails on the uncorrected snapshot.
- [x] Synchronize Abstract, Methods, Results/Discussion, Figure 4 captions, README, monitoring note and supplement. Correct source-year/target-year wording and qualify regularized node identity.
- [x] Regenerate the original manuscript, journal-layout manuscript and supplement with unchanged builders.
- [x] Verify generated equality, numerical table agreement, negative mutation tests, idempotence, and no changes to any analysis or frozen contract.
- [ ] Materialize checked documents on the existing PR branch with a concurrency check; retain draft/unmerged status.

## Explicitly outside this change

Existing failures in measurement-layer and TNC-authority checks are recorded separately. No prospective physiological measurement, new calibration inference, causal identification or final author sign-off is supplied by this documentation change.
