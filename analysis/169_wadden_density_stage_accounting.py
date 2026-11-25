#!/usr/bin/env python3
"""Original workbook, matched density contrasts; allocation scenarios not observed comparisons."""
import argparse, hashlib, io, itertools, json, zipfile
from pathlib import Path
import numpy as np,pandas as pd
HASH='ad0097d3e14373bf0cb7babef0dd4aa26678d6bb97c7e5d94af5f7e534bc05e1'
DOI='10.34894/FKSY2M'
def run(path,out):
    out.mkdir(parents=True,exist_ok=True)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read('manifest.json')); f=next(x for x in m if x.get('doi')==DOI)['files'][0]
        raw=z.read(f['file']);assert hashlib.sha256(raw).hexdigest()==f['sha256']
        wb=pd.ExcelFile(io.BytesIO(raw));r=pd.read_excel(wb,'Recruitment_success&efficiency');pl=pd.read_excel(wb,'Plantdata_August2020')
    keys=['Plot_ID','Block','Restoration_scale_m²','Seeding_density/m²']
    assert len(r)==144 and len(pl)==90 and not r.duplicated(['Plot_ID','Year','Replicate']).any() and not pl.duplicated(['Plot_ID','Replicate_plant']).any()
    assert r.groupby(['Plot_ID','Year']).size().eq(4).all() and pl.groupby('Plot_ID').size().eq(5).all()
    p=r.groupby(keys+['Year']).Recruitment_success.mean().unstack().reset_index().rename(columns={2020:'G1',2021:'G2'})
    p=p.merge(pl.groupby(keys)['Spathes/plant'].mean().rename('spathes').reset_index(),on=keys,validate='one_to_one').rename(columns={keys[2]:'area',keys[3]:'dose'})
    assert len(p)==18 and p.groupby(['Block','area','dose']).size().eq(1).all() and (p[['G1','G2','spathes']]>0).all().all()
    p['spathes_proxy']=p.G1*p.spathes;p['conversion']=p.G2/p.spathes_proxy;p['renewal']=p.G2/p.G1
    p['injections']=p.area*p.dose;p['G1_per_inj']=p.G1/p.dose;p['G2_per_inj']=p.G2/p.dose
    cols=['G1','G2','spathes','spathes_proxy','conversion','renewal','G1_per_inj','G2_per_inj']
    q=p.pivot(index=['Block','area'],columns='dose',values=cols)
    logd=pd.DataFrame({v:np.log(q[v][50]/q[v][10]) for v in cols})
    assert np.allclose(logd.G2,logd.G1+logd.spathes+logd.conversion)
    assert np.allclose(logd.renewal,logd.spathes+logd.conversion)
    assert np.allclose(logd.G2_per_inj,logd.G2-np.log(5))
    def summarize(d):
        b=d.groupby('Block').mean();n=len(b);assert n==3
        ids=np.asarray(list(itertools.product(range(n),repeat=n)));z=b.to_numpy();s=z[ids].mean(1)
        signs=np.asarray(list(itertools.product([-1,1],repeat=n)));summary={}
        for j,v in enumerate(d.columns):
            est=z[:,j].mean();bs=s[:,j];obs=d[v]
            summary[v]={'log_ratio':float(est),'geometric_high_low_ratio':float(np.exp(est)),'conditional_block_bootstrap95_ratio':np.exp(np.quantile(bs,[.025,.975])).tolist(),'block_log_ratios':z[:,j].tolist(),'n_pairs_positive':int((obs>0).sum()),'n_pairs_negative':int((obs<0).sum()),'n_pairs':len(obs),'sign_flip_p_block':float(np.mean(np.abs((signs*z[:,j]).mean(1))>=abs(est)-1e-12))}
        return {'metrics':summary,'G1_elasticity':float(b.G1.mean()/np.log(5)),'G2_elasticity':float(b.G2.mean()/np.log(5)),'delta_elasticity':float(b.renewal.mean()/np.log(5))}
    contrast={'all':summarize(logd),'by_area':{str(a):summarize(logd.xs(a,level='area',drop_level=False)) for a in [4,40,400]},'40_and_400':summarize(logd[logd.index.get_level_values('area').isin([40,400])])}
    budget=20000;scenario=[]
    for (a,d),v in p.groupby(['area','dose']):
        assert budget%(a*d)==0
        scenario.append({'area_per_plot':int(a),'injections_per_m2':int(d),'number_of_plots':int(budget/(a*d)),'total_nominal_area_m2':budget/d,'predicted_G1_density':float(v.G1.mean()),'predicted_G2_density':float(v.G2.mean()),'scenario_G1_total':float(budget*v.G1.mean()/d),'scenario_G2_total':float(budget*v.G2.mean()/d),'G2_per_injection':float(v.G2_per_inj.mean()),'G2_per_injection_by_block':v.sort_values('Block').G2_per_inj.tolist()})
    for x in scenario:
        x['dominated_on_G2_density_and_efficiency']=any(y['predicted_G2_density']>=x['predicted_G2_density'] and y['G2_per_injection']>=x['G2_per_injection'] and (y['predicted_G2_density']>x['predicted_G2_density'] or y['G2_per_injection']>x['G2_per_injection']) for y in scenario)
    outres={'status':'executed original-data descriptive contrast; scenarios conditional on additive noninteracting replication','source':{'doi':DOI,'artifact_sha256':HASH,'workbook_sha256':f['sha256']},'audit':{'plots':len(p),'blocks':3,'recruitment_rows':len(r),'sampled_plants':len(pl),'equal_total_injections_design_exists':bool(p[['area','dose','injections']].drop_duplicates().injections.duplicated().any())},'contrasts':contrast,'fixed_injection_budget':budget,'scenarios':scenario,'limits':['Spathe proxy is not actual seed output; no causal mediation.','Three blocks, response-open comparisons, no independent replication.','No animal treatment; density and spacing co-vary; no equal-budget treatment comparison.','Allocation scenarios assume same observed plot means in independent replicated patches; no forecast validation or area constraint.']}
    p.to_csv(out/'plot_stage_data.csv',index=False);logd.to_csv(out/'paired_log_ratios.csv');pd.DataFrame(scenario).to_csv(out/'fixed_budget_scenarios.csv',index=False);(out/'results.json').write_text(json.dumps(outres,indent=2,allow_nan=False)+'\n');return outres
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('artifact',type=Path);a.add_argument('--out',type=Path,required=True);v=a.parse_args();run(v.artifact,v.out)
