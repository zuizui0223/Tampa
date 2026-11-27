#!/usr/bin/env python3
"""Fixed habitat footprint; compare observed endpoints with distance-matched directions across graph gap thresholds."""
import hashlib,io,json,re,sys,zipfile
from pathlib import Path
import numpy as np,pandas as pd,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from pyproj import Transformer,Geod
from mpl_toolkits.basemap import Basemap,basemap_datadir
ARCHIVE='c17dcaa395b9dabc6ab5b61ce918e1abc68fe87b528a2bd12c0e01dd2a97920f'
H={'tracking_dwca.zip':'60a07ef8d0b750d93ee2bee18785b215107aada65f0aab2b9015f1f5e90ecdab','tracking_obis.json':'8db45fd00463cc99c8c3f539d6d42f5b247c9a606e6b04491d202556a4012193','ts_meadows.geojson':'d8452b77714c7902fcbcc872e580af98b3e91b7f135c13b33676a9babcedca1b'}
GAPS=[0,100,300,600,1000,2000,5000];LAGS=[7];G=Geod(ellps='WGS84');tf=Transformer.from_crs(4326,32754,always_xy=True).transform

def parts(g):
    if g.geom_type=='Polygon':return [g]
    return [x for p in g.geoms for x in parts(p)] if hasattr(g,'geoms') else []

def read(path):
    b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==ARCHIVE
    z=zipfile.ZipFile(io.BytesIO(b));raw={k:z.read(k) for k in H};assert all(hashlib.sha256(raw[k]).hexdigest()==v for k,v in H.items())
    a=pd.read_csv(zipfile.ZipFile(io.BytesIO(raw['tracking_dwca.zip'])).open('occurrence.txt'),sep='\t',low_memory=False)
    o=pd.DataFrame(json.loads(raw['tracking_obis.json'])['results']);assert len(a)==len(o)==6154
    a=a.merge(o[['occurrenceID','flags','decimalLatitude','decimalLongitude']],on='occurrenceID',validate='1:1',suffixes=('','_obis'));assert np.allclose(a.decimalLatitude,a.decimalLatitude_obis) and np.allclose(a.decimalLongitude,a.decimalLongitude_obis)
    a['day']=pd.to_datetime(a.eventDate);assert a.eventTime.isna().all() and a.coordinateUncertaintyInMeters.eq(300).all()
    a=a[~a['flags'].map(lambda x:'ON_LAND' in x)].drop_duplicates(['organismID','day','decimalLatitude','decimalLongitude']);assert len(a)==5884
    a=a[a.decimalLatitude>-15].copy();fs=json.loads(raw['ts_meadows.geojson'])['features'];assert len(fs)==316
    ps=[(f['properties'],transform(tf,shapely.make_valid(shape(f['geometry'])))) for f in fs]
    near=[g for p,g in ps if any(2008<=int(y)<=2012 for y in re.findall(r'\b(?:19|20)\d{2}\b',p['SURVEY_DATE']))];assert len(near)==159
    return a,{'near':shapely.union_all(near),'all':shapely.union_all([g for p,g in ps])}

def groups(p,gaps):
    n=len(p);a=np.array([x.area for x in p]); tree=shapely.STRtree(p)
    # Exact distance between polygons. No new habitat is added, unlike buffering.
    ii,jj=tree.query(p,predicate='dwithin',distance=max(gaps));valid=ii<jj;ii,jj=ii[valid],jj[valid]
    dd=shapely.distance(np.array(p,dtype=object)[ii],np.array(p,dtype=object)[jj]); result={};info={}
    for gap in gaps:
        parent=np.arange(n)
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        for i,j in zip(ii[dd<=gap+1e-8],jj[dd<=gap+1e-8]):parent[find(i)]=find(j)
        labels=np.array([find(i) for i in range(n)]);_,labels=np.unique(labels,return_inverse=True)
        ar=np.bincount(labels,weights=a);big=int(ar.argmax());result[gap]=labels
        info[gap]={'clusters':len(ar),'largest_cluster_area_fraction':float(ar[big]/a.sum()),'largest_label':big}
    return result,info

def label(tree,x,y,unique=False):
    x=np.asarray(x);y=np.asarray(y);out=np.full(x.size,-1,dtype=np.int32)
    for j,p in enumerate(tree.geometries):
        lo,bot,hi,top=p.bounds
        sel=np.flatnonzero((x>=lo)&(x<=hi)&(y>=bot)&(y<=top))
        if len(sel):
            shapely.prepare(p);out[sel[shapely.intersects_xy(p,x[sel],y[sel])]]=j
    return out

def main(path,step=10):
    a,maps=read(path);angles=np.arange(0,360,step,dtype=float)
    b=Basemap(projection='cyl',llcrnrlon=140,llcrnrlat=-12,urcrnrlon=146,urcrnrlat=-8,resolution='i',area_thresh=0)
    land=shapely.union_all([transform(tf,shapely.make_valid(Polygon(p.get_coords()))) for p in b.landpolygons]);shapely.prepare(land)
    bound=lambda lon,lat:(lon>=141)&(lon<=145)&(lat>=-11)&(lat<=-9)
    pinfo={};mapdata={}
    for k,m in maps.items():
        pp=parts(m);gg,inf=groups(pp,GAPS);pinfo[k]={'original_polygons':len(pp),'fixed_area_km2':m.area/1e6,'gap':inf};mapdata[k]=(shapely.STRtree(pp),gg,inf)
    results=[];audit=[]
    for (species,animal),g in a.groupby(['scientificName','organismID']):
        days={k:v for k,v in g.groupby('day')}
        for lag in LAGS:
            r=[]
            for day,u in days.items():
                v=days.get(day+pd.Timedelta(days=lag))
                if v is None:continue
                n,k=len(u),len(v);r.append(pd.DataFrame({'x':np.repeat(u.decimalLongitude.to_numpy(),k),'y':np.repeat(u.decimalLatitude.to_numpy(),k),'xx':np.tile(v.decimalLongitude.to_numpy(),n),'yy':np.tile(v.decimalLatitude.to_numpy(),n),'w':1/(n*k)}))
            if len(r)<5:continue
            q=pd.concat(r,ignore_index=True);x,y,xx,yy,w=[q[k].to_numpy() for k in ['x','y','xx','yy','w']];w/=len(r);assert np.isclose(w.sum(),1)
            _,_,dd=G.inv(x,y,xx,yy);ox,oy=tf(x,y);ex,ey=tf(xx,yy)
            rx,ry,_=G.fwd(np.repeat(x,len(angles)),np.repeat(y,len(angles)),np.tile(angles,len(x)),np.repeat(dd,len(angles)))
            rxm,rym=tf(rx,ry);okrot=(bound(rx,ry)&~shapely.intersects_xy(land,rxm,rym)).reshape(len(q),-1)
            okobs=bound(xx,yy)&~shapely.intersects_xy(land,ox,oy)&~shapely.intersects_xy(land,ex,ey)
            nrot=okrot.sum(axis=1);safe=np.maximum(nrot,1)
            for name,(tree,gg,inf) in mapdata.items():
                pi=label(tree,ox,oy,True);pj=label(tree,ex,ey,True);pr=label(tree,rxm,rym,True).reshape(len(q),-1)
                om=pi>=0;em=pj>=0;rm=pr>=0;eligible=om&okobs&(nrot>0)
                nm=(rm&okrot).sum(axis=1)/safe
                for gap in GAPS:
                    lab=gg[gap];si=np.where(om,lab[np.maximum(pi,0)],-1);sj=np.where(em,lab[np.maximum(pj,0)],-1);sr=np.where(rm,lab[np.maximum(pr,0)],-1)
                    other=em&(si!=sj);ro=rm&(sr!=si[:,None]);no=(ro&okrot).sum(axis=1)/safe
                    # Count all mapped destination arrivals, separate same-cluster and different-cluster. Identical denominators for all gap thresholds.
                    for name2,sel in [('all',np.ones(len(dd),bool)),('near10',dd<10000),('far10',dd>=10000)]:
                        for origin,os in [('all',np.ones(len(dd),bool)),('largest',si==inf[gap]['largest_label']),('other',si!=inf[gap]['largest_label'])]:
                            valid=eligible&sel&os;ww=w[valid];den=ww.sum()
                            if den<=0:continue
                            avg=lambda z:float(np.dot(z[valid],ww)/den)
                            results.append(dict(species=species,animal=str(animal),lag=lag,daypairs=len(r),map=name,gap=gap,distance=name2,origin_class=origin,weight=float(den),observed_mapped=avg(em),null_mapped=avg(nm),observed_cross=avg(other),null_cross=avg(no),excess_cross=avg(other-no),observed_same=avg(em&~other),null_same=avg(nm-no),mean_km=avg(dd/1000),origin_largest=avg(si==inf[gap]['largest_label'])))
            audit.append({'species':species,'lag':lag,'daypairs':len(r),'fixpairs':len(q)})
            print(species,lag,len(r),len(q),flush=True)
    df=pd.DataFrame(results);summ=[]
    for key,g in df.groupby(['species','lag','map','gap','distance','origin_class']):
        rec=dict(zip(['species','lag','map','gap','distance','origin_class'],key));rec['animals']=len(g);rec['negative']=int((g.excess_cross< -1e-10).sum())
        for k in ['weight','observed_mapped','null_mapped','observed_cross','null_cross','excess_cross','observed_same','null_same','mean_km','origin_largest']:rec[k]=float(g[k].mean())
        vals=g.excess_cross.to_numpy();loo=[np.delete(vals,i).mean() for i in range(len(vals))] if len(vals)>1 else []
        rec['loo_cross']=[float(min(loo)),float(max(loo))] if loo else None;summ.append(rec)
    # Monotonicity on fixed denominator and exact arithmetic; no statistical tests on dependent pairs.
    test=df[df.origin_class=='all']
    for _,g in test.groupby(['species','animal','lag','map','distance']):
        g=g.sort_values('gap');assert len(g)==len(GAPS) and np.ptp(g.weight)<1e-12 and np.ptp(g.observed_mapped)<1e-12 and np.ptp(g.null_mapped)<1e-12
        assert np.all(np.diff(g.observed_cross)<=1e-12) and np.all(np.diff(g.null_cross)<=1e-12)
    return dict(archive=ARCHIVE,hashes=H,coast_hashes={n:hashlib.sha256(Path(basemap_datadir,n).read_bytes()).hexdigest() for n in ['gshhs_i.dat','gshhsmeta_i.dat']},bearing_step=step,gaps_m=GAPS,maps=pinfo,audit=audit,summary=summ,individual=results,limits=['Distance-matched isotropic endpoint reference, NOT water transport. No tracked ingestion, defecation or seed survival.','Gap graph joins polygons by single linkage across gaps; no extra habitat area and no evidence that gaps are traversable by seeds. Largest cluster and origin class change with gap.','Maps are historical composite footprints; outside does not mean unsuitable. Coast mask endpoints only, no path constraint.','Day-level possible pairs, equal day pairs then animals. Few tracked animals; no pair-level significance.'])
if __name__=='__main__':
    out=main(sys.argv[1],int(sys.argv[3]) if len(sys.argv)>3 else 10);Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda v:v.item())+'\n')
