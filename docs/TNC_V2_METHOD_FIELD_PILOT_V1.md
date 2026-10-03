# Tampa TNC-v2 response-independent method / field pilot v1

## Purpose

Resolve the remaining **method-dependent** fields in `field/tnc_v2_precollection_freeze.json` before the first outcome-bearing core.

This pilot is not an ecological test. It may inspect analytical measurements needed to validate the method, but it must not use future meadow response, final-node future trajectories, or any association between pilot TNC and ecological state to choose a protocol.

The pilot resolves:

- horizontal rhizome tissue class;
- minimum perpendicular offset from the permanent transect;
- core diameter;
- core depth;
- maximum collection-to-preservation time;
- preservation method.

Campaign dates and final node/calendar manifests remain logistical freezes outside this pilot.

## Literature basis

The primary assay remains HPLC because published seagrass method comparisons show strong protocol dependence and substantially better analytical precision for HPLC than common colorimetric assays.

- Sørensen et al. 2018, *Aquatic Botany* 151:71–79, DOI 10.1016/j.aquabot.2018.08.006.
- The standardized paper reported HPLC estimates within about 1.1% of expected standard-mix carbohydrate levels and showed that extraction and starch-processing choices materially change NSC estimates.
- A published *Thalassia testudinum* HPLC dataset reports approximately 10% relative reproducibility for its TNC workflow (BCO-DMO dataset 917954).

The acceptance values below are **method QC tolerances**, not biological thresholds.

## Pilot material boundary

Use non-outcome-bearing *Thalassia* material:

- dedicated pilot material outside permanent outcome-bearing core footprints; or
- surplus material explicitly collected for method development before final-node sampling.

Do not select pilot samples by known future response.

Target at least:

- 8 independent rhizome specimens for analytical matrix/preservation work;
- 10 field pilot core attempts for geometry/tissue-recovery work;
- material from at least 2 collection locations or collection batches when feasible.

The pilot sample count is a method-feasibility target, not inferential ecological replication.

## A. HPLC matrix acceptance

Use the same candidate extraction, hydrolysis, chromatographic and dry-mass workflow that would become the primary method.

Required checks:

1. calibration / standard identity is unambiguous for the primary soluble-NSC analytes and starch-derived glucose;
2. analytical blank is below the laboratory LOQ;
3. a blank following the high standard shows no material carryover above LOQ;
4. mean recovery of a known analytical standard mixture is 95–105%;
5. pooled-*Thalassia* matrix spike recovery is 85–115%;
6. median technical-duplicate CV for TNC is <=10%;
7. no more than 10% of technical-duplicate pairs have CV >15%;
8. >=90% of pilot extracts place the required primary analytes inside the frozen calibration range without post-hoc dilution rules.

If these fail, laboratory optimization is allowed **within the response-independent pilot**. Once all criteria pass, freeze the final extraction/HPLC workflow before outcome-bearing material is processed.

Do not choose among passing methods by whichever gives the strongest ecological contrast or the largest TNC variance.

## B. Horizontal-rhizome tissue-class pilot

The primary tissue remains **live horizontal rhizome**.

Candidate ontogenetic/segment definitions must be written down before comparison. Each candidate must be objectively identifiable in the field/lab.

Selection hierarchy:

1. >=90% unambiguous classification success among pilot specimens;
2. >=90% of specimens yield sufficient dry material for the full soluble-NSC + starch assay plus one repeat/QC aliquot;
3. tissue can be collected under the frozen destructive-sampling guardrail;
4. if multiple classes pass, choose the class requiring the least destructive footprint;
5. if still tied, choose the first candidate in the predeclared candidate order.

**Do not select tissue class by mean TNC, TNC variance, or association with ecological state.**

Record the selected class verbatim in `horizontal_rhizome_tissue_class`.

## C. Core geometry pilot

Before the field pilot, list feasible candidate core diameter/depth combinations based on permit, boat/field handling and likely rhizome depth.

Test candidates from least to most destructive.

A geometry passes when:

- >=9 of 10 pilot core attempts recover identifiable live horizontal-rhizome tissue of the frozen candidate class;
- >=9 of 10 yield the HPLC-required dry mass;
- the core can be extracted and restored without encroaching on the permanent monitoring footprint;
- three non-overlapping q25/q50/q75 anchor cores remain physically feasible under the existing spatial design.

Choose the **least destructive passing geometry**.

Do not enlarge the core because a larger geometry produces higher TNC or lower variance.

Freeze the selected diameter and depth before outcome-bearing coring.

## D. Permanent-transect offset pilot

The offset protects the future response unit from the measurement intervention.

Before outcome-bearing sampling:

1. obtain the monitoring authority's no-disturbance / access boundary;
2. combine that boundary with the selected core radius and safe restoration workspace;
3. test placement at representative q25/q50/q75 anchors;
4. choose one minimum perpendicular offset that can be applied reproducibly across the planned network.

The selected minimum must be based on physical protection, permit constraints and placement feasibility only.

Do not choose an offset from ecological response or TNC values.

## E. Preservation method and latency pilot

Field metabolism can continue after collection, so preservation timing must be frozen.

Predeclare candidate field-preservation methods based on actual logistics. At minimum, compare the proposed method against an immediate-preservation reference using split aliquots from the same rhizome specimen.

For each candidate maximum delay:

- use paired aliquots from at least 6 independent pilot specimens;
- process delayed and immediate aliquots through the same final HPLC workflow.

A candidate delay passes when:

- median absolute relative TNC difference from immediate preservation is <=10%;
- 90th percentile absolute relative difference is <=15%;
- no monotonic directional drift is evident across the tested delay sequence;
- all samples remain physically suitable for the frozen HPLC workflow.

Select the **shortest operationally feasible preservation method** and the **longest tested delay that passes** as the maximum allowed collection-to-preservation time.

Do not widen the maximum delay during the outcome-bearing campaign.

## F. Frozen batch randomization

Already resolved:

> blinded core IDs are assigned to HPLC batches using reproducible blocked randomization spanning available water bodies and campaign dates; each node's three cores are distributed across at least two batches when capacity permits; the same calibration/QC scheme is used in every batch.

The batch manifest must be frozen before primary carbohydrate values are opened.

## Pilot completion rule

The method pilot is complete only when all six selected outputs are non-null:

- horizontal rhizome tissue class;
- minimum perpendicular transect offset;
- core diameter;
- core depth;
- preservation method;
- maximum collection-to-preservation minutes.

The validator must also record passing analytical QC.

Only then may those values be copied into the authoritative TNC-v2 precollection freeze.

## Claim boundary

Passing this pilot means the method is reproducible enough and physically bounded enough for the prospective study.

It does **not** mean:

- the selected tissue class is biologically superior;
- the selected TNC method is the only valid seagrass carbohydrate method;
- higher TNC is healthier;
- the future ecological mechanism is supported.
