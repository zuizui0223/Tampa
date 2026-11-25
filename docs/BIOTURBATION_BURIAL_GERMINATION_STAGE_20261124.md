# Bioturbator effects on seed burial and germination: matched-tank stage audit (2026-11-24)

## Source and scope
Laukaityte et al. (2025), Oecologia, DOI 10.1007/s00442-025-05662-y. Public deposited data.txt at SimonaLaukaityte/heatwave-on-animal-plant-interactions commit ea4679016e8bddcd083cd93fe2fd6f33b6b1025e, git blob cb12f65a477078f3980a381b5251a635db312d53. Author R code at 14286c76bf40a5416060b32e29c9e57f9ec51bd2 explicitly selects records 81:240 (deposit runs 2 and 3). Source obtained and calculated using the GitHub connector, retaining those 160 cores. Five fauna treatments within each of 32 tanks, 16 tanks/temperature across two runs. Temperature treatment involves shared external water baths; no independent core-level heatwave interaction inference. Original study already found altered non-trophic interactions under warming; the following is a post-outcome matched-block accounting of different stage endpoints, not a claim of first discovery.

## Data audit
All depth counts sum to counted total and all depth-specific germination counts sum to germination total. 1529 counted seeds and 171 germinated among 160 cores nominally receiving 10 seeds each. 34 cores exceed ten counted seeds and 61 fall below ten. These discrepancies are not silently corrected; no individual seed loss, mortality or viability imputation. In 75 of 160 cores the deposited germinated_perc is different from germ_nb / seed_nb, so the new endpoints use the integer germination counts or expressly named counted-seed denominators, not that percentage. The original reported percentage may use a different denominator. This is an observation audit, not a refutation of the published analysis.

## Equal-core means for buried fraction, recorded germination counts
Temperature | fauna | mean buried fraction | summed counted seeds | germinated
COLD | NO | .330740 |144|15
COLD | COCKLE | .741892 |156|23
COLD | SHRIMP | .419934 |155|18
COLD | WORM | .421314 |152|21
COLD | MIX | .536836 |161|11
WARM | NO | .197301 |139|16
WARM | COCKLE | .784991 |160|24
WARM | SHRIMP | .424116 |158|12
WARM | WORM | .320739 |143|16
WARM | MIX | .701673 |161|15

Matched differences vs NO within same tank, four faunal contrasts by two temperatures by two endpoints (16 posthoc two-sided exact within-pair label swaps, 65536 sign configurations, Holm correction). Supported buried fraction contrasts: cold cockle +.411152 (Holm p=.0009765625), warm cockle +.587690 (Holm p=.011962890625), warm mix +.504372 (Holm p=.001373291015625). All eight germinated-count contrasts Holm p=1.0. Warm mix mean count difference -.0625/core. Cold mix +.206095 burial / -.25 germinated per core. Cold/warm cockle both +.5 germinated/core. This does not establish no germination effect or absence of a temperature interaction; no equivalence test, and no direct difference-in-differences test. The original publication analyzed germination conditional on burial position and used a different response/model. The present count endpoint is distinct.

Post-outcome sensitivity restricting pairs to both cores with counted totals <=10: cold cockle 11 pairs, burial +.363420 / germinated +.0909; warm cockle 10 pairs, +.613611 / +.100; warm mix 11 pairs, +.393182 / -.363636. No inference from this selected subset.

## Pooled counted-seed accounting
For treatment, recorded germinated / counted = p*u + (1-p)*w, with p fraction buried among counted seeds, u germinated per counted buried seed, w germinated per counted surface seed. The symmetric arithmetic decomposition is not causal mediation: position and germination assessed together at the end, individual paths unknown, and true original denominators unresolved. Cold mix vs no fauna: total difference -.035844, burial-composition component -.016270, location-conditional component -.019574; warm mix: total -.021940, components +.003248 / -.025188. Warm cockle: total +.034892, components +.002077 / +.032815. No newly inferred viable seed bank or later recruitment. No genetics or otter treatment in this experiment.

## Reproduction and limitations
analysis/158_bioturbation_burial_germination_stage_audit.py reproduces counts and exact tests from the pinned original Git blob. Numerical calculations executed in-session using actual source through GitHub; Python implementation added to Draft PR #170, not independently executed yet. Previous burial experiment workflow 45391102705 succeeded. Latest prior PR head d1e1eb87ba62ffe90b326e5d1bec6270aa4ea479 had 17/18 successful workflows; unrelated external clone/paternity workflow 45391101902 failed at missing external_reproductive/zostera_noltei_s004.xlsx after the acquisition step. It had passed earlier; this is an acquisition reproducibility blocker, not newly refuted ecology. Preserve fail-closed behavior. Tampa Paper A and TNC unchanged.

Next: directly compare experiments with predation protection, seed retention and emergence in the same randomized unit; do not pool burial, germination, emergence, seed mass, or plant fitness as interchangeable effects. Contrasting polychaete burial modes and lugworm exclusion interventions already established in prior literature. A novel cross-study question is how a measurable physical-engineering effect transmits (or fails to transmit) to successive recruitment stages across comparable designs; no meta-analysis of incomparable endpoints.
