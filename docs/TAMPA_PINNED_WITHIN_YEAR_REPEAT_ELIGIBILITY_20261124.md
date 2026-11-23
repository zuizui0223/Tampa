# Tampa same-year repeat-survey feasibility: original pinned Event metadata audit (2026-11-24)

## Scientific question

Does the 1997–2025 *Tampa Bay* monitoring archive actually contain enough repeated surveys at the same sampled meter marks within one year to calibrate a mark-level imperfect-detection model, independently of annual changes in true species occupancy?

**Source-locked protocol:** Use only `dwc/event.csv` from tbep-tech/obis-example at commit `6c567beff95ea04f0e397101befb49d5233ace8f`, verifying raw byte size **24,654,717** and Git blob SHA1 `583b4d4e328290ab065346579eb4f29f03ea0f99`. Neither `Occurrence` nor `eMoF` is downloaded. No Thalassia presence, shoot state, Braun-Blanquet or event outcomes are examined or fitted.

## Fixed archival frame

Prior source reconstruction shows **1,497 eligible Transect visits**, **1,480 unique node-years** and **71 stable nodes**, where a visit is eligible if its Transect parent has at least three Point child event rows.

From this alone, the difference `1497 - 1480 = 17` places a structural *upper bound* of **17 extra eligible parent visit records** beyond one per stable node-year in the entire 29-year archive. It does not prove these 17 were independent, on separate field dates, or repeated at identical Point IDs.

## Audit gates, without opening any biological response

1. Verify exact Event byte length / Git blob and complete expected header; hard stop on drift.
2. Reconstruct the original >=3 child-Point eligibility. Confirm 1,497 visits, 1,480 node-years, 71 nodes and exactly 17 extra visits; hard stop if not.
3. For every node-year with >=2 eligible parent events, inventory unique parent dates, sampling protocols, institution codes, and associated child-Point `locationID` mark rosters.
4. Record overlapping Point IDs in repeated parent visit pairs. Classify same date separately from distinct dates. Tabulate pairs of distinct dates with shared mark IDs and their separation, with descriptive 7/14/30-day windows (not biological closure criteria).
5. Record number of marks repeated on distinct parent dates. **Never** interpret overlapping `locationID` as verified same photographic microquadrat; the same IDs can be visited with different effective footprints.
6. Every output remains `valid_independent_detection_replicates_verified=false`. The source's eventDate may contain administrative/default date conventions, notably the independently documented 2016 protocol issue.

These are **maximum historical metadata eligibility bounds**, not detection probabilities. Visit count is not the number of statistically independent repeated observations, parent event date is not necessarily field time, and same-day duplicated parent visits may be technical or administrative duplicates rather than independent surveys.

## Consequences for research

- If no groups have distinct-date overlap at sampled Point IDs, the available historical source lacks even the nominal temporal repeat structure needed for within-year detection calibration under this exact fixed-transect frame.
- If some groups do, they are *candidates* for manual inspection of field notebooks, original footprint, observer, date provenance, and a biologically reasonable occupancy-closure window. Only then might some independent detection histories be constructed.
- In either case, the 29-year annual table does not by itself prove the retrospective 1,0,1 -> 0 observation association is biological hysteresis; a new detection and direct ecological-state measurement layer remains required for mechanism inference.
- Do not promote a candidate metadata repeat to a calibrated 2026 probability of detection or rely on a selected new lag/condition model from the already-opened outcome series.

## Reproduction

- `analysis/113_pinned_event_within_year_repeat_eligibility.py` (Python standard library only).
- `validation/test_pinned_event_within_year_repeat_eligibility.py` (six synthetic fail-closed tests).
- `.github/workflows/tampa-within-year-repeat-eligibility.yml`: checks source identity, prints the full source-only group ledger and uploads machine-readable JSON.

**Separate programme:** Prospective four-bay TNC-v2 sampling (41 historical candidate nodes; >=36 analyzable, >=6 per bay) is protected and not altered by this archival audit. Sampling still requires independent field permissions/method pilots. This work does not create a real field observation or ecological mechanism result.

## Verified original Event result — 2026-11-24

The full source-only Python workflow **PASSED** against the pinned original Event bytes on [GitHub Actions run #45246024947](https://github.com/zuizui0223/Tampa/actions/runs/45246024947), with 6/6 synthetic tests passing. The original Event SHA256 is `45c5fec414cb9c63a2a63fbd4f8dcd823ae05239dee598d5dd53dbcb34359b62`. CI artifact #14854212197 has ZIP SHA256 `1de47c0d84c731c41f9b16c43f1cc751d40cd8ca85dea0ea8cb63af435af7747`.

Canonical numerical report: `results/pinned_within_year_repeat_eligibility_verified_20261124.json`.

| Reconstructed metric | Measured in original Event metadata |
| --- | ---: |
| Eligible fixed-transect visits / unique node-years / stable nodes | **1,497 / 1,480 / 71** |
| Node-year groups with two eligible visits | **17** |
| Groups with distinct parent Event dates | **17/17** |
| Groups sharing at least one Point locationID across different dates | **17/17** |
| Sum of overlapping mark IDs across the 17 groups | **222** |
| Different-date shared-mark survey pairs within 7 days | **0** |
| Within 14 days | **0** |
| Within 30 days | **0** |
| Smallest / median / largest nominal between-visit day gap | **80 / 271 / 334 days** |

The 17 groups occur across 1999, 2007, 2009, 2010, 2011, 2012, 2016, 2021, and 2024. The 2016 pairs are dated January 26 to December 25 (334 days), the latter being an already documented candidate for an administrative date convention. The shortest nominal 80-day pair is S3T13 in 2024 (September 16 to December 5), and it shares only **2 Point locationIDs**. The full 17-group ledger and date/mark overlaps are retained in the canonical JSON, not simply aggregated by year.

**Interpretation:** The archive has *some* source-labeled distinct-date mark revisits, so it would be inaccurate to assert no same-year repeats anywhere. However, **none occurs within even 30 nominal days**; all are separated by 80–334 days and are not automatically observations under ecological closure. There is also no evidence in this metadata alone of independently repeated detection, identical microquadrat footprint, or stable true occupancy over those gaps. It does not supply a defensible historical mark-specific detection calibration.

The relevant inference boundary is therefore now source-backed: a new independent short-interval detection measurement layer is necessary if a future paper wants to distinguish the observed re-recording fragility pattern from mark-specific observation heterogeneity. Do not label the calculated 222 mark overlaps as independent detectability replicates or assign true survival/recovery status to any 0→1 sequences.

## Status

Source-verified quantitative metadata result complete, pinned to an exact CI success and archival JSON. No Occurrence/eMoF or ecological mechanism outcome was opened.
