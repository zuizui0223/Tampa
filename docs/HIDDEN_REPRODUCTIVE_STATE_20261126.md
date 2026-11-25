# Hidden reproductive-state discordance after simulated grazing (2026-11-26 JST)

## Scope
New executed secondary analysis of the existing Kollars & Stachowicz 2022 experiment (Ecology e3710, DOI 10.1002/ecy.3710). The original publication already demonstrates that simulated goose grazing suppresses colonization and flowering despite shoot recovery in the recurrent disturbance arm; no claim of discovering that mechanism. We test the block-level discordance of recorded shoot abundance and newly detected multilocus genotypes (MLGs), and retrospective held-block predictability. No new independent study, future outcome, actual goose or otter treatment, sexual recruitment identification, or causal mediation.

Source: nmkollars/Field-Goose commit eeff76e6a68f73db8d5c2afd3225e17ebf2b4d7e, Kollars_feedback_shoots.csv blob b4f417bc95f21a3828399e3a54943031759ace32; derived plot ledger at Tampa commit 58600bd10b5e53d90cc551fd08e5d9be97d3a996, results/goose_reproductive_recovery_plots_20261125.csv blob 046acb03b5cbd6baa1972430ba15eaf584cd97a1, original MLG provenance in prior report. Both retrieved at exact refs, returned blob IDs checked. Unique 36 block/plot keys; exact treatment, initial/final shoots and May/June shoot/flower counts match. 20 shoot dates, one missing Apr2018 control; no imputation. Prior paper/README conflict on whether date counts denote vegetative or total shoots: keep recorded shoot counts, no area conversion. Flower counts are standing stocks. Genet gain is set difference of two observed samples, not verified biological origin. See previous source audit for two genotype-richness discrepancies.

## Analysis and observed results
Pair each treatment to 0X within each of 9 randomized blocks. For nonnegative endpoint A (treated), C (control), symmetric contrast d=(A-C)/(A+C), set d=0 for joint observed zeros (tie, not a ratio). Difference d_shoot-d_gain is a dimensionless contrast of descriptive scales, not physiological sensitivity or mediation. Enumerate all 2^n paired label swaps for mean difference; exact under pairwise exchangeability and sharp null of no effect on the measured composite, not proof of equal relative treatment effects under a nonzero common effect. All choices response-open, no familywise correction. Raw lower gain with shoot >= control is a deliberately simple posthoc discordance indicator, not a validated decision threshold. Baseline-adjusted sensitivity compares A/A_initial vs C/C_initial. 1X and 4X (no second-year clipping) kept distinct from recurrent 2X.

| 2X window | lower raw MLG gain blocks | shoot >= control among lower gain | mean d_shoot - d_gain | exploratory swap p |
|---|---:|---:|---:|---:|
| 2018 May-June | 6/9 | 3/6 | .699215 | .015625 |
| final October 2018 | 6/9 | 4/6 | .690313 | .01953125 |
| May-June baseline-normalized | 6/9 | 1/6 | .681428 | .00390625 |
| final baseline-normalized | 6/9 | 1/6 | .664510 | .01171875 |
| May-June omit discrepant blocks 5/9 | 4/7 | 3/4 | .659110 | .0625 |
| May-June common sampled grid gain | 6/9 | 3/6 | .699215 | .015625 |
| May-June expected rarefied gain k28 | 7/9 | 3/7 | .789812 | .0078125 |

At May-June blocks 2,7,8 each have more recorded shoots but fewer flowering shoots AND fewer recorded gained MLGs than control; all three remain after omit blocks 5/9. Adjusting baseline leaves only block 2. Final raw discordance adds block5. Full date ledger reported, not treating 20 dates as independent trials. The 1X and 4X May-June composite contrasts are .0251 (p=.918) and -.2309 (p=.449), not evidence of general dose or recovery differences. Prior 2X raw control-relative mean shoots 1.068, flowers .355, gain .091. No equivalence claim.

## Can shoot history classify recorded genotype gain?
Outcome any MLG gain over full experiment. Leave out whole block, training-only centering and scaling; logistic ridge penalty on standardized slopes (unpenalized intercept) lambda=1 main descriptive comparison, .1 and 10 sensitivities, fixed gradient descent. No tuning/independent test. Comparator training event proportion with .5 pseudocount per class. Standing model baseline log1p shoot, initial MLG richness, May-June shoot and final shoot. History adds growing2017 and pre2018 means. Flower model adds May-June flowers. Treatment model baseline plus treatment indicators. All observations retained; 2018 spring/terminal shoot measurements and flowering overlap the two-year gain outcome; these are NOT prospective forecasts or treatment-independent validations. Held blocks are not independent estuaries.

| model | 36-plot Brier | log loss |
|---|---:|---:|
| mean | .253775 | .701164 |
| baseline | .248289 | .689186 |
| standing | .272227 | .746820 |
| history | .304957 | .836973 |
| standing + flowers | .289889 | .795318 |
| history + flowers | .317297 | .890836 |
| baseline + treatment | .187507 | .551062 |

No improvement from standing/history/flower over mean at any of the three penalties in all plots. Treatment history improves compared with mean in all three penalties; 0X/2X-only sensitivity gives mean .266917 vs baseline+treatment .189155 at lambda1, history .389018 and flowers .368794. This is small same-experiment retrospective model comparison, not proof that observed abundance/flowering cannot predict recruitment generally, or that recording disturbance history enables external management prediction. Zero gain can be undetected real genets; existing study-wide origin ambiguity unchanged. Treatment effect on detected gain already known; the held-block comparison is new descriptive information about whether these particular shoot summaries can substitute for treatment history. No individual fate linkage. Other experimental systems can give different response direction; warming study shows marked adult mortality and unresolved reproductive total change, so not general reproductive-first hierarchy.

## Reproduction
node analysis/186_hidden_reproductive_state.cjs ORIGINAL_SHOOTS.csv FROZEN_GAIN.csv output.json
Executable source includes byte-level Git blob checks for offline reproduction; the analysis function was actually executed on retrieved exact-ref strings in JS. Node wrapper not independently executed/CI-replayed. Full result ledger has paired rows, date/window contrasts, held-block predictions and penalty sensitivities. No main/manuscript or TNC modifications. Do not treat as a new independent study for meta-analysis.

## Next test
Obtain independently genotyped longitudinal seed/recruit cohort, repeated detection surveys and disturbance histories; test whether reproductive/genetic endpoint adds actionable risk prediction conditional on baseline and standing stocks. Distinguish adult abundance, flowering stock, seed supply, seed survival, sexual recruit origin and genotype detection. Freeze a genuinely new source before outcome access. Do not retroactively count this analysis as prospective.
