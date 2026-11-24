# Reproductive duration and ovule-count diagnostics (2026-11-25)

## Provenance
Original artifact 14925937983 from run 45408641314, ZIP SHA256 5f0bdb9f65d277e3e0e52fd4d680893090bfb91a51ff9e742f750992c1b18117 verified locally. Eight input member SHA256 checks in analysis/171. Executed the Python script on the original bytes, not simulated outcomes. This step uses two new source systems, but does not validate the previous functional-visitor-weight model across regions. Prior head e71e1b3351e502d28f663ba846cc99e17367e1cd returned mostly queued/in-progress CI; the specific 170 workflow was not in the first page, hence not independently verified here.

## Penstemon digitalis
Dieringer & Cabrera R. 2026, Nordic Journal of Botany, DOI 10.1002/njb.04977; Dryad 10.5061/dryad.xpnvx0kwt. Original study reports cumulative pollen acquisition but no significant mean seed-count gain with prolonged exposure, and proposes insurance against variable visitation. New diagnostic compares distributions, zero-record fractions, and equal-year contrasts, not a novel discovery of prolonged receptivity or proof of insurance.

2015 microscopy: 20 independent flowers per day; same within-day sample keys align across three raw first sheets. Days are different flower/plant samples; IDs 1–20 recycled. Positive pollen/top/base counts D1 6/0/0, D2 17/14/0, D3 20/20/20. All 60 joined spatial count rows nested numerically, but these are snapshots, not tracked grains. One discrepancy in 2015 pollen across workbooks: D2 ID6 =245 in stigma microscopy sheet, 145 in year-comparison sheet. Retain each experiment's deposited records without replacing. Hidden XLSTAT sheets contain values inconsistent with raw counts (base D2 summary 5.95 vs raw all zero); do not use hidden summaries. Single-visit pollen deposition 80 flowers (Anthophora n24 mean4.917 median2 zero5; Bombus n32 mean12.969 median3.5 zero5; Ceratina n14 mean7.571 median1.5 zero3; Hoplitis n10 mean3.7 median2 zero4). Taxon means already reported; no new between-taxon significance claim. Original paper states the sampled stigmas were excised, possibly interrupting fertilization; thus no per-taxon seed-effect weights or single-visit fertility conclusion.

Pollen accumulation dataset: 130 records, 2015/2018/2020. Seed dataset: 129 records, 2017/2018/2020. For seed cohort D2 means natural exposure until day2 then bagged, D3 means open through day3; seeds measured later. Different flower cohorts and plant IDs reused; do not join pollen to seed or match across days. README defines Seeds as seeds per fruit while article defines seeds per flower. Retain recorded counts and zero-record fraction without interpreting as exact fruit-set or whole-plant reproductive failure. Separate outcomes and years, no causal individual mediation or actual trajectory.

|Endpoint/year selection|D2 mean|D3 mean|D2 zero fraction|D3 zero fraction|difference of means (conditional bootstrap 95%)|zero fraction difference (conditional bootstrap 95%)|
|---|---:|---:|---:|---:|---|---|
|pollen all 3 years|93.7833|176.5300|.116667|.026667|82.7467 (52.6363,111.9542)|-.0900 (-.1733,-.0100)|
|seed all 3 years|86.0000|88.2467|.125000|.150000|2.2467 (-16.4482,20.8294)|.0250 (-.0928,.1450)|
|pollen shared 2018/20|86.4250|136.4450|.1000|.0400|50.0200 (20.1500,78.7362)|-.0600 (-.1600,.0400)|
|seed shared 2018/20|79.9250|79.4200|.0875|.1750|-.5050 (-21.6895,20.2093)|.0875 (-.0492,.2283)|

Within-year seed count differences D3−D2: +7.75 (2017), +9.30 (2018), −10.31 (2020); zero-fraction differences −.10,+.10,+.075. The pooled descriptive comparison therefore does not show a reduction in zero seed records. This does not establish absence of insurance under other visitation regimes. Bootstrap 10000 draws seed20261125, resample observations independently within year/day, equal-year weight, conditional on observed years and source independent-flower description; not across-year inference or confirmatory multiplicity-adjusted test. Additional arithmetic decompositions and empirical rank comparisons in script output. Breeding workbook raw totals A 0/21, O359/422, S21/32, X20/36; article S21/30,X20/32. Duplicate Plant ID27/X records; no assumption which is erroneous, no new breeding-system hypothesis test.

## Clarkia pollen supplementation
James & Geber 2025, Ecological Monographs DOI 10.1002/ecm.1649, Dryad 10.5061/dryad.k3j9kd56r. Original paper already estimates pollinator-mediated versus independent effects and finds forb/grass competition across reproductive components. Here distinguish filled-ovule fraction from realized count of filled seeds, using observed paired treatment records rather than total fecundity models.

430 rows: 255 control and 175 supplemental; unique plot/focal-species/treatment. 175 matched plot-by-focal-species contexts, with identical block/background species/background biomass/grass/forb/flower-number metadata. README describes two treatment fruits per focal plant, but no explicit focal individual ID; label candidate paired records, not independently confirmed individual pairing. 156 pairs with both seed and ovule counts observed, and averaged ovule field matches across all complete pairs. 14 contain at least one assigned ovule count; primary 142 directly counted pairs, 37 blocks. No missing fruit or zero ovule imputation, no assumptions about dropped fruits. May be selected by observation or survival.

|Focal species|pairs|mean filled fraction difference (supplement minus control)|mean filled-seed count difference|
|---|---:|---:|---:|
|C. cylindrica|33|.141574|15.1212|
|C. speciosa|31|-.053297|-.9355|
|C. unguiculata|47|.267030|17.6383|
|C. xantiana|31|.112164|5.8387|
|All|142|.134135|10.4225|

Overall cluster percentile bootstrap 95% intervals .089813–.176014 and 7.87498–12.76822, 10000 draws of whole blocks stratified by background species (9/9/9/10 blocks, seed20261125). Conditional on observed study and complete-record subset; not the original model or causal estimate of general population response. Equal-block mean effects .113224 and 8.726716. In 17/142 pairs signs of fraction and count differences disagree (7 higher fraction but fewer filled seeds, 10 converse). Complete 156 pairs give .141050 and 10.615385; same 17 opposite. Primary zero counts 10 control,5 supplemental; no inference on missing fruits.

Exact symmetric arithmetic decomposition at each pair: seeds = ovules × filled fraction. Count difference = mean ovules × fraction difference + mean fraction × ovule difference. Mean terms +8.33208 and +2.09046 sum to +10.42254; they are not causal contributions. Positive average ovule difference may reflect different flowers or selection; pollen supplementation does not imply it increased preexisting ovule number. No total individual seed production, no resource limitation fitted from this identity.

## Synthesis and status
A longer receptive period can improve measured pollen acquisition without clear improvement in mean or zero frequency of seeds, whereas supplemental pollen in the Clarkia complete-pair subset has a positive average count contrast. Different treatments and metrics cannot be pooled as a transmission coefficient. Distinguish availability, realized pollen delivery, time/compatibility of tube growth, available ovules and seed filling. These datasets do not have matched pollinator identity/behavior and seed fate for each visitor, so the previous cross-region functional weight question is still unresolved. No new otter raw data. Local exact-source run passed; independent 171 CI not yet checked. Draft PR #170, no merge/submission or changes to Paper A/frozen TNC.
