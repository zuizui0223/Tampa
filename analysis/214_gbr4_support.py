#!/usr/bin/env python3
"""Static structured-grid interpolation support; velocity pilot is one day only."""
import hashlib,io,json,zipfile,sys,re
from pathlib import Path
import numpy as np,pandas as pd,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from scipy.spatial import cKDTree
from pyproj import Transformer
from mpl_toolkits.basemap import Basemap
T='c17dcaa395b9dabc6ab5b61ce918e1abc68fe87b528a2bd12c0e01dd2a97920f'; C='5e4f81c353b9f9b39540d56464eaa671b036e376b6da4b708be2a15a3ab67885'
H={'tracking_dwca.zip':'60a07ef8d0b750d93ee2bee18785b215107aada65f0aab2b9015f1f5e90ecdab','tracking_obis.json':'8db45fd00463cc99c8c3f539d6d42f5b247c9a606e6b04491d202556a4012193','ts_meadows.geojson':'d8452b77714c7902fcbcc872e580af98b3e91b7f135c13b33676a9babcedca1b'}
def get(path,h):
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==h;return zipfile.ZipFile(io.BytesIO(b))
def main(track,pilot):
 z=get(track,T);raw={k:z.read(k) for k in H};assert all(hashlib.sha256(raw[k]).hexdigest()==v for k,v in H.items())
 a=pd.read_csv(zipfile.ZipFile(io.BytesIO(raw['tracking_dwca.zip'])).open('occurrence.txt'),sep='\t',low_memory=False);o=pd.DataFrame(json.loads(raw['tracking_obis.json'])['results']);a=a.merge(o[['occurrenceID','flags','decimalLatitude','decimalLongitude']],on='occurrenceID',validate='1:1',suffixes=('','_obis'));assert len(a)==6154 and np.allclose(a.decimalLatitude,a.decimalLatitude_obis) and np.allclose(a.decimalLongitude,a.decimalLongitude_obis)
 a['day']=pd.to_datetime(a.eventDate);assert a.eventTime.isna().all();a=a[~a['flags'].map(lambda x:'ON_LAND' in x)].drop_duplicates(['organismID','day','decimalLatitude','decimalLongitude']).reset_index(drop=True);assert len(a)==5884
 a['region']=np.where(a.decimalLatitude>-15,'Torres','Shoalwater');assert a.groupby('organismID').region.nunique().max()==1
 z=get(pilot,C);m=json.loads(z.read('manifest.json'));assert m['state']=='ACQUIRED'
 for r in m['files']:assert hashlib.sha256(z.read(r['file'])).hexdigest()==r['sha256']
 g=dict(np.load(io.BytesIO(z.read('gbr4_grid.npz')),allow_pickle=False));v=dict(np.load(io.BytesIO(z.read('gbr4_velocity_pilot.npz')),allow_pickle=False));x,y,b=g['lon'],g['lat'],g['botz'];finite=np.isfinite(x)&np.isfinite(y);wet=finite&np.isfinite(b)&(b>0)
 assert x.shape==(180,600) and np.array_equal(np.isfinite(v['u']),np.isfinite(v['v']));mask=np.isfinite(v['u'])&np.isfinite(v['v']);assert np.array_equal(mask.all(0),np.isfinite(v['botz'])) and np.array_equal(mask.any(0),mask.all(0))
 i,j=v['offset'];sl=(slice(i,i+v['lon'].shape[0]),slice(j,j+v['lon'].shape[1]));assert np.array_equal(x[sl],v['lon']) and np.array_equal(y[sl],v['lat']) and np.allclose(b[sl],v['botz'],equal_nan=True)
 # Use projected metre geometry and quads of neighboring *centers*, not actual cell edges.
 tf=Transformer.from_crs(4326,3577,always_xy=True).transform;X,Y=tf(x,y);ax,ay=tf(a.decimalLongitude.to_numpy(),a.decimalLatitude.to_numpy());P=shapely.points(ax,ay)
 qgood=finite[:-1,:-1]&finite[1:,:-1]&finite[1:,1:]&finite[:-1,1:];qwet=wet[:-1,:-1]&wet[1:,:-1]&wet[1:,1:]&wet[:-1,1:];ii,jj=np.where(qgood)
 corners=np.stack([np.column_stack([X[ii,jj],Y[ii,jj]]),np.column_stack([X[ii+1,jj],Y[ii+1,jj]]),np.column_stack([X[ii+1,jj+1],Y[ii+1,jj+1]]),np.column_stack([X[ii,jj+1],Y[ii,jj+1]])],axis=1)
 quads=shapely.polygons(corners);assert shapely.is_valid(quads).all() and (shapely.area(quads)>0).all()
 def covered(p,sel):
  tree=shapely.STRtree(p[sel]);idx,_=tree.query(P,predicate='covered_by');v=np.zeros(len(P),bool);v[idx]=True;return v
 a['inside_center_grid']=covered(quads,np.ones(len(quads),bool));a['strict_four_wet']=covered(quads,qwet[ii,jj]);assert (a.strict_four_wet<=a.inside_center_grid).all()
 # Nearest cell center amongst all finite coordinates, including dry, without snapping positions.
 tr=cKDTree(np.c_[X[finite],Y[finite]]);d,k=tr.query(np.c_[ax,ay]);a['nearest_dist_m']=d;a['nearest_wet_2p8km']=wet[finite][k]&(d<=2800)
 a['after_start']=a.day>=pd.Timestamp('2010-09-02') # conservatively covers arbitrary noon/midnight release after actual start 02 UTC Sep1
 a['pilot_valid_at_nearest']=False
 # Pilot verified for all wet centers in slab; strict quad support must lie within pilot region to be directly checked on pilot day.
 vp=np.zeros_like(wet);vp[sl]=mask.all(0);qpilot=vp[:-1,:-1]&vp[1:,:-1]&vp[1:,1:]&vp[:-1,1:];a['pilot_four']=covered(quads,qpilot[ii,jj]);a['pilot_valid_at_nearest']=vp[finite][k]&(d<=2800)
 # Replicate near-map paired denominator 212 on Torres only. GSHHS intermediate endpoint mask, not water trajectories.
 tf2=Transformer.from_crs(4326,32754,always_xy=True).transform;bb=Basemap(projection='cyl',llcrnrlon=138,llcrnrlat=-13,urcrnrlon=148,urcrnrlat=-7,resolution='i',area_thresh=0);land=shapely.union_all([transform(tf2,shapely.make_valid(Polygon(p.get_coords()))) for p in bb.landpolygons]);shapely.prepare(land)
 f=json.loads(raw['ts_meadows.geojson'])['features'];near=shapely.union_all([transform(tf2,shapely.make_valid(shape(f0['geometry']))) for f0 in f if any(2008<=int(y0)<=2012 for y0 in re.findall(r'\b(?:19|20)\d{2}\b',f0['properties']['SURVEY_DATE']))]);shapely.prepare(near)
 lon=a.decimalLongitude.to_numpy();lat=a.decimalLatitude.to_numpy();torres=a.region.eq('Torres').to_numpy();u0,v0=tf2(lon[torres],lat[torres]);water=np.zeros(len(a),bool);water[torres]=~shapely.intersects_xy(land,u0,v0);mapped=np.zeros(len(a),bool);mapped[torres]=shapely.intersects_xy(near,u0,v0);inside=(lon>=141)&(lon<=145)&(lat>=-11)&(lat<=-9)
 rows=[]
 for (sp,region,aid),h in a.groupby(['scientificName','region','organismID']):
  days=dict(tuple(h.groupby('day')));pairs=[]
  for date,g0 in days.items():
   g1=days.get(date+pd.Timedelta(days=7))
   if g1 is not None:pairs.append(pd.DataFrame(dict(si=np.repeat(g0.index,len(g1)),ei=np.tile(g1.index,len(g0)),w=1/(len(g0)*len(g1)))))
  if len(pairs)<5:continue
  p=pd.concat(pairs);p.w/=len(pairs)
  for panel in ['all_date_pairs']+(['near_meadow'] if region=='Torres' else []):
   r=p if panel=='all_date_pairs' else p[mapped[p.si]&water[p.si]&water[p.ei]&inside[p.ei]]
   if len(r)==0:continue
   w=r.w.to_numpy();w=w/w.sum();s=a.iloc[r.si]; fields=['inside_center_grid','strict_four_wet','nearest_wet_2p8km','after_start','pilot_four','pilot_valid_at_nearest']; q={k:float(w@s[k].to_numpy()) for k in fields};q.update({k+'_and_time':float(w@(s[k]&s.after_start).to_numpy()) for k in ['inside_center_grid','strict_four_wet','nearest_wet_2p8km','pilot_four','pilot_valid_at_nearest']});q['mapped_destination']=float(w@mapped[r.ei]) if region=='Torres' else None
   rows.append(dict(species=sp,region=region,animal=str(aid),panel=panel,origins=len(np.unique(r.si)),pairs=len(r),daypairs=len(pairs),**q))
 df=pd.DataFrame(rows);summary=[]
 for k,h in df.groupby(['species','region','panel']):
  row=dict(zip(['species','region','panel'],k));row['animals']=len(h);row['origins']=int(h.origins.sum());row['pairs']=int(h.pairs.sum());row.update({key:float(h[key].mean()) for key in h.columns[7:] if key!='mapped_destination'});summary.append(row)
 # Track fixes vs spatial support, independent of selection by a future date pair.
 track_summary=[]
 for k,h in a.groupby(['region','scientificName']):
  row=dict(region=k[0],species=k[1],fixes=len(h),animals=h.organismID.nunique(),strict_four_wet=int(h.strict_four_wet.sum()),nearest_wet=int(h.nearest_wet_2p8km.sum()));track_summary.append(row)
 return dict(archive=T,pilot=C,grid=dict(shape=list(x.shape),finite_centers=int(finite.sum()),wet_centers=int(wet.sum()),valid_quads=len(quads),four_wet_quads=int(qwet.sum()),depth_range=[float(np.nanmin(b)),float(np.nanmax(b))],pilot_hours=len(v['time']),pilot_wet_centers=int(mask.all(0).sum()),pilot_total_centers=int(mask.all(0).size),pilot_valid_fraction=float(mask.mean()),pilot_start=str(v['time'][0]),pilot_end=str(v['time'][-1]),pilot_depth=float(v['depth'])),track_summary=track_summary,summary=summary,individual=rows,limits=['Quads join adjacent model cell centers, not actual EMS cell polygons; strict interpolation support is conservative geometric diagnostic. Nearest finite center within 2.8 km, including dry centers, is a separate sensitivity, not snapping or filling.','Static seabed wet mask checked against all 24 pilot hours in northern subset only. No full date series or trajectory verified; no extrapolation of pilot currents. Time coverage only metadata start filter.','Torres near-map denominator replicates previous map/endpoint filter; Shoalwater all date pairs only, no meadow map yet; not comparable mapped origin populations. No ingestion, seed deposition or recruitment.'])
if __name__=='__main__':
 out=main(sys.argv[1],sys.argv[2]);Path(sys.argv[3]).write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda v:v.item())+'\n');print(json.dumps(dict(grid=out['grid'],summary=out['summary'],track_summary=out['track_summary']),indent=2))
