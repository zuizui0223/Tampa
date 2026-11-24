#!/usr/bin/env python3
"""Davis et al. 2026, source-locked within-year held-out block diagnostics.
Do not link 2020 abundance/yield to 2021 single-visit effectiveness as measured same plants.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss,brier_score_loss
FILES={
'Oikos_2020_cross_season_abundance.csv':'c3cf1b5360ddad374c322f331c6421b6ccaa9588698821e4ed01bd3387047d94',
'Oikos_2020_focal_taxa_abundance.csv':'122b92b7866bbab5fb1893d441e4f1cf9d3b33c055ae39f6f26401819f9bda8f',
'Oikos_2020_total_plant_yield.csv':'9a5e808dc9c20404f1ea234d56fef753d9ca1a893b33170995e52fbf607f2d61',
'Oikos_2021_fruit_set_poll_obs.csv':'74d3d03544d17b8105a7603669c34cf1f079c9573eea3b4a5ce0057f36e95ee0',
'Oikos_2021_poll_importance.csv':'916c071c908741681b364a86e1cdf9df25e79df8732768b5a10df0d8f00fb212'}
def read(root,name):
 p=root/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==FILES[name];return pd.read_csv(p)
def indicators(a,levels):return np.column_stack([(a==v).astype(float) for v in levels])
def regress(X,y,blocks,cat,alpha):
 # Continuous inputs standardized on training only; categorical indicators unchanged.
 out=np.empty(len(y))
 for b in sorted(set(blocks)):
  test=blocks==b;train=~test;z=X.copy()
  if cat<X.shape[1]:
   sc=StandardScaler().fit(X[train,cat:]);z[:,cat:]=sc.transform(X[:,cat:])
  out[test]=Ridge(alpha=alpha).fit(z[train],y[train]).predict(z[test])
 e=(out-y)**2
 return {'rmse':float(np.sqrt(e.mean())),'block_rmse':{str(b):float(np.sqrt(e[blocks==b].mean())) for b in sorted(set(blocks))}}
def logistic(X,y,blocks,cat,C):
 out=np.empty(len(y))
 for b in sorted(set(blocks)):
  test=blocks==b;train=~test;z=X.copy()
  if cat<X.shape[1]:
   sc=StandardScaler().fit(X[train,cat:]);z[:,cat:]=sc.transform(X[:,cat:])
  out[test]=LogisticRegression(C=C,solver='lbfgs',max_iter=2000,tol=1e-9).fit(z[train],y[train]).predict_proba(z[test])[:,1]
 return {'log_loss':float(log_loss(y,out,labels=[0,1])),'brier':float(brier_score_loss(y,out)), 'block_log_loss':{str(b):float(log_loss(y[blocks==b],out[blocks==b],labels=[0,1])) for b in sorted(set(blocks))}}
def analyze(root):
 a,b,c=[read(root,k) for k in list(FILES)[:3]];taxa=list(b.columns[1:]);x=a.merge(b,on='id',validate='one_to_one').merge(c,on=['id','block','treat'],validate='one_to_one');assert len(x)==92
 assert (x.total_visitors>0).all() and (x.total_yield_grams>0).all();x['other']=x.total_visitors-x[taxa].sum(axis=1);assert (x.other>=0).all();x=x.dropna(subset=['total_flow']);assert len(x)==91
 cats=indicators(x.treat,['H','J']);cont=np.log1p(x[['total_flow','n_samp_dates','total_visitors']].to_numpy(float));shares=x[taxa].to_numpy(float)/x.total_visitors.to_numpy()[:,None];y=np.log(x.total_yield_grams.to_numpy());blocks=x.block.to_numpy();
 models={'plant_context':np.column_stack([cats,cont[:,:2]]),'total_visits':np.column_stack([cats,cont]),'composition':np.column_stack([cats,cont,shares])}
 cv={str(alpha):{k:regress(v,y,blocks,2,alpha) for k,v in models.items()} for alpha in (.1,1,10)}
 f=read(root,list(FILES)[3]);assert len(f)==1034 and f.plant_id.nunique()==74 and f.groupby('plant_id')[['block','treatment']].nunique().max().max()==1 and set(f.fruit_set)=={0,1}
 guilds=['Apis','Augo','Bombus','Colletes','Lasioglossum'];assert set(f.morphospecies)==set(guilds)
 def cv_visit(z,behavior):
  tr=indicators(z.treatment,['h','j']);tax=indicators(z.morphospecies,guilds[1:]);inter=np.column_stack([tr[:,i]*tax[:,j] for i in range(2) for j in range(4)]);day=z.julian_date.to_numpy(float);Y=z.fruit_set.to_numpy();B=z.block.to_numpy(); designs={'context':(tr,day),'taxon':(np.column_stack([tr,tax]),day),'taxon_by_treatment':(np.column_stack([tr,tax,inter]),day)}
  if behavior:
   be=indicators(z.pol_or_nec,['nectar','pollen & nectar']);designs.update({'context_behavior':(np.column_stack([tr,be]),day),'taxon_behavior':(np.column_stack([tr,tax,be]),day),'taxon_treatment_behavior':(np.column_stack([tr,tax,inter,be]),day)})
  return {str(C):{k:logistic(np.column_stack([d,t]),Y,B,d.shape[1],C) for k,(d,t) in designs.items()} for C in (.1,1,10)}
 v=f.dropna(subset=['pol_or_nec']);assert len(v)==956 and set(v.pol_or_nec)=={'nectar','pollen','pollen & nectar'}
 q=read(root,list(FILES)[4]);assert len(q)==370 and not q.duplicated(['plant_id','morphospecies']).any() and q.groupby('plant_id').size().eq(5).all();assert q.groupby('plant_id')[['block','treatment','n_visitors_allseas']].nunique().max().max()==1
 total=q.groupby('plant_id').n_visitors_allseas.first()-q.groupby('plant_id').n_bees_morph.sum()
 return {'status':'posthoc_within_year_block_cv_not_causal_or_cross_year_prediction','source_hashes':FILES,'yield_2020':{'plants':92,'complete':len(x),'blocks':3,'missing_flower_count':1,'taxa':taxa,'cv_log_yield':cv},'single_visit_2021':{'visits':len(f),'plants':74,'blocks':6,'behavior_complete_visits':len(v),'fruits':int(f.fruit_set.sum()),'by_taxon':f.groupby('morphospecies').fruit_set.agg(['sum','count','mean']).to_dict('index'),'by_taxon_treatment':{str(k):g.fruit_set.agg(['sum','count','mean']).to_dict() for k,g in f.groupby(['morphospecies','treatment'])},'cv_all':cv_visit(f,False),'cv_behavior_complete':cv_visit(v,True),'importance_missing_rows':int(q.poll_imp.isna().sum()),'focal_exceeds_total_plants':int((total<0).sum())},'limitations':['Source annual experiments separate; 2020 total fruit yield includes resource limitation and all pollination, not per-visit effect. No imputation for missing flower count. Focal share predictors use all observed visits as denominator; residual category omitted.','Leave-one-block-out validation holds out entire plants in a spatial block; 3 and 6 blocks only, no independent year or location validation. Prespecified ridge strengths .1,1,10 and inverse penalties .1,1,10 reported as sensitivity, no tuning.','2021 visit identity and behavior are observed, not randomized. Each record is an observed single visit, repeated plant records are not independent. Equal-visit scoring; no causal interpretation.','2021 importance table not used to predict fruit set: contains outcome-derived quantities, missing values, and counts exceeding all-visitor totals.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('cross_system_sources/herbivory_pollinator'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
