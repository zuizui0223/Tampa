#!/usr/bin/env python3
"""Core reproduction: forward-year SIBES mean weight / biomass prediction, separate marsh data.
Full local script includes per-year predictions, further sensitivities and audit."""
import argparse,hashlib,io,json,zipfile,itertools
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
HASH='843038aefe1afaed39ded71f4d5e5890262a778300c1f0ab011245b7e61ead8a'
def run(path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  manifest=json.loads(z.read('manifest.json'));hs={r['file']:r['sha256'] for r in manifest[1]['files']+manifest[2]['members']}
  def read(n,sep=','):
   b=z.read(n);assert hashlib.sha256(b).hexdigest()==hs[n]
   return pd.read_csv(io.BytesIO(b),sep=sep,low_memory=False).loc[:,lambda d:~d.columns.str.startswith('Unnamed')]
  s,b,sp=[read('official_'+n+'.csv') for n in ['samples','biota','species']];a=read('hautekiet_262_Survival_data.csv',';');g=read('hautekiet_11_Algal_cover.csv',';');f=read('hautekiet_7_LossRate_defaunation_exp1.csv',';')
 assert len(s)==59463 and not b.duplicated(['sample_id','sibes_id']).any()
 s=s[~s.sample_id.duplicated(False)].copy();s['year']=pd.to_datetime(s.date).dt.year;s['doy']=pd.to_datetime(s.date).dt.dayofyear
 hid=sp.loc[sp.name.eq('Hediste diversicolor'),'sibes_id'].item();fid=sp.loc[sp.name.eq('Nereididae'),'sibes_id'].item()
 h=s.merge(b[b.sibes_id.eq(hid)],on='sample_id',validate='one_to_one');h['family']=h.sample_id.isin(b.loc[b.sibes_id.eq(fid),'sample_id'])
 h=h[h.sampling_type.eq('grid')&h.abundance_m2.gt(0)&h.afdm_m2.gt(0)].rename(columns={'sampling_station_id':'station','tidal_basin_name':'basin','abundance_m2':'N','afdm_m2':'B','median_grain_size':'grain','percentage_mud':'mud'}).copy()
 assert len(h)==16794 and not h.duplicated(['station','year']).any()
 h['M']=1000*h.B/h.N;h['logB']=np.log(h.B);h['logM']=np.log(h.M)
 h=h[h.groupby(['year','basin']).station.transform('size').ge(30)].sort_values(['station','year']).copy();assert len(h)==16207
 h['historyM']=h.groupby('station').logM.transform(lambda x:x.expanding().mean());h['historyB']=h.groupby('station').logB.transform(lambda x:x.expanding().mean());h['history_count']=h.groupby('station').cumcount()+1
 past=h[['station','year','basin','logB','logM','historyM','historyB','history_count','x','y','grain','mud','doy','family']].copy();past['target_year']=past.year+1
 target=h[['station','year','basin','logB','logM','family']].rename(columns={'year':'target_year','logB':'target_logB','logM':'target_logM','family':'target_family'})
 p=past.merge(target,on=['station','target_year','basin'],validate='one_to_one');assert len(p)==8957
 p['spfold']=((np.floor(p.x*67/10).astype(int)*31+np.floor(p.y*111/10).astype(int)*17)%5).astype(int)
 p=pd.concat([p,pd.get_dummies(p.basin,prefix='basin',dtype=float)],axis=1)
 base=[c for c in p if c.startswith('basin_')]+['x','y','grain','mud','doy']
 models={'environment':base,'environment_B':base+['logB'],'environment_B_M':base+['logB','logM'],'environment_B_M_history':base+['logB','logM','historyB','historyM','history_count']}
 def forecast(data,spatial=False,alpha=10,nonlinear=False,start_year=2013):
  data=data.copy()
  if nonlinear:
   for v in ['logB','logM','historyB','historyM']:data[v+'_sq']=data[v]**2
   data['logBM_product']=data.logB*data.logM
  out=[];annual=[]
  for yr in range(start_year,2023):
   pred=[]
   for fold in (range(5) if spatial else [None]):
    train=data[data.target_year.lt(yr)&(data.spfold.ne(fold) if fold is not None else True)]
    test=data[data.target_year.eq(yr)&(data.spfold.eq(fold) if fold is not None else True)].copy()
    if test.empty:continue
    assert len(train)>=100
    for t in ['M','B']:
     y='target_log'+t;test['pred_'+t+'_mean']=train[y].mean();test['pred_'+t+'_persistence']=test['log'+t]
     for name,cols in models.items():
      if nonlinear:cols=cols+[v+'_sq' for v in ['logB','logM','historyB','historyM'] if v in cols]+(['logBM_product'] if 'logB' in cols and 'logM' in cols else [])
      model=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),Ridge(alpha=alpha))
      model.fit(train[cols],train[y]);test['pred_'+t+'_'+name]=model.predict(test[cols])
    pred.append(test)
   if not pred:continue
   pp=pd.concat(pred);out.append(pp)
   for t in ['M','B']:
    for name in ['mean','persistence',*models]:
     annual.append({'year':yr,'target':t,'model':name,'n':len(pp),'mse':float(np.mean((pp['target_log'+t]-pp['pred_'+t+'_'+name])**2))})
  allp=pd.concat(out);res={}
  for t in ['M','B']:
   y='target_log'+t;res[t]={}
   for name in ['mean','persistence',*models]:
    col='pred_'+t+'_'+name;mse=float(np.mean((allp[y]-allp[col])**2));hits=nn=sel=groups=0
    for _,q in allp.groupby(['target_year','basin']):
     if len(q)<20 or q[col].nunique()<2 or name=='mean':continue
     true=q[y].ge(q[y].quantile(.75));pick=q[col].ge(q[col].quantile(.75));hits+=int((true&pick).sum());nn+=int(true.sum());sel+=int(pick.sum());groups+=1
    res[t][name]={'n':len(allp),'rmse_log':float(np.sqrt(mse)),'mse':mse,'top_recall':hits/nn if nn else None,'top_precision':hits/sel if sel else None,'top_hits':hits,'top_n':nn,'selected_n':sel,'groups':groups}
   for v in res[t].values():v['skill_vs_environment_B']=1-v['mse']/res[t]['environment_B']['mse']
  return {'metrics':res,'annual':annual},allp
 main,pred=forecast(p);spatial,_=forecast(p,spatial=True);sens={}
 for alpha in [1,100]:sens['ridge_'+str(alpha)]=forecast(p,alpha=alpha)[0]['metrics']
 sens['2012_onward_pairs']=forecast(p[p.year.ge(2012)],start_year=2016)[0]['metrics'];sens['nonlinear']=forecast(p,nonlinear=True)[0]['metrics'];sens['no_family']=forecast(p[~p.family&~p.target_family])[0]['metrics']
 fw=f.pivot(index=['Level','Replicate'],columns='Species',values='Loss rate');assert len(fw)==15 and fw.notna().all().all();fw['difference']=fw['Def-As']-fw.As
 rng=np.random.default_rng(20261125);B=30000;levels={}
 for level,v in fw.groupby('Level'):
  d=v.difference.to_numpy();signs=np.asarray(list(itertools.product([-1,1],repeat=len(d))));obs=d.mean()
  levels[level]={'n_pairs':len(d),'control_mean':float(v.As.mean()),'defaunated_mean':float(v['Def-As'].mean()),'delta':float(obs),'ci_conditional_pair_bootstrap':np.quantile(rng.choice(d,(B,len(d)),replace=True).mean(1),[.025,.975]).tolist(),'all_deltas':d.tolist(),'p_sign_flip':float(np.mean(np.abs((signs*d).mean(1))>=abs(obs)-1e-12))}
 d=fw.difference.to_numpy();sg=np.asarray(list(itertools.product([-1,1],repeat=len(d))));obs=d.mean()
 pooled={'n_pairs':len(d),'control_mean':float(fw.As.mean()),'defaunated_mean':float(fw['Def-As'].mean()),'delta':float(obs),'p_sign_flip':float(np.mean(np.abs((sg*d).mean(1))>=abs(obs)-1e-12)),'all_negative':bool((d<0).all()),'ci_conditional_stratified_bootstrap':np.quantile(np.mean([rng.choice(v.difference.to_numpy(),(B,len(v)),replace=True).mean(1) for _,v in fw.groupby('Level')],axis=0),[.025,.975]).tolist()}
 g[['pot_token','visit']]=g['Image Name'].str.rsplit('_',n=1,expand=True);g['Pot']=g.pot_token.str.extract(r'T4_(\d+)').astype(int);gw=g.pivot(index='Pot',columns='visit',values='Average GEI').reset_index().merge(a[['Pot','Worms','Vaucheria','nr_end','nr_start']],on='Pot',validate='one_to_one')
 assert len(gw)==10 and gw.Worms.eq(1).all() and gw.Vaucheria.eq(1).all()
 gw['change']=gw.end-gw.start;gw['survival']=gw.nr_end/gw.nr_start
 return {'status':'response-open conditional forecasts, not recruitment risk','source_hashes':hs,'counts':{'eligible_station_years':len(h),'pairs':len(p),'test_pairs':len(pred),'test_stations':pred.station.nunique()},'temporal':main,'temporal_spatial':spatial,'sensitivity':sens,'hautekiet':{'field_defaunation':levels,'field_defaunation_pooled':pooled,'GEI_worm_algae_only':{'n_pots':len(gw),'start_mean':float(gw.start.mean()),'end_mean':float(gw.end.mean()),'decrease_n':int(gw.change.lt(0).sum()),'rho_change_vs_survival':float(spearmanr(gw.change,gw.survival).statistic),'rows':gw.to_dict('records')}}},pred
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r,pred=run(a.artifact);a.out.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');pred.to_csv(a.out.with_name('forward_predictions.csv'),index=False)
