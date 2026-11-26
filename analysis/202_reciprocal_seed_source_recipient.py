#!/usr/bin/env python3
"""Exact archive analysis. Counts are shoot density stocks, not marked seedlings."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
ARCHIVE='8026c12f40414c2f34c01966b37d1946915c30dccef808a35e8b20a20081976b'
HASHES={'MIE0B9':'19535dc2e92ce30e4ce2468d3f1b0442104e94599c438d467cd3b4aca4d6d5c1','C4GJFA':'f74a3ac0eb0d5f44514136272b97a47d51dafbf19080079e4f9757d1d04c187d','GUWZQA':'0b5276d295a01c831b0c468b8236e6888ced5769bcdab42b920654ff3583172e'}
Y='Total_shoot_density_Zm_m2'; STAGES=['Spring','Early Summer','Late Summer']; SITES=['NC1','NC2','NC10','VA1','VA3','VA5']
def records(d): return json.loads(d.to_json(orient='records',date_format='iso'))
def rho(x,y):
    if len(set(x))<2 or len(set(y))<2:return None
    return float(spearmanr(x,y).statistic)
def read(arc,slug):
    names=[n for n in arc.namelist() if n.startswith(slug+'_') and n.endswith('.tab')]
    assert len(names)==1
    b=arc.read(names[0]);assert hashlib.sha256(b).hexdigest()==HASHES[slug]
    assert b[:2]==b'PK' # original XLSX, Dataverse label .tab
    return pd.read_excel(io.BytesIO(b))
def decomp(d):
    mat=d.pivot(index=['Site_Number','ID'],columns='Rep',values='z')
    assert mat.shape==(d.Site_Number.nunique()*6,3) and not mat.isna().any().any()
    mean=d.z.mean(); predD=d.groupby('Site_Number').z.transform('mean');predO=d.groupby('ID').z.transform('mean');predCell=d.groupby(['Site_Number','ID']).z.transform('mean')
    ss={'destination':float(((predD-mean)**2).sum()),'source':float(((predO-mean)**2).sum()),'interaction':float(((predCell-predD-predO+mean)**2).sum()),'within_cell':float(((d.z-predCell)**2).sum())};total=float(((d.z-mean)**2).sum());assert np.isclose(sum(ss.values()),total)
    return {'ss':ss,'fraction':{k:v/total for k,v in ss.items()},'total':total}
def main(path):
    b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==ARCHIVE
    arc=zipfile.ZipFile(io.BytesIO(b));d=read(arc,'MIE0B9');t=read(arc,'C4GJFA');e=read(arc,'GUWZQA')
    assert len(d)==20 and d.Site.is_unique and set(d.Year)=={2023} and not d.isna().any().any()
    d['State']=d.Site.str[:2];assert d.groupby('State').size().to_dict()=={'NC':10,'VA':10}
    assert d.Seed_Bank_Percent_Viable.between(0,100).all()
    d['viable_proxy']=d.Seed_Bank_Density_m2*d.Seed_Bank_Percent_Viable/100
    v=['Mean_Cover_Zostera','Mean_ShootDensity_m2','Seed_Bank_Density_m2','Seed_Bank_Percent_Viable','viable_proxy']
    s=d.groupby('State')[v].agg(['mean','median']);states={state:{key:{k:float(s.loc[state,(key,k)]) for k in ['mean','median']} for key in v} for state in ['NC','VA']}
    assoc={k:{x:rho(g[x],g.viable_proxy) for x in v[:-1]} for k,g in [('all',d),*d.groupby('State')]}
    assert len(t)==702 and not t.duplicated(['Site_Number','Date','Quadrat_Number']).any() and set(t.Site_Number)==set(t.ID)==set(SITES)
    keys=['Site_Number','Quadrat_Number'];assert t.groupby(keys).ngroups==108 and t.groupby(keys)[['ID','Rep','Source_State','Source_Site']].nunique().max().max()==1
    assert t.groupby(['Site_Number','Date']).size().eq(18).all() and t.groupby(['Site_Number','Date','ID']).size().eq(3).all()
    assert (t[Y]>=0).all() and t.Percent_Cover_Zm.between(0,100).all()
    assert (t.ID.str[:2]==t.Source_State).all() and (t.Site_Number.str[:2]==t.Transplant_State).all()
    t['Date']=pd.to_datetime(t.Date);a=t[t.Date==t.groupby(['Site_Number','Season']).Date.transform('max')].copy();assert len(a)==324
    a['z']=np.log1p(a[Y]);a['positive']=(a[Y]>0).astype(int)
    stage=a.groupby(['Site_Number','Season']).agg(date=('Date','first'),n=(Y,'size'),mean=(Y,'mean'),positive=('positive','sum'),cover=('Percent_Cover_Zm','mean')).reset_index()
    means=a.groupby(['Season','Site_Number','ID'])[Y].mean().reset_index(name='mean')
    transitions=a.pivot(index=['Site_Number','ID','Quadrat_Number'],columns='Season',values=Y).reset_index();assert len(transitions)==108
    transitions['early_positive']=transitions['Early Summer']>0;transitions['terminal_positive']=transitions['Late Summer']>0
    decomposition={k:decomp(a[a.Season==k]) for k in STAGES}
    decomposition_va={k:decomp(a[(a.Season==k)&a.Site_Number.str.startswith('VA')]) for k in STAGES}
    transform_sensitivity={}
    for endpoint in [Y,'Percent_Cover_Zm']:
        for transform,fn in [('raw',lambda x:x),('log1p',np.log1p),('sqrt',np.sqrt)]:
            for stage_name in ['Spring','Late Summer']:
                frame=a[(a.Season==stage_name)&a.Site_Number.str.startswith('VA')].copy();frame['z']=fn(frame[endpoint]);transform_sensitivity[endpoint+'|'+transform+'|'+stage_name]=decomp(frame)
    origin_state=records(a.groupby(['Season','Transplant_State','Source_State']).agg(mean=(Y,'mean'),positive=('positive','sum'),n=(Y,'size')).reset_index())
    final=means[means.Season=='Late Summer'].pivot(index='Site_Number',columns='ID',values='mean').loc[SITES,SITES]
    spring=means[means.Season=='Spring'].pivot(index='Site_Number',columns='ID',values='mean').loc[SITES,SITES]
    early=means[means.Season=='Early Summer'].pivot(index='Site_Number',columns='ID',values='mean').loc[SITES,SITES]
    va=final.loc[['VA1','VA3','VA5']];donor=d.set_index('Site').loc[SITES];origin_2023=donor['viable_proxy'];raw_2023=donor.Seed_Bank_Density_m2
    source_association={dest:{'viable_proxy':rho(origin_2023,va.loc[dest]),'bank':rho(raw_2023,va.loc[dest]),'spring_density':rho(spring.loc[dest],va.loc[dest]),'early_density':rho(early.loc[dest],va.loc[dest])} for dest in va.index}
    source_rank_repro={f'{s}-{j}':rho(va.loc[s],va.loc[j]) for i,s in enumerate(va.index) for j in va.index[i+1:]}
    choice=[]
    for dest in va.index:
        train=va.drop(index=dest);pred=train.rank(axis=1,method='average').mean(axis=0)
        test=va.loc[dest];rows=[]
        for name,score in [('prior_viable_stock',origin_2023),('prior_total_stock',raw_2023),('other_receiving_meadow_rank',pred)]:
            selected=list(score[score==score.max()].index);value=float(test[selected].mean())
            rows.append({'rule':name,'chosen':selected,'density':value,'rank_rho':rho(score,test),'fraction_of_observed_best':value/float(test.max())})
        choice.append({'destination':dest,'observed_best':str(test.idxmax()),'best_density':float(test.max()),'rows':rows,'mean_all_sources':float(test.mean())})
    assert len(e)==144790 and set(e.Site)==set(SITES)
    e['DateTime']=pd.to_datetime(e.DateTime.astype(str).str.strip(),errors='raise');assert not e.duplicated(['Site','DateTime']).any()
    summer=e[(e.DateTime>='2024-06-01')&(e.DateTime<'2024-09-01')].copy();summer['day']=summer.DateTime.dt.floor('D')
    daily=summer.groupby(['Site','day']).agg(valid=('Temp','count'),mean=('Temp','mean'),maximum=('Temp','max'),hot28=('Temp',lambda x:float((x>=28).sum()/4)),hot30=('Temp',lambda x:float((x>=30).sum()/4))).reset_index()
    daily['valid_day']=daily.valid>=90
    coverage=[]
    for site,g in e.groupby('Site'):
        days=daily[(daily.Site==site)&daily.valid_day]; total=daily[daily.Site==site]
        coverage.append({'site':site,'n_rows':len(g),'missing_temp':int(g.Temp.isna().sum()),'missing_PAR':int(g.PAR.isna().sum()),'summer_days_present':len(total),'summer_valid_days':len(days),'mean_valid_day_temp':float(days['mean'].mean()) if len(days) else None,'mean_hot28_hours':float(days.hot28.mean()) if len(days) else None,'mean_hot30_hours':float(days.hot30.mean()) if len(days) else None})
    shared=set.intersection(*[set(daily[(daily.Site==site)&daily.valid_day].day) for site in SITES])
    common_coverage=records(daily[daily.day.isin(shared)].groupby('Site').agg(n_days=('day','size'),mean_temp=('mean','mean'),hot28=('hot28','mean'),hot30=('hot30','mean')).reset_index())
    out={'archive':ARCHIVE,'source_hashes':HASHES,'audit':{'summary_sites':len(d),'columns_2023':list(d.columns[:-2]),'transplant_rows':len(t),'plots':t.groupby(keys).ngroups,'season_selected_rows':len(a),'height_missing_positive':int(t.loc[t[Y]>0,'Height'].isna().sum()),'repro_greater_than_total':int((t.Repro_m2>t[Y]).sum()),'cover_positive_zero_shoot':int(((t.Percent_Cover_Zm>0)&(t[Y]==0)).sum()),'env_rows':len(e)},'state_2023':states,'site_2023':records(d),'rank_associations_2023':assoc,'stage_summary':records(stage),'source_destination_stage_means':records(means),'plot_landmarks':records(transitions),'decomposition':decomposition,'decomposition_va':decomposition_va,'transform_sensitivity_va':transform_sensitivity,'origin_state':origin_state,'source_associations_va':source_association,'source_rank_agreement_va':source_rank_repro,'donor_rules_va':choice,'temperature_coverage':coverage,'temperature_common_days':common_coverage,'limits':['2023 workbook contains 20 site summaries only, no flowering counts or raw quadrat samples. Viable proxy product of reported density and percentage, not actual viable density or collected seed-lot viability; cross-year observational linkage.','2024 data complete site x source x three quadrats at each visit; last recorded visit per reported season (not identical dates). Shoot count density includes clonal growth; no tagged seed survival or dose denominator. Plot randomization, initial seed input, and equivalence of planting/viability not inferred from workbook.','Descriptive balanced two-way sums of squares on log1p stock; 6 sites and 6 sources, no general inference. Zero final density in NC sites not proof of mortality or permanent extinction. VA-only source ranking conditioned on observed recipient outcome; no validated management rule.','Temperature summaries restricted to days with >=90 observed readings, different coverage; hot hours conditional on recorded times and regular 15-min interval, no causation; no temporal interpolation. PAR not fitted. Repro_m2 inconsistency and height missingness excluded from models. No animal treatment, no measured dispersal, no meta-analysis.']}
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('archive');ap.add_argument('output');a=ap.parse_args();out=main(a.archive);Path(a.output).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['site_2023','source_destination_stage_means','plot_landmarks']},indent=2,allow_nan=False))
