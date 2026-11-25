#!/usr/bin/env python3
"""Core reproduction: paired-flower failure accounting and blueberry outcome coverage.
Descriptive, no causal mediation or unconditional yield estimate."""
import argparse, zipfile, hashlib, json, io
from pathlib import Path
import numpy as np, pandas as pd
H='860fa163a35d0d650e98b8e4d9e1f5e45b019eef9372c8068e9f29da75c5da44'
def run(path,out):
 out.mkdir(exist_ok=True,parents=True)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==H
 with zipfile.ZipFile(path) as z:
  m=json.loads(z.read('manifest.json'));hs={f['file']:f['sha256'] for a in m for f in a['files'] if f['status']=='ACQUIRED'}
  def read(n):
   b=z.read(n);assert hashlib.sha256(b).hexdigest()==hs[n];return pd.read_csv(io.BytesIO(b))
  c=read('10814705_PLdataindividual.csv');poll=read('10814705_pollinator.csv')
  def blue(kind,exp):return read(f'3987488_fruit_{kind}_{exp}_experiments_JAPPL-2020-00197.csv')
  s0,w0=blue('set','pollination'),blue('weight','pollination');s1,w1=blue('set','multiple_visits'),blue('weight','multiple_visits')
 def group(x,weights=None):
  x=np.asarray(x,float);w=np.ones(len(x)) if weights is None else np.asarray(weights,float);w=w/w.sum();p=w[x>0].sum();mu=(w*x).sum()
  return dict(n=len(x),zero=int((x==0).sum()),p_positive=float(p),mean=float(mu),positive_mean=float(mu/p) if p else None)
 def account(a,b):
  p,m=a['p_positive'],a['positive_mean'];q,n=b['p_positive'],b['positive_mean'];i=(q-p)*(m+n)/2;j=(n-m)*(p+q)/2
  assert np.isclose(i+j,b['mean']-a['mean'])
  return dict(delta=b['mean']-a['mean'],incidence=i,positive_magnitude=j)
 idx=['experimental.population','individual','autonomy','size','site','source.population'];assert len(c)==237 and not c.duplicated(idx+['treatment']).any() and c.seednumber.ge(0).all()
 p=c.pivot(index=idx,columns='treatment',values='seednumber').reset_index();complete=p.dropna(subset=['C','S']);assert len(p)==128 and len(complete)==109
 complete.to_csv(out/'campanula_pairs.csv',index=False)
 camp={}
 for mode,dd in [('complete_plant',complete),('available_C',p[p.C.notna()]),('complete_population_equal',complete)]:
  cells={};src={}
  for (aut,size),x in dd.groupby(['autonomy','size']):
   w=1/x.groupby('experimental.population').individual.transform('size') if mode=='complete_population_equal' else None
   v={'C':group(x.C,w),'n_pop':x['experimental.population'].nunique()}
   if mode!='available_C':v.update(S=group(x.S,w),S_minus_C=account(v['C'],group(x.S,w)),C_zero_S_positive=int((x.C.eq(0)&x.S.gt(0)).sum()),C_positive_S_zero=int((x.C.gt(0)&x.S.eq(0)).sum()),both_zero=int((x.C.eq(0)&x.S.eq(0)).sum()))
   cells[aut+'|'+size]=v
  for (sp,sz),x in dd.groupby(['source.population','size']):
   w=1/x.groupby('experimental.population').individual.transform('size') if mode=='complete_population_equal' else None;src[sp+'|'+sz]=group(x.C,w)
  camp[mode]={'cells':cells,'source_cells':src,'source_small_minus_single':{sp:account(src[sp+'|single'],src[sp+'|small']) for sp in ['AB','V','AL79','VA73']},'contrasts':{**{aut+'_small_minus_single':account(cells[aut+'|single']['C'],cells[aut+'|small']['C']) for aut in ['high','low']},**{sz+'_high_minus_low':account(cells['low|'+sz]['C'],cells['high|'+sz]['C']) for sz in ['single','small']}}}
 camp['coverage']={'plants_by_population_key':len(p),'complete_pairs':len(complete),'C_only':int((p.C.notna()&p.S.isna()).sum()),'S_only':int((p.C.isna()&p.S.notna()).sum()),'seed_populations':c['experimental.population'].nunique(),'pollinator_populations':poll['experimental.population'].nunique(),'pollinator_only_ids':sorted(set(poll['experimental.population'])-set(c['experimental.population']))}
 def blueberry(s,w,exp):
  key=['Species','Block','Year','RP','Tag'];assert not s.duplicated(key).any() and not w.duplicated(key).any()
  x=s.merge(w[key+['FS','Fresh.wgt']],on=key,how='left',suffixes=('_set','_w'),validate='one_to_one');matched=x.FS_w.notna();assert not (matched & x.FS_set.ne(x.FS_w)).any()
  same=x['Fresh.wgt_set'].notna()&x['Fresh.wgt_w'].notna();assert np.allclose(x.loc[same,'Fresh.wgt_set'],x.loc[same,'Fresh.wgt_w'])
  x['mass']=x['Fresh.wgt_set'].combine_first(x['Fresh.wgt_w']);x['valid_mass']=x.mass.where(x.FS_set.eq(1)&x.mass.gt(0));x['fs0_mass']=x.FS_set.eq(0)&x.mass.gt(0)
  x['group']=pd.cut(x.sumvisits,[-1,0,1,3,5,15],labels=['0','1','2-3','4-5','6-15']).astype(str) if exp=='visits' else x.TREATMENT
  rows=[]
  for (sp,gp),g in x.groupby(['Species','group']):
   rows.append(dict(Species=sp,group=gp,n=len(g),fruit_set=int(g.FS_set.sum()),p_set=float(g.FS_set.mean()),n_mass=int(g.valid_mass.count()),mass_coverage_given_set=float(g.valid_mass.count()/g.FS_set.sum()) if g.FS_set.sum() else None,mean_measured_positive_mass=float(g.valid_mass.mean()) if g.valid_mass.notna().any() else None,fs0_positive_mass=int(g.fs0_mass.sum())))
  pd.DataFrame(rows).to_csv(out/f'blueberry_{exp}_groups.csv',index=False)
  comps=[('0','1'),('1','6-15'),('1','2-3')] if exp=='visits' else [('No pollination','Self pollination'),('Self pollination','Cross pollination')]
  contrasts=[]
  for sp,g in x.groupby('Species'):
   for ref,trt in comps:
    z=[]
    for (bl,yr),v in g.groupby(['Block','Year']):
     a,b=v[v.group.eq(ref)],v[v.group.eq(trt)]
     if min(len(a),len(b))<5:continue
     t=dict(block=bl,year=int(yr),n_ref=len(a),n_trt=len(b),p_ref=float(a.FS_set.mean()),p_trt=float(b.FS_set.mean()),n_mass_ref=int(a.valid_mass.count()),n_mass_trt=int(b.valid_mass.count()))
     if min(a.valid_mass.count(),b.valid_mass.count())>=5:t.update(mass_ref=float(a.valid_mass.mean()),mass_trt=float(b.valid_mass.mean()))
     z.append(t)
    if z:
     zz=pd.DataFrame(z);v=zz.p_trt-zz.p_ref;e=dict(species=sp,reference=ref,treatment=trt,site_year_n=len(z),mean_RD=float(v.mean()),positive_strata=int(v.gt(0).sum()),by_stratum=z)
     if 'mass_ref' in zz:
      zz=zz.dropna(subset=['mass_ref','mass_trt']);e.update(mass_strata_n=len(zz),mean_mass_difference_g=float((zz.mass_trt-zz.mass_ref).mean()))
     contrasts.append(e)
  return dict(set_rows=len(s),weight_rows=len(w),matched=int(matched.sum()),weight_only=len(w)-int(matched.sum()),set_flag_conflicts=0,positive_mass_with_FS0=int(x.fs0_mass.sum()),FS1=int(x.FS_set.sum()),FS1_with_positive_mass=int(x.valid_mass.count()),groups=rows,common_site_year_contrasts=contrasts)
 r=dict(status='descriptive endpoint comparison; no unconditional mass or pooled meta-analysis',artifact_sha256=H,source_sha256=hs,campanula=camp,blueberry_pollination=blueberry(s0,w0,'pollination'),blueberry_visits=blueberry(s1,w1,'visits'))
 (out/'results.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
 return r
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('artifact',type=Path);a.add_argument('--out',type=Path,required=True);p=a.parse_args();run(p.artifact,p.out)
