#!/usr/bin/env python3
"""Verified raw PANGAEA event counts; published Kendrick Table 4 aggregate audit.
No direct observation of flowering time, mating synchronization, or animal effects."""
import hashlib,zipfile,json,io,itertools,argparse
from pathlib import Path
import numpy as np,pandas as pd
HASH='0052956db19a0fb8acf5c24a9bc712c829186ae35424f5aa8c361cd4aaa92cd3'
RAW='c96c00fff4bb0a430d016d3a45317989b946de66ba7ebf11a255974175a24295'
def run(path,out):
 out.mkdir(parents=True,exist_ok=True)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  m=json.loads(z.read('manifest.json'));raw=z.read('pangaea_937393.tsv');assert hashlib.sha256(raw).hexdigest()==RAW==m[-1]['sha256']
 d=pd.read_csv(io.StringIO(raw.decode('utf-8-sig').split('*/',1)[1]),sep='\t');d.columns=['event','date','tank','box','treat','shoot','new','newmonth','flower','pct','newpct','flowerpct'];d.date=pd.to_datetime(d.date)
 assert len(d)==576 and not d.duplicated(['tank','box','date']).any() and d.groupby(['treat','tank']).size().eq(48).all()
 assert d[['shoot','new','newmonth','flower','pct','newpct','flowerpct']].isna().all(axis=1).equals(d.shoot.isna())
 missing=d[d.shoot.isna()];assert len(missing)==12 and missing.tank.eq('E2').all() and missing.box.eq(4).all()
 d=d.dropna(subset=['shoot']).copy();assert len(d)==564 and (d.flower<=d.shoot).all() and (d[['shoot','flower','new']]>=0).all().all()
 assert np.max(np.abs(d.flower/6*100-d.flowerpct))<=.5
 assert np.max(np.abs(d.shoot/6*100-d.pct))<=.5
 a=d.groupby(['treat','tank','date'],as_index=False).agg(events=('flower','sum'),original=('shoot','sum'),boxes=('box','size'),new=('new','sum'));a['initial_monitored']=a.boxes*6
 a['events_per_initial']=a.events/a.initial_monitored;a['cumulative']=a.groupby(['treat','tank']).events.cumsum();a['cumulative_per_initial']=a.cumulative/a.initial_monitored
 assert a.groupby('tank').initial_monitored.nunique().eq(1).all()
 a['day']=(a.date-pd.Timestamp('2016-01-01')).dt.days
 dates=sorted(d.date.unique());prev=dict(zip(dates[1:],dates[:-1]));a['prev_day']=a.date.map(prev).apply(lambda x:(x-pd.Timestamp('2016-01-01')).days if pd.notna(x) else np.nan)
 assert a.loc[a.events.gt(0),'prev_day'].notna().all();a['midday']=(a.day+a.prev_day)/2
 cut=pd.Timestamp('2016-04-29');a['early']=a.events.where(a.date<=cut,0);a['late']=a.events.where(a.date>cut,0)
 by=a.groupby(['treat','date'],as_index=False).agg(events=('events','sum'),cumulative=('cumulative','sum'),tanks_with_event=('events',lambda s:(s>0).sum()),tanks_ever_positive=('cumulative',lambda s:(s>0).sum()),original=('original','sum'),initial=('initial_monitored','sum'),mean_tank_cumulative_rate=('cumulative_per_initial','mean'))
 q=a.groupby(['treat','tank'],as_index=False).agg(events=('events','sum'),early=('early','sum'),late=('late','sum'),initial=('initial_monitored','first'),first_original=('original','first'),final_original=('original','last'),new=('new','sum'))
 q['event_rate']=q.events/q.initial;q['early_rate']=q.early/q.initial;q['late_rate']=q.late/q.initial;q['final_original_rate']=q.final_original/q.initial
 for col in ['day','prev_day','midday']:
  tmp=a.assign(weighted=a.events*a[col].fillna(0)).groupby(['treat','tank']).weighted.sum().rename('event_sum_'+col).reset_index();q=q.merge(tmp,on=['treat','tank'],validate='one_to_one')
 rng=np.random.default_rng(20261125);B=40000;cells={k:v.reset_index(drop=True) for k,v in q.groupby('treat')};boot={}
 for k,v in cells.items():
  ix=rng.integers(0,6,size=(B,6));x={c:v[c].to_numpy()[ix] for c in ['events','early','late','event_rate','early_rate','late_rate','final_original_rate','event_sum_day','event_sum_prev_day','event_sum_midday']};boot[k]={c:z.mean(1) for c,z in x.items()};boot[k]['positive']=(x['events']>0).mean(1);boot[k]['early_positive']=(x['early']>0).mean(1);boot[k]['early_share']=np.divide(x['early'].sum(1),x['events'].sum(1),out=np.full(B,np.nan),where=x['events'].sum(1)>0)
  for t in ['day','prev_day','midday']:boot[k][t]=np.divide(x['event_sum_'+t].sum(1),x['events'].sum(1),out=np.full(B,np.nan),where=x['events'].sum(1)>0)
 def stats(v):
  n=int(v.events.sum());r={'events':n,'early':int(v.early.sum()),'late':int(v.late.sum()),'monitored_initial':int(v.initial.sum()),'positive_tanks':int(v.events.gt(0).sum()),'early_positive_tanks':int(v.early.gt(0).sum()),'early_share':float(v.early.sum()/n),'count_per_positive_tank':float(v[v.events.gt(0)].events.mean()),'mean_tank_event_rate':float(v.event_rate.mean()),'mean_tank_early_rate':float(v.early_rate.mean()),'mean_tank_late_rate':float(v.late_rate.mean()),'mean_tank_final_original_rate':float(v.final_original_rate.mean()),'pooled_event_rate':float(n/v.initial.sum())}
  for col in ['day','prev_day','midday']:r[col]=float(v['event_sum_'+col].sum()/n)
  return r
 arm={k:stats(v) for k,v in cells.items()};diff={}
 for name in ['event_rate','early_rate','late_rate','final_original_rate','positive','early_positive','early_share','day','midday']:
  b=boot['Heat'][name]-boot['Ambient'][name];diff[name]={'bootstrap95_conditional':np.nanquantile(b,[.025,.975]).tolist(),'valid_draws':int(np.isfinite(b).sum())}
 bounds=[arm['Heat']['prev_day']-arm['Ambient']['day'],arm['Heat']['day']-arm['Ambient']['prev_day']]
 loo=[]
 for i,j in itertools.product(range(6),repeat=2):
  c,h=stats(cells['Ambient'].drop(index=i)),stats(cells['Heat'].drop(index=j));loo.append([h['day']-c['day'],h['early_share']-c['early_share'],h['mean_tank_event_rate']-c['mean_tank_event_rate']])
 known=[('Stark Bay',110,100,0),('Parker Point',139,40,8)]
 recruits=[('Thomson Bay',2013,35,19,0),('Stark Bay',2013,27,23,1),('Parker Point',2013,29,9,7),('Thomson Bay',2014,30,9,3),('Stark Bay',2014,31,20,1),('Parker Point',2014,31,7,8)]
 kr=[dict(site=k,cohort=y,n=n,local=l,nonlocal_assigned=o,unresolved=n-l-o) for k,y,n,l,o in recruits]
 kd=[dict(site=k,n=n,local=l,nonlocal_assigned=o,unresolved=n-l-o,local_confirmation=l/n,incorrect_nonlocal_assignment=o/n) for k,n,l,o in known]
 kp=[]
 for k in sorted(set(x['site'] for x in kr)):
  s=[x for x in kr if x['site']==k];n,l,o,u=[sum(x[v] for x in s) for v in ['n','local','nonlocal_assigned','unresolved']];kp.append(dict(site=k,n=n,local=l,nonlocal_assigned=o,unresolved=u,observed_nonlocal_fraction=o/n,nonlocal_among_resolved=o/(l+o),unresolved_fraction=u/n,hypothetical_nonlocal_bounds_if_resolved_correct=[o/n,(o+u)/n]))
 res={'status':'PANGAEA raw-data reanalysis plus published Table4 accounting; no direct animal mechanism','archive_sha256':HASH,'source_sha256':RAW,'data_doi':'10.1594/PANGAEA.937393','paper_doi':'10.1002/lno.11947','audit':{'rows':576,'usable':564,'missing_box_all_dates':'E2 box4','tanks':12,'dates':12,'monitored_boxes':47,'published_ambient_events_implied_by_10.4pct':15,'table_ambient_events':14},'by_arm':arm,'bootstrap_differences':diff,'timing_interval_bounds_heat_minus_ambient_days':bounds,'loo_drop_one_tank_per_arm_ranges':dict(zip(['day_difference','early_share_difference','event_rate_difference'],np.array([np.min(loo,axis=0),np.max(loo,axis=0)]).T.tolist())),'kendrick':{'doi':'10.1002/ece3.10456','data_doi':'10.5061/dryad.vhhmgqnwz','status':'published Table4 only; original raw file HTTP401','known_origin':kd,'recruits':kr,'pooled_by_site':kp},'limits':['Seed-containing spathes counted once at first detection, not pollen release or actual fertilization date; 49-day Feb–Apr gap. No unobserved events identified.','Missing E2 box4 throughout; no imputation. Observed tank positive incidence for E2 uncertain. Paper reports 15 ambient events, data 14; no repair.','Six tanks per treatment, conditional bootstrap and response-open timing cutoff, not causal timing mediation. Treatment includes shared community processes; no animal manipulation.','Kendrick published assignment table: unresolved origin not nonlocal; known-origin assignment error especially Parker Point; bounds hypothetical perfect classification of resolved, not true origin bounds. Habitat predation reversals confounded with protocol and year.']}
 a.to_csv(out/'tank_date.csv',index=False);q.to_csv(out/'tank_season.csv',index=False);by.to_csv(out/'treatment_date.csv',index=False);pd.DataFrame(kp).to_csv(out/'recruit_origin_summary.csv',index=False);(out/'results.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n');return res
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.artifact,a.out);print(json.dumps(r,indent=2))
