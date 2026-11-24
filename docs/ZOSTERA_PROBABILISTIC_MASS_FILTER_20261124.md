# Soft mass-dependent representation sensitivity (2026-11-24)

## Scope and execution
This diagnostic replaces deterministic removal in analysis/154 with hypothetical independent Bernoulli retention. It uses the 844 and 693 seed records in Sgambelluri et al. 2025, Dryad 10.5061/dryad.6t1g1jx7p, verified source members with the same SHA256 values as analysis/153 and 154. Downloaded artifact 14916683079, SHA256 2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8. Executed locally in this turn with exact member checks and an exhaustive four-seed conditional-null test.

Jorgensen, Labouriau & Olesen 2019, DOI 10.1371/journal.pone.0215157, reported 20.0% vs 29.3% emergence at 6 cm for small vs large sorted seeds. The primary seed-size main effect was not significant and the interaction with depth was supported. Overall viable unemerged fractions 23.1% vs 37.2% are a different endpoint. Sorting was visual, and dry weights were measured on separate samples. The 2025 README describes weighing viable seeds before DNA extraction; no calibrated mapping of those mass values to the 2019 sorted classes. Both probability pairs are therefore illustrative settings only, not fitted or transferable demographic coefficients.

Within each site and scope (all or outcross only) assign probability p_i=.293 to the upper mass half including cutoff ties and .2 otherwise. Separately consider the viable-unemerged illustration .372/.231; do not multiply endpoints. Independence assumed, no density or shared mortality. For each sire g, let I_g be its sampled seed set. The statistic is the ratio of expected retained same-sire pairs to expected retained total pairs: sum_g sum_{i<j in I_g} p_i p_j / sum_{i<j} p_i p_j. This is not the expected realized ratio, effective population size, or observed descendants. Equal weights recover the original distinct-pair same-sire probability exactly.

Conditional reference randomly permutes probability labels within maternal shoot x reproductive branch x spathe x observed mating label. The denominator is invariant. Within a stratum of n with k_g sire-g records, multiply choose(k_g,2) by the average product of two distinct weights in the stratum. Across strata, multiply expected total weights of the same sire; exact expectation, no Monte Carlo p-value. This retains the architecture-associated allocation of probability weights.

## Locally computed 6 cm illustration
| cohort | scope | site | baseline C % | weighted C % | change vs baseline % | change vs conditional expectation % |
|---|---|---:|---:|---:|---:|---:|
| original | all |1|2.5784|2.2557|-12.516|-0.776|
| original | all |2|2.7675|2.5291|-8.612|-0.733|
| original | all |3|2.9397|2.5584|-12.972|-0.475|
| high locus | all |1|2.8718|2.6249|-8.596|+0.140|
| high locus | all |2|3.0502|2.7254|-10.647|-1.511|
| high locus | all |3|3.4293|2.9759|-13.222|-0.532|
| original | outcross only |1|2.3188|2.1161|-8.743|-0.434|
| original | outcross only |2|3.1106|2.8337|-8.901|-0.722|
| original | outcross only |3|2.3643|2.2457|-5.018|-1.621|
| high locus | outcross only |1|2.6142|2.4749|-5.329|-0.929|
| high locus | outcross only |2|3.2952|2.9562|-10.286|-1.273|
| high locus | outcross only |3|2.8112|2.5009|-11.038|-2.182|

All cells decline relative to baseline, but the conditional contrast is -2.182% to +0.140%. The separate viable-unemerged illustration gives baseline changes -6.098% to -16.001% and conditional changes -2.601% to +0.208%. These are overlapping cohort versions and three sites, not independent replication. Architecture-conditioned reference accounts for most of the numerical change. Cannot establish a sire-specific genetic selection mechanism, actual survival, or transferability. No p-values.

## Next empirical gate and status
Run analysis/156_zostera_probabilistic_mass_filter.py with --root pointing to original seed_mass member directory. Local computation and synthetic test passed; independent CI not added for this small diagnostic because current source/analysis runs are queued. Prior burial workbook acquisition run 45388872185 remained queued with no artifacts at last check. Direct local PLOS and Figshare access failed DNS. No claim of new original-data analysis of the 2019 experiment. Prioritize its real pot-level emergence, viable-unemerged, and biomass outcomes, with distinct harvest cohorts and no forced joins. In particular deep burial may reduce recruit numbers while increasing size among survivors or residual viable seed stock: test per-planted-seed outcomes using matched harvest denominators, not product of published marginal means. No paper submission, merge, Tampa Paper A or TNC changes.
