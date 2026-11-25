#!/usr/bin/env python3
"""Paired endpoints in Chin et al. tropical seagrass experiment. One independent study.
Cumulative exposure proxy is trapezoidal time-average of measured depth means.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd
SHA='388d57cbe66ba8ba69253f867101db61cc2a3f23cdf4eb1257792966baaa1852'
KEY=['Tank','Unit_ID','Treatment','Light_Dark','Ambient_Sulfide','NoClam_Clam']
CONTEXTS=['LA','LS','DA','DS']
COLS=['final_sulfide','timeavg_sulfide','rhizome_growth','leaf_growth','net_shoot_change']
SIGNS=np.array([-1.,-1.,1.,1.])
def read(p):
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SHA:raise ValueError('source drift')
    return pd.read_excel(p,sheet_name=['Sulfide','Shoot','Rhizome','Leaf'])
def analyze(p):
    d=read(p);s,sh,r,l=[d[k] for k in ('Sulfide','Shoot','Rhizome','Leaf')]
    assert (len(s),len(sh),len(r),len(l))==(864,96,144,144)
    for a in d.values():
        assert a.Unit_ID.nunique()==48 and a.groupby('Unit_ID')[KEY].nunique().eq(1).all().all()
        assert a[KEY].drop_duplicates().groupby('Tank').Treatment.nunique().eq(8).all()
    assert not s.duplicated(KEY+['Date_Collected','Depth_cm']).any() and not sh.duplicated(KEY+['Status']).any()
    assert not r.duplicated(KEY+['Segment_Color']).any() and not l.duplicated(KEY+['Segment_Color']).any()
    assert set(s.Depth_cm)=={5,10} and s.Sulfide_uM.min()==10
    a=s.groupby(KEY+['Date_Collected','Status'],as_index=False).agg(sulfide=('Sulfide_uM','mean'),n=('Depth_cm','size'))
    assert a.n.eq(2).all() and a.groupby('Unit_ID').size().eq(9).all()
    vals=[]
    for k,g in a.groupby(KEY):
        g=g.sort_values('Date_Collected');assert list(g.Status)==['Initial']+['Interim']*7+['Final']
        days=(g.Date_Collected-g.Date_Collected.iloc[0]).dt.days.to_numpy();v=g.sulfide.to_numpy()
        integral=lambda j:float(np.sum(np.diff(days[j:])*(v[j:-1]+v[j+1:])/2)/(days[-1]-days[j]))
        vals.append(dict(zip(KEY,k),final_sulfide=v[-1],initial_sulfide=v[0],timeavg_sulfide=integral(1),timeavg_including_initial=integral(0)))
    x=pd.DataFrame(vals)
    q=sh.pivot(index=KEY,columns='Status',values='Shoot_Count').reset_index()
    assert (q.Initial>0).all();q['net_shoot_change']=(q.Final-q.Initial)/q.Initial
    rr=r[r.Include=='Y'].copy();rr['rhizome_growth']=rr.del_Tag_Length_cm*10/(rr.Date_Collected-rr.Date_Planted).dt.days/rr.Shoot_Count_Planting
    ll=l[l.Leaf_New_g.notna()].copy();ll['leaf_growth']=ll.Leaf_New_g*1000/(ll.Date_Collected-ll.Date_Punched).dt.days/ll.Shoot_Count_End
    assert len(rr)==len(ll)==119 and (rr.rhizome_growth>=0).all() and (ll.leaf_growth>0).all()
    x=x.merge(q,on=KEY,validate='one_to_one').merge(rr.groupby(KEY,as_index=False).rhizome_growth.mean(),on=KEY,validate='one_to_one').merge(ll.groupby(KEY,as_index=False).leaf_growth.mean(),on=KEY,validate='one_to_one')
    assert len(x)==48 and np.isfinite(x[COLS]).all().all()
    out={};infs=[];ests=[]
    for c in CONTEXTS:
        a,b=[x[x.Treatment==c+f].sort_values('Tank') for f in ('N','C')]
        assert list(a.Tank)==list(b.Tank)==list(range(1,7))
        aa,bb=[z[COLS].to_numpy(float) for z in (a,b)];ma,mb=aa.mean(0),bb.mean(0)
        assert (ma[:4]>0).all() and (mb[:4]>0).all()
        eff=np.r_[np.log(mb[:4]/ma[:4])*SIGNS,mb[4]-ma[4]]
        infl=np.column_stack(((bb[:,:4]/mb[:4]-aa[:,:4]/ma[:4])*SIGNS,bb[:,4]-aa[:,4]));infs.append(infl);ests.extend(eff)
        out[c]={'control_means':ma.tolist(),'clam_means':mb.tolist(),'percent_changes_positive_means':(100*(mb[:4]/ma[:4]-1)).tolist(),'net_shoot_change_difference_pp':100*eff[4],'effect_vector':eff.tolist(),'paired_tank_covariance':(np.cov(infl,rowvar=False)/6).tolist(),'tank_sign_counts_clam_minus_control':(bb>aa).sum(0).tolist(),'leave_one_tank_out':[np.r_[np.log(np.delete(bb,i,0).mean(0)[:4]/np.delete(aa,i,0).mean(0)[:4])*SIGNS,np.delete(bb,i,0).mean(0)[4]-np.delete(aa,i,0).mean(0)[4]].tolist() for i in range(6)]}
        out[c]['initial_sulfide_arm_means']=[float(z.initial_sulfide.mean()) for z in (a,b)]
        out[c]['timeavg_including_initial_arm_means']=[float(z.timeavg_including_initial.mean()) for z in (a,b)]
    C=np.cov(np.column_stack(infs),rowvar=False)/6
    return {'status':'one_study_matched_tank_multi_endpoint_pilot','paper_doi':'10.1111/1365-2745.13462','data_doi':'10.6084/m9.figshare.12574010.v1','source_sha256':SHA,'host_units':48,'tanks':6,'sulfide_rows':864,'floor_10_count':int((s.Sulfide_uM==10).sum()),'floor_10_final_count':int(((s.Sulfide_uM==10)&(s.Status=='Final')).sum()),'sulfide_dates':sorted(s.Date_Collected.dt.strftime('%Y-%m-%d').unique()),'live_segment_rows':119,'endpoint_order':COLS,'contrasts':out,'full_block_covariance_labels':[c+'|'+k for c in CONTEXTS for k in COLS],'full_block_covariance':C.tolist(),'limits':['Time average is trapezoidal interpolation of measured 5/10 cm depth means from first interim (Nov20) to final (Jan1), not continuous true sulfide dose. Initial included sensitivity is separate. Recorded 10uM detection floor retained, no imputation below it.','Rhizome elongation per day per initial shoot among source Include=Y segments, leaf new mass per day per final shoot among available live segments; mesocosm equal-weighted averages; survivor-conditioned growth, not whole-plant biomass or net production. Rhizome includes acclimation. Shoot count percentage change all 48 units; not a measured fitness rate.','Four context-specific paired contrasts within six complete tank blocks; rank of full 20x20 covariance at most 5. Small-sample delta covariance is descriptive. No independent contexts or general mediation or pooled cross-family effect.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path('transmission_sources/chin_2021/Chin_etal_2020_JEcol_data.xlsx'));a=p.parse_args();print(json.dumps(analyze(a.input),indent=2,sort_keys=True,allow_nan=False))
