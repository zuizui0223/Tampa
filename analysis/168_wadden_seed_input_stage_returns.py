#!/usr/bin/env python3
"""Original workbook audit and stage-specific seed-input contrasts; no causal biotic effect."""
import argparse, hashlib, io, itertools, json, zipfile
from pathlib import Path
import pandas as pd, numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
HASH='ad0097d3e14373bf0cb7babef0dd4aa26678d6bb97c7e5d94af5f7e534bc05e1'
def run(path,out):
    out.mkdir(exist_ok=True,parents=True)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read('manifest.json'))
        def source(doi):
            f=next(r for r in m if r.get('doi')==doi)['files'][0]
            b=z.read(f['file']);assert hashlib.sha256(b).hexdigest()==f['sha256'];return pd.ExcelFile(io.BytesIO(b)),f['sha256']
        a,sha1=source('10.34894/FHEZIR');c,sha2=source('10.34894/ZY6U9J');g,sha3=source('10.34894/FKSY2M')
        u=pd.read_excel(a,'UIthuizen2017');n=pd.read_excel(c,'2022data');y=pd.read_excel(c,'yearcomparison');r=pd.read_excel(g,'Recruitment_success&efficiency')
    assert len(u)==24 and u.plotnr.is_unique and u.groupby(['block','size','density']).size().eq(1).all()
    u['label_nominal_seeds']=u.density.map({'low':40,'high':400});u['implied_seeds']=u.plant_density/(1-u.loss/100);u['implied_nominal_seeds']=np.where(np.isclose(u.implied_seeds,40),40,np.where(np.isclose(u.implied_seeds,400),400,np.nan));assert u.implied_nominal_seeds.notna().all()
    u['nominal_matches_label']=u.implied_nominal_seeds.eq(u.label_nominal_seeds);assert np.isclose(u.loss,100*(1-u.plant_density/u.implied_nominal_seeds)).all()
    u['plants_per_1000_implied_seeds']=1000*u.plant_density/u.implied_nominal_seeds;u['plants_per_1000_label_seeds']=1000*u.plant_density/u.label_nominal_seeds
    u.to_csv(out/'uithuizen_label_audit.csv',index=False)
    assert len(n)==72 and len(y)==72 and not n.duplicated(['plot_ID','Month']).any() and not y.duplicated(['plot_ID','year']).any()
    k=['plot_ID','Block','Depth','Seed amount per inject','Seed amount per plot'];assert n.groupby('plot_ID')[k[1:]].nunique().eq(1).all().all()
    p=n[n.Month.eq('June')][k+['patches']].rename(columns={'patches':'June_patches'}).merge(n[n.Month.eq('August')][['plot_ID','patches','Cover m2']].rename(columns={'patches':'August_patches','Cover m2':'August22'}),on='plot_ID',validate='one_to_one')
    p['August22']=pd.to_numeric(p.August22,errors='raise');y['cover m2']=pd.to_numeric(y['cover m2'],errors='coerce');p=p.merge(y.pivot(index='plot_ID',columns='year',values='cover m2').reset_index(),on='plot_ID',validate='one_to_one');assert np.allclose(p.August22,p[2022])
    p=p.drop(columns=[2022]).rename(columns={2023:'August23','Seed amount per inject':'dose','Seed amount per plot':'seeds'});assert len(p)==36 and p.groupby(['Block','Depth','dose']).size().eq(1).all() and (p.seeds==16*p.dose).all()
    p['patches_per1000']=1000*p.June_patches/p.seeds;p['area22_per1000']=1000*p.August22/p.seeds;p['area23_per1000']=1000*p.August23/p.seeds;p['area_change']=p.August23-p.August22
    p.to_csv(out/'noltei_plot_history.csv',index=False)
    rng=np.random.default_rng(20261125)
    def pair_summary(x):
        x=np.asarray(x,dtype=float);assert np.isfinite(x).all();obs=float(x.mean());n=len(x);signs=np.array(list(itertools.product([-1,1],repeat=n)));bs=rng.choice(x,(30000,n),replace=True).mean(1)
        return dict(mean=obs,n_blocks=n,by_block=x.tolist(),ci_conditional_bootstrap95=np.quantile(bs,[.025,.975]).tolist(),p_exact_sign_flip=float(np.mean(np.abs((signs*x).mean(1))>=abs(obs)-1e-12)),n_positive=int((x>0).sum()),n_negative=int((x<0).sum()))
    def contrast(d,group,doses,outcomes):
        q=d.groupby(['block' if 'block' in d else 'Block',group])[outcomes].mean().unstack(group);o={}
        for v in outcomes:
            lo,hi=q[v][doses[0]],q[v][doses[1]];valid=lo.notna()&hi.notna();lo=lo[valid];hi=hi[valid]
            o[v]={'low_mean':float(lo.mean()),'high_mean':float(hi.mean()),'ratio_high_low':float(hi.mean()/lo.mean()) if lo.mean()!=0 else None,'difference':pair_summary(hi-lo)}
        return o
    u1=contrast(u,'implied_nominal_seeds',[40,400],['plant_density','plants_per_1000_implied_seeds']);u2=contrast(u,'label_nominal_seeds',[40,400],['plant_density','plants_per_1000_label_seeds'])
    prim=contrast(p,'dose',[5,20],['June_patches','patches_per1000','August22','area22_per1000']);fullblocks=p.groupby('Block').August23.apply(lambda s:s.notna().all());complete=p[p.Block.isin(fullblocks[fullblocks].index)]
    late=contrast(complete,'dose',[5,20],['June_patches','August22','August23','area22_per1000','area23_per1000','area_change']);obs=p[p.August23.notna()];missing=p[p.August23.isna()]
    changed={'pairs':len(obs),'mean22':float(obs.August22.mean()),'mean23':float(obs.August23.mean()),'ratio_total':float(obs.August23.sum()/obs.August22.sum()),'n_decrease':int(obs.area_change.lt(0).sum()),'n_increase':int(obs.area_change.gt(0).sum()),'n_same':int(obs.area_change.eq(0).sum()),'complete_blocks':int(fullblocks.sum()),'complete_block_equal_change':pair_summary(complete.groupby('Block').area_change.mean()),'missing_ids':missing.plot_ID.tolist(),'missing_needed_sum_for_no_total_decline':float(p.August22.sum()-obs.August23.sum())}
    models={'mean':[],'design':['logdose','Depth'],'June':['logJune'],'August22':['logArea22'],'design_June':['logdose','Depth','logJune'],'design_August22':['logdose','Depth','logArea22'],'June_August22':['logJune','logArea22']}
    p['logdose']=np.log(p.dose);p['logJune']=np.log1p(p.June_patches);p['logArea22']=np.log1p(p.August22)
    cv={}
    for alpha in [.1,1,10]:
        cv[str(alpha)]={}
        for name,cols in models.items():
            errs=[];fold=[]
            for block in sorted(obs.Block.unique()):
                train=p[(p.Block!=block)&p.August23.notna()];test=p[(p.Block==block)&p.August23.notna()];Y=np.sqrt(train.August23);actual=np.sqrt(test.August23);pred=np.repeat(Y.mean(),len(test)) if not cols else make_pipeline(StandardScaler(),Ridge(alpha=alpha)).fit(train[cols],Y).predict(test[cols]);e=(np.maximum(pred,0)-actual)**2;errs.extend(e);fold.append(float(np.mean(e)))
            cv[str(alpha)][name]={'mse_sqrt_m2':float(np.mean(errs)),'rmse':float(np.sqrt(np.mean(errs))),'fold_mse':fold}
    gg=r.groupby(['Plot_ID','Block','Restoration_scale_m²','Seeding_density/m²','Year']).Recruitment_success.mean().unstack().reset_index().rename(columns={'Block':'block','Seeding_density/m²':'dose','Restoration_scale_m²':'scale',2020:'G1',2021:'G2'});assert len(gg)==18 and gg.groupby(['block','dose','scale']).size().eq(1).all()
    gg['G1_per_injection']=gg.G1/gg.dose;gg['G2_per_injection']=gg.G2/gg.dose
    cross=contrast(gg,'dose',[10,50],['G1','G2','G1_per_injection','G2_per_injection'])
    res={'sources':{'2017':sha1,'2022_23':sha2,'2020_21':sha3},'uithuizen':{'n':len(u),'n_label_disagreements':int((~u.nominal_matches_label).sum()),'max_abs_error_implied_nominal':float(np.max(np.abs(u.implied_seeds-u.implied_nominal_seeds))),'inferred_label_sensitivity':u1,'original_label_sensitivity':u2},'noltei':{'n_plots':len(p),'n_blocks':int(p.Block.nunique()),'early_dose':prim,'late_complete_blocks_dose':late,'matched_change':changed,'cv':cv},'marina_2020_21':cross}
    (out/'results.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n');return res
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('artifact',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();run(a.artifact,a.out)
