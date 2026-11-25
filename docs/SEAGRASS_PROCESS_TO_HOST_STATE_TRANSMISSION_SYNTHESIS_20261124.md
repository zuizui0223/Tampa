# Seagrass interactions: process-to-host-state transmission — exploratory integration

**Date:** 2026-11-24  
**Status:** New calculations from published public experimental datasets and source-verified reviews. **Not** a new six-family statistical meta-analysis or untested ecological mechanism proof.

## Generalizable biological question

> When a biotic partner changes a proximate process that could protect a seagrass (algal shading, sedimentary sulfide, fixed nitrogen, pollen delivery or herbivore access), under what circumstances does that improvement propagate to aboveground condition, belowground biomass, reproduction and then persistence?

This is stronger than claiming all interspecific effects are positive. It distinguishes the **recipient**, the **measured stage**, the **duration**, the independent replication unit and what was never measured. *Meta-analysis must pair process and plant outcomes within the same intervention before inferring transmission.* A result with only proximal changes is **not** a plant-resilience estimate.

| Published interaction system | Evidence for partner --> process | Partner --> host quantitative state | Time-to-persistence | What is not justified |
| --- | --- | --- | --- | --- |
| ZEN *Zostera* global grazer deterrent (Duffy et al. 2015) | 600 plots, 15 sites, grass-grazer deterrent suppresses plot grazer biomass and increases epiphyte chl a | Source CSV has no plant biomass/cover/survival outcome | None in this file | Grazer effect inferred as guaranteed plant biomass gain |
| *Zostera noltei* x lucinid × organic inputs (van der Geest et al. 2020) | F_sulfide drops with clam addition (published P=.048), despite high organic-load induced sulfide stress | Direct rhizome biomass clam effect not supported (published P=.80); OM decreases rhizome biomass P=.048 | 50-day endpoints, no annual survival | A statistically proven clam×organic stress interaction or rhizome carbohydrate buffering |
| *Posidonia oceanica* nitrogen fixation (Mohr et al. 2021) | Original measured root-piece fixation and plant-level 2016 season contrast | Article reports up to ~20% fixed N transferred to leaves in 24 h; not a 2016 within-plant survival trial | None | Light-driven carbon-cost switch, seasonal causal N manipulation |
| *Thalassia* animal pollination (van Tussenbroek et al. 2016) | Aquarium pollination and animal pollen transport | Some reproductive readouts published, but no Tampa pollen/fruit measurements | No annual meadow fate | New discovery of zoobenthophily or climate-varying pollinator need |
| Akumal rhodoliths x turtles (van Tussenbroek et al. 2024) | Sediment accumulation inside natural beds lower than outside; conditional protection in original paper | Original site/plot seagrass responses in published article | No globally matched trend | Universal algae facilitation or equivalence to Charlotte algae GIS |
| Otter/crab/mesograzer network; invasive Batillaria/Gracilaria (2013–2026) | Food-web and attachment pathways in original experiments | Plant and invertebrate recipients can be affected in **opposite directions** | Site-specific, not global | A single shared beneficial interaction sign |

## A. Original global 15-site grazer experiment — actual reanalysis

Full original source CSV checksum SHA256 `5a97763735a22076eac25a86736c50cb12611a529c5e233941fbc3a73ad4c6ae`. Published experimental design: 15 sites, 40 randomized plots/site, 10 plots in each D±×N± treatment. Public original CSV source: https://www.bco-dmo.org/dataset/659737.

**Source metadata units verified:** `chla_per_Zostera`: epiphyte chlorophyll a µg/g eelgrass blade; `grazer_bmass_per_g`: BCO-DMO defines this despite its name as **total mesograzer biomass in grams**. D+ is *grazer deterrent* and N+ is fertilization.

- D+ versus D−, equal-site geometric ratio of epiphyte chl a: **1.2747**; site-bootstrap CI **[1.0549, 1.7008]**, 12/15 sites positive (post-hoc log cell-mean analysis).
- D+ versus D−, equal-site geometric ratio of grazer biomass: **0.7923**, interval **[0.6482, 0.9677]**.
- N+ versus N−, epiphyte chl a ratio **1.0434 [0.9416, 1.1539]**; D×N ratio of ratios **0.9021 [0.7030, 1.1610]**.
- Raw difference is dominated by VA: original-scale chl a mean +141.81 µg/g, but leave-VA-out only +26.97 µg/g. The **post-outcome** log ratio leave-one-site-out range is **1.1337–1.3237**, so direction is not unique to VA but effect magnitude is sensitive to scale. The original 2015 authors had already established this general effect.
- Local site-level grazer effect temperature screen: Pearson r **+0.5294** at 15 sites (LOO **0.4659–0.6118**), raw two-sided label-permutation p **0.0461**, **three-moderator maxT familywise p=0.1408**. Salinity **r=−0.216 (adjusted p=0.808)**, site grazer richness **r=+0.160 (adjusted p=0.917)**. Temperature was NOT manipulated, variables/analysis were selected post-hoc, and the original 2015 paper already evaluated biodiversity/environment. This supports **hypothesis-generation only**.

Source-frozen files: `results/zen_15site_mesograzer_exploratory_verified_20261124.json` and `results/zen_15site_moderator_posthoc_verified_20261124.json`. Reproducibility: `analysis/118_zen_15site_mesograzer_factorial.py`, `analysis/125_zen_site_moderator_posthoc_robustness.py` and dedicated CI.

## B. Posidonia nitrogen-fixing root endophyte — plant instead of root-piece units

Original source: Mohr et al. *Nature* (2021), DOI 10.1038/s41586-021-04063-4; Source Data Fig2 Panel a XLSX digest `877242abb476cb2d933048778037f8eaf53435e346be42adf327d4af75c7156b`.

The Figure 2 workbook **changes to a separate microbiome panel at row 30**. Previously treating all rows as N2 fixation failed source schema QC; the working source-gated analysis isolates root-piece fixation in rows 5–29 and excludes microbiome metadata/data beginning at row 30. There are **170 root-piece values from 31 labelled plants** in six sampling campaigns, not 170 independent plants. Zeros are retained as reported.

| Campaign | Plants | Root-piece readings | Mean of independent plant means (µmol N gDW^-1 day^-1) |
| --- | ---: | ---: | ---: |
| April 2016 | 5 | 23 | 0.001999 |
| May 2015 | 8 | 22 | 0.005846 |
| May 2017 | 3 | 15 | 0.000389 |
| June 2014 | 6 | 37 | 0.433321 |
| August 2016 | 6 | 61 | 0.370853 |
| September 2018 | 3 | 12 | 0.420225 |

The **2016 April–August** contrast of unmatched plant mean rates is **+0.36885 µmol N gDW^-1 day^-1**, with an **exploratory plant-resampling interval [0.14808, 0.60975]**; 5 distinct April plants and 6 distinct August plants, *not repeated measures of the same plants*. This reaggregation supports the previously published late-summer seasonal activity pattern, not a novel mechanism or randomized light effect. Other campaign differences are confounded with year and season. The independent-unit correction is critical if building a downstream quantitative synthesis.

Verified result: `results/posidonia_n2_plant_campaign_exploratory_verified_20261124.json`; code `analysis/124_posidonia_n2_plant_campaign_reaggregation.py`.

## C. Published field lucinid experiment — proximal protection did not translate to rhizome mass on a 50-day scale

van der Geest et al. (2020), https://doi.org/10.3389/fmars.2020.00011, 4 factorial treatments C,L,OM,L+OM, each n=6 field plots, reported table and original statistical tests.

- Leaf sediment-derived sulfide fraction (%): **20.3, 19.1, 25.3, 22.3**; clam effect P=.048. The absolute clam mean contrasts are −1.2 percentage points without OM and −3.0 with OM, but the original authors **did not find a significant interaction**.
- Rhizome biomass (g dry m^-2): **65.9,70.4,48.4,48.8**; clam main effect P=.80, OM main effect P=.048.
- This **does not prove that stress protection never causes growth benefits**; it reveals different endpoints can have different sensitivity and time horizons in one field experiment.
- Raw 2012 and 2020 Dryad workbook APIs returned 401 in the automated GitHub runtime; published treatment-mean arithmetic is not mislabeled as raw experimental reanalysis.

## D. Synthesis and novelty filter

The difference between **buffering a proximal process** and **improving the host's quantitative state** is an empirical contrast in the 2020 field paper and a crucial missing link in the ZEN CSV. It has been studied before; it is not the first demonstration of such a conceptual separation.

**Potential new cross-system meta estimand:** For each independent published factorial experiment *with both a proximal stress and plant endpoint measured*, calculate a partner effect on each endpoint in its proper units, then test whether the partner effect on the stress predicts the partner effect on **plant biomass/shoots/reproduction**, conditional on stress context and follow-up duration. Use hierarchical random effects for article/experiment/site and shared controls. **Do not pool pollen counts with grazer biomass as if they shared a universal unit.** If trials have only one endpoint, report stage-specific missingness; don't impute benefit to later stages. Ecosystem recipient identity (seagrass vs invertebrate biodiversity) is an explicit effect moderator.

**Current status:** 6 families indexed, one original multi-site experiment fully reaggregated, a plant-unit isotope dataset reaggregated, one published 2×2 field factorial summarized, other families remain original literature/limited source preflights. **No matched multi-experiment meta effect has been estimated.** Tampa's prospective rhizome TNC remains separate and unmeasured.
