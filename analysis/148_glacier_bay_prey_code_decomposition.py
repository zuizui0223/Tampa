#!/usr/bin/env python3
"""Response-open matched-site decomposition of prey retrieval rates by source prey code."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
HASH='d4b902fb8216844bb078cf9ba0e9a87f1767defc1781534245761a45c82cadfd'
KEY=['bout_id','dive_num']
def run(path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  manifest=json.loads(z.read('manifest.json'));src=next(s for s in manifest['sources'] if s['name']=='forage');f=next(f for f in src['files'] if f['source_name'].endswith('bouts_1993-2019.csv'));b=z.read(f['file']);assert hashlib.sha256(b).hexdigest()==f['sha256']
  cat=json.loads(z.read('forage_65fc57bdd34e64ff1548d3c3.json'));e=next(x for x in cat['files'] if x['name']==f['source_name']);assert hashlib.md5(b).hexdigest()==e['checksum']['value'].zfill(32)
 raw=pd.read_csv(io.BytesIO(b));d=raw.drop_duplicates().copy();dt=pd.to_datetime(d.bout_date);d['year']=dt.dt.year;d['month']=dt.dt.month
 d=d[d.site_name.notna()&~d.site_name.isin(['Dundas','Althorp','Inian','Lemesurier',''])&(d.otter_long < -135.6)&d.otter_lat.notna()].copy()
 d['size']=d.preysize_cd.fillna('').str.lower().str.strip();d['code']=d.preytype_cd.fillna('').str.lower().str.strip().replace('','UNRECORDED')
 d['valid_success']=d.success_cd.isin(['y','n']);d['qty_missing']=d.success_cd.eq('y')&(d.prey_qty.isna()|d.prey_qty.lt(1));d['qty_failed']=d.success_cd.eq('n')&d.prey_qty.notna()&d.prey_qty.ne(0);d['qty']=d.prey_qty.where(d.success_cd.eq('y'),0).fillna(0)
 a=d.groupby(KEY,sort=False).agg(site=('site_name','first'),year=('year','first'),month=('month','first'),sex=('sex_cd','first'),age=('ageclass_cd','first'),nsite=('site_name','nunique'),nyear=('year','nunique'),nmonth=('month','nunique'),nsex=('sex_cd','nunique'),nage=('ageclass_cd','nunique'),ndt=('dive_time','nunique'),nst=('surface_time','nunique'),nsuccess=('success_cd','nunique'),dt=('dive_time','first'),st=('surface_time','first'),valid=('valid_success','all'),missing=('qty_missing','any'),failed_qty=('qty_failed','any'),qty=('qty','sum'))
 good=a.valid&~a.missing&~a.failed_qty&a.nsite.eq(1)&a.nyear.eq(1)&a.nmonth.eq(1)&a.nsuccess.eq(1)&a.ndt.eq(1)&a.nst.eq(1)&a.dt.gt(0)&a.st.gt(0)
 p=a[good].copy();p['hours']=(p.dt+p.st)/3600;p['period']=np.select([p.year<=2007,p.year.between(2010,2011),p.year>=2018],['early','mid','late'],default='other');assert not p.period.eq('other').any();assert len(p)==17128
 d=d.join(p[['site','period','hours']],on=KEY,how='inner',validate='many_to_one');assert d.qty.sum()==p.qty.sum()
 codes=sorted(d.loc[d.qty>0,'code'].unique())
 def calc(label,min_bouts=5,summer=False,adult_female=False,strict=False):
  pp=p.copy()
  if summer:pp=pp[pp.month.between(6,8)]
  if adult_female:pp=pp[pp.sex.eq('f')&pp.age.eq('a')&pp.nsex.eq(1)&pp.nage.eq(1)]
  pp=pp[pp.period.isin(['early','late'])]
  bb=pp.reset_index().groupby(['site','period']).bout_id.nunique().unstack(fill_value=0);sites=sorted(bb.index[(bb.early>=min_bouts)&(bb.late>=min_bouts)])
  pp=pp[pp.site.isin(sites)];assert len(sites)>0
  rr=d.set_index(KEY).loc[d.set_index(KEY).index.isin(pp.index)].copy()
  rr['small']=rr.qty.where(rr['size'].str.startswith('1'),0)
  large=rr['size'].isin(['2a','2b','2c','3a','3b','3c','4z']) if strict else rr['size'].str[0].isin(['2','3','4'])
  rr['large']=rr.qty.where(large,0);rr['unknown']=rr.qty-rr.small-rr.large
  idx=pd.MultiIndex.from_product([sites,['early','late'],codes],names=['site','period','code']);cols=['qty','small','large','unknown']
  q=rr.groupby(['site','period','code'])[cols].sum().reindex(idx,fill_value=0);h=pp.groupby(['site','period']).hours.sum();rate=q.div(h.reindex(q.index.droplevel('code')).to_numpy(),axis=0)
  v={m:{t:rate[m].xs(t,level='period').unstack('code').reindex(index=sites,columns=codes).to_numpy() for t in ['early','late']} for m in cols}
  for t in ['early','late']:assert np.allclose(v['qty'][t],sum(v[m][t] for m in cols[1:]))
  rng=np.random.default_rng(20261124);n=len(sites);ids=rng.integers(n,size=(20000,n))
  means={m:{t:a.mean(0) for t,a in x.items()} for m,x in v.items()};bs={m:{t:a[ids].mean(1) for t,a in x.items()} for m,x in v.items()}
  def summary(e,l):
   delta=l-e;return {'early':float(e.mean()),'late':float(l.mean()),'delta':float(delta.mean()),'ci':np.quantile(delta[ids].mean(1),[.025,.975]).tolist(),'sites_increase':int((delta>1e-9).sum()),'sites_decrease':int((delta<-1e-9).sum())}
  def decomp(N0,N1,A0,A1):
   p0=np.divide(A0,N0,out=np.zeros_like(A0),where=N0>0);p1=np.divide(A1,N1,out=np.zeros_like(A1),where=N1>0);p0=np.where(N0>0,p0,p1);p1=np.where(N1>0,p1,p0);a=(N1-N0)*(p0+p1)/2;c=(p1-p0)*(N0+N1)/2;assert np.allclose(a+c,A1-A0);return a,c
  out={'label':label,'n_sites':n,'sites':sites,'n_dives':len(pp),'total':{m:summary(v[m]['early'].sum(1),v[m]['late'].sum(1)) for m in cols},'decomposition':{},'codes':{},'site_summary':[]}
  for m in ['small','large']:
   ab,fr=decomp(means['qty']['early'],means['qty']['late'],means[m]['early'],means[m]['late']);ab_b,fr_b=decomp(bs['qty']['early'],bs['qty']['late'],bs[m]['early'],bs[m]['late']);out['decomposition'][m]={'code_rate_component':float(ab.sum()),'within_code_size_fraction_component':float(fr.sum()),'rate_ci':np.quantile(ab_b.sum(1),[.025,.975]).tolist(),'fraction_ci':np.quantile(fr_b.sum(1),[.025,.975]).tolist()}
   for j,c in enumerate(codes):out['codes'].setdefault(c,{})[m+'_decomp']={'rate':float(ab[j]),'fraction':float(fr[j])}
  for j,c in enumerate(codes):
   for m in cols:out['codes'][c][m]=summary(v[m]['early'][:,j],v[m]['late'][:,j])
  for m in ['small','large']:
   delta=means[m]['late']-means[m]['early'];rank=np.argsort(-delta if m=='small' else delta);top=rank[:3];out['decomposition'][m]['top3_codes']=[codes[j] for j in top];out['decomposition'][m]['top3_delta']=float(delta[top].sum());out['decomposition'][m]['other_codes']=summary(v[m]['early'][:,[j for j in range(len(codes)) if j not in top]].sum(1),v[m]['late'][:,[j for j in range(len(codes)) if j not in top]].sum(1))
   dd=v[m]['late'].sum(1)-v[m]['early'].sum(1);out['decomposition'][m]['loo_site_delta_range']=[float(np.min((dd.sum()-dd)/(n-1))),float(np.max((dd.sum()-dd)/(n-1)))] if n>1 else None
  for i,s in enumerate(sites):out['site_summary'].append({'site':s,**{m:{t:float(v[m][t][i].sum()) for t in ['early','late']} for m in cols}})
  return out
 return {'status':'response-open observed retrieval counts; code labels not verified taxa or function','source_artifact_sha256':HASH,'source_csv_sha256':f['sha256'],'raw_rows':len(raw),'n_domain_complete_dives':len(p),'primary':calc('prior broad size classes'),'strict_size_sensitivity':calc('exclude ambiguous 2z/3z from large'),'adult_female_sensitivity':calc('adult female only',adult_female=True),'summer_sensitivity':calc('June-August only',summer=True),'min10_sensitivity':calc('>=10 bouts per site-period',min_bouts=10),'limits':['Source codes may be broad or unidentified, not taxonomic resolution. No verified forage taxonomy lookup yet.','Rate is retrieved items per recorded dive+surface hour, not ingestion, biomass or removal flux.','Aggregate matched-site rates and size fractions, not individual-level selection or causal prey depletion.','Post-hoc fixed-site bootstrap, no spatial or temporal dependence correction.','No direct connection with plant function or otter density.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2,allow_nan=False)+'\n')
