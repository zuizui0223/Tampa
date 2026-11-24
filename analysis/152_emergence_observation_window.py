#!/usr/bin/env python3
"""Jorgensen 2019 original-data emergence and fate; descriptive tank-level contrasts."""
import argparse,hashlib,io,itertools,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from openpyxl import load_workbook
HASH='9286792a9cca0b46ec1e9d1add5a869625b91c57bb53ee32788b982b825bbfa3'
def run(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        manifest=json.loads(z.read('manifest.json'))
        def read(k):
            name=f'jorgensen_s{k}.xlsx';b=z.read(name)
            assert hashlib.sha256(b).hexdigest()==next(x['sha256'] for x in manifest if x['file']==name)
            rows=list(load_workbook(io.BytesIO(b),data_only=True).active.values)
            return pd.DataFrame(rows[1:],columns=rows[0]).loc[:,lambda d:d.columns.notna()].dropna(how='all')
        e,f,b=read(2),read(3),read(4)
    pot='Pot ID';tank='Mesocosm ID';depth='Seed burial depth (cm)';size='Seed size grouping';day='Time (days)';week='Time (weeks)';count='Seedling emergence';final='Total seedling emergence';total='Total number of seeds'
    assert len(e)==1070 and len(f)==100 and len(b)==486 and f[pot].is_unique and not e.duplicated([pot,day]).any()
    assert not e[[pot,tank,depth,size,day,count]].isna().any().any()
    assert e[count].between(0,15).all() and (e[count]%1==0).all()
    assert set(e[pot])==set(f[pot])
    d=e.merge(f[[pot,tank,depth,size,week,final]],on=[pot,tank,depth,size],validate='many_to_one')
    assert len(d)==len(e)
    d=d.sort_values([pot,day]);assert (d.groupby(pot).tail(1)[count]==d.groupby(pot).tail(1)[final]).all()
    decreasing=d.loc[d.groupby(pot)[count].diff()<0,[pot,day,count]].to_dict('records')
    outcomes=[final,'Dead seeds','Viable seeds','Unsuccessfully emerged seeds']
    assert (f[outcomes].sum(axis=1)==f[total]).all()
    assert (f[outcomes]>=0).all().all()
    u=d[d[size].eq('unsorted') & d[day].le(62)].copy()
    assert len(u)==630 and u[pot].nunique()==70
    depths=[.1,1.,2.,3.,4.,6.,8.];days=[16,19,21,26,34,40,47,55,62]
    cube=u.groupby([tank,depth,day])[count].mean().unstack([depth,day])/15
    assert cube.shape==(5,63) and u.groupby([tank,depth,day]).size().eq(2).all()
    rng=np.random.default_rng(20261124);ids=rng.integers(0,5,size=(50000,5))
    def paired(x):
        x=np.asarray(x,float);assert len(x)==5
        o=float(x.mean());ci=np.quantile(x[ids].mean(axis=1),[.025,.975]).tolist()
        null=np.asarray([np.mean(x*np.array(s)) for s in itertools.product([-1,1],repeat=5)])
        return dict(mean=o,conditional_tank_bootstrap95=ci,by_tank=x.tolist(),exact_sign_flip_two_sided=float(np.mean(np.abs(null)>=abs(o)-1e-12)))
    emergence=[]
    for dep in depths:
        means={str(t):float(cube[dep,t].mean()) for t in days}
        emergence.append(dict(depth_cm=dep,rates=means,early_fraction_of_day62=means['16']/means['62'],late_gain=paired(cube[dep,62]-cube[dep,16])))
    contrast4={str(t):paired(cube[4,t]-cube[.1,t]) for t in [16,26,40,62]}
    contrast4['change_in_contrast_16_to_62']=paired((cube[4,62]-cube[.1,62])-(cube[4,16]-cube[.1,16]))
    fate=[]
    for w in [8,24]:
        s=f[f[size].eq('unsorted')&f[week].eq(w)].copy()
        assert len(s)==35
        shallow=s[s[depth].isin([1.,2.])];deep=s[s[depth].isin([6.,8.])]
        row=dict(week=w,groups={},contrasts_deep_minus_shallow={})
        for label,g in [('shallow_1_2',shallow),('deep_6_8',deep)]:
            assert len(g)==10
            row['groups'][label]={'n_pots':len(g),'reported_total':int(g[total].sum()),'nominal_sown':150,'n_below_nominal':int(g[total].lt(15).sum()),'n_above_nominal':int(g[total].gt(15).sum()),'counts':{x:int(g[x].sum()) for x in outcomes},'pooled_reported_fractions':{x:float(g[x].sum()/g[total].sum()) for x in outcomes},'pot_equal_reported_fractions':{x:float((g[x]/g[total]).mean()) for x in outcomes}}
        for x in outcomes:
            a=(deep[x]/deep[total]).groupby(deep[tank]).mean();b0=(shallow[x]/shallow[total]).groupby(shallow[tank]).mean()
            row['contrasts_deep_minus_shallow'][x]=paired((a-b0).values)
        fate.append(row)
    p={r['depth_cm']:r['rates']['62'] for r in emergence}
    scenario=[dict(depth_cm=k,observed_E=v,min_risk_at_1cm_if_other_depth_risk_zero=1-v/p[1.],break_even_risk_at_depth_if_1cm_risk_20pct=1-(p[1.]*(1-.2)/v) if v>0 else None) for k,v in p.items() if k>1]
    sizes=[]
    s=f[f[week].eq(10)].copy();assert len(s)==30
    for dep in [2.,4.,6.]:
        g=s[s[depth].eq(dep)];assert len(g)==10
        small=g[g[size].eq('small')].set_index(tank);large=g[g[size].eq('large')].set_index(tank)
        rec=dict(depth_cm=dep,emergence_large_minus_small=paired((large[final]-small[final])/15),viable_reported_large_minus_small=paired(large['Viable seeds']/large[total]-small['Viable seeds']/small[total]),failed_reported_large_minus_small=paired(large['Unsuccessfully emerged seeds']/large[total]-small['Unsuccessfully emerged seeds']/small[total]))
        sizes.append(rec)
    bc=b.groupby(pot).size().reindex(f[pot],fill_value=0).to_numpy();bjoin=b.merge(f[[pot,week]],on=pot,suffixes=('_mass','_fate'),validate='many_to_one')
    return dict(status='response-open original data; tank-clustered descriptive contrasts; no causal biotic partner effect',source='10.1371/journal.pone.0215157',archive_sha256=HASH,counts=dict(emergence_rows=len(e),pots=len(f),biomass_rows=len(b),unsorted_pots=u[pot].nunique(),tanks=5,nominal_seeds=1500,fate_below15=int(f[total].lt(15).sum()),fate_above15=int(f[total].gt(15).sum()),fate_equal15=int(f[total].eq(15).sum()),nonmonotone_records=decreasing,biomass_row_count_mismatch_pots=int((bc!=f[final].to_numpy()).sum()),biomass_harvest_time_mismatch_rows=int((bjoin[week+'_mass']!=bjoin[week+'_fate']).sum())),emergence=emergence,contrast_4cm_minus_point1cm=contrast4,fate=fate,scenario_only=scenario,seed_size_10week=sizes,limitations=['Day 62 is common observed endpoint; seedling counts not individual survival, two later decreases. Nominal 15 seeds planted per pot; fate accounting denominator is reported total, 39 pots differ from nominal.','All bootstrap intervals conditional on five tanks and unadjusted; sign flip assumes symmetric independent tank-level differences. No independent site or external validation.','8- and 24-week destructive harvests use different pots, not individual seed histories.','Scenario assumes independent additional mortality and unchanged emergence conditional on survival; not a measured joint predator-depth effect.','Biomass totals not estimated owing to incomplete and inconsistent row-to-pot counts.'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2)+'\n')
