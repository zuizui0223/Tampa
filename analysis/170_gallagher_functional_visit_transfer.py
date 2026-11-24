#!/usr/bin/env python3
"""Transfer independently measured visitor efficacy into a phenology experiment.
A weighted index, not measured effective pollen or seed flux; no causal mediation.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
FILES={'gallagher_2020/gallagher&campbell_pollinatorEffectivenessData.xlsx':'bbfcbbaf43b53b0ef835b891bd8932ae3761a383e4ecb1f38440a4ba9d477c38','gallagher_2021/gallagher&campbell_frontiersinecology&evolution_data.xlsx':'152e09ab8bd0f49c2c5052e284fbaeb3f7362fd0f82998ed1a27001bd0e7250d'}
def verify(root,k):
    p=root/k
    if hashlib.sha256(p.read_bytes()).hexdigest()!=FILES[k]:raise ValueError('source drift')
    return p

def calibration(a):
    v=a[a.treat=='V'].copy();assert len(v)==94 and v.plantID.is_unique and (v.noFlrs>0).all() and (v.noFlrs==v.flrsVisited).all()
    assert np.allclose(v.seedCnt/v.noFlrs,v.seedPerFlr)
    assert v.seedPerFlr.between(0,4).all()
    assert set(v.visID)=={'Bombus','Osmia','Muscoidea','Hoverfly'}
    v['guild']=v.visID.replace({'Hoverfly':'fly','Muscoidea':'fly','Osmia':'solitary','Bombus':'Bombus'})
    v['two']=np.where(v.guild=='Bombus','Bombus','other')
    weights={}; details={}
    for site,g in [('pooled',v),*list(v.groupby('site'))]:
        for typ in ['two','guild']:
            if typ=='guild' and set(g.guild)!={'Bombus','solitary','fly'}:continue
            for mode in ['seed_ramet','seed_flower','pollen_ramet']:
                t=g if mode!='pollen_ramet' else g[g.polDepMC.notna()]
                if mode=='pollen_ramet' and set(t[typ])!=set(g[typ]):continue
                means={k:float((j.seedCnt.sum()/j.noFlrs.sum()) if mode=='seed_flower' else j['seedPerFlr' if mode=='seed_ramet' else 'polDepMC'].mean()) for k,j in t.groupby(typ)}
                key='|'.join([site,typ,mode]);norm=means['Bombus'];assert norm>0
                weights[key]={k:m/norm for k,m in means.items()}
                details[key]={'ramets':len(t),'groups':{k:{'n':len(j),'flowers':int(j.noFlrs.sum()),'mean':means[k]} for k,j in t.groupby(typ)},'relative_to_Bombus':weights[key]}
    return v,weights,details

def target(p):
    x=pd.read_excel(p,sheet_name='exp3_meansForAnalysis');r=pd.read_excel(p,sheet_name='exp3_PolObs_2016');s=pd.read_excel(p,sheet_name='exp3_2016_seedCnt')
    assert len(x)==115 and x.plantID.is_unique
    rr=r.dropna(subset=['plantID']);counts=rr.groupby('plantID')[['noVisitors','BombusVisits','nonBombusVisits']].sum(min_count=1)
    rawseed=s.dropna(subset=['plantID','seedCnt']).groupby('plantID').seedCnt.mean().rename('raw_mean_seed')
    j=x.merge(counts,left_on='plantID',right_index=True,how='left',validate='one_to_one').merge(rawseed,left_on='plantID',right_index=True,how='left',validate='one_to_one')
    j['agree']=(j.sVis==j.noVisitors)&(j.sBombVis==j.BombusVisits)&(j.sNonBombVis==j.nonBombusVisits)&np.isclose(j.mseed,j.raw_mean_seed,equal_nan=True)
    z=j[j.mseed.notna()&(j.sVis==j.sBombVis+j.sNonBombVis)].copy();assert len(z)==113 and z.agree.sum()==88
    z['three_agree']=z.sVis==z.sBombVis+z.sbbVis+z.sflyVisits
    assert z.three_agree.sum()==112
    assert z.mseed.between(0,4).all() and (z.mVisRate>=0).all() and ((z.sVis==0)==(z.mVisRate==0)).all()
    return z

def cv(z,weights,split,alpha,water):
    y=z.mseed.to_numpy(float);week=z.week.to_numpy();t=z.treat.to_numpy();n=z.sVis.to_numpy(float);rate=z.mVisRate.to_numpy(float)
    cat=np.column_stack([t=='A',t=='D']+([week==i for i in (2,3,4)] if split=='array_categorical' else [])).astype(float)
    base=[np.log1p(z.flrCnt.to_numpy(float))]
    if split!='array_categorical':base.append(week.astype(float))
    if water=='measured':base.append(z.mVWC.to_numpy(float))
    base=np.column_stack(base);c=np.column_stack([cat,n>0]);share=np.divide(z.sBombVis.to_numpy(float),n,out=np.zeros(len(n)),where=n>0)
    designs={'context':(np.column_stack([cat,base]),cat.shape[1]),'unweighted':(np.column_stack([c,base,np.log1p(rate)]),c.shape[1]),'unweighted_plus_share':(np.column_stack([c,base,np.log1p(rate),share]),c.shape[1])}
    for name,w in weights.items():
        if 'other' in w:num=z.sBombVis*w['Bombus']+z.sNonBombVis*w['other']
        else:num=z.sBombVis*w['Bombus']+z.sbbVis*w['solitary']+z.sflyVisits*w['fly']
        factor=np.divide(num.to_numpy(float),n,out=np.ones(len(n)),where=n>0)
        q=rate*factor
        designs[name]=(np.column_stack([c,base,np.log1p(q)]),c.shape[1])
    blocks=week if split=='week_linear' else week*10+z.array.to_numpy()
    out={}
    for name,(d,k) in designs.items():
        pred=np.empty(len(y))
        for block in sorted(set(blocks)):
            test=blocks==block;train=~test;v=d.copy();sc=StandardScaler().fit(d[train,k:]);v[:,k:]=sc.transform(d[:,k:]);pred[test]=Ridge(alpha=alpha).fit(v[train],y[train]).predict(v[test])
        err=(pred-y)**2
        out[name]={'rmse':float(np.sqrt(err.mean())),'fold_mse':{str(int(b)):float(err[blocks==b].mean()) for b in sorted(set(blocks))}}
    return out

def analyze(root):
    a=pd.read_excel(verify(root,list(FILES)[0]),sheet_name='Exp2.4_2016_AllData');z=target(verify(root,list(FILES)[1]));assert len(a)==232 and not(set(a.plantID)&set(z.plantID))
    v,w,detail=calibration(a)
    # Main analysis: two guilds, mean seeds per flower (equal ramet weights).
    # Three-guild mapping is explicitly a proxy (Osmia for all solitary bees; observed flies for all flies).
    chosen={k:w[k] for k in ['pooled|two|seed_ramet','pooled|two|seed_flower','pooled|two|pollen_ramet','RG|two|seed_ramet','SP|two|seed_ramet','pooled|guild|seed_ramet','pooled|guild|seed_flower','pooled|guild|pollen_ramet']}
    # Include one fixed counterfactual grid, never use it to choose a fitted weight.
    for q in (0.,.25,.5,.75,1.,1.5,2.):chosen[f'scenario_other_{q:g}']={'Bombus':1.,'other':q}
    panels={}
    for name,x in [('author',z),('raw_agreement',z[z.agree]),('three_guild_complete',z[z.three_agree])]:
        use=chosen if name=='three_guild_complete' else {k:v for k,v in chosen.items() if 'other' in v}
        panels[name]={'n':len(x),'cv':{sp:{water:{str(alpha):cv(x,use,sp,alpha,water) for alpha in (.1,1.,10.)} for water in ('assigned','measured')} for sp in ('array_categorical','array_linear','week_linear')}}
    return {'status':'posthoc_separate_experiment_weight_transfer_not_external_site_validation','source_hashes':FILES,'calibration_n':len(v),'target_n':len(z),'overlapping_plant_ids':0,'calibration':detail,'panels':panels,'limits':['2016 separate experiment ramet identifiers do not overlap with target. Same region/year and researchers; not independent study or out-of-region validation. No target seed outcomes used to calculate weights.','Rate is flowers visited per available flower per observation hour, taxon shares are counts of insect visitors; weighted product is a proxy assuming visitors in each group visit comparable numbers of flowers; not a measured effective seed flux.','Weights normalized to Bombus=1 to maintain common log1p scale; zero observed visits mapped to zero weighted rate, with same zero indicator as baseline.','Three-guild sensitivity excludes one additional count mismatch and maps Osmia onto all small-bodied/solitary bees and sampled flies onto fly group, not a verified species-level transfer. Pollen weights from selected subset; hoverfly has no pollen observation. No invented pollen value.','Same models in array_linear and week_linear to isolate split from week-encoding change; array_categorical retained for comparison to analysis/169. Measured VWC contemporaneous. Four week folds and twenty array folds; no independent season replication.','Fixed weight grid is sensitivity only, not tuning. No causal seed-limitation model or meta-analysis.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('cross_system_sources'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
