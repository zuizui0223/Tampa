# Verified warning evidence: manuscript synchronization

## Completed scope

The canonical Abstract, Methods, Results/Discussion, Figure 4 captions, README and operational note now reflect the completed fixed-mark audit. The existing single-file manuscript, Estuaries and Coasts layout and supplement were regenerated with the original, unchanged builders. Supplementary Tables S10–S12 separately preserve the original predictor comparison, the regularized node-ID comparison, the mark-revisit partitions and the unchanged alert-list counts.

The source computation remains GitHub Actions run 38109944875, executed head `fc3792e21f2d34e74de10cdbed6b48ac5603aabe`, artifact 11691158710. The source archive SHA256 is `18109267f68732c5460a9e4d087e2711282ed71f13f96ed7d0a484ed0320d89e`. A fresh independent reaggregation of the archived probabilities and overlap rows reproduced the prior result without refitting or rebuilding raw Event/Occurrence tables.

## Corrections

The manuscript build previously stopped because its required wording `not demographic extinction` had been lost from the canonical prose. That sentence was restored in context without disabling the guard. The stored manuscript outputs were then rebuilt rather than hand-edited. The supplementary Methods also now correctly name **source year**, not target year, as the predictor used by the actual model.

Figure 4 is not silently changed to the node-ID comparator: it retains the original space/time/effort comparison. Its title now describes low source state rather than claiming a measured deterioration sequence. The newer reference and revisit results are explicitly separated in Tables S10–S12. The Methods explain that L2-regularized node identity does not remove every possible persistent-site explanation.

Old pending labels for the completed fixed-mark result were removed from the active README, results section and operational note. The authorship paragraph no longer attests, without evidence, that final human review has already been completed. The draft remains subject to author review.

## Checked

`python validation/verify_warning_reporting_sync.py` passes 53 reporting and original-builder checks, including all three generated-file equalities, the original bibliography/caption/abstract guards, and numeric agreement between Tables S10–S12 and the canonical records. Deliberately changing an S11 event count, adding stale text to the generated manuscript, and removing the Methods mortality boundary each caused the verifier to fail; restoring the files restored PASS.

No analysis script, frozen ecological contract, original manuscript builder, model, predictor, fold, capacity, support rule or year exclusion was changed. This is a reporting synchronization, not a new ecological finding or an additional confirmation.

## Remaining boundaries

This does not certify the whole repository. In the pre-change snapshot, `verify_measurement_layer_hard_stop.py` failed an exact-text requirement for the functional-insurance equivalence rule, and `verify_tnc_v2_authority.py` failed an exact-text requirement for the TNC status note. Those unrelated checks and their source contracts were not changed or relaxed here. No TNC measurements, physiological mechanism, demographic mortality, management intervention result or final human-author approval is supplied. PR #155 remains draft and unmerged.
