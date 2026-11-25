#!/usr/bin/env python3
"""Common mapped cells and prior-year SIBES overlap. No inferred absence beyond map support."""
import argparse,zipfile,json,hashlib,io,numpy as np,pandas as pd,shapely as sh
from pathlib import Path
from pyproj import Transformer
from scipy.spatial import cKDTree
def run(MAP,BENTH,OUT):
    OUT.mkdir(exist_ok=True,parents=True)
    assert hashlib.sha256(MAP.read_bytes()).hexdigest()=='ad0097d3e14373bf0cb7babef0dd4aa26678d6bb97c7e5d94af5f7e534bc05e1'
    assert hashlib.sha256(BENTH.read_bytes()).hexdigest()=='843038aefe1afaed39ded71f4d5e5890262a778300c1f0ab011245b7e61ead8a'
    tr=Transformer.from_crs(4326,28992,always_xy=True);years=[2011,2014,2017,2020,2023];maps={};audit={}
    with zipfile.ZipFile(MAP) as z:
        m=json.loads(z.read('manifest.json'));hashes={r['data']['file']:r['data']['sha256'] for x in m for r in x.get('layers',[]) if 'data' in r}
        for y in years:
            n=f'zeegras_zostera_marina_{y}_features.geojson';raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==hashes[n];j=json.loads(raw);f=j['features'];assert len(f)==j['numberMatched']==j['numberReturned'] and j['crs']['properties']['name'].endswith('CRS::84')
            g=sh.transform(sh.from_geojson([json.dumps(x['geometry']) for x in f]),tr.transform,interleaved=False);c=sh.get_coordinates(sh.centroid(g));a=sh.area(g);assert sh.is_valid(g).all() and np.max(np.abs(c-(np.floor(c/20)*20+10)))<.2
            d=pd.DataFrame([x['properties'] for x in f]);assert d.jaar.eq(y).all() and d.hoofdgeb.eq('Waddenzee').all() and d[['bed_zosmar','bed_zosnol']].notna().all().all() and d[['bed_zosmar','bed_zosnol']].ge(0).all().all()
            d['i']=np.floor(c[:,0]/20).astype(int);d['j']=np.floor(c[:,1]/20).astype(int)
            dup=d.duplicated(['i','j'],False);audit[y]={'rows':len(d),'ambiguous_duplicate_rows':int(dup.sum()),'ambiguous_cells':len(d[dup][['i','j']].drop_duplicates()),'marina_positive':int(d.bed_zosmar.gt(0).sum()),'noltei_positive':int(d.bed_zosnol.gt(0).sum()),'area_range':list(map(float,[a.min(),a.max()]))}
            maps[y]=d[~dup].set_index(['i','j'])[['bed_zosmar','bed_zosnol','deelgeb']].sort_index()
    with zipfile.ZipFile(BENTH) as z:
        m=json.loads(z.read('manifest.json'));h={x['file']:x['sha256'] for x in m[1]['files']}
        def read(n):
            b=z.read('official_'+n+'.csv');assert hashlib.sha256(b).hexdigest()==h['official_'+n+'.csv'];return pd.read_csv(io.BytesIO(b))
        s,b,sp=map(read,['samples','biota','species'])
    assert sp.loc[sp.name.eq('Hediste diversicolor'),'sibes_id'].item()==11 and sp.loc[sp.name.eq('Nereididae'),'sibes_id'].item()==15
    s=s[~s.sample_id.duplicated(False)].copy();s['year']=pd.to_datetime(s.date).dt.year;s['doy']=pd.to_datetime(s.date).dt.dayofyear;s=s[s.sampling_type.eq('grid')].copy();s=s[s.sample_id.isin(b.sample_id)].copy()
    s=s.merge(b[b.sibes_id.eq(11)][['sample_id','abundance_m2','afdm_m2']],on='sample_id',how='left',validate='one_to_one')
    s['detected']=s.abundance_m2.notna();s['B']=s.afdm_m2.where(s.detected,0);s['N']=s.abundance_m2.where(s.detected,0);s['M']=1000*s.B/s.N;s['family']=s.sample_id.isin(b.loc[b.sibes_id.eq(15),'sample_id']);s['rdx'],s['rdy']=tr.transform(s.x.to_numpy(),s.y.to_numpy());s['i']=np.floor(s.rdx/20).astype(int);s['j']=np.floor(s.rdy/20).astype(int)
    trans=[];panels=[]
    for y0,y1 in zip(years[:-1],years[1:]):
        mm=maps[y0].join(maps[y1],lsuffix='_0',rsuffix='_1',how='inner');xy=np.array(mm.index.tolist())*20+10;tree=cKDTree(xy);dd={'from':y0,'to':y1,'common_cells':len(mm)}
        for host in ['mar','nol']:
            x=mm['bed_zos'+host+'_0'].gt(0);y=mm['bed_zos'+host+'_1'].gt(0);dd[host]={'00':int((~x&~y).sum()),'01':int((~x&y).sum()),'10':int((x&~y).sum()),'11':int((x&y).sum())}
        trans.append(dd)
        for lag in [1,2,4]:
            ss=s[s.year.eq(y1-lag)].copy();ss=ss[~ss.sampling_station_id.duplicated(False)].copy();p=ss[['rdx','rdy']].to_numpy()
            for radius in [0,100,250,500]:
                if radius==0:
                    groups=mm.index.get_indexer(pd.MultiIndex.from_frame(ss[['i','j']])).reshape(-1,1);groups=[g[g>=0] for g in groups];nominal=1
                else:groups=tree.query_ball_point(p,radius);nominal=np.pi*radius**2/400
                for k,idx in enumerate(groups):
                    if len(idx)==0:continue
                    f=ss.iloc[k];t=mm.iloc[idx];q={'from':y0,'to':y1,'lag':lag,'radius':radius,'n_cells':len(idx),'support_fraction':len(idx)/nominal}
                    q.update(f[['sample_id','sampling_station_id','year','doy','tidal_basin_name','rdx','rdy','median_grain_size','percentage_mud','N','B','M','family','detected']].to_dict())
                    for host in ['mar','nol']:
                        x=t['bed_zos'+host+'_0'];y=t['bed_zos'+host+'_1'];q.update({host+'_p0':float(x.gt(0).mean()),host+'_p1':float(y.gt(0).mean()),host+'_cover0':float(x.mean()),host+'_cover1':float(y.mean()),host+'_n01':int((x.eq(0)&y.gt(0)).sum()),host+'_n10':int((x.gt(0)&y.eq(0)).sum())})
                    panels.append(q)
    p=pd.DataFrame(panels);p.to_csv(OUT/'map_benthos_overlap.csv',index=False)
    common=maps[years[0]].index
    for y in years[1:]:common=common.intersection(maps[y].index)
    q=maps[2023];outside=q[~q.index.isin(maps[2020].index)]
    primary=p.query('lag==1 and radius==0')
    res={'map_audit':audit,'transitions':trans,'all_five_common_cells':len(common),'all_five_common_counts':{y:{h:int(maps[y].loc[common,'bed_zos'+h].gt(0).sum()) for h in ['mar','nol']} for y in years},'outside_2020_2023_positive_by_area':outside[outside.bed_zosmar.gt(0)].groupby('deelgeb').size().to_dict(),'exact_prior_year':{'n':len(primary),'stations':int(primary.sampling_station_id.nunique()),'n_recorded_M':int(primary.M.notna().sum()),'mar_gain':int(primary.mar_n01.sum()),'mar_loss':int(primary.mar_n10.sum())},'radius_gate':p.groupby(['lag','radius','from']).agg(n=('sample_id','size'),n_M=('M','count'),support=('support_fraction','median'),mar_gain=('mar_n01',lambda x:sum(x>0)),mar_loss=('mar_n10',lambda x:sum(x>0))).reset_index().to_dict('records')}
    (OUT/'audit.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
    return res
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('map',type=Path);a.add_argument('benthos',type=Path);a.add_argument('--out',type=Path,required=True);v=a.parse_args();print(json.dumps(run(v.map,v.benthos,v.out),indent=2))
