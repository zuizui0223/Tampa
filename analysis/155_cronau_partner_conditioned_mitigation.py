#!/usr/bin/env python3
"""Exploratory reanalysis of Cronau 2023. Aquaria, not individual ramets, are units.
No block ID provided in CSV; condition on observed treatment cells, no causal mediation.
"""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
SHA='05f7586f961ea26fe6685155eac93078ac62a8c0213dfa0222fceac02744ea33'
KEYS=['ragworm','nutrient','periwinkle']

def run(artifact):
 assert hashlib.sha256(artifact.read_bytes()).hexdigest()==SHA
 with zipfile.ZipFile(artifact) as z:
  manifest=json.loads(z.read('manifest.json')); dan=next(x for x in manifest if x['doi']=='10.17026/dans-x38-abzq')
  def read(fid):
   rec=next(x for x in dan['files'] if x['id']==fid); b=z.read(rec['file']);assert hashlib.sha256(b).hexdigest()==rec['sha256'];return pd.read_csv(io.BytesIO(b),sep=';',decimal=',')
  plant,glue,field,cage=map(read,[623,622,621,620])
 assert len(plant)==192 and plant.aq.nunique()==32 and len(glue)==1344 and not glue.duplicated(['aquarium','days','plantnr']).any()
 assert plant.groupby('aq')[KEYS].nunique().eq(1).all().all()
 assert glue.groupby('aquarium')[KEYS].nunique().eq(1).all().all()
 assert (plant.groupby('aq')[KEYS].first()==glue.groupby('aquarium')[KEYS].first().rename_axis('aq')).all().all()
 assert plant.groupby(KEYS).aq.nunique().eq(4).all()
 rng=np.random.default_rng(20261124); B=30000
 def factorial(d,cols):
  out={}
  for v in cols:
   cell={k:x[v].dropna().to_numpy() for k,x in d.groupby(KEYS)}
   assert len(cell)==8 and all(len(a)>=2 for a in cell.values())
   means={k:a.mean() for k,a in cell.items()}; draws={k:rng.choice(a,(B,len(a)),replace=True).mean(1) for k,a in cell.items()}
   def contrasts(c):
    x={}
    for n in ['no','yes']:
     d0=c['no',n,'yes']-c['no',n,'no'];d1=c['yes',n,'yes']-c['yes',n,'no']
     x[n+'_without_worm']=d0;x[n+'_with_worm']=d1;x[n+'_interaction']=d1-d0
    for s in ['without_worm','with_worm','interaction']:x['average_'+s]=(x['no_'+s]+x['yes_'+s])/2
    return x
   est=contrasts(means);bs=contrasts(draws)
   out[v]={'cell_means':{'|'.join(k):float(x) for k,x in means.items()},'cell_n':{'|'.join(k):len(a) for k,a in cell.items()},'contrasts':{k:{'estimate':float(x),'ci_conditional_aquarium_bootstrap':np.quantile(bs[k],[.025,.975]).tolist()} for k,x in est.items()}}
  return out
 plant_cols=['shoots','leaves','belowdw','abovedw','totaldw'];p=plant.groupby(['aq']+KEYS)[plant_cols].mean().reset_index()
 raw=factorial(p,plant_cols)
 bad_aqs=[int(i) for i,x in plant.groupby('aq') if sorted(x.plantnr)!=list(range(1,7))]
 variants={'exclude_18_19':factorial(p[~p.aq.isin(bad_aqs)],plant_cols)}
 dup=plant[plant.duplicated(['aq','plantnr'],False)]
 assert bad_aqs==[18,19] and len(dup)==2 and set(dup.aq)=={19}
 for i,idx in enumerate(dup.index):
  a=plant.copy();a.loc[idx,'aq']=18;assert a.groupby('aq').size().eq(6).all() and not a.duplicated(['aq','plantnr']).any()
  variants['hypothetical_move_duplicate_'+str(i)]=factorial(a.groupby(['aq']+KEYS)[plant_cols].mean().reset_index(),plant_cols)
 invalid=glue.gluedleaf.gt(glue.totalleaf);assert invalid.sum()==3
 glue['valid_glue_pct']=(100*glue.gluedleaf/glue.totalleaf).where(glue.totalleaf.gt(0)&~invalid)
 days=[27,40,49,54,61]
 use=glue[glue.days.isin(days)]
 a=use.groupby(['aquarium']+KEYS+['days'])[['valid_glue_pct','epicover','bites']].mean().reset_index()
 assert len(a)==160 and a[['valid_glue_pct','epicover','bites']].notna().all().all()
 late=a.groupby(['aquarium']+KEYS)[['valid_glue_pct','epicover','bites']].mean().reset_index()
 time={str(int(d)):factorial(x,['valid_glue_pct','epicover','bites']) for d,x in a.groupby('days')}
 assert len(field)==40 and not field.duplicated(['plot','moment']).any()
 assert len(cage)==40
 assert len(set(field[field.periwinkle.eq('No')]['plot'])&set(cage[cage.cage.eq('yes')]['plot']))==10
 wide=field.pivot(index=['location','plot','periwinkle'],columns='moment',values='pucount').reset_index()
 wide['change']=wide[2]-wide[1];wide['ratio_observed']=wide[2]/wide[1]
 fmeans={};fcontr={}
 for v in [1,2,'change','ratio_observed']:
  cell={k:x[v].to_numpy() for k,x in wide.groupby(['location','periwinkle'])};assert all(len(x)==5 for x in cell.values())
  means={k:x.mean() for k,x in cell.items()};bs={k:rng.choice(x,(B,len(x)),replace=True).mean(1) for k,x in cell.items()}
  ds=[means[k,'Yes']-means[k,'No'] for k in ['SJ','VP']]; bds=np.mean([bs[k,'Yes']-bs[k,'No'] for k in ['SJ','VP']],axis=0)
  fmeans[str(v)]={'|'.join(k):float(x) for k,x in means.items()};fcontr[str(v)]={'by_site':ds,'site_equal_difference':float(np.mean(ds)),'conditional_ci':np.quantile(bds,[.025,.975]).tolist()}
 return {'status':'response-open original data reanalysis; conditional bootstrap, no block-adjusted or mechanistic causal inference','artifact_sha256':SHA,'source_doi':'10.17026/dans-x38-abzq','audit':{'plant_rows':len(plant),'aquaria':32,'duplicate_plant_id_rows':dup[['aq','plantnr','shoots','leaves']].to_dict('records'),'mislabeled_aquaria':bad_aqs,'missing_biomass_rows':int(plant.totaldw.isna().sum()),'glue_rows':len(glue),'invalid_glue_rows':glue.loc[invalid,['aquarium','days','plantnr','totalleaf','gluedleaf']].to_dict('records'),'day14_no_denominator':bool(glue.loc[glue.days.eq(14),'totalleaf'].isna().all()),'field_shared_controls':10,'block_id_in_plant_csv':'block' in plant},'final_plant':raw,'final_sensitivities':variants,'late_damage_days':days,'late_damage':factorial(late,['valid_glue_pct','epicover','bites']),'damage_by_day':time,'field':{'means':fmeans,'contrasts':fcontr},'limitations':['Published randomized block design; released CSV lacks block labels. Unadjusted cell-stratified aquarium bootstrap, 2-4 aquaria/cell; no inference on block-level variability.','Two aquaria have conflicting ramet IDs; original labels are retained and sensitivity excludes or hypothetically reassigns one row; no actual identity inferred. One biomass value missing, not zero.','Damaged leaf counts and epiphyte estimates use observed ramets, not assigned-cohort survival; missing entries may depend on plant death. Bites are counts at visits, not cumulative attack rate. Invalid ratios excluded, day14 not used for gluing.','Field first visit is post-treatment, not pretreatment; change is descriptive. Planting units are stocks, can increase by growth, not individual survival. Two sites only; shared control plots counted once.','No reproductive measurements, no otter or pollination effect, no causal mediation or independent validation.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2,allow_nan=False)+'\n')
