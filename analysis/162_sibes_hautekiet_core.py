#!/usr/bin/env python3
"""Core reproduction of source-verified SIBES ranks and Hautekiet survival contrasts.
Full local script additionally outputs field sensitivity, audit, and per-year tables.
"""
import argparse,hashlib,io,json,zipfile,itertools
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr
HASH='843038aefe1afaed39ded71f4d5e5890262a778300c1f0ab011245b7e61ead8a'
def run(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read('manifest.json'))
        hashes={x['file']:x['sha256'] for x in m[1]['files']+m[2]['members']}
        def read(name,sep=','):
            b=z.read(name);assert hashlib.sha256(b).hexdigest()==hashes[name]
            return pd.read_csv(io.BytesIO(b),sep=sep,low_memory=False).loc[:,lambda x:~x.columns.str.startswith('Unnamed')]
        s,b,sp=[read('official_'+f+'.csv') for f in ('samples','biota','species')]
        a=read('hautekiet_262_Survival_data.csv',';')
        f=read('hautekiet_9_SeedlingSurvival_Vaucheria-vs-Mud.csv',';')
    assert not b.duplicated(['sample_id','sibes_id']).any() and b.sample_id.isin(s.sample_id).all() and sp.sibes_id.is_unique
    ids=s.loc[s.sample_id.duplicated(False),'sample_id'].unique();assert len(ids)==6
    s0=s[~s.sample_id.isin(ids)].copy();s0['year']=pd.to_datetime(s0.date).dt.year
    assert s0.sample_id.is_unique
    hid=sp.loc[sp.name.eq('Hediste diversicolor'),'sibes_id'].item()
    fid=sp.loc[sp.name.eq('Nereididae'),'sibes_id'].item();assert hid==11 and fid==15
    h=b[b.sibes_id.eq(hid)].merge(s0,on='sample_id',validate='one_to_one')
    h['family_also_recorded']=h.sample_id.isin(b.loc[b.sibes_id.eq(fid),'sample_id'])
    assert h.abundance_m2.gt(0).all() and h.afdm_m2.ge(0).all()
    def aggregate(d):
        assert d.groupby(['sampling_station_id','year']).tidal_basin_name.nunique().le(1).all()
        a=d.groupby(['sampling_station_id','year','tidal_basin_name'],as_index=False).agg(N=('abundance_m2','mean'),B=('afdm_m2','mean'),samples=('sample_id','size'))
        a['M']=1000*a.B/a.N;return a
    def ranking(d,groupcols,min_n=30):
        rows=[];marks=[]
        for key,x in d.groupby(groupcols):
            if len(x)<min_n:continue
            x=x.copy();x['Btop']=x.B.ge(x.B.quantile(.75));x['Mtop']=x.M.ge(x.M.quantile(.75));x['B_rank']=x.B.rank(pct=True);x['M_rank']=x.M.rank(pct=True)
            B=int(x.Btop.sum());M=int(x.Mtop.sum());both=int((x.Btop&x.Mtop).sum())
            key=key if isinstance(key,tuple) else (key,)
            rows.append(dict(zip(groupcols,key))|dict(n=len(x),Btop=B,Mtop=M,both=both,jaccard=both/(B+M-both),rho_B_M=float(spearmanr(x.B,x.M).statistic)))
            marks.append(x)
        return pd.DataFrame(rows),pd.concat(marks,ignore_index=True)
    def digest(r):
        return dict(groups=len(r),events=int(r.n.sum()),top_B=int(r.Btop.sum()),top_M=int(r.Mtop.sum()),both=int(r.both.sum()),fraction_Mtop_outside_Btop=float(1-r.both.sum()/r.Mtop.sum()),median_group_rho_B_M=float(r.rho_B_M.median()))
    pos=h[h.afdm_m2.gt(0)].copy();grid=pos[pos.sampling_type.eq('grid')];primary=aggregate(grid)
    rows,marked=ranking(primary,['year','tidal_basin_name']);annual,_=ranking(primary,['year'])
    sens={}
    for name,dd in [('all_sampling_types',pos),('grid_no_family',grid[~grid.family_also_recorded]),('grid_2012_2022',grid[grid.year.ge(2012)]),('grid_2008_2021',grid[grid.year.le(2021)]),('grid_include_recorded_zero_AFDM',h[h.sampling_type.eq('grid')])]:
        r,_=ranking(aggregate(dd),['year','tidal_basin_name']);sens[name]=digest(r)
    bands=[]
    for lo,hi in [(.5,1),(1,2),(2,4),(4,8),(8,16)]:
        x=primary[primary.B.ge(lo)&primary.B.lt(hi)];q=x.M.quantile([.1,.5,.9]).tolist()
        bands.append(dict(AFDM_band=[lo,hi],events=len(x),mean_individual_AFDM_mg_q10_q50_q90=q))
    left=marked[['sampling_station_id','year','tidal_basin_name','B','M','N','Btop','Mtop','B_rank','M_rank']].copy();right=left.copy();right.year-=1
    pairs=left.merge(right,on=['sampling_station_id','year','tidal_basin_name'],suffixes=('_t','_t1'),validate='one_to_one')
    trans={}
    for metric in ['B','M']:
        t=pairs[metric+'top_t'];u=pairs[metric+'top_t1'];trans[metric]={'n_start_top':int(t.sum()),'n_retained_top':int((t&u).sum()),'retention':float((t&u).sum()/t.sum())}
    sameB=pairs.B_t1.div(pairs.B_t).between(.9,1.1);ratio=pairs.M_t1/pairs.M_t
    trans['similar_B_10pct']={'n':int(sameB.sum()),'M_twofold_change':int((sameB&((ratio>=2)|(ratio<=.5))).sum()),'M_rank_class_switches':int((sameB&(pairs.Mtop_t!=pairs.Mtop_t1)).sum())}
    assert len(a)==40 and a.Pot.is_unique and a.nr_start.eq(5).all() and a.nr_end.between(0,5).all() and a.groupby(['Worms','Vaucheria']).size().eq(10).all()
    a['survival']=a.nr_end/a.nr_start;cells={k:x.survival.to_numpy() for k,x in a.groupby(['Worms','Vaucheria'])};means={k:v.mean() for k,v in cells.items()}
    rng=np.random.default_rng(20261125);B=50000;bs={k:rng.choice(v,(B,len(v)),replace=True).mean(1) for k,v in cells.items()}
    def contrasts(c):
        w0=c[1,0]-c[0,0];w1=c[1,1]-c[0,1];v0=c[0,1]-c[0,0];v1=c[1,1]-c[1,0]
        return {'worm_without_algae':w0,'worm_with_algae':w1,'algae_without_worm':v0,'algae_with_worm':v1,'interaction_RD':w1-w0}
    con=contrasts(means);cb=contrasts(bs)
    full={'cells':{'|'.join(map(str,k)):dict(n_pots=len(v),surviving=int(v.sum()*5+.5),initial=len(v)*5,mean=float(v.mean())) for k,v in cells.items()},'contrasts':{k:dict(estimate=float(v),ci_conditional_pot_bootstrap=np.quantile(cb[k],[.025,.975]).tolist()) for k,v in con.items()}}
    vals=[]
    for k,v in cells.items():
        for i in range(len(v)):
            m0=means.copy();m0[k]=np.delete(v,i).mean();vals.append(contrasts(m0)['interaction_RD'])
    full['interaction_loo_range']=[min(vals),max(vals)]
    f['survival']=f.End_nr/f.Start_nr;fw=f.pivot(index='Plot',columns='Treatment',values='survival');assert len(fw)==6 and fw.notna().all().all()
    d=(fw.Vau-fw.Mud).to_numpy();sg=np.array(list(itertools.product([-1,1],repeat=len(d))))
    full['field_paired']={'n_pairs':len(d),'means':fw.mean().to_dict(),'delta':float(d.mean()),'by_pair':d.tolist(),'ci_conditional_pair_bootstrap':np.quantile(rng.choice(d,(B,len(d)),replace=True).mean(1),[.025,.975]).tolist(),'p_sign_flip_two_sided':float(np.mean(np.abs((sg*d).mean(1))>=abs(d.mean())-1e-12))}
    return {'source_hashes':hashes,'SIBES':{'sample_rows':len(s),'biota_rows':len(b),'unique_stations':s.sampling_station_id.nunique(),'identified_hediste_rows':len(h),'primary_station_years':len(primary),'primary_stations':primary.sampling_station_id.nunique(),'year_basin_ranking':digest(rows),'year_ranking':digest(annual),'sensitivity':sens,'same_total_biomass_bands':bands,'consecutive_station_year_pairs':len(pairs),'consecutive_transitions':trans},'Hautekiet':full},rows,marked
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    r,rr,mm=run(a.artifact);a.out.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    rr.to_csv(a.out.with_name('year_basin_ranking.csv'),index=False);mm.to_csv(a.out.with_name('station_year_ranks.csv'),index=False)
