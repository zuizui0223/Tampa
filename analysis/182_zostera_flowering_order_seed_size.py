#!/usr/bin/env python3
"""Matched spathe mass/area contrasts on source-coded viable, genotyped seeds.
No cross-publication join, no proof of final maturity or seedling recruitment.
"""
import argparse, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
ARCHIVE='2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8'
FILES={'Seed_mass.csv':('460a7ec2e3388863a10d547b758d2f70e7199430d2f16ba564f9005c3a7ff06d','Mass',844),'Seed_mass_-_reduced_dataset.csv':('3844e2767ccbbaf228e679063c9eb35e15fdb8c80ba6308abe2235ec09d6e79e','Mass',693),'Seed_area.csv':('4349e7b4b482027b66d7e33ad018165d205600c28af94806a24a9bc67a1f25cb','Area',873)}
K=['Site','Maternal ID','Rhipidium','Spathe']; B=20000

def summary(records,cols,by_sire=False):
    if not records:return {'rows':0,'mothers':0}
    x=pd.DataFrame(records);u=x.groupby(K[:3])[cols].mean() if by_sire else x.set_index(K[:3])[cols];assert u.index.is_unique
    m=u.groupby(level=[0,1]).mean();a=m.to_numpy();rng=np.random.default_rng(20261125);boot=np.zeros((B,len(cols)))
    for _,g in m.groupby(level=0):
        v=g.to_numpy();boot+=v[rng.integers(len(v),size=(B,len(v)))].sum(1)
    boot/=len(m)
    return {'rows':len(x),'branches':len(u),'mothers':len(m),'means':m.mean().to_dict(),'conditional_mother_bootstrap_95':dict(zip(cols,np.quantile(boot,[.025,.975],axis=0).T.tolist())),'negative_mothers':{c:int((m[c]<-1e-10).sum()) for c in cols if c.endswith('difference')},'site_means':{str(i):g.mean().to_dict() for i,g in m.groupby(level=0)},'records':records}

def rich(d,k):
    n=len(d);assert n>=k
    return sum(1-(math.comb(n-int(c),k)/math.comb(n,k) if n-c>=k else 0) for c in d['Paternal ID'].value_counts())

def relation(rows):
    if len(rows)<3:return None
    m=pd.DataFrame(rows).groupby(K[:2])[['richness_difference','size_difference']].mean()
    def corr(v):
        if len(v)<3 or (v.std()==0).any():return None
        r=float(v.corr().iloc[0,1]);return r if np.isfinite(r) else None
    c=m-m.groupby(level=0).transform('mean')
    return {'mothers':len(m),'both_negative':int(((m.richness_difference< -1e-10)&(m.size_difference< -1e-10)).sum()),'pearson':corr(m),'site_centered_pearson':corr(c),'leave_one_site_out_pearson':{str(i):corr(m[m.index.get_level_values(0)!=i]) for i in m.index.get_level_values(0).unique()}}

def analyze_panel(d,endpoint):
    assert not d.duplicated(K+['Seed']).any() and d['Paternal ID'].notna().all() and set(d.Selfed)=={'Selfed','Outcrossed'} and (d[endpoint]>0).all() and np.isfinite(d[endpoint]).all()
    outcomes={k:[] for k in ('all','outcross','self','outcross_k2','outcross_k3','shared_labels_all','shared_labels_outcross','shared_labels_outcross_min2','mixed_class_accounting')}
    for key,g in d.groupby(K[:3]):
        first,last=int(g.Spathe.min()),int(g.Spathe.max())
        if first==last:continue
        a,b=[g[g.Spathe==r] for r in (first,last)];rec=dict(zip(K[:3],map(int,key)),first_spathe=first,last_spathe=last)
        def entry(x,y):
            u,v=x[endpoint].mean(),y[endpoint].mean();return dict(**rec,n_first=len(x),n_last=len(y),size_first=float(u),size_last=float(v),size_difference=float(v-u))
        outcomes['all'].append(entry(a,b))
        for label,cls in [('outcross','Outcrossed'),('self','Selfed')]:
            x,y=[v[v.Selfed==cls] for v in (a,b)]
            if min(len(x),len(y))<1:continue
            outcomes[label].append(entry(x,y))
            if label=='outcross':
                for k in (2,3):
                    if min(len(x),len(y))>=k:
                        u,v=rich(x,k),rich(y,k);outcomes[f'outcross_k{k}'].append(dict(**entry(x,y),richness_first=u,richness_last=v,richness_difference=v-u))
        for (cls,sire),x in a.groupby(['Selfed','Paternal ID']):
            y=b[(b.Selfed==cls)&(b['Paternal ID']==sire)]
            if not len(y):continue
            q=dict(**entry(x,y),sire_label=sire,reproductive_mode=cls);outcomes['shared_labels_all'].append(q)
            if cls=='Outcrossed':
                outcomes['shared_labels_outcross'].append(q)
                if min(len(x),len(y))>=2:outcomes['shared_labels_outcross_min2'].append(q)
        if a.Selfed.nunique()==b.Selfed.nunique()==2:
            p,q=[(g.Selfed=='Outcrossed').mean() for g in (a,b)];u,v=[g.loc[g.Selfed=='Outcrossed',endpoint].mean() for g in (a,b)];s,t=[g.loc[g.Selfed=='Selfed',endpoint].mean() for g in (a,b)]
            comp=(q-p)*((u-s)+(v-t))/2;within=(q+p)/2*(v-u)+(1-(p+q)/2)*(t-s);delta=b[endpoint].mean()-a[endpoint].mean();assert math.isclose(comp+within,delta,abs_tol=1e-12)
            outcomes['mixed_class_accounting'].append(dict(**entry(a,b),composition_component=float(comp),within_class_component=float(within)))
    ans={}
    for k,v in outcomes.items():
        cols=['size_first','size_last','size_difference']
        if k.startswith('outcross_k'):cols+=['richness_first','richness_last','richness_difference']
        if k=='mixed_class_accounting':cols+=['composition_component','within_class_component']
        ans[k]=summary(v,cols,by_sire=k.startswith('shared_labels'))
        if k.startswith('outcross_k'):ans[k]['descriptive_change_association']=relation(v)
    return {'source_seeds':len(d),'source_mothers':d.groupby(K[:2]).ngroups,'source_spathes':d.groupby(K).ngroups,'endpoint':endpoint,'panels':ans}

def analyze(path):
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ARCHIVE;out={};data={}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for name,(sha,ep,n) in FILES.items():
            b=z.read('seed_mass/'+name);assert hashlib.sha256(b).hexdigest()==sha;d=pd.read_csv(io.BytesIO(b),dtype={'Paternal ID':str});assert len(d)==n;data[name]=d;out[name]=analyze_panel(d,ep)
    a=data['Seed_mass.csv'];b=data['Seed_mass_-_reduced_dataset.csv'];j=a.merge(b,on=K+['Seed'],validate='one_to_one',suffixes=('_main','_reduced'));assert len(j)==690 and np.allclose(j.Mass_main,j.Mass_reduced)
    return {'status':'posthoc_within_branch_size_and_sire_label_diagnostic','paper_doi':'10.1093/evolut/qpaf111','data_doi':'10.5061/dryad.6t1g1jx7p','archive_sha256':ARCHIVE,'member_hashes':{k:v[0] for k,v in FILES.items()},'shared_mass_reduced_seed_keys':len(j),'panels':out,'limits':['All sampled 4 May 2021, one collection date, spathe rank is a developmental/timing proxy; later seeds can be younger. Mass and area at collection are not final mature seed size or recruitment. Only viable, measured, genotyped seeds; no missing/nonviable seeds imputed.','Compare first and last observed spathe per branch, not necessarily first and last actual flower; hold endpoints fixed before subset filtering. Equal branch then mother weights, shared sire labels equal within each branch. Bootstrap mothers within three sites, conditional intervals, exploratory.','Same-sire labels inferred by COLONY, not directly observed parents; shared-label subset is selected and sample counts often one. Cannot infer controlled genetic effect or resource limitation.','Mixed-class decomposition restricted to pairs with both classes observed at both endpoints. Algebraic contributions, not causal fractions. No generalization to absent classes.','Rarefy sire-label count by whole outcross seeds, same endpoint pairs; descriptive correlation of changes not proof of diversity affecting mass. Three overlapping data panels, not independent replication. No individual matching to burial trials, no mass-to-emergence calibration.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();x=analyze(a.archive);a.out.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
