#!/usr/bin/env python3
"""Reproduce field lag contrasts and seed-ball emergence history audit; response-open."""
import argparse,io,zipfile,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf
from sklearn.linear_model import Ridge
HASH='5f9be541c571700e2209d374d300a0a93781b7551ce31f721881f091cd5bd1c3'
def run(path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  m=json.loads(z.read('manifest.json'));f=z.read(m[0]['file']);assert hashlib.sha256(f).hexdigest()==m[0]['sha256']
  p=next(x for x in m[1]['files'] if x['name']=='seed_ball.csv');b=z.read(p['file']);assert hashlib.sha256(b).hexdigest()==p['sha256']
  d=pd.read_csv(io.StringIO(f.decode('utf-8-sig').split('*/',1)[1]),sep='\t',skip_blank_lines=True);s=pd.read_csv(io.BytesIO(b))
 assert d.columns.tolist()==m[0]['columns'];d.columns=['label','sow','date','lat','lon','loc','plot','month','color','n','dens','asym','worm','wdens','day','sal','temp','comment']
 assert len(d)==434 and d['plot'].nunique()==62 and not d.duplicated(['plot','date']).any()
 assert d.groupby('plot')[['month','color','sow']].nunique().eq(1).all().all()
 assert d.n.between(0,100).all() and (d.n%1==0).all() and d.dens.eq(4*d.n).all()
 x=d[d.date.ne(d.sow)].copy();assert len(x)==372 and x[['worm','n']].notna().all().all() and x.wdens.eq(4*x.worm).all() and x.groupby('plot').size().eq(6).all()
 x['block']=x['plot'].str.split('_').str[0];x['group']=x.month+'_'+x.color
 x=x.sort_values(['plot','date']);x['logn']=np.log1p(x.n);x['next_log']=x.groupby('plot').logn.shift(-1);x['next_n']=x.groupby('plot').n.shift(-1);x['next_date']=x.groupby('plot').date.shift(-1)
 x=x[x.next_date.notna()].copy();assert len(x)==310
 x['delta']=x.next_log-x.logn;x['raw_delta']=x.next_n-x.n;x['early']=(x.date.le('2023-05-19')).astype(int);x['worm5']=x.worm/5;x['stratum']=x.date+'_'+x.group
 def fit(data,y='delta',fixed=True,adjust=True):
  formula=f'{y} ~ C(stratum) + '+('C(plot)' if fixed else 'C(block)')+(' + logn' if adjust else '')+' + worm5 + worm5:early'
  r=smf.ols(formula,data).fit(cov_type='cluster',cov_kwds={'groups':data['plot'],'use_correction':True},use_t=True)
  def contrast(w):
   v=np.array([w.get(k,0) for k in r.params.index]);o=r.t_test(v);return {'estimate':float(np.asarray(o.effect).item()),'ci':np.asarray(o.conf_int()).ravel().tolist(),'p':float(np.asarray(o.pvalue).item())}
  return {'n':int(r.nobs),'n_plots':data['plot'].nunique(),'formula':formula,'late':contrast({'worm5':1}),'early':contrast({'worm5':1,'worm5:early':1}),'early_minus_late':contrast({'worm5:early':1})}
 flagged=set(d.loc[d.comment.fillna('').str.contains('outside|next to it',case=False),'plot'])
 mods={'primary':fit(x),'no_initial_stock':fit(x,adjust=False),'between_and_within':fit(x,fixed=False),'raw_change':fit(x,y='raw_delta'),'omit_flagged_plots':fit(x[~x['plot'].isin(flagged)])}
 for bl in sorted(x.block.unique()):mods['exclude_'+bl]=fit(x[x.block.ne(bl)])
 design=pd.get_dummies(x.stratum,dtype=float);design['logn']=x.logn.to_numpy();design['worm5']=x.worm5.to_numpy();design['worm_early']=(x.worm5*x.early).to_numpy();y=x.next_log.to_numpy();cv=[]
 for alpha in [.1,1,10]:
  row={'ridge_alpha':alpha,'folds':[]};e0=[];e1=[]
  for block in sorted(x.block.unique()):
   train=x.block.ne(block).to_numpy();test=~train;pred=[]
   for cols in [design.columns[:-2],design.columns]:
    X=design[cols].to_numpy();mu=X[train].mean(0);sd=X[train].std(0);sd[sd==0]=1;X=(X-mu)/sd
    model=Ridge(alpha=alpha).fit(X[train],y[train]);pred.append(np.maximum(0,model.predict(X[test])))
   q0=(y[test]-pred[0])**2;q1=(y[test]-pred[1])**2;e0.extend(q0);e1.extend(q1);row['folds'].append({'block':block,'n':int(test.sum()),'baseline_mse':float(q0.mean()),'worm_mse':float(q1.mean())})
  row.update(baseline_mse=float(np.mean(e0)),worm_mse=float(np.mean(e1)),relative_skill=float(1-np.mean(e1)/np.mean(e0)));cv.append(row)
 field={'n_plots':62,'n_intervals':310,'n_spatial_blocks':3,'flagged_plots':sorted(flagged),'models':mods,'cv':cv,'visit_summary':d[d.date.ne(d.sow)].groupby('date').agg(seedling_mean=('n','mean'),mound_mean=('worm','mean')).reset_index().to_dict('records')}
 s['pot']=s.pot.str.lower();s['integrity_recorded']=s.ball_integrity.gt(0);s['integrity_valid']=s.ball_integrity.where(s.integrity_recorded);s['emerged']=(s.n_green_leaves+s.n_white_leaves>0).astype(int);s['leaves']=s.n_green_leaves+s.n_white_leaves
 assert len(s)==2240 and s.ball_id.nunique()==448 and s.pot.nunique()==14 and s.replicate.nunique()==28 and not s.duplicated(['ball_id','date']).any()
 assert s.groupby('ball_id').size().eq(5).all() and s.groupby('ball_id')[['replicate','pot','treatment']].nunique().eq(1).all().all()
 assert s.groupby('replicate').ball_id.nunique().eq(16).all() and s.groupby('pot').replicate.nunique().eq(2).all()
 s=s.sort_values(['ball_id','date']);s['ever']=s.groupby('ball_id').emerged.cummax();end=s[s.date.eq(s.date.max())];first=s[s.date.eq(sorted(s.date.unique())[1])]
 assert len(end)==448
 tab=s.groupby(['treatment','replicate','pot','date']).agg(emerged=('emerged','mean'),leaves=('leaves','mean'),integrity=('integrity_valid','mean'),ever=('ever','mean')).reset_index();summary=[]
 for t,g in tab.groupby('treatment'):
  a=g.groupby('date')[['emerged','ever','leaves','integrity']].mean();last=end[end.treatment.eq(t)];beg=first[first.treatment.eq(t)];joint=beg[['ball_id','emerged']].merge(last[['ball_id','emerged']],on='ball_id',suffixes=('_early','_last'))
  summary.append({'treatment':t,'n_replicates':g.replicate.nunique(),'n_final':len(last),'final_visible':int(last.emerged.sum()),'ever_visible':int(last.ever.sum()),'early_visible':int(beg.emerged.sum()),'early_visible_final_absent':int(((joint.emerged_early==1)&(joint.emerged_last==0)).sum()),'trajectories':json.loads(a.reset_index().to_json(orient='records'))})
 last=tab[tab.date.eq(tab.date.max())].copy();assert len(last)==28
 model=smf.ols('emerged ~ C(treatment, Treatment(reference="naked seeds")) + C(pot)',last).fit()
 surf=s[~s.treatment.isin(['naked seeds','buried fireclay balls'])];later=surf[surf.date.ne(surf.date.min())];init=surf[surf.date.eq(surf.date.min())];ever_final=surf[surf.date.eq(surf.date.max())][['ball_id','ever']];init=init.merge(ever_final,on='ball_id',suffixes=('_initial','_final'),validate='one_to_one')
 audit={'later_crosstab':{str(int(e))+'|'+str(int(rec)):int(n) for (e,rec),n in later.groupby(['emerged','integrity_recorded']).size().items()},'initial_integrity_vs_ever_visible':{str(int(rec))+'|'+str(int(e)):int(n) for (rec,e),n in init.groupby(['integrity_recorded','ever_final']).size().items()}}
 ref=next(r for r in summary if r['treatment']=='naked seeds')
 for r in summary:
  r['final_deficit_vs_naked']=ref['final_visible']-r['final_visible'];r['ever_deficit_vs_naked']=ref['ever_visible']-r['ever_visible'];r['extra_disappearance_vs_naked']=(r['ever_visible']-r['final_visible'])-(ref['ever_visible']-ref['final_visible'])
  assert r['final_deficit_vs_naked']==r['ever_deficit_vs_naked']+r['extra_disappearance_vs_naked']
 seedball={'integrity_audit':audit,'n_units':448,'n_replicates':28,'n_pot_labels':14,'n_visits':5,'summary':summary,'pot_adjusted_contrasts_vs_naked':{k:float(v) for k,v in model.params.items() if 'C(treatment' in k},'pot_model_rank':int(model.model.rank),'pot_model_df_resid':float(model.df_resid),'replicate_end':json.loads(last.to_json(orient='records'))}
 return {'status':'response-open; no causal worm-stage effect or protection estimate','artifact_sha256':HASH,'field_source':m[0]['sha256'],'seedball_source':p['sha256'],'field':field,'seedball':seedball}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2,allow_nan=False)+'\n')
