# Contemporary TNC anchor crosswalk — response-blind candidate gate v1

## Research purpose

The Tampa paper-level decisive prospective test is a *within-transect* contrast:

```text
future_BB_anchor ~ baseline_BB_anchor
                 + within_node_centered_anchor_TNC + node_fixed_effect
```

The sample frame is frozen as **four bays**, requiring **at least 36 complete q25/q50/q75 triplets** and **at least six in each bay**. This can only be interpreted if each TNC tissue sample is matched to a reproducible, unique fixed metre mark that also has **current** quantitative Braun–Blanquet (BB) and a **future same-mark** BB value.

The existing authoritative `analysis/70_freeze_tnc_v2_execution_manifest.py` validates node/bay status and baseline/TNC dates but does **not** identify the three local metre marks or their current quantitative BB. The archived 2023–2025 crosswalk in [PR #159](https://github.com/zuizui0223/Tampa/pull/159) supplies a reconnaissance reference, **not present-day eligibility**. Its 38 historic complete triplets and 114 historic marks must never be silently treated as contemporary q25/q50/q75 choices.

## Response-independent inputs

**Node/date manifest** uses the existing `field/tnc_v2_execution_manifest_template.csv` exact columns:

```csv
node_id,water_body,thalassia_positive,tnc_date,baseline_survey_date
```

**Current full sampled-point census** uses the new, initially empty `field/tnc_current_point_roster_template.csv` exact columns:

```csv
node_id,water_body,baseline_survey_date,point_location_id,site_m,thalassia_present,baseline_bb_anchor
```

- Each row is one **actually sampled contemporaneous fixed metre mark**; provide the full original baseline sampled-point roster, not only hand-picked promising TNC marks.
- `point_location_id` is the monitoring authority's actual stable mark ID, never a generated guess.
- `site_m` is the measured numeric fixed transect position in metres; multiple marks in one node may not share the same site position or official ID.
- `thalassia_present` must reflect actual contemporary observed presence, not the 2023–2025 historical preflight or a predicted occurrence.
- `baseline_bb_anchor` is the contemporaneous **numeric** focal BB at that sampled mark. Focal-positive selected marks need numeric BB greater than zero and at most five. Focal-present nonnumeric text such as `Reported` is **not** silently recoded to any quantitative value.
- Both files must be prepared independently of TNC assays and **before** any future meadow response is inspected. Extra/future outcome columns are rejected.
- No retrospective history and no HPLC values are used in the candidate-selection algorithm.

## Original anchor rule reproduced, not retuned

Within each node marked currently positive, sort **all current focal-positive sampled metre marks**, use the same linear-interpolation quartile targets `[0.25, 0.50, 0.75]`, then choose the nearest still-unused site; a site-position tie takes the lower metre mark. The original historical preflight `analysis/62_tnc_anchor_bb_four_bay_preflight.py` uses the identical **nearest-unique** logic.

Crucially, if the chosen mark lacks valid numeric BB, **the entire node is excluded** from complete-triplet candidacy. The script must not choose the next available mark to rescue sample size. If fewer than three current positive marks exist, no three-anchor node is created.

The validator also rejects unknown/duplicated locations, discrepancies between node and point-level focal presence, mismatched survey dates and violations of the **original <=28-day campaign / +/-14-day TNC-to-baseline alignment** rules. It does not create/relax any new ecological or sampling threshold.

## Run and inspect

After the monitoring authority provides complete **real** contemporaneous baseline records (the source templates stay blank in Git), make local copies, then run:

```bash
python analysis/70_freeze_tnc_v2_execution_manifest.py \
  --manifest field/tnc_v2_execution_manifest_current.csv \
  --out results/generated_tnc/tnc_v2_node_date_candidate.json

python analysis/84_tnc_current_anchor_candidate.py \
  --nodes field/tnc_v2_execution_manifest_current.csv \
  --points field/tnc_current_point_roster.csv \
  --out results/generated_tnc/tnc_current_anchor_candidate.json \
  --candidate-csv results/generated_tnc/tnc_current_anchor_candidate.csv
```

The script classifies **only** candidate mark geometry:
- `PASS_ANCHOR_CANDIDATE_GEOMETRY_ONLY`: at least 36 complete nodes, at least six in each bay, unique marks and numeric current BB; **NOT sampling authorization**.
- `STOP_COMPLETE_TRIPLET_GATE`: below the frozen complete-triplet gate; do not promote an encouraging supportive network-scale TNC result into the decisive primary.
- malformed/inconsistent input: fail closed rather than guessing the source location, date or observation.

The exported CSV labels each location `sampling_authority_status=NOT_AUTHORIZED`, regardless of candidate status. It is a **candidate survey-linked index** only. It does not mutate `field/tnc_v2_precollection_freeze.json`, `field/integrated_campaign_resource_freeze.json`, any model/code hash, or a final author-approved anchor set.

## Biological scope of the selected anchor cohort

The frozen within-node TNC question is **conditional on current, established focal occupancy sufficient to locate three distinct *Thalassia*-positive marks**. The archival preflight found 38 three-mark nodes among 41 recently positive nodes; three sparse historical nodes had only one or two focal-positive marks. This is a real denominator limitation for interpretation, **not an invitation to relax or reselect the 36-node/6-per-bay design**.

A future supported within-node TNC coefficient would mean measured reserve state helps forecast **divergence among already-occupied local patches with complete matched quantitative records**, after the specified baseline BB and node identity controls. It would not by itself establish a buffer against whole-meadow extinction, explain recovery of near-empty sites, or generalize to nodes unable to supply three current positive anchors. Conversely, a null within that restricted frame would not rule out a different reserve role at severely sparse or newly recolonizing locations.

The selected cohort's current composition and the excluded sparse-node registry should be reported alongside the eventual point estimate rather than hidden. Historical selection eligibility is *not* contemporary eligibility.

## Non-negotiable downstream checks

Before first outcome-bearing TNC collection, the separate monitoring and permit authority must verify the actual fixed locationID and core separation/no-disturbance geometry; the prospective method pilot must pass its frozen tissue/recovery/HPLC/preservation gates; resources and laboratory capacity must be frozen; every actual TNC sample/core ID must be bound to its **approved q25/q50/q75 mark**, and the original quantitative baseline must be preserved.

This additional script **cannot** infer whether a field crew will place its sampling core in exactly the right microhabitat, whether future sampling will revisit the exact location, or whether a high TNC value represents resistance rather than current unmeasured condition. Those uncertainties remain part of the scientific interpretation.

## Tests and provenance

`validation/test_tnc_current_anchor_candidate.py` constructs a wholly synthetic four-bay baseline with 41 positive nodes, 38 three-mark candidates (8/10/12/8 by bay), and confirms the 114 selected q25/q50/q75 records. It tests denial of rescue after a selected BB becomes nonnumeric, duplicate official IDs, an unregistered node, extra future-response columns, contradictory focal presence, and date mismatches.

The workflow `.github/workflows/tnc-current-anchor-crosswalk.yml` runs both this new test and the original node/date manifest test. **No current Tampa TNC field sampling or future responses are available in this repository**, and a successful synthetic test must never be described as field readiness.
