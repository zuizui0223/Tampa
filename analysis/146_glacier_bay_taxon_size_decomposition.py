"""Species/size decomposition of matched observed benthic sites; no causal otter claim."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
HASH='d4b902fb8216844bb078cf9ba0e9a87f1767defc1781534245761a45c82cadfd'
KEY=['year','region','site_zone','site_name']
def run(path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  m=json.loads(z.read('manifest.json'));s=next(s for s in m['sources'] if s['name']=='benthos');f=next(f for f in s['files'] if 'sizeCount' in f['source_name']);b=z.read(f['file']);assert hashlib.sha256(b).hexdigest()==f['sha256'];raw=pd.read_csv(io.BytesIO(b))
  cat=json.loads(z.read('benthos_627d23b2d34e3bef0c9a1d3a.json'));entry=next(f for f in cat['files'] if 'sizeCount' in f['name']);assert hashlib.md5(b).hexdigest()==entry['checksum']['value'].zfill(32)
 assert raw[KEY+['quad']].notna().all().all()
 quadrats=raw[KEY+['quad']].drop_duplicates().groupby(KEY).size().rename('nq');assert quadrats.sum()==1828
 taxa=sorted(raw.loc[raw.species_type=='Clam','scientific_name'].unique())
 def calc(threshold=50,dedup=False):
  d=raw.drop_duplicates() if dedup else raw
  c=d[d.species_type.eq('Clam') & d['count'].gt(0)].copy();assert c['size'].gt(0).all()
  c['large']=c['count']*c['size'].ge(threshold)
  for k,m in [(1,'L'),(2,'L2'),(3,'L3')]:c[m]=c['count']*(c['size']/50)**k
  metrics=['count','large','L','L2','L3']
  a=c.groupby(KEY+['scientific_name'])[metrics].sum().unstack(fill_value=0).reindex(quadrats.index,fill_value=0)
  a=a.reindex(columns=pd.MultiIndex.from_product([metrics,taxa]),fill_value=0).div(quadrats,axis=0)
  a['period']=np.where(a.index.to_frame(index=False).year<=2007,'early','late')
  paired=a.groupby(['region','site_zone','site_name','period']).mean().unstack('period').dropna(how='any')
  out={};rng=np.random.default_rng(20261124)
  for zone in ['Intertidal','Subtidal']:
   x=paired.xs(zone,level='site_zone');n=len(x);assert n=={'Intertidal':44,'Subtidal':11}[zone]
   ids=rng.integers(n,size=(20000,n))
   def summ(e,l):
    diff=l-e
    return dict(early=float(e.mean()),late=float(l.mean()),delta=float(diff.mean()),ci=np.quantile(diff[ids].mean(axis=1),[.025,.975]).tolist(),ratio=float(l.mean()/e.mean()) if e.mean()>0 else None)
   def vec(m,t):return x[m].xs(t,axis=1,level='period').to_numpy()
   totals={};species={}
   for metric in metrics:
    e,l=vec(metric,'early'),vec(metric,'late');totals[metric]=summ(e.sum(axis=1),l.sum(axis=1))
    for j,t in enumerate(taxa):species.setdefault(t,{})[metric]=summ(e[:,j],l[:,j])
   def decomp(N0,N1,A0,A1):
    p0=np.divide(A0,N0,out=np.zeros_like(A0),where=N0>0);p1=np.divide(A1,N1,out=np.zeros_like(A1),where=N1>0)
    p0=np.where(N0>0,p0,p1);p1=np.where(N1>0,p1,p0)
    ab=(N1-N0)*(p0+p1)/2;fr=(p1-p0)*(N0+N1)/2
    assert np.allclose(ab+fr,A1-A0)
    return ab,fr
   ee,ll,aa,bb=[vec(m,t) for m,t in [('count','early'),('count','late'),('large','early'),('large','late')]]
   ab,fr=decomp(*[v.mean(0) for v in (ee,ll,aa,bb)])
   ab_b,fr_b=decomp(*[v[ids].mean(1) for v in (ee,ll,aa,bb)])
   dec={t:dict(abundance_component=float(ab[i]),size_fraction_component=float(fr[i]),delta=float(ab[i]+fr[i])) for i,t in enumerate(taxa)}
   sums=dict(abundance_component=float(ab.sum()),size_fraction_component=float(fr.sum()),delta=float((ab+fr).sum()))
   assert np.isclose(sums['delta'],totals['large']['delta'])
   for metric in ['large','L2']:
    e=x[metric].xs('early',axis=1,level='period');l=x[metric].xs('late',axis=1,level='period')
    totals[metric+'_excluding_Saxidomus']=summ(e.drop(columns='Saxidomus gigantea').sum(1).to_numpy(),l.drop(columns='Saxidomus gigantea').sum(1).to_numpy())
   d=ll-ee;h=d[:,taxa.index('Hiatella arctica')];l=d[:,taxa.index('Leukoma staminea')]
   co=dict(hiatella_increase=int((h>0).sum()),leukoma_decrease=int((l<0).sum()),both=int(((h>0)&(l<0)).sum()),spearman=float(spearmanr(h,l).statistic))
   out[zone]=dict(n_sites=n,totals=totals,species=species,decomposition=dec,decomposition_sum=sums,decomposition_bootstrap_ci={'abundance_component':np.quantile(ab_b.sum(1),[.025,.975]).tolist(),'size_fraction_component':np.quantile(fr_b.sum(1),[.025,.975]).tolist()},site_change_cooccurrence=co)
  return out
 return dict(status='response-open observed compact-quadrat reanalysis; no functional or causal inference',source_sha256=f['sha256'],artifact_sha256=HASH,primary=calc(),threshold40=calc(40),threshold60=calc(60),dedup50=calc(50,True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2)+'\n')
