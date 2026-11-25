#!/usr/bin/env python3
"""Fixed-dose seed-loss clustering diagnostic, not a density-response experiment."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
from scipy.stats import binom, betabinom
from openpyxl import load_workbook
HASH='144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c'
SPECS=[('Carcinus maenas',3,37,7,8),('Pagurus bernhardus',41,70,2,3),('Strongylocentrotus droebachiensis',73,102,3,4)]
def run(path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  m=json.loads(z.read('manifest.json'));f=next(x for x in m['sources'] if x.get('file')=='infantes_burial.xlsx');b=z.read(f['file']);assert hashlib.sha256(b).hexdigest()==f['sha256'];r=list(load_workbook(io.BytesIO(b),data_only=True).active.values)
 def models(x):
  p=(x.sum()+.5)/(10*len(x)+1);raw=x.mean()/10
  pair=np.mean(x*(x-1)/90);rho=np.clip((pair-raw**2)/max(raw*(1-raw),1e-12),0,.99)
  k=np.arange(11);pb=binom.pmf(k,10,p)
  pm=betabinom.pmf(k,10,p*(1-rho)/rho,(1-p)*(1-rho)/rho) if rho>1e-10 else pb
  return pb,pm,float(rho)
 out=[];preds=[];rng=np.random.default_rng(20261125)
 for sp,lo,hi,n,k in SPECS:
  for d in [0,1,2]:
   x=np.array([a[n]-a[k] for a in r[lo-1:hi] if a[1]==d],int);assert np.all((x>=0)&(x<=10));p=x.mean()/10
   a=rng.choice(x,(30000,len(x)),replace=True);m=a.mean(1)/10
   delta=(a==10).mean(1)-m**10;pairdelta=(a*(a-1)/90).mean(1)-m*m
   z=models(x);o=dict(species=sp,depth_cm=d,n=len(x),counts=np.bincount(x,minlength=11).tolist(),p_loss=float(p),any_loss=float(np.mean(x>0)),all_loss=float(np.mean(x==10)),all_loss_independent=float(p**10),excess_all_loss=float(np.mean(x==10)-p**10),excess_all_loss_bootstrap95=np.quantile(delta,[.025,.975]).tolist(),within_tank_pair_excess=float(np.mean(x*(x-1)/90)-p*p),within_tank_pair_excess_bootstrap95=np.quantile(pairdelta,[.025,.975]).tolist(),moment_rho=z[2])
   for i,v in enumerate(x):
    pb,pm,rho=models(np.delete(x,i));preds.append(dict(species=sp,depth_cm=d,observed=int(v),bin_logscore=float(-np.log(pb[v])),bb_logscore=float(-np.log(pm[v])),bin_all=float(pb[10]),bb_all=float(pm[10]),bin_zero=float(pb[0]),bb_zero=float(pm[0]),rho=rho))
   out.append(o)
 def score(rows):
  x=np.array([r['observed'] for r in rows]);a=np.array([r['bin_logscore'] for r in rows]);b=np.array([r['bb_logscore'] for r in rows]);out={'n':len(rows),'mean_nll_bin':float(a.mean()),'mean_nll_beta_binomial':float(b.mean()),'nll_improvement':float((a-b).mean()),'tanks_improved':int((b<a-1e-12).sum())}
  for v,tag in [(0,'zero'),(10,'all')]:
   y=x==v;out[tag+'_brier_bin']=float(np.mean((y-np.array([r['bin_'+tag] for r in rows]))**2));out[tag+'_brier_bb']=float(np.mean((y-np.array([r['bb_'+tag] for r in rows]))**2))
  return out
 scored={'surface':score([r for r in preds if r['depth_cm']==0]),'surface_and_1cm':score([r for r in preds if r['depth_cm']<2]),'all':score(preds),'by_species_surface':{sp:score([r for r in preds if r['species']==sp and r['depth_cm']==0]) for sp,*_ in SPECS}}
 independent=[]
 for sp,n,positive,full in [('Dyspanopeus sayi',18,13,5),('Pagurus longicarpus',20,4,3)]:
  pmin=(10*full+positive-full)/(10*n);pmax=(10*full+9*(positive-full))/(10*n)
  independent.append(dict(species=sp,n=n,positive=positive,full=full,empirical_all=full/n,mean_loss_bounds=[pmin,pmax],independent_all_upper=pmax**10,excess_all_lower=full/n-pmax**10))
 return dict(status='exploratory fixed-dose within-tank loss clustering; no inference on density response or spatial layout',artifact_sha256=HASH,source_doi='10.1371/journal.pone.0168128',groups=out,loo_scores=scored,loo_predictions=preds,independent_published_bounds={'doi':'10.1111/1365-2745.13154','n_seed_per_tank':10,'duration_days':5,'rows':independent},limits=['Tank is observation unit. No seed-level independence assumption for empirical intervals.','Binomial is a homogeneous probability benchmark, not a mechanistic null for a shared predator. Beta-binomial moment fit is exploratory, not external prediction.','All-zero groups have no resolved variation; empirical bootstrap intervals at zero are degenerate, not evidence of true zero.','Predator individual heterogeneity, detection, shared tank conditions or repeated attacks can produce clustering; not identified causal seed-to-seed contagion.','No seed density or allocation manipulation; cannot infer attraction or satiation. Carroll bounds from reported counts, not raw data.'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2,allow_nan=False)+'\n')
