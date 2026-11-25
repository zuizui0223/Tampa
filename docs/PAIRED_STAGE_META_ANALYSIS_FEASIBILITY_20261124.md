# Paired-stage synthesis: study eligibility and sampling covariance (2026-11-24)

## Question and scope
Does a randomized change in a partner or antagonist modify a proximal ecological process and does a host-plant response follow? Distinguish process modification, host performance, recruitment and persistence. Existing literature already addresses context-dependent facilitation; generic stage decoupling is not a novelty claim. Target a quantitative, covariance-aware within-family synthesis of measured effect pairs, not pooling the significance of unrelated endpoints.

## Study screening
Registry: data/seagrass_interactions_v1/paired_stage_meta_registry_v1.csv. Twelve candidate rows, including separate experiments and exclusion records; not 12 independent effect-bearing studies. Six experiments are design-eligible candidates for two measured stages; only Laukaityte 2025 currently has a computed joint sampling covariance. Van der Geest 2020 has published marginal means/SE but no verified raw paired covariance. Four lucinid-detoxification studies are the first focused evidence family: van der Heide 2012 (Science), van der Geest 2020 (Frontiers), Chin 2021 (J Ecol), de Fouw 2022 (MEPS). Donaher 2021 Exp 1 offers epiphyte and plant performance in the same experiment, while Exp 2 does not measure epiphytes and is not interchangeable with Exp 1. Unsworth 2024 laboratory predation and field establishment are separate. ZEN 2015 public dataset lacks plant performance; Jorgensen 2019 manipulates burial, not fauna. No causal chain obtained by linking these experiments.

## Actual new source calculation
Laukaityte 2025 data.txt, exact original Git blob cb12f65a477078f3980a381b5251a635db312d53. Retain author analysis rows 81–240. For each tank contrast against no fauna, calculate the difference in fraction buried among counted seeds and difference in germinated count divided by nominal 10 introduced. The latter is a count scaled by planting effort, not a verified probability. Within each temperature, use equal mean of two run-specific means (8 tanks per run); estimated sampling covariance of mean is sum of the two run-specific sample covariance matrices divided by 8 and by 4. This is conditional on runs and assumes independent tank contrasts within run; shared water baths and only two runs preclude a general temperature effect inference. No between-temperature covariance estimated.

| temperature | partner | burial fraction difference | SE | germinated count difference per nominal 10 | SE (same scale) | within-pair sampling correlation |
|---|---|---:|---:|---:|---:|---:|
| cold | cockle | .411152 | .065497 | .050000 | .041188 | .02872 |
| cold | shrimp | .089193 | .103499 | .018750 | .043237 | -.23579 |
| cold | worm | .090573 | .115855 | .037500 | .038672 | .30164 |
| cold | mix | .206095 | .084251 | -.025000 | .023858 | -.03696 |
| warm | cockle | .587690 | .122155 | .050000 | .029693 | -.15508 |
| warm | shrimp | .226815 | .072914 | -.025000 | .028347 | -.05402 |
| warm | worm | .123438 | .084781 | .000000 | .044194 | -.17442 |
| warm | mix | .504372 | .075224 | -.006250 | .038017 | .04112 |

In the paper-independent arithmetic calculation, cold shrimp and worm germination effect sampling correlation is ~.688. Shared controls are important. This is an eight-component vector per temperature, not eight studies. Full matrices in results/bioturbation_joint_effect_covariance_20261124.json, computed in-session directly from verified original source. Python reproduction script analysis/159 imports the exact source parser from 158. Previous 158 CI succeeded at run 45394468281. Independent verification of 159 is pending.

## Published-summary illustration only
Van der Geest et al. 2020 Table 1, n=6 plots per treatment, same stress context:
- Without organic matter: clam/control mean ratio leaf sulfide intrusion .940887, rhizome biomass 1.068285, leaf biomass 1.110821, root biomass .964169, shoot density 1.315702.
- With organic matter: clam/control mean ratio leaf sulfide intrusion .881423, rhizome biomass 1.008264, leaf biomass .708197, root biomass .653409, shoot density .933281.
These are calculations from reported treatment means, not refits, not significant interactions; authors found no significant interaction. No sampling covariance from table, no sum of tissue SEs without covariance, no inference of mediation or actual adverse clam effects. Cannot count each tissue as an independent study.

## Acquisition
analysis/160 uses public repository APIs for five source candidates (2012 Zenodo mirror identified by Groningen research portal, 2020 and Donaher Dryad, Chin Figshare, de Fouw 2022 DANS). Local direct network access failed DNS; public metadata verified but new raw data acquisition is pending. Source gate records failures explicitly and never treats access denial as no effect. Do not use inventory success as proof of all files acquired. No raw data committed.

## Synthesis contract (exploratory, before further raw-source opening)
First family: lucinid addition vs absence in matched stress conditions, paired process (porewater sulfide) and host (whole-plant final dry biomass if documented; otherwise separate tissue/growth endpoint strata). Orient log response ratios so reduced sulfide and increased host outcome are positive. Positive arm means required; near-zero or zero sulfide flagged, not shifted by arbitrary constants. If incompatible growth or tissue measures, retain separate endpoints and do not substitute. Record exact units, timing, treatment assignment, block, shared controls and missingness. Preserve paired plot-level covariance via block contrasts/bootstrap or sampling covariance from joint model. No correlation assumed zero by default; if only summary means, report marginal ratios and sensitivity instead of pretending paired covariance is known. Distinguish same contrast at distinct times from longitudinal mediation. Do not fit an across-study transmission slope from one study or pretend stress contexts are studies. With at least three independent experiments with comparable paired endpoints, a small descriptive family-specific pilot may be reported with explicit imprecision; general stress moderation requires broader study-level coverage. No universal threshold on strength; no cross-family pooling without scientifically comparable endpoints and specified units. No paper submission, merge, Paper A or TNC change.