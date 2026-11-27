#!/usr/bin/env python3
"""Historic position-pair diagnostic; no observed seed ingestion or deposition."""
import hashlib, io, json, re, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer, Geod
ARCHIVE='c17dcaa395b9dabc6ab5b61ce918e1abc68fe87b528a2bd12c0e01dd2a97920f'
HASHES={'tracking_dwca.zip':'60a07ef8d0b750d93ee2bee18785b215107aada65f0aab2b9015f1f5e90ecdab','tracking_obis.json':'8db45fd00463cc99c8c3f539d6d42f5b247c9a606e6b04491d202556a4012193','ts_meadows.geojson':'d8452b77714c7902fcbcc872e580af98b3e91b7f135c13b33676a9babcedca1b'}
LAGS=[1,6,7,10,13]; THRESH=[1,5,10,25]; geod=Geod(ellps='WGS84')
def main(path):
    b=Path(path).read_bytes(); assert hashlib.sha256(b).hexdigest()==ARCHIVE
    z=zipfile.ZipFile(io.BytesIO(b)); raw={n:z.read(n) for n in HASHES};assert all(hashlib.sha256(raw[n]).hexdigest()==v for n,v in HASHES.items())
    a=pd.read_csv(zipfile.ZipFile(io.BytesIO(raw['tracking_dwca.zip'])).open('occurrence.txt'),sep='\t',low_memory=False)
    o=pd.DataFrame(json.loads(raw['tracking_obis.json'])['results']); assert len(a)==len(o)==6154 and a.occurrenceID.is_unique and o.occurrenceID.is_unique
    a=a.merge(o[['occurrenceID','flags','decimalLatitude','decimalLongitude']],on='occurrenceID',validate='1:1',suffixes=('','_obis')); assert len(a)==6154 and np.allclose(a.decimalLatitude,a.decimalLatitude_obis) and np.allclose(a.decimalLongitude,a.decimalLongitude_obis)
    assert a.eventTime.isna().all() and a.eventDate.str.len().eq(10).all() and a.coordinateUncertaintyInMeters.eq(300).all()
    a['landflag']=a['flags'].map(lambda x:'ON_LAND' in x);a['day']=pd.to_datetime(a.eventDate);a['region']=np.where(a.decimalLatitude>-15,'Torres Strait','Shoalwater Bay'); assert a.groupby('organismID').region.nunique().max()==1 and a.organismID.nunique()==21
    geo=json.loads(raw['ts_meadows.geojson']); assert len(geo['features'])==316 and geo['crs']['properties']['name'].endswith('4326')
    tf=Transformer.from_crs(4326,32754,always_xy=True).transform
    features=[(f['properties'],transform(tf,shapely.make_valid(shape(f['geometry'])))) for f in geo['features']]
    near=[g for p,g in features if any(2008<=int(y)<=2012 for y in re.findall(r'\b(?:19|20)\d{2}\b',p['SURVEY_DATE']))]
    allmap=shapely.union_all([g for p,g in features]); mainmap=shapely.union_all(near)
    maps={'near_2008_2012':mainmap,'near_erode300m':mainmap.buffer(-300),'near_buffer300m':mainmap.buffer(300),'all_dates':allmap}
    x,y=tf(a.decimalLongitude.to_numpy(),a.decimalLatitude.to_numpy()); pts=shapely.points(x,y)
    for k,g in maps.items(): a[k]=shapely.covers(g,pts)
    a['in_map_bbox']=a.decimalLongitude.between(141,145)&a.decimalLatitude.between(-11,-9)
    def calc(data):
        out=[]
        for (sp,region,aid),g in data.groupby(['scientificName','region','organismID']):
            days={d:h for d,h in g.groupby('day')}
            for lag in LAGS:
                dist=[]; per=[]
                for day,u in days.items():
                    v=days.get(day+pd.Timedelta(days=lag))
                    if v is None:continue
                    n,m=len(u),len(v);_,_,km=geod.inv(np.repeat(u.decimalLongitude.to_numpy(),m),np.repeat(u.decimalLatitude.to_numpy(),m),np.tile(v.decimalLongitude.to_numpy(),n),np.tile(v.decimalLatitude.to_numpy(),n));km=km/1000
                    dist.append(km);row={'distance_mean':float(km.mean()),'distance_max':float(km.max()),'distance_tail':[float((km>=k).mean()) for k in THRESH]}
                    if region=='Torres Strait':
                        row['maps']={}
                        for key in maps:
                            start=np.repeat(u[key].to_numpy(),m);end=np.tile(v[key].to_numpy(),n);inside=np.tile(v.in_map_bbox.to_numpy(),n)
                            row['maps'][key]={'start':start.mean(),'end':end.mean(),'both':(start&end).mean(),'start_bbox_end':(start&inside).mean(),'far':[float((start&(km>=k)).mean()) for k in THRESH],'far_both':[float((start&end&(km>=k)).mean()) for k in THRESH]}
                    per.append(row)
                if not per:continue
                w=np.concatenate([np.full(len(v),1/len(v)/len(per)) for v in dist]);v=np.concatenate(dist);i=np.argsort(v);cdf=np.cumsum(w[i]);q=lambda p:float(v[i[min(np.searchsorted(cdf,p),len(i)-1)]])
                row=dict(species=sp,region=region,animal=str(aid),lag=lag,daypairs=len(per),mean_km=float(np.mean([x['distance_mean'] for x in per])),median_km=q(.5),p90_km=q(.9),max_km=float(max(x['distance_max'] for x in per)),tail=np.mean([x['distance_tail'] for x in per],axis=0).tolist())
                if region=='Torres Strait':
                    row['maps']={}
                    for key in maps:
                        u=[x['maps'][key] for x in per];s=float(np.mean([x['start'] for x in u]));e=float(np.mean([x['end'] for x in u]));both=float(np.mean([x['both'] for x in u]));f=np.mean([x['far'] for x in u],axis=0);fb=np.mean([x['far_both'] for x in u],axis=0)
                        row['maps'][key]=dict(origin=s,dest=e,both=both,dest_given_origin=both/s if s else None,delta=both/s-e if s else None,bbox_end_given_origin=float(np.mean([x['start_bbox_end'] for x in u])/s) if s else None,far_given_origin=(f/s).tolist() if s else None,far_and_mapped_given_origin=(fb/s).tolist() if s else None,mapped_given_origin_and_far=[float(b/a) if a else None for a,b in zip(f,fb)])
                out.append(row)
        return out
    # De-duplicate identical animal/date/coordinate records; ON_LAND flag removed in primary (not OBIS dropped status).
    keys=['organismID','day','decimalLatitude','decimalLongitude']; clean=a[~a.landflag].drop_duplicates(keys); full=a.drop_duplicates(keys)
    primary=calc(clean); include=calc(full)
    def summarize(rows,minpairs=5):
        out=[]
        for (species,region,lag),g in pd.DataFrame(rows).query('daypairs>=@minpairs').groupby(['species','region','lag']):
            r={'species':species,'region':region,'lag':int(lag),'animals':len(g),'daypairs':int(g.daypairs.sum()),'mean_km':float(g.mean_km.mean()),'mean_animal_median_km':float(g.median_km.mean()),'mean_animal_p90_km':float(g.p90_km.mean()),'max_km':float(g.max_km.max()),'tail':np.mean(g['tail'].tolist(),axis=0).tolist()}
            if region=='Torres Strait':
                r['maps']={}
                for key in maps:
                    u=[x[key] for x in g['maps'] if x[key]['origin']>0]; avg=lambda k:float(np.mean([x[k] for x in u])) if u else None
                    r['maps'][key]={'animals_with_mapped_origin':len(u),'origin':avg('origin'),'dest':avg('dest'),'dest_given_origin':avg('dest_given_origin'),'delta':avg('delta'),'bbox_end_given_origin':avg('bbox_end_given_origin'),'far_given_origin':np.mean([x['far_given_origin'] for x in u],axis=0).tolist() if u else None,'far_and_mapped_given_origin':np.mean([x['far_and_mapped_given_origin'] for x in u],axis=0).tolist() if u else None,'mapped_given_origin_and_far':[float(np.mean(v)) if len(v:=[x['mapped_given_origin_and_far'][j] for x in u if x['mapped_given_origin_and_far'][j] is not None]) else None for j in range(len(THRESH))]}
            out.append(r)
        return out
    distance_contrasts=[]
    for species in ['Dugong dugon','Chelonia mydas']:
        for lag in [6,7,10,13]:
            for key in maps:
                rr=[r for r in primary if r['region']=='Torres Strait' and r['species']==species and r['lag']==lag and r['daypairs']>=5]
                for k,threshold in enumerate(THRESH):
                    vals=[]
                    for r in rr:
                        h=r['maps'][key]
                        if h['far_given_origin'] is None:continue
                        f0=h['far_given_origin'][k];b0=h['far_and_mapped_given_origin'][k];c0=h['dest_given_origin']
                        if 1e-12<f0<1-1e-12:
                            lo=b0/f0;sh=(c0-b0)/(1-f0)
                            vals.append({'animal':r['animal'],'far_endpoint_mapped':lo,'near_endpoint_mapped':sh,'difference':lo-sh})
                    if not vals:continue
                    dv=[v['difference'] for v in vals];loo=[float(np.mean(dv[:i]+dv[i+1:])) for i in range(len(dv))] if len(dv)>1 else []
                    distance_contrasts.append({'species':species,'lag':lag,'map':key,'threshold_km':threshold,'eligible_animals':len(vals),'far':float(np.mean([v['far_endpoint_mapped'] for v in vals])),'near':float(np.mean([v['near_endpoint_mapped'] for v in vals])),'difference':float(np.mean(dv)),'n_negative':int(sum(v< -1e-10 for v in dv)),'loo_difference_range':[min(loo),max(loo)] if loo else None,'individuals':vals})
    audit={'records':len(a),'flagged_land':int(a.landflag.sum()),'primary_unique':len(clean),'all_unique':len(full),'animals':int(a.organismID.nunique()),'region_species_counts':clean.groupby(['region','scientificName']).agg(fixes=('id','size'),animals=('organismID','nunique')).reset_index().to_dict('records'),'map_features_all':len(features),'map_features_near':len(near),'map_area_km2':{k:g.area/1e6 for k,g in maps.items()}}
    return {'archive':ARCHIVE,'source_hashes':HASHES,'audit':audit,'lags_days':LAGS,'thresholds_km':THRESH,'distance_contrasts':distance_contrasts,'primary_individual':primary,'all_flags_individual':include,'primary_min5':summarize(primary),'primary_min1':summarize(primary,1),'primary_min10':summarize(primary,10),'include_flags_min5':summarize(include),'limits':['Dates only; lag d days means unknown actual elapsed time near d +/-1 days; all start/end position combinations equally weighted per observed date pair, then equal animals. Not actual trajectories or gut passage, feeding or seed deposition. Daypairs dependent and fix sampling uneven.','2008-2012 maps are union of historical/composite polygons with at least one survey date in range; mapped footprint not actual contemporaneous suitable habitat or absence outside. All-date map and +/-300m boundary sensitivity. No species-specific seed or habitat success data.','Conditional mapped-origin diagnostic is hypothetical uniform within day observations; not an ingestion model. No causal interpretation of endpoint association or comparison to passive dispersal. Only small number of tracked animals and foraging-area tracks, no population inference.']}
if __name__=='__main__':
    out=main(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
