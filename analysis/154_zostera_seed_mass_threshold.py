#!/usr/bin/env python3
"""Observed viable seed mass ranks and hypothetical filtering; no survival model fitted."""
import argparse,csv,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
FILES={'original':('Seed_mass.csv','460a7ec2e3388863a10d547b758d2f70e7199430d2f16ba564f9005c3a7ff06d',844), 'high_locus':('Seed_mass_-_reduced_dataset.csv','3844e2767ccbbaf228e679063c9eb35e15fdb8c80ba6308abe2235ec09d6e79e',693)}
FRACTIONS=(.75,.50,.25)
def load(root,name,sha,n):
    raw=(root/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('source member hash drift')
    rows=[];keys=set()
    for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))):
        k=tuple(int(r[x]) for x in ('Site','Maternal ID','Rhipidium','Spathe','Seed'))
        f=r['Paternal ID'].strip();s=r['Selfed'];w=float(r['Mass'])
        if k in keys or not f or s not in ('Selfed','Outcrossed') or not math.isfinite(w) or w<=0:raise ValueError('source row')
        keys.add(k);rows.append((k,f,s,w))
    if len(rows)!=n:raise ValueError('source count')
    return rows
def pair_count(c):return sum(v*(v-1)/2 for v in c.values())
def condition_null(rows, selected):
    # Within mother x reproductive branch x spathe x mating label, retain exact observed k.
    groups=defaultdict(list); counts=Counter()
    for k,f,s,w in rows:
        h=(k[:4],s);groups[h].append(f)
        if k in selected:counts[h]+=1
    exp_pairs=0.;prior=Counter(); active=0
    for h,fs in groups.items():
        n=len(fs);k=counts[h];c=Counter(fs)
        if 0<k<n and len(c)>1:active+=1
        if n>1:exp_pairs+=pair_count(c)*k*(k-1)/(n*(n-1))
        curr={f:k*v/n for f,v in c.items()}
        exp_pairs+=sum(v*prior[f] for f,v in curr.items());prior.update(curr)
    return exp_pairs,active

def compute(rows):
    out=[]
    for site in sorted({r[0][0] for r in rows}):
        v=[r for r in rows if r[0][0]==site];N=len(v);base=pair_count(Counter(r[1] for r in v))/math.comb(N,2)
        for fraction in FRACTIONS:
            threshold=sorted((r[3] for r in v),reverse=True)[math.ceil(N*fraction)-1]
            kept=[r for r in v if r[3]>=threshold];n=len(kept);c=Counter(r[1] for r in kept);den=math.comb(n,2)
            obs=pair_count(c)/den;null,active=condition_null(v,{r[0] for r in kept});null/=den
            out.append(dict(site=site,target_fraction=fraction,threshold_mg=threshold,N=N,retained=n,retained_fraction=n/N,observed_sires=len(c),full_same_sire_pair_probability=base,retained_same_sire_pair_probability=obs,conditional_null_same_sire_pair_probability=null,ratio_to_full=obs/base,ratio_to_conditional_null=obs/null if null else None,active_strata=active))
    return out

def analyze(root):
    out={}
    for label,(name,sha,n) in FILES.items():
        rows=load(root,name,sha,n)
        out[label]={'sha256':sha,'all':compute(rows),'outcross_only':compute([r for r in rows if r[2]=='Outcrossed'])}
    return {'status':'posthoc_hypothetical_mass_threshold_on_observed_viable_seeds','source_doi':'10.5061/dryad.6t1g1jx7p','datasets':out,'limitations':['Mass rank threshold is a scenario, not observed mortality or fitted survival. Include all ties at cutoff.','Compare probability of same sire among two distinct retained seeds, not inverse Simpson or effective population size.','Unstratified random thinning at same n has expected pair probability equal to full sample. Conditional reference fixes selected counts in each maternal branch x spathe x mating-label cell, then samples uniformly; no p-values or causal test.','Only genotyped viable seeds observed; no individual germination or establishment. Three sites, overlapping source versions; no independent replicate counts across thresholds.']}

def selftest():
    rows=[((1,1,1,1,i),f,'Outcrossed',float(i)) for i,f in enumerate(['a','a','b','b'],1)]
    v,a=condition_null(rows,{rows[0][0],rows[1][0]});assert abs(v-1/3)<1e-12 and a==1
    v,a=condition_null(rows,{r[0] for r in rows});assert v==2 and a==0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('external_reproductive/seed_mass'));a=p.parse_args();selftest();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
