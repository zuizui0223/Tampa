# Global seagrass macroecology: measurement coupling and repeat-year eligibility (2026-11-24)

## Purpose
Start an independent **global macroecological** analysis connected to Tampa's main biological question: ecological foundation-species states are multidimensional. The global extension first asks whether measures of biomass, cover and shoot density are **co-reported in the same observation**, and whether the apparent year dimension contains repeated geocoordinates/genus within individual studies.

This is intentionally **NOT** an attempt to resume frozen external Tampa early-warning predictive validation. The original SeagrassNet USA/Canada archive response was already partly opened under a terminal no-rescue contract; this project does not relabel that archive as response-unseen. No new Tampa fit, refit of any Tampa four-year loss endpoint or journal submission results.

## Original global dataset
- Strydom et al. (2021), *Global database of key seagrass structure, biomass and production variables*, PANGAEA https://doi.org/10.1594/PANGAEA.929968, CC-BY-4.0; publication Strydom et al. (2023), ESSD https://doi.org/10.5194/essd-15-511-2023.
- 2025-05-06 metadata correction to some longitudes is acknowledged. Download live source text and record exact SHA256, columns, observation count, number of independent publications, coverage of genera and bioregions.
- The 2023 publication describes **14,271 extracted data points from 390 papers** and 11 biological measures. That is a literature extraction set, **not a 14,271-location long-term monitoring panel**.
- A 2025 *Journal of Biogeography* article (DOI https://doi.org/10.1111/jbi.70041) has already modeled total biomass, total NPP, shoot density and cover across seagrass genera, life histories and geography. **Do not claim a new global mean or generic life-history gradient**.

## Additional independent source-quality warning (not a result of this PR)

A separate public assembly project [coastal-crawler Strydom README](https://github.com/kevinqnb/coastal-crawler/blob/main/data/compilations/strydom-seagrass/README.md) reports **6,658 original table rows, 14,266 nonblank measurement cells, 12 genera, 6 bioregions and 405 raw Reference strings** for the revised 2025-05-06 source. The 2023 peer-reviewed data-descriptor discusses **14,271 data points in 390 publications**. These are not interchangeable denominators: raw reference strings can differ from articles and reported point counts can differ between version/document definitions. The independent assembly flags **283 rows belonging to exact duplicate groups**, 13 rows with missing observation year, and malformed bibliography strings apparently produced by spreadsheet auto-fill. Its findings are *contextual crosschecks only*, not the output or validation of our new CI. The current PR independently counts source rows, exact duplicates and raw references and must keep those categories separate.

Another 2025 *Journal of Biogeography* global analysis (https://doi.org/10.1111/jbi.70041) already examined cover, shoot density, total biomass/NPP and life-history/environmental gradients. The more defensible new quantitative axis (if genuinely paired rows are sufficient) would be *above- versus below-ground biomass allocation coupling and its cross-biome heterogeneity*, but this must not be relabeled physiological reserve TNC or a tested longitudinal persistence mechanism.

## Four pre-result eligibility questions
1. **Observation pairing:** how many **individual rows** contain both positive aboveground and positive belowground dry biomass; how many studies and genera contribute? This is necessary for a valid per-same-record allocation ratio.
2. **Quantitative indicator overlap:** how many *same rows* jointly measure shoot density+cover or cover+belowground biomass? Do not join values from different articles or same approximate geocoordinate as though they were paired field quadrats.
3. **Repeat-year candidate survey design:** among identical publication/reference+latitude+longitude+genus, how many groups have records in >=2 different years? These are **only candidate repeated publication-site records**, not certified fixed plots.
4. **Structural coverage and bias:** genus/bioregion distribution, cover positivity (whether any 0/negative cover is actually reported), missing coordinates/year/measurements and study clusters. Positive-covered meadows cannot estimate true species absence or Tampa-style 1→0 transitions.

## Analytic decision gates (report truth even if disappointing)
- If >=100 strictly paired positive above/below records from >=10 papers and >=3 genera, a **descriptive** macro-level below/above allocation landscape can be computed by genus and bioregion. A clustered inferential model requires additional independent-study support and must not turn static allocation into a reserve/causality result.
- If within-publication multi-year geocoordinate/genus support is poor or marks cannot be verified, **stop** claims that PANGAEA supports true longitudinal state-decoupling. Report it as a cross-sectional study compilation rather than forcing temporal slopes.
- If adequate paired cover+biomass or shoot+cover exists, assess *quantitative indicator coupling* (not presence vs absence), controlling study identity and genus when feasible. Avoid unverified record-to-record pairing.
- For a truly longitudinal macro test of Tampa's original phenomenon, obtain another field monitoring dataset with stable permanent mark identity, repeated quantitative cover and explicit sampled zeros. Holdout status must be reported honestly; already opened data cannot become untouched validation.

## Reproducibility
`analysis/114_global_seagrass_929968_feasibility.py` uses the source PANGAEA text export, checks actual header/row validity, tallies same-row paired measures and reports study-site-year candidates. `validation/test_global_seagrass_929968_feasibility.py` contains deterministic source-independent parsing tests, and the dedicated GitHub workflow archives the JSON result only after original source fetch succeeds.

**No macroecological coefficient is pre-claimed.** Results must come from actual publicly retrieved file, not the PANGAEA catalogue numbers alone.
