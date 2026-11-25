#!/usr/bin/env python3
"""Observed plot/subplot cover trajectories and finite missing-data bounds.
Do not infer source month labels from plot color or the published design.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

FILES={
    'Exp2_Regrowth_All.xlsx':'290285c4d1f3d3e93d75f648a6ecbece0cc28eb77d44370622f243ed842589e4',
    'Exp2_BiomassCores_All.xlsx':'964eb013048f607b61d9e6a9d0d68caf973dc13319c329536c0fd4ebd2d39091',
}
TIME=['PRE','POST','OCTOBER','SPRING']
KEY=['Sample ID','Color','Treatment','Disturbance Month']

def read(root,k):
    p=root/k
    if hashlib.sha256(p.read_bytes()).hexdigest()!=FILES[k]: raise ValueError('source drift '+k)
    return pd.read_excel(p,sheet_name=1)

def describe(a):
    a=np.asarray(a,float);v=a[np.isfinite(a)]
    return {'expected':len(a),'observed':len(v),'mean':float(v.mean()) if len(v) else None,'median':float(np.median(v)) if len(v) else None}

def analyze(root):
    d=read(root,'Exp2_Regrowth_All.xlsx');b=read(root,'Exp2_BiomassCores_All.xlsx')
    assert len(d)==374 and d['Sample ID'].nunique()==32
    assert d.groupby('Sample ID').Treatment.nunique().eq(1).all()
    assert d.groupby('Treatment')['Sample ID'].nunique().eq(8).all()
    assert d['Percent Cover'].dropna().between(0,100).all()
    unknown=d[d.Color.isna()];assert len(unknown)==2 and len(unknown.drop_duplicates())==1
    x=d[d.Color.notna()].copy();assert len(x)==372 and not x.duplicated(['Sample ID','Color','Timepoint']).any()
    assert x.groupby(['Sample ID','Color'])['Disturbance Month'].nunique().eq(1).all()
    p=x.pivot(index=KEY,columns='Timepoint',values='Percent Cover').reset_index()
    assert len(p)==96 and p.groupby('Sample ID').Color.nunique().eq(3).all()
    assert set(p['Disturbance Month'])=={'APRIL','MAY','JUNE','NONE'}
    # All recorded color keys remain in the panel; absent visits and blank cover remain missing.
    plots=p.groupby(['Sample ID','Treatment','Disturbance Month'])[TIME].mean().reset_index()
    lo=p.copy();hi=p.copy();lo[TIME]=lo[TIME].fillna(0);hi[TIME]=hi[TIME].fillna(100)
    lows=lo.groupby(['Sample ID','Treatment','Disturbance Month'])[TIME].mean().reset_index()
    highs=hi.groupby(['Sample ID','Treatment','Disturbance Month'])[TIME].mean().reset_index()
    summary={}
    for (tr,month),g in plots.groupby(['Treatment','Disturbance Month']):
        k=f'{tr}|{month}';a=lows[(lows.Treatment==tr)&(lows['Disturbance Month']==month)];z=highs[(highs.Treatment==tr)&(highs['Disturbance Month']==month)]
        summary[k]={t:{**describe(g[t]),'all_key_mean_lower':float(a[t].mean()),'all_key_mean_upper':float(z[t].mean())} for t in TIME}
    contrasts={}
    for month in ('APRIL','MAY','JUNE'):
        a=summary['CD|'+month]['SPRING'];z=summary['D|'+month]['SPRING']
        contrasts[month]={'observed_mean_difference_pp':a['mean']-z['mean'],'bounded_difference_pp':[a['all_key_mean_lower']-z['all_key_mean_upper'],a['all_key_mean_upper']-z['all_key_mean_lower']]}
    j=p[p['Disturbance Month']=='JUNE'].copy()
    assert len(j)==13 and j.groupby('Treatment')['Sample ID'].nunique().to_dict()=={'CD':7,'D':6}
    a,z=[j[j.Treatment==t].SPRING.dropna().to_numpy() for t in ('CD','D')]
    loo=[float(np.delete(a,i).mean()-z.mean()) for i in range(len(a))]+[float(a.mean()-np.delete(z,i).mean()) for i in range(len(z))]
    severe=j[j.POST<=10];complete=j.dropna(subset=['PRE','SPRING']).copy();complete['gain']=complete.SPRING-complete.PRE
    gap=plots.pivot(index=['Sample ID','Treatment'],columns='Disturbance Month',values='SPRING').dropna(subset=['APRIL','JUNE']).reset_index();gap['gap']=gap.APRIL-gap.JUNE
    assert len(gap)==9
    pair={t:describe(g.gap) for t,g in gap.groupby('Treatment')}
    # The biomass workbook has no usable sampling date for time-resolved predictor linkage.
    bk=['Plot Number','Year','Location','Disturbance Date','Species']
    assert len(b)==256 and set(b.Year)=={2019}
    biomass={'rows':len(b),'year_labels':sorted(int(v) for v in b.Year.unique()),'duplicate_context_rows_beyond_first':int(b.duplicated(bk).sum()),'status':'STOP_temporal_biomass_to_recovery_join'}
    return {'status':'source_month_exploratory_cover_diagnostic_not_original_ANCOVA','source_hashes':FILES,'study_doi':'10.1002/ecs2.3804','data_doi':'10.5061/dryad.9cnp5hqh7','raw_rows':len(d),'plot_count':32,'known_color_panel_keys':len(p),'known_color_rows':len(x),'blank_cover_rows':int(x['Percent Cover'].isna().sum()),'absent_color_time_rows':int(len(p)*len(TIME)-len(x)),'unlabeled_duplicate_rows_excluded':len(unknown),'spring_recorded_values':sorted(p.SPRING.dropna().unique().tolist()),'month_date_counts':{k:{str(j):int(n) for j,n in v['Disturbance Date'].value_counts(dropna=False).items()} for k,v in x.groupby('Disturbance Month')},'plot_summary':summary,'spring_contrasts':contrasts,'june_leave_one_observed_plot_out_difference_range':[min(loo),max(loo)],'june_post_at_most_10_sensitivity':{t:describe(g.SPRING) for t,g in severe.groupby('Treatment')},'june_pre_spring_complete':{t:{k:describe(g[k]) for k in ('PRE','SPRING','gain')} for t,g in complete.groupby('Treatment')},'same_plot_april_minus_june_spring':pair,'same_plot_gap_difference_CD_minus_D':pair['CD']['mean']-pair['D']['mean'],'biomass_source_audit':biomass,'limits':['Published experiment describes two subplots and April/June disturbances; deposited cover sheet has three color labels per plot and April/May/June month labels. June actual date is missing. Use source labels, not a reconstruction of the published timing design.','Two identical unlabeled SPRING rows excluded rather than assigning to colors. Missing values not assigned zero except explicit [0,100] bounds; absent color-time cells included in bounds. Equal mean of observed colors within plot/month, then equal plot weights.','September PRE means pre-hurricane, not pre-disturbance. Fall cover is predominantly Halodule and spring mixed-species cover; not same-species recovery. Same-plot paired gap is descriptive, not a randomized timing effect. Post<=10 restriction is post-treatment selected sensitivity.','Bounds are deterministic missing-data sensitivity, not uncertainty intervals or proof of significance. No carbon reserves measured. Biomass sheet year all 2019, 86 duplicate keys; no unique before/after biomass join. No causal mediator or new independent experiment.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('transmission_sources/donaher_2021'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
