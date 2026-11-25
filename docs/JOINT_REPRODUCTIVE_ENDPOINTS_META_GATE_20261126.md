# Joint reproductive endpoints: source-locked analysis and meta-analysis eligibility (2026-11-26 JST)

## Scope
Targeted prior registry had 52 publication records (not independent studies and not a systematic search). Added Marion & Orth 2012 and Statton et al. 2017, now 54 records. Separate 11-record multistage eligibility ledger identifies exact endpoint pairs, treatment families, linkage and uncertainty. No pooled estimate: the only directly comparable joint animal-addition burial/germination original-data panel currently acquired is Laukaityte 2025. Shared controls, repeated strata, source articles and proxy outcomes cannot be treated as independent studies. This is a response-open reanalysis, not a registered systematic review. No new treatment effect for otters.

## 1. Joint burial and germination within the same experimental cores
Laukaityte et al. 2025, Oecologia 207:30, DOI 10.1007/s00442-025-05662-y. Original file from SimonaLaukaityte/heatwave-on-animal-plant-interactions commit ea4679016e8bddcd083cd93fe2fd6f33b6b1025e, blob cb12f65a477078f3980a381b5251a635db312d53. Exact ref and blob verified. Rows 81–240 as prior author-code selection (runs 2 and 3); 160 cores, 32 complete five-arm blocks, four fixed run-temperature strata, eight blocks per stratum. 1,529 recovered and 171 germinated records. 34 cores report >10 recovered despite nominal ten; retain counts. Depth bins close exactly. Endpoints: per-core fractions buried and germinated among recovered records, equally weighted across blocks and fixed strata. Not per-initial-seed germination, no measured realized recruitment. Burial is a position at recovery, not itself a positive survival transition. Original paper already reports heatwave-related interaction changes and increased germination among BURIED seeds in certain treatments; that conditional denominator is distinct from our all-recovered-record endpoint. No claim of refuting it.

Joint resampling preserves paired endpoints and all five treatment contrasts in the same sampled blocks; 40,000 within-stratum draws. Simultaneous centered max-standardized-error interval across 15 contrasts (five treatment pairs x buried, germinated, burial-minus-germination difference of contrasts). Approximate conditional interval, not randomization-exact or between-study inference; strata fixed, not independent climate replicates. Critical 2.79087. No seed-level pseudoreplication. Comparisons response-open. Percentage points:

| treatment – reference | buried diff [simultaneous 95%] | germinated diff [simultaneous 95%] | contrast gap [simultaneous 95%] |
|---|---|---|---|
| COCKLE – NO | +49.94 [31.88,68.00] | +2.94 [-4.70,10.57] | +47.01 [26.82,67.19] |
| SHRIMP – NO | +15.80 [-0.74,32.35] | -2.09 [-9.75,5.56] | +17.90 [-1.41,37.20] |
| WORM – NO | +10.70 [-8.10,29.50] | +0.17 [-8.29,8.63] | +10.53 [-10.04,31.10] |
| MIX – NO | +35.52 [20.76,50.29] | -4.05 [-10.88,2.78] | +39.57 [23.10,56.05] |
| MIX – COCKLE | -14.42 [-27.67,-1.16] | -6.99 [-13.68,-0.29] | -7.43 [-23.75,8.89] |

Mix vs no germination point estimate negative in all four observed strata, but simultaneous interval crosses zero. Both mix-vs-cockle endpoints lower, in all four observed strata; not proof of a general biodiversity cost (species density/composition differ), not a temperature interaction. Strict sensitivity excluding pairs with >10 recovered records changes cockle germination to -0.83 pp and mix/no to -5.12 pp; selection on post-treatment counts, not primary estimate. Mix/cockle strict germination -8.40 pp, per-nominal-ten germ count diff -0.65625 per core (scaled -6.56 pp). Conditional bootstrap sign fractions not posterior probabilities. Gap is difference in two measured fractions, not a physiological transmission rate or mediated effect.

## 2. Independent field evidence: burial and variation in the stage of benefit
Marion & Orth 2012, MEPS 448:197–207, DOI 10.3354/meps09612. Original text PDF retrieved via web, printed pp201–203 Results/Discussion and abstract; web screenshot attempted pages 4/5, cache miss. No graph digitization. Three sites, separate destructive recovery plots (50 seeds; four blocks) and repeated seedling video plots (200 seeds; six plots per treatment/site). Use source reported means and rounded post-peak losses (same site order verified). For each site final count ratio = implied peak stock ratio x relative stock retention from peak to final. Peak values are derived from rounded values, not new observed measures. Difference in peak date and observation/detection allowed. No direct individual survival or causal mediation; original study already reports burial reduced winter loss.

| site | final % surface/buried | reported peak loss % surface/buried | final ratio | postpeak stock-retention ratio | implied peak stock ratio |
|---|---|---|---|---|---|
| Piankatank River | 1.2/40.4 | 93/1 | 33.667 | 14.143 | 2.380 |
| Mumfort Island | 3.8/16.8 | 26/21 | 4.421 | 1.068 | 4.141 |
| Spider Crab Bay | 2.8/10.3 | 80/50 | 3.679 | 2.500 | 1.471 |

Postpeak fraction of log final ratio (descriptive additive log identity) Piankatank River 75.3%; Mumfort Island 4.4%; Spider Crab Bay 70.3%. Under half-unit rounding of displayed loss percentages and half-tenth of final percentages, dominance of peak vs postpeak component remains unchanged (see JSON). This is not sampling uncertainty. Recovery ratios from separate destructive plots 5.600, 3.000, 1.222; do not combine with terminal stock to infer cohort-level conditional survival. Germination among seeds retrieved after Dec was 90% pooled; no site x treatment-specific rate. Physical burial not animal manipulation.

## 3. Prior-art and scope boundaries
Statton et al. 2017, Scientific Reports DOI 10.1038/s41598-017-13833-y, 216 plots across eight locations and four seedling transitions, already identifies variation in the critical life stage: four shallow sheltered/moderate sites with early complete loss and three exposed sites with later complete loss; one sheltered deep site drives survival. Authors state cage effects confounded survival except Owen Anchorage, and exclude caged plots for main location analysis. Do not infer animal causality or convert matrix-model substituted zeros into observed survival. No raw replicate data found in accessible article; published context only.

The original burial/heatwave paper, Marion and Statton already demonstrate important parts of the stage-specific bottleneck idea. New target is quantitative joint endpoint comparison with same assigned units, covariance, source hierarchy and independent validation, not discovery that life stages differ. Registry is curated and response-open. Next systematic search should prespecify contrast family animal presence/access/abundance vs no animal, outcome order and cohort linkage, and separately collect randomized study-level joint effect estimates with sampling covariance. Do not pool physical manipulation, observational otter gradient, flowering proxies or distinct cohorts into an animal-recruitment effect. No main/Paper A/TNC changes.

## Reproduction
node analysis/189_joint_burial_germination.cjs data.txt output.json
node analysis/190_burial_field_peak_accounting.cjs output.json
Both analysis functions executed in JS on exact original file or audited published values; offline wrappers not independently CI-replayed. Results and 11-record eligibility ledger committed.
