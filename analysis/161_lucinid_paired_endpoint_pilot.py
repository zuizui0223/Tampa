#!/usr/bin/env python3
"""Three-study lucinid paired endpoint pilot. No cross-study pooled causal effect."""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
FILES={
 "lucinid_2012/Experimental_data.xlsx":"f59e66910a97daef609b275772f319b8c7f63b98e3e1b05644c3d37499ade7ac",
 "lucinid_2020/Table_7_Field_experiment_porewater_nutrient_and_sulfide_concentrations.txt":"68ae3ffbd9773f6aa51cf3aa1dce5423081da75da172fe86ef3643d8109a7d4b",
 "lucinid_2020/Table_9_Field_experiment_Z_noltei_AND_L_orbiculatus_data_per_experimental_plot.txt":"203771a3f17fb412d2585659263095befdc5c385d4a50072cfbe7f3c8c155094",
 "de_fouw_2022/data.total.csv":"4ba710916d5f4a4d304d83daba1c91bb4c3309edbb44b72e8148f23fb35f1c8f"}
SIGN=np.array([-1.,1.])
def read(root,i):
    path=root/list(FILES)[i]
    if hashlib.sha256(path.read_bytes()).hexdigest()!=FILES[list(FILES)[i]]:raise ValueError("source drift: "+str(path))
    return path
def arm(x,cols):
    a=x[cols].to_numpy(float)
    if not np.isfinite(a).all() or (a<=0).any():raise ValueError("nonpositive/missing endpoint")
    return a
def effect(a,b):
    ma=a.mean(0);mb=b.mean(0)
    v=SIGN*np.log(mb/ma)
    return v
def independent(a,b):
    # Conditional delta-method sampling covariance of oriented log ratios.
    ma=a.mean(0);mb=b.mean(0)
    return np.outer(SIGN,SIGN)*(np.cov(a,rowvar=False)/len(a)/np.outer(ma,ma)+np.cov(b,rowvar=False)/len(b)/np.outer(mb,mb))
def row(a,b):
    v=effect(a,b);m=a.mean(0);n=b.mean(0)
    return {"control_n":len(a),"treated_n":len(b),"control_means":m.tolist(),"treated_means":n.tolist(),"oriented_log_response_ratios":v.tolist(),"percent_change":((n/m-1)*100).tolist()}
def study2012(root):
    p=read(root,0);a=pd.read_excel(p,"Abiotic");b=pd.read_excel(p,"Zostera")
    assert len(a)==40 and len(b)==20 and set(a.Zostera)=={"C","Z"} and set(a.Loripes)=={"C","L"}
    a=a[a.Zostera=="Z"].copy();a["Zostera_Loripes"]=np.where(a.Loripes=="L","ZL","Z")
    x=b.merge(a,on=["Zostera_Loripes","Sulfide","#"],validate="one_to_one")
    assert len(x)==20 and not x[["Shoot_biomass","Rhizome_bioamss","Root_biomass"]].isna().any().any()
    x["total"]=x[["Shoot_biomass","Rhizome_bioamss","Root_biomass"]].sum(axis=1)
    out={}
    for stress in ("C","S"):
        a,b=[arm(x[(x.Sulfide==stress)&(x.Loripes==f)],["Sulfide_t10","total"]) for f in ("C","L")]
        assert len(a)==len(b)==5
        r=row(a,b);C=independent(a,b)
        r["conditional_delta_covariance_assuming_sheet_replicate_keys_match"]=C.tolist()
        r["conditional_delta_se"]=np.sqrt(C.diagonal()).tolist()
        out[stress]=r
    return {"doi":"10.1126/science.1219973","host_units":20,"all_abiotic_units":40,"contrasts":out,
      "design":"five independently assigned columns per cell, one shared basin; treatment + replicate number used to align two workbook sheets. Pairing assumption for covariance, not independently validated specimen IDs. T10 sulfide and final shoot+rhizome+root dry biomass. Do not pair equal replicate numbers across arms."}
def study2020(root):
    p,q=read(root,1),read(root,2)
    a=pd.read_csv(p,sep=r"\s+");b=pd.read_csv(q,sep=r"\s+")
    keys=["Site","Block","Experimental_group","Plot_ID","OM_addition","Loripes_addition"]
    x=a.merge(b,on=keys,validate="one_to_one")
    assert len(a)==len(b)==len(x)==24 and x.Plot_ID.nunique()==24 and x.Block.nunique()==6
    assert not x[["Zn_leaf_DW_g_per_core","Zn_rhizome_DW_g_per_core","Zn_root_DW_g_per_core"]].isna().any().any()
    x["total"]=x[["Zn_leaf_DW_g_per_core","Zn_rhizome_DW_g_per_core","Zn_root_DW_g_per_core"]].sum(axis=1)
    out={};influences=[]
    for stress in ("C","OM"):
        a,b=[x[(x.OM_addition==stress)&(x.Loripes_addition==f)].sort_values("Block") for f in ("C","L")]
        assert len(a)==len(b)==6 and list(a.Block)==list(b.Block)
        aa,bb=[arm(z,["Sulfide_micromol_per_L","total"]) for z in (a,b)]
        r=row(aa,bb)
        V=(bb/bb.mean(0)-aa/aa.mean(0))*SIGN;influences.append(V)
        r["paired_block_delta_covariance"]=(np.cov(V,rowvar=False)/len(V)).tolist()
        r["leave_one_block_out_log_ratios"]=[effect(np.delete(aa,i,axis=0),np.delete(bb,i,axis=0)).tolist() for i in range(6)]
        r["end_clam_density_per_core_means"]=[float(z.Loripes_density_per_core.mean()) for z in (a,b)]
        r["leaf_sulfide_intrusion_means"]=[float(z.Fsulfide.mean()) for z in (a,b)]
        r["near_zero_control_sulfide_lt_1_micromol_L"]=bool(aa[:,0].mean()<1)
        out[stress]=r
    return {"doi":"10.3389/fmars.2020.00011","host_units":24,"contrasts":out,
      "full_block_delta_covariance_labels":["C|detox","C|biomass","OM|detox","OM|biomass"],
      "full_block_delta_covariance":(np.cov(np.column_stack(influences),rowvar=False)/6).tolist(),
      "design":"six randomized field blocks, four plots each. Day 49 porewater and day 50 dry biomass matched by plot. Control has resident clams; addition not presence/absence. Near-zero control sulfide flagged; no ratio pooling."}
def study2022(root):
    x=pd.read_csv(read(root,3),sep=";",decimal=",")
    assert len(x)==40 and x.tank.nunique()==4 and set(x.temperature)=={"yes","no"}
    assert not x[["s_dm_A","s_dm_B"]].isna().any().any()
    x["total"]=x.s_dm_A+x.s_dm_B
    out={}
    for t in ("no","yes"):
        tanks=sorted(x[x.temperature==t].tank.unique());assert len(tanks)==2
        for stress in ("no","yes"):
            pools=[];cov=[];eff=[];detail={}
            for tank in tanks:
                a,b=[arm(x[(x.tank==tank)&(x.injection==stress)&(x.loripes==f)],["sulfide","total"]) for f in ("no","yes")]
                assert min(len(a),len(b))>=2
                pools.append((a,b));cov.append(independent(a,b));eff.append(effect(a,b));detail[str(tank)]=row(a,b)
            a,b=[np.concatenate(v) for v in zip(*pools)];assert len(a)==len(b)==5
            r=row(a,b);v=np.mean(eff,axis=0);C=sum(cov)/4
            r.update(tanks=detail,equal_tank_mean_log_ratios=v.tolist(),equal_tank_conditional_delta_covariance=C.tolist(),equal_tank_conditional_delta_se=np.sqrt(C.diagonal()).tolist())
            out[f"{t}|{stress}"]=r
    return {"doi":"10.3354/meps14074","host_units":40,"contrasts":out,
      "design":"4 water tanks, 2 per temperature, 5 mesocosms per factorial cell. Equal-tank sensitivity averages within-tank oriented log ratios; covariance conditional on observed tanks and independent columns within tanks. Only 2 tanks/temperature; no general heat moderation inference or between-tank variance estimate. Pooled ratios for comparison with other studies, not independent tank-level effects."}
def analyze(root):
    s={"2012":study2012(root),"2020":study2020(root),"2022":study2022(root)}
    assert sum(v["host_units"] for v in s.values())==84
    assert s["2020"]["contrasts"]["C"]["near_zero_control_sulfide_lt_1_micromol_L"]
    return {"status":"three_study_descriptive_paired_endpoint_pilot_not_pooled_meta_analysis",
      "endpoint_order":["porewater_sulfide","total_final_seagrass_dry_biomass"],"orientation":"positive log ratio denotes lower sulfide or greater biomass",
      "source_hashes":FILES,"studies":s,"limitations":["Different baseline sulfide, stress types, duration, habitats and interventions. No universal dose-response, mediation or independent replication across treatment contexts.",
        "Delta covariances approximate and conditional; 2012 sheet alignment assumes within-treatment replicate identifiers correspond. 2020 retains complete paired-block cross-context covariance; 2022 equal-tank estimates conditional on the four sampled tanks. Do not combine covariance matrices as if all independent.",
        "Final biomass is standing biomass not directly measured productivity. Sulfide and host biomass jointly measured at or near experiment end; no temporal mediation.",
        "No pooled meta effect; only two laboratory presence/absence studies and one field addition study. Near-zero field baseline ratio unstable. Fourth independent laboratory study awaits source access."]}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("transmission_sources"));a=p.parse_args()
    print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
