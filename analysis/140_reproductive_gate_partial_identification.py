"""Exploratory partial-identification and serial-gate model from original published workbooks.
Usage: python analyze.py ARTIFACT.zip --out results.json
"""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
from collections import defaultdict
import numpy as np
from openpyxl import load_workbook

HASH='144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c'

def run(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        manifest=json.loads(z.read('manifest.json'))
        def rows(name):
            b=z.read(name)
            assert hashlib.sha256(b).hexdigest()==next(x['sha256'] for x in manifest['sources'] if x.get('file')==name)
            return list(load_workbook(io.BytesIO(b),data_only=True).active.values)
        w=rows('infantes_one_week.xlsx')
        f=rows('meysick_seed_trapping.xlsx')
    assert w[2][:6]==('Trial','LABEL','CODE','TREATMENT','Seeds','Art. Seeds')
    assert f[1][:8]==('Treatment No','Description','Lateral width of objects (cm)','No objects in flume','Flow velocity (cm/s)','Scouring area (cm2)','Trapped seeds','No seeds')
    arms=['CAGE','CAGE-HAND','CAGE-SAND'] # A=no crab surface, B=crab surface, C=crab buried
    g=defaultdict(list); seen=set()
    for trial,lab,_,t,k,m,*rest in w[3:]:
        if t not in arms: continue
        assert (trial,lab) not in seen and 0<=k<=200 and 0<=m<=20
        seen.add((trial,lab)); g[t,trial].append((k/200,m/20))
    assert len(seen)==18 and all(len(g[t,j])==3 for t in arms for j in [2,3])
    # axis: treatment, trial, plot, endpoint (real, mimic).
    arr=np.array([[g[t,j] for j in [2,3]] for t in arms])
    means=arr.mean(axis=2)
    def contrast(a):
        A,B,C=a[...,0,:],a[...,1,:],a[...,2,:]
        return {'crab_removal_surface':A[...,0]-B[...,0], 'burial_with_crab':C[...,0]-B[...,0],
            'substitution_lower_bound':A[...,0]+C[...,0]-B[...,0]-1,
            'substitution_upper_bound':A[...,0]+C[...,0]-B[...,0],
            'relative_rr_ratio_lower_bound':A[...,0]*C[...,0]/B[...,0],
            'burial_real_minus_mimic_contrast':(C[...,0]-B[...,0])-(C[...,1]-B[...,1]),
            'removal_real_minus_mimic_contrast':(A[...,0]-B[...,0])-(A[...,1]-B[...,1])}
    overall=means.mean(axis=1)
    obs=contrast(overall)
    rng=np.random.default_rng(20261124); B=50000
    draws=np.array([[arr[i,j][rng.integers(0,3,size=(B,3))].mean(axis=1) for j in range(2)] for i in range(3)]).mean(axis=1).transpose(1,0,2)
    cb=contrast(draws)
    boot={k:np.quantile(v,[.025,.975]).tolist() for k,v in cb.items()}
    bytrial={str(j):{k:float(v) for k,v in contrast(means[:,i,:]).items()} for i,j in enumerate([2,3])}
    # Only equal short-shoot count contrast, additional bivalve structure not diversity alone.
    grid=defaultdict(dict)
    for t,desc,width,nobj,v,scour,k,n,*loc in f[2:]:
        assert n==30 and 0<=k<=n and v not in grid[t]
        grid[t][v]={'trapped':k/n,'desc':desc,'width_cm':width,'n_objects':nobj}
    vs=list(range(12,31,2)); assert all(set(x)==set(vs) for x in grid.values()) and len(grid)==16
    records=[]
    for v in vs:
        a,b=grid[2][v],grid[16][v]
        assert a['trapped']>0 and b['trapped']>a['trapped']
        records.append({'flow_cm_s':v,'short_shoot_trapping':a['trapped'],'mixed_trapping':b['trapped'],
                        'break_even_predation_risk_ratio':a['trapped']/b['trapped'],
                        'minimum_predation_risk_reduction_for_substitution':1-a['trapped']/b['trapped']})
    ta=np.mean([r['short_shoot_trapping'] for r in records]); tb=np.mean([r['mixed_trapping'] for r in records])
    thresholds=[r['minimum_predation_risk_reduction_for_substitution'] for r in records]
    return {'schema':'tampa.reproductive_gate_partial_identification.v1','source_artifact_sha256':HASH,
        'status':'post-hoc original-workbook partial identification and theoretical thresholds; no causal otter effect estimate',
        'field':{'arms':arms,'trials':[2,3],'plots_per_arm_trial':3,'means_real_mimic':overall.tolist(),
                 'contrasts':{k:float(v) for k,v in obs.items()},'conditional_plot_bootstrap_percentile_95':boot,
                 'bootstrap_seed':20261124,'bootstrap_draws':B,'by_trial':bytrial,
                 'missing_arm':'no-crab + sand within cage; bound recovery probability in [0,1]'},
        'serial_gate':{'model':'R=S*T*(1-q)*E; perfect predator control delta=S*T*q*E. Assuming S,E unchanged, engineer modifies delta by T1*q1-T0*q0. Substitution if q1/q0<T0/T1. No estimation of q1/q0 in flume.',
            'treatment_2':'10 short shoots','treatment_16':'10 short shoots, 6 mussels, 3 oysters',
            'rows':records,'equal_flow_mean_short':float(ta),'equal_flow_mean_mixed':float(tb),
            'threshold_if_same_q0_and_q_ratio_across_flow':float(1-ta/tb),'threshold_range':[float(min(thresholds)),float(max(thresholds))]},
        'limitations':['Recovery, not actual germination/survival; real/mimic transport differs.', 'Bound is on additive probability scale at observed means, not identified missing arm, no mechanism inference; ceiling constrains it.', 'Bootstrap conditions on two observed trial periods, no between-estuary uncertainty.', 'Flume has one trial per treatment x flow cell; scenario thresholds are not independent replication; structures differ in width and density.', 'No jointly measured retention and predation or otter intervention; q ratio unknown.']}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(run(a.artifact),indent=2)+'\n')
