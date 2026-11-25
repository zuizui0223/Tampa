#!/usr/bin/env python3
"""Observed zero outcomes versus positive outcome size. Accounting, not mediation."""
import hashlib,io,json,zipfile,itertools,argparse
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import binomtest
from openpyxl import load_workbook
H1='843038aefe1afaed39ded71f4d5e5890262a778300c1f0ab011245b7e61ead8a'
H2='144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c'
def run(a,b):
 assert hashlib.sha256(a.read_bytes()).hexdigest()==H1 and hashlib.sha256(b.read_bytes()).hexdigest()==H2
 with zipfile.ZipFile(a) as z:
  m=json.loads(z.read('manifest.json'));hs={x['file']:x['sha256'] for x in m[2]['members']}
  def read(n):
   v=z.read(n);assert hashlib.sha256(v).hexdigest()==hs[n];return pd.read_csv(io.BytesIO(v),sep=';')
  lab=read('hautekiet_262_Survival_data.csv');field=read('hautekiet_9_SeedlingSurvival_Vaucheria-vs-Mud.csv')
 with zipfile.ZipFile(b) as z:
  m=json.loads(z.read('manifest.json'));n='infantes_eight_month.xlsx';f=next(x for x in m['sources'] if x.get('file')==n);v=z.read(n);assert hashlib.sha256(v).hexdigest()==f['sha256'];r=list(load_workbook(io.BytesIO(v),data_only=True).active.values)
  sea=pd.DataFrame([dict(plot=i,treatment=t,y=float(k)) for i,t,k,*_ in r[4:] if i is not None])
 assert len(lab)==40 and lab.Pot.is_unique and lab.nr_start.eq(5).all() and lab.nr_end.between(0,5).all() and lab.groupby(['Worms','Vaucheria']).size().eq(10).all()
 assert len(field)==12 and field.Start_nr.eq(5).all() and field.End_nr.between(0,5).all() and not field.duplicated(['Plot','Treatment']).any()
 fw=field.pivot(index='Plot',columns='Treatment',values='End_nr');assert fw.notna().all().all() and len(fw)==6
 assert len(sea)==12 and sea['plot'].is_unique and sea.groupby('treatment').size().eq(4).all()
 def group(x):
  n=len(x);positive=int((x>0).sum());ci=binomtest(n-positive,n).proportion_ci(.95,method='exact')
  return dict(n=n,zero=n-positive,zero_fraction=(n-positive)/n,zero_exact_ci_independent_units=[ci.low,ci.high],mean=float(x.mean()),p_positive=positive/n,positive_mean=float(x[x>0].mean()) if positive else None,counts=x.tolist())
 def split(p,q):
  a,b=(p>0).mean(),(q>0).mean()
  if a==0 or b==0:return None
  c,d=p[p>0].mean(),q[q>0].mean();x=(b-a)*(c+d)/2;y=(d-c)*(a+b)/2
  assert np.isclose(x+y,q.mean()-p.mean());return np.array([x,y])
 rng=np.random.default_rng(20261125);B=40000
 def contrast(p,q,paired=False):
  p,q=np.array(p,dtype=float),np.array(q,dtype=float);a,b=group(p),group(q);delta=q.mean()-p.mean();parts=split(p,q)
  ix=rng.integers(0,len(p),(B,len(p)));iy=ix if paired else rng.integers(0,len(q),(B,len(q)))
  pp,qq=p[ix],q[iy];pa,pb=(pp>0).mean(1),(qq>0).mean(1);valid=(pa>0)&(pb>0);pc=pp.mean(1)[valid]/pa[valid];pd_=qq.mean(1)[valid]/pb[valid];part1=(pb[valid]-pa[valid])*(pc+pd_)/2;part2=(pd_-pc)*(pa[valid]+pb[valid])/2
  out=dict(reference=a,treatment=b,mean_difference=float(delta),mean_difference_ci=np.quantile(qq.mean(1)-pp.mean(1),[.025,.975]).tolist(),zero_difference=float(a['zero_fraction']*-1+b['zero_fraction']),zero_difference_ci=np.quantile(pa-pb,[.025,.975]).tolist(),accounting_parts=parts.tolist() if parts is not None else None,accounting_fraction_undefined_bootstrap=float(1-valid.mean()),accounting_ci_conditional_both_positive=[np.quantile(z,[.025,.975]).tolist() for z in [part1,part2]] if valid.any() else None)
  if paired:out['discordant_zero']={'improved':int(((p==0)&(q>0)).sum()),'worse':int(((p>0)&(q==0)).sum())}
  return out
 cells={k:g.nr_end.to_numpy()/5 for k,g in lab.groupby(['Worms','Vaucheria'])}
 return {'status':'executed original-data arithmetic decomposition; no causal mediator or meta-analysis','source_hashes':[hs['hautekiet_262_Survival_data.csv'],hs['hautekiet_9_SeedlingSurvival_Vaucheria-vs-Mud.csv'],f['sha256']], 'lab_algae_no_worm':contrast(cells[0,0],cells[0,1]),'lab_algae_with_worm':contrast(cells[1,0],cells[1,1]),'field_algal_habitat':contrast(fw.Mud.to_numpy()/5,fw.Vau.to_numpy()/5,True),'eelgrass_closed_vs_open_cage':contrast(sea.loc[sea.treatment.eq('Open cage'),'y'],sea.loc[sea.treatment.eq('Close cage'),'y']),'eelgrass_closed_vs_no_cage':contrast(sea.loc[sea.treatment.eq('No cage'),'y'],sea.loc[sea.treatment.eq('Close cage'),'y']),'limits':['Zero is observed at endpoint, not proven permanent extinction. Positive outcome subset is post-treatment; accounting terms not causal mechanisms.','Intervals conditional on small number of pots or field plots; exact binomial intervals assume independent units. Bootstrap boundary degeneracy. Paired habitat comparison is not randomized algae effect.','Hautekiet lab and field are same publication, not independent study-level replication. Infantes endpoint count not per-seed survival; original denominator conflict. No pooling.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('marsh',type=Path);p.add_argument('eelgrass',type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.write_text(json.dumps(run(a.marsh,a.eelgrass),indent=2,allow_nan=False)+'\n')
