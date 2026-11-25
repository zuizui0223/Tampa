#!/usr/bin/env python3
"""Posthoc seed-count vs mass-weighted sire diversity, conditional on sampled viable seeds.
Sgambelluri et al. 2025, Dryad 10.5061/dryad.6t1g1jx7p. No fitness inference.
"""
import argparse,csv,hashlib,io,json
from collections import defaultdict
from pathlib import Path
import numpy as np
FILES={'original':('Seed_mass.csv','460a7ec2e3388863a10d547b758d2f70e7199430d2f16ba564f9005c3a7ff06d',844,35,221),
       'high_locus':('Seed_mass_-_reduced_dataset.csv','3844e2767ccbbaf228e679063c9eb35e15fdb8c80ba6308abe2235ec09d6e79e',693,34,192)}

def load(root,f,h,n,m,g):
    raw=(root/f).read_bytes();assert hashlib.sha256(raw).hexdigest()==h
    out=[];ids=set()
    for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))):
        k=tuple(int(r[a]) for a in ('Site','Maternal ID','Rhipidium','Spathe','Seed'))
        if k in ids:raise ValueError('duplicate seed key')
        ids.add(k);w=float(r['Mass']);st=r['Selfed'];father=r['Paternal ID'].strip()
        assert w>0 and np.isfinite(w) and st in ('Selfed','Outcrossed') and father
        out.append((k,father,st,w))
    assert len(out)==n and len({r[0][:2] for r in out})==m and len({(r[0][0],r[1]) for r in out})==g
    return out

def hill(x):
    a=np.asarray(x,float);return float(a.sum()**2/(a@a))

def group_metrics(rows):
    fathers=defaultdict(list)
    for k,f,s,w in rows:fathers[f].append(w)
    c=hill([len(v) for v in fathers.values()]);m=hill([sum(v) for v in fathers.values()])
    return dict(seeds=len(rows),sires=len(fathers),count_hill2=c,mass_hill2=m,relative_change=m/c-1)

def diagnostics(rows,seed=20261124,B=1999):
    by_site=defaultdict(list);by_mom=defaultdict(list)
    for row in rows:
        by_site[row[0][0]].append(row);by_mom[row[0][:2]].append(row)
    moms={k:v for k,v in by_mom.items() if len({r[1] for r in v})>=2}
    mm={str(k):group_metrics(v) for k,v in moms.items()};observed=np.array([v['relative_change'] for v in mm.values()]);rng=np.random.default_rng(seed)
    # Conditional on maternal shoot, spathe and selfing class. Not a causal test.
    null=np.zeros(B);strata_permuted=0
    for k,v in moms.items():
        fid={f:i for i,f in enumerate(sorted({r[1] for r in v}))};idx=np.array([fid[r[1]] for r in v]);mass=np.array([r[3] for r in v]);c=hill(np.bincount(idx));strata=defaultdict(list)
        for i,r in enumerate(v):strata[(r[0][2:4],r[2])].append(i)
        active=[np.array(j) for j in strata.values() if len(j)>1 and len(set(idx[j]))>1];strata_permuted+=len(active)
        for b in range(B):
            w=mass.copy()
            for j in active:w[j]=rng.permutation(w[j])
            null[b]+=hill(np.bincount(idx,weights=w,minlength=len(fid)))/c-1
    null/=len(moms);obs=float(observed.mean())
    return dict(sites={str(k):group_metrics(v) for k,v in sorted(by_site.items())},mothers=mm,
        mother_summary={'informative':len(mm),'positive':int((observed>1e-12).sum()),'negative':int((observed< -1e-12).sum()),'median_relative_change':float(np.median(observed)),'mean_relative_change':obs},
        permutation_diagnostic={'strata':'mother x rhipidium x spathe x observed selfing label','active_strata':strata_permuted,'draws':B,'seed':seed,'observed_mother_equal_mean_change':obs,'null_mean':float(null.mean()),'null_q025_q975':np.quantile(null,[.025,.975]).tolist(),'upper_tail_fraction_plus_one':float((1+(null>=obs-1e-12).sum())/(B+1))})

def analyze(root):
    out={};keys={}
    for label,(f,h,n,m,g) in FILES.items():
        r=load(root,f,h,n,m,g);keys[label]={x[0]:x[3] for x in r}
        out[label]=dict(source_sha256=h,seed_rows=n,mothers=m,sires=g,all=diagnostics(r),outcross_only=diagnostics([x for x in r if x[2]=='Outcrossed']))
    shared=keys['original'].keys()&keys['high_locus'].keys()
    return {'status':'posthoc_viable_seed_representation_not_genetic_fitness','source_doi':'10.5061/dryad.6t1g1jx7p','datasets':out,'cross_table_key_overlap':len(shared),'shared_seed_mass_disagreements':sum(abs(keys['original'][k]-keys['high_locus'][k])>1e-9 for k in shared),
        'limits':['Use raw deposited cohorts separately, not paper cohort count or join to 2024 paternal IDs. The reduced CSV has 693 rows; published text describes 688 in a subset.','Mass-weighted Hill2 describes allocation of observed viable seed mass, not genetic effective size, realized descendants or fitness.','Three meadows; overlapping reruns, mother-level outputs not independent population replications.','Posthoc conditional shuffling is an exchangeability diagnostic, not a randomized treatment test. Within-spathe seed position and other biological differences can violate exchangeability.','No nonviable seed weights or genotypes, no causal inference on postzygotic selection.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('external_reproductive/seed_mass'));a=p.parse_args()
    assert hill([1,1])==2 and hill([1,3])==1.6
    print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
