#!/usr/bin/env python3
"""Nearby survey-point support at observed and rotated endpoints; not seed fate."""
import hashlib,io,json,sys,zipfile
from pathlib import Path
import numpy as np,pandas as pd,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from scipy.spatial import cKDTree
from pyproj import Transformer,Geod
from mpl_toolkits.basemap import Basemap
H=['c17dcaa395b9dabc6ab5b61ce918e1abc68fe87b528a2bd12c0e01dd2a97920f','a1a705e26568fb73e8157466fe689f101acdd97e77de04a1ad8f2b2fc0f6a4db','31d4831e2efa3552e58db32a70fefccf6dcad5049e2bed4f2ca09d984b547e06']
I={'tracking_dwca.zip':'60a07ef8d0b750d93ee2bee18785b215107aada65f0aab2b9015f1f5e90ecdab','tracking_obis.json':'8db45fd00463cc99c8c3f539d6d42f5b247c9a606e6b04491d202556a4012193','ts_meadows.geojson':'d8452b77714c7902fcbcc872e580af98b3e91b7f135c13b33676a9babcedca1b','shoalwater_meadows.geojson':'d0698578315c0bee949d02f29e8ac6512e25a766e0d059507bc7078524648bc8','torres_survey_points.geojson':'9727c28d4dafcd225a754f2439e010fe09f2835dfbeefe03b28cc5d8f940facf','shoalwater_survey_points.geojson':'6a57c41ad14db93d64293214ca51fc76db3326eab38141c8c61f504ed58df552'}
G=Geod(ellps='WGS84'); WINDOWS=[0,1,3,99]; RADII=[300,1000,2000]; ANGLES=np.arange(0,360,10.)
def load(path,h):
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==h;return zipfile.ZipFile(io.BytesIO(b))
def read(z,k):
 b=z.read(k);assert hashlib.sha256(b).hexdigest()==I[k];return b
def parts(g):return [g] if g.geom_type=='Polygon' else [p for x in getattr(g,'geoms',[]) for p in parts(x)]
def inside(pp,x,y):
 v=np.zeros(len(x),bool)
 for p in pp:
  l,b,r,t=p.bounds;j=np.flatnonzero((x>=l)&(x<=r)&(y>=b)&(y<=t));shapely.prepare(p)
  if len(j):v[j]|=shapely.intersects_xy(p,x[j],y[j])
 return v
def main(*paths):
 z,m,s=[load(p,h) for p,h in zip(paths,H)];a=pd.read_csv(zipfile.ZipFile(io.BytesIO(read(z,'tracking_dwca.zip'))).open('occurrence.txt'),sep='\t',low_memory=False);o=pd.DataFrame(json.loads(read(z,'tracking_obis.json'))['results']);a=a.merge(o[['occurrenceID','flags','decimalLatitude','decimalLongitude']],on='occurrenceID',validate='1:1',suffixes=('','_obis'));assert len(a)==6154 and np.allclose(a.decimalLatitude,a.decimalLatitude_obis) and np.allclose(a.decimalLongitude,a.decimalLongitude_obis)
 a['day']=pd.to_datetime(a.eventDate);assert a.eventTime.isna().all();a=a[~a['flags'].map(lambda x:'ON_LAND' in x)].drop_duplicates(['organismID','day','decimalLatitude','decimalLongitude']);assert len(a)==5884
 out=dict(archives=H,inner=I,audit={},point_vs_map=[],fix_support=[],individual=[],summary=[])
 for region in ['torres','shoalwater']:
  t=a[a.decimalLatitude.gt(-15) if region=='torres' else a.decimalLatitude.lt(-15)].reset_index(drop=True);assert len(t)==(1875 if region=='torres' else 4009)
  tf=Transformer.from_crs(4326,32754 if region=='torres' else 32756,always_xy=True).transform;box=(141,-11,145,-9) if region=='torres' else (148.5,-24,152,-20.5)
  fs=json.loads(read(z,'ts_meadows.geojson') if region=='torres' else read(m,'shoalwater_meadows.geojson'))['features'];pp=parts(shapely.union_all([transform(tf,shapely.make_valid(shape(f['geometry']))) for f in fs]))
  bm=Basemap(projection='cyl',llcrnrlon=box[0]-1,llcrnrlat=box[1]-1,urcrnrlon=box[2]+1,urcrnrlat=box[3]+1,resolution='i',area_thresh=0);land=shapely.union_all([transform(tf,shapely.make_valid(Polygon(p.get_coords()))) for p in bm.landpolygons]);shapely.prepare(land)
  def water(x,y):return ~shapely.intersects_xy(land,*tf(x,y))
  def bbox(x,y):return (x>=box[0])&(x<=box[2])&(y>=box[1])&(y<=box[3])
  f=json.loads(read(s,region+'_survey_points.geojson'))['features'];d=pd.DataFrame([x['properties'] for x in f]);xy=np.array([x['geometry']['coordinates'] for x in f]);d['x'],d['y']=tf(xy[:,0],xy[:,1]);d['year']=d['Year' if region=='torres' else 'YEAR'].astype(int);d['p']=d.SG_present if region=='torres' else d.PRESENCE_A.map({'present':1,'absent':0});assert d.p.isin([0,1]).all();d['map']=inside(pp,d.x.to_numpy(),d.y.to_numpy())
  yrs=t.day.dt.year.to_numpy();out['audit'][region]=dict(survey_records=len(d),positive=int(d.p.sum()),negative=int((d.p==0).sum()),track_fixes=len(t),track_years=sorted(set(yrs)),map_area_km2=sum(p.area for p in pp)/1e6)
  for panel,u in [('all',d),('track_years',d[d.year.isin(yrs)]),('2008_2014',d[d.year.between(2008,2014)])]:
   out['point_vs_map'].append(dict(region=region,panel=panel,rows=len(u),positive_in=int(((u.p==1)&u['map']).sum()),positive_out=int(((u.p==1)&~u['map']).sum()),negative_in=int(((u.p==0)&u['map']).sum()),negative_out=int(((u.p==0)&~u['map']).sum())))
  trees={}
  for yr in set(yrs):
   for win in WINDOWS:
    u=d if win==99 else d[(d.year-yr).abs()<=win];trees[yr,win]=[cKDTree(u[u.p==p][['x','y']].to_numpy()) if (u.p==p).any() else None for p in [0,1]]
  def distances(x,y,year,win):
   X,Y=tf(x,y);v=np.full((len(X),2),np.inf);xy=np.c_[X,Y]
   for yr in np.unique(year):
    j=np.flatnonzero(year==yr)
    for p,k in enumerate(trees[yr,win]):
     if k is not None:v[j,p]=k.query(xy[j])[0]
   return v
  def lab(ds,r,mode):
   neg,pos=ds.T;v=np.full(len(ds),-1,np.int8)
   if mode=='nearest':v[(pos<=r)&(pos+1<neg)]=1;v[(neg<=r)&(neg+1<pos)]=0
   else:v[(pos<=r)&(neg>r)]=1;v[(neg<=r)&(pos>r)]=0
   return v
  x=t.decimalLongitude.to_numpy();y=t.decimalLatitude.to_numpy();mp=inside(pp,*tf(x,y));wet=water(x,y)
  for win in WINDOWS:
   ds=distances(x,y,yrs,win)
   for r in RADII:
    for mode in ['nearest','consensus']:
     v=lab(ds,r,mode)
     for sp,g in t.groupby('scientificName'):
      j=g.index.to_numpy();out['fix_support'].append(dict(region=region,species=sp,window=win,radius=r,mode=mode,n=len(j),positive=int((v[j]==1).sum()),negative=int((v[j]==0).sum()),unknown=int((v[j]<0).sum()),map_out_positive=int(((v[j]==1)&~mp[j]).sum()),map_in_negative=int(((v[j]==0)&mp[j]).sum())))
  for (sp,aid),g in t.groupby(['scientificName','organismID']):
   days=dict(tuple(g.groupby('day')));rr=[]
   for day,u in days.items():
    v=days.get(day+pd.Timedelta(days=7))
    if v is not None:rr.append(pd.DataFrame(dict(si=np.repeat(u.index,len(v)),ei=np.tile(v.index,len(u)),w=1/(len(u)*len(v)))))
   if len(rr)<5:continue
   p=pd.concat(rr,ignore_index=True);w=p.w.to_numpy()/len(rr);si=p.si.to_numpy();ei=p.ei.to_numpy();assert np.isclose(w.sum(),1)
   _,_,dd=G.inv(x[si],y[si],x[ei],y[ei]);n=len(ANGLES);ro,ra,_=G.fwd(np.repeat(x[si],n),np.repeat(y[si],n),np.tile(ANGLES,len(si)),np.repeat(dd,n));okrot=(bbox(ro,ra)&water(ro,ra)).reshape(-1,n);nr=okrot.sum(1);base=mp[si]&wet[si]&wet[ei]&bbox(x[ei],y[ei])&(nr>0)
   for win in WINDOWS:
    d0=distances(x[si],y[si],yrs[si],win);d1=distances(x[ei],y[ei],yrs[ei],win);dr=distances(ro,ra,np.repeat(yrs[ei],n),win)
    for r in RADII:
     for mode in ['nearest','consensus']:
      ls=lab(d0,r,mode);le=lab(d1,r,mode);lr=lab(dr,r,mode).reshape(-1,n);ns=((lr>=0)&okrot).sum(1);pos=((lr==1)&okrot).sum(1);nl=pos/np.maximum(nr,1);nu=(pos+nr-ns)/np.maximum(nr,1);conditional=pos/np.maximum(ns,1)
      for cat,sel in [('all',np.ones(len(dd),bool)),('far10',dd>=10000)]:
       for source,cond in [('map',np.ones(len(dd),bool)),('map_and_survey_positive',ls==1)]:
        use=base&sel&cond;ww=w[use];total=ww.sum()
        if total<=0:continue
        avg=lambda v:float(ww@v[use]/total)
        al,au,bl,bu=avg(le==1),avg(le!=0),avg(nl),avg(nu)
        row=dict(region=region,species=sp,animal=str(aid),distance=cat,origin=source,window=win,radius=r,mode=mode,origin_weight=float(total),observed_known=avg(le>=0),null_known=avg(ns/np.maximum(nr,1)),observed_lower=al,observed_upper=au,null_lower=bl,null_upper=bu,diff_lower=al-bu,diff_upper=au-bl,matched={})
        for k in [1,3,6]:
         j=use&(le>=0)&(ns>=k);v=w[j];zv=v.sum();row['matched'][str(k)]=dict(weight=float(zv/total),observed=float(v@(le[j]==1)/zv) if zv else None,null=float(v@conditional[j]/zv) if zv else None)
        out['individual'].append(row)
  print(region,'complete',flush=True)
 df=pd.DataFrame(out['individual']);keys=['region','species','distance','origin','window','radius','mode']
 for k,g in df.groupby(keys):
  rs=g.to_dict('records');row=dict(zip(keys,k));row['animals']=len(g)
  for c in ['origin_weight','observed_known','null_known','observed_lower','observed_upper','null_lower','null_upper','diff_lower','diff_upper']:row[c]=float(g[c].mean())
  row['matched']={}
  for j in ['1','3','6']:
   vals=[r['matched'][j] for r in rs if r['matched'][j]['weight']>0];diff=[r['observed']-r['null'] for r in vals];loo=[float(np.mean(diff[:i]+diff[i+1:])) for i in range(len(diff))] if len(diff)>1 else []
   row['matched'][j]=dict(animals=len(vals),mean_weight=float(np.mean([r['matched'][j]['weight'] for r in rs])),observed=float(np.mean([r['observed'] for r in vals])) if vals else None,null=float(np.mean([r['null'] for r in vals])) if vals else None,difference=float(np.mean(diff)) if vals else None,positive=sum(x>1e-10 for x in diff),loo=[min(loo),max(loo)] if loo else None)
  out['summary'].append(row)
 out['limits']=['Survey points may underlie the historical polygons: separate representation, not independent field validation. Nearby sampled presence/absence is a proxy, not endpoint truth. Unknown not absence.','Nearest rule chooses closer positive/negative (ties within 1m unresolved); consensus requires only one class within radius. Year windows symmetric including later surveys, 99=all years.','7-day possible date pairs, equal date-pair then animal weights, mapped origins, 36 direction endpoint water mask; not passive transport or actual seed movement. Matched support conditions on both observed and rotated surveyed endpoints and may be selective. Bounds on proxy labels are not confidence intervals or true habitat bounds.']
 return out
if __name__=='__main__':
 out=main(*sys.argv[1:4]);Path(sys.argv[4]).write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda x:x.item())+'\n')
