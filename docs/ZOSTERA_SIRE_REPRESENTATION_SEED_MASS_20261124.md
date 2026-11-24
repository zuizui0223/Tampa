# Zostera: observed sire representation and viable seed mass, 2026-11-24

## Data and boundary

Sgambelluri et al. 2024, Dryad 10.5061/dryad.dfn2z358x, deposited sire and spathe CSV files. These are existing COLONY inferences, not new parentage fits. High-locus sire table: 180 sire records, 688 contributions; totals close with spathe table in each site (171,287,230). At sites 1 and 2, source-labeled outcross sire contributions are one less than spathe outcross seed counts, and self-labeled contributions one more. Thus strategy restriction is by source sire label, not reconstructed seed-level identity. Original sire table 208 records / 852 contributions versus slim spathe total 844, with 8 extra in site 2. Do not reconcile silently or combine cohorts.

The observed inverse Simpson effective number of sires (Hill2) is (sum n_i)^2 / sum(n_i^2). This is not population-genetic effective size. At fixed observed sample N and number of sires G, the mathematical maximum occurs when positive integer contributions are as even as possible. The same-sire probability for two distinct sampled seeds is sum n_i(n_i-1)/[N(N-1)]. These are finite-pool arithmetic diagnostics, not a random mating model.

| high-locus site | sire records | seed contributions | Hill2 | Hill2/max | same-sire probability/min | share of upper ceil(20% G) sires |
|---|---:|---:|---:|---:|---:|---:|
|1|51|171|24.186104|.483871|2.507246|.561404|
|2|68|287|32.518358|.482827|2.399573|.567944|
|3|61|230|24.133212|.400547|3.027778|.617391|

Outcross-labeled sire records only: G=46/63/57, Hill2=25.124183/30.453838/26.842315, Hill2/max=.562092/.490545/.477046. Original cohort gives similar descriptive ratios but has count discrepancies. No across-site inference from only three sites. Original study already studied paternity skew; new arithmetic distinguishes richness and observed representation.

## Seed mass dataset successfully acquired

Sgambelluri et al. 2025, DOI 10.1093/evolut/qpaf111, Dryad 10.5061/dryad.6t1g1jx7p. Source inventory run 45386116309, artifact 14916683079, verified ZIP SHA256 2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8. README specifies viable seeds measured in mg; no nonviable seed genetic data. Original Seed_mass.csv SHA256 460a7ec2e3388863a10d547b758d2f70e7199430d2f16ba564f9005c3a7ff06d: 844 unique seed keys, 35 mothers, 221 site-specific inferred sires. Reduced CSV SHA256 3844e2767ccbbaf228e679063c9eb35e15fdb8c80ba6308abe2235ec09d6e79e: 693 unique seeds, 34 mothers,192 sires. Deposited reduced table has 693 rows; published text refers to a 688-seed subset. Use source table as deposited and label discrepancy. 690 shared seed keys, identical weights; three reduced keys absent original. No cross-paper paternal ID joins.

For identical observed seed set, calculate Hill2 once on father counts, once on total measured mass of father-assigned seeds. All original sites:
|site|count Hill2|mass Hill2|relative difference|
|---|---:|---:|---:|
|1|33.430972|40.754980|.219079|
|2|32.401602|36.219095|.117818|
|3|30.674574|38.482121|.254528|

Reduced all-site differences .102007/.187450/.259911; original outcross-only .132663/.082832/.070132; reduced outcross-only .050131/.173377/.139754. Within mothers with >=2 observed sires, original all 26/32 positive, median +.066971, equal-mother mean +.131059. Reduced all 25/31 positive, median +.066502, mean +.125943. Original outcross 19/31 positive, mean +.041829; reduced outcross 21/29 positive, mean +.044695. Published research already documented negative association between siring success and seed mass; this calculation is a new descriptive representation diagnostic, not a new claim about paternal effects.

## Conditional exchangeability diagnostic

Shuffle mass 1999 times (numpy seed 20261124) within mother x rhipidium x spathe x observed selfing status. Keep father labels/counts and group-level mass distributions fixed. Statistic is equal-mother mean relative difference mass Hill2/count Hill2 minus 1, informative mothers only. This is an exploratory conditional comparison, not a randomized experiment. Seed position within spathe, genetic associations and other factors can violate exchangeability.
|cohort|observed|permuted mean|95% null quantiles|upper tail (+1)|
|---|---:|---:|---|---:|
|original all|.131059|.124339|.103729,.144231|.2565|
|original outcross|.041829|.030805|.006527,.055578|.2000|
|reduced all|.125943|.117313|.096797,.139828|.2075|
|reduced outcross|.044695|.028067|.004911,.052812|.0995|

Observed increased mass representation evenness is compatible with the conditional reference. No evidence here for an extra sire-specific contribution beyond this conditioning. This is NOT a refutation of the original regression or a test of causal mediation. No genotype-specific germination, survival, net allele transmission, or fitness inferred. Different cohorts overlap; not independent experiments. No change to Paper A/TNC.

## Reproducibility

Locally executed analysis/152_zostera_realized_sire_representation.py on exact members in external_reproductive/zostera_paternity and analysis/153_zostera_seed_mass_sire_representation.py on verified seed_mass archive. Both source gates and local numeric checks succeeded; new independent CI pending. Draft PR #170.
