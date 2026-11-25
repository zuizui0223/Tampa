# Three-study paired lucinid sulfide–host endpoint pilot (2026-11-24)
 
## Source acquisition and design
Prior head 4a34da011a018163bd2b4240aeb4f83e59f5d1a3: 20/20 workflows successful, including joint effect covariance. Run 45395577581, artifact 14920613486, ZIP SHA256 0e7b1b2dd9e506621f0d7b863276293bd2dc4b393aa68fed6873bd94afb1176d checked in local container. 4/5 datasets acquired (2012, 2020, 2022, Donaher). Chin failed on file metadata KeyError downloadUrl; source gate 160 updated to recognize provider's advertised download_url or downloadUrl, no guessed URL. Retry pending. Donaher not yet analyzed in this turn. 
- van der Heide et al. 2012, DOI 10.1126/science.1219973, Dryad 10.5061/dryad.210mp, Zenodo mirror 4958629. 40 abiotic records, 20 Zostera-bearing columns (4 cells of 5). Join Abiotic and Zostera sheets by Zostera/Loripes treatment, sulfide treatment and replicate number. All 20 keys close. Same experiment; within-treatment # assumed same column for covariance, no separately validated ID. Independent arm means; do not treat same replicate number across treatment arms as a block. Last sulfide measurement t10 and final shoot+rhizome+root biomass. Single shared seawater basin.
- van der Geest et al. 2020, DOI 10.3389/fmars.2020.00011, Dryad 10.5061/dryad.jm63xsj6n. 24 plots in 6 randomized field blocks, 4 treatments per block. Table7 and Table9 join exactly by Site/Block/Experimental_group/Plot_ID/OM_addition/Loripes_addition. No missing focal endpoints. Porewater day49 and final leaf+rhizome+root biomass day50. Control already has lucinids; compare addition assignment, not absence/presence.
- de Fouw et al. 2022, DOI 10.3354/meps14074, DANS 10.17026/dans-x9d-ytww. 40 mesocosms, 5 per factorial cell; tank IDs 1,2 warm and 3,4 ambient. All combinations represented within each tank (2–3 per cell). Sum s_dm_A and s_dm_B. Compare pooled arm means, then equal-tank mean of within-tank log response ratios as sensitivity. Only 2 tanks per temperature. No general temperature interaction significance inferred.
 
## Original source calculations
84 host-bearing experimental units in three studies; eight context-specific contrasts (not eight independent studies). Positive oriented log ratio = reduced porewater sulfide (log control/treated), or higher final total biomass (log treated/control). Raw arm means:
|study/context|sulfide control|sulfide treated|biomass control g|biomass treated g|oriented log sulfide|log biomass|
|---|---:|---:|---:|---:|---:|---:|
|2012 C|206.26|10.98|.68308|.83242|2.933062|.197725|
|2012 S|2219.64|13.08|.52654|.73148|5.134016|.328743|
|2020 C|.08765311|.35078815|1.6017|1.6862|-1.386795|.051412|
|2020 OM|1170.860767|716.354279|1.51341667|1.16276667|.491320|-.263568|
|2022 ambient no OM|410.88|43.86|.21536|.32948|2.237298|.425205|
|2022 ambient OM|3851.20|267.18|.28892|.58632|2.668217|.707716|
|2022 warm no OM|1326.48|117.92|.23060|.28750|2.420278|.220538|
|2022 warm OM|4961.24|380.78|.248864837|.35114|2.567189|.344275|
2020 control sulfide near zero (<1 micromol/L), flag rather than pool its log ratio. In OM plots final observed clam counts per core were 29.0 (no addition) and 28.333 (addition). Assignment effect is not an achieved clam density contrast; post-treatment counts cannot replace randomized treatment. OM contrast biomass ratio .7683 despite lower average sulfide. Across six leave-one-block-out analyses OM sulfide log ratio stays positive (.1695 to .7839), biomass log ratio stays negative (-.3938 to -.1279). This is sensitivity of point estimates, not a significant negative host effect.
 
2022 OM equal-tank log ratios: ambient (2.786986,.740867), warm (2.670855,.342902). Conditional within-tank log-biomass effects: ambient tanks .655959/.825774; warm .338144/.347659. Same direction of smaller host response under warming, even when relative detoxification similar. But only two tanks per temperature; absolute residual sulfide higher (267.18 vs380.78) and other physiological constraints plausible. No inferred mediation or claim that residual sulfide causes attenuation.
 
## Covariance
2012 independent-arm delta covariance for oriented log ratios conditional on source-key matching:
C [[.05912802,-.00092463],[-.00092463,.00534552]];
S [[.01798150,.00129470],[.00129470,.00294941]].
2020 full 4x4 block delta covariance (C detox, C biomass, OM detox, OM biomass) retains dependence across contexts. OM marginal SE .409253/.194634. 2022 equal-tank conditional delta SE for OM .248010/.196850 ambient; .216245/.196716 warm. Does not include between-tank random effects. All variance estimates exploratory approximations on small samples.
 
## Interpretation and limits
The two laboratory studies show strong sulfide reductions but host response magnitudes differ. The field addition experiment has a weaker/more uncertain realized intervention and a nonpositive host mean contrast with organic loading. Near-zero denominators, different stress manipulation, timing, laboratory vs field and resident vs absent clam controls prevent a scientifically meaningful single pooled transmission coefficient at this stage. This is actual multi-study paired effect-size extraction, not a finished pooled meta-analysis. Do not regress 8 context rows as independent studies or infer a universal residual-stress threshold. Original publications already described detoxification and context-dependent facilitation. New diagnostic is total host biomass versus matched porewater response, preserving dependence and explicit field intervention boundary. The published PDF text was inspected; screenshot requests returned cache misses, so no graph digitization or visual PDF claim used. Raw numeric results independently computed in local Python from source artifact; script 161 committed, independent CI pending. Draft PR #170, no merge or changes to Paper A/TNC.