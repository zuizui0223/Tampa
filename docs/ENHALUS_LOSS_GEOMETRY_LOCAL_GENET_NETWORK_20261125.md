# Enhalus: virtual loss geometry, local genet neighborhoods and landscape diversity (2026-11-25)

## Source and analysis boundary
Yu et al. (2019), Ecology and Evolution, DOI 10.1002/ece3.5106; Dryad 10.5061/dryad.sn1h87s. Original workbook "yu/Ramets For Two plots.xlsx" extracted from source artifact 14911175880. Verified archive SHA256 b5b116221241e9e603896a9dc99f66287f4707a313c12bf83ff7dd00487dc1f2 and workbook SHA256 10e1465ac9255ad2d873d6142386b5140320740ebc660196b4a9eb0e2251c959. Two 20 x 20 m coordinate plots: A fragmented, 271 sampled shoots, 214 exact multilocus genotypes; B continuous, 395 shoots, 255 exact multilocus genotypes. Eight diploid loci, sort alleles within locus; no missing coordinates/loci or duplicated coordinates. No flowering, sex, compatibility, current measurements or actual disturbance treatment in the analyzed records. Exact MLG identity is a working genet proxy. The comparison is conditional on the sampled points and excludes donors outside the plots. One plot per observed habitat, no independent habitat-level replication.

## Counterfactual design
Remove exactly round(n*loss) sampled ramets at losses 25%, 50%, 75%; remaining counts 203/135/68 in A and 296/197/99 in B. 500 virtual removals per plot x loss x mode (9,000 masks overall). Three modes:
- Random: uniform independent scores, remove lowest ranked.
- Localized gap: remove ramets nearest to a center uniformly sampled in the 20x20-m square (possibly clipped by plot boundary).
- Parallel gaps: remove ramets nearest to periodic parallel lines 6 m apart, with uniform orientation in [0,pi) and phase in [0,6). This period is illustrative, not field-calibrated.
Independent random tie breaks; seeds 20261125/20261126. Count all distinct *other* MLGs among retained neighbors within 1,2,4 m, average over retained focal shoots, and count distinct retained MLGs across the full plot. Also use an illustrative directed donor sector within +/-45 degrees of one of eight uniformly sampled orientations, same axis per replicate across removal modes. This is only a geometric restriction, not a hydrodynamic model. All calculations executed locally on verified original data; sparse matrix implementation reproduced 100-replicate pilot output byte-for-byte. 500-replicate output generated successfully. Simulation quantiles describe the scenario draws, not biological sampling CIs. No fitted reproductive effect, no causal claim or true pollen connectivity.

## Results
At 50% nominal loss (fixed 135/197 survivors):
| plot | geometry | mean retained MLGs across plot | mean distinct other MLGs within 1m | within 2m | within 4m | 2m sector count | fraction with zero other MLGs in sector |
|---|---|---:|---:|---:|---:|---:|---:|
| A | random | 120.280 | 1.0701 | 3.1183 | 11.4347 | 1.1762 | .27554 |
| A | localized gap | 108.928 | 1.9324 | 5.1501 | 16.6949 | 1.9725 | .13394 |
| A | parallel gaps | 112.920 | 1.6760 | 4.0854 | 10.2268 | 1.5592 | .22824 |
| B | random | 148.286 | 1.4147 | 4.0149 | 13.9746 | 1.5605 | .15940 |
| B | localized gap | 131.018 | 2.6010 | 6.7491 | 20.4855 | 2.6703 | .07486 |
| B | parallel gaps | 140.636 | 2.1991 | 5.2110 | 12.4826 | 2.0557 | .15401 |

Unremoved plot mean distinct other MLGs within 2m: A 5.900369, B 7.410127. Localized gaps preserve more local candidates per surviving ramet than random loss (+65.2%, +68.1% at 2m) but fewer distinct MLGs across the entire plot (-9.44%, -11.64%). At 2m parallel gaps preserve more local candidates than random loss, but at 4m they preserve fewer in both plots (-1.2079, -1.4920 mean other MLGs). The reversal holds in the illustrative 90-degree sector at 2 versus 4m. This pattern depends on the chosen spacing of cleared strips relative to the neighborhood radius, not a universal result about fragmentation. Larger local neighborhood counts do not imply higher total seed production; removed recipients, sex-specific flowering and transport not measured. Random loss preserves more plot-wide MLGs on average in these simulations while spatially localized loss preserves denser survivor neighborhoods. Population-level richness and local potential mating access are distinct conservation quantities.

## Implication and next validation
Candidate hypothesis: reproductive consequences of seagrass loss depend jointly on the spatial pattern of remaining shoots, their clone identities and the realized scale/direction of pollen transport. Test with observed sex/flowering maps, paired water/animal transport measurements and recipient-level reproduction, before estimating management thresholds. Do not claim water/animal complementarity from these simulations or label them empirical reproduction. Extend distance and gap-width sensitivity with independently measured dispersal kernels, and use observed true before/after patches where available. No manuscript/TNC or main-branch changes. Local calculations finished; no new independent CI run in this turn.

Reproduce: python analysis/177_enhalus_virtual_removal_geometry.py <verified-source-workbook-or-original-artifact-zip> --simulations 500 --out results.json
