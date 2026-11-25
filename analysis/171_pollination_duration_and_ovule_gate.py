#!/usr/bin/env python3
"""Source-locked distributional and pollen supplementation diagnostics.
Penstemon independent day cohorts; Clarkia plot-by-focal-species pairs.
No cross-study pooling, individual mediation, or validation of taxon weights.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

HASHES={
 'penstemon_2026/Stigma_pollen_grains.xlsx':'5303c97e6a375a5911b1be80f2ceac88e101b71178ae74156dd2fe96be60025f',
 'penstemon_2026/Pollen_tubes_top.xlsx':'a6b1b2c509466c9f51a2cc70fc19bd05b3237d70ea893f8d3ea02323859654c7',
 'penstemon_2026/Pollen_tubes_base.xlsx':'44d7109f87e54c7994dae05bdea3e813d0477312055ce32a98ad4b682babf7bd',
 'penstemon_2026/Stigma_pollen_over_day_and_year.xlsx':'721f3e20bec484bdb039b87ec121d01f178ba80085b1a65d1fa4c83dd17b0d0f',
 'penstemon_2026/Seeds_over_day_and_year.xlsx':'4510076f82cf714e7f22a6d688ca6065e38d66e84e996d39e6159f0613e10e9e',
 'penstemon_2026/Single_visit_pollen_deposition.xlsx':'07685caae0120f6d108ccfdd098c8dad31c571735c580daf266ea25ec0199447',
 'penstemon_2026/Breed_system_data.xlsx':'dd9819ca180d8943bf025d043ee1639324ca642ef8b0b718a0ea375e5519d44b',
 'clarkia_reproduction/clarkia_data_2017_kingsnake.csv':'a6b82a14761f1de282148195d9a2d56f6ba355812419253b8a2cb24014fa0568'}
B=10000

def read(root,key):
    p=root/key
    if hashlib.sha256(p.read_bytes()).hexdigest()!=HASHES[key]:raise ValueError('source drift: '+key)
    return pd.read_excel(p,sheet_name=0) if p.suffix=='.xlsx' else pd.read_csv(p)

def dist(v):
    a=np.asarray(v,float);assert len(a)>0 and np.isfinite(a).all() and (a>=0).all()
    return {'n':len(a),'mean':float(a.mean()),'zero':int((a==0).sum()),'zero_fraction':float((a==0).mean()),'mean_positive':float(a[a>0].mean()) if (a>0).any() else None,'quantiles_10_25_50_75_90':np.quantile(a,[.1,.25,.5,.75,.9]).tolist()}

def year_summary(d,col,years):
    rng=np.random.default_rng(20261125);draw=np.zeros((B,2));out={};d2=[];d3=[]
    for y in years:
        a,b=[d.loc[(d.Year==y)&(d.Day==day),col].to_numpy(float) for day in ('D2','D3')]
        x,z=dist(a),dist(b);d2.append([x['mean'],x['zero_fraction']]);d3.append([z['mean'],z['zero_fraction']])
        p,q=1-x['zero_fraction'],1-z['zero_fraction'];u,v=x['mean_positive'],z['mean_positive']
        dc=(q-p)*(u+v)/2;dp=(v-u)*(p+q)/2
        assert np.isclose(dc+dp,z['mean']-x['mean'])
        cmp=b[:,None]-a[None,:]
        out[y]={'D2':x,'D3':z,'mean_difference':z['mean']-x['mean'],'zero_fraction_difference':z['zero_fraction']-x['zero_fraction'],'positive_frequency_component':dc,'conditional_positive_count_component':dp,'probability_D3_exceeds_D2_half_ties':float(((cmp>0).sum()+.5*(cmp==0).sum())/cmp.size)}
        aa=a[rng.integers(len(a),size=(B,len(a)))];bb=b[rng.integers(len(b),size=(B,len(b)))];draw+=np.column_stack([bb.mean(1)-aa.mean(1),(bb==0).mean(1)-(aa==0).mean(1)])/len(years)
    m,n=np.mean(d2,axis=0),np.mean(d3,axis=0)
    return {'years':years,'by_year':out,'endpoint_order':['mean_count','zero_fraction'],'equal_year_D2':m.tolist(),'equal_year_D3':n.tolist(),'equal_year_difference':(n-m).tolist(),'conditional_stratified_bootstrap_interval':np.quantile(draw,[.025,.975],axis=0).T.tolist()}

def penstemon(root):
    a,t,b,p,s,v,c=[read(root,k) for k in list(HASHES)[:7]]
    assert list(map(len,(a,t,b,p,s,v,c)))==[60,60,60,130,129,80,84]
    for d,k in [(a,['Plant ID','Day']),(t,['Plant ID','Day']),(b,['Plant ID','Day']),(p,['Plant ID','Day','Year']),(s,['Plant ID','Day','Year']),(v,['Plant ID'])]:assert not d.duplicated(k).any()
    j=a.merge(t,on=['Plant ID','Day'],validate='one_to_one').merge(b,on=['Plant ID','Day'],validate='one_to_one');assert len(j)==60
    micro={day:{k:dist(g[k]) for k in ('Pollen','NTubesTop','NTubesBase')} for day,g in j.groupby('Day')}
    y=j[j.Day!='D1'].merge(p[p.Year=='Y15'],on=['Plant ID','Day'],suffixes=('_mic','_year'),validate='one_to_one');assert len(y)==40
    mismatch=y[y.Pollen_mic!=y.Pollen_year][['Plant ID','Day','Pollen_mic','Pollen_year']].to_dict('records')
    cross=c.groupby('Type of Cross')[[' Flowers Crossed','Fruits Produced']].sum()
    assert (c['Fruits Produced']<=c[' Flowers Crossed']).all()
    return {'paper_doi':'10.1002/njb.04977','data_doi':'10.5061/dryad.xpnvx0kwt','microscopy':micro,'nonmonotone_spatial_count_rows':int(((j.NTubesTop>j.Pollen)|(j.NTubesBase>j.NTubesTop)).sum()),'pollen_2015_sheet_disagreements':mismatch,'pollen_all_years':year_summary(p,'Pollen',['Y15','Y18','Y20']),'seed_all_years':year_summary(s,'Seeds',['Y17','Y18','Y20']),'pollen_shared_years':year_summary(p,'Pollen',['Y18','Y20']),'seed_shared_years':year_summary(s,'Seeds',['Y18','Y20']),'single_visit_pollen':{k:dist(g.Pollen) for k,g in v.groupby('Bee taxon')},'breeding_source_totals':cross.to_dict('index'),'breeding_duplicate_cross_keys':int(c.duplicated(['Plant ID','Type of Cross']).sum()),'limits':['Separate flower cohorts across days and experiments; do not match IDs across days or pollen to seed. IDs are recycled. Microscopy matches only within day in same 2015 experiment.','D2 and D3 are exposure-duration treatments for seed cohort, not seed production on those days. README labels Seeds per fruit; article per flower. Report recorded seed counts and zero records; no verified fruit-set denominator.','Equal year weighting, bootstrap samples independent records within year/day, conditional on these years; no inference across years and no formal test of equivalence or insurance mechanism.','Single visit measures pollen only; paper reports stigma excision may disrupt reproduction. No group-specific seed success derived. Primary raw first sheet; hidden XLSTAT outputs and paper breeding denominators differ, not reconciled.']}

def clarkia(root):
    d=read(root,list(HASHES)[-1]);assert len(d)==430 and not d.duplicated(['plot','focal_sp','treatment']).any()
    assert set(d.treatment)=={'cont_seed','supp_seed'} and set(d.focal_sp)=={'C','S','U','X'}
    a,b=[d[d.treatment==v].set_index(['plot','focal_sp']) for v in ('cont_seed','supp_seed')];assert len(a)==255 and len(b)==175
    j=a.join(b,lsuffix='_c',rsuffix='_s',how='inner',validate='one_to_one').reset_index();assert len(j)==175
    for k in ('block','bg_sp','bg_Cwt','n_grass','n_forb','n_flower'):assert (j[k+'_c']==j[k+'_s']).all()
    z=j.dropna(subset=['n_seed_c','n_seed_s','n_ovule_c','n_ovule_s']).copy();assert len(z)==156 and (z.aver_n_ovule_c==z.aver_n_ovule_s).all()
    for suf in ('_c','_s'):assert (z['n_ovule'+suf]>0).all() and (z['n_seed'+suf]>=0).all() and (z['n_seed'+suf]<=z['n_ovule'+suf]).all()
    z['p_c']=z.n_seed_c/z.n_ovule_c;z['p_s']=z.n_seed_s/z.n_ovule_s;z['delta_fraction']=z.p_s-z.p_c;z['delta_seeds']=z.n_seed_s-z.n_seed_c
    z['fill_component']=z.delta_fraction*(z.n_ovule_c+z.n_ovule_s)/2;z['ovule_component']=(z.n_ovule_s-z.n_ovule_c)*(z.p_s+z.p_c)/2
    assert np.allclose(z.delta_seeds,z.fill_component+z.ovule_component)
    z['n']=1
    def report(q):
        cols=['delta_fraction','delta_seeds','fill_component','ovule_component'];r=q[cols].mean().to_dict();r.update(pairs=len(q),blocks=q.block_c.nunique(),zero_control=int((q.n_seed_c==0).sum()),zero_supplement=int((q.n_seed_s==0).sum()),opposite=int((q.delta_fraction*q.delta_seeds<0).sum()),higher_fraction_fewer_seeds=int(((q.delta_fraction>0)&(q.delta_seeds<0)).sum()),lower_fraction_more_seeds=int(((q.delta_fraction<0)&(q.delta_seeds>0)).sum()));return r
    q=z[(z.n_ovule_assigned_c==0)&(z.n_ovule_assigned_s==0)].copy();assert len(q)==142
    g=q.groupby(['bg_sp_c','block_c'])[['delta_fraction','delta_seeds','n']].sum();assert len(g)==37
    rng=np.random.default_rng(20261125);draw=np.zeros((B,3))
    for _,v in g.groupby(level=0):
        a=v.to_numpy();draw+=a[rng.integers(0,len(a),size=(B,len(a)))].sum(axis=1)
    return {'paper_doi':'10.1002/ecm.1649','data_doi':'10.5061/dryad.k3j9kd56r','source_rows':len(d),'pairs_matched':len(j),'complete_pairs':report(z),'directly_counted_pairs':report(q),'directly_counted_by_focal_species':{k:report(g) for k,g in q.groupby('focal_sp')},'equal_block_mean':q.groupby('block_c')[['delta_fraction','delta_seeds']].mean().mean().to_dict(),'conditional_block_bootstrap_interval':np.quantile(draw[:,:2]/draw[:,2:],[.025,.975],axis=0).T.tolist(),'limits':['Unique plot-by-focal-species-by-treatment keys and identical focal metadata; no explicit individual ID, so report candidate paired fruits in plot/species rather than verified individual matching.','Complete observed fruit records only, assigned ovule counts removed in primary. Missing fruits not zero-imputed; selection may bias. No whole-plant fecundity or causal resource mediation.','Seed-count difference decomposed algebraically into filled-fraction and ovule-count differences. Neither arithmetic component identifies a causal pathway; actual flower ovule counts differ between treatments.','Cluster bootstrap conditional on observed background species strata and resamples whole blocks; not original model or confirmatory inference.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('cross_system_sources'));a=p.parse_args();print(json.dumps({'status':'posthoc_distributional_and_pollen_addition_diagnostics','source_hashes':HASHES,'penstemon':penstemon(a.root),'clarkia':clarkia(a.root)},indent=2,sort_keys=True,allow_nan=False))
