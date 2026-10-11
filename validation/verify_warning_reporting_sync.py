#!/usr/bin/env python3
"""Reporting-only checks of existing Tampa warning evidence; never fits a model."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path = ROOT) -> dict:
    failures = []
    checked = []
    def need(ok: bool, message: str) -> None:
        checked.append(message)
        if not ok:
            failures.append(message)
    def read(path: str) -> str:
        return (root / path).read_text(encoding='utf-8')
    record = json.loads(read('results/early_warning_fixed_mark_overlap_verified_v1.json'))
    need(record['registry'] == {'all_transitions':688,'recorded_losses':24,'scored_rows':570,'scored_losses':19,'scored_years':23}, 'unchanged recorded-state registries')
    for source, output in [
        ('build_manuscript.py','TAMPA_ECOLOGY_MANUSCRIPT_V1.md'),
        ('build_esco_submission.py','TAMPA_ECOLOGY_ESCO_SUBMISSION_V1.md'),
        ('build_supplement.py','TAMPA_ECOLOGY_SUPPLEMENT_ASSEMBLED_V1.md')]:
        spec = importlib.util.spec_from_file_location('report_'+source,root/'manuscript'/source)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            need(module.build() == read('manuscript/'+output), 'fresh generated output: '+output)
        except Exception as exc:
            need(False, 'builder succeeds: '+source+' ('+str(exc)+')')
    methods = read('manuscript/TAMPA_ECOLOGY_METHODS_V1.md')
    need('L2-regularized' in methods and 'C=1.0' in methods, 'Methods identifies the penalized node reference')
    need('not demographic extinction' in methods, 'Methods preserves exact mortality boundary')
    need('source year' in methods and 'previously recorded-positive' in methods, 'Methods documents predictor timing and nominal mark matching')
    for path in ['README.md','manuscript/TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md','docs/EARLY_WARNING_MONITORING_UTILITY_V1.md']:
        text = read(path)
        need('fixed-mark' in text.lower() and '17/24' in text, path+': completed fixed-mark finding')
        need('not yet confirmed' not in text.lower() and 'separate pending descriptive audit' not in text.lower(),path+': no stale pending outcome')
    for path in ['manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_V1.md','manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_ESCO_V1.md']:
        text=read(path)
        need('Quantitative degradation can precede' not in text,path+': Figure 4 does not infer temporal decline from low state')
        need('space/time/survey-effort' in text and 'S10' in text,path+': legacy comparator retained and new comparison separated')
    supplement=read('manuscript/TAMPA_ECOLOGY_SUPPLEMENT_V1.md')
    for key,label in [('all_losses','All loss events'),('scored_losses','Scored loss events'),('target_2016_losses','2016 loss events')]:
        r=record['loss_partitions'][key]
        row=f"| {label} | {r['events']} | {r['no_positive_mark_revisited']} | {r['some_but_not_all_revisited']} | {r['all_positive_marks_revisited']} |"
        need(row in supplement, 'S11 matches canonical partition: '+key)
    for r in record['capacity_decomposition']:
        row=f"| {r['nominal_capacity']:.0%} | {r['alerts_per_arm']} | {r['captured_all_node']} | {r['captured_all_node_quant']} | {r['captured_revisited_node']} | {r['captured_revisited_node_quant']} |"
        need(row in supplement,'S12 matches unchanged alert counts: '+str(r['nominal_capacity']))
    need('same nominal' in supplement.lower() and 'not a new significance test' in supplement, 'Supplement states observation and post-hoc limits')
    display = json.loads(read('results/warning_reporting_metrics_v1.json'))
    need(display['source'] == record['source'], 'display metrics retain verified artifact lineage')
    for arm,label in [('space','Space/time/effort'),('space_quant','Space/time/effort + quantity'),('node','Regularized node ID + space/time/effort'),('node_quant','Same regularized reference + quantity')]:
        m=display['metrics'][arm]
        row=f"| {label} | {m['macro_log_loss']:.6f} | {m['auc']:.5f} | {m['brier']:.6f} |"
        need(row in supplement, 'S10 matches archive-reaggregated metric: '+arm)
    main = read('manuscript/TAMPA_ECOLOGY_MANUSCRIPT_V1.md').lower()
    refs = read('manuscript/TAMPA_ECOLOGY_REFERENCES_V1.md').lower()
    for word in ['ellison','orth','waycott','roca','lefcheck','unsworth','lee','carlson','beck','rising','williams']:
        need(word in refs and word in main,'existing bibliography/in-text guard: '+word)
    for word in ['post-hoc external ecological','do not establish direct competitive replacement','not demographic extinction','target year 2016','# references']:
        need(word in main,'existing main manuscript guard: '+word)
    for token in ['[ref','citation needed','confirmed extinction','confirmed recolonization']:
        need(token not in main,'existing forbidden wording guard: '+token)
    esco=read('manuscript/TAMPA_ECOLOGY_ESCO_SUBMISSION_V1.md')
    abstract=esco[esco.index('## Abstract')+len('## Abstract'):esco.index('## Keywords')].strip()
    words=re.findall(r"\b\w+[\w’'-]*\b",re.sub(r'[*_]',' ',abstract))
    need(150<=len(words)<=250,'existing ESCO abstract length guard')
    keywords=esco[esco.index('## Keywords')+len('## Keywords'):esco.index('# Introduction')].strip().split(';')
    need(4<=len(keywords)<=6,'existing ESCO keyword count guard')
    caps=read('manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_ESCO_V1.md').splitlines()
    figlines=[x for x in caps if x.startswith('**Fig. ')]
    need(len(figlines)==4 and all(not x.rstrip().endswith('.') for x in figlines),'existing ESCO four-caption format guard')
    references=read('manuscript/TAMPA_ECOLOGY_REFERENCES_V1.md').splitlines()
    names=[x.split(',')[0] for x in references if x and not x.startswith('#') and not x.startswith('This list') and '(' in x]
    need(names==sorted(names,key=str.casefold),'existing ESCO bibliography ordering guard')
    need(not re.findall(r"\([A-Z][^()]{0,80}\bet al\. (?:19|20)\d{2}\)",esco),'existing ESCO citation punctuation guard')
    return {'schema':'tampa.warning_reporting_sync_v1','status':'PASS_REPORTING_SYNC' if not failures else 'FAIL_REPORTING_SYNC',
            'checks':len(checked),'failures':failures,
            'scope':'Reporting and existing builder equality only; no raw-source rebuild, model refit, author approval or whole-repository certification.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path)
    args=p.parse_args();report=check()
    text=json.dumps(report,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
    print(text,end='')
    raise SystemExit(0 if not report['failures'] else 1)
