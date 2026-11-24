#!/usr/bin/env python3
"""Posthoc paired-stage audit; conditional on the same experiment, no mediation."""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
CHIN='chin_2021/Chin_etal_2020_JEcol_data.xlsx'
FIELD7='lucinid_2020/Table_7_Field_experiment_porewater_nutrient_and_sulfide_concentrations.txt'
FIELD9='lucinid_2020/Table_9_Field_experiment_Z_noltei_AND_L_orbiculatus_data_per_experimental_plot.txt'
HASHES={CHIN:'388d57cbe66ba8ba69253f867101db61cc2a3f23cdf4eb1257792966baaa1852',FIELD7:'68ae3ffbd9773f6aa51cf3aa1dce5423081da75da172fe86ef3643d8109a7d4b',FIELD9:'203771a3f17fb412d2585659263095befdc5c385d4a50072cfbe7f3c8c155094'}
KEY=['Tank','Unit_ID','Treatment','Light_Dark','Ambient_Sulfide','NoClam_Clam']
CONTEXTS=['LA','LS','DA','DS']
END=['timeavg_sulfide','rhizome_S','leaf_S','rhizome_growth','leaf_growth','shoot_change']
def verified(root,k):
    p=root/k
    assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[k]
    return p

def chin(root):
    d=pd.read_excel(verified(root,CHIN),sheet_name=['Sulfide','Sulfur','Rhizome','Leaf','Shoot','Nutrients','Clams'])
    s,ts,r,l,sh,nu,cl=[d[k] for k in ['Sulfide','Sulfur','Rhizome','Leaf','Shoot','Nutrients','Clams']]
    for a in [s,ts,r,l,sh,nu]:
        assert a.Unit_ID.nunique()==48 and a.groupby('Unit_ID')[KEY].nunique().eq(1).all().all()
    assert len(s)==864 and len(ts)==255 and not ts.duplicated(KEY+['Segment_Color','Tissue']).any()
    assert not s.duplicated(KEY+['Date_Collected','Depth_cm']).any()
    a=s.groupby(KEY+['Date_Collected','Status'],as_index=False).agg(v=('Sulfide_uM','mean'),n=('Depth_cm','size'))
    assert a.n.eq(2).all() and a.groupby('Unit_ID').size().eq(9).all()
    rows=[]
    for k,g in a.groupby(KEY):
        g=g.sort_values('Date_Collected');assert list(g.Status)==['Initial']+['Interim']*7+['Final']
        days=(g.Date_Collected-g.Date_Collected.iloc[0]).dt.days.to_numpy()[1:];v=g.v.to_numpy()[1:]
        rows.append(dict(zip(KEY,k),timeavg_sulfide=np.sum(np.diff(days)*(v[:-1]+v[1:])/2)/(days[-1]-days[0])))
    x=pd.DataFrame(rows)
    rr=r[r.Include=='Y'].copy();rr['rhizome_growth']=rr.del_Tag_Length_cm*10/(rr.Date_Collected-rr.Date_Planted).dt.days/rr.Shoot_Count_Planting
    ll=l[l.Leaf_New_g.notna()].copy();ll['leaf_growth']=ll.Leaf_New_g*1000/(ll.Date_Collected-ll.Date_Punched).dt.days/ll.Shoot_Count_End
    assert len(rr)==len(ll)==119
    assert not ts[ts.Dead=='Y'].PctS.notna().any()
    tissue=ts.groupby(KEY+['Tissue']).PctS.mean().unstack().reset_index().rename(columns={'rhizome':'rhizome_S','leaf':'leaf_S'})
    q=sh.pivot(index=KEY,columns='Status',values='Shoot_Count').reset_index();q['shoot_change']=(q.Final-q.Initial)/q.Initial
    for y in [tissue,rr.groupby(KEY,as_index=False).rhizome_growth.mean(),ll.groupby(KEY,as_index=False).leaf_growth.mean(),q]:
        x=x.merge(y,on=KEY,validate='one_to_one')
    assert len(x)==48 and np.isfinite(x[END]).all().all() and (x[END[:3]]>0).all().all()
    effects={};paired=[]
    for context in CONTEXTS:
        a,b=[x[x.Treatment==context+f].sort_values('Tank') for f in ['N','C']]
        assert list(a.Tank)==list(b.Tank)==list(range(1,7))
        av,bv=[z[END].to_numpy(float) for z in (a,b)]
        r0,r1=[v.mean(0) for v in (av,bv)]
        delta=bv-av
        effects[context]={'control_means':r0.tolist(),'clam_means':r1.tolist(),'percent_change_first_five':(100*(r1[:5]/r0[:5]-1)).tolist(),'shoot_change_difference_pp':100*(r1[5]-r0[5]),'positive_tanks':(delta>0).sum(0).tolist(),'negative_tanks':(delta<0).sum(0).tolist(),'raw_difference':delta.mean(0).tolist(),'raw_difference_covariance':(np.cov(delta,rowvar=False)/6).tolist()}
        for tank,aa,bb in zip(a.Tank,av,bv):
            paired.append(dict(tank=int(tank),context=context,log_bulk_relief=math.log(aa[0]/bb[0]),log_bulk_residual=math.log(bb[0]),log_rhizome_relief=math.log(aa[1]/bb[1]),log_leaf_relief=math.log(aa[2]/bb[2]),rhizome_delta=bb[3]-aa[3],leaf_delta=bb[4]-aa[4],shoot_delta=bb[5]-aa[5]))
    # Add predictive increments, in original endpoint units, on held-out tank pairs.
    # These are simultaneous end-point diagnostics, NOT prospective predictions.
    z=pd.DataFrame(paired).sort_values(['tank','context']);ctx=np.array([[int(c==k) for k in CONTEXTS] for c in z.context],float)
    models={'context_only':[],'bulk_relief':['log_bulk_relief'],'bulk_relief_residual':['log_bulk_relief','log_bulk_residual'],'tissue_relief':['log_rhizome_relief','log_leaf_relief'],'bulk_and_tissue':['log_bulk_relief','log_bulk_residual','log_rhizome_relief','log_leaf_relief']}
    cv={}
    for yname in ['rhizome_delta','leaf_delta','shoot_delta']:
        y=z[yname].to_numpy(float);results={}
        for name,fields in models.items():
            X=np.column_stack([ctx,z[fields].to_numpy(float)]);pred=np.empty(len(z))
            for tank in range(1,7):
                test=z.tank.to_numpy()==tank; train=~test
                beta,_,rank,_=np.linalg.lstsq(X[train],y[train],rcond=None)
                assert rank==X.shape[1]
                pred[test]=X[test]@beta
            losses=(pred-y)**2;results[name]={'rmse':float(np.sqrt(losses.mean())),'per_tank_mse':[float(losses[z.tank==tank].mean()) for tank in range(1,7)]}
        base=results['context_only']['rmse']
        for v in results.values():v['rmse_ratio_to_context_only']=v['rmse']/base
        cv[yname]=results
    return {'host_units':48,'tanks':6,'tissue_records':len(ts),'missing_pctS':int(ts.PctS.isna().sum()),'dead_rhizomes_without_pctS':int((ts.Dead=='Y').sum()),'min_available_tissue_records_per_unit':int(ts.groupby(['Unit_ID','Tissue']).PctS.count().min()),'endpoints':END,'contexts':effects,'cv':cv,'paired_vectors':paired}

def field(root):
    a=pd.read_csv(verified(root,FIELD7),sep=r'\s+');b=pd.read_csv(verified(root,FIELD9),sep=r'\s+')
    key=['Site','Block','Experimental_group','Plot_ID','OM_addition','Loripes_addition'];x=a.merge(b,on=key,validate='one_to_one')
    assert len(x)==24 and x.Block.nunique()==6
    x['plant_total']=x[['Zn_leaf_DW_g_per_core','Zn_rhizome_DW_g_per_core','Zn_root_DW_g_per_core']].sum(axis=1)
    cols=['Loripes_density_per_core','Loripes_total_DW_g_per_core','Sulfide_micromol_per_L','Fsulfide','SS_leaves','plant_total']
    out={}
    for stress in ['C','OM']:
        a,b=[x[(x.OM_addition==stress)&(x.Loripes_addition==f)].sort_values('Block') for f in ['C','L']]
        assert len(a)==len(b)==6 and list(a.Block)==list(b.Block)
        a,b=[v[cols].to_numpy(float) for v in [a,b]]; assert np.isfinite(a).all() and np.isfinite(b).all()
        m,n=a.mean(0),b.mean(0);delta=b-a
        out[stress]={'control_means':m.tolist(),'addition_means':n.tolist(),'percent_change':(100*(n/m-1)).tolist(),'positive_blocks':(delta>0).sum(0).tolist(),'negative_blocks':(delta<0).sum(0).tolist(),'paired_difference_covariance':(np.cov(delta,rowvar=False)/6).tolist()}
    return {'host_plots':24,'blocks':6,'endpoints':cols,'contexts':out}

def analyze(root):
    return {'status':'posthoc_stage_diagnostic_not_causal_or_pooled_meta','source_hashes':HASHES,'chin2021':chin(root),'van_der_geest2020':field(root),'limits':['Chin total tissue S (% DW) is not isotope-estimated sulfide intrusion, nor a measure of free toxic sulfide. Both tissue and growth are survivor conditioned; no imputation for dead rhizomes.','Field Fsulfide is isotope-estimated fraction of leaf S from sediment sulfide; SS_leaves is sediment-derived S as % dry weight. Not comparable to Chin total S.','CV uses differences from paired tank contrasts; all four contexts in each held-out tank, fixed context indicators and specified simultaneous process covariates. No prospective prediction, no independent external validation, no causal mediation. Small posthoc comparison on six tanks, overlapping training sets.','No pooling of species, endpoint units, or independent context rows. Field addition increased clam biomass even where counts were similar; count-only conclusion of failed manipulation is not justified.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('transmission_sources'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
