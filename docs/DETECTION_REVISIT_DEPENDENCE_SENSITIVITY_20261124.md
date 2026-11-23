# Tampa: dependence-aware detection effort sensitivity (2026-11-24)

**Status:** Response-free analytic sampling design; no new ecological observation; no estimated Tampa detection parameter. Extends the observation identifiability gate in PR #167.

## Why the old independent-repeat formula may be optimistic

The previous 95%-cumulative-detection table treated repeated surveys as unconditionally independent with identical fixed p. But if each mark has a *stable* recording propensity p_i, recordings are marginally correlated even when repeat observations are independent *conditional on p_i*. This is directly relevant to the earlier known-truth explanation of the 1,0,1 -> 0 observational association.

Illustrative model (not a fitted Tampa model): every mark is truly occupied throughout a justified short survey-closure window; its p_i is sampled across marks from a Beta(alpha,beta) distribution. Given p_i, K equal-effort surveys are conditionally independent Bernoulli(p_i). The marginal per-survey mean is m = alpha/(alpha+beta); the marginal pairwise within-mark intraclass correlation is rho = 1/(alpha+beta+1). Set alpha=m*(1/rho-1), beta=(1-m)*(1/rho-1) for rho>0; for rho=0, take the homogeneous independent limit.

P(all K visits miss a truly occupied mark) = product over j from 0 to K-1 of (beta+j)/(alpha+beta+j).

For rho=0, the expression reduces to (1-m)^K. We find the first integer K with P(all missed)<=0.05 without using any biological outcome or fitted detection values.

## Conditional illustrative sensitivity results

| Mean recording m | K at rho=0 | K at rho=.1 | K at rho=.2 |
| ---: | ---: | ---: | ---: |
| .4 | 6 | 9 | 15 |
| .6 | 4 | 5 | 6 |
| .8 | 2 | 3 | 3 |

At m=.4, changing rho from 0 to .2 changes K from **6 to 15**. At 15 independent-conditional visits, the marginal all-miss probability in this *hypothetical* Beta mixture is **0.04868**, versus **0.05343** at 14. This is an exact conditional model-based arithmetic threshold, not an estimated Tampa sample size, a power calculation for biological state transitions or a detection-adjusted confidence interval.

### Structural-zero recording component

Suppose a fraction z of truly occupied marks has **effective** p_i=0 under the chosen survey footprint and method. If the remaining marks follow the Beta mixture:

P(all missed) = z + (1-z) * P_Beta(all missed).

Its asymptotic floor is z. For the **illustrative** case z=.08, no finite K meets a 5% all-miss criterion. This is a demonstration that adding revisits cannot correct a systematically wrong footprint or survey method; it is NOT evidence of 8% unrecordable Tampa marks.

## Future field components that must remain separate

- **Recognition error:** blinded classification of an identical fixed georeferenced image by different observers; measures recognition disagreement, not independent visits.
- **Repeat field observation:** separate visits to the identical georeferenced quadrat within an independently justified temporal closure period, retaining observer and survey-effort records.
- **Spatial patch encounter:** independently identified and marked offset subquadrats, analyzed as different spatial units, not repeats of one site.
- **Detection heterogeneity:** variation in p_i among marks/nodes with clustering and potential structural-zero confounding; a p_i=0 history can also be true absence and may not be identifiable from detection histories alone.
- **Biological buffering:** future matched quantitative shoots/BB and below-ground TNC, with outcomes opened after predictor/geometry freeze. A detection-model improvement is not proof of clonal buffering.

The optional raw pilot input template in field/return_detection_pilot_raw_v1_template.csv remains empty and NOT field-ready; its validator prevents unvisited zeros, photo reuse and confusing repeated observer readings with new field revisits.

## Existing field study is protected

The frozen four-bay TNC-v2 study remains first priority, with a 41-node historical recent-positive frame, >=36 primary analyzable nodes and >=6 per bay, synchronized campaign and lab-pilot constraints. The source-readiness status is STOP_RESOURCE_FREEZE_INCOMPLETE. Nothing in this illustration changes site selection, field authorization, TNC assays, outcome contracts, or permits. It does not imply anyone should automatically conduct 15 actual repeat visits.

The strongest *current ecological evidence* remains the geographically distinct decline in measured plant morphology/density or local species frequency/composition under partly persistent recorded Thalassia. The re-recording effect remains an observation-state signal until real detection and biological state are jointly measured.

## Conditional miss probability is NOT posterior absence confidence

The model's 5% criterion is P(K consecutive zeros | TRUE occupancy) <= .05. That must not be paraphrased as P(TRUE absence | K zeros) >= .95. Under *illustrative assumptions* of prior true occupancy psi, perfect specificity, and the same detection model, Bayes' rule gives

P(TRUE occupied | all K zeros) = psi * M(K) / ((1-psi) + psi * M(K)),

where M(K) is the previously computed conditional all-miss probability.

At mean p=.6, ICC=.2, and K=6, M(K)=0.0420992. The implications differ sharply by assumed historical occupancy prior:

| Prior true occupancy psi (assumed) | P(still truly present | 6 zeros) | K for posterior true presence <=5% |
| ---: | ---: | ---: |
| .50 | 4.04% | 6 |
| .80 | 14.41% | 12 |
| .90 | 27.48% | 17 |
| .95 | **44.44%** | **24** |

For the lower illustrative detection case mean p=.4 and ICC=.2, psi=.95 requires K=104 to reach <=5% posterior true occupancy in this exact model. Such numbers illustrate why an intensive repeat-only design can be impractical; they are **not feasible target survey schedules for real Tampa sites**.

The relevant priors psi, recording mean, dependence and specificity are **unknown** for Tampa's actual historical marks. Structural-zero recording also creates a posterior floor that can prevent the target being achieved by repeats alone. This extension supplies no site-specific absence probabilities, loss estimates or independent forecasting performance.

## Reproduction

- analysis/112_detection_revisit_dependence_sensitivity.py: standard-library-only Beta-mixed all-miss probability and repeat-effort grid with a structural-zero floor.
- validation/test_detection_revisit_dependence_sensitivity.py: eleven synthetic tests for analytic moments, repeat minima and non-estimability.
- CI extends the existing response-free return-fragility exchangeability workflow and emits an inspectable JSON artifact.
