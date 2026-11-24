#!/usr/bin/env python3
"""Source-pinned SIBES linkage audit, not a recruitment-effect estimator."""
from pathlib import Path
import argparse,hashlib,io,json,zipfile
import numpy as np,pandas as pd
HASH='843038aefe1afaed39ded71f4d5e5890262a778300c1f0ab011245b7e61ead8a'
SITES={'Griend':(5.2949,53.2692),'Uithuizen':(6.6883,53.4663)}
# Grafnings et al. DOI 10.1111/rec.13851: trial sites; March planting 2018, July assessment;
# 2019 May assessment, exact day not provided. No fabricated event day.
RADII=[.5,1,2,5]
def run(path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
 with zipfile.ZipFile(path) as z:
  m=json.loads(z.read('manifest.json'));hs={r['file']:r['sha256'] for r in m[1]['files']}
  def read(n):
   b=z.read(n);assert hashlib.sha256(b).hexdigest()==hs[n];return pd.read_csv(io.BytesIO(b))
  s,b,sp=[read('official_'+x+'.csv') for x in ['samples','biota','species']]
 assert len(s)==59463 and not b.duplicated(['sample_id','sibes_id']).any() and sp.sibes_id.is_unique
 s=s[~s.sample_id.duplicated(False)].copy();s['date']=pd.to_datetime(s.date);s['year']=s.date.dt.year
 hid=sp.loc[sp.name.eq('Hediste diversicolor'),'sibes_id'].item();fid=sp.loc[sp.name.eq('Nereididae'),'sibes_id'].item();assert (hid,fid)==(11,15)
 s=s.merge(b[b.sibes_id.eq(hid)][['sample_id','abundance_m2','afdm_m2']],on='sample_id',how='left',validate='one_to_one')
 s['recorded_biota']=s.sample_id.isin(b.sample_id);s['family']=s.sample_id.isin(b[b.sibes_id.eq(fid)].sample_id)
 s['M']=1000*s.afdm_m2/s.abundance_m2
 rows=[];samples=[]
 for site,(lon,lat) in SITES.items():
  q=s.copy();p=np.deg2rad(q.y);p0=np.deg2rad(lat);dl=np.deg2rad(q.x-lon)
  q['km']=6371.0088*2*np.arcsin(np.sqrt(np.sin((p-p0)/2)**2+np.cos(p)*np.cos(p0)*np.sin(dl/2)**2));q['site']=site
  samples.append(q[q.km.le(5)].copy())
  for mode in ['grid','all']:
   z=q[q.sampling_type.eq('grid')] if mode=='grid' else q
   for y in range(2008,2023):
    yy=z[z.year.eq(y)]
    for radius in RADII:
     x=yy[yy.km.le(radius)];p=x[x.abundance_m2.gt(0)&x.afdm_m2.gt(0)];known=x[x.recorded_biota]
     rows.append(dict(site=site,year=y,radius_km=radius,sampling=mode,n_samples=len(x),n_stations=x.sampling_station_id.nunique(),n_with_biota=len(known),n_H_record=int(x.abundance_m2.notna().sum()),n_H_positive_complete=len(p),n_family=int(x.family.sum()),nearest_km=float(yy.km.min()) if len(yy) else None,first_date=x.date.min().strftime('%Y-%m-%d') if len(x) else None,last_date=x.date.max().strftime('%Y-%m-%d') if len(x) else None,identified_detection_fraction=x.abundance_m2.notna().sum()/len(known) if len(known) else None,B_mean=float(p.afdm_m2.mean()) if len(p) else None,B_median=float(p.afdm_m2.median()) if len(p) else None,M_median=float(p.M.median()) if len(p) else None,M_pooled=float(1000*p.afdm_m2.sum()/p.abundance_m2.sum()) if len(p) else None,N_mean=float(p.abundance_m2.mean()) if len(p) else None,all_biota_identified_B_mean=float(known.afdm_m2.fillna(0).mean()) if len(known) else None))
 d=pd.DataFrame(rows);samp=pd.concat(samples,ignore_index=True)
 x=d[(d.year.isin([2017,2018,2019]))&d.sampling.eq('grid')]
 out=x.pivot(index=['year','radius_km'],columns='site',values=['n_samples','n_H_positive_complete','B_mean','M_median','M_pooled','all_biota_identified_B_mean']).reset_index()
 contrasts=[]
 for _,r in out.iterrows():
  z={'year':int(r[('year','')]),'radius_km':float(r[('radius_km','')])}
  for v in ['B_mean','M_median','M_pooled','all_biota_identified_B_mean']:
   z[v+'_Uith_minus_Griend']=float(r[(v,'Uithuizen')]-r[(v,'Griend')])
  contrasts.append(z)
 return {'status':'coordinate/date linkage audit only; two restoration sites, no association model','archive_sha256':HASH,'source_hashes':hs,'coordinates':SITES,'plant_outcomes_published_2019':{'Griend_plants_per_m2':57,'Uithuizen_plants_per_m2':0,'assessment_month':'2019-05','source_doi':'10.1111/rec.13851'},'grid_2017_2019_contrasts':contrasts,'limits':['Survey coordinates are site centroids not planting plots. Radii were selected for sensitivity, not exposure radii.','Primary complete positive H. diversicolor rows; detection fraction conditional on biota records. Identified-species total per sampled biota record may use nondetection zero, not actual absence. Unresolved family-level individuals not assigned.','SIBES June–October; 2019 local July/August after May seedling observation. Prior summer not spring exposure.','Two sites cannot identify size effects; treatment design, hydrodynamics, restoration and habitat differ. No use of post-outcome measurements as predictors.']},d,samp
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r,d,s=run(a.artifact);a.out.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');d.to_csv(a.out.with_name('site_year_radius.csv'),index=False);s.to_csv(a.out.with_name('local_sample_records.csv'),index=False)
