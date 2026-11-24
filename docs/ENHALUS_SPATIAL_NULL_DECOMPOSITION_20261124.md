# Enhalus genetic neighbourhood: exact random-label decomposition (2026-11-24)

## Provenance and scope
Post-outcome diagnostic following analysis/141. Prior independent Actions run 45375509055 passed, downloaded artifact 14910454999 SHA256 319f74067ffacd72a7b3155bc0aa696d9d688fc931361fb082869d5441b97e0d. Original workbook from source-member artifact 14911175880 SHA256 b5b116221241e9e603896a9dc99f66287f4707a313c12bf83ff7dd00487dc1f2; workbook SHA256 10e1465ac9255ad2d873d6142386b5140320740ebc660196b4a9eb0e2251c959. Yu et al. 2019 DOI 10.1002/ece3.5106, Dryad 10.5061/dryad.sn1h87s. A fragmented/polluted and B continuous, one plot each. Exact unphased MLGs 214/255, sampled ramets 271/395.

## Estimand
For a focal point with m observed neighbouring ramets, let U be the number of distinct other exact MLGs. Under uniform random relabeling of the same N coordinates with the same clone-size roster k_g, the exact expected U is sum_g (1-k_g/N)[1-C(N-1-k_g,m)/C(N-1,m)] with impossible combinations assigned zero. Average over focal degrees. Validated by exhaustive enumeration in a synthetic four-ramet example and singleton/one-clone limits. This is a deliberately nonbiological random-label reference, not demographic disturbance or causal intervention.

For each plot: mean U = mean degree D - [D-E_null U] - [E_null U-U]. First bracket is redundancy expected from global clone sizes at the observed degree distribution; second is additional spatial-arrangement deficit relative to that reference. Neither is a causal independent effect. Both depend on scale/degree; no between-plot randomization. At four cumulative radii:

| radius m | A observed U | A null E U | A spatial deficit fraction | B observed U | B null E U | B spatial deficit fraction |
|---:|---:|---:|---:|---:|---:|---:|
|1|2.129151|2.537645|.160974|2.764557|3.530173|.216878|
|2|5.900369|6.973808|.153924|7.410127|9.973182|.256995|
|4|20.856089|25.025720|.166614|24.620253|33.551373|.266192|
|8|68.955720|79.704880|.134862|78.103797|96.610264|.191558|

B minus A identity:

| radius m | degree advantage B-A | excess global-composition redundancy B-A | excess spatial deficit B-A | actual U advantage B-A | share of degree advantage offset by total redundancy difference |
|---:|---:|---:|---:|---:|---:|
|1|1.023495|.030966|.357123|.635406|.379180|
|2|3.217208|.217833|1.489617|1.509758|.530724|
|4|10.751497|2.225844|4.761488|3.764165|.649894|
|8|32.416927|15.511543|7.757307|9.148078|.717799|

At 1 and 2 m, spatial deficit accounts for 92.0% and 87.2% of the *difference in total redundancy*, falling to 33.3% at 8m. This is not a partition of causal variance. Despite greater B absolute and proportional deficit in U, same-MLG pair enrichment relative to its own clone-composition baseline is greater in A at 1m (92.36 vs 37.39), so do not generalize as uniformly stronger standardized spatial clustering in B.

Within-plot same-MLG undirected edge counts vs random-label expectation at 1m: A 54 vs .584666; B 126 vs 3.370301. At 2m: A 60 vs 1.613339; B 236 vs 9.671092. All four radii in both plots exceed all 4,999 random relabelings (one-sided unadjusted Monte Carlo p=.0002 each). These are within-plot tests of label exchangeability, not replicated tests of disturbance or eight independent ecological outcomes. Clonal spatial autocorrelation is already known and was studied in the original paper; novelty of this neighbourhood accounting is not established.

## Ecological interpretation
Absolute distinct-genet availability is jointly shaped by local ramet count, clone-size roster and arrangement. Continuous meadow retains more neighbouring MLGs in observed absolute terms, but its excess redundancy offsets 38–72% of its ramet-neighbour advantage. Spatially concentrated clonality can reduce encounter opportunities even without changing plot-scale richness. Different MLGs are not proven flowering opposite-sex donors. In dioecious Enhalus, sex, flower phenology and floating pollen transport need independent measurements. No general causal claim about disturbance or reproduction.

## Reproducibility
Actual calculations executed locally using the verified original workbook; synthetic exact-enumeration checks passed. Code analysis/142_enhalus_spatial_null_decomposition.py. Dedicated independent CI with tolerance-based checks against the locally derived observed and null values added separately; not yet independently run when this note was written. No prior Tampa paper, TNC or frozen results changed.
