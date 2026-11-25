#!/usr/bin/env python3
"""Core reproduction: field recovery tail and within-plot recruitment dispersion.
Independent studies, no joint causal effect. Full local analysis also includes plot bootstraps."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import hypergeom,binom
from openpyxl import load_workbook
H1='144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c'
H2='ad0097d3e14373bf0cb7babef0dd4aa26678d6bb97c7e5d94af5f7e534bc05e1'
def run(a,b,out):
 out.mkdir(parents=True,exist_ok=True)
 assert hashlib.sha256(a.read_bytes()).hexdigest()==H1 and hashlib.sha256(b.read_bytes()).hexdigest()==H2
 with zipfile.ZipFile(a) as z:
  m=json.loads(z.read('manifest.json'));name='infantes_one_week.xlsx';f=next(x for x in m['sources'] if x.get('file')==name);buf=z.read(name);assert hashlib.sha256(buf).hexdigest()==f['sha256'];r=list(load_workbook(io.BytesIO(buf),data_only=True).active.values)
 assert r[2][:6]==('Trial','LABEL','CODE','TREATMENT','Seeds','Art. Seeds')
 d=pd.DataFrame([dict(trial=t,label=l,arm=arm,real=int(k),mimic=int(m),coats=int(co)) for t,l,_,arm,k,m,co,*_ in r[3:]])
 assert len(d)==30 and d.real.between(0,200).all() and d.mimic.between(0,20).all()
 arms=['CAGE','CAGE-HAND','CAGE-SAND'];p=d[d.arm.isin(arms)].copy();assert len(p)==18 and not p.duplicated(['trial','label']).any() and p.groupby(['trial','arm']).size().eq(3).all()
 field={}
 for arm in arms:
  field[arm]={}
  for col,n in [('real',200),('mimic',20)]:
   x=np.stack([n-p[p.arm.eq(arm)&p.trial.eq(t)][col].to_numpy() for t in [2,3]])
   prob=float(x.mean()/n);tail=float(hypergeom.pmf(10,n,x,10).mean());ref=float(np.mean((x.mean(1)/n)**10))
   field[arm][col]=dict(loss_counts=x.tolist(),mean_loss=prob,near_total=float((x/n>=.8).mean()),full_loss=float((x==n).mean()),ten_draw_all_lost=tail,homogeneous_p10=prob**10,trial_homogeneous_p10=ref,trial_conditional_excess=tail-ref,pair_excess=float((x*(x-1)/(n*(n-1))).mean()-prob**2))
 p.to_csv(out/'field_plot_counts.csv',index=False)
 with zipfile.ZipFile(b) as z:
  m=json.loads(z.read('manifest.json'));f2=next(e for e in m if e.get('doi')=='10.34894/FKSY2M')['files'][0];buf=z.read(f2['file']);assert hashlib.sha256(buf).hexdigest()==f2['sha256'];w=pd.read_excel(io.BytesIO(buf),sheet_name='Recruitment_success&efficiency')
 assert len(w)==144 and not w.duplicated(['Plot_ID','Year','Replicate']).any() and w.groupby(['Plot_ID','Year']).size().eq(4).all()
 q=w.pivot(index=['Plot_ID','Block','Restoration_scale_m²','Seeding_density/m²','Year'],columns='Replicate',values='Recruitment_success').reset_index()
 counts=q[[1,2,3,4]].to_numpy();assert np.all(counts>=0) and np.all(counts%1==0);s=counts.sum(1);assert np.all(s>0)
 q['total']=s;q['mean']=s/4;q['dispersion']=((counts-s[:,None]/4)**2/(s[:,None]/4)).sum(1)/3
 for k in [0,1,3]:
  q['obs_le'+str(k)]=(counts<=k).sum(1);q['exp_le'+str(k)]=4*binom.cdf(k,s,.25)
 q['same_quadrat_pair_excess']=np.divide((counts*(counts-1)).sum(1),s*(s-1),out=np.full(len(s),np.nan),where=s>1)-.25
 rng=np.random.default_rng(20261125);B=50000
 def test(x):
  tot=x.total.to_numpy();sim=np.stack([rng.multinomial(int(n),[.25]*4,size=B) for n in tot],axis=1)
  obs=float(x.dispersion.mean());null=(((sim-tot[None,:,None]/4)**2/(tot[None,:,None]/4)).sum(2)/3).mean(1)
  o=dict(n_plots=len(x),mean_dispersion=obs,conditional_mc_p=float((1+sum(null>=obs-1e-12))/(B+1)),null_mc95=np.quantile(null,[.025,.975]).tolist())
  for k in [0,1,3]:
   v=int(x['obs_le'+str(k)].sum());nn=(sim<=k).sum((1,2));o['le'+str(k)]=dict(observed=v,expected=float(x['exp_le'+str(k)].sum()),p_excess=float((1+sum(nn>=v))/(B+1)))
  return o
 rec={str(y):test(q[q.Year.eq(y)]) for y in [2020,2021]}
 second=q[q.Year.eq(2021)]
 sens={name:test(x) for name,x in [('exclude_400_high',second[~(second['Restoration_scale_m²'].eq(400)&second['Seeding_density/m²'].eq(50))]),('exclude_two_max_dispersion',second.drop(second.dispersion.nlargest(2).index)),*[(f'exclude_block_{i}',second[second.Block.ne(i)]) for i in [1,2,3]]]}
 by=q.groupby(['Year','Seeding_density/m²']).same_quadrat_pair_excess.agg(['count','mean']).reset_index().to_dict('records')
 wide=q.pivot(index=['Plot_ID','Block','Restoration_scale_m²','Seeding_density/m²'],columns='Year',values='dispersion');d=(wide[2021]-wide[2020]).groupby('Block').mean()
 q.to_csv(out/'recruitment_plot_dispersion.csv',index=False)
 res=dict(status='original-data exploratory diagnostics, not a causal spatial model',source_hashes=[f['sha256'],f2['sha256']],field=field,recruitment=rec,sensitivity_2021=sens,same_quadrat_pair_excess_by_dose=by,paired_year_change_by_block=d.to_list())
 (out/'results.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
 return res
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('predation',type=Path);p.add_argument('restoration',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.predation,a.restoration,a.out)
