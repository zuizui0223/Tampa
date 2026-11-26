#!/usr/bin/env python3
"""Reanalyse exact Canadian public archive; cross-sectional stocks, not marked cohorts."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
ARCHIVE='8026c12f40414c2f34c01966b37d1946915c30dccef808a35e8b20a20081976b'
INNER='9993a811fa2ab88d8e31dd8484b746ac76a1eb81f6d36b68415e7358e5115564'
SITE='Site_Location'; DATE='Date'; SHOOT=[SITE,DATE,'Rshoot_ID']; BR=SHOOT+['Branch_ID']
BAYS={'Lower Three Fathom Harbour':'L3F',"Port l'Hebert":'PH',"Taylor's Head Shallow":'TH',"Taylor's Head Deep":'TH','Sambro Shallow':'Sambro','Sambro Deep':'Sambro'}
def rec(x):return json.loads(x.to_json(orient='records',date_format='iso'))
def rho(x,y):return float(spearmanr(x,y).statistic) if len(set(x))>1 and len(set(y))>1 else None
def main(path):
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==ARCHIVE
 c=zipfile.ZipFile(io.BytesIO(b)).read('canada_CSV.zip');assert hashlib.sha256(c).hexdigest()==INNER
 z=zipfile.ZipFile(io.BytesIO(c));read=lambda n:pd.read_csv(z.open('CSV/'+n+'.csv'),encoding='utf-8-sig')
 m=read('Reproductive Shoots Morphology');p=read('Peak Reproductive Metrics');r=read('Reproductive Metrics');d=read('Shoot Densities');s=read('Seed Biomass')
 assert (len(m),len(p),len(r),len(d),len(s))==(1330,80,6,549,337)
 assert not m.duplicated(BR).any() and not s.duplicated([SITE,DATE,'Core_ID']).any()
 for a in [m,d,s]:a[DATE]=pd.to_datetime(a[DATE],format='%d/%m/%Y')
 p['Peak_date']=pd.to_datetime(p.Peak_date,format='%d/%m/%Y');pk=p[[SITE,'Peak_date']].drop_duplicates();assert len(pk)==6
 assert m.groupby(SHOOT).Rshoot_Length_mm.nunique().max()<=1
 slots=[]
 for i in range(1,7):
  a=m[BR+['Nb_of_Spathes',f'S{i}_Dev',f'S{i}_Nb_of_Pistils',f'S{i}_Dev4_Nb_of_Pistils',f'S{i}_Dev4_Nb_of_Pistils_NF']].copy();a.columns=BR+['branch_n','dev','pistils','p4','nf4'];a['slot']=i;slots.append(a)
 t=pd.concat(slots,ignore_index=True);assert t.pistils.dropna().ge(0).all() and t.nf4.dropna().ge(0).all()
 assert not (t.nf4>t.p4).any() and not (t.p4.notna()&t.nf4.isna()).any()
 t['present']=t.dev.notna();t['outside']=t.present&t.branch_n.notna()&(t.slot>t.branch_n)
 peak_m=m.merge(pk,left_on=[SITE,DATE],right_on=[SITE,'Peak_date']);peak_t=t.merge(pk,left_on=[SITE,DATE],right_on=[SITE,'Peak_date']);assert peak_m.groupby(SITE).Rshoot_ID.nunique().eq(10).all()
 peak=[]; per_shoot=[]
 for site,a in peak_m.groupby(SITE):
  q=peak_t[peak_t[SITE]==site];a0=r[r[SITE]==site].iloc[0];n=a.Rshoot_ID.nunique();nb=a.Nb_of_Spathes.sum();assert a.Nb_of_Spathes.notna().all()
  obs=q[q.present&q.pistils.notna()];assert len(obs)>0
  length=a.groupby('Rshoot_ID').Rshoot_Length_mm.first()
  st=q[q.dev.str.startswith('4',na=False)];v=st[st.p4.notna()&st.nf4.notna()];stage4_frac=1-v.nf4.sum()/v.p4.sum()
  out={SITE:site,'peak':str(a[DATE].iloc[0].date()),'shoots':n,'branches_per_shoot':len(a)/n,'reported_spathes_per_shoot':nb/n,'stage_records':int(q.present.sum()),'pistil_records':len(obs),'pistil_count_per_shoot':obs.pistils.sum()/n,'pistil_per_counted_spathe':obs.pistils.mean(),'length_mean':length.mean(),'length_n':int(length.notna().sum()),'paper_pistils_per_shoot':a0.Peak_nb_pistils,'published_summary_length':a0.Max_Reproshoot_length,'published_fertilization':a0.Mean_fertilization/100,'stage4_pistil_weighted_fert_fraction':stage4_frac,'stage4_records':len(st),'stage4_complete':len(v),'p4_total':v.p4.sum(),'nf4_total':v.nf4.sum(),'reported_density':a0.Peak_Repro_density,'peak_table_density':p.loc[p[SITE]==site,'Repro_density_peak'].mean()}
  out['observed_count_per_record']=len(obs)/int(q.present.sum());out['observed_spathes_per_shoot']=int(q.present.sum())/n
  assert np.isclose(out['observed_spathes_per_shoot']*out['observed_count_per_record']*out['pistil_per_counted_spathe'],out['pistil_count_per_shoot'])
  a1=d[(d[SITE]==site)&(d[DATE].dt.year==2018)].groupby(DATE).Density_Repro_shoots.mean();out['max_raw_density_2018']=a1.max();out['max_raw_dates']=[str(x.date()) for x in a1.index[a1==a1.max()]];peak.append(out)
  for sh,g in q.groupby('Rshoot_ID'):
   per_shoot.append({SITE:site,'shoot':int(sh),'stage_records':int(g.present.sum()),'pistil_records':int((g.present&g.pistils.notna()).sum()),'observed_pistils':float(g.loc[g.present,'pistils'].sum()),'length':float(length.loc[sh]) if pd.notna(length.loc[sh]) else None})
 v=t[(t.dev=='4b')&t.p4.notna()&t.nf4.notna()].copy();assert len(v)==723
 v['F']=v.p4-v.nf4
 shoot4=v.groupby(SHOOT).agg(n=('p4','size'),P=('p4','sum'),F=('F','sum')).reset_index();shoot4['P_per_spathe']=shoot4.P/shoot4.n;shoot4['F_per_P']=shoot4.F/shoot4.P.replace(0,np.nan)
 stages=[]
 for dev,q in t[t.dev.str.startswith('4',na=False)].groupby('dev'):
  v0=q[q.p4.notna()&q.nf4.notna()];stages.append({'dev':dev,'n_records':len(q),'n_complete':len(v0),'pistils':float(v0.p4.sum()),'nonfert':float(v0.nf4.sum()),'fraction_recorded_fert':float(1-v0.nf4.sum()/v0.p4.sum())})
 same_stage=[]
 for site,a in v.groupby(SITE):
  g=shoot4[shoot4[SITE]==site];same_stage.append({SITE:site,'n_spathes':len(a),'n_shoots':len(g),'n_dates':g[DATE].nunique(),'pistil_per_spathe':a.p4.mean(),'fert_fraction':a.F.sum()/a.p4.sum(),'fert_pistils_per_spathe':a.F.mean(),'equal_shoot_pistil_per_spathe':g.P_per_spathe.mean()})
 assert not (s.Seeds_assessed>s.Full_seeds).any() and not (s.Viable_seeds>s.Seeds_assessed).any()
 winter=s[(s[DATE].dt.year==2018)&(s[DATE].dt.month>=11)];spring=s[s[DATE].dt.year==2019];assert len(winter)==39
 season=[]
 for site in r[SITE]:
  for period,g in [('winter',winter[winter[SITE]==site]),('first_2019',spring[(spring[SITE]==site)&(spring[DATE]==spring.loc[spring[SITE]==site,DATE].min())])]:
   assert len(g)>0 and g.Full_seeds.notna().all() and g.Seeds_assessed.notna().all() and g.Viable_seeds.notna().all()
   positive=g.Full_seeds>0;ass=g.Seeds_assessed.sum();full=g.Full_seeds.sum();vi=g.Viable_seeds.sum();vv=g[g.Viable_seeds>0];weight=vv[vv.Mean_weight_viable_seed_mg.notna()];valid_mass=float((weight.Viable_seeds*weight.Mean_weight_viable_seed_mg).sum())
   season.append({SITE:site,'period':period,'date':str(g[DATE].iloc[0].date()),'cores':len(g),'full':full,'assessed':ass,'viable':vi,'positive_cores':int(positive.sum()),'viability_assessed':vi/ass if ass else None,'full_per_core':full/len(g),'confirmed_viable_per_core':vi/len(g),'possible_viable_upper_per_core':(vi+full-ass)/len(g),'viable_mass_weighted_mean_mg':valid_mass/weight.Viable_seeds.sum() if len(weight) else None,'viable_mass_seed_count_coverage':float(weight.Viable_seeds.sum()/vi) if vi else None,'weight_types':sorted(g.Weight_type.unique().tolist()),'germinated':int(g.Germinated_seeds.sum()),'seedlings':int(g.Seedlings.sum())})
 c=s.dropna(subset=['Full_seeds','AG_biomass_g','BG_biomass_g']).copy();c['bay']=c[SITE].map(BAYS);c['AG']=np.log1p(c.AG_biomass_g);c['BG']=np.log1p(c.BG_biomass_g);c['total']=np.log1p(c.AG_biomass_g+c.BG_biomass_g);c['y']=np.log1p(c.Full_seeds)
 def test(c,field,features,lam):
  keys=[SITE,DATE]; c=c.copy();cols=features+[field];c[cols]=c[cols]-c.groupby(keys)[cols].transform('mean');pred=[];coef=[]
  for bay in sorted(c.bay.unique()):
   tr=c[c.bay!=bay];te=c[c.bay==bay].copy();X=tr[features].to_numpy();S=np.sqrt(np.mean(X**2,axis=0));S[S==0]=1;X=X/S
   w=np.linalg.solve(X.T@X+lam*np.eye(len(features)),X.T@tr[field].to_numpy())/S if features else np.array([])
   te['pred']=te[features].to_numpy()@w if features else 0.;pred.append(te);coef.append({'bay':bay,'slopes':w.tolist()})
  a=pd.concat(pred);pairs=[]
  for (site,day),g in a.groupby(keys):
   x=g[field].to_numpy();y=g.pred.to_numpy();i,j=np.triu_indices(len(x),1);pairs.extend({'site':site,'date':str(day.date()),'obs':float(o),'pred':float(p),'se':float((o-p)**2)} for o,p in zip(x[i]-x[j],y[i]-y[j]))
  p=pd.DataFrame(pairs); site=p.groupby('site').se.mean();by_date=p.groupby(['site','date']).se.mean().groupby('site').mean();o=p.obs.abs()>1e-12;v=p.pred.abs()>1e-12
  return {'n_cores':len(c),'n_groups':c.groupby(keys).ngroups,'n_pairs':len(p),'mse':p.se.mean(),'equal_site_mse':site.mean(),'equal_site_date_mse':by_date.mean(),'by_site':site.to_dict(),'concordant':int((o&v&(p.obs*p.pred>0)).sum()),'discordant':int((o&v&(p.obs*p.pred<0)).sum()),'predicted_ties':int((o&~v).sum()),'observed_ties':int((~o).sum()),'coefficients':coef}
 cv={};models={'null':[],'AG':['AG'],'BG':['BG'],'AG_BG':['AG','BG'],'total':['total']}
 for label,rr,field in [('all_full',c,'y'),('winter_spring_full',c[(c[DATE].dt.year==2019)|(c[DATE].dt.month>=11)],'y'),('exclude_largest_core',c[c.Full_seeds<c.Full_seeds.max()],'y'),('confirmed_viable',c[c.Viable_seeds.notna()],'yvi')]:
  rr=rr.copy();rr['yvi']=np.log1p(rr.Viable_seeds)
  cv[label]={k:{str(l):test(rr,field,f,l) for l in [.1,1,10]} for k,f in models.items()}
 return {'source_archive':ARCHIVE,'canada_CSV':INNER,'audit':{'branch_rows':len(m),'shoot_keys':m.groupby(SHOOT).ngroups,'site_dates':m.groupby([SITE,DATE]).ngroups,'stage_records':int(t.present.sum()),'outside_reported_branch_count':int(t.outside.sum()),'missing_branch_spathe_count':int(m.Nb_of_Spathes.isna().sum()),'peak_shoots':60,'seed_cores':len(s),'complete_biomass_count':len(c),'winter_cores':len(winter)},'peak':peak,'peak_shoots':per_shoot,'stage4_substage':stages,'same_stage_4b':same_stage,'seed_stock':season,'local_cv':cv,'limits':['Raw count of recorded pistils is not ultimate seed production; absent and uncounted pistils not imputed, developmental stage affects completeness. Published peak date preserved, different aggregation and source mismatch recorded.','Seed cores are destructive cross-sectional samples; no cohort, capture or mortality rates. Viability uses assessed denominator, not germination. Measured wet and dry mass separate.','Within-date/bay holdout uses measured biomass at same visit as outcome; relative comparison only, not prospective forecast or causal trapping effect. Four bays, six sites, dependent pair scores; no inference from pair-level sample size.']}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('archive');ap.add_argument('output');a=ap.parse_args();out=main(a.archive);Path(a.output).write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda x:x.item())+'\n')
