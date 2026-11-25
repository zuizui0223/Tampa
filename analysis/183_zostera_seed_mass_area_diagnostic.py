#!/usr/bin/env python3
"""Size-conditioned first/last spathe mass diagnostic, not maturation correction."""
import argparse, hashlib, io, json, zipfile, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
ARCHIVE='2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8'
FILES={'Seed_mass.csv':'460a7ec2e3388863a10d547b758d2f70e7199430d2f16ba564f9005c3a7ff06d','Seed_area.csv':'4349e7b4b482027b66d7e33ad018165d205600c28af94806a24a9bc67a1f25cb'}
K=['Site','Maternal ID','Rhipidium','Spathe','Seed']
B=20000

def slope(x):
    g=x.groupby(K[:4]);a=x.la-g.la.transform('mean');b=x.lm-g.lm.transform('mean');assert a@a>0
    return float((a@b)/(a@a))

def report(rows):
    if not rows:return {'pairs':0}
    d=pd.DataFrame(rows);cols=['dm','da','dr','dr15','dr_pool'];m=d.groupby(K[:3])[cols].mean().groupby(level=[0,1]).mean();rng=np.random.default_rng(20261125);boot=np.zeros((B,len(cols)))
    for _,g in m.groupby(level=0):
        v=g.to_numpy();boot+=v[rng.integers(len(v),size=(B,len(v)))].sum(1)
    boot/=len(m);mu=m.mean();ci=np.quantile(boot,[.025,.975],axis=0).T
    return {'rows':len(d),'branches':d.groupby(K[:3]).ngroups,'mothers':len(m),'mean_log_contrasts':mu.to_dict(),'percent_changes_geometric':(100*np.expm1(mu)).to_dict(),'conditional_mother_bootstrap_percent_95':dict(zip(cols,(100*np.expm1(ci)).tolist())),'negative_mothers':(m<0).sum().to_dict(),'site_mean_log_contrasts':{str(i):g.mean().to_dict() for i,g in m.groupby(level=0)},'leave_one_site_out_residual_percent':{str(i):float(100*np.expm1(m.loc[m.index.get_level_values(0)!=i,'dr'].mean())) for i in m.index.get_level_values(0).unique()} if m.index.get_level_values(0).nunique()>1 else {},'records':rows}

def analyze(path):
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ARCHIVE
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        data={k:z.read('seed_mass/'+k) for k in FILES};assert all(hashlib.sha256(v).hexdigest()==FILES[k] for k,v in data.items());m,a=[pd.read_csv(io.BytesIO(v),dtype={'Paternal ID':str}) for v in data.values()]
    assert (len(m),len(a))==(844,873)
    j=m.merge(a,on=K,validate='one_to_one',suffixes=('_m','_a'));assert len(j)==839 and j.groupby(K[:2]).ngroups==35
    audit={k:int((j[k+'_m'].fillna('NA')!=j[k+'_a'].fillna('NA')).sum()) for k in ('Selfed','Paternal ID','Offspring Heterozygosity','Maternal Heterozygosity','Paternal Heterozygosity','Seeds per Shoot')};assert audit['Selfed']==audit['Paternal ID']==audit['Offspring Heterozygosity']==0
    assert (j[['Mass','Area']]>0).all().all() and np.isfinite(j[['Mass','Area']]).all().all()
    j['lm']=np.log(j.Mass);j['la']=np.log(j.Area)
    calibration={};bounds={};panels={k:[] for k in ('all','outcross','self','shared_outcross','shared_outcross_min2','overlap_all')};matches={f'{cls}|{tol}':[] for cls in ('all','same_class','outcross') for tol in (.05,.10,.20)}
    for (site,mom),g in j.groupby(K[:2]):
        train=j[(j.Site!=site)|(j['Maternal ID']!=mom)];beta=slope(train);beta_pool=float(np.cov(train.la,train.lm)[0,1]/np.var(train.la,ddof=1));calibration[f'{site}|{mom}']={'within_spathe':beta,'pooled':beta_pool}
        for branch,h in g.groupby('Rhipidium'):
            src=m[(m.Site==site)&(m['Maternal ID']==mom)&(m.Rhipidium==branch)];lo,hi=src.Spathe.min(),src.Spathe.max()
            if lo==hi:continue
            x,y=h[h.Spathe==lo],h[h.Spathe==hi]
            if min(len(x),len(y))==0:continue
            rec={**dict(zip(K[:3],map(int,(site,mom,branch)))),'first':int(lo),'last':int(hi),'beta':beta,'beta_pool':beta_pool}
            def entry(u,v,**extra):
                dm=float(v.lm.mean()-u.lm.mean());da=float(v.la.mean()-u.la.mean());return dict(**rec,n0=len(u),n1=len(v),dm=dm,da=da,dr=dm-beta*da,dr15=dm-1.5*da,dr_pool=dm-beta_pool*da,**extra)
            panels['all'].append(entry(x,y))
            if max(x.la.min(),y.la.min())<=min(x.la.max(),y.la.max()):
                low=max(x.la.min(),y.la.min());high=min(x.la.max(),y.la.max());u,v=x[x.la.between(low,high)],y[y.la.between(low,high)]
                if len(u) and len(v):panels['overlap_all'].append(entry(u,v))
            for cls,label in [('Outcrossed','outcross'),('Selfed','self')]:
                u,v=x[x.Selfed_m==cls],y[y.Selfed_m==cls]
                if min(len(u),len(v))==0:continue
                panels[label].append(entry(u,v))
                if label=='outcross':
                    for sire,ss in u.groupby('Paternal ID_m'):
                        tt=v[v['Paternal ID_m']==sire]
                        if len(tt):
                            panels['shared_outcross'].append(entry(ss,tt,sire=sire))
                            if min(len(ss),len(tt))>=2:panels['shared_outcross_min2'].append(entry(ss,tt,sire=sire))
            # Max-cardinality then minimum-log-area-distance matching of distinct seeds,
            # within same branch, endpoint rank fixed; no matching on mass.
            for cls in ('all','same_class','outcross'):
                u,v=(x[x.Selfed_m=='Outcrossed'],y[y.Selfed_m=='Outcrossed']) if cls=='outcross' else (x,y)
                if min(len(u),len(v))==0:continue
                dist=np.abs(u.la.to_numpy()[:,None]-v.la.to_numpy()[None,:])
                for tol in (.05,.10,.20):
                    valid=dist<=math.log1p(tol)+1e-12
                    if cls=='same_class':valid&=u.Selfed_m.to_numpy()[:,None]==v.Selfed_m.to_numpy()[None,:]
                    cost=np.where(valid,dist,1000.)
                    ii,jj=linear_sum_assignment(cost);ok=valid[ii,jj];ii,jj=ii[ok],jj[ok]
                    if len(ii):matches[f'{cls}|{tol}'].append(entry(u.iloc[ii],v.iloc[jj],max_area_ratio=float(np.exp(dist[ii,jj].max()))))
    return {'status':'area_conditioned_descriptive_diagnostic_not_maturity_or_causal_resource_effect','source_archive_sha256':ARCHIVE,'member_hashes':FILES,'mass_n':len(m),'area_n':len(a),'matched_n':len(j),'mothers':35,'audit_disagreements':audit,'within_spathe_slope_all':slope(j),'training_slope_range':[min(v['within_spathe'] for v in calibration.values()),max(v['within_spathe'] for v in calibration.values())],'calibration':calibration,'panels':{k:report(v) for k,v in panels.items()},'matched_area_sensitivity':{k:report(v) for k,v in matches.items()},'limits':['One collection date, seed age and maturity, water content, thickness and reserve concentration unknown. Cross-sectional area is not volume or development time. Residual mass is not density, dry storage mass, resource allocation or final seed size.','Whole maternal shoot held out when fitting within-spathe log mass/log area slope. Regression slope is a conditional descriptive reference; residual is a log-ratio accounting contrast, not a causal direct effect. Fixed slope 1.5 is similar-shape constant-density geometric reference only.','First and last observed spathe rank defined in mass table before restricting to matched size records. Equal shared-sire rows within branch, equal branches within mother and equal mothers. Bootstrap of precomputed contrasts within three sites; conditions on fitted slopes and selected records, not full uncertainty of estimated slope.','Area matching within same branch endpoints with max cardinality and minimum absolute log area distance; equal branch then mother weights. Conditioning on size selects subsets and may induce bias. No causal effect or proof of mature mass differences.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.archive),indent=2,sort_keys=True,allow_nan=False)+'\n')
