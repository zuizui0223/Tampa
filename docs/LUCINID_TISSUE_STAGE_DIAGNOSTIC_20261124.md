# Tissue-stage diagnostic and realized partner biomass, 2026-11-24

## Question and novelty boundary
Maestre et al. (2009), DOI 10.1111/j.1365-2745.2008.01476.x, already distinguished resource and non-resource stress and species traits in refinements of the stress-gradient hypothesis. Chin et al. (2021), DOI 10.1111/1365-2745.13462, already showed context-dependent facilitation, including tissue sulfur and tissue-specific growth. Do not claim the generic idea of stress-specific facilitation or the tissue sulfur reduction as novel. The present exploratory diagnostic separates measured external sulfide, tissue sulfur measures, achieved partner biomass, and host outcomes on identical experimental units, and evaluates incremental within-experiment predictive performance against a context-specific baseline. It is not a formal test against the original community-level SGH.

## Source and checks
Original source artifact 14924199338 (run 45404388315), archive SHA256 cb072af9f5b731120108a25360f27f8e4438d5beaa97bf2e321aaf35d755d149, independently checked. Local execution of analysis/164 equivalent implementation completed on source member hashes pinned in script. No graph digitization or new source values inferred. The prior independent 161/162/163 runs (45405600411 and 45405600631) were still in progress at last check.

## Chin 2021, 48 mesocosms in six complete tank blocks
Use the 2017-11-20 through 2018-01-01 trapezoid time-average of 5/10 cm porewater sulfide means as in 162. Sulfur sheet: 255 records; 25 dead rhizome records have no PctS and one leaf measurement missing; at least one available measurement for each tissue in all 48 units. Average available segment-level PctS to the mesocosm, then equal-weight unit averages. PctS is total tissue sulfur % dry weight, NOT toxic sulfide, isotope-estimated sedimentary sulfide intrusion or an interchangeable metric of external sulfide. No imputation or denominator for dead tissues. Growth definitions as in 162; survivor-conditioned, unlike unit-level change in live shoots.

Percent changes in ratio of arithmetic treatment means:
|context|period-average porewater sulfide|rhizome total S|leaf total S|rhizome elongation|leaf growth|
|---|---:|---:|---:|---:|---:|
|LA|-93.1531|-21.7897|-31.4392|-17.4061|14.1867|
|LS|-95.7328|-37.3314|-33.5559|54.5152|38.6834|
|DA|-92.2802|-27.2178|-25.5431|182.3598|19.3879|
|DS|-95.7215|-37.5656|-35.8044|83.1789|39.1632|

Across 24 clam/no-clam paired tank contrasts, porewater sulfide lower in 24/24, rhizome sulfur lower in 20/24, leaf sulfur lower in 19/24, rhizome growth higher in 19/24. These are dependent contrasts, not independent replication counts. No formal effect transmission efficiency calculated from concentrations with different units and composition. Lower total S may partly reflect tissue dilution/growth, not only reduced intrusion. Effects on tissue and growth cannot establish mediation.

## Held-out tank diagnostic, not external prediction
Construct 24 paired tank-context differences in original host endpoint units (including zero rhizome elongation without adding constants). OLS with four context indicators and no additional intercept. Compare context-only to adding log control/clam ratio of measured period-average sulfide, adding also log residual sulfide, adding two log tissue sulfur ratios, and all four covariates. Train on five tanks / twenty pairs and test all four contexts in remaining tank; six folds, no tuning, same samples for all models. Predict simultaneous host treatment differences using observed process contrasts, not future or untreated-site response. Post-outcome exploratory, no inference that context model is an actual SGH model.

|predictor increment|rhizome RMSE|leaf RMSE|shoot-change RMSE|
|---|---:|---:|---:|
|context only|.08444484|.36883108|.39065227|
|bulk relief|.08473285|.35325705|.40090973|
|bulk relief + residual|.08910442|.37567544|.42883297|
|tissue relief|.11949836|.37456125|.39484799|
|all|.12213251|.37281785|.41513644|

No consistent incremental skill. Models conditional on context, small 6 tanks and potentially noisy/multicollinear predictors; negative predictive result does not show sulfide is biologically unimportant or refute a causal mechanism. Do not generalize across stressors or studies.

## Correction to field intervention interpretation (van der Geest 2020)
Original DOI 10.3389/fmars.2020.00011. Exact Table 7/Table 9 join on six plot keys; 24 plots, six blocks, two organic matter contexts. Count and total clam dry mass must both be retained. The article already reports higher clam flesh dry weight with addition (56% overall), so the previous count-only interpretation of weak realized addition was incomplete. In organic-matter treatment, control/addition clam densities 29/28.333 per core, but clam mass .149295/.232650 g per core (+55.8324%); no-OM mass .0890833/.139615 (+56.7240%). Clam biomass higher in 5/6 blocks in both contexts. Hence similar counts do not imply absence of an achieved biomass intervention; final biomass is not a direct measure of microbial activity or longitudinal exposure.

|organic matter context|count change %|clam biomass %|porewater sulfide %|leaf sedimentary sulfide fraction Fsulfide %|leaf sediment-derived S SS_leaves %|plant total biomass %|
|---|---:|---:|---:|---:|---:|---:|
|none|12.8205|56.7240|300.2005|-5.5614|-2.1352|5.2756|
|addition|-2.2989|55.8324|-38.8181|-11.7320|-7.6977|-23.1694|

No-OM porewater means .08765/.35079 micromolar, so +300% is unstable/near-zero absolute background and should not be interpreted as stress increase; keep absolute values. OM leaf Fsulfide means 25.27798/22.31237%, lower in 5/6 blocks; plant total biomass means 1.51342/1.16277 g, lower in 5/6 blocks. Descriptive directions, no new significant negative host effect. The paper did not establish a significant treatment interaction, and porewater sulfide comparison between OM and L+OM was nonsignificant. Fsulfide is isotope-estimated fraction of leaf S derived from sediment, SS_leaves is sediment-derived S concentration, not Chin total S. No pooling or formal attenuation fraction across non-equivalent variables. The additional diagnostic confirms the field chain includes achieved clam biomass, leaf intrusion and final plant biomass; it does not establish physiological causation.

## Next evidence requirement
For a mechanistic SGH extension, prospectively identify distinct causal routes and comparable endpoints, measure toxic exposure inside host tissue, establish partner density/biomass/function and host state, then compare out-of-study performance of stress type/context-only and measured pathway models with independent studies. Avoid inventing a categorical stress-match score from observed outcomes or pooling correlated factorial contexts. Existing six-study registry remains a pilot; no new independent study or pooled meta-analysis in this step. Preserve Paper A/TNC; draft PR only. New CI pending.