# ZEN2: habitat structure persists across years, but trophic outcomes do not follow from previous-year state alone

24 November 2026 — exploratory, post-hoc, source-locked ecological analysis. Not an independent meta-analysis, an untouched forecasting holdout, or a new controlled ecological mechanism.

## Independent original source provenance

The 2014 ZEN2 survey has 50 subsite summaries in 25 region codes (original SHA256 c2af785e48aa76f88834e6c96ab69f49f85feb0918a89f9ec0585680cb170034), DOI https://doi.org/10.26008/1912/bco-dmo.712069.1. The 2015 ZEN2 tether experiment covers 17 experimental sites and 2,666 tethered animals (SHA256 3de12972e709f6a856e60e6d8cbf6fd81cf824edb7d907c453301e3e42d596fb), DOI https://doi.org/10.26008/1912/bco-dmo.724015.2.

Source-only latitude/longitude matching was executed before looking at the new crossyear associations. It selected the **closest original 2014 subsite** with the SAME source region code and at most 25 km from the 2015 site. This yields 14/17 matches (BB, CR, FI, FR, JN, JS, MX, NC, OR, QU, SD, SF, VA, WA). GA has no predecessor. KOA and KOB have two distinguishable geographic locations, but both share the 2014 code KO, so were excluded from primary one-to-one matching. Six other 2014 paired-region A/B subsites lie more than 25 km apart from the 2015 site (including MX ~161 km, WA ~172 km), so averaging all A/B site-code records would be a false local match.

**No same permanent plot identity is inferred.** The 2014 subsites were independent summaries and the 2015 plots were newly sampled experimental units.

## Empirical exploratory result 1 — persistence in the physical shoot-density rank

Spearman rho between source 2014 nearest-subsite Zostera shoots per square metre and 2015 ambient original experimental pre-thinning shoots per square metre was **+0.828571** across the 14 eligible localities. The site-label two-sided 20,000-permutation p value was **0.000650**. Leave-one-site-out rho ranged **+0.8022 to +0.9066**.

A stricter 5-km geographic condition eliminates BB and retains 13 sites: rho **+0.8022**, 5,000-permutation p **0.000800**. This is evidence of stable **spatial relative ranking** of standing shoots across two nearby surveys in consecutive years; it does NOT show that individual plants survived or that each patch's absolute biomass remained unchanged.

## Empirical exploratory result 2 — no support for previous-year state predicting next-year predation contrasts

One site is the independent unit. Only 2014 prior measured shoot density or periphyton and one of two 2015 site risk effects was compared. Four post-hoc comparisons were jointly corrected with a fixed-site 20,000-shuffle maxT family. The 2015 outcome series had already been opened in PR #171 before this secondary analysis; adjusted p values cannot make it prospective.

| Prior 2014 feature | Later 2015 24h tether risk contrast | Spearman rho | MaxT familywise p |
| --- | --- | ---: | ---: |
| Shoot density | Edge minus interior | −0.382 | 0.571 |
| Shoot density | 80% thinning minus ambient | −0.068 | 0.999 |
| Standardized periphyton | Edge minus interior | +0.196 | 0.948 |
| Standardized periphyton | 80% thinning minus ambient | −0.355 | 0.644 |

None of these was supported. This **does not prove trophic interaction is intrinsically unstable**: the response was binary 24-hour tether mortality, with a high baseline risk and saturation at many sites, different predator communities, and only 14 geographical replicates. The 2014 periphyton summary and 2015 epibiont biomass measure need not capture exactly the same biological compartment.

## Original literature novelty boundary and conservation relevance

Hovel et al. (2021), Ecology DOI https://doi.org/10.1002/ecy.3316, already tested same-year habitat structure, epibiont biomass and alternative crustacean prey as moderators of patch-edge predation and found geographically varying edge effects. Repeating that claim is not a new discovery.

The distinct **crossyear question** here is whether a foundation-species structural state is a persistent enough local signature to indicate future trophic-function status. The observed stable rank of shoots is encouraging for monitoring spatial habitat state. The lack of supported correspondence to later predation contrasts warns against interpreting seagrass structural condition by itself as a proven proxy for consumer refuge or ecosystem function.

Together with Tampa's own independently observed decoupling of measured vegetative axes, this motivates, but does NOT establish, a larger foundation-species hypothesis: stable habitat signatures can coexist with ecosystem interactions that require different direct measurements.

## Reproducibility

Original source-verified run: https://github.com/zuizui0223/Tampa/actions/runs/45330784453 — all six source and code jobs passed. Raw original source SHA values above were independently checked. Complete numerical outputs, site-code mapping and all per-site values are in:

- results/zen2_2014_2015_geographic_link_verified_20261124.json
- results/zen2_2014_prior_state_2015_trophic_risk_verified_20261124.json

Source analysis: analysis/130_zen2_2014_2015_geographic_link_gate.py and analysis/131_zen2_prior2014_state_later2015_interaction.py. The PR workflow independently re-downloads sources and compares both complete result objects to their archived versions, failing on any drift.

This report is exploratory only; Tampa Paper A and the protected prospective four-bay rhizome TNC measurement contract were not changed.
