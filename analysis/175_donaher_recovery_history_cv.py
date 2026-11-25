#!/usr/bin/env python3
"""Observed post-storm cover and disturbance-history prediction within one study."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
SHA='290285c4d1f3d3e93d75f648a6ecbece0cc28eb77d44370622f243ed842589e4'

def panel(d):
    # Pair endpoints within known color key before aggregation; all missing stay missing.
    v=d.dropna(subset=['POST','SPRING']).groupby(['Sample ID','Treatment','Disturbance Month','Elevation'],as_index=False)[['POST','SPRING']].mean()
    ids=v['Sample ID'].to_numpy(); n=v.groupby('Sample ID').SPRING.transform('size').to_numpy();w=1/n;y=v.SPRING.to_numpy()
    e=v[['Elevation']].to_numpy();p=v[['POST']].to_numpy();m=np.column_stack([v['Disturbance Month']==k for k in ['MAY','JUNE']]).astype(float);c=(v.Treatment=='CD').to_numpy(float)[:,None]
    designs={'elevation':(e,1),'state':(np.c_[e,p],2),'history':(np.c_[e,m,c],1),'state_month':(np.c_[e,p,m],2),'state_clam':(np.c_[e,p,c],2),'state_history':(np.c_[e,p,m,c],2),'state_history_interaction':(np.c_[e,p,m,c,m*c],2)}
    out={}
    for alpha in (.1,1.,10.):
        results={}
        for name,(X,nc) in designs.items():
            pred=np.empty(len(v))
            for i in sorted(set(ids)):
                te=ids==i;tr=~te;z=X.copy();sc=StandardScaler().fit(X[tr,:nc],sample_weight=w[tr]);z[:,:nc]=sc.transform(X[:,:nc]);pred[te]=Ridge(alpha=alpha).fit(z[tr],y[tr],sample_weight=w[tr]).predict(z[te])
            err=(pred-y)**2
            results[name]={'rmse':float(np.sqrt(np.average(err,weights=w))),'plot_mse':{str(int(i)):float(err[ids==i].mean()) for i in sorted(set(ids))}}
        out[str(alpha)]=results
    return {'matched_color_records':int(d[['POST','SPRING']].notna().all(1).sum()),'plot_months':len(v),'plots':len(set(ids)),'month_counts':v['Disturbance Month'].value_counts().to_dict(),'cv':out}

def analyze(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
    a=pd.read_excel(path,sheet_name=1);assert len(a)==374 and a['Sample ID'].nunique()==32
    assert len(a[a.Color.isna()])==2
    x=a.dropna(subset=['Color']);assert not x.duplicated(['Sample ID','Color','Timepoint']).any()
    assert x.groupby('Sample ID').Treatment.nunique().eq(1).all()
    elevation_conflicts=x.groupby('Sample ID').Elevation.nunique(); conflicts=[int(i) for i in elevation_conflicts[elevation_conflicts>1].index]
    assert conflicts==[15] and set(x[x['Sample ID']==15].Treatment)=={'C'}
    assert x.groupby(['Sample ID','Color'])['Disturbance Month'].nunique().eq(1).all()
    disturbed=x[x.Treatment.isin(['D','CD'])];assert disturbed.groupby('Sample ID').Elevation.nunique().eq(1).all()
    d=disturbed.pivot(index=['Sample ID','Color','Treatment','Disturbance Month','Elevation'],columns='Timepoint',values='Percent Cover').reset_index()
    assert len(d)==48 and d['Sample ID'].nunique()==16
    assert not set(x[x['Disturbance Month']=='NONE']['Sample ID'])&set(d['Sample ID'])
    s=d[d.Color.map({'BLUE':'JUNE','ORANGE':'MAY','PINK':'APRIL'})==d['Disturbance Month']]
    return {'status':'posthoc_within_site_plot_holdout_not_causal_or_carbohydrate_analysis','source_sha256':SHA,'source_doi':'10.5061/dryad.9cnp5hqh7','paper_doi':'10.1002/ecs2.3804','raw_rows':len(a),'disturbed_color_keys':len(d),'elevation_conflict_plot_ids_outside_analysis':conflicts,'panels':{'source_labels':panel(d),'color_label_agreement_sensitivity':panel(s)},'limits':['Paper describes two subplots and April/June disturbance, deposited sheet has three colors and April/May/June labels. Primary preserves labels; sensitivity restricts modal color-month correspondence without reassigning records. Not reconstruction of randomized timing.','POST is after Hurricane Dorian and after excavation, not a pre-excavation baseline. Elevation is a depth proxy. Spring cover includes both species, unlike fall cover. No individual or species recovery inferred.','Non-disturbed C/S plots separate; no within-plot undisturbed reference. Conditional on jointly observed POST/SPRING records; all color records within each plot-month averaged before modeling. Equal plot weights for training and scoring; whole plots held out. Standardize continuous predictors on training folds, ridge alpha fixed .1/1/10 sensitivity, no tuning.','Same site/season, small 16-plot sample. Prediction difference not statistical significance, not a causal clam or timing effect. No measured reserve data, physiological or external validation.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path('transmission_sources/donaher_2021/Exp2_Regrowth_All.xlsx'));a=p.parse_args();print(json.dumps(analyze(a.input),indent=2,sort_keys=True,allow_nan=False))
