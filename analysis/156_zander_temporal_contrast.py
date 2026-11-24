"""Reproduce tank-level temporal contrasts in Zander et al. PANGAEA 984655."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
HASH='05f7586f961ea26fe6685155eac93078ac62a8c0213dfa0222fceac02744ea33'
def run(path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  m=json.loads(z.read('manifest.json'));name='pangaea_984655.tsv';b=z.read(name);src=next(r for r in m if r.get('file')==name);assert hashlib.sha256(b).hexdigest()==src['sha256']
 d=pd.read_csv(io.StringIO(b.decode('utf-8-sig').split('*/',1)[1].strip()),sep='\t');assert d.columns.tolist()==src['columns'];d.columns=['origin','date','species','box','n','asym','density','sow','tempchange','adapt','day','aday','temp_tr','temp','sal_tr','sal','color']
 d['tank']=d.box.str.extract(r'^(T\d+)')
 assert len(d)==3384 and d.box.nunique()==72 and d.tank.nunique()==12 and d.aday.nunique()==47 and not d.duplicated(['box','aday']).any()
 assert d.groupby('tank').box.nunique().eq(6).all() and d.groupby('box').aday.nunique().eq(47).all()
 assert d.groupby('box')[['origin','color','temp_tr']].nunique().eq(1).all().all() and d.groupby('tank').temp_tr.nunique().eq(1).all()
 assert d.n.between(0,100).all() and (d.n%1==0).all()
 d['sal_group']=d.groupby('tank').sal_tr.transform(lambda x:x.mode().iloc[0])
 mismatch=d[d.sal_group!=d.sal_tr][['tank','box','date','sal_tr','sal']].to_dict('records');assert len(mismatch)==1
 wrong=d[(d.sal_group.eq('5')&d.sal.gt(10))|(d.sal_group.eq('18-20')&d.sal.lt(10))][['tank','date']].drop_duplicates();bad=set(wrong.tank);assert bad=={'T1','T7'}
 d['condition']=d.sal_group+'|'+d.temp_tr.astype(str)
 t=d.groupby(['tank','condition','aday']).n.mean().unstack('aday');assert t.shape==(12,47)
 days=np.array(t.columns,dtype=float);assert days[0]==0 and days[-1]==93
 a=t.reset_index()[['tank','condition']].copy()
 for day in [31,40,48,63,93]:a['day'+str(day)]=t[day].values
 a['late_change']=a.day93-a.day40
 a['stock_auc_0_93']=np.trapz(t.values,days,axis=1)/93
 a['early_stock_auc_0_40']=np.trapz(t.loc[:,t.columns<=40].values,days[days<=40],axis=1)/40
 a['peak_day']=t.idxmax(axis=1).values;a['peak_stock']=t.max(axis=1).values
 a['half_peak_day']=np.array([days[np.where(row>=row.max()/2)[0][0]] for row in t.values])
 a['day40_fraction_of_peak']=a.day40/a.peak_stock;a['day93_fraction_of_peak']=a.day93/a.peak_stock
 metrics=list(a.columns[2:]);rng=np.random.default_rng(20261124)
 def compare(a):
  out={}
  for sal in ['5','18-20']:
   x=a[a.condition.eq(sal+'|5')];y=a[a.condition.eq(sal+'|10')];assert len(x)>=2 and len(y)>=2
   ix=rng.integers(len(x),size=(50000,len(x)));iy=rng.integers(len(y),size=(50000,len(y)))
   out[sal]={'n_5':len(x),'n_10':len(y),'metrics':{}}
   for m in metrics:
    xx=x[m].to_numpy(float);yy=y[m].to_numpy(float)
    out[sal]['metrics'][m]={'mean_5':float(xx.mean()),'mean_10':float(yy.mean()),'diff_10_minus_5':float(yy.mean()-xx.mean()),'conditional_ci':np.quantile(yy[iy].mean(1)-xx[ix].mean(1),[.025,.975]).tolist()}
  return out
 primary=compare(a);sensitivity=compare(a[~a.tank.isin(bad)])
 loo={}
 for tank in a.tank:
  aa=a[~a.tank.eq(tank)]
  loo[tank]={s:{m:float(aa[aa.condition.eq(s+'|10')][m].mean()-aa[aa.condition.eq(s+'|5')][m].mean()) for m in ['day40','day93','late_change','half_peak_day']} for s in ['5','18-20']}
 c=d.groupby(['tank','condition','color','aday']).n.mean().unstack('aday').reset_index();color={}
 for sal in ['5','18-20']:
  color[sal]={}
  for co in ['Grey','Dark','Light']:
   x=c[c.condition.eq(sal+'|5')&c.color.eq(co)];y=c[c.condition.eq(sal+'|10')&c.color.eq(co)]
   color[sal][co]={str(v):{'mean_5':float(x[v].mean()),'mean_10':float(y[v].mean()),'diff':float(y[v].mean()-x[v].mean())} for v in [40,93]}
 return dict(status='response-open original-data tank-level descriptive comparison, no animal treatment',source='10.1594/PANGAEA.984655',paper='10.1111/rec.70396',artifact_sha256=HASH,source_sha256=src['sha256'],audit=dict(n_rows=len(d),n_tanks=d.tank.nunique(),n_boxes=d.box.nunique(),n_dates=d.aday.nunique(),n_seedling_count_decreases=int(d.sort_values(['box','aday']).groupby('box').n.diff().lt(0).sum()),salinity_label_mismatch=mismatch,measured_salinity_anomaly_tank_dates=wrong.to_dict('records'),n_inconsistent_measured_salinity_tank_dates=int(d.groupby(['tank','aday']).sal.nunique().gt(1).sum()),n_inconsistent_measured_temperature_tank_dates=int(d.groupby(['tank','aday']).temp.nunique().gt(1).sum())),tank_metrics=a.to_dict('records'),primary=primary,exclude_T1_T7=sensitivity,leave_one_tank_out=loo,color_descriptive=color,trajectories=[{'condition':r[0],'aday':int(r[1]),'mean_count':float(v)} for r,v in d.groupby(['condition','aday']).n.mean().items()])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2,allow_nan=False)+'\n')
