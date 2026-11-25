#!/usr/bin/env python3
"""Within-branch spathe rank, outcross subset diversity; no inferred cross-file ID mapping."""
import argparse, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
Z24='c0f4a1b0b988dc4a9f678f10cd8c413b8636585c554fd81591502b4af69d7d61'
Z25='2d0b308672fc68732d4fa30e5383e9ad48eb6236a8463ea4d3425ab81d7dd9a8'
F24={'Seed_Genotypes.xlsx':'394758533a8ef6d26c85c590bba398480f12231c2836294c6dd972c830867b48','Parent_Genotypes.xlsx':'ced25203e0b3bcbb3898c56fbab5eae25e9f0204f7694733415fbc0a17cc93de','by_spathe_dataset_slim.csv':'ce02d8e5404a270177a82bc29910542406b2bbf25e4839dbc19ca0bc07746a14'}
F25={'Seed_mass.csv':'460a7ec2e3388863a10d547b758d2f70e7199430d2f16ba564f9005c3a7ff06d','Seed_mass_-_reduced_dataset.csv':'3844e2767ccbbaf228e679063c9eb35e15fdb8c80ba6308abe2235ec09d6e79e','Seed_area.csv':'4349e7b4b482027b66d7e33ad018165d205600c28af94806a24a9bc67a1f25cb'}
KEY=['Site','Maternal ID','Rhipidium','Spathe'];COLS=[f'ZM{i} Allele{j}' for i in range(1,11) for j in (1,2)]
def source(path,sha,prefix,files):
 b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==sha
 with zipfile.ZipFile(io.BytesIO(b)) as z:d={f:z.read(prefix+'/'+f) for f in files}
 assert all(hashlib.sha256(d[f]).hexdigest()==h for f,h in files.items());return d

def rich_from_counts(n,c,k):
 assert n>=k and all(0<c0<=n for c0 in c)
 return sum(1-(math.comb(n-int(a),k)/math.comb(n,k) if n-int(a)>=k else 0) for a in c)
def sire_rich(v,k):return rich_from_counts(len(v),v['Paternal ID'].value_counts().to_numpy(),k)
def allele_rich(v,k):
 a=v[COLS].to_numpy().reshape(-1,10,2);assert np.isfinite(a).all()
 return float(np.mean([rich_from_counts(len(v),[int((a[:,l,:]==b).any(1).sum()) for b in np.unique(a[:,l,:])],k) for l in range(10)]))

def summarize(rows):
 if not rows:return {'pairs':0,'mothers':0}
 d=pd.DataFrame(rows);cols=[c for c in d if c not in KEY[:3]+['first','last','n0','n1','subset_n0','subset_n1']];m=d.groupby(KEY[:2])[cols].mean();a=m.to_numpy();rng=np.random.default_rng(20261125);draw=np.zeros((20000,len(cols)))
 for _,g in m.groupby(level=0):
  v=g.to_numpy();draw+=v[rng.integers(len(v),size=(len(draw),len(v)))].sum(1)
 draw/=len(m)
 return {'pairs':len(d),'mothers':len(m),'means':m.mean().to_dict(),'conditional_mother_bootstrap_95':dict(zip(cols,np.quantile(draw,[.025,.975],axis=0).T.tolist())),'signs':{c:{'negative':int((m[c]<-1e-10).sum()),'positive':int((m[c]>1e-10).sum()),'tie':int((abs(m[c])<=1e-10).sum())} for c in cols if c.endswith('_difference')},'site_means':{str(i):g.mean().to_dict() for i,g in m.groupby(level=0)},'leave_one_site_out_means':{str(i):m[m.index.get_level_values(0)!=i].mean().to_dict() for i in m.index.get_level_values(0).unique()},'records':rows}

def endpoint_pairs(x):
 for key,g in x.groupby(KEY[:3]):
  lo,hi=int(g.Spathe.min()),int(g.Spathe.max())
  if lo==hi:continue
  yield dict(zip(KEY[:3],map(int,key)),first=lo,last=hi),g[g.Spathe==lo],g[g.Spathe==hi]

def labels(x):
 assert not x.duplicated(KEY+['Seed']).any() and x['Paternal ID'].notna().all() and set(x.Selfed)=={'Outcrossed','Selfed'}
 pairs=list(endpoint_pairs(x));base=[];panels={}
 for r,a,b in pairs:
  p,q=[float((v.Selfed=='Outcrossed').mean()) for v in (a,b)];base.append(dict(**r,n0=len(a),n1=len(b),outcross_first=p,outcross_last=q,outcross_difference=q-p,no_outcross_first=float(p==0),no_outcross_last=float(q==0),no_outcross_difference=float(q==0)-float(p==0)))
 for k in (2,3):
  all_rows=[];matched=[]
  for r,a,b in pairs:
   if min(len(a),len(b))<k:continue
   v,w=[sire_rich(v,k) for v in (a,b)];row=dict(**r,n0=len(a),n1=len(b),all_first=v,all_last=w,all_difference=w-v);all_rows.append(row)
   c,d=[v[v.Selfed=='Outcrossed'] for v in (a,b)]
   if min(len(c),len(d))<k:continue
   u,z=[sire_rich(v,k) for v in (c,d)];matched.append(dict(**row,subset_n0=len(c),subset_n1=len(d),out_first=u,out_last=z,out_difference=z-u,out_minus_all_difference=(z-u)-(w-v),outcross_first=len(c)/len(a),outcross_last=len(d)/len(b),outcross_difference=len(d)/len(b)-len(c)/len(a)))
  panels[str(k)]={'all':summarize(all_rows),'same_pairs_outcross_only':summarize(matched)}
 return {'seeds':len(x),'mothers':x.groupby(KEY[:2]).ngroups,'spathes':x.groupby(KEY).ngroups,'selfed':int((x.Selfed=='Selfed').sum()),'mixed_site_sire_label_classes':int((x.groupby(['Site','Paternal ID']).Selfed.nunique()>1).sum()),'incidence':summarize(base),'panels':panels}

def genotype(s,p):
 p=p.iloc[:26].copy();assert p['Maternal ID'].str.fullmatch(r'Shoot\d+').all();p['Maternal ID']=p['Maternal ID'].str.replace('Shoot','',regex=False).astype(int);p.Site=p.Site.astype(int);assert not p.duplicated(KEY[:2]).any();p=p.set_index(KEY[:2]);assert set(p.index)==set(map(tuple,s[KEY[:2]].to_numpy()))
 assert len(s)==844 and s['Offspring Number'].nunique()==844 and not s.duplicated(KEY+['Offspring Number']).any()
 pairs=list(endpoint_pairs(s));base=s.dropna(subset=COLS).copy();assert len(base)==674;panels={}
 for threshold in (.925,.99,1.):
  flags=[]
  for _,r in base.iterrows():
   m=p.loc[(r.Site,r['Maternal ID'])];n=[]
   for l in range(1,11):
    pr=float(m['Prob' if l==1 else f'Prob.{l-1}']);a={m[f'ZM{l} Allele 1'],m[f'ZM{l} Allele 2']}
    if pr>=threshold and all(pd.notna(list(a))):n.append(sum(r[f'ZM{l} Allele{j}'] not in a for j in (1,2)))
   flags.append((1 in n and 2 not in n,2 in n))
  z=base.copy();z['nonself'],z['conflict']=np.array(flags).T;z=z.set_index('Offspring Number');out={}
  for k in (2,3):
   all_rows=[];matched=[]
   for r,a,b in pairs:
    a,b=[z.loc[z.index.intersection(v['Offspring Number'])] for v in (a,b)]
    if min(len(a),len(b))<k:continue
    v,w=[allele_rich(v,k) for v in (a,b)];row=dict(**r,n0=len(a),n1=len(b),all_first=v,all_last=w,all_difference=w-v);all_rows.append(row)
    c,d=[v[v.nonself] for v in (a,b)]
    if min(len(c),len(d))<k:continue
    u,t=[allele_rich(v,k) for v in (c,d)];matched.append(dict(**row,subset_n0=len(c),subset_n1=len(d),out_first=u,out_last=t,out_difference=t-u,out_minus_all_difference=(t-u)-(w-v)))
   out[str(k)]={'all':summarize(all_rows),'same_pairs_nonself_compatible_only':summarize(matched)}
  panels[str(threshold)]={'complete_seeds':len(z),'compatible_nonself':int(z.nonself.sum()),'conflict':int(z.conflict.sum()),'panels':out}
 return panels

def analyze(a,b):
 d=source(a,Z24,'zostera_paternity',F24);e=source(b,Z25,'seed_mass',F25);s=pd.read_excel(io.BytesIO(d['Seed_Genotypes.xlsx']));p=pd.read_excel(io.BytesIO(d['Parent_Genotypes.xlsx']),sheet_name='Original Data');t=pd.read_csv(io.BytesIO(d['by_spathe_dataset_slim.csv']));v={f:pd.read_csv(io.BytesIO(e[f]),dtype={'Paternal ID':str}) for f in F25}
 def common(a,b,k):return len(set(map(tuple,a[k].to_numpy()))&set(map(tuple,b[k].to_numpy())))
 joins={f:{'mother_key_overlap':common(s,x,KEY[:2]),'spathe_key_overlap':common(s,x,KEY),'nominal_seed_key_overlap':common(s.rename(columns={'Offspring Number':'Seed'}),x,KEY+['Seed'])} for f,x in v.items()}
 j=s.groupby(KEY).size().rename('n').reset_index().merge(t,on=KEY,validate='one_to_one');audit={'genotype_vs_slim_summary_mothers':common(s,t,KEY[:2]),'genotype_vs_slim_summary_spathes':len(j),'shared_spathes_with_matching_seed_counts':int((j.n==j['Genotyped Seeds']).sum()),'cross_archive':joins,'status':'NO_VERIFIED_CROSSWALK_DO_NOT_JOIN'}
 assert len(v['Seed_mass.csv'])==844 and len(v['Seed_mass_-_reduced_dataset.csv'])==693 and len(v['Seed_area.csv'])==873
 return {'status':'within_source_posthoc_conditional_outcross_diagnostic_not_direct_cross_archive_decomposition','source_dois':['10.5061/dryad.dfn2z358x','10.5061/dryad.6t1g1jx7p'],'archive_sha256':[Z24,Z25],'member_hashes':[F24,F25],'join_audit':audit,'2025_labels':{f:labels(x) for f,x in v.items()},'2024_genotype_nonself_proxy':genotype(s,p),'limits':['No validated crosswalk between individual seed IDs or maternal IDs in the two deposited sources; even 2024 slim per-spathe summary IDs differ from raw genotype table. Never assign individual paternity using row order, inferred relabeling or aggregate counts. Both papers same study region/research group and potentially overlapping original cohorts; no independent replication assumed.','First and last observed spathe rank within each rhipidium fixed before eligibility filtering within each deposited panel. Rank is proxy for timing, not measured dates. Restrict to available seed records, not all ovules or nonviable seeds.','2025 rarefied sire-label richness among k observed seeds; outcross status is deposited COLONY classification, not independent father identity. Reduced panel has two site-sire labels with mixed self/outcross status; do not relabel, keep row classifications and report discrepancy. All/conditional comparisons on same pairs, also report all eligible pairs. Selection on at least k outcrossed seeds in both groups limits generality.','2024 conditional nonself proxy requires at least one confident locus with exactly one nonmaternal allele and no confident locus with two nonmaternal alleles, among complete ten-locus seeds. Maternal genotypes reconstructed using same seeds; excludes ambiguous and conflicting seeds, not a direct outcross classification. Observed offspring allelic richness, not true sire count.','Bootstrap resamples maternal shoots within observed sites (20,000 draws); average within mother then equal mothers. Conditional descriptive uncertainty, not across-site generalization, confirmatory p-values or causal mediation. No decomposition attributing a fraction of loss to selfing because selected samples and distinct estimands.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive2024',type=Path);p.add_argument('archive2025',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.archive2024,a.archive2025),indent=2,sort_keys=True,allow_nan=False)+'\n')
