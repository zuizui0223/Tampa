#!/usr/bin/env python3
"""Source-locked scenario only: published two-class contrasts on independent seed mass data.
No calibrated transfer from 2019 dry mass to 2025 measured mass; no actual survival.
Locally executed on artifact 14916683079, SHA256 2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8.
Posthoc: 2019 DOI 10.1371/journal.pone.0215157 reported small/large
6 cm emergence .200/.293, and overall viable unemerged .231/.372.
These are separate endpoints, not sequential probabilities or new 2019 fits.
"""
import argparse,csv,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
FILES={'original':('Seed_mass.csv','460a7ec2e3388863a10d547b758d2f70e7199430d2f16ba564f9005c3a7ff06d',844),'high_locus':('Seed_mass_-_reduced_dataset.csv','3844e2767ccbbaf228e679063c9eb35e15fdb8c80ba6308abe2235ec09d6e79e',693)}
SCENARIOS={'equal_emergence':(.2,.2),'six_cm_emergence_illustration':(.2,.293),'unemerged_viability_illustration':(.231,.372)}
def load(root,name,sha,n):
    raw=(root/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('source drift')
    rows=[];keys=set()
    for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))):
        k=tuple(int(r[x]) for x in ('Site','Maternal ID','Rhipidium','Spathe','Seed'))
        f=r['Paternal ID'].strip();st=r['Selfed'];w=float(r['Mass'])
        if k in keys or not f or st not in ('Selfed','Outcrossed') or not math.isfinite(w) or w<=0:raise ValueError('row')
        keys.add(k);rows.append((k,f,st,w))
    if len(rows)!=n:raise ValueError('count')
    return rows
def pairs(v):
    return ((sum(v)**2)-sum(x*x for x in v))/2
def measures(rows,lo,hi):
    N=len(rows);threshold=sorted((r[3] for r in rows),reverse=True)[math.ceil(N/2)-1]
    p=[hi if r[3]>=threshold else lo for r in rows]
    by_f=defaultdict(list);by_h=defaultdict(list)
    for row,w in zip(rows,p):
        k,f,s,_=row;by_f[f].append(w);by_h[(k[:4],s)].append((f,w))
    den=pairs(p);num=sum(pairs(v) for v in by_f.values());base=sum(math.comb(len(v),2) for v in by_f.values())/math.comb(N,2)
    prior=Counter();null=0.;active=0
    for group in by_h.values():
        f=Counter(x[0] for x in group);w=[x[1] for x in group];n=len(w)
        if n>1:
            null+=sum(math.comb(k,2) for k in f.values())*pairs(w)/math.comb(n,2)
        active+=len(set(w))>1 and len(f)>1
        curr={g:k*sum(w)/n for g,k in f.items()}
        null+=sum(v*prior[g] for g,v in curr.items());prior.update(curr)
    c=num/den;ref=null/den
    return dict(N=N,threshold_mg=threshold,upper_count=sum(r[3]>=threshold for r in rows),lo=lo,hi=hi,expected_retained=sum(p),baseline_same_sire=base,weighted_same_sire=c,conditional_same_sire=ref,ratio_to_baseline=c/base,ratio_to_conditional=c/ref,active_strata=active)
def analyze(root):
    out={}
    for label,(name,sha,n) in FILES.items():
        rows=load(root,name,sha,n)
        out[label]={}
        for scope,rs in [('all',rows),('outcross_only',[r for r in rows if r[2]=='Outcrossed'])]:
            out[label][scope]={str(site):{s:measures([r for r in rs if r[0][0]==site],*p) for s,p in SCENARIOS.items()} for site in (1,2,3)}
    return {'status':'hypothetical_independent_bernoulli_weights_not_a_survival_fit','seed_mass_doi':'10.5061/dryad.6t1g1jx7p','published_contrast_doi':'10.1371/journal.pone.0215157','datasets':out,'limitations':['Upper half of 2025 measured mass within site/scope, including ties; not calibrated to 2019 visually sorted and separately dry-weighed classes.','Independent retention assumed. Report ratio of expected same-sire retained pairs to expected all retained pairs, not expectation of the realized sample ratio.','Conditional null permutes probability labels within mother x rhipidium x spathe x selfing status; exact expectation, no p-value.','Unemerged viability contrast is not emergence/survival; keep it a separate illustrative endpoint.','Original/high-locus cohorts overlap; no actual descendant genotypes or survival measured.']}
def selftest():
    rs=[((1,1,1,1,i),f,'Outcrossed',float(i)) for i,f in enumerate(('a','a','b','c'),1)]
    a=measures(rs,.2,.2);assert abs(a['ratio_to_baseline']-1)<1e-12 and abs(a['ratio_to_conditional']-1)<1e-12
    import itertools
    n=0.;d=0.
    for ii in itertools.combinations(range(4),2):
        p=[.3 if i in ii else .2 for i in range(4)];n+=p[0]*p[1];d+=pairs(p)
    assert abs(measures(rs,.2,.3)['conditional_same_sire']-n/d)<1e-12
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('external_reproductive/seed_mass'));a=p.parse_args();selftest();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
