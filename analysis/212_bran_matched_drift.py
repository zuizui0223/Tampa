#!/usr/bin/env python3
"""Matched dates/origins: daily-mean upper-ocean particle scenario, NOT seed fate."""
import sys,io,json,zipfile,hashlib,re
from pathlib import Path
import numpy as np,pandas as pd,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from pyproj import Transformer,Geod
from scipy.interpolate import RegularGridInterpolator
from mpl_toolkits.basemap import Basemap,basemap_datadir
T='c17dcaa395b9dabc6ab5b61ce918e1abc68fe87b528a2bd12c0e01dd2a97920f'
C='9f204beb344cc91e74cc03e91586f5ffdb166968caec9a14078f8fe9e4a2e355'
H={'tracking_dwca.zip':'60a07ef8d0b750d93ee2bee18785b215107aada65f0aab2b9015f1f5e90ecdab','tracking_obis.json':'8db45fd00463cc99c8c3f539d6d42f5b247c9a606e6b04491d202556a4012193','ts_meadows.geojson':'d8452b77714c7902fcbcc872e580af98b3e91b7f135c13b33676a9babcedca1b'}
G=Geod(ellps='WGS84');tf=Transformer.from_crs(4326,32754,always_xy=True).transform
GAPS=[0,300,600];LAGS=[6,7,13]
def readzip(path,h):
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==h;return zipfile.ZipFile(io.BytesIO(b))
def parts(g):return [g] if g.geom_type=='Polygon' else [p for x in getattr(g,'geoms',[]) for p in parts(x)]
def clusters(pp,gap):
 t=shapely.STRtree(pp);i,j=t.query(pp,predicate='dwithin',distance=gap+1e-8);p=np.arange(len(pp))
 def root(k):
  while p[k]!=k:p[k]=p[p[k]];k=p[k]
  return k
 for a,b in zip(i[i<j],j[i<j]):p[root(a)]=root(b)
 return np.unique([root(i) for i in range(len(pp))],return_inverse=True)[1]
def read(track,current):
 z=readzip(track,T);raw={k:z.read(k) for k in H};assert all(hashlib.sha256(raw[k]).hexdigest()==v for k,v in H.items())
 a=pd.read_csv(zipfile.ZipFile(io.BytesIO(raw['tracking_dwca.zip'])).open('occurrence.txt'),sep='\t',low_memory=False);o=pd.DataFrame(json.loads(raw['tracking_obis.json'])['results']);a=a.merge(o[['occurrenceID','flags','decimalLatitude','decimalLongitude']],on='occurrenceID',validate='1:1',suffixes=('','_obis'));assert len(a)==6154 and np.allclose(a.decimalLatitude,a.decimalLatitude_obis) and np.allclose(a.decimalLongitude,a.decimalLongitude_obis)
 assert a.eventTime.isna().all() and a.eventDate.str.len().eq(10).all() and a.coordinateUncertaintyInMeters.eq(300).all();a['day']=pd.to_datetime(a.eventDate);a=a[~a['flags'].map(lambda x:'ON_LAND' in x)].drop_duplicates(['organismID','day','decimalLatitude','decimalLongitude']);assert len(a)==5884;a=a[a.decimalLatitude>-15].reset_index(drop=True);assert len(a)==1875
 f=json.loads(raw['ts_meadows.geojson'])['features'];p=[(x['properties'],transform(tf,shapely.make_valid(shape(x['geometry'])))) for x in f];near=[g for a0,g in p if any(2008<=int(y)<=2012 for y in re.findall(r'\b(?:19|20)\d{2}\b',a0['SURVEY_DATE']))];assert len(f)==316 and len(near)==159
 maps={}
 for name,v in [('near',near),('all',[g for _,g in p])]:
  pp=parts(shapely.union_all(v));maps[name]=(shapely.STRtree(pp),{g:clusters(pp,g) for g in GAPS})
 z=readzip(current,C);m=json.loads(z.read('manifest.json'));assert len(m)==16 and all(r['state']=='ACQUIRED' for r in m);ds={}
 for mo in sorted(set(r['month'] for r in m)):
  uv=[]
  for c in ['u','v']:
   r=next(r for r in m if r['month']==mo and r['component']==c);b=z.read(r['file']);assert hashlib.sha256(b).hexdigest()==r['sha256'];q=np.load(io.BytesIO(b),allow_pickle=False);assert float(q['depth'])==2.5 and r['variables'][c]['units']=='m/sec';uv.append(dict(q))
  u,v=uv;assert all(np.array_equal(u[k],v[k]) for k in ['time','lat','lon']);assert np.array_equal(np.isfinite(u['values']),np.isfinite(v['values']));assert u['values'].shape[1:]==(51,81)
  for i,t in enumerate(pd.to_datetime(u['time'])):
   assert t.hour==12 and t.normalize() not in ds;ds[t.normalize()]=(u['lat'],u['lon'],np.stack((u['values'][i],v['values'][i]),axis=-1))
 assert len(ds)==243;return a,maps,ds,[{k:r[k] for k in ['month','component','sha256','shape','depth','start','end']} for r in m]
def locate(tree,x,y):
 # Bounding boxes then prepared polygon queries avoids enormous STRtree point query against complex union.
 xm,ym=tf(x,y);out=np.full(len(x),-1,dtype=int)
 for j,p in enumerate(tree.geometries):
  lo,bot,hi,top=p.bounds;idx=np.flatnonzero((xm>=lo)&(xm<=hi)&(ym>=bot)&(ym<=top));shapely.prepare(p)
  if len(idx):out[idx[shapely.intersects_xy(p,xm[idx],ym[idx])]]=j
 return out
def main(track,current):
 a,maps,ds,meta=read(track,current);b=Basemap(projection='cyl',llcrnrlon=138,llcrnrlat=-13,urcrnrlon=148,urcrnrlat=-7,resolution='i',area_thresh=0);land=shapely.union_all([transform(tf,shapely.make_valid(Polygon(p.get_coords()))) for p in b.landpolygons]);shapely.prepare(land)
 def is_land(x,y):return shapely.intersects_xy(land,*tf(x,y))
 def bbox(x,y):return (x>=141)&(x<=145)&(y>=-11)&(y<=-9)
 inter={(d,k):RegularGridInterpolator((lat,lon),v,method=k,bounds_error=False,fill_value=np.nan) for d,(lat,lon,v) in ds.items() for k in ['linear','nearest']}
 def simulate(s,lag,hour,step,mode):
  x=s.decimalLongitude.to_numpy().copy();y=s.decimalLatitude.to_numpy().copy();status=np.full(len(x),'complete',dtype='<U32');t0=s.day+pd.Timedelta(hours=hour);dt=step*3600;initial=np.zeros(len(s),bool);failure_hour=np.full(len(s),-1,dtype=int)
  for k in range(lag*24//step):
   days=(t0+pd.Timedelta(hours=k*step)).dt.normalize().to_numpy()
   for day in np.unique(days[status=='complete']):
    ix=np.flatnonzero((days==day)&(status=='complete'));f=inter.get((pd.Timestamp(day),mode))
    if f is None:status[ix]='missing_day';failure_hour[ix]=k*step;continue
    uv=f(np.c_[y[ix],x[ix]]);ok=np.isfinite(uv).all(1);
    if k==0:initial[ix]=ok
    status[ix[~ok]]='missing_velocity_start';failure_hour[ix[~ok]]=k*step;ix=ix[ok];uv=uv[ok]
    if not len(ix):continue
    mx,my,_=G.fwd(x[ix],y[ix],np.degrees(np.arctan2(uv[:,0],uv[:,1])),np.linalg.norm(uv,axis=1)*dt/2);ll=is_land(mx,my);status[ix[ll]]='land_midpoint';failure_hour[ix[ll]]=k*step;ix=ix[~ll];mx=mx[~ll];my=my[~ll]
    if not len(ix):continue
    uv=f(np.c_[my,mx]);ok=np.isfinite(uv).all(1);status[ix[~ok]]='missing_velocity_midpoint';failure_hour[ix[~ok]]=k*step;ix=ix[ok];uv=uv[ok]
    if not len(ix):continue
    ex,ey,_=G.fwd(x[ix],y[ix],np.degrees(np.arctan2(uv[:,0],uv[:,1])),np.linalg.norm(uv,axis=1)*dt);ll=is_land(ex,ey);status[ix[ll]]='land_endpoint';failure_hour[ix[ll]]=k*step;ix=ix[~ll];ex=ex[~ll];ey=ey[~ll]
    if not len(ix):continue
    # Check straight short-step segments against coarse land mask, not actual substep trajectory.
    line=shapely.linestrings(np.stack([np.column_stack(tf(x[ix],y[ix])),np.column_stack(tf(ex,ey))],axis=1));ll=shapely.intersects(land,line);status[ix[ll]]='land_segment';failure_hour[ix[ll]]=k*step;ix=ix[~ll];x[ix]=ex[~ll];y[ix]=ey[~ll]
  status[(status=='complete')&~bbox(x,y)]='outside_map_bbox';_,_,d=G.inv(s.decimalLongitude.to_numpy(),s.decimalLatitude.to_numpy(),x,y)
  return pd.DataFrame(dict(status=status,x=x,y=y,km=d/1000,initial=initial,failure_hour=failure_hour),index=s.index)
 x=a.decimalLongitude.to_numpy();y=a.decimalLatitude.to_numpy();water=~is_land(x,y);inside=bbox(x,y);pos={n:locate(t,x,y) for n,(t,_) in maps.items()};pairs=[]
 for (sp,aid),g in a.groupby(['scientificName','organismID']):
  days=dict(tuple(g.groupby('day')))
  for lag in LAGS:
   rr=[]
   for day,u in days.items():
    v=days.get(day+pd.Timedelta(days=lag))
    if v is not None:rr.append(pd.DataFrame(dict(si=np.repeat(u.index,len(v)),ei=np.tile(v.index,len(u)),w=1/(len(u)*len(v)))))
   if len(rr)<5:continue
   q=pd.concat(rr,ignore_index=True);q.w/=len(rr);q['species']=sp;q['animal']=str(aid);q['lag']=lag;q['daypairs']=len(rr);pairs.append(q)
 q=pd.concat(pairs,ignore_index=True);q=q[water[q.si]&water[q.ei]&inside[q.ei]&((pos['near'][q.si]>=0)|(pos['all'][q.si]>=0))].copy();_,_,d=G.inv(x[q.si],y[q.si],x[q.ei],y[q.ei]);q['animal_km']=d/1000
 # GBR4 catalog bounds only: necessary, not sufficient, for actual wet grid support.
 gbr=q[q.lag==7].copy();gbr=gbr.assign(in_gbr_bbox=(x[gbr.si]>=142.168788)&(x[gbr.si]<=156.8856378)&(y[gbr.si]>=-28.6960218)&(y[gbr.si]<=-7.0119082),in_gbr_time=(a.day.iloc[gbr.si].to_numpy()>=np.datetime64('2010-09-01')));gbr['both']=gbr.in_gbr_bbox&gbr.in_gbr_time;gbr=gbr.assign(mapped_near=pos['near'][gbr.si]>=0);gbr=gbr[gbr.mapped_near];gbr_diag=[]
 for sp,g in gbr.groupby('species'):
  u=g.drop_duplicates('si');w=g.groupby('animal').w.transform('sum');z=g.w/w;gbr_diag.append(dict(species=sp,animals=g.animal.nunique(),unique_origins=len(u),bbox_origins=int(u.in_gbr_bbox.sum()),time_origins=int(u.in_gbr_time.sum()),both_origins=int(u.both.sum()),both_weight=float((z*g.both).sum()/g.animal.nunique())))
 out=[];coverage=[]
 for lag in LAGS:
  pp=q[q.lag==lag];s=a.loc[sorted(pp.si.unique())];spec=[('linear_3h_noon',12,3,'linear')]
  if lag==7:spec += [('linear_1h_noon',12,1,'linear'),('linear_3h_midnight',0,3,'linear'),('nearest_3h_noon',12,3,'nearest')]
  for sc,h,st,mode in spec:
   sim=simulate(s,lag,h,st,mode);p=pp.join(sim,on='si',validate='m:1');print(lag,sc,len(s),sim.status.value_counts().to_dict(),flush=True);coverage.append(dict(lag=lag,scenario=sc,unique_origins=len(s),initial_velocity=int(sim.initial.sum()),physical_complete=int(sim.failure_hour.eq(-1).sum()),completed_24h=int((sim.failure_hour.eq(-1)|sim.failure_hour.ge(24)).sum()),completed_72h=int((sim.failure_hour.eq(-1)|sim.failure_hour.ge(72)).sum()),status=sim.status.value_counts().to_dict()))
   for name,(tree,groups) in maps.items():
    p0=p.assign(origin=pos[name][p.si],dest=pos[name][p.ei],passive=locate(tree,p.x.to_numpy(),p.y.to_numpy()));p0=p0[p0.origin>=0]
    for (sp,aid),g in p0.groupby(['species','animal']):
     w=g.w.to_numpy(copy=True);w/=w.sum();known=g.status.eq('complete').to_numpy();unk=float(w[~known].sum());am=g.dest.to_numpy()>=0;pm=g.passive.to_numpy()>=0;ori=g.origin.to_numpy();ae=g.dest.to_numpy();pe=g.passive.to_numpy();af=g.animal_km.to_numpy()>=10;pf=g.km.to_numpy()>=10
     avg=lambda v:float(np.dot(w,v));match=lambda v:float(np.dot(w[known],v[known])/w[known].sum()) if known.any() else None
     row=dict(lag=lag,scenario=sc,map=name,species=sp,animal=str(aid),n_origins=g.si.nunique(),n_pairs=len(g),known_weight=max(0,1-unk),unknown_weight=min(1,unk),initial_velocity_weight=avg(g.initial),physical_complete_weight=avg(g.failure_hour.eq(-1)),status_weight={k:avg(g.status.eq(k)) for k in sorted(g.status.unique())},animal_km=avg(g.animal_km),matched_animal_km=match(g.animal_km.to_numpy()),matched_passive_km=match(g.km.to_numpy()),metrics={})
     metrics=[('mapped',am,pm),('far10',af,pf),('far10_mapped',af&am,pf&pm)]+[(f'cross_gap{gap}',am&(groups[gap][ori]!=groups[gap][np.maximum(ae,0)]),pm&(groups[gap][ori]!=groups[gap][np.maximum(pe,0)])) for gap in GAPS]
     for k,av,pv in metrics:
      obs=avg(av);lo=avg(pv&known);hi=min(1,lo+unk);ma,mp=match(av),match(pv);row['metrics'][k]=dict(animal=obs,passive_lower=lo,passive_upper=hi,difference_lower=obs-hi,difference_upper=obs-lo,matched_animal=ma,matched_passive=mp,matched_difference=ma-mp if ma is not None else None)
     out.append(row)
 summary=[]
 for (lag,sc,mp,sp),a0 in pd.DataFrame(out).groupby(['lag','scenario','map','species']):
  rs=a0.to_dict('records');v=[r for r in rs if r['known_weight']>1e-12];row=dict(lag=int(lag),scenario=sc,map=mp,species=sp,animals=len(rs),complete_animals=len(v),known_weight=float(a0.known_weight.mean()),initial_velocity_weight=float(a0.initial_velocity_weight.mean()),physical_complete_weight=float(a0.physical_complete_weight.mean()),animal_km=float(a0.animal_km.mean()),matched_animal_km=float(np.mean([r['matched_animal_km'] for r in v])) if v else None,matched_passive_km=float(np.mean([r['matched_passive_km'] for r in v])) if v else None,metrics={})
  for k in rs[0]['metrics']:
   d=[r['metrics'][k] for r in rs];dv=[r['metrics'][k] for r in v];m={k:float(np.mean([r[k] for r in d])) for k in ['animal','passive_lower','passive_upper','difference_lower','difference_upper']};m.update({k:float(np.mean([r[k] for r in dv])) if dv else None for k in ['matched_animal','matched_passive','matched_difference']});m['robust_positive']=sum(r['difference_lower']>1e-10 for r in d);m['robust_negative']=sum(r['difference_upper']< -1e-10 for r in d);row['metrics'][k]=m
  summary.append(row)
 return dict(track_archive=T,current_archive=C,current_files=meta,coast_hashes={n:hashlib.sha256(Path(basemap_datadir,n).read_bytes()).hexdigest() for n in ['gshhs_i.dat','gshhsmeta_i.dat']},coverage=coverage,gbr4_catalog_bbox_time=gbr_diag,summary=summary,individual=out,limits=['2.5m daily-average current, piecewise constant by UTC date, RK2 midpoint geodesic. No tides, diffusion, settling, windage, ingestion or seeds. Date-only starts assumed UTC noon, midnight sensitivity.','Strict bilinear finite neighbors, nearest finite cell sensitivity without filling. Stop at missing velocity or coarse shoreline; outside map bbox unresolved. Unknown endpoints bounded, never presumed dead. Map overlap not suitability. Bounds conditional on model and mapped footprint, not statistical CI.','Complete-case subset selected by passive support. Animal movement paths unknown. Equal date pairs then animals; no independent pair inference.'])
if __name__=='__main__':
 out=main(sys.argv[1],sys.argv[2]);Path(sys.argv[3]).write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda x:x.item())+'\n')
