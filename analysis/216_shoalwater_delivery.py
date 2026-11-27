#!/usr/bin/env python3
"""Independent-region historic geometric endpoint diagnostic (not current transport)."""
import hashlib,io,json,zipfile,sys,re
from pathlib import Path
import numpy as np,pandas as pd,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from pyproj import Transformer,Geod
from mpl_toolkits.basemap import Basemap
T='c17dcaa395b9dabc6ab5b61ce918e1abc68fe87b528a2bd12c0e01dd2a97920f';M='a1a705e26568fb73e8157466fe689f101acdd97e77de04a1ad8f2b2fc0f6a4db'
H={'tracking_dwca.zip':'60a07ef8d0b750d93ee2bee18785b215107aada65f0aab2b9015f1f5e90ecdab','tracking_obis.json':'8db45fd00463cc99c8c3f539d6d42f5b247c9a606e6b04491d202556a4012193'}
G=Geod(ellps='WGS84');tf=Transformer.from_crs(4326,32756,always_xy=True).transform

def zopen(path,h):
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==h;return zipfile.ZipFile(io.BytesIO(b))
def parts(p):return [p] if p.geom_type=='Polygon' else [x for g in getattr(p,'geoms',[]) for x in parts(g)]
def loc(pp,x,y):
 X,Y=tf(x,y);out=np.full(len(X),-1,dtype=np.int32)
 for j,p in enumerate(pp):
  l,b,r,t=p.bounds;k=np.flatnonzero((X>=l)&(X<=r)&(Y>=b)&(Y<=t));shapely.prepare(p)
  if len(k):out[k[shapely.intersects_xy(p,X[k],Y[k])]]=j
 return out

def main(track,meadows,step=10):
 z=zopen(track,T);r={k:z.read(k) for k in H};assert all(hashlib.sha256(r[k]).hexdigest()==v for k,v in H.items())
 a=pd.read_csv(zipfile.ZipFile(io.BytesIO(r['tracking_dwca.zip'])).open('occurrence.txt'),sep='\t',low_memory=False);o=pd.DataFrame(json.loads(r['tracking_obis.json'])['results']);a=a.merge(o[['occurrenceID','flags','decimalLatitude','decimalLongitude']],on='occurrenceID',validate='1:1',suffixes=('','_obis'));assert len(a)==6154 and np.allclose(a.decimalLatitude,a.decimalLatitude_obis) and np.allclose(a.decimalLongitude,a.decimalLongitude_obis)
 a['day']=pd.to_datetime(a.eventDate);a=a[~a['flags'].map(lambda x:'ON_LAND' in x)].drop_duplicates(['organismID','day','decimalLatitude','decimalLongitude']);assert len(a)==5884;a=a[a.decimalLatitude<-15].reset_index(drop=True);assert len(a)==4009
 z=zopen(meadows,M);b=z.read('shoalwater_meadows.geojson');assert hashlib.sha256(b).hexdigest()=='d0698578315c0bee949d02f29e8ac6512e25a766e0d059507bc7078524648bc8';fs=json.loads(b)['features'];assert len(fs)==389
 # Survey_Dat uses English month + 2-digit year, including a few missing separators; explicit ranges only.
 def years(s):
  return [2000+int(x) if int(x)<50 else 1900+int(x) for x in re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(\d{2})(?!\d)',str(s),re.I)]
 gs=[(years(f['properties']['Survey_Dat']),transform(tf,shapely.make_valid(shape(f['geometry'])))) for f in fs];assert sum(not y for y,g in gs)==1
 sets={'all':gs,'near2010_2014':[(y,g) for y,g in gs if any(2010<=k<=2014 for k in y)],'pre2012_only':[(y,g) for y,g in gs if y and max(y)<2012]}
 maps={};info={}
 for name,rows in sets.items():
  p=shapely.union_all([g for _,g in rows]);pp=parts(p);maps[name]=pp;info[name]=dict(features=len(rows),components=len(pp),area_km2=p.area/1e6,largest_area_fraction=max(g.area for g in pp)/p.area)
 for name,delta in [('all_eroded300',-300),('all_buffered300',300)]:
  p=shapely.union_all([g for _,g in gs]).buffer(delta);pp=parts(p);maps[name]=pp;info[name]=dict(features=len(gs),components=len(pp),area_km2=p.area/1e6,largest_area_fraction=max(g.area for g in pp)/p.area)
 bbox=lambda x,y:(x>=148.5)&(x<=152)&(y>=-24)&(y<=-20.5)
 bm=Basemap(projection='cyl',llcrnrlon=147,llcrnrlat=-25,urcrnrlon=154,urcrnrlat=-19,resolution='i',area_thresh=0);land=shapely.union_all([transform(tf,shapely.make_valid(Polygon(p.get_coords()))) for p in bm.landpolygons]);shapely.prepare(land)
 water=lambda x,y:~shapely.intersects_xy(land,*tf(x,y))
 x=a.decimalLongitude.to_numpy();y=a.decimalLatitude.to_numpy();a['water']=water(x,y);fix=[]
 for name,pp in maps.items():
  a[name]=loc(pp,x,y)
  for sp,d in a.groupby('scientificName'):fix.append(dict(map=name,species=sp,fixes=len(d),mapped=int((d[name]>=0).sum()),water=int(d.water.sum()),equal_animal_mapped=float(d.assign(m=d[name]>=0).groupby('organismID').m.mean().mean())))
 rows=[];audit=[];angles=np.arange(0,360,float(step));nb=len(angles)
 for (sp,aid),g in a.groupby(['scientificName','organismID']):
  days=dict(tuple(g.groupby('day')));rr=[]
  for day,u in days.items():
   v=days.get(day+pd.Timedelta(days=7))
   if v is not None:rr.append(pd.DataFrame(dict(si=np.repeat(u.index,len(v)),ei=np.tile(v.index,len(u)),w=1/(len(u)*len(v)))))
  if len(rr)<5:continue
  p=pd.concat(rr);w=p.w.to_numpy()/len(rr);si=p.si.to_numpy();ei=p.ei.to_numpy();assert np.isclose(w.sum(),1)
  _,_,d=G.inv(x[si],y[si],x[ei],y[ei]);ro,ra,_=G.fwd(np.repeat(x[si],nb),np.repeat(y[si],nb),np.tile(angles,len(si)),np.repeat(d,nb));okrot=(bbox(ro,ra)&water(ro,ra)).reshape(-1,nb);nrot=okrot.sum(1);okobs=bbox(x[ei],y[ei])&a.water.to_numpy()[si]&a.water.to_numpy()[ei];audit.append(dict(species=sp,daypairs=len(rr),fixpairs=len(si)))
  for name,pp in maps.items():
   pi=a[name].to_numpy()[si];pj=a[name].to_numpy()[ei];pr=loc(pp,ro,ra).reshape(-1,nb);em=pj>=0;rm=pr>=0;other=em&(pi!=pj);rot_other=rm&(pr!=pi[:,None]);ok=(pi>=0)&okobs&(nrot>0);nm=(rm&okrot).sum(1)/np.maximum(nrot,1);no=(rot_other&okrot).sum(1)/np.maximum(nrot,1)
   for cat,sel in [('all',np.ones(len(d),bool)),('near10',d<10000),('far10',d>=10000)]:
    use=ok&sel;ww=w[use];weight=ww.sum()
    if weight<=0:continue
    avg=lambda v:float(ww@v[use]/weight)
    rows.append(dict(map=name,species=sp,animal=str(aid),distance=cat,daypairs=len(rr),origin_weight=float(weight),mapped=avg(em),null_mapped=avg(nm),other=avg(other),null_other=avg(no),mean_km=avg(d/1000)))
 df=pd.DataFrame(rows);summ=[]
 for key,g in df.groupby(['map','species','distance']):
  a0=g.mapped-g.null_mapped; a1=g.other-g.null_other
  loo=lambda a:[float(min(v)),float(max(v))] if len(a)>1 and (v:=[float(a.drop(i).mean()) for i in a.index]) else None
  s=dict(zip(['map','species','distance'],key));s.update(animals=len(g),**{k:float(g[k].mean()) for k in ['origin_weight','mapped','null_mapped','other','null_other','mean_km']},excess_mapped=float(a0.mean()),excess_other=float(a1.mean()),mapped_loo=loo(a0),other_loo=loo(a1),n_positive_mapped=int((a0>1e-10).sum()),n_positive_other=int((a1>1e-10).sum()));summ.append(s)
 return dict(track=T,map_archive=M,bearing_step=step,unparsed_date_ids=[f['properties']['Unique_ID'] for f in fs if not years(f['properties']['Survey_Dat'])],map_info=info,fix=fix,audit=audit,summary=summ,individual=rows,limits=['Historical polygons with any recorded date within 2010-14 are not contemporaneous or surveyed absence; old map all dates is sensitivity, not true habitat.','Water endpoint mask and isotropic rotated bearings are geometry, not actual currents. Long-distance endpoints may be within same union polygon. Day-only tracking and multiple possible fix pairs; equal date-pair then animal weights; small groups; no statistical significance.','No ingestion, seed deposition, actual seed survival or animal superiority.'])
if __name__=='__main__':
 out=main(sys.argv[1],sys.argv[2],int(sys.argv[4]) if len(sys.argv)>4 else 10);Path(sys.argv[3]).write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda x:x.item())+'\n');print(json.dumps({k:out[k] for k in ['map_info','fix','summary']},indent=2))
