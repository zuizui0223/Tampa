# Flowering donor availability and external genetic source gates

## Prior verification
Enhalus spatial null decomposition run 45377497716, at head eb7e1f9a50f2ef51e27e98a5e323346b9e7affde, completed successfully; 9/9 PR workflows succeeded. Previous actual coordinate and MLG results unchanged.

## New computation, executed on exact original Enhalus workbook
SHA256 10e1465ac9255ad2d873d6142386b5140320740ebc660196b4a9eb0e2251c959. Same two 20x20 m plots (A disturbed, B continuous). Conditional on focal genet female and flowering; assign each other MLG an independent male probability p. Within radius r, other MLG g has k_g observed ramets. If independent ramet flowering probability f is assumed within male genets, probability of at least one active male ramet from g is q_g=p[1-(1-f)^k_g]; alternatively perfect flowering synchrony gives q_g=p*f. Then P(any candidate male)=1-product_g(1-q_g), E(active distinct male MLGs)=sum_g q_g. Average over measured focal ramets, and separately weight each genet equally. This is a scenario on actual geometry, not measured sex, flowering, pollen transfer or fertilization. Marker-defined MLG as genet proxy; no flow, pollen dose, outside-plot source, phenology or compatibility data. No claim of causal disturbance effect.

At p=.5,f=.1, independent ramet mode:

|radius m|A P(any)|B P(any)|A expected active male MLGs|B expected active male MLGs|
|---:|---:|---:|---:|---:|
|1|.1029|.1381|.1073|.1457|
|2|.2801|.3628|.3256|.4412|
|4|.7042|.8051|1.2365|1.6406|
|8|.9719|.9911|4.2118|5.4534|

Equal p=.3/.5/.7, f=.01/.05/.1/.25/.5/1, 2 within-genet flowering modes, 4 radii =144 scenario cells. B exceeds A in ramet-weighted P(any) and expected number of active male MLGs in all cells; genet-equal P(any) exceeds A in 142/144 (two near-saturated 4m cells differ by <1e-7 in opposite direction). These are not independent replicates or statistical evidence. P(any) can approach one even while expected count differs; an active male count is not realized number of sires.

Exploratory break-even computation on the same geometry: fix B at f=.10 and both plots p=.5; solve mean_A(f)=mean_B(.10) by 40 bisection iterations on [0,1]. Required A flowering probabilities for P(any), independent ramets: .136296, .137277, .136041, .140982 at r=1,2,4,8 m. Synchronous genets: .130009, .126054, .118692, .119537. This describes hypothetical compensation for geometry; not an observed response of disturbed plants. Main sensitivity and tests in analysis/143_enhalus_hypothetical_flowering_donor_gate.py. Break-even arithmetic executed locally and described here; not a new preregistered or independent validation.

## Independent source candidates and novelty boundary
- Berković et al. 2018, DOI 10.1371/journal.pone.0199275; original S1 Table DOI 10.1371/journal.pone.0199275.s004 has genotype and coordinates, 3185 analyzed ramets, 1999 MLGs. 803 occupied sample coordinates, four ramets per 4m2 quadrat, average nearest plot spacing 96m; no equivalent dense grid at 1-8m. Do not treat unsampled positions as absent plants. Candidate for within-quadrat MLG overlap and sampled landscape-scale geometry only. Published work already found clonal dispersal over kilometers.
- Sgambelluri, Dryad 10.5061/dryad.dfn2z358x: original parent/seed genotypes, COLONY paternity files, per-shoot and per-spathe outputs; three NC meadows, sampled flowering shoots had no detected clones, average 8 sires, about 70% outcrossing. Direct realized paternity, but not verified matched dense adult coordinate maps; cannot claim it tests geometry-specific pollination distance or Enhalus donor access.
- Rottnest Posidonia Dryad 10.5061/dryad.dfn2z3577: adult and seedling genotypes, metadata reports random GPS adult points in 50m circles, seven loci including triploids. Inspect coordinate grain, ploidy and identity before fitting. Site coordinates not automatically individual coordinates.
- Existing studies already connect clone dimensions and pollen dispersal: Posidonia australis DOI 10.1093/aob/mcu048 mean pollen distances 30.8/26.8m vs mean clone sizes 12.8/13.8m and near complete outcrossing; Zostera noltei study PMC3002472 found pollen and clone sizes similar with high outcrossing. No first-discovery claim of scale-dependent mating.

Added original-source acquisition/inventory script 144 and dedicated Actions workflow. Local network DNS prevented direct source downloads; web metadata is available but new external workbook contents not yet confirmed. External source inventory jobs can succeed while reporting individual STOP; never interpret a green job as completed external ecological replication. No new Paper A or TNC changes; keep Draft.
