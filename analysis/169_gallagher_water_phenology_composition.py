#!/usr/bin/env python3
"""Posthoc within-study array-held-out prediction of seed set; not causal mediation."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
P21='gallagher_2021/gallagher&campbell_frontiersinecology&evolution_data.xlsx'
P20='gallagher_2020/gallagher&campbell_phenologyExperimentData.xlsx'
HASHES={P21:'152e09ab8bd0f49c2c5052e284fbaeb3f7362fd0f82998ed1a27001bd0e7250d',P20:'51263c0cabe9dd04dbf716a4594e7d700c5235dd3f85a65ab51f43fcef828411'}
def verified(root,p):
    x=root/p;assert hashlib.sha256(x.read_bytes()).hexdigest()==HASHES[p];return x

def cv(x,split,alpha,water):
    # Fixed context: water assignment and flowering week, plus measured flower count.
    # Leave-week-out sensitivity instead uses continuous week, so unseen levels not encoded.
    w=x.week.to_numpy();t=x.treat.to_numpy();y=x.mseed.to_numpy(float)
    c=np.column_stack([t=='A',t=='D']+([w==i for i in [2,3,4]] if split=='array' else [])).astype(float)
    base=[np.log1p(x.flrCnt.to_numpy(float))]
    if split=='week':base.append(w.astype(float))
    if water=='measured':base.append(x.mVWC.to_numpy(float))
    rate=np.log1p(x.mVisRate.to_numpy(float));n=x.sVis.to_numpy(float)
    share=np.divide(x.sBombVis.to_numpy(float),n,out=np.zeros(len(x)),where=n>0)
    # At zero observed visits the composition has no defined meaning. Include zero indicator
    # in the total-visit model as well, so the share cannot improve by merely identifying zeros.
    base=np.column_stack(base)
    X={'context':np.column_stack([c,base]),'total_rate':np.column_stack([c,n>0,base,rate]),'composition':np.column_stack([c,n>0,base,rate,share])}
    nc={'context':c.shape[1],'total_rate':c.shape[1]+1,'composition':c.shape[1]+1}
    blocks=w*10+x.array.to_numpy() if split=='array' else w
    out={}
    for name,z in X.items():
        pred=np.empty(len(y))
        for b in sorted(set(blocks)):
            te=blocks==b;tr=~te;v=z.copy();s=StandardScaler().fit(z[tr,nc[name]:]);v[:,nc[name]:]=s.transform(z[:,nc[name]:])
            pred[te]=Ridge(alpha=alpha).fit(v[tr],y[tr]).predict(v[te])
        err=(pred-y)**2
        out[name]={'rmse':float(np.sqrt(err.mean())),'fold_mse':{str(int(b)):float(err[blocks==b].mean()) for b in sorted(set(blocks))}}
    return out

def analyze(root):
    p=verified(root,P21);x=pd.read_excel(p,sheet_name='exp3_meansForAnalysis');r=pd.read_excel(p,sheet_name='exp3_PolObs_2016');s=pd.read_excel(p,sheet_name='exp3_2016_seedCnt');old=pd.read_excel(verified(root,P20),sheet_name='Exp2_2015_Means')
    assert len(x)==115 and x.plantID.is_unique and len(old)==40 and old.plantID.is_unique
    assert set(x.treat)=={'A','C','D'} and x.groupby(['week','array']).ngroups==20
    rr=r.dropna(subset=['plantID']);assert len(rr)==1210
    counts=rr.groupby('plantID')[['noVisitors','BombusVisits','nonBombusVisits']].sum(min_count=1)
    rawseed=s.dropna(subset=['plantID','seedCnt']).groupby('plantID').seedCnt.mean().rename('raw_mean_seed')
    j=x.merge(counts,left_on='plantID',right_index=True,how='left',validate='one_to_one').merge(rawseed,left_on='plantID',right_index=True,how='left',validate='one_to_one')
    j['counts_match_raw']=(j.sVis==j.noVisitors)&(j.sBombVis==j.BombusVisits)&(j.sNonBombVis==j.nonBombusVisits)
    j['seed_matches_raw']=np.isclose(j.mseed,j.raw_mean_seed,equal_nan=True)
    assert (x.sVis!=x.sBombVis+x.sNonBombVis).sum()==1
    z=j[j.mseed.notna()&(j.sVis==j.sBombVis+j.sNonBombVis)].copy();assert len(z)==113
    assert z.mseed.between(0,4).all() and (z.flrCnt>0).all()
    # Primary uses authors' analysis table; raw matching sensitivity does not presume raw means correct.
    panels={'author_aggregate':z,'raw_count_and_seed_agreement':z[z.counts_match_raw&z.seed_matches_raw]}
    result={}
    for name,d in panels.items():
        result[name]={'plants':len(d),'array_blocks':d.groupby(['week','array']).ngroups,'cv':{split:{water:{str(alpha):cv(d,split,alpha,water) for alpha in (.1,1,10)} for water in ('assigned','measured')} for split in ('array','week')}}
    week={str(int(k)):{'plants':len(g),'mean_visit_rate':float(g.mVisRate.mean()),'mean_seeds_per_flower':float(g.mseed.mean()),'pooled_bombus_share_of_classified_visits':float(g.sBombVis.sum()/(g.sBombVis.sum()+g.sNonBombVis.sum()))} for k,g in z.groupby('week')}
    treatment={str(k):{'plants':len(g),'mean_visit_rate':float(g.mVisRate.mean()),'mean_seeds_per_flower':float(g.mseed.mean()),'mean_vwc':float(g.mVWC.mean())} for k,g in z.groupby('treat')}
    return {'status':'posthoc_author_aggregate_prediction_not_causal','study_doi':'10.3389/fevo.2021.641693','source_hashes':HASHES,'source_plants':len(x),'old_2015_overlap_plant_ids':len(set(old.plantID)&set(x.plantID)),'raw_pollinator_rows':len(rr),'raw_pollinator_plants':len(counts),'raw_seed_mean_disagrees':int((~j.seed_matches_raw).sum()),'raw_count_disagrees_among_observed_plants':int((j.noVisitors.notna()&~j.counts_match_raw).sum()),'aggregate_count_closure_disagrees':1,'missing_seed_outcome':int(x.mseed.isna().sum()),'primary_zero_observed_visits':int((z.sVis==0).sum()),'primary_zero_visits_positive_seeds':int(((z.sVis==0)&(z.mseed>0)).sum()),'week_summary':week,'treatment_summary':treatment,'panels':result,'limits':['2016 author-level plant table used as deposited, not a reconstruction of all paper filters. A=wet, C=control, D=dry. Exclude missing outcome and one aggregate visitor-count closure discrepancy. Source raw rows disagree with aggregates; sensitivity conditions on agreement and is potentially selected.','Visitation rate and Bombus share measured during observation windows, not complete season visits or causal pollen delivery. Zero observed visits not absence of pollination. Share assigned zero only with zero-visit indicator included in both visit models.','Array split holds out week-by-array blocks within season; week split holds out all plants from a flowering week using linear week rather than categorical week. Only four weeks; no independent site validation. Measured VWC sensitivity uses contemporaneous measurements.','2015 and 2016 reuse plant IDs; not independent studies; no cross-year model. No causal or prospective prediction and no pooled meta effect.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('cross_system_sources'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
