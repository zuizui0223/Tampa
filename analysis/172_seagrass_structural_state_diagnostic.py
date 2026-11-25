#!/usr/bin/env python3
"""Source-locked standing biomass and density contrasts, not temporal ordering or mediation."""
import argparse,hashlib,itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
FILES={
'lucinid_2020/Table_9_Field_experiment_Z_noltei_AND_L_orbiculatus_data_per_experimental_plot.txt':'203771a3f17fb412d2585659263095befdc5c385d4a50072cfbe7f3c8c155094',
'lucinid_2012/Experimental_data.xlsx':'f59e66910a97daef609b275772f319b8c7f63b98e3e1b05644c3d37499ade7ac',
'donaher_2021/Exp1_BiomassCores_All.xlsx':'b728f7b1df148e0ea0945ddfca4af1266cfd9c88233e028d0fc337b736360e76'}
def read(root,key,sheet=0):
 p=root/key
 if hashlib.sha256(p.read_bytes()).hexdigest()!=FILES[key]:raise ValueError('source drift: '+key)
 return pd.read_excel(p,sheet_name=sheet) if p.suffix=='.xlsx' else pd.read_csv(p,sep=r'\s+')
def holm(p):
 i=np.argsort(p);o=np.empty(len(p));o[i]=np.minimum(1,np.maximum.accumulate(p[i]*(len(p)-np.arange(len(p)))));return o

def field(root):
 x=read(root,list(FILES)[0]).rename(columns={'Zn_shoot_density_per_core':'shoots','Zn_leaf_DW_g_per_core':'leaf','Zn_rhizome_DW_g_per_core':'rhizome','Zn_root_DW_g_per_core':'root'})
 assert len(x)==24 and x.Plot_ID.is_unique and x.Block.nunique()==6 and not x.duplicated(['Block','OM_addition','Loripes_addition']).any()
 x['below']=x.rhizome+x.root;x['total']=x.below+x.leaf
 organs=['leaf','rhizome','root','below','total'];cols=['shoots']+organs+[c+'_per_shoot' for c in organs]
 for c in organs:x[c+'_per_shoot']=x[c]/x.shoots
 assert np.isfinite(x[cols]).all().all() and (x[cols]>0).all().all()
 S=np.array(list(itertools.product([-1,1],repeat=12)));out={}
 for name,f,levels,h in [('organic_matter','OM_addition',['C','OM'],'Loripes_addition'),('clam_addition','Loripes_addition',['C','L'],'OM_addition')]:
  D=[];strata={}
  for k,g in x.groupby(h):
   a,b=[g[g[f]==i].sort_values('Block') for i in levels]
   assert len(a)==len(b)==6 and list(a.Block)==list(b.Block)
   z=np.log(b[cols].to_numpy()/a[cols].to_numpy());D.append(z);strata[k]={'ratio':dict(zip(cols,np.exp(z.mean(0)).tolist())),'block_log_ratios':z.tolist()}
  z=np.concatenate(D);obs=z.mean(0);p=(np.abs(S@z/12)>=np.abs(obs)-1e-12).mean(0);adj=holm(p)
  zz=np.mean(D,axis=0);loo=np.exp((zz.sum(0)-zz)/5)
  # Conditioning on assignment of the other factor, independent swaps within 12 pairs.
  out[name]={'strata':strata,'endpoints':{c:{'ratio':float(np.exp(obs[i])),'unadjusted_randomization_p':float(p[i]),'holm_11_p':float(adj[i]),'negative_blocks':int((zz[:,i]<0).sum()),'leave_one_block_out_range':[float(loo[:,i].min()),float(loo[:,i].max())]} for i,c in enumerate(cols)},'covariance_equal_block_log_effect':(np.cov(zz,rowvar=False)/6).tolist()}
  for c in organs:assert np.allclose(z[:,cols.index(c)],z[:,0]+z[:,cols.index(c+'_per_shoot')])
 return {'plots':24,'blocks':6,'endpoint_order':cols,'contrasts':out,'limits':'Final standing biomass, not reserves or time series. Per-shoot index is core mass divided by shoot count, not anatomically assigned ramet mass. Conditional 2^12 label-swap randomization assumes unrestricted random assignment of all four treatment combinations within each block, conditioning on the other factor; tests sharp nulls, not time-ordering. Holm adjustment over 11 exploratory endpoints separately per manipulation. Leave-block-out ranges are not confidence intervals.'}

def laboratory(root):
 x=read(root,list(FILES)[1],sheet='Zostera').rename(columns={'Shoot_biomass':'leaf','Rhizome_bioamss':'rhizome','Root_biomass':'root'})
 assert len(x)==20 and not x.duplicated(['Zostera_Loripes','Sulfide','#']).any()
 x['below']=x.rhizome+x.root;x['total']=x.below+x.leaf;cols=['leaf','rhizome','root','below','total'];assert np.isfinite(x[cols]).all().all() and (x[cols]>0).all().all()
 m=x.groupby(['Zostera_Loripes','Sulfide'])[cols].mean();assert x.groupby(['Zostera_Loripes','Sulfide']).size().eq(5).all()
 return {'host_columns':20,'endpoint_order':cols,'sulfide_effect_by_clam':{k:(m.loc[(k,'S')]/m.loc[(k,'C')]).to_dict() for k in ['Z','ZL']},'clam_effect_by_sulfide':{k:(m.loc[('ZL',k)]/m.loc[('Z',k)]).to_dict() for k in ['C','S']},'limits':'Ratios of arithmetic arm means, five columns per treatment. Shared water basin; no temporal ordering or direct statistical comparison across studies.'}

def donaher_audit(root):
 x=read(root,list(FILES)[2],sheet=1);assert len(x)==192 and not x.duplicated(['Sample ID','Year','Month','Species']).any()
 q=pd.to_numeric(x['Shoot Density'],errors='coerce');bad=x.loc[x['Shoot Density'].notna()&q.isna(),'Shoot Density'].astype(str).value_counts().to_dict();x['numeric_density']=q
 assert bad=={'N':1}
 b=x.pivot(index=['Sample ID','Year','Month'],columns='Species',values='Below Sample Weight')
 duplicated=int((b.HALODULE.notna()&b.ZOSTERA.notna()&np.isclose(b.HALODULE,b.ZOSTERA)).sum())
 d=x[x.Year==2019];out={}
 for (m,s),g in d.groupby(['Month','Species']):
  z=g.dropna(subset=['numeric_density','Above Sample Weight']);out[m+'|'+s]={'complete_rows':len(z),'zero_density_positive_mass':int(((z.numeric_density==0)&(z['Above Sample Weight']>0)).sum()),'observed_density_range':[float(z.numeric_density.min()),float(z.numeric_density.max())]}
 return {'rows':len(x),'nonnumeric_density_labels':bad,'duplicate_belowground_values_in_both_species_rows':duplicated,'by_2019_context':out,'status':'STOP_per_shoot_replication_until_units_and_zero_records_resolved','limits':'Shoot Density metadata labels shoots/cm2; 2019 July Halodule values are nearly integer counts whereas May Halodule and both Zostera months use different numerical scale. July Zostera has positive mass at recorded zero density. Belowground mass repeated across species, cannot allocate per species. Do not repair or compare cross-month mass/density without verified units and denominator.'}
def analyze(root):
 return {'status':'posthoc_structural_state_diagnostic_not_temporal_or_meta_analysis','source_hashes':FILES,'field_2020':field(root),'laboratory_2012':laboratory(root),'donaher_source_audit':donaher_audit(root)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('transmission_sources'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
