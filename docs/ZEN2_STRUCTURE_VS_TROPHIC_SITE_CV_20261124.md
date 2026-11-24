# ZEN2 predictive comparison: prior-year structure versus subsequent trophic interaction

**24 November 2026. Status: source-frozen exploratory analysis, response already opened.** This is **not** untouched external validation, not a new experiment, and not evidence of a causally unstable food web. It does not modify Tampa Paper A or the protected prospective TNC study.

## Ecological question and datasets

Does the previous year's independently measured eelgrass habitat structure carry **usable predictive information** about the next year's plant structural state, and is that same prior state also an adequate proxy for an experimentally measured *mesograzer predator-risk contrast*?

The first target is a direct biological state (shoots/m²); the next two are the original 2015 Hovel et al. 2021 site-specific *tethered-prey predation risk differences*, not free-living consumer survival. These are different endpoints with different observation errors; predictive comparisons alone do not prove ecological mechanisms or intrinsic function turnover.

Two published original BCO-DMO datasets were source-hashed and kept separate:

- 2014 observational seagrass 50 subsites in 25 region codes: DOI https://doi.org/10.26008/1912/bco-dmo.712069.1, SHA256 **c2af785e48aa76f88834e6c96ab69f49f85feb0918a89f9ec0585680cb170034**.
- 2015 experimental 17 sites / 2,666 tethered prey records: DOI https://doi.org/10.26008/1912/bco-dmo.724015.2, SHA256 **3de12972e709f6a856e60e6d8cbf6fd81cf824edb7d907c453301e3e42d596fb**.

The source-only geographically selected nearest 2014 subsite within 25 km, same source region code, yields **14 independently labelled site contexts**, 13 within 5 km. This is not an exact permanent-plot survey. Locations had already been inspected and outcomes were opened before the new predictive test. The map is fixed in `results/zen2_2014_2015_geographic_link_verified_20261124.json`.

## Geographical/latitude challenge to the strong crossyear rank

Before comparing prediction errors, sensitivity to coarse biogeography was quantified from the same source-frozen 14 sites. Site rankings for shoot density in 2014 vs 2015:

| Domain | Matched localities | Crossyear Spearman rho |
| --- | ---: | ---: |
| Pacific (both Eastern and Western Pacific) | 8 | **+0.929** |
| Atlantic + Mediterranean | 6 | +0.371 |
| Pooled | 14 | **+0.829** |

Partial Spearman rank correlation conditional on latitude rank is **+0.824**. A **20,000-draw permutation restricted to original Pacific vs Atlantic/Mediterranean membership**, which retains *between-basin* scale differences but disrupts within-basin identities, gives **two-sided p=0.00125**. This does **not** account for all coastline spatial autocorrelation, method differences, nor independent validation. It was performed **after** the pooled positive rank correlation had already been seen. Original-code result with source and full site list is pinned at `results/zen2_2014_2015_basin_latitude_sensitivity_verified_20261124.json`.

## Leave-one-geographic-site-out predictive comparison (same 14 site labels)

For each candidate, hold out exactly **one matched regional site**. Train an **intercept plus single log(1+x) previous-year habitat predictor** on the 13 other sites. The reference prediction is **the mean of those 13 training site outcomes** on the identical outcome scale, refitted in each fold. For plant shoot density, predict log(1 + 2015 shoots/m²); for 2015 tethered risk effects, retain the original site-mean risk-difference scale (fractions). Thus all predictor models and their own references use a **same-outcome, same-unit** comparison. The identical site count prevents treating 2,666 animal trials as independent ecosystems.

Site-LOOCV skill is `1 - Σ(model prediction error²) / Σ(fold-reference prediction error²)`. Positive means improvement over fold-specific training mean; negative means worse. **This is within one published study and was designed after outcomes had been opened**, not an independent or prospective predictive test.

| Previous 2014 predictor | Next 2015 outcome | Geographically held-out n | LOOCV R² vs fold mean | Model / reference RMSE | Held-out sites with smaller absolute error |
| --- | --- | ---: | ---: | ---: | ---: |
| **Shoot density** | **Shoot density** (log1p scale) | **14** | **+0.6936** | **0.6686 / 1.2079** | **11/14** |
| Shoot density | Edge minus patch interior tether predation risk | 14 | −0.0057 | 0.0540 / 0.0539 | 8/14 |
| Shoot density | 80%-thinning minus ambient tether risk | 14 | −0.4133 | 0.0961 / 0.0809 | 6/14 |
| Standardized periphyton | Edge minus interior tether risk | 14 | −0.2086 | 0.0592 / 0.0539 | 6/14 |
| Standardized periphyton | 80%-thinning minus ambient tether risk | 14 | −0.0336 | 0.0822 / 0.0809 | 6/14 |

RMSE scales are **outcome-specific**: one log(1+shoot density) unit versus **unit fractions** of predation; do not compare absolute RMSE across outcomes. The dimensionless within-outcome LOOCV R² is more relevant.

A **5-km-only geographic sensitivity**, excluding BB, retained **13 localities**: shoot density `R²=+0.6943`, whereas 80%-thinning risk `R²=−0.4145`. This was not optimized to improve or rescue either endpoint.

**Outcome and interpretation:** Spatial differences in the vegetative standing stock are preserved and can be predicted, in a within-study one-year local context, much better than the 2015 tethering-risk contrasts. **This alone does not prove that predation functions are more temporally variable**: there is no 2014 predation endpoint to measure true interaction turnover, the 2015 assay has a high binary-ceiling, no demonstrated comparison of measurement reliability across target types, and the site sample is tiny. A complex multivariable predator model could conceivably change the risk skill. Original Hovel et al. (2021), DOI https://doi.org/10.1002/ecy.3316, already analyzed contemporaneous source habitat and predation effects.

### Ecological hypothesis, not confirmed mechanism

A foundation species' **spatially persistent structure may be an inadequate surrogate for its biodiversity and trophic functions**. Conserving or remotely mapping shoots/cover may identify stable habitat state without identifying actual predation risk or consumer shelter. A publishable, general claim needs repeated, independent sites and times with **same plot** host canopy (leaf/3D architecture, shoots, above/below biomass), **free-moving** mesograzer fates, predator identities and a direct host-health endpoint. Reanalysis of the two separate 2011/2015 ZEN programs cannot identify a causal bidirectional feedback or canopy-behavior mechanism.

## Provenance, reproducibility and audit status

Original six-job crossyear analysis succeeded at [Actions #45330784453](https://github.com/zuizui0223/Tampa/actions/runs/45330784453). A further seven-job geographic robustness run succeeded at [#45331299618](https://github.com/zuizui0223/Tampa/actions/runs/45331299618). **Eight jobs including the fully source-frozen LOOCV test succeeded at [#45332093895](https://github.com/zuizui0223/Tampa/actions/runs/45332093895)**.

- Site/response pairing code: `analysis/130_zen2_2014_2015_geographic_link_gate.py` and `analysis/131_zen2_prior2014_state_later2015_interaction.py`.
- Basin/latitude robustness: `analysis/132_zen2_crossyear_basin_latitude_rank_sensitivity.py`.
- Train-only held-out site estimator: `analysis/133_zen2_crossyear_structure_vs_trophic_site_cv.py`. The CV code has no hyperparameter or phenotype selection inside the held-out fold.
- Canonical results with original source hashes and CI provenance:
  - `results/zen2_2014_2015_basin_latitude_sensitivity_verified_20261124.json`
  - `results/zen2_2014_2015_host_vs_interaction_cv_verified_20261124.json`
- Workflow exact equality checks independently reproduce both full JSON results, not just headline effects. No original 2014/2015 source, Tampa main manuscript, prospective TNC, or prior prediction holdout contract has been modified.

**Decision:** Good enough for **hypothesis generation and methods evidence**, not enough to brand as a new global proof or causal multi-trophic mechanism. Further exploratory modeling within these same 14 localities risks post-hoc overfit; the next decisive dataset should use jointly repeated plant and trophic outcomes.
