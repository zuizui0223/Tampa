#!/usr/bin/env python3
"""Exploratory conditional compositional overlap reference, not a causal randomization test."""
import argparse, collections, hashlib, json, math, random, statistics, zipfile
from pathlib import Path

ARCHIVE='31d4831e2efa3552e58db32a70fefccf6dcad5049e2bed4f2ca09d984b547e06'
INNER='9727c28d4dafcd225a754f2439e010fe09f2835dfbeefe03b28cc5d8f940facf'
S=['CR_PA','CS_PA','EA_PA','HC_PA','HD_PA','HO_PA','HS_PA','HT_PA','HU_PA','SI_PA','TC_PA','TH_PA','ZC_PA']
SPECS={'lobster':('Torres Strait lobster surveys',1,1570,1570,503,416),'cucumber':('Torres Strait sea cucumber surveys',2,1036,1034,99,98)}

def read_panels(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=ARCHIVE: raise ValueError('archive identity drift')
    with zipfile.ZipFile(path) as z: raw=z.read('torres_survey_points.geojson')
    if hashlib.sha256(raw).hexdigest()!=INNER: raise ValueError('inner identity drift')
    features=json.loads(raw)['features']
    assert len(features)==28732
    out={}
    for name,(survey,lag,n,uniq,npos,nboth) in SPECS.items():
        rows=collections.defaultdict(dict);count=0
        for f in features:
            p=f['properties']
            if p['Survey']!=survey: continue
            count+=1;st=tuple(f['geometry']['coordinates']);y=int(p['Year'])
            assert p['Month']=='Contact data custodian'
            assert all(p[k] in (0,1) for k in S)
            taxa=frozenset(k for k in S if p[k]==1)
            assert len(taxa)==p['SG_species'] and bool(taxa)==bool(p['SG_present'])
            d=float(p['Depth_MSL']); assert math.isfinite(d)
            val=(taxa,d)
            assert y not in rows[st] or rows[st][y]==val
            rows[st][y]=val
        assert count==n and sum(map(len,rows.values()))==uniq
        pairs=[];positive=0
        for st,years in sorted(rows.items()):
            for y0,y1 in zip(sorted(years),sorted(years)[1:]):
                if y1-y0!=lag:continue
                s,d=years[y0];t,d1=years[y1];assert d==d1
                if not s: continue
                positive+=1
                if t:pairs.append((st,y1,s,t,d))
        assert positive==npos and len(pairs)==nboth
        out[name]=pairs
    return out

def metrics(s,t):
    k=len(s&t)
    return (k/len(s), k/len(s|t), float(k==0))

def evaluate(pairs,depth_width,seed=20261127,draws=999):
    # Match target year and exact observed source/target richness. Optionally depth bin.
    # Conditioning on both endpoints being positive defines a descriptive reference, not a treatment effect.
    groups=collections.defaultdict(list)
    for p in pairs:
        st,y,s,t,d=p
        key=(y,len(s),len(t),None if depth_width is None else math.floor(d/depth_width))
        groups[key].append(p)
    rows=[];movable=[]
    for group in groups.values():
        if len(group)<2:continue
        # If all candidate target compositions identical, no assemblage can actually change.
        if len({x[3] for x in group})<2:continue
        movable.append(group);rows.extend(group)
    n=len(rows)
    if n==0:return {'estimable':False,'all_pairs':len(pairs),'movable_pairs':0}
    obs=[sum(metrics(p[2],p[3])[k] for p in rows)/n for k in range(3)]
    expected=[0.]*3
    for group in movable:
        m=len(group)
        for p in group:
            for target in group:
                v=metrics(p[2],target[3])
                for k in range(3):expected[k]+=v[k]/m/n
    r=random.Random(seed);sim=[[] for _ in range(3)]
    for _ in range(draws):
        v=[0.]*3
        for group in movable:
            ts=[p[3] for p in group];r.shuffle(ts)
            for p,t in zip(group,ts):
                a=metrics(p[2],t)
                for k in range(3):v[k]+=a[k]/n
        for k in range(3):sim[k].append(v[k])
    out={}
    for k,label in enumerate(['prior_taxon_retention','jaccard','no_shared_taxon']):
        ss=sorted(sim[k]);out[label]={'observed':obs[k],'expected':expected[k],'difference':obs[k]-expected[k],
            'shuffle_reference_2.5_97.5':[ss[int(.025*(draws-1))],ss[int(.975*(draws-1))]]}
    return {'estimable':True,'all_pairs':len(pairs),'movable_pairs':n,'movable_fraction':n/len(pairs),
            'movable_stations':len({p[0] for p in rows}),'movable_strata':len(movable),'all_strata':len(groups),'metrics':out}

def selftest():
    a=frozenset({'A'});b=frozenset({'B'})
    r=evaluate([((0,0),1,a,a,1.),((1,1),1,b,b,1.)],2,draws=99)
    assert r['movable_pairs']==2 and abs(r['metrics']['prior_taxon_retention']['expected']-.5)<1e-12
    assert abs(r['metrics']['no_shared_taxon']['expected']-.5)<1e-12
    assert not evaluate([((0,0),1,a,a,1.)],2,draws=99)['estimable']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('archive',nargs='?');ap.add_argument('out',nargs='?');ap.add_argument('--selftest',action='store_true')
    a=ap.parse_args();selftest()
    if a.selftest:return
    panels=read_panels(a.archive)
    result={'archive_sha256':ARCHIVE,'inner_sha256':INNER,'primary_reference':'same target year, exact initial and later richness, 2m depth bins','panels':{},'limits':['Response-open diagnostic; conditioning on observed target richness and presence is not a prospective forecast.','Candidate target assemblages are permuted within matching strata; repeated stations, spatial autocorrelation and detection can violate exchangeability. Reference quantiles are not inferential confidence intervals or causal p-values.','Restricted to movable pairs; different matching widths may select different populations. No evidence of animal-mediated transport or true taxon survival.']}
    for nm,p in panels.items():
        result['panels'][nm]={str(w):evaluate(p,w) for w in [2,1,5,None]}
    Path(a.out).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
