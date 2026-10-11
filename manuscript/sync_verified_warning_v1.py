#!/usr/bin/env python3
"""One-time synchronization of already-verified warning evidence, without model fits.

Run only against the documented pre-sync sources. Existing builders remain authoritative.
The script refuses changed section anchors; a failing run must not be committed.
"""
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
def edit(path, old, new):
    p=ROOT/path; text=p.read_text()
    if text.count(old)!=1: raise RuntimeError((path,'replacement count',text.count(old),old[:80]))
    p.write_text(text.replace(old,new),encoding='utf-8')
def section(path, start, end, new):
    p=ROOT/path; text=p.read_text();a=text.index(start);b=text.index(end,a)
    p.write_text(text[:a]+new.rstrip()+'\n\n'+text[b:],encoding='utf-8')

methods='''## Quantitative state and next-year recorded-state instability

We constructed 688 consecutive annual transitions from source-year recorded-positive Tampa transects: 24 next-year recorded losses and 664 recorded persistences. Recorded loss means that no eligible sampled point recorded the focal species during the next year; it is not demographic extinction, measured mortality or loss of underground rhizomes. A missing target-year survey was not coded as either loss or persistence.

The original logistic-regression comparison used source year, longitude, latitude, water-body identity, cyclic source-survey date and log source sampled-point count. The quantitative arm added source-year focal frequency and the all-point Braun–Blanquet index. Strict walk-forward fitting used only transitions with target years earlier than the scored year. A training gate required at least five earlier losses and 50 earlier persistences. The resulting evaluation contained 570 predictions, including 19 losses, in 23 target years (2003–2025).

A subsequent, outcome-exposed reference audit added categorical stable node identity to both arms without changing the observations, predictors, training folds or learner. Numeric predictors were standardized and categorical predictors one-hot encoded. LogisticRegression(C=1.0, max_iter=2000) was L2-regularized, including the node coefficients. Thus the comparison tests incremental prediction beyond this specified regularized node-ID reference, not removal of every persistent-site explanation or identification of within-node biological deterioration.

Log loss and Brier score were calculated by target year; pooled AUC was descriptive. The frozen reference-audit rule required lower macro annual log loss, improvement in at least 16 of 23 years, and a one-sided year sign-test probability below 0.05. Target year 2016 was retained in the primary evaluation; omitting it remained sensitivity only. The audit was fixed before its own result was evaluated but after exposure to the broader Tampa outcomes; it is not an untouched preregistered ecological confirmation.

For an operational description, the unchanged out-of-time probabilities ranked eligible transects separately within each target year. Nominal 10% and 20% capacities selected max(1, floor(capacity times the yearly scored count)); ties were ordered by node ID. Actual alert counts, captured recorded losses and precision were reported without optimizing thresholds or adding a significance test. This evaluation is conditional on being resurveyed the next year, not a prospective full-network deployment.

The fixed-mark audit matched previously recorded-positive point-event locationIDs to sampled IDs in the target year. A source point was positive if recorded in any eligible source-year visit; a target point was revisited if sampled in any eligible target-year visit. We classified losses into none, some, or all former positive marks revisited. The same nominal mark does not guarantee identical microquadrat placement or perfect detection. The original alert lists were partitioned by revisit status after inspection without refitting or reranking. This is an observation-process description, not a new mechanism test (Supplementary Tables S10–S12).
'''
section('manuscript/TAMPA_ECOLOGY_METHODS_V1.md','## Quantitative state and next-year recorded-state instability','## Temporal-state diagnostics',methods)
edit('manuscript/TAMPA_ECOLOGY_METHODS_V1.md',
'All scientific questions, frozen decision rules, source selections, analyses, interpretations, code changes, and final manuscript text were reviewed and approved by the human author(s), who take responsibility for the work.',
'Human authors retain responsibility for reviewing the sources, analyses, code and final text before submission. This working draft does not attest that final author review and approval have been completed.')

abstract='''## Abstract

Recorded occurrence and quantitative meadow state need not change together. We analyzed 1997–2025 fixed-transect monitoring of *Thalassia testudinum* in Tampa Bay, Florida, comprising 1,497 visits and 1,480 annual records at 71 stable transects. Recorded presence, within-transect frequency, Braun–Blanquet abundance, blade length and shoot density were treated as distinct observation dimensions.

After 2016, recorded occurrence changed weakly in several bay segments while particular quantitative dimensions declined. Old Tampa Bay showed declining blade length and shoot density, Middle Tampa Bay declining blade length, and Lower Tampa Bay declining focal frequency and abundance with compositional reorganization. An already-opened external *Zostera marina* panel also showed quantitative change under saturated recorded presence.

In an exploratory, strict walk-forward comparison of 570 source-positive cases with 19 next-year non-detections, quantitative state improved prediction beyond a regularized node-identity reference in 17 of 23 years. Pooled AUC increased from 0.671 to 0.736, but macro annual log-loss improvement was small and 2016 was strongly adverse. A fixed-mark audit found that 17 of 24 recorded-loss events revisited at least one previously positive mark. The added alert capture was not confined to events lacking such revisits, but nominal revisits did not identify mortality or eliminate observation error.

Persistent recorded occurrence is therefore an incomplete description of meadow state. The results support state-specific monitoring and conditional recorded-state prediction, not an identified decline mechanism or an intervention-validated early-warning system.
'''
section('manuscript/TAMPA_ECOLOGY_ABSTRACT_INTRO_V1.md','## Abstract','## Keywords',abstract)
edit('manuscript/TAMPA_ECOLOGY_ABSTRACT_INTRO_V1.md',
'Finally, if quantitative degradation often precedes change in the coarse state, source-year abundance measures should contain information about next-year recorded-state loss beyond space, time and survey-effort covariates.',
'Finally, we test whether source-year quantitative state contains information about next-year recorded-state loss beyond specified space, time, survey-effort and node-identity references. Predictive improvement alone does not demonstrate a biological decline sequence.')

result='''## Quantitative state predicted recorded loss under two specified references

Across 688 consecutive source-positive transitions, 24 were followed by recorded loss and 664 by persistence. Median source focal frequency was 0.0627 before loss versus 0.302 before persistence; the all-point Braun–Blanquet medians were 0.0495 and 0.713. These are differences in source state, not measurements of the rate of preceding decline.

The original space/time/effort comparison gave pooled AUC 0.636 to 0.739 and macro annual log loss 0.15563 to 0.14645 after quantitative augmentation. The subsequent regularized node-ID comparison retained the same 570 predictions, 19 losses and 23 target years. AUC increased from 0.67055 to 0.73636 and macro annual log loss decreased from 0.148268 to 0.147230. The augmented arm improved log loss in 17/23 years (one-sided sign test p = 0.0173448), meeting the frozen reference-audit rule. The absolute macro improvement was small. Target year 2016 remained adverse, with an augmented-minus-reference log-loss difference of +0.305633 (Table S10). These are internally evaluated, outcome-exposed results, not external confirmation.

At nominal annual capacities of 10% and 20%, the fixed lists selected 47 and 105 historical alerts per model. Quantitative augmentation increased recorded-loss capture from 6 to 9 of 19 and from 9 to 13 of 19, respectively; augmented precision was 19.1% and 12.4%. These counts describe conditional follow-up targeting, not prevention of loss (Table S12).

## Fixed-mark revisits constrain the sampling-footprint explanation

Of the 24 recorded-loss events, 10 revisited all former positive marks, seven revisited some and seven revisited none. Thus 17/24 revisited at least one formerly positive mark. In the scored subset, the partition was seven all, seven some and five none, giving 14/19 with a revisit. The 24 and 19 events involved 18 and 14 nodes, respectively, not independent meadows. All five 2016 loss events revisited a previously positive mark (Table S11).

Using the original lists without refitting or reranking, captures involving at least one revisited positive mark increased from four to six under the 10% capacity and from seven to nine under the 20% capacity. The additional captures split into two revisited and one unvisited event at 10%, and two revisited and two unvisited events at 20%. Neither list lost a previously captured event. The added revisited events differed between capacities; these partitions are descriptive and cannot be added as independent confirmations (Table S12).

The absence of any revisit leaves the fate of former positive points unresolved. A revisit excludes omission of all those points as the sole explanation, but cannot distinguish true local change from imperfect detection, effective quadrat repositioning or protocol variation. No loss was relabelled as a false alarm or as confirmed mortality.
'''
section('manuscript/TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md','## Low quantitative state preceded some next-year recorded losses within Tampa','## Immediate local state was strongly informative',result)

discussion='''## Conditional prediction is not identification of a decline mechanism

The quantitative-state increment survived the specified L2-regularized node-ID reference. That is evidence of out-of-time recorded-state information beyond that fitted reference, not proof that all stable-site alternatives were eliminated or that within-node physiological decline was identified. Low state and declining state are not interchangeable. The small average log-loss improvement, rare events, adverse 2016 result and dependence on subsequent survey attendance limit operational extrapolation.

The fixed-mark audit narrows one alternative explanation: added capture is not confined to events in which no previous positive mark was revisited. Nevertheless, the same nominal metre-mark ID does not ensure identical microquadrat placement or perfect detection. Recorded loss is not demographic extinction, and unvisited positive marks do not establish continuing presence. The independent-new-draw formula (1-p)^n remains an illustrative counterexample, not a fitted detection model for the repeated-mark archive.

A proposed observation-quality safeguard is to report both the number of sampled points and the number of previously positive points revisited. These are distinct. For example, S1T17 in 2007–2008 shared 109 sampled mark IDs and had 110 target-year marks, yet neither of its two source-positive marks was revisited. This motivates better documentation, not a demonstrated management benefit. Prospective use still requires detection-aware follow-up, frozen eligibility and an explicit cost/false-alarm context.
'''
section('manuscript/TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md','## Local quantitative state predicts next-year recorded absence beyond stable transect identity','## The temporal signal is better described',discussion)

for f in ['manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_V1.md','manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_ESCO_V1.md']:
    edit(f,'Quantitative degradation can precede recorded-state instability','Source quantitative state differs before recorded persistence and loss')
    old='Recorded loss is an observation-state endpoint and is not interpreted as demographic extinction'
    new='The space/time/survey-effort comparison in panel C is retained unchanged; the regularized node-ID comparison and fixed-mark audit appear separately in Tables S10–S12. Recorded loss is an observation-state endpoint and is not interpreted as demographic extinction'
    edit(f,old,new)

readme='''## Completed recorded-state prediction and fixed-mark audits

The original space/time/effort comparison is retained (pooled AUC 0.636 to 0.739). Adding the same source frequency and Braun–Blanquet state to the **L2-regularized node-ID reference** gave AUC **0.67055 to 0.73636**, macro annual log loss **0.148268 to 0.147230**, and **17/23** improved target years (frozen one-sided sign p **0.0173448**). The small average improvement includes strongly adverse 2016 (**+0.305633** annual log-loss difference). Support is relative to that specified predictive reference, not proof of a causal within-node deterioration process.

The fixed-mark audit is complete. Among **24** recorded losses in 688 source-positive transitions, **17/24** revisited at least one formerly positive mark: 10 all, seven some and seven none. Among the **19** scored losses in 570 predictions, the corresponding partition is seven all, seven some and five none (**14/19** revisited). All five 2016 losses had a revisit. Nominal mark identity does not guarantee identical microquadrat placement or perfect detection; non-detection is not measured mortality.

The unchanged 10%/20% nominal annual lists selected 47/105 alerts. Capture increased **6 to 9** and **9 to 13** of 19 losses. Within the original lists, captures with a prior positive mark revisited increased **4 to 6** and **7 to 9**. No list was refitted or reranked, and the partition adds no new statistical test or intervention claim. Historical targeting is conditional on a next-year survey.

See [verified source and interpretation](docs/EARLY_WARNING_FIXED_MARK_VERIFIED_V1.md), [canonical overlap result](results/early_warning_fixed_mark_overlap_verified_v1.json), and [Supplementary Tables S10–S12](manuscript/TAMPA_ECOLOGY_SUPPLEMENT_ASSEMBLED_V1.md). The source computation succeeded in [run 38109944875](https://github.com/zuizui0223/Tampa/actions/runs/38109944875); a separate artifact reaggregation reproduced its counts and probabilities without refitting.

The [condition-leading test](results/condition_leads_thinning_v1.json) did not support an annual blade-length/shoot-density to next-year thinning sequence. The ecological interpretation remains state-specific change, not a demonstrated serial cascade. No future TNC, reserve buffering, mortality or management outcome was measured here.
'''
section('README.md','## Completed site-identity falsification:','## Current reproducible result',readme)

# Update the operational note at the source, instead of retaining conflicting pending labels.
p=ROOT/'docs/EARLY_WARNING_MONITORING_UTILITY_V1.md';text=p.read_text()
text=text.replace('The [original site-saturated falsification](results/early_warning_site_identity_saturation_v1_contract.json)','The [original site-saturated falsification](../results/early_warning_site_identity_saturation_v1_contract.json)')
text=text.replace('beyond a stable-site signature.','beyond the specified L2-regularized node-ID reference, not beyond every possible persistent-site explanation.')
text=text.replace('The audit was authored after the long-term outcomes had already been opened. It is a descriptive assessment of **observation-process plausibility**, not a new preregistered test of sea-grass deterioration. No overlap values or positive ecological conclusion are supplied until the empirical workflow succeeds.',
'The audit was authored after the long-term outcomes had already been opened. It is a descriptive assessment of **observation-process plausibility**, not a new preregistered test of seagrass deterioration. The computation is now complete: **17/24** full-cohort losses and **14/19** scored losses revisited at least one former positive mark. The none/some/all partitions were 7/7/10 and 5/7/7. All five 2016 losses had a revisit. In the unchanged lists, revisited-event captures increased 4 to 6 at the 10% cap and 7 to 9 at the 20% cap. These descriptive partitions do not identify mortality or justify reranking. See [the verified report](EARLY_WARNING_FIXED_MARK_VERIFIED_V1.md).')
text=text.replace('The fixed-mark overlap follow-up is a separate pending descriptive audit.','The fixed-mark audit also succeeded in run 38109944875; Tables S10–S12 and the verified report now contain its result. No new mechanism test was added.')
p.write_text(text,encoding='utf-8')

s5='''# Supplementary Methods S5. Next-year recorded-state instability

This endpoint was formulated after exposure to the Tampa state-decoupling results. The internal walk-forward comparison and subsequent reference audit are developmental, not untouched external or preregistered ecological confirmation.

The registry contains 688 source-positive consecutive annual transitions (24 recorded losses, 664 persistences). A missing next-year visit is not an absence. Recorded loss is non-detection at all eligible sampled points in the next year, not demographic extinction.

The original baseline used **source year**, longitude, latitude, water body, cyclic source-survey date and log source point count. The quantitative arm added source-year frequency and all-point Braun–Blanquet. Each target-year fold trained only on earlier target years and required at least five earlier losses and 50 earlier persistences, yielding 570 predictions, 19 losses and 23 scored years (2003–2025). Standardized numeric and one-hot categorical inputs entered LogisticRegression(C=1.0, max_iter=2000).

The post-hoc reference audit added node identity to both arms without changing folds, features, regularization or outcomes. Node coefficients were L2-regularized, so this is not an unpenalized saturated fixed-effect identification design. The frozen rule required lower macro annual log loss, at least 16/23 yearly improvements and a one-sided sign-test probability below 0.05. Pooled AUC is descriptive. The adverse 2016 target year remains primary; its exclusion is sensitivity only (Table S10).

The nominal 10%/20% annual alert lists use max(1, floor(capacity times that year's scored count)), with lexical node-ID tie-breaking. They are retrospective conditional-on-resurvey lists. No capacity was optimized and no extra inferential test was fitted (Table S12).

For fixed-mark matching, source-positive IDs and target-sampled IDs were unions over eligible visits within each year. Losses were partitioned according to whether none, some or all previously positive IDs were revisited. The same nominal ID need not imply the same microquadrat position or perfect detectability. Original lists were not reranked after this partition. This is not a new significance test or mortality endpoint (Tables S11–S12).
'''
section('manuscript/TAMPA_ECOLOGY_SUPPLEMENT_V1.md','# Supplementary Methods S5.','# Supplementary Methods S6.',s5)

record=json.loads((ROOT/'results/early_warning_fixed_mark_overlap_verified_v1.json').read_text())
metrics={'space': {'log_loss': 0.14971493590809562, 'brier': 0.03216681846779974, 'auc': 0.636354952717547, 'macro_log_loss': 0.1556293347558577}, 'space_quant': {'log_loss': 0.13804604022180997, 'brier': 0.029781448477710918, 'auc': 0.7385614671888433, 'macro_log_loss': 0.14645165934327545}, 'node': {'log_loss': 0.14335738584231025, 'brier': 0.03141783406376481, 'auc': 0.6705511510172891, 'macro_log_loss': 0.14826766946459452}, 'node_quant': {'log_loss': 0.13887333640527613, 'brier': 0.030017389281513655, 'auc': 0.7363645047282453, 'macro_log_loss': 0.14723029062512885}}
tables='''# Supplementary Tables S10–S12. Verified recorded-state audits

These tables report existing frozen predictions and post-hoc observation-process descriptions, not new biological outcomes. Source computation: run 38109944875, artifact 11691158710, ZIP SHA256 `18109267f68732c5460a9e4d087e2711282ed71f13f96ed7d0a484ed0320d89e`. Canonical partitions: `results/early_warning_fixed_mark_overlap_verified_v1.json`. A separate archive reaggregation checked the exported probabilities and counts without refitting.

## Table S10. Matched prediction references

| Reference | Macro annual log loss | Pooled AUC | Pooled Brier score |
|---|---:|---:|---:|
'''
for arm,label in [('space','Space/time/effort'),('space_quant','Space/time/effort + quantity'),('node','Regularized node ID + space/time/effort'),('node_quant','Same regularized reference + quantity')]:
    m=metrics[arm];tables+=f"| {label} | {m['macro_log_loss']:.6f} | {m['auc']:.5f} | {m['brier']:.6f} |\n"
tables+='''
All arms use the same 570 predictions, 19 recorded losses and 23 target years. The node-reference increment won 17/23 years (frozen one-sided sign p = 0.0173448); its macro annual log-loss difference was -0.001037 and its 2016 difference +0.305633. A reference-audit PASS is not proof of causal deterioration or independent external validation. "Quantity" denotes source frequency and all-point Braun–Blanquet, not measured biomass.

## Table S11. Previous positive marks revisited during recorded-loss events

| Population | Events | None revisited | Some, not all | All revisited |
|---|---:|---:|---:|---:|
'''
for key,label in [('all_losses','All loss events'),('scored_losses','Scored loss events'),('target_2016_losses','2016 loss events')]:
    r=record['loss_partitions'][key];tables+=f"| {label} | {r['events']} | {r['no_positive_mark_revisited']} | {r['some_but_not_all_revisited']} | {r['all_positive_marks_revisited']} |\n"
tables+='''
The 24 full-cohort events involve 18 nodes; the 19 scored events involve 14 nodes. These rows are nested populations, not independent replicates. No revisit leaves the fate of the previous positive marks unresolved; at least one revisit rules out omission of every previous positive mark as the sole explanation, not observation error generally.

## Table S12. Original annual alert lists, unchanged after mark classification

| Nominal cap | Alerts/model | All captures: node | All captures: +quantity | Revisited captures: node | Revisited captures: +quantity |
|---|---:|---:|---:|---:|---:|
'''
for r in record['capacity_decomposition']:
    tables+=f"| {r['nominal_capacity']:.0%} | {r['alerts_per_arm']} | {r['captured_all_node']} | {r['captured_all_node_quant']} | {r['captured_revisited_node']} | {r['captured_revisited_node_quant']} |\n"
tables+='''
The added captures split into two revisited/one unvisited event at 10% and two revisited/two unvisited events at 20%. No previously captured loss was dropped. The two additional revisited events differ across capacities and cannot be added as independent confirmations. Overall augmented precision remains 9/47 = 19.1% and 13/105 = 12.4%; unvisited events were not reclassified as false alarms. The classification is post-hoc, not a new significance test, and the same nominal mark is not proof of identical placement or perfect detection.

'''
p=ROOT/'manuscript/TAMPA_ECOLOGY_SUPPLEMENT_V1.md';text=p.read_text();text=text.replace('# Supplementary display inventory',tables+'# Supplementary display inventory')
text+='\n**Table S10** Matched original and regularized node-ID prediction references  \n**Table S11** None/some/all prior positive mark revisits for recorded-loss events  \n**Table S12** Unchanged annual alert-list captures, with the descriptive revisit partition\n'
p.write_text(text,encoding='utf-8')
p=ROOT/'manuscript/TAMPA_ECOLOGY_SUPPLEMENT_CAPTIONS_V1.md'
p.write_text(p.read_text()+'''\n\n**Table S10** Original and regularized node-ID predictive comparisons on exactly the same 570 scored cases. Metrics are not an independent external validation.\n\n**Table S11** Revisit status of previously recorded-positive nominal metre marks during recorded-loss events. Events are repeated observations within nodes, not independent meadows.\n\n**Table S12** Loss captures under the original nominal 10%/20% annual capacities, partitioned by revisit status without refitting or reranking. The partition is descriptive, not a new causal or significance test.\n''',encoding='utf-8')

# Record the exact display values used above with source lineage, not a new model fit.
out={'schema':'tampa.warning_reporting_metrics_v1','evidence_class':'display_only_reaggregation_of_archived_predictions','source':record['source'],'metrics':metrics,'changes_to_models_or_thresholds':False}
(ROOT/'results/warning_reporting_metrics_v1.json').write_text(json.dumps(out,indent=2)+'\n')
print('Edited canonical sections and descriptive tables; no estimator or frozen contract modified.')

import subprocess, sys
for builder in ['build_manuscript.py','build_esco_submission.py','build_supplement.py']:
    subprocess.run([sys.executable,str(ROOT/'manuscript'/builder)],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(ROOT/'validation/verify_warning_reporting_sync.py'),'--out',str(ROOT/'results/warning_reporting_sync_v1.json')],cwd=ROOT,check=True)
