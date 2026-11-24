#!/usr/bin/env python3
"""Size information loss audit. Glacier Bay clam counts, not SIBES or plant risk."""
import argparse, hashlib, zipfile, json, io
from pathlib import Path
import pandas as pd, numpy as np
from scipy.stats import spearmanr
H1='d4b902fb8216844bb078cf9ba0e9a87f1767defc1781534245761a45c82cadfd'
H2='e54e44830d2906015cae7434fb0bf3fd13a5145340efad3084523ec84126b7ac'
KEY=['year','region','site_zone','site_name']
TAXA=['Leukoma staminea','Saxidomus gigantea','Strongylocentrotus droebachiensis','Macoma spp.','Mya spp.']
def run(a,b):
 assert hashlib.sha256(a.read_bytes()).hexdigest()==H1
 assert hashlib.sha256(b.read_bytes()).hexdigest()==H2
 with zipfile.ZipFile(a) as z:
  m=json.loads(z.read('manifest.json'));f=next(f for s in m['sources'] if s['name']=='benthos' for f in s['files'] if 'sizeCount' in f['source_name']); raw=z.read(f['file']);assert hashlib.sha256(raw).hexdigest()==f['sha256'];d=pd.read_csv(io.BytesIO(raw))
 with zipfile.ZipFile(b) as z:
  m=json.loads(z.read('manifest.json'));raw=z.read('benthos_sites.csv');assert hashlib.sha256(raw).hexdigest()==next(x['sha256'] for x in m if x['file']=='benthos_sites.csv');s=pd.read_csv(io.BytesIO(raw))
 for x in [d,s]:x.site_name=x.site_name.astype(str)
 d=d.merge(s[['year','site_name','site_zone','site_selection']],on=['year','site_name','site_zone'],how='inner',validate='many_to_one')
 d=d[d.site_zone.eq('Intertidal')&d.site_selection.eq('Random')].copy()
 q=d[KEY+['quad']].drop_duplicates().groupby(KEY).size().rename('nq')
 x=d[d['count'].gt(0)&d.scientific_name.isin(TAXA)].copy();assert x['size'].notna().all() and x['size'].ge(14).all()
 assert x['size'].mod(1).eq(0).all()
 x['size_sum']=x['size']*x['count'];x['cube']=x['count']*(x['size']/50)**3
 def data(g,t):
  g=g.copy();g['large']=g['count']*g['size'].ge(t)
  a=g.groupby(KEY)[['count','size_sum','cube','large']].sum().join(q,how='left').reset_index();a['density']=a['count']/a.nq;a['mean_length']=a.size_sum/a['count'];a['cube_density']=a.cube/a.nq;a['large_density']=a.large/a.nq;a['large_frac']=a.large/a['count'];a['mean_cube_mass']=a.cube/a['count']
  a['cube_mean_proxy']=a.density*(a.mean_length/50)**3
  a['jensen_ratio']=a.cube_density/a.cube_mean_proxy
  a['upper_large_frac']=np.minimum(1,a.mean_cube_mass/(t/50)**3)
  assert (a.large_frac<=a.upper_large_frac+1e-9).all()
  return a
 def metrics(a):
  n=len(a);cols=['density','mean_length','cube_density','cube_mean_proxy','mean_cube_mass'];r={'n_events':n,'n_sites':a.site_name.nunique(),'individuals':int(a['count'].sum()),'large_positive':int(a.large.gt(0).sum()),'jensen_ratio_median':float(a.jensen_ratio.median()),'upper_bound_gap_median':float((a.upper_large_frac-a.large_frac).median())}
  if n<10 or a.large_density.nunique()<2:return r
  r['rho']={v:float(spearmanr(a[v],a.large_density).statistic) for v in cols}
  t=a.large_density.quantile(.75);ref=a.large_density.ge(t)&a.large_density.gt(0)
  r['top_quartile_large']=int(ref.sum());r['top_sets']={}
  for v in cols:
   pred=a[v].ge(a[v].quantile(.75)); inter=(pred&ref).sum();union=(pred|ref).sum()
   r['top_sets'][v]={'n_pred':int(pred.sum()),'intersection':int(inter),'jaccard':float(inter/union),'recall':float(inter/ref.sum()),'excluded_large_top':int((ref&~pred).sum())}
  v=a[['density','mean_length','large_frac','large_density','count']].to_numpy();i,j=np.triu_indices(n,1);keep=(np.abs(np.log(v[i,0]/v[j,0]))<=np.log(1.1))&(np.abs(v[i,1]-v[j,1])<=3);i,j=i[keep],j[keep];diff=np.abs(v[i,2]-v[j,2]);r['similar_density_mean_pairs']={'n_pairs':len(diff),'large_fraction_gap_median':float(np.median(diff)) if len(diff) else None,'gap_ge_20pp':int((diff>=.20-1e-12).sum())}
  if len(diff):
   k=np.argmax(diff);r['similar_pair_max']={'gap':float(diff[k]),'events':a.iloc[[i[k],j[k]]][KEY+['count','nq','density','mean_length','large_frac','large_density']].to_dict('records')}
  return r
 out={};tables=[]
 for tax in TAXA:
  g=x[x.scientific_name.eq(tax)];out[tax]={}
  for t in [40,50,60]:
   a=data(g,t);a['taxon']=tax;a['threshold_mm']=t;tables.append(a)
   out[tax][str(t)]={'all_positive':metrics(a),'min5_individuals':metrics(a[a['count'].ge(5)].reset_index(drop=True)),'min10_individuals':metrics(a[a['count'].ge(10)].reset_index(drop=True))}
 return {'source':'10.5066/P9LODH0Z','archives':[H1,H2],'status':'descriptive rank-information audit; not SIBES, no actual biomass or plant risk','n_random_intertidal_events':len(q),'observed_quadrats':int(q.sum()),'taxa':out},pd.concat(tables,ignore_index=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('counts',type=Path);p.add_argument('sites',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r,t=run(a.counts,a.sites);a.out.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');t.to_csv(a.out.with_suffix('.csv'),index=False)
