#!/usr/bin/env python3
"""Fixed-count virtual removals on source-mapped Enhalus ramets.
Not observed disturbance, flowering, pollen movement or seed production.
"""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix

ARCHIVE_SHA='b5b116221241e9e603896a9dc99f66287f4707a313c12bf83ff7dd00487dc1f2'
MEMBER='yu/Ramets For Two plots.xlsx'
MEMBER_SHA='10e1465ac9255ad2d873d6142386b5140320740ebc660196b4a9eb0e2251c959'
RADII=(1.,2.,4.)
LOSS=(.25,.50,.75)
MODELS=('random','localized_gap','parallel_gaps_6m')
N_SIM=500

def read_source(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()==ARCHIVE_SHA:
        raw=zipfile.ZipFile(io.BytesIO(raw)).read(MEMBER)
    if hashlib.sha256(raw).hexdigest()!=MEMBER_SHA:raise ValueError('source hash mismatch')
    return raw

def graph_matrices(xy,g,r,angle=None):
    vec=xy[None,:,:]-xy[:,None,:]
    dist=cdist(xy,xy)
    close=(dist>0)&(dist<=r)&(g[:,None]!=g[None,:])
    if angle is not None:
        close&=(vec[:,:,0]*np.cos(angle)+vec[:,:,1]*np.sin(angle)>=dist*np.sqrt(.5)-1e-12)
    rows,cols=np.nonzero(close)
    pairs=np.column_stack([rows,g[cols]])
    groups,inv=np.unique(pairs,axis=0,return_inverse=True)
    H=csr_matrix((np.ones(len(cols),dtype=np.int16),(inv,cols)),shape=(len(groups),len(g)))
    return csr_matrix(close.astype(np.int16)),H,groups[:,0]

def metrics(graph,keep,g):
    G,H,parents=graph
    active=np.asarray(keep,bool);k=active.astype(np.int16)
    d=np.asarray(G @ k).ravel()[active]
    unique=np.bincount(parents,weights=(np.asarray(H @ k).ravel()>0).astype(float),minlength=len(g))[active]
    assert np.array_equal(d==0,unique==0) and (d>=unique).all()
    return np.array([len(np.unique(g[active])),float(np.mean(d)),float(np.mean(unique)),float(np.mean(unique==0)),float(np.mean(unique>=3))])

def summarized(a):
    return {'mean':np.mean(a,axis=0).tolist(),'simulation_quantiles_025_50_975':np.quantile(a,[.025,.5,.975],axis=0).tolist()}

def plot_sim(xy,g,seed,nsim):
    n=len(g);rng=np.random.default_rng(seed);full=np.ones(n,bool)
    mats={r:[graph_matrices(xy,g,r)]+[graph_matrices(xy,g,r,i*np.pi/4) for i in range(8)] for r in RADII}
    baselines={str(r):{'isotropic':metrics(mats[r][0],full,g).tolist(),'directional_axis_mean':np.mean([metrics(m,full,g) for m in mats[r][1:]],axis=0).tolist()} for r in RADII}
    out={}
    for fraction in LOSS:
        removed=round(n*fraction);keep_n=n-removed
        values={m:{str(r):{'isotropic':[],'directional':[]} for r in RADII} for m in MODELS}
        for sim in range(nsim):
            center=rng.uniform(0,20,2);theta=rng.uniform(0,np.pi);phase=rng.uniform(0,6);axis=int(rng.integers(8))
            d=np.linalg.norm(xy-center,axis=1)
            s=xy@np.array([np.cos(theta),np.sin(theta)])
            stripe=np.abs((s-phase+3)%6-3)
            scores=[rng.random(n),d,stripe]
            for mode,score in zip(MODELS,scores):
                k=np.ones(n,bool);k[np.lexsort((rng.random(n),score))[:removed]]=False
                assert k.sum()==keep_n
                for r in RADII:
                    values[mode][str(r)]['isotropic'].append(metrics(mats[r][0],k,g))
                    values[mode][str(r)]['directional'].append(metrics(mats[r][1+axis],k,g))
        result={'retained':keep_n,'removed':removed,'models':{m:{r:{d:summarized(np.asarray(a)) for d,a in z.items()} for r,z in q.items()} for m,q in values.items()},'paired_difference_vs_random':{}}
        for mode in MODELS[1:]:
            result['paired_difference_vs_random'][mode]={r:{d:summarized(np.asarray(values[mode][r][d])-np.asarray(values['random'][r][d])) for d in ('isotropic','directional')} for r in map(str,RADII)}
        out[str(fraction)]=result
    return {'source_ramets':n,'source_exact_MLGs':len(np.unique(g)),'full':baselines,'virtual_removal':out}

def analyze(path,nsim=N_SIM):
    raw=read_source(path);out={}
    for i,(sheet,nn,ng) in enumerate([('PLOTA',271,214),('PLOTB',395,255)]):
        a=pd.read_excel(io.BytesIO(raw),sheet_name=sheet,header=None).iloc[3:]
        assert len(a)==nn and not a.iloc[:,[0,1,*range(2,18),19,20]].isna().any().any()
        xy=a.iloc[:,[19,20]].to_numpy(float);assert len(np.unique(xy,axis=0))==nn and xy.min()==0 and xy.max()==20
        gmat=np.sort(a.iloc[:,2:18].to_numpy(int).reshape(-1,8,2),axis=2).reshape(-1,16)
        _,g=np.unique(gmat,axis=0,return_inverse=True);assert len(np.unique(g))==ng
        out[sheet]=plot_sim(xy,g,20261125+i,nsim)
    return {'status':'source_mapped_counterfactual_geometry_not_field_effect','doi':'10.1002/ece3.5106','data_doi':'10.5061/dryad.sn1h87s','archive_sha256':ARCHIVE_SHA,'member_sha256':MEMBER_SHA,'simulations_per_plot_loss_mode':nsim,'metrics':['retained_plot_MLGs','mean_other_MLG_shoot_neighbors','mean_distinct_other_MLG_neighbors','fraction_without_other_MLG_neighbor','fraction_with_at_least_3_other_MLG_neighbors'],'plot_results':out,'limitations':['Each mapped sample is a ramet observation, not a flowering individual. Exact multilocus marker identity is the working clone label. Other MLGs are potential distinct genets, not confirmed compatible or male/female donors.','Random removal, distance-to-random-center removal and distance-to-parallel-lines removal with exact equal survivor counts are counterfactual geometries. They are not observed disturbance or measured fragment sizes. Period 6 m chosen as a sensitivity scenario, not calibrated.','Distance cutoffs 1/2/4 m and eight 90-degree donor sectors are illustrative, not measured dispersal kernels. No empirical water direction, velocity, animal transport, sex or flowering phenology. Directional mean averages simulated orientations; no biological pollen prediction.','Two 20x20 m source plots, one per habitat; no independent habitat replication. Within-plot boundaries omit outside donors; results conditional on sampling. Simulation quantiles reflect chosen virtual masks, not field confidence intervals. No causal effect of fragmentation or inference of seed production.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--simulations',type=int,default=N_SIM);p.add_argument('--out',type=Path);args=p.parse_args();s=json.dumps(analyze(args.source,args.simulations),indent=2,sort_keys=True,allow_nan=False)
    if args.out:args.out.write_text(s+'\n')
    else:print(s)
