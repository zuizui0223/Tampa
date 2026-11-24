#!/usr/bin/env python3
"""Paired epiphyte and aboveground biomass in Donaher experiment 1.
Repeated plot covariance, not causal mediation or independent study replicates.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd
FILES={'Exp1_Epiphyte_All.xlsx':'486e973c0de103142ca129423cf2be3436937896c762bcd118e7ebd488c02e76','Exp1_BiomassCores_All.xlsx':'b728f7b1df148e0ea0945ddfca4af1266cfd9c88233e028d0fc337b736360e76'}
KEY=['Sample ID','Year','Month','Species','Treatment','Clam','Experiment']
ENDPOINTS=['Epiphyte','Above Sample Weight']
SIGN=np.array([-1.,1.])
CONTEXTS=[(2019,m,s) for m in ('MAY','JULY') for s in ('HALODULE','ZOSTERA')]
def read(root,name):
    p=root/name
    if hashlib.sha256(p.read_bytes()).hexdigest()!=FILES[name]:raise ValueError('source drift '+name)
    return pd.read_excel(p,sheet_name=1)
def ratios(a,b):
    m,n=a.mean(0),b.mean(0)
    if (m<=0).any() or (n<=0).any():raise ValueError('nonpositive means')
    return np.log(n/m)*SIGN
def analyze(root):
    e,b=[read(root,name) for name in FILES]
    assert len(e)==320 and len(b)==192 and e['Sample ID'].nunique()==b['Sample ID'].nunique()==32
    for d in (e,b):
        assert not d.duplicated(KEY[:4]).any()
        assert set(d.Clam)=={'YES','NO'} and set(d.Experiment)=={'PRESS'}
        assert (d.Clam==d.Treatment.map({'C':'YES','CN':'YES','N':'NO','S':'NO'})).all()
        assert d.groupby('Sample ID').Clam.nunique().eq(1).all()
    x=e.merge(b,on=KEY,validate='one_to_one')
    assert len(x)==192 and ((x.Elevation-x['Elevation 2018'].where(x.Year==2018,x['Elevation 2019'])).abs()<1e-8).all()
    groups={};arr={t:[] for t in ('NO','YES')};aids={t:sorted(e.loc[e.Clam==t,'Sample ID'].unique()) for t in arr}
    for key,d in x.groupby(['Year','Month','Species']):
        group={};arrays=[]
        for t in arr:
            g=d[d.Clam==t].set_index('Sample ID').reindex(aids[t]);raw=g[ENDPOINTS].to_numpy(float);ok=np.isfinite(raw).all(1)
            assert len(raw)==16 and np.nanmin(raw)>=0 and ok.sum()>=10
            y=raw[ok];arrays.append(y)
            group[t]={'complete_plots':int(ok.sum()),'means':y.mean(0).tolist(),'endpoint_available_means':np.nanmean(raw,axis=0).tolist(),'missing_by_endpoint':np.isnan(raw).sum(0).tolist()}
        v=ratios(*arrays);group.update(oriented_log_response_ratios=v.tolist(),percent_change=(np.exp(v*SIGN)-1).tolist())
        groups['|'.join(map(str,key))]=group
    effects=[];influence={t:[] for t in arr};all_present={t:np.ones(16,bool) for t in arr}
    for year,month,species in CONTEXTS:
        d=x[(x.Year==year)&(x.Month==month)&(x.Species==species)]
        data={t:d[d.Clam==t].set_index('Sample ID').reindex(aids[t])[ENDPOINTS].to_numpy(float) for t in arr}
        keep={t:np.isfinite(z).all(1) for t,z in data.items()}
        means={t:data[t][keep[t]].mean(0) for t in arr}
        effects.extend(np.log(means['YES']/means['NO'])*SIGN)
        for t in arr:
            k=keep[t];z=np.zeros((16,2));z[k]=(data[t][k]-means[t])/means[t]/k.mean()*SIGN
            influence[t].append(z);all_present[t]&=k
    C=sum(np.cov(np.column_stack(influence[t]),rowvar=False)/16 for t in arr)
    effects=np.array(effects);se=np.sqrt(np.diag(C));labels=[f'{y}|{m}|{s}|{a}' for y,m,s in CONTEXTS for a in ('epiphyte_reduction','aboveground_biomass')]
    panel={}
    for year,month,species in CONTEXTS:
        d=x[(x.Year==year)&(x.Month==month)&(x.Species==species)]
        q=[d[d.Clam==t].set_index('Sample ID').reindex(aids[t])[ENDPOINTS].to_numpy(float)[all_present[t]] for t in arr]
        panel[f'{year}|{month}|{species}']=ratios(*q).tolist()
    changes={}
    for i,s in enumerate(('HALODULE','ZOSTERA')):
        D=np.zeros((2,8));D[:,i*2:i*2+2]=-np.eye(2);D[:,4+i*2:6+i*2]=np.eye(2)
        changes[s]={'july_minus_may':(D@effects).tolist(),'covariance':(D@C@D.T).tolist(),'se':np.sqrt(np.diag(D@C@D.T)).tolist()}
    return {'status':'one_study_matched_plot_endpoint_extraction_not_pooled_meta_analysis','study_doi':'10.1002/ecs2.3804','data_doi':'10.5061/dryad.9cnp5hqh7','source_hashes':FILES,'plot_count':32,'matched_rows':len(x),'groups':groups,'primary_2019':{'labels':labels,'estimate':effects.tolist(),'se':se.tolist(),'sampling_covariance':C.tolist(),'sampling_correlation':(C/np.outer(se,se)).tolist(),'july_minus_may':changes,'common_complete_panel_plot_n':{t:int(v.sum()) for t,v in all_present.items()},'common_complete_panel_estimates':panel},'limitations':['Experiment 1 only; resident clams not removed; 16 plots per assigned arm. C and CN pooled, N and S pooled using deposited Clam assignment. Same plot sampled repeatedly, not eight independent studies.','Use paper-reported biomass months May/July 2019 primary; July 2018 deposited biomass retained as exploratory descriptive sensitivity. Match year/month/species/plot, not same leaf or exact date.','Epiphyte chl a per blade area and aboveground dry mass per core; not total epiphyte mass per plot or whole plant productivity. No combined belowground biomass added across species.','Complete-pair contrasts condition on observed endpoints; no missing values assigned zero. Common panel sensitivity is post-outcome selection.','Delta covariance conditional on independent plots within treatment, no elevation adjustment or temporal causal inference. Differences in season effects descriptive, not causal mediation or treatment interaction claims.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('transmission_sources/donaher_2021'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
