# Seagrass structural-state diagnostic (2026-11-25)

## Question
Return to the Tampa meadow-buffering question: do final shoot abundance, aboveground tissue mass, and belowground tissue mass respond in the same direction to biotic interaction and stress? This is an exploratory reanalysis of two previously acquired experiments, not a new independent replication of the Tampa time series. No assumption of a universal order of decline, no measurement of rhizome carbohydrates or individual clone reserves, and no causal transmission coefficient.

## Provenance
Artifact 14924199338 from run 45404388315, ZIP SHA256 cb072af9f5b731120108a25360f27f8e4438d5beaa97bf2e321aaf35d755d149 verified locally. The three exact source-member hashes are fixed in analysis/172_seagrass_structural_state_diagnostic.py. Executed locally on original source bytes; all schema/identity checks passed. Prior head f3fa22b9b62dbad962dcfa5019828b5a7dabf3dc returned 21 successful PR runs on the first page; that page did not include the specific analysis/171 workflow, so no claim that 171 independently passed.

## Field experiment: van der Geest et al. 2020
Paper DOI 10.3389/fmars.2020.00011; data DOI 10.5061/dryad.jm63xsj6n. Table 9: 24 unique plots, 6 blocks, each of four OM x clam assignments once per block. All 24 have positive shoot number and leaf, rhizome and root mass per core. Total belowground = rhizome + root, total mass = belowground + leaf. Core mass divided by shoot number is a structural index, not tissue assigned to a clone/ramet and not a carbohydrate concentration.

Within each block and stratum of the other factorial treatment, compute log(treatment/control); equal mean across twelve contrasts, equivalently mean of six block-average effects. Exact identity log mass ratio = log shoot-count ratio + log mass-per-shoot ratio holds for each pair. Conditional randomization uses all 2^12 within-pair label swaps, conditional on the other factor's assignment and assuming unrestricted random allocation of four combinations within each block as in the published design. This is a sharp-null diagnostic rather than a mixed-effects-model replication. Holm across eleven exploratory endpoints within each manipulation; covariance calculated from the six block-average effect vectors. Leave-one-block-out ranges are sensitivity of point estimates, not confidence intervals.

| Endpoint | OM geometric ratio | Clam geometric ratio |
|---|---:|---:|
| shoot count | .895170585 | 1.180648458 |
| leaf mass | .889532738 | .939515507 |
| rhizome mass | .709677617 | 1.006523380 |
| root mass | .751975325 | .839474753 |
| combined belowground mass | .731777391 | .921033772 |
| total mass | .802210030 | .917707545 |
| leaf mass per shoot | .993701930 | .795762278 |
| rhizome mass per shoot | .792784782 | .852517423 |
| root mass per shoot | .840035786 | .711028543 |
| belowground mass per shoot | .817472562 | .780108394 |
| total mass per shoot | .896153252 | .777291105 |

Clam addition: shoot-count ratio 1.18065, belowground mass per shoot .78011, total mass per shoot .77729. Belowground per-shoot ratio <1 in all six block-average contrasts; leave-one-block-out range .76515–.80546. Shoot ratio range 1.14026–1.31336. However the sharp-null permutation p=.16699 for belowground mass per shoot; leaf per shoot p=.03955 but Holm p=.43506. No endpoint survives Holm for either manipulation. Do not claim demonstrated density increases or harmful clam effects, nor infer compensation or causal competition. OM rhizome mass ratio .70968 (unadjusted p=.08154, Holm=.89697), rhizome per shoot .79278 (LOO .70886–.83941). The original paper already found an adverse OM effect on rhizome biomass with its mixed model (p=.048) and no significant shoot-density effect; the new diagnostic estimates the structural per-shoot contrast and checks its robustness without substituting the exploratory test for the original analysis.

## Laboratory experiment: van der Heide et al. 2012
DOI 10.1126/science.1219973; Dryad 10.5061/dryad.210mp; Zenodo 4958629. Zostera sheet, 20 host-bearing columns, five each per factorial treatment. Use reported Shoot_biomass as aboveground mass, sum Rhizome_bioamss and Root_biomass. Ratios of arithmetic means, no independent heat or temporal inference, one shared water basin.

| Tissue | Sulfide added vs control, no clam | Sulfide added vs control, clam |
|---|---:|---:|
| shoot mass | .507887136 | .710996395 |
| rhizome | 1.027516217 | 1.015128915 |
| root | .765294344 | .917028606 |
| belowground | .864941158 | .948329197 |
| total | .770832113 | .878739098 |

The direction of the most affected tissue differs from the 2020 field experiment. This is not a significant cross-study difference: sulfide directly added in laboratory vs organic loading in field, different treatment and exposure, no independent estimate of temporal order. The original papers already report tissue-specific results; new value is placing them in a consistent state-variable diagnostic with explicit denominator accounting.

## Independent replication stop: Donaher et al. 2021
DOI 10.1002/ecs2.3804, Dryad 10.5061/dryad.9cnp5hqh7. Exp1_BiomassCores_All.xlsx has 192 unique plot/year/month/species rows; the metadata labels Shoot Density shoots/cm2. One literal N is nonnumeric. July 2019 Halodule density values in complete mass/density rows range 6.0000–82.0000, whereas May range 254.65–7639.44. This suggests a possible scale/unit discrepancy but is not proof; no unit correction applied. July Zostera has five complete records with recorded zero density and positive aboveground mass. Eighty plot/year/month groups contain identical nonmissing belowground mass in both species rows; original article reports combined-species belowground biomass, so no allocation by species or double counting. Stop the per-shoot replication until units/zero-denominator records are resolved. This does not invalidate the previously extracted epiphyte and aboveground-mass endpoint comparison, which does not use shoot density.

## Interpretation and status
Presence and shoot abundance cannot be assumed to report leaf, rhizome or root standing biomass, and a measured response of the interaction partner is not a sufficient proxy for recipient structural state. For Tampa monitoring, motivate paired core-level density and biomass diagnostics, including belowground sampling at a stratified subset of sites, rather than inferring a common decline sequence. No threshold, prediction of loss, causal pathway, or true longitudinal buffering demonstrated by the present analysis. Reanalysis of previously acquired sources only; no new independent study, no pooled meta-effect, no new otter source or pollinator-weight validation. Local source-locked execution successful; independent CI pending. Draft PR #170 only, no merge/submission or Paper A/frozen TNC changes.
