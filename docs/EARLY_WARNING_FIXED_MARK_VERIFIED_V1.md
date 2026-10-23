# Fixed-mark revisit audit: completed result and alert-capture decomposition

## Current status

**COMPLETED_OBSERVATION_PROCESS_AUDIT**, verified 2026-10-11. This resolves the analysis/81 result that earlier draft README/manuscript sections labelled pending. Those earlier pending labels do not describe the current evidence; this report and the accompanying canonical JSON are the result record.

This is a post-hoc audit of an already-opened observation endpoint, not an additional ecological mechanism test. The existing predictive model, 2016 handling, 10%/20% capacities and statistical support rule were not altered. The capture decomposition below was calculated after the overlap outcome was inspected and is descriptive only.

## Source and verification

- Successful workflow: https://github.com/zuizui0223/Tampa/actions/runs/38109944875
- Executed head: `fc3792e21f2d34e74de10cdbed6b48ac5603aabe`.
- Artifact ID: `11691158710`, `tampa-site-saturated-early-warning`.
- ZIP SHA256: `18109267f68732c5460a9e4d087e2711282ed71f13f96ed7d0a484ed0320d89e`.
- Raw source reconstructed and hash-checked by that workflow: `tbep-tech/obis-example` at `6c567beff95ea04f0e397101befb49d5233ace8f`.
- A separate calculation verified the downloaded archive digest, every exported overlap row, the matched prediction cohort, all four arms' probability-derived scores and the original alert lists. It did not import the repository's estimator or refit any model. This was **independent artifact reaggregation**, not another independent reconstruction from raw Event/Occurrence bytes.

The earlier four prediction outputs remain numerically consistent: maximum probability difference between the two successful runs was below 8e-15, and the monitoring-utility JSON was byte-identical.

## 1. Were previously positive marks revisited?

A positive mark means a nominal permanent metre-mark `locationID` at which Thalassia was recorded in at least one eligible source-year visit. Revisited means the same ID appears in at least one eligible next-year visit. These are identities in the observation archive, not a guarantee of identical microquadrat placement or perfect detection.

| Recorded-loss population | Loss events | No source-positive mark revisited | Some but not all revisited | All source-positive marks revisited |
|---|---:|---:|---:|---:|
| All consecutive source-positive transitions | 24 | 7 | 7 | 10 |
| Original scored walk-forward cohort | 19 | 5 | 7 | 7 |
| Target-year 2016 loss events | 5 | 0 | 3 | 2 |

Thus at least one previously positive mark was revisited in **17/24** full-cohort losses and **14/19** scored losses. The full source-positive cohort has 688 transitions; the scored cohort has 570. Loss events are repeated observations, not independent meadows: they involve 18 and 14 nodes, respectively.

For 7/24 events, the archive does not establish what happened to the original positive marks in the target year. A changed sampling footprint is possible; persistence of the unvisited plants is not established. For 17/24, failure to revisit any original positive mark cannot be the sole explanation of the recorded transition. True local change, imperfect detection, effective quadrat repositioning and protocol effects remain unresolved alternatives.

A concrete example explains why sampled-point count alone is insufficient: at S1T17 in 2007-2008, 109 sampled mark IDs were shared between years and 110 marks were sampled in the target year, yet neither of the two source-positive marks was revisited. This does not prove that those patches survived.

All five adverse 2016 loss events revisited at least one previously positive mark. At S3T5, 13 of the 15 source-positive marks were revisited. This narrows the footprint explanation but does not resolve the previously documented 2016 date/protocol concern or identify a mortality mechanism.

## 2. Does the added event capture occur only in unvisited patches?

No. The original annual alert lists were left unchanged and their captured loss events were classified by mark-revisit status. No subset was reranked, refitted or used to rescue a statistical endpoint.

| Nominal annual cap | Alerts in each arm | All loss captures: node -> node+quant | Captures with >=1 prior positive mark revisited | Added captures: revisited / none revisited |
|---|---:|---:|---:|---:|
| 10% | 47 | 6 -> 9 | 4 -> 6 | 2 / 1 |
| 20% | 105 | 9 -> 13 | 7 -> 9 | 2 / 2 |

Neither capacity lost an event previously captured by the node reference. The lists changed 13 and 35 selections, respectively. The two added revisited events are **different events across the two capacities**; do not add the counts together as independent confirmations.

At the 10% cap, the newly captured revisited events are S3T9 in 2014 (2/2 previous positive marks revisited) and S1T18 in 2021 (1/1). At the 20% cap they are S3T2 in 2006 (2/7) and S3T9 in 2011 (3/5). The other added captures had no source-positive mark revisited.

The original overall positive predictive values remain **9/47 = 19.1%** and **13/105 = 12.4%**. Revisited non-detection is not a measured mortality endpoint, and the unvisited events are not relabelled false alarms. The partition adds no new p-value, detection-error estimate or treatment benefit.

## 3. Predictive result retained, causal wording narrowed

Independent probability-based calculation reproduced the earlier result: pooled AUC **0.67055 -> 0.73636**, macro annual log loss **0.148268 -> 0.147230**, and **17/23** improved target years (frozen one-sided sign-test p **0.0173448**). The 2016 increment remains adverse at **+0.305633**.

The historical filename uses "site saturation", but the implemented node-ID one-hot coefficients are penalized by `LogisticRegression(C=1.0)`. This is not an unpenalized saturated fixed-effect identification design. The supported claim is prediction beyond **that specified regularized node-ID reference**, not elimination of all persistent-site explanations or proof of within-node physiological decline.

The independent-new-draw formula `(1-p)^n` is an illustrative counterexample, not a fitted Tampa detection model. It cannot simply be applied to loss events with nominally revisited positive marks. Conversely, such revisits do not make detectability or protocol error disappear.

## 4. Ecological and monitoring interpretation

**The added prediction is not confined to events in which the previously occupied marks were omitted from the next survey. Nevertheless, the archive cannot identify whether non-detection at a revisited mark represents true shoot loss, physiological deterioration or an observation-process change.**

A practical implication proposed from this audit is to retain two separate fields alongside a transect non-detection: whether any former positive mark was revisited, and whether all former positive marks were revisited. The number of sampled points alone does not capture this distinction. This is a proposed observation-quality safeguard, not a demonstrated improvement in conservation outcomes.

The priorities remain to measure biological state and validate detection independently. No rhizome TNC, genet survival, reserve buffering, ecosystem-engineering function or management intervention was measured by this audit. Do not reinterpret this result as biological collapse, proof of a degradation cascade or a validated lead time.

## Scope of closure

The fixed-mark-overlap computation and its frozen-alert decomposition are complete within the archived-data scope. The endpoint definitions and predictive model were not changed. This result does not authorize more threshold/window/model tuning on the already-opened endpoint. PR #155 remains a draft; this report is not a merge or a complete manuscript/repository integrity certification.
