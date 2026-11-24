# Flower visitor guild audit and a resident–transient distinction

2026-11-24. Follow-up to REPRODUCTIVE_INTERACTION_GATES_20261124.md. Published aggregate reanalysis; NOT species-level confirmed pollination or grazing, NOT a meta-analysis.

## Sources and provenance

- Van Tussenbroek et al. 2012, 10.3354/meps10072, Table 2 and Supplement 2, https://www.int-res.com/articles/suppl/m469p001_supp.pdf . 76 flowers sampled (51 pollen-bearing male, 19 male without pollen, 6 female), 312 individuals total (252 crustaceans, 60 annelids). Supplement 2 is accessible as indexed PDF text. Screenshot endpoint failed; keep totals across flower categories only, because some PDF column alignments are ambiguous. Preserve source taxon strings, including unidentified morphotaxa and historical spellings; no WoRMS resolution claimed. These are taxonomic records rather than 34 verified species.
- All peracarid rows (source crustacean rows 12–45) transcribed to data/seagrass_interactions_v1/flower_visitor_peracarid_2012.csv. Summed specimen counts across flower types are cross-checked against the rounded order totals in Table 2 (Mysida 2.6%, Amphipoda 17.9%, Isopoda 5.4%, Cumacea 11.2%, Tanaidacea 3.8%). Diet bins reflect original H/O labels: H herbivore, O omnivore (possibly additional feeding guilds); other = stated diet without H or O; unknown = missing or ambiguous. Isopod Dynamenella quadriralata has ambiguous extracted column alignment, conservatively unknown. No imputation or trait harmonisation.
- Van Tussenbroek et al. 2016, 10.1038/ncomms12980, https://www.nature.com/articles/ncomms12980 . Mixed-fauna experiments establish pollen delivery and pollen tube growth; illustrated body pollen carriers include decapod zoeae and a syllid polychaete. One illustrated majid zoea contained pollen in the digestive tract, which is ingestion rather than proof of transfer. Experimental light traps preferentially sampled small fauna. No taxon-isolated estimate of effective pollination.
- Van Tussenbroek et al. 2016, 10.1007/s00442-016-3665-7, documents already-established hydrophilous pollen-limitation Allee effects in Zostera noltei, including ca. 35% reduced fruit set in fragmented vs continuous populations of comparable reproductive density. This invalidates claims of novelty for density-dependent reproductive failure alone. Both the 2012 and 2016 animal-pollination papers already proposed reproductive assurance under weak flow and sparse flowering.
- Gross et al. 2024, 10.1111/geb.13918, documented eelgrass genetic richness associations with the peracarid: gastropod balance and taxonomic/trait composition. Their Dryad deposit 10.5061/dryad.np5hqc00p lists Code_and_data.zip (185.31 KB) and README.md. Foster et al. 2021, 10.1126/science.abf2343 / Dryad 10.5061/dryad.ns1rn8pt4, reported an association between otter recovery and plant genetic diversity. Neither raw data archive was accessible in this runtime (DNS failed; web API access failed). No new Gross or Foster model fitted.

## Executed reaggregation

Group | taxa | specimens | H | O | other | unknown
---|---:|---:|---:|---:|---:|---:
Mysida |1|8|0|8|0|0
Amphipoda |8|56|31|7|5|13
Isopoda |11|17|5|0|2|10
Cumacea |10|35|10|0|24|1
Tanaidacea |4|12|0|11|0|1
Total |34|128|46|26|31|25

Peracarids account for 128/312 = 41.03% of all flower specimens and 128/252 = 50.79% of crustacean specimens. 72/128 = 56.25% are source-coded herbivores or omnivores; 72/103 = 69.90% among known bins; 75.78% is the extreme upper bound if all unknown records were H/O. Tethygeneia longleyi accounts for 30/128 = 23.44% of peracarids. Numbers describe pooled specimens, not site prevalence or independent flower-level replicates. No selection test, no direct overlap of species-level pollination and epiphyte consumption demonstrated. Analysis arithmetic executed in JS and matched order totals; equivalent Python script is committed for reproducibility, not independently run this turn.

## Revised hypothesis: habitat-linked residents versus mobile/transient vectors

2012 field flower visitors include many peracarids and other groups; 2016 experimental evidence of pollen attachment includes larvae and worms. Thus the predicted animal contribution cannot be reduced to one grazer guild. Distinguish resident animal abundance tied to canopy and food supply from nocturnal migrant/larval influx (water movement, plankton supply, settlement). Residents could link the host's state to pollen transport and algal control; mobile immigrants might preserve pollen transport during local thinning. Which pathway dominates remains unknown.

A candidate encounter model separates lambda_water, lambda_resident and lambda_transient with fruit set 1-exp[-(lambda_water + lambda_resident + lambda_transient)], only an illustrative idealized model. If the resident vector supply rises with canopy density D and male density also rises with D, the resident contribution can scale as D^2 while independent migrant supply yields a linear contribution. Under that limiting example local decline can be amplified or buffered, but these exponents are hypotheses not estimates. Flower density, sex ratio, flow, reproduction timing and vector arrival should be measured separately. In particular, absence of a statistically detected distance effect is not proof of equivalence; 2016 treatments randomized at tank level, flowers within tank not independent treatment replicates.

## Next data gates

1. Species-specific functional intersection: resident taxa have direct evidence of epiphyte consumption AND pollen transport/seed set, using local species and life stage; a H/O label is only screening.
2. Need background faunal availability before interpreting visitor enrichment; Monroy-Velazquez et al. 2017 (10.7717/peerj.3411) surveys coral-rubble peracarids in the same regional park, but not matched seagrass flowers, and is a candidate regional species pool only.
3. Obtain Gross archive and test plant genetic diversity vs community-weighted peracarid diets conditional on plant architecture, geography, and species-level trait coverage. Model total peracarid fraction separately from traits within peracarids; no global claim of animal pollination in Zostera.
4. Obtain Foster raw archive; no shared sites between the Caribbean pollination study and BC otter study assumed. Do not multiply associations across studies. If raw archives are obtained, independently check eligibility, model and holdout gates.
