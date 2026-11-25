#!/usr/bin/env python3
"""Conditional mixing reference for reconstructed eelgrass sire labels.
Not a paternity refit, spatial dispersal estimate, or independent study replication.
"""
import argparse, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import hypergeom
ARCHIVE='c0f4a1b0b988dc4a9f678f10cd8c413b8636585c554fd81591502b4af69d7d61'
FILES={'Reduced_Paternity.xlsx':'78d649e1c268aeeabb80c668760aeaafc02177f6726febd0e10cc0b58e72243b','Paternity.xlsx':'de1537cdca93f3126e07f44ad9d08cf756e55e49540e4da9de0caa895d9b7988','Reduced_Paternal_Heterozygosity.csv':'62c128849b0decc7e09d1e04a885aa58c7cabe33cb8d80042cf7d540e022fb8f','Paternal_Heterozygosity.csv':'71dcd6557604e2af34182d70deb5a6d15fb2edb8d5602e554168e2f5abf6bf89','Parent_Genotypes.xlsx':'ced25203e0b3bcbb3898c56fbab5eae25e9f0204f7694733415fbc0a17cc93de'}
def read(z,f,s=None):
    raw=z.read('zostera_paternity/'+f)
    if hashlib.sha256(raw).hexdigest()!=FILES[f]:raise ValueError('source drift '+f)
    d=pd.read_excel(io.BytesIO(raw),sheet_name=s) if f.endswith('xlsx') else pd.read_csv(io.BytesIO(raw))
    d.columns=d.columns.str.strip();d=d[pd.to_numeric(d.Site,errors='coerce').notna()].copy();d.Site=d.Site.astype(int)
    if 'Sire' in d:d.Sire=d.Sire.astype(str)
    return d

def null(counts,slots,obs,seed,B):
    counts=np.asarray(counts,int);slots=np.asarray(slots,int);N=int(counts.sum()); assert N==slots.sum() and (counts>0).all() and (slots>=0).all()
    # Expected share across at least 2 mothers. Each sire's seeds are a uniform subset of all slots.
    pr_one=np.sum([hypergeom.pmf(counts,N,int(k),counts) for k in slots],axis=0)
    expected=float((1-pr_one).sum())
    # Simulate the full conditional reference preserving all sire and mother margins simultaneously.
    labels=np.repeat(np.arange(len(counts)),counts);maternal=np.repeat(np.arange(len(slots)),slots)
    rng=np.random.default_rng(seed);x=np.empty(B,int)
    for i in range(B):
        c=np.bincount(maternal*len(counts)+rng.permutation(labels),minlength=len(slots)*len(counts)).reshape(len(slots),len(counts))
        x[i]=np.sum((c>0).sum(0)>=2)
    assert abs(x.mean()-expected)<.25
    return {'outcross_seed_slots':N,'observed_shared_sire_labels':int(obs),'expected_shared_sire_labels':expected,'simulated_mean':float(x.mean()),'null_quantiles_025_50_975':np.quantile(x,[.025,.5,.975]).tolist(),'lower_tail_mc_p':float((1+(x<=obs).sum())/(B+1)),'B':B,'observed_expected_ratio':float(obs/expected)}

def panel(z,typ,B):
    if typ=='high_locus': f='Reduced_Paternity.xlsx'; ds='By Dad';ms='Per Shoot';cs='Reduced_Paternal_Heterozygosity.csv'
    else:f='Paternity.xlsx';ds='Slim Dads';ms='Slim Shoot';cs='Paternal_Heterozygosity.csv'
    d=read(z,f,ds);m=read(z,f,ms);h=read(z,cs)
    col=next(c for c in d if c.lower()=='shoots fertilized')
    j=d.merge(h,on=['Site','Sire'],validate='one_to_one',suffixes=('_d','_h'))
    assert len(j)==len(d)==len(h) and (j['Seeds Fertilized_d']==j['Seeds Fertilized_h']).all()
    assert set(j['Reproductive Strategy'])=={'Outcrossing','Selfing'}
    assert not m.duplicated(['Site','Maternal ID']).any()
    out={}
    for site,g in j.groupby('Site'):
        a=g[g['Reproductive Strategy']=='Outcrossing'];b=m[m.Site==site]
        counts=a['Seeds Fertilized_d'].to_numpy(int);slots=b['Outcrossed Seeds'].to_numpy(int);obs=int((a[col]>1).sum());gap=int(counts.sum()-slots.sum())
        r={'maternal_shoots':len(b),'sire_labels_all':len(g),'sire_labels_outcross_labeled':len(a),'sire_seed_total_all':int(g['Seeds Fertilized_d'].sum()),'maternal_genotyped_total':int(b['Genotyped Seeds'].sum()),'sire_outcross_total':int(counts.sum()),'maternal_outcross_total':int(slots.sum()),'outcross_margin_difference':gap,'observed_shared_outcross_sire_labels':obs,'observed_shared_all_sire_labels':int((g[col]>1).sum()),'maternal_outcross_slots':slots.tolist(),'sire_outcross_count_histogram':{str(k):int(v) for k,v in zip(*np.unique(counts,return_counts=True))}}
        if gap==0:r['status']='MATCHED_OUTCROSS_MARGINS';r['conditional_null']=null(counts,slots,obs,20261125+int(site),B)
        else:
            r['status']='STOP_EXACT_NULL_MARGIN_MISMATCH'
            # No source correction. If exactly one count missing, bracket expectations by all possible positions.
            if abs(gap)==1:
                alternatives=[]
                for i in range(len(slots)):
                    s=slots.copy();s[i]+=gap
                    if s[i]<0:continue
                    e=float(np.sum(1-np.sum([hypergeom.pmf(counts,counts.sum(),int(k),counts) for k in s],axis=0)))
                    alternatives.append(e)
                r['hypothetical_one_slot_adjustment_expected_range']=[min(alternatives),max(alternatives)]
        out[str(site)]=r
    return {'sire_rows':len(d),'maternal_rows':len(m),'sites':out}

def ambiguity(z):
    d=read(z,'Parent_Genotypes.xlsx','Reduced Data');h=read(z,'Reduced_Paternal_Heterozygosity.csv')
    d=d.merge(h[['Site','Sire','Reproductive Strategy']],on=['Site','Sire'],validate='one_to_one');assert len(d)==180
    ans={}
    for site,x in d[d['Reproductive Strategy']=='Outcrossing'].groupby('Site'):
        A=np.stack([np.sort(x[[f'ZM{i} Allele 1',f'ZM{i} Allele 2']].to_numpy(float),axis=1) for i in range(1,11)],axis=1)
        P=x[['Prob']+[f'Prob.{i}' for i in range(1,10)]].to_numpy(float)
        confident=P>=.925;assert (confident.sum(1)==x['# Reconstructed Loci'].to_numpy()).all()
        pairs=np.triu_indices(len(x),1);i,j=pairs
        both=confident[i]&confident[j];overlap=both.sum(1);mismatch=np.any((A[i]!=A[j]).any(2)&both,axis=1)
        ans[str(site)]={'labels':len(x),'pairs':len(i),'pairs_no_conflicting_confident_locus':int((~mismatch).sum()),'by_minimum_joint_confident_loci':{str(k):{'comparable_pairs':int((overlap>=k).sum()),'no_conflicting_pairs':int(((overlap>=k)&~mismatch).sum())} for k in (3,5,8,10)}}
    return ans

def analyze(path,B):
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ARCHIVE
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        high=panel(z,'high_locus',B);slim=panel(z,'slim',B);ambigu=ambiguity(z)
    return {'status':'original_reconstructed_sire_label_conditional_reference_not_spatial_paternity_model','paper_doi':'10.1002/ece3.11608','data_doi':'10.5061/dryad.dfn2z358x','archive_sha256':ARCHIVE,'member_hashes':FILES,'high_locus':high,'slim':slim,'high_locus_marker_identity_audit':ambigu,'limits':['Use deposited sire and maternal summary tables, not individual seed assignments, actual father coordinates, or COLONY reanalysis. Sire sharing across maternal reproductive shoots is a property of reconstructed labels, not necessarily actual individual identity.','Outcross-labeled sire counts do not close to maternal outcross counts in some sites; skip exact reference there. No repaired counts. Site 1 high-locus alternative expectations only are hypothetical sensitivity.','Conditional complete mixing preserves each sire seed count and each mother outcross slot count, but not timing, space, genetic compatibility, assignment uncertainty or sampling of nonviable seeds. Reference p is model-conditional, not evidence of any particular ecological process or independent site replicates.','Sire-level no-conflict at shared confident markers does not demonstrate identical genotype. No merging or estimate of true father sharing. The two source cohorts overlap and are not independent experiments.','Enhalus coordinates cannot be linked to these Zostera parents; no inference about pollen transport distance, donor-loss outcome, or flowering synchrony.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--simulations',type=int,default=20000);p.add_argument('--out',type=Path);a=p.parse_args();v=json.dumps(analyze(a.source,a.simulations),indent=2,sort_keys=True,allow_nan=False)+'\n';a.out.write_text(v) if a.out else print(v,end='')
