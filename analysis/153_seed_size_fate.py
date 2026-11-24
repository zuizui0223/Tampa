#!/usr/bin/env python3
"""Stage-resolved seed size comparison, Jorgensen 2019 S2/S3; five tanks, three fixed depths."""
import argparse, hashlib, io, itertools, json, zipfile
from pathlib import Path
import numpy as np,pandas as pd
from openpyxl import load_workbook
HASH='9286792a9cca0b46ec1e9d1add5a869625b91c57bb53ee32788b982b825bbfa3'
def run(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read('manifest.json'))
        def read(k):
            name=f'jorgensen_s{k}.xlsx';b=z.read(name)
            assert hashlib.sha256(b).hexdigest()==next(x['sha256'] for x in m if x['file']==name)
            r=list(load_workbook(io.BytesIO(b),data_only=True).active.values)
            return pd.DataFrame(r[1:],columns=r[0]).loc[:,lambda d:d.columns.notna()].dropna(how='all')
        f=read(3);e=read(2)
    pot='Pot ID';tank='Mesocosm ID';depth='Seed burial depth (cm)';size='Seed size grouping';total='Total number of seeds';day='Time (days)';em='Total seedling emergence'
    d=f[f['Time (weeks)'].eq(10)].copy();assert len(d)==30 and d.groupby([tank,depth,size]).size().eq(1).all() and set(d[depth])=={2,4,6} and set(d[size])=={'large','small'}
    fs=[em,'Dead seeds','Viable seeds','Unsuccessfully emerged seeds'];assert d[fs].sum(1).eq(d[total]).all()
    for s in fs:d[s+'_reported']=d[s]/d[total]
    d['emerged_nominal']=d[em]/15
    d['failed_or_dead_reported']=(d['Dead seeds']+d['Unsuccessfully emerged seeds'])/d[total]
    d['emerged_or_viable_reported']=(d[em]+d['Viable seeds'])/d[total]
    metrics=[s+'_reported' for s in fs]+['emerged_nominal','failed_or_dead_reported','emerged_or_viable_reported']
    ee=e[e[pot].isin(d[pot]) & e[day].le(62)].copy();assert ee[pot].nunique()==30
    tab=ee.pivot(index=pot,columns=day,values='Seedling emergence');assert tab.notna().all().all()
    d['early_stock_area_16_62']=d[pot].map(pd.Series(np.trapezoid(tab.to_numpy()/15,x=tab.columns.to_numpy(dtype=float),axis=1)/(62-16),index=tab.index));metrics+=['early_stock_area_16_62']
    rng=np.random.default_rng(20261124);ids=rng.integers(0,5,(50000,5));signs=np.asarray(list(itertools.product([-1,1],repeat=5)))
    def summarize(t):
        x=t.groupby([tank,size])[metrics].mean().unstack(size);assert len(x)==5 and not x.isna().any().any()
        out={}
        for k in metrics:
            a=x[k]['small'].values;b=x[k]['large'].values;dd=b-a;obs=dd.mean()
            out[k]={'small':float(a.mean()),'large':float(b.mean()),'delta':float(obs),'ci_conditional_bootstrap':np.quantile(dd[ids].mean(1),[.025,.975]).tolist(),'p_sign_flip':float(np.mean(np.abs((signs*dd).mean(1))>=abs(obs)-1e-12)),'tank_deltas':dd.tolist()}
        return out
    return {'source':'10.1371/journal.pone.0215157 S2/S3','source_artifact_sha256':HASH,'n_pots':30,'n_tanks':5,'fixed_depths_cm':[2,4,6],'n_reported_total_not_15':int(d[total].ne(15).sum()),'n_reported_total_below_15':int(d[total].lt(15).sum()),'n_reported_total_above_15':int(d[total].gt(15).sum()),'pooled_equal_depth_tank':summarize(d),'by_depth':{str(dep):summarize(d[d[depth].eq(dep)]) for dep in [2,4,6]},'limits':['Reported fate denominators differ from planted 15 in some pots. No planted-seed probability for such fates.','Five tanks are replication units; fixed depths are averaged, not independent studies. Bootstrap conditional on observed tanks; sign flips assume symmetry/exchangeability.','Viable un-emerged seeds are not future seedlings; no post-harvest followup or predator treatment.','Observation-window average shoot stock is not individual emergence time or predation exposure.','Response-open, not an independent validation or meta-analysis.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2)+'\n')
