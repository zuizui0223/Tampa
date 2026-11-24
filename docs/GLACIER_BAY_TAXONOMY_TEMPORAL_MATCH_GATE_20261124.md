# Glacier Bay taxonomy, sampling design and temporal-overlap audit

2026-11-24. Response-open observational reanalysis; **not a prey-selection model or a causal plant/otter effect**.

## Provenance and new source files
Original run 45383304380 artifact 14914948367 SHA256 d4b902fb8216844bb078cf9ba0e9a87f1767defc1781534245761a45c82cadfd, USGS DOI 10.5066/P9T6UB5G forage and 10.5066/P9LODH0Z mixed-sediment benthos. Retried source run 45386052728 artifact 14915918501 SHA256 e54e44830d2906015cae7434fb0bf3fd13a5145340efad3084523ec84126b7ac. Downloaded archives, source SHA256, publisher MD5, byte counts verified locally.
- forage_taxonomy.csv 83 unique prey codes, cp1252, SHA256 82fa3ba5e9d40b8dee1207c0fa6f1f4141d5c57ea5b380b809eaf47e91427499.
- benthos_sites.csv 161 rows, unique year/zone/site, SHA256 0cede7c116d92cd945026b2d4e888d249db1f1336dfad1132af3d8141ce9e79d.
- benthos_metadata.xml SHA256 ae7d6de9296f741b16829c09b519c10a2d7aa93f3183b3c85b62ce6fd7ba43d8.
Exactly 160 sampled benthic events match site metadata. Site 240 has an unmatched 2000 compact-count event and 1999 metadata-only event; do not silently equate or impute. Omit from design and spatial comparisons. Compact observed quadrats remain denominator, including explicit empty quadrats.

## 1. Time windows aligned to benthic survey years
Same dive inclusion as analysis 148 (17,128 valid complete cycles), but restrict early to 1998,1999,2000,2001,2002,2004,2005,2006,2007; middle 2010–11; late 2018–19. Select sites with >=5 bouts in all three windows, 12 sites/12,356 dives. Equal weight site-level rate (ratio of total retrieved counts to sum of complete dive + surface hours). Site bootstrap 20,000, seed 20261124. These are observed cycle rates, not biomass, intake, or removal flux.

| Endpoint | Early | Middle | Late | Mid minus early [95% site bootstrap] | Late minus mid [95%] |
|---|---:|---:|---:|---:|---:|
| Small |34.69|86.35|304.92|+51.66 [38.80,65.51]|+218.58 [132.42,311.91]|
| Large |34.18|17.08|4.84|-17.09 [-24.09,-8.99]|-12.24 [-19.82,-6.11]|
| Total |70.02|103.93|310.12|+33.91 [21.46,46.80]|+206.19 [124.20,296.16]|

58.3% of observed early-to-late large decline accrued by middle observations; 80.9% of observed small increase accrued between middle and late. Not a continuous time lag estimate; there are no 2012–17 observations, windows unequal, and no direct spatiotemporal prey pairing. Sensitivity to >=10 bouts (10 sites), summer only (8), adult females (8), equal site-year weighting, all early years, retention of duplicate rows, and dropping high-count dives (global 95th percentile) retains directions; latter reduces small late mean to 163.29 and after-middle fraction to 63.4%. No independence of spatial sites guaranteed.

## 2. Taxonomy clarifies the later increase
Source code mus = any mussel (Mytilidae, not a resolved species), mtr = Mytilus trossulus, uni = unidentified prey; mom = northern horse mussel (source misspells genus Modilous), cla = any clam, std = Strongylocentrotus droebachiensis. Previously recorded 13-site long-window small increase contributions mus 49.8%, mtr 28.9%, uni 13.5%; not all species IDs.
For the new balanced 12 sites, classify small retrieved items as mus+mtr, uni, other codes with a source class, and other class-unassigned codes. All positive count prey codes have source lookup records. Mean per cycle hour:

| Group | Early | Middle | Late | Late minus middle (95% site bootstrap) |
|---|---:|---:|---:|---:|
| mus+mtr |2.1464|4.1423|219.6974|215.5551 [133.3275,303.3015]|
| other class assigned |28.8324|68.7202|43.7656|-24.9546 [-41.3216,-9.6631]|
| uni |3.7141|13.4111|41.4243|28.0132 [10.4806,47.6799]|
| other unclassified |0|0.0747|0.0361|-0.0386 [-0.1941,0.0696]|

98.62% of net small-item increase in last contrast due to mus+mtr. Other class-assigned counts decline in 9/12 sites. Mussels increase in 11/12, one unchanged. These proportions refer to net arithmetic changes, not share of diet or causal mechanism. Leach et al. 2024 (10.1002/ecs2.70084) already described late Mytilus shift, noted dense beds observed in 2018, and suggested a resource pulse / sea star wasting / marine heatwave explanation. No novelty claim for that prior hypothesis. The time normalization, within-site contrasts and design audit are extensions. No detailed co-located mussel abundance observations for 2018–19 in this source.

## 3. Design-stratified benthos contrasts
Using source site_selection categories, match early <=2007 and 2010–11 site-years; within site equal years, within group equal sites, observed-quadrat densities, site bootstrap 20,000 seed 20261124 independently per group. Random intertidal 35 matched, selected high-clam-density intertidal 9, selected subtidal 11.
| Group | Total early -> mid | Total delta [95%] | >=50mm early -> mid | Large delta [95%] |
|---|---|---|---|---|
| random intertidal |19.1511 -> 22.6678|+3.5166 [-0.5306,7.4690]|1.6041 ->1.0665|-0.5376 [-1.4333,0.3160]|
| selected intertidal |95.9695 ->77.3778|-18.5918 [-42.9716,-1.1078]|10.0609 ->5.3889|-4.6720 [-7.7467,-1.8368]|
| selected subtidal |55.4584 ->30.9646|-24.4937 [-36.5869,-14.0214]|16.5581 ->8.5510|-8.0071 [-14.1229,-2.2186]|

Random intertidal Leukoma staminea 2.614 -> .380 (-2.234 [-3.844,-.910]), Hiatella arctica 3.254 ->7.039 (+3.784 [1.009,6.820]), Saxidomus gigantea .660 ->.549 (-.111 [-.780,.414]). Qualitative community reorganization survives the design check; broad decline of large clams is unresolved in random locations. No evidence of direct interspecies replacement or direct otter causality. Selected sites were chosen for high initial abundance, regression to mean and habitats matter; difference of significant and nonsignificant results is not an interaction test. Percentile intervals exploratory and spatial dependence not modeled. Size cutoff post-hoc.

## 4. Geographic and temporal match gate
Each eligible bout has one verified bout coordinate/date. Assign to nearest sampled benthic site-year in same calendar year, <=90 absolute days and radius .5/1/2/5 km. Exclude unmatched site 240 event; use observed compact quadrats, don't create zero for missing samples. Random intertidal primary. Match only source exact recorded clam labels (explicit Leukoma synonym), Mya and Macoma collapsed to genus; 14 forage codes to 11 clam taxonomic labels. Keep generic cla and uni separate. Hiatella not specifically identifiable in forage taxonomy. No assumption that all unknown prey are sampled clam species. Nonrandom and subtidal alternative cases diagnostic. A bout only counted once per case. Spatial proximity does not establish the animal fed at the quadrat.

| Random intertidal radius | Matched bouts | site-years | sites | adequate events (>=5 bouts and >=10 matched clam items) | sites adequate in BOTH early/middle |
|---|---:|---:|---:|---:|---:|
|0.5 km|53|5|3|4|1|
|1 km|131|9|7|5|1|
|2 km|242|14|11|9|1|
|5 km|521|26|15|18|3|

2 km case 1,921 dives, 6,179 retrieved items, 1,071 mapped clam items (17.33% of all), 698 generic clams, 779 uni; among mapped plus generic clam counts only 60.54% resolved to comparable labels. Adequate events span 7 sites, only 2 early events and 7 middle events; only one repeated site. All zones at 5 km yields 796 bouts, 50 site-years, 32 adequate events, 5 repeated sites, but mixes habitats and targeted designs. No formal selection model fitted: benthic survey samples organisms >=14 mm in mixed sediment at MLLW or shallow selected subtidal clam beds, not representative of epibenthic mussel beds or all potential foraging depths. Calendar/date/spatial gates cannot fix this sampling mismatch. Small cutoffs are paw-width not mm, and prior study notes no detailed 2018–19 Mytilus time series. These screening thresholds are exploratory, not power guarantees.

## 5. Revised ecological question and next independent data
The pronounced late mussel-specific acquisition increase is compatible with a resource pulse as well as top-down effects; we cannot distinguish these using existing benthos. Do not claim a new prey-switching mechanism. Traiger et al. 2022 reports heatwave/sea-star-wasting-associated mussel increases elsewhere in Gulf of Alaska; separate regions, not Glacier Bay availability estimates. The original Leach study already links these mechanisms. Prior USGS rocky intertidal monitoring protocol DOI 10.3133/ofr20101283 ends its reported sampling in 2001. Need public epibenthic site-year census through 2019, local otter abundance, actual consumed prey and same habitat. The original study's 2018 dive observations are qualitative contextual evidence, not acquired survey tables. For seagrass work specifically, no locally matched seed capture or establishment measurements. The relevant hypothesis is whether resource pulses and prey replacement preserve or change the functional pathways available to foundation species. Maintain plant-side manipulative evidence separately, and do not use unrelated Alaska clam counts as a seagrass mechanism. Main/manuscript untouched.

Local exact executed scripts overlap_windows.py and site_taxon_link.py and full JSON outputs retained; repository summary is a compact machine-readable record, not full bootstrap draws. No independent replication or new heldout validation.
