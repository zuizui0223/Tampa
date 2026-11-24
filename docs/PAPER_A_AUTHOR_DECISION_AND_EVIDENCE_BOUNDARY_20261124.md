# Tampa Paper A — author-facing scientific and journal decision (24 November 2026)

**Evidence class:** Editorial/claim-boundary audit. No reanalysis, no changed outcome, no new mechanism and **NOT a submitted manuscript**. This file supplements the author-review artefact built by stacked PR #161 on scientific PR #155.

## Decision in one paragraph

**Keep the 29-year ecological state-axis manuscript together and proceed to author sign-off**, without waiting for the four-bay rhizome-TNC pilot or another retrospective mechanism search. The defensible result is heterogeneous *measured* changes beneath partially persistent *recorded* Thalassia occurrence at 71 permanent transects: Old Tampa Bay mainly plant stature/density, Middle blade stature, Lower within-transect occurrence/abundance and species composition. The post-hoc independent Zostera cover comparison demonstrates a similar binary-versus-quantitative observation structure in a separate species/system. The exploratory strict year-forward recorded-non-detection comparison has information beyond a **specific regularized node-ID** reference but provides neither independent predictive confirmation nor true extinction/hysteresis evidence. The journal choice and final author assertions are **unresolved human decisions**.

## Paper-level supported claims and exact source identities

| Claim | Primary source/status | Safe number or statement | Prohibited extension |
| --- | --- | --- | --- |
| Permanent-monitoring design | Original Event/Occurrence/eMoF reconstruction, main frozen source commit `6c567beff95ea04f0e397101befb49d5233ace8f` | 1997–2025; 71 transects; 1497 visits; 1480 node-years | 1480 independent experiments |
| Different state axes by bay | `results/current_validation_v2.json` in PR #155 | Old blade **−1.093 mm/yr**, shoots **−38.30 m−2/yr**; Middle blade **−0.405 mm/yr**; Lower focal frequency **−0.01277/yr** | One serial condition→thinning→loss mechanism |
| Community reorganization | Same source | Lower *Thalassia* and *Syringodium* frequency decrease, *Halodule* frequency increases | Experimental competition or newly established colonization |
| External transfer | `results/nps_persistent_cover_v1.json`, post-hoc | Zostera recorded 240/240, cover slope **−1.52 percentage points/yr**, heterogeneous sites | Untouched external prospective validation or universal seagrass decline |
| Quantitative early-warning candidate | `results/warning_reporting_metrics_v1.json`; PR #155 | For 570 scored source-positive node-years/19 recorded losses, L2 node-baseline AUC **0.67055** versus augmented **0.73636**, mean annual log loss **0.148268→0.147230**; adverse 2016 | Extinction forecast, verified intervention threshold, generic causal early warning |
| Previous-positive mark coverage | `results/early_warning_fixed_mark_overlap_verified_v1.json`; PR #155 | Among **24** node-year recorded losses, **17** revisited at least one previously positive mark; 7 did not; 14/19 in scored subset revisited | Same microquadrat, perfect detection or plant mortality |
| Same-year source revisit capability | Separate source-only PR #168, successful run #45246392618, frozen `results/pinned_within_year_repeat_eligibility_verified_20261124.json` | 17 node-years with two eligible parent visits across 29 years; 222 shared mark IDs summed across those groups; **0** pairs <=30 nominal days; gaps **80–334 days** | This **different** 17 is NOT the 17/24 recorded-loss mark revisit numerator; these counts cannot be pooled. Source dates are not field-time verified. |
| Re-recording fragility | Separate exploratory PRs #166/#167 | Observed 30/83 vs 64/497 next-year re-non-detection | Genuine biological recovery debt, mortality, a fitted detection rate or validated additional watchlist |

**The two different '17' counts are especially easy to confuse.** PR #155's 17/24 refers to *next-year overlap of previously positive sampled mark IDs in observed-loss node-year transitions*. PR #168's 17 refers to *same-calendar-year repeated eligible parent transect visits*. Their cohorts, denominators and ecological meanings are different. PR #168 does not refit PR #155 and is not material evidence of the risk model's predictive validity.

## Novelty boundary, independently checked 24 November 2026

- Rising, Bulling & Sweet (2026), iScience 29:114871, DOI **10.1016/j.isci.2026.114871**: 500-study/34-expert monitoring synthesis *already* recommends integrating multiple biological levels. Do **not** claim Tampa invented multi-level seagrass monitoring.
- Peng et al. (2026), Nature 655:663–669, DOI **10.1038/s41586-026-10704-3**: global 10-m map *already* separates mapped extent loss from dense-to-sparse cover degradation. Do **not** claim Tampa first demonstrated that presence maps hide degradation.
- **Tampa's empirical increment:** 29 years of fixed-transect *species-specific frequency, Braun-Blanquet, blade length, shoot density and co-occurring community data*, with **geographically nonuniform measured state-axis trends** and a narrowly bounded annual observed-state forecast.
- The binary presence variable is **derived from positive focal frequency** (presence = one if frequency >0). The positive-frequency/presence contrast by itself is partly deterministic thresholding. Independently measured shoot/leaf/composition trajectories carry the nontrivial ecological evidence.
- The NPS Zostera comparison uses already-opened data. Its directional heterogeneity, including increasing cover at Moriches Bay, must remain explicit.

## Journal-fit decision: no automatic acceptance

### First candidate: *Estuaries and Coasts* (CERF)

Official live scope on 24 Nov 2026 (https://www.cerf.science/journal) favors novel coastal findings of **general interest** and explicitly says submissions that are **primarily descriptive or strongly place based fall outside scope**. This paper is not automatically rescued by labeling it a Brief Report. Keep Original Article as the *provisional* first candidate only if the corresponding author is comfortable defending the general state-axis inference beyond one geographic system and accepts desk-rejection risk.

**Best rationale for CERF:** rather than reporting Tampa acreage changes, the study tests whether one foundation species' multidimensional state changes congruently under fixed monitoring; finds bay-specific divergences and a separate-species, separate-monitoring-system post-hoc parallel; and audits whether quantitative state has recorded non-detection information when fixed node identities are controlled. This still cannot claim causality or biological memory.

### Conservation-centered alternative: *Aquatic Conservation: Marine and Freshwater Ecosystems* (Wiley)

Official live scope on 24 Nov 2026 (https://onlinelibrary.wiley.com/page/journal/10990755/homepage/productinformation.html) explicitly considers **local-to-global aquatic conservation research**. This is a potentially better substantive fit for *monitoring triage and interpretation of existing coastal surveillance*, provided the abstract and discussion retain the distinction between **targeted verification** and a validated management intervention. If the corresponding author chooses this journal, rebuild formatting from its then-current instructions; do **not** submit the CERF-formatted ZIP unchanged.

**Recommendation for author decision:** If minimizing scope-based desk rejection matters more than first-shot journal positioning, select *Aquatic Conservation*. If retaining *Estuaries and Coasts* first, acknowledge the explicit scope risk and make the transferable state-axis hypothesis—not Tampa's local decline—the cover-letter opening argument. Neither outcome is guaranteed.

## Three scientific wording points to sign off before final export

1. **Temporal precedence / warning:** Terms such as “presence is a lagging indicator”, “early diagnosis” or “detect late” should be interpreted as information loss from coarsening, not a proven universal leaf→frequency→presence temporal ordering. Existing cross-lag test does **not** validate that sequence. Prefer: “Presence alone cannot identify concurrent change in finer measured state.”
2. **Recorded state versus biology:** Next-year observed non-detection is not mortality. The **source-positive-meter-mark revisit** audit reduces one omission explanation but cannot identify true absence. The separate same-year 17-group source audit shows that all nominal repeat gaps were at least 80 days; it does not provide a closed-occupancy detection-calibration panel. This belongs in Supplementary limitations only, unless editorial space permits one sentence.
3. **Community context versus ecosystem function:** Lower Tampa Bay's rising Halodule frequency and the pooled mixed-patch occupancy retention do **not** establish competitive replacement, functional equivalence, improved biomass, or causal biodiversity insurance. The node-saturated pooled-mixture interval crosses zero.

## Figure-to-claim map (existing frozen figure contracts)

- **Figure 1:** 71 locations and stable node-identity versus year descriptive shares — *different variability structures, not causal ecological memory*.
- **Figure 2:** 2016–2025 Old/Middle/Lower/Boca quantified condition axes — *ecological primary*.
- **Figure 3A:** Lower species-frequency reorganization — *not competition*.
- **Figure 3B:** NPS Zostera cover under saturated observed presence — *post-hoc external comparison*.
- **Figure 4:** Observed-state early-warning from a spatial and regularized node baseline, including adverse 2016 — *secondary predictive monitoring candidate, not external validation*.

## Files built, and human gate still missing

PR #155 scientific head `ea51e975e8aae2af0312442f28bd497a82bc41ae` has 20/20 source scientific CI runs PASS reported in its own provenance; PR #161 is a stacked draft on that exact head. PR #161's successful [GitHub Actions #39906448761](https://github.com/zuizui0223/Tampa/actions/runs/39906448761) generated a **non-submitted** author-review package (main Word + proof PDF, SI Word/PDF, EPS/TIFF plates, S1–S12 tables, cover-letter template). The generated package was certified by its software/source/layout checks but was **not** verified as an accepted submission. No manuscript result or numeric endpoint is changed in this note.

Before submission, a human corresponding author must: confirm the target journal; confirm all actual authors, affiliations and contributions; confirm the source's licensing and any required monitoring permissions/ethics; approve acknowledgements, funding and conflicts; visually inspect all figures and page proofs; verify the current journal formatting and SI policy; approve the manuscript/SI and cover letter; freeze a public submission citation/release or DOI; and explicitly authorize actual submission. These declarations must not be filled by inference.

## Decision status

**READY FOR SCIENTIFIC AUTHOR REVIEW — NOT READY TO SUBMIT.** The ecological retrospective first paper can move forward without new TNC or detector measurements. Those measurements belong to a distinct prospective mechanism paper. PRs #166–#168 are useful *observation-process limitations/design* notes; do not fold their illustrative detection parameters into Paper A's biological Results.
