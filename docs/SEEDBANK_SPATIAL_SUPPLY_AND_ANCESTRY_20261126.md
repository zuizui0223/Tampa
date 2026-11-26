# Scale-dependent coupling of local flowering and dispersed seed stocks (2026-11-26 JST)

## Scope, source, and acquisition
Sotka, Hughes, Hanley & Hays (2024), Molecular Ecology, DOI 10.1111/mec.17565. Original author public repository https://github.com/esotka/ZosteraSNPs/tree/bec412e35b8669b2850bf8f1d525e5c0ab850d00 (exact commit). Paper methods and results checked against indexed publisher text, https://onlinelibrary.wiley.com/doi/10.1111/mec.17565 ; deposited archive DOI 10.5281/zenodo.13798979 landing page not accessible in current runtime, so do not assume GitHub files identical to final archived data. Exact source hashes checked via connector. The new analyses are on original deposited phenotype CSVs and author-produced genetic outputs, not a re-fit of the original SNP likelihood or DAPC models. No newly collected data.

Files for analysis 196:
- data/seedPhenotypes.csv 1a1dc32028592569eeeef716873570d9230450db
- data/perm.quad.density.2019.csv 3a9ee3bf0c6a0be0fa2688d87a8cba6acc80f883
- output/SeedAssignment-DAPC.txt 8b83e6473a085036a044e1a671f4aa0022bf691d
- output/SiteQuadratLatLon.csv 7d37d8cad640bbb294c4533bdb6aee25925ed343
- data/214adults99seeds_noClones_clean 080e05545930f83b2d298798b77f77596830d681
- output/sigma_estimates.txt 4233b972171dfd9df45466e72192778d73bc3b6e
Files for analysis 197: same 313-ID list and data/ngsAdmixFiles/k02run1.qopt c5792c09d5c48708d34215e25fb87878510aaad3, k05run1.qopt 9409a9f2192728e80edb4a8c6bd2a0abdaf53748, k09run1.qopt b767d3c144a0dbaae4b8d623c762ca123d4a7323. Author R scripts for source grain, filtering, and positional qopt mapping inspected. All Q rows sum to one within tolerance.

Acquisition recheck: Canadian Vercaemer source 56cfea6f-aeca-47ed-94ab-c519d9e63c91 now has exact CSV.zip, XLSX.zip and DataDictionary.csv URLs at api-proxy.edh-cde.dfo-mpo.gc.ca catalogue record attachments plus public DFO ArcGIS MapServer. Government catalogue indexed; web direct 403 and local requests for CSV, dictionary and ArcGIS failed DNS. No Canadian original data acquired. Kendrick Dryad 10.5061/dryad.vhhmgqnwz and 10.5061/dryad.dfn2z3577 and Sinclair et al. 2018 10.5061/dryad.8s3n710 metadata identify datasets (latter floating fruit assignments and model matrices), local direct Dryad API DNS failed. No new original Rottnest or Sinclair data acquired. Sinclair et al. 2018 DOI 10.1111/mec.14939 already explicitly identifies mixed fruit origins with hydrodynamic transport, different host/propagule/stage; do not claim source-sink separation as new.

## 1. Grain and data-quality gate
Four Massachusetts meadows, three grids per depth, two depths, 24 grids. June 2019, 141 valid 25x25-cm shoot-count quadrat records (4–7 per grid), checked total = flowering + vegetative count; August sampling is separate, not used. September, 90 sediment cores, 10 cm diameter and depth (3 per grid Curlew and 4 elsewhere), all explicit core keys retained, including source FALSE zero records. Pair at site × depth × grid, not same shoots or tracked seeds. Counts are different measurement areas and observation dates. Original author R/seedPhenotypes.R sums seedTF, so use TRUE count as primary count, not all rows or mass count. 224 CSV rows = 170 TRUE, 54 FALSE; 162/8 TRUE shallow/deep, all rows 178/46. Paper prose reports 176/46 dispersed seeds; unresolved difference, no assertion of cause or repair. Some TRUE records labeled seedcoat, rotten, dead, lost or with no mass. One duplicate within-core seed index DC SH 1 B 1: rotten and tissue (distinct records, actual identity not identifiable). Preserve original row counting, not claim 170 unique viable seeds. Sensitivity restricted to 132 TRUE positive measured masses (128 shallow, 4 deep), selected by handling/availability and not a corrected viable seed count. No blank core imputation; all 90 expected cores explicitly represented.

## 2. Spatial concentration and depth
|Site|Shallow mean seedTF count/core|Deep mean|Shallow:deep June flowering mean ratio|Shallow:deep core mean ratio|
|---|---:|---:|---:|---:|
|Curlew|8.55556|0.55556|9.000|15.400|
|Lynch|0.41667|0.08333|2.714|5.000|
|West|5.75000|0|11.000|undefined (zero recorded deep)|
|Niles|0.91667|0.16667|6.333|5.500|

Shallow greater in all four, a previously published pattern. Pooled 45 cores each: shallow 162/45 =3.6, positive 29/45 (64.44%), conditional mean 5.586; deep 8/45=.17778, positive 7/45 (15.56%), conditional mean 1.143. Symmetric arithmetic decomposition of difference 3.4222: incidence +1.6449 (48.06%), positive-core abundance +1.7773 (51.94%). This is neither dispersal-mediated nor causal. A single Curlew shallow core DC|SH|3|A contains 53/170 TRUE records (31.18% of all, 68.83% within Curlew shallow); top three 47.06%. In measured-mass subset 41/132 (31.06%) in same core. Inverse concentration (sum counts)^2 / sum squared counts =7.992 of 90 cores, not effective independent sample size. Exclude largest core only as response-open sensitivity: remaining 109/44 shallow vs 8/45 deep, ratio 13.935 (primary 20.25); direction not driven entirely by largest core. Curlew shallow mean without largest core 3.0. No inference of clustering process, seed immigration or successful recruitment; spatial aggregation may reflect seed supply, retention, local habitat, loss or sampling.

## 3. Does local flowering predict later seed counts?
Across 24 grid means, Spearman .6083 (flowering count), .5936 (vegetative), .5940 (total). Within fixed site × depth groups of three grids, compare all 24 unordered pairs: flowering vs seed count, 6 concordant,7 discordant,11 ties; vegetative 12/4/8; total 11/5/8. Mass-only flowering 8/6/10. Pair counts dependent and exploratory, not an independent sign test or proof of no local effect. Observed local flower density is not total seed production.

Leave-one-entire-meadow-out ridge diagnostic; target log1p(grid mean seedTF count/core); predictor standardization on training set only, unpenalized intercept, fixed lambda 1 primary, .1 and 10 sensitivity, predictions clipped nonnegative. Equal grid weight, no tuning or independent year. 18 training and 6 held grids per fold (4 folds). MSE:
|Model|All grids|Exclude entire largest-core grid|Measured-mass subset all grids|
|---|---:|---:|---:|
|Training mean|.776306|.491571|.668492|
|Depth|.619645|.429939|.516828|
|Vegetative|.660737|.423194|.548253|
|Flowering|.434328|.316742|.334192|
|Depth+vegetative|.645035|.429610|.537061|
|Depth+vegetative+flowering|.463085|.340092|.359443|

Adding flowering to depth+vegetative reduces pooled MSE 28.21%, 3/4 held meadows improve at lambda1; positive pooled increment at all three penalties, in mass subset and response-open largest-core-grid exclusion. Flowering-only model lower MSE than all fixed comparators in this tested panel, but not a selected validated model. No new forecast guarantee: one year/four meadows, response-open predictors, no independent spatial region, no estimate of cause. The positive regional scale diagnostic does not contradict weak within-stratum ranking: larger-scale structure may generate the predictive signal. This is the new contribution, not discovery of shallower higher seed counts. No direct dispersal or local seed supply budget inferred.

## 4. Published-output DAPC assignment audit
Author script builds eight adult site/depth groups and forces assignment of seeds to those groups. Table rows predicted adult group, columns seed collection group; 99 total, all column counts agree with 99 IDs in source 313-ID list. 48 same meadow/depth, 8 same meadow other depth, 43 other meadow (14 West-S labels among Curlew-S, 29 Lynch labels among West-S). This output appears less locally concentrated than qualitative 'nearly all' paper wording; version difference or interpretation unresolved. No per-seed DAPC label/posterior or independent classification calibration. Seed nuclear signal includes both parents; labels are not maternal origins or verified migration. Group centroid straight-line distances: depth pairs 133–194 m; West-Lynch label pairs 4.52–4.55 km, West-Curlew 17.90 km. These are distances between sampling grids, not seed movement. Published final paper sigma approximately 111–153 m depending MAF (kernel standard deviation approximate mean, not a hard range); repository sigma output 147–192 m, different version/estimator, not reconciled. No use of either Gaussian model to rule out real long-distance dispersal.

## 5. New ancestry-vector classification sensitivity
NGSadmix Q files from original author run, K=2,5,9 (paper best K2 and finer K5/9). Row order follows source author R script and 313 ID list, no independent ID field in Q files. 214 clone-filtered adult and 99 seed vectors. Nearest-centroid classifier using adult site/depth groups, adult grid-equal centroid, Euclidean primary; Hellinger distance, individual weighting and four site-only groups as sensitivities. Hold out each of 24 adult grid labels for adult centroid estimation, then classify adult samples; seed samples classified with all adult centroids. Importantly, Q vectors were ALREADY fit jointly with all samples; adult holdout only excludes centroid labels, NOT genetic model training. This is a transductive diagnostic, not independent validation of DAPC or natal origin. Adult known label is collection site, not origin. Site-depth labels are observational. No uncertainty posterior or p-values.

Primary site/depth classifier:
|K|Adults assigned same sampling meadow /214|Seeds resembling same collection meadow /99|Seed other-meadow labels|
|---|---:|---:|---:|
|2|123|48|51|
|5|167|38|61|
|9|175|69|30|

Adult same-depth+site accuracy 79/214,115/214,132/214. West adults same meadow 4/38,13/38,22/38. Thus especially West has low adult label discrimination despite joint fit. Full 24 configurations in JSON; different models give substantially different seed labels. Across four prespecified descriptive fine-K sensitivity combinations (K5/K9 x Euclidean/Hellinger, same grid-weighted site-depth centroid), 36/99 seeds all local, 19/99 always nonlocal, only 18/99 assigned same nonlocal meadow in all four, 45/99 neither consistently local nor same nonlocal. For West, 17/47 consistently resemble one different meadow, 0/47 always local; Curlew 1/38 stable nonlocal, Niles 11/11 stable local. These are agreement counts across correlated methods, NOT confidence, immigrant fraction, or individual DAPC agreement (individual DAPC results unavailable). No correction using adult errors because adult collection origin unknown and seeds differ from adult genotype distributions; cannot identify true migration. This reinforces original authors' warning on forced assignments and mixed-origin ambiguity.

## Conclusion and conservation boundary
Locally high reproductive shoot density is useful for comparative seed stock monitoring, but its predictive utility is scale-dependent and seed records can be very concentrated within a meadow. Demonstrating seed-source vs recipient habitat separation requires origin-calibrated evidence and independent repeated seed flux/stock and recruitment records. Current results justify measuring local flowering and spatially replicated seed-bank cores separately; they do not identify a high-quality recipient meadow, quantify import or a causal effect of otters/other animals. Do not pool separate study outcomes. No changes to main/Paper A/TNC. Registry 69→70 records, multistage context ledger 19→20, not independent study effects.

## Reproduction
node analysis/196_seedbank_spatial_supply_gate.cjs seedPhenotypes.csv perm.quad.density.2019.csv SeedAssignment-DAPC.txt SiteQuadratLatLon.csv 214adults99seeds_noClones_clean sigma_estimates.txt output.json
node analysis/197_seed_ancestry_label_sensitivity.cjs 214adults99seeds_noClones_clean k02run1.qopt k05run1.qopt k09run1.qopt output.json
Both analysis functions actually executed in JS on exact-ref source content; saved Node wrappers include exact Git blob checks. No independent CI replay, SNP refit or manuscript submission.
