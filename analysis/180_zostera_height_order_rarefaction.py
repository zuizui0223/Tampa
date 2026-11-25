#!/usr/bin/env python3
"""Within-shoot rarefaction of offspring allelic richness, no hydrodynamic inference."""
import argparse, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
ARCHIVE='c0f4a1b0b988dc4a9f678f10cd8c413b8636585c554fd81591502b4af69d7d61'
MEMBER='zostera_paternity/Seed_Genotypes.xlsx'
SHA='394758533a8ef6d26c85c590bba398480f12231c2836294c6dd972c830867b48'
KEY=['Site','Maternal ID','Rhipidium','Spathe','Offspring Number']
COLS=[f'ZM{i} Allele{j}' for i in range(1,11) for j in (1,2)]

def rarefy(a,k):
    # Expected distinct alleles after drawing k WHOLE diploid seeds without replacement.
    n=len(a); assert n>=k and np.isfinite(a).all()
    den=math.comb(n,k)
    return sum(1-(math.comb(n-c,k)/den if n-c>=k else 0) for x in np.unique(a) for c in [int((a==x).any(axis=1).sum())])

def summarize(p):
    if not len(p):return {'pairs':0,'mothers':0}
    d=pd.DataFrame(p); m=d.groupby(['site','mother'])[['lower','upper','difference']].mean();v=m.difference.to_numpy()
    rng=np.random.default_rng(20261125);draw=np.zeros(20000)
    # Resample maternal shoots within observed sites; condition on these three sites.
    for site,g in m.groupby(level=0):
        a=g.difference.to_numpy();draw+=a[rng.integers(len(a),size=(len(draw),len(a)))].sum(axis=1)
    draw/=len(m)
    return {'pairs':len(d),'mothers':len(m),'mean_lower':float(m.lower.mean()),'mean_upper':float(m.upper.mean()),'mean_difference':float(v.mean()),'maternal_positive':int((v>1e-10).sum()),'maternal_negative':int((v< -1e-10).sum()),'maternal_tie':int((abs(v)<=1e-10).sum()),'conditional_mother_bootstrap_95':np.quantile(draw,[.025,.975]).tolist(),'site_means':{str(i):{'mothers':len(g),'difference':float(g.difference.mean())} for i,g in m.groupby(level=0)},'leave_one_mother_out_range':[float(min((v.sum()-v)/(len(v)-1))),float(max((v.sum()-v)/(len(v)-1)))] if len(v)>1 else None,'records':p}

def compare(s,k,mode,complete):
    p=[]
    for (site,mom),g in s.groupby(KEY[:2]):
        lo,hi=int(g.Rhipidium.min()),int(g.Rhipidium.max()); groups=[]
        if mode in ('matched_spathe','first_spathe'):
            for sp in ([1] if mode=='first_spathe' else sorted(g.Spathe.unique())):
                groups.append((lo,hi,int(sp),int(sp),g[(g.Rhipidium==lo)&(g.Spathe==sp)],g[(g.Rhipidium==hi)&(g.Spathe==sp)]))
        elif mode=='pooled_branch':groups.append((lo,hi,None,None,g[g.Rhipidium==lo],g[g.Rhipidium==hi]))
        elif mode=='adjacent_height':
            for sp,h in g.groupby('Spathe'):
                levels=set(h.Rhipidium)
                for rh in sorted(levels):
                    if rh+1 in levels:groups.append((int(rh),int(rh+1),int(sp),int(sp),h[h.Rhipidium==rh],h[h.Rhipidium==rh+1]))
        elif mode=='adjacent_timing':
            for rh,h in g.groupby('Rhipidium'):
                levels=set(h.Spathe)
                for sp in sorted(levels):
                    if sp+1 in levels:groups.append((int(rh),int(rh),int(sp),int(sp+1),h[h.Spathe==sp],h[h.Spathe==sp+1]))
        elif mode=='timing_within_branch':
            for rh,h in g.groupby('Rhipidium'):
                a,b=int(h.Spathe.min()),int(h.Spathe.max());
                if a<b:groups.append((int(rh),int(rh),a,b,h[h.Spathe==a],h[h.Spathe==b]))
        for r0,r1,t0,t1,a,b in groups:
            if complete:a,b=a.dropna(subset=COLS),b.dropna(subset=COLS)
            x,y=[],[];n0,n1=[],[]
            for i in range(10):
                c=COLS[2*i:2*i+2];aa=a[c].dropna().to_numpy();bb=b[c].dropna().to_numpy();n0.append(len(aa));n1.append(len(bb))
                if min(len(aa),len(bb))<k:break
                x.append(rarefy(aa,k));y.append(rarefy(bb,k))
            if len(x)!=10:continue
            p.append({'site':int(site),'mother':int(mom),'lower_branch':r0,'upper_branch':r1,'lower_spathe':t0,'upper_spathe':t1,'lower':float(np.mean(x)),'upper':float(np.mean(y)),'difference':float(np.mean(np.array(y)-x)),'lower_n_by_locus':n0,'upper_n_by_locus':n1,'lower_richness_by_locus':x,'upper_richness_by_locus':y})
    return summarize(p)

def analyze(path):
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ARCHIVE
    with zipfile.ZipFile(io.BytesIO(raw)) as z:b=z.read(MEMBER)
    assert hashlib.sha256(b).hexdigest()==SHA
    s=pd.read_excel(io.BytesIO(b));assert len(s)==844 and not s.duplicated(KEY).any() and s.groupby(KEY[:2]).ngroups==26
    assert s.groupby(KEY[:4]).ngroups==162 and s.groupby(KEY[:3]).ngroups==83
    assert all(s[COLS[i]].isna().equals(s[COLS[i+1]].isna()) for i in range(0,20,2));assert s.groupby(KEY[:2]).Rhipidium.min().eq(1).all()
    complete=int(s[COLS].notna().all(axis=1).sum());assert complete==674
    # A seed with homozygous copies contributes one presence, not two independent alleles.
    assert math.isclose(rarefy(np.array([[1,1],[1,2],[3,3]]),1),4/3)
    assert math.isclose(rarefy(np.array([[1,1],[1,2],[3,3]]),2),7/3)
    panels={}
    for mode in ('matched_spathe','first_spathe','pooled_branch','timing_within_branch'):
        for k in (2,3,4,5,6):
            for c in (True,False):
                key=f'{mode}|{k}|'+('complete_seed' if c else 'locuswise')
                panels[key]=compare(s,k,mode,c)
    for mode in ('adjacent_height','adjacent_timing'):
        panels[mode+'|3|complete_seed']=compare(s,3,mode,True)
    h=pd.DataFrame(panels['matched_spathe|3|complete_seed']['records']).groupby(['site','mother']).difference.mean()
    t=pd.DataFrame(panels['timing_within_branch|3|complete_seed']['records']).groupby(['site','mother']).difference.mean()
    common=pd.concat([h,t],axis=1,keys=['height','order']).dropna();common['order_minus_height']=common.order-common.height
    rng=np.random.default_rng(20261125);draw=np.zeros(20000)
    for site,g in common.groupby(level=0):
        v=g.order_minus_height.to_numpy();draw+=v[rng.integers(len(v),size=(len(draw),len(v)))].sum(1)
    shared={'mothers':len(common),'mean_differences':common.mean().to_dict(),'site_means':{str(i):g.mean().to_dict() for i,g in common.groupby(level=0)},'conditional_bootstrap_95_order_minus_height':np.quantile(draw/len(common),[.025,.975]).tolist()}
    return {'shared_mother_sensitivity':shared,'status':'posthoc_morphological_position_rarefaction_not_measured_flow','paper_doi':'10.1002/ece3.11608','data_doi':'10.5061/dryad.dfn2z358x','comparison_prior_art_doi':'10.3389/fmars.2019.00008','archive_sha256':ARCHIVE,'member_sha256':SHA,'seeds':len(s),'complete_10_locus_seeds':complete,'mothers':26,'panels':panels,'primary':'matched_spathe|3|complete_seed','limits':['Branch index is the source proxy for water-column height and spathe rank proxy for timing; actual heights, velocities, flowering dates and donor locations not measured here. Compare lowest and highest observed branches at same spathe rank, not absolute physical height or simultaneous flowering.','Rarefy by whole diploid offspring rather than independent alleles; different sample size and marker set from Follett 2019. Offspring allele richness is not number of fathers or actual pollen dispersal. No reconstructed parent genotypes used.','Available genotype sample conditional on seed survival and source QC; panels change coverage. Equal within-mother pair weighting then equal mothers. Mother bootstrap stratified by site conditional on these three meadows, not randomized effect or general across-site CI. Posthoc descriptive contrast; no equivalence test.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.source),indent=2,sort_keys=True,allow_nan=False)+'\n')
