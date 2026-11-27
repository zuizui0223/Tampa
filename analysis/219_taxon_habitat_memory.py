#!/usr/bin/env python3
"""Same-record-coordinate re-observation, not plant survival or seed fate."""
import hashlib,json,zipfile,sys
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
A='31d4831e2efa3552e58db32a70fefccf6dcad5049e2bed4f2ca09d984b547e06'
H='9727c28d4dafcd225a754f2439e010fe09f2835dfbeefe03b28cc5d8f940facf'
S=['CR_PA','CS_PA','EA_PA','HC_PA','HD_PA','HO_PA','HS_PA','HT_PA','HU_PA','SI_PA','TC_PA','TH_PA','ZC_PA']
SURVEYS={'lobster':('Torres Strait lobster surveys',1),'cucumber':('Torres Strait sea cucumber surveys',2)}
def main(path):
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==A
 z=zipfile.ZipFile(path);b=z.read('torres_survey_points.geojson');assert hashlib.sha256(b).hexdigest()==H
 f=json.loads(b)['features'];assert len(f)==28732
 d=pd.DataFrame([r['properties'] for r in f]);d['lon'],d['lat']=np.array([r['geometry']['coordinates'] for r in f]).T
 out={'archive':A,'inner':H,'species_columns':S,'audit':{},'panels':{},'prediction':{}}
 def panel(b):
  p=b[b.p0==1].copy();q=p[p.p1==1].copy();p['retained']=p.shared/p.n0;q['retained']=q.shared/q.n0;q['J']=q.shared/(q.n0+q.n1-q.shared)
  both=p.p1.mean();ret=p.retained.mean();within=both-ret;lost=1-both
  assert np.isclose(lost+within+ret,1)
  eq=p.groupby('station')[['p1','retained']].mean().mean()
  types=[]
  for s in S:
   at=p[p[s+'_0']==1];remain=at[at.p1==1];n=len(at)
   if n:types.append(dict(taxon=s,initial=n,still_any=int(at.p1.sum()),still_taxon=int(at[s+'_1'].sum()),lost_all=int((at.p1==0).sum()),lost_taxon_while_any=int(((at.p1==1)&(at[s+'_1']==0)).sum())))
  return dict(pairs=len(b),stations=b.station.nunique(),initial_positive=len(p),both_positive=len(q),both_positive_stations=q.station.nunique(),grass_reobserved=float(both),prior_taxon_reobserved_equal_pair=float(ret),prior_taxon_reobserved_pooled=float(p.shared.sum()/p.n0.sum()),loss_all_grass=float(lost),loss_prior_taxon_while_grass_present=float(within),species_retention_conditional_on_any=float(q.retained.mean()),equal_station_grass=float(eq.p1),equal_station_taxon=float(eq.retained),both_any_lost=int((q.lost>0).sum()),both_any_gained=int((q.gain>0).sum()),both_identical=int(((q.lost+q.gain)==0).sum()),both_no_overlap=int((q.shared==0).sum()),both_mean_richness0=float(q.n0.mean()),both_mean_richness1=float(q.n1.mean()),both_mean_jaccard=float(q.J.mean()),taxon=types)
 for name,(survey,lag) in SURVEYS.items():
  a=d[d.Survey==survey].copy();assert a[S].isin([0,1]).all().all() and (a[S].sum(axis=1)==a.SG_species).all() and ((a.SG_species>0)==(a.SG_present==1)).all();assert a.Month.eq('Contact data custodian').all()
  keys=['lon','lat','Year'];assert a.groupby(keys)[S+['SG_present','Depth_MSL']].nunique().max().max()==1
  n=len(a);a=a.drop_duplicates(keys);a['station']=a.groupby(['lon','lat']).ngroup();xy=Transformer.from_crs(4326,32754,always_xy=True).transform(a.lon.to_numpy(),a.lat.to_numpy());a['x'],a['y']=xy
  rr=[]
  for st,g in a.groupby('station'):
   v=g.sort_values('Year').to_dict('records')
   for u,w in zip(v[:-1],v[1:]):
    s=np.array([u[k] for k in S]);t=np.array([w[k] for k in S]);assert u['Depth_MSL']==w['Depth_MSL']
    rr.append(dict(station=int(st),year0=int(u['Year']),year1=int(w['Year']),dt=int(w['Year']-u['Year']),p0=int(u['SG_present']),p1=int(w['SG_present']),n0=int(s.sum()),n1=int(t.sum()),shared=int((s&t).sum()),lost=int((s&~t).sum()),gain=int((~s&t).sum()),depth=float(u['Depth_MSL']),x=float(u['x']),y=float(u['y']),**{k+'_0':int(s[i]) for i,k in enumerate(S)},**{k+'_1':int(t[i]) for i,k in enumerate(S)}))
  b=pd.DataFrame(rr);out['audit'][name]=dict(records=n,duplicates=n-len(a),unique_station_year=len(a),all_stations=a.station.nunique(),repeated_stations=b.station.nunique(),lag_counts={str(k):int(v) for k,v in b.dt.value_counts().items()},year_pairs={str(k):int(v) for k,v in b.groupby(['year0','year1']).size().items()});out['panels'][name]={'all':panel(b),'selected_lag':panel(b[b.dt==lag])}
  # Conditional choice of a recipient already known to have any grass at previous survey.
  # Predict next observation of focal species, not persistence of an individually marked plant.
  q=b[(b.dt==lag)&(b.p0==1)].reset_index(drop=True);q['richness']=np.log1p(q.n0)
  if name!='lobster':continue # 2y series contains only a few different year pairs; no comparable temporal forecast
  def fit_splits(splits):
   pred=[];folds=[]
   for label,tr,te in splits:
    train=q.iloc[tr];test=q.iloc[te];assert len(train)>0 and len(test)>0
    ns=0
    for s in S:
     y=train[s+'_1'].to_numpy();yt=test[s+'_1'].to_numpy()
     if y.sum()<20 or len(y)-y.sum()<20:continue
     ns+=1
     for nm,cols in [('generic',['depth','richness']),('identity',['depth','richness',s+'_0'])]:
      x=train[cols].to_numpy();xt=test[cols].to_numpy();sc=StandardScaler().fit(x);m=LogisticRegression(C=1,max_iter=1000).fit(sc.transform(x),y);p=m.predict_proba(sc.transform(xt))[:,1];p=np.clip(p,1e-8,1-1e-8)
      pred.extend(dict(fold=label,station=int(st),year=int(yr),taxon=s,model=nm,y=int(yy),brier=float((pp-yy)**2),logloss=float(-yy*np.log(pp)-(1-yy)*np.log1p(-pp))) for st,yr,yy,pp in zip(test.station,test.year1,yt,p))
    folds.append(dict(fold=label,train_pairs=len(tr),test_pairs=len(te),taxa=ns))
   p=pd.DataFrame(pred);assert len(p)>0;assert p.groupby(['fold','station','year','taxon']).model.nunique().eq(2).all()
   # Equal taxa, then stations within taxon; per-year aggregate also retained.
   bytax=p.groupby(['model','taxon','station'])[['brier','logloss']].mean().groupby(['model','taxon']).mean();m=bytax.groupby('model').mean();fold=p.groupby(['fold','model'])[['brier','logloss']].mean().unstack('model');ft=[]
   for k in fold.index:ft.append(dict(fold=k,generic_brier=float(fold.loc[k,('brier','generic')]),identity_brier=float(fold.loc[k,('brier','identity')]),generic_logloss=float(fold.loc[k,('logloss','generic')]),identity_logloss=float(fold.loc[k,('logloss','identity')])))
   return dict(predictions=len(p)//2,folds=folds,metrics=m.to_dict('index'),per_taxon=[dict(model=k[0],taxon=k[1],**v.to_dict()) for k,v in bytax.iterrows()],per_fold=ft)
  for size in [5000,10000,20000]:
   groups=[str(int(x//size))+'|'+str(int(y//size)) for x,y in zip(q.x,q.y)];gkf=GroupKFold(n_splits=5);splits=[(str(i),tr,te) for i,(tr,te) in enumerate(gkf.split(q,groups=groups))];out['prediction']['spatial_'+str(size)]=fit_splits(splits)
  splits=[]
  for y in sorted(q.year1.unique()):
   tr=np.flatnonzero(q.year1.to_numpy()<y);te=np.flatnonzero(q.year1.to_numpy()==y)
   if len(tr)>=100 and len(te)>=10:splits.append((str(y),tr,te))
  out['prediction']['forward_year']=fit_splits(splits)
 out['limits']=['Exact repeated recorded coordinates, not tagged individuals/quadrats. Month unspecified for both programs; differing seasons, detectability and observation coverage can produce turnover. Same recorded depth is not independently measured bathymetry. No animal treatment or causal mechanism.','Each adjacent observed year at a station is a dependent comparison; programs and lag distributions differ, no pooling or comparative significance. Target prior-species re-observation decomposes algebraically into all-grass absence and selective non-recording; not species mortality.','Prediction models limited to lobster 1y prior-positive observations, eligible taxa chosen using train outcomes only, matched model rows. Spatial blocks and rolling years retrospective; no independent regional validation or actual establishment.']
 return out
if __name__=='__main__':
 out=main(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'audit':out['audit'],'panels':{k:{n:{x:y for x,y in v.items() if x!='taxon'} for n,v in a.items()} for k,a in out['panels'].items()},'prediction':{k:{'metrics':v['metrics'],'folds':v['folds'],'per_fold':v['per_fold']} for k,v in out['prediction'].items()}},indent=2))
