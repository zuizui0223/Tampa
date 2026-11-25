# Original burial experiment: current emergence versus residual viable seeds (2026-11-24)

## Original source and prior-work boundary
Jorgensen, Labouriau & Olesen (2019), DOI 10.1371/journal.pone.0215157 (open article and S1–S4 supplements). The original paper already established burial-depth effects on emergence/mortality and size effects on seed longevity and initial seedling biomass; the following is post-outcome accounting of matched source records, not a new discovery of those effects. Article methods: five outdoor tanks, 15 seeds per pot, 30 sorted-size pots (small/large × 2/4/6 cm), 70 unsorted pots (7 depths × two destructive harvest cohorts). S1–S4 archive artifact 14918042341 from run 45388872185, downloaded and verified ZIP SHA256 74f0c656295996b258907469cbbfd15a75df41744279d39a74947fbd74ad5374. S2–S4 individually hash-locked in analysis/157. S1 size measurements from separate samples, no individual mass-to-fate join.

## Source integrity audit
100 unique tank/pot records, 1070 valid repeated emergence observations plus 22 blank rows. Last emergence observation equals S3 reported emergence for all 100 pots; two time series (tank 1 pots 11,12) decrease, so do not reconstruct individual emergence event times. All four reported categories (emerged, viable, dead, unsuccessfully emerged) close to the reported total in all 100 pots, BUT total across 100 pots is 1451 rather than 1500 planted. 28 pots below 15 and 11 above 15. Never classify the discrepancies as deaths or surviving seeds, and do not normalize them away. Counts per planted seed are descriptive, not a closed probability vector. Report pooled ratios per reported total separately. For sorted pots, 26 totals are 15 and four are 14. The 24wk 0.1cm pots have totals 10/12/3/8/4, so the post-hoc extreme-depth comparison uses 1 vs 8 cm rather than the source's shallowest condition. It is not a frozen primary contrast.

## Actual original sorted-size experiment at ten weeks
Counts per condition of five pots, 75 seeds originally planted:
| depth | size | emerged | viable unemerged | unsuccessfully emerged | dead | reported total |
|---:|---|---:|---:|---:|---:|---:|
|2|small|31|18|13|11|73|
|2|large|40|22|2|11|75|
|4|small|37|15|14|9|75|
|4|large|26|33|8|8|75|
|6|small|15|18|29|12|74|
|6|large|22|29|15|8|74|

Pooled large minus small (225 planted per size): emergence +5, viable unemerged +33, unsuccessful -31, dead -5, reported total +2. In five tank blocks summed over depths, viable differences +6,+13,+4,+7,+3 (all positive); emergence differences +2,-3,-2,-3,+11 (2/5 positive). Arithmetic E+V differences +8,+10,+2,+4,+14; NOT all living individuals, future recruits, or a demographic rate. At 4cm, E decreases 11 but V increases 18; this contrast is descriptive, not a new statistically significant pairwise effect. Pooled ratios per reported total for viable: 51/222=22.97%, 84/224=37.50%. Equal-pot percentages may differ (as in original paper). No new inferential p-values.

## Unsorted separate harvest cohorts
At 24 weeks, five pots each at 1 and 8cm, both reported totals 75. 1cm: E45,V11,failed2,dead17. 8cm: E5,V22,failed10,dead38. E difference -40, V +11, failed +8, dead +21. E+V recorded category sum -29. All five within-tank differences negative for E and E+V, positive for dead, V positive 4/5 with one tie. At 8 weeks, 1 vs 8cm gives E40 vs2, V11 vs17, failed4 vs14, dead18 vs37 (reported totals 73 vs70), E+V decreases in 5/5 tank comparisons too. These are separate experimental pots, not longitudinal transitions; cannot infer future emergence or duration of dormancy. Deep burial is not pure temporal storage; more residual viable seeds can coexist with reduced recruitment and increased loss. Already consistent with original published mortality mechanism. No animal or genotype measured.

## Biomass completeness sensitivity (not primary)
486 unique biomass rows; 1 record (tank4 pot48 plant2) has harvest week 9 vs fate week8, excluded, no correction. After metadata gate 23/100 pots have biomass row count unequal to recorded emerged number. Some biomass components missing. Restrict sorted size contrasts to tank-depth pairs where both pots have matching emergence and biomass row counts, all above/below components present. 2cm: 4 tank pairs, mean large-minus-small recovered biomass per planted seed +0.0112833 g DW. 4cm: 3 pairs, +0.00223111g; 6cm: 3 pairs, +0.00746444g. Positive in 3/4,2/3,3/3 included pairs. This is post-outcome selected completeness sensitivity, not unbiased total production or a fitness estimate. Do not impute missing components or join individual weights.

## Interpretation and next gate
Treat immediate emergence, residual viable seed stock, mortality and recovered biomass separately. Potential bioturbation-related change in burial-depth distribution could alter the allocation of seed fates; no evidence here that otters actually cause such redistribution, that residual viable seeds later emerge, or that this changes paternal lineages. A next test must directly measure animal-induced depth redistribution and subsequent tagged seed fate, ideally genotype-linked. Do not combine the 2019 experiment and 2025 father weights as a calibrated survival model. Tampa Paper A and TNC unchanged. Local computation of script 157 succeeded; new independent CI not yet confirmed at writing.
