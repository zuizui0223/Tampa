#!/usr/bin/env python3
"""Distance- and origin-matched geometric null; NOT hydrodynamic dispersal."""
import hashlib,io,json,re,zipfile,sys
from pathlib import Path
import numpy as np,pandas as pd,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from pyproj import Transformer,Geod
from mpl_toolkits.basemap import Basemap,basemap_datadir
ARCHIVE='c17dcaa395b9dabc6ab5b61ce918e1abc68fe87b528a2bd12c0e01dd2a97920f'
H={'tracking_dwca.zip':'60a07ef8d0b750d93ee2bee18785b215107aada65f0aab2b9015f1f5e90ecdab','tracking_obis.json':'8db45fd00463cc99c8c3f539d6d42f5b247c9a606e6b04491d202556a4012193','ts_meadows.geojson':'d8452b77714c7902fcbcc872e580af98b3e91b7f135c13b33676a9babcedca1b'}
G=Geod(ellps='WGS84');tf=Transformer.from_crs(4326,32754,always_xy=True).transform

def read(path):
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==ARCHIVE
 z=zipfile.ZipFile(io.BytesIO(b));raw={k:z.read(k) for k in H};assert all(hashlib.sha256(raw[k]).hexdigest()==v for k,v in H.items())
 a=pd.read_csv(zipfile.ZipFile(io.BytesIO(raw['tracking_dwca.zip'])).open('occurrence.txt'),sep='\t',low_memory=False)
 o=pd.DataFrame(json.loads(raw['tracking_obis.json'])['results']);assert len(a)==len(o)==6154
 a=a.merge(o[['occurrenceID','flags','decimalLatitude','decimalLongitude']],on='occurrenceID',validate='1:1',suffixes=('','_obis'));assert np.allclose(a.decimalLatitude,a.decimalLatitude_obis) and np.allclose(a.decimalLongitude,a.decimalLongitude_obis)
 a['day']=pd.to_datetime(a.eventDate);assert a.eventTime.isna().all() and a.coordinateUncertaintyInMeters.eq(300).all()
 a=a[~a['flags'].map(lambda x:'ON_LAND' in x)].drop_duplicates(['organismID','day','decimalLatitude','decimalLongitude']);assert len(a)==5884
 a=a[a.decimalLatitude>-15].copy();fs=json.loads(raw['ts_meadows.geojson'])['features'];assert len(fs)==316
 polys=[(f['properties'],transform(tf,shapely.make_valid(shape(f['geometry'])))) for f in fs]
 near=[g for p,g in polys if any(2008<=int(y)<=2012 for y in re.findall(r'\b(?:19|20)\d{2}\b',p['SURVEY_DATE']))];assert len(near)==159
 m=shapely.union_all(near);maps={'near':m,'eroded300':m.buffer(-300),'buffered300':m.buffer(300),'all':shapely.union_all([g for p,g in polys])}
 return a,maps

def poly_parts(g):
 if g.geom_type=='Polygon':return [g]
 return [x for p in g.geoms for x in poly_parts(p)] if hasattr(g,'geoms') else []

def patch_index(p,pts):
 # Union components only: touching/overlapping polygons count as one component, never ID-defined meadows.
 parts=poly_parts(p); tree=shapely.STRtree(parts); i,j=tree.query(pts,predicate='covered_by'); out=np.full(len(pts),-1,dtype=int);out[i]=j
 return out,len(parts)

def main(path, bearing_step=10):
 a,maps=read(path)
 b=Basemap(projection='cyl',llcrnrlon=140,llcrnrlat=-12,urcrnrlon=146,urcrnrlat=-8,resolution='i',area_thresh=0)
 land=shapely.union_all([transform(tf,shapely.make_valid(Polygon(p.get_coords()))) for p in b.landpolygons]);shapely.prepare(land)
 # Exclude observed positions AND rotated endpoints that coincide with this coarse shoreline mask in a sensitivity analysis.
 hashes={n:hashlib.sha256(Path(basemap_datadir,n).read_bytes()).hexdigest() for n in ['gshhs_i.dat','gshhsmeta_i.dat']}
 bounds=lambda lon,lat:(lon>=141)&(lon<=145)&(lat>=-11)&(lat<=-9)
 point=lambda lon,lat:shapely.points(*tf(lon,lat))
 assert bearing_step in (5,10)
 angles=np.arange(0,360,float(bearing_step))
 results=[];audit=[];mapinfo={}
 for name,m in maps.items():
  parts=poly_parts(m); mapinfo[name]={'components':len(parts),'area_km2':m.area/1e6,'largest_component_fraction':max(p.area for p in parts)/m.area};shapely.prepare(m)
 for (species,animal),g in a.groupby(['scientificName','organismID']):
  days={k:v for k,v in g.groupby('day')}
  for lag in [6,7,10,13]:
   rr=[];count_day=0
   for day,u in days.items():
    v=days.get(day+pd.Timedelta(days=lag));
    if v is None:continue
    count_day+=1;n=len(u);k=len(v)
    x=np.repeat(u.decimalLongitude.to_numpy(),k);y=np.repeat(u.decimalLatitude.to_numpy(),k);xx=np.tile(v.decimalLongitude.to_numpy(),n);yy=np.tile(v.decimalLatitude.to_numpy(),n)
    _,_,d=G.inv(x,y,xx,yy);rr.append(pd.DataFrame({'lon':x,'lat':y,'end_lon':xx,'end_lat':yy,'d_m':d,'w':1/(n*k)}))
   if count_day<5:continue
   q=pd.concat(rr,ignore_index=True);q['w']/=count_day;assert abs(q.w.sum()-1)<1e-10
   lon=q.lon.to_numpy();lat=q.lat.to_numpy();el=q.end_lon.to_numpy();ea=q.end_lat.to_numpy();dist=q.d_m.to_numpy();w=q.w.to_numpy();orig=point(lon,lat);end=point(el,ea)
   # All fixed bearings, preserve WGS84 geodesic length exactly; restrict to map query bbox, and alternatively coastal-mask water endpoints.
   ro,ra,_=G.fwd(np.repeat(lon,len(angles)),np.repeat(lat,len(angles)),np.tile(angles,len(q)),np.repeat(dist,len(angles)))
   rx,ry=tf(ro,ra);inside=bounds(ro,ra).reshape(-1,len(angles));water=(~shapely.intersects_xy(land,rx,ry)).reshape(-1,len(angles));obs_in=bounds(el,ea);obs_water=~shapely.covers(land,end);orig_water=~shapely.covers(land,orig)
   for name,m in maps.items():
    pi,nparts=patch_index(m,orig);pj,_=patch_index(m,end);
    om=pi>=0;em=pj>=0;other=em&(pi!=pj);rot_m=shapely.intersects_xy(m,rx,ry).reshape(-1,len(angles));rot_same=np.zeros_like(rot_m);parts=poly_parts(m);rx2=rx.reshape(-1,len(angles));ry2=ry.reshape(-1,len(angles))
    for k in np.unique(pi[om]):
     sel=pi==k;part=parts[k];shapely.prepare(part);rot_same[sel]=shapely.intersects_xy(part,rx2[sel],ry2[sel])
    rot_other=rot_m&~rot_same
    for mask in ['bbox','water']:
     okrot=inside if mask=='bbox' else inside&water
     okobs=obs_in if mask=='bbox' else obs_in&obs_water&orig_water
     denom=okrot.sum(axis=1);valid=om&okobs&(denom>0);safe=np.maximum(denom,1)
     null=(rot_m&okrot).sum(axis=1)/safe;null_other=(rot_other&okrot).sum(axis=1)/safe
     for thresh,sel in [('all',np.ones(len(q),dtype=bool)),('near10',dist<10000),('far10',dist>=10000)]:
      base=om&sel;eligible=valid&sel;ww=w[eligible];total=ww.sum();base_w=w[base].sum()
      if total<=0:continue
      avg=lambda x:float(np.dot(x[eligible],ww)/total)
      results.append({'species':species,'animal':str(animal),'lag':lag,'daypairs':count_day,'map':name,'mask':mask,'distance_group':thresh,'eligible_weight':float(total),'origin_weight':float(base_w),'retained_fraction':float(total/base_w),'observed_mapped':avg(em),'null_mapped':avg(null),'excess_mapped':avg(em-null),'observed_other_component':avg(other),'null_other_component':avg(null_other),'excess_other_component':avg(other-null_other),'mean_distance_km':avg(dist/1000),'mean_valid_bearings':avg(denom)})
   print(species, str(animal), lag, count_day, len(q),flush=True);audit.append({'animal':str(animal),'species':species,'lag':lag,'daypairs':count_day,'pairs':len(q)})
 df=pd.DataFrame(results);summ=[]
 for k,g in df.groupby(['species','lag','map','mask','distance_group']):
  row=dict(zip(['species','lag','map','mask','distance_group'],k));row['animals']=len(g);row['positive_mapped']=int((g.excess_mapped>1e-10).sum());row['positive_other']=int((g.excess_other_component>1e-10).sum())
  for v in ['retained_fraction','observed_mapped','null_mapped','excess_mapped','observed_other_component','null_other_component','excess_other_component','mean_distance_km','mean_valid_bearings']:row[v]=float(g[v].mean())
  for col in ['excess_mapped','excess_other_component']:
   a0=g[col].to_numpy();l=[np.delete(a0,i).mean() for i in range(len(a0))] if len(a0)>1 else [];row[col+'_loo']=[float(min(l)),float(max(l))] if l else None
  summ.append(row)
 return {'archive':ARCHIVE,'source_hashes':H,'coast_source':'Basemap bundled GSHHS intermediate resolution (endpoint mask only; not navigability or water depth)','coast_hashes':hashes,'bearing_increment_deg':bearing_step,'maps':mapinfo,'audit':audit,'summary':summ,'individual':results,'limitations':['This is an isotropic geometric endpoint null matched on observed origin and displacement, not passive transport or a hydrodynamic model. Does not constrain trajectory across land. No observed seed carriage or settlement.','Map bbox is query extent, not complete surveyed coverage; alternative coastline mask is coarse, temporal mismatch and small islands remain. Different maps change conditioning populations.','Equal possible fix combinations per day pair, equal dates then animals; pair records dependent. Date-only; five-pair minimum. No confidence intervals or significance. Map union connected components not true populations or meadow identity.']}
if __name__=='__main__':
 out=main(sys.argv[1],int(sys.argv[3]) if len(sys.argv)>3 else 10);Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda x:x.item())+'\n')
