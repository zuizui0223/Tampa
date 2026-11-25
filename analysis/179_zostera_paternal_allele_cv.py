#!/usr/bin/env python3
"""Paternal-allele conditional prediction, not a paternal-genotype refit.
Use maternal calls from the original COLONY output and observed diploid seed calls.
No father IDs or father positions used. Alphabet conditioned on observed locus values.
"""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp

ARCHIVE='c0f4a1b0b988dc4a9f678f10cd8c413b8636585c554fd81591502b4af69d7d61'
FILES={'Parent_Genotypes.xlsx':'ced25203e0b3bcbb3898c56fbab5eae25e9f0204f7694733415fbc0a17cc93de','Seed_Genotypes.xlsx':'394758533a8ef6d26c85c590bba398480f12231c2836294c6dd972c830867b48'}

def read_records(path):
    raw=path.read_bytes(); assert hashlib.sha256(raw).hexdigest()==ARCHIVE
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        data={f:z.read('zostera_paternity/'+f) for f in FILES}
        assert all(hashlib.sha256(data[f]).hexdigest()==h for f,h in FILES.items())
    p=pd.read_excel(io.BytesIO(data['Parent_Genotypes.xlsx']),sheet_name='Original Data')
    assert len(p)==235 and p.iloc[26]['Site']=='Site' and p.iloc[26]['Maternal ID']=='Sire'
    p=p.iloc[:26].copy(); assert p['Maternal ID'].str.fullmatch(r'Shoot\d+').all()
    p['Maternal ID']=p['Maternal ID'].str.replace('Shoot','',regex=False).astype(int);p.Site=p.Site.astype(int)
    s=pd.read_excel(io.BytesIO(data['Seed_Genotypes.xlsx']));assert len(s)==844
    s.Site=s.Site.astype(int)
    key=['Site','Maternal ID'];seedkey=key+['Rhipidium','Spathe','Offspring Number']
    assert not p.duplicated(key).any() and not s.duplicated(seedkey).any()
    assert set(map(tuple,p[key].to_numpy()))==set(map(tuple,s[key].to_numpy()))
    for l in range(1,11):
        assert s[f'ZM{l} Allele1'].isna().equals(s[f'ZM{l} Allele2'].isna())
    s['typed_loci']=s[[f'ZM{l} Allele1' for l in range(1,11)]].notna().sum(axis=1)
    rec=[];audit=[]
    for (site,mom),g in s.groupby(key):
        m=p[(p.Site==site)&(p['Maternal ID']==mom)].iloc[0]
        for l in range(1,11):
            pc='Prob' if l==1 else f'Prob.{l-1}'
            a=np.array([m[f'ZM{l} Allele 1'],m[f'ZM{l} Allele 2']],float)
            if not np.isfinite(a).all():continue
            prob=float(m[pc]); assert 0<=prob<=1
            x=g.dropna(subset=[f'ZM{l} Allele1',f'ZM{l} Allele2'])
            b=x[[f'ZM{l} Allele1',f'ZM{l} Allele2']].to_numpy(float)
            assert np.equal(a,np.floor(a)).all() and np.equal(b,np.floor(b)).all()
            non=(b[:,:,None]!=a[None,None,:]).all(2); n=non.sum(1)
            audit.append(dict(site=int(site),mom=int(mom),locus=l,prob=prob,observed=len(x),unique=int((n==1).sum()),ambiguous=int((n==0).sum()),incompatible=int((n==2).sum())))
            for i,r in enumerate(x.itertuples(index=False,name=None)):
                if n[i]!=1:continue
                q=dict(zip(x.columns,r)); rec.append(dict(site=int(site),mom=int(mom),rh=int(q['Rhipidium']),sp=int(q['Spathe']),seed=int(q['Offspring Number']),locus=l,allele=int(b[i][non[i]][0]),a=int(a[0]),b=int(a[1]),prob=prob,typed_loci=int(q['typed_loci']),clean=bool((n==2).sum()==0)))
    d=pd.DataFrame(rec);a=pd.DataFrame(audit)
    assert len(d)==1458 and len(a)==260
    return d,a,s

def fit_pool(counts,mask,alpha=.5):
    # P(observed paternal allele a | a not in maternal alleles) = p_a / sum of permitted p.
    # Half a pseudo-observation per allele stabilizes the full allele distribution.
    n=counts.sum(1);tot=counts.sum(0);A=len(tot)
    def fn(v):
        ls=logsumexp(np.where(mask,v,-np.inf),axis=1);lsall=logsumexp(v)
        p=np.exp(np.where(mask,v,-np.inf)-ls[:,None]);pall=np.exp(v-lsall)
        val=n@ls-tot@v+alpha*(A*lsall-v.sum());grad=n@p-tot+alpha*(A*pall-1)
        return val,grad
    res=minimize(fn,np.zeros(A),jac=True,method='L-BFGS-B',options={'ftol':1e-11,'gtol':1e-6,'maxiter':300})
    assert res.success,res.message
    lp=np.where(mask,res.x,-np.inf);return np.exp(lp-logsumexp(lp,axis=1)[:,None])

def evaluate(d,mode):
    out=[]
    for (site,locus),g in d.groupby(['site','locus']):
        if g.mom.nunique()<2:continue
        # Conditional allele alphabet (including test allele names, not counts), not a prospective novel-allele forecast.
        alleles=sorted(set(g.allele)|set(g.a)|set(g.b));moms=sorted(g.mom.unique());md={m:i for i,m in enumerate(moms)};ad={a:i for i,a in enumerate(alleles)}
        mi=g.mom.map(md).to_numpy();ai=g.allele.map(ad).to_numpy();rh=g.rh.to_numpy();sp=g.sp.to_numpy();mask=np.ones((len(moms),len(alleles)),bool)
        for m,k in g.groupby('mom'):
            a,b=k[['a','b']].iloc[0];assert len(k[['a','b']].drop_duplicates())==1;mask[md[m],[ad[a],ad[b]]]=False
        assert mask[mi,ai].all()
        c=np.zeros(mask.shape);np.add.at(c,(mi,ai),1)
        folds=sorted(set(zip(mi,rh))) if mode=='rhipidium' else sorted(set(zip(mi,rh,sp)))
        for f in folds:
            m,r=f[:2];te=(mi==m)&(rh==r)
            if mode=='spathe':
                te&=(sp==f[2]);same_branch=(mi==m)&(rh==r)&~te;other_branch=(mi==m)&(rh!=r)
                if not same_branch.any() or not other_branch.any():continue
            train=c.copy();np.add.at(train,(mi[te],ai[te]),-1)
            if train[m].sum()==0:continue
            pp=fit_pool(train,mask);aidx=ai[te]
            pred={'pooled':pp[m]}
            for shrink in (5,20,50):pred[f'mother_{shrink}']=(train[m]+shrink*pp[m])/(train[m].sum()+shrink)
            if mode=='spathe':
                br=np.bincount(ai[same_branch],minlength=len(alleles));other=np.bincount(ai[other_branch],minlength=len(alleles))
                for shrink in (5,20,50):
                    mom=(other+shrink*pp[m])/(other.sum()+shrink);pred[f'branch_{shrink}']=(br+shrink*mom)/(br.sum()+shrink)
            z={'site':site,'mom':moms[m],'rh':r,'locus':locus,'sp':f[2] if len(f)==3 else -1}
            for k,v in pred.items():
                assert np.isclose(v.sum(),1.) and (v[aidx]>0).all();z[k]=-np.log(v[aidx])
            out.append(pd.DataFrame(z))
    v=pd.concat(out,ignore_index=True)
    cols=[c for c in v if c=='pooled' or c.startswith(('mother_','branch_'))]
    def summarize(g):
        mom=g.groupby(['site','mom'])[cols].mean();avg=g[cols].mean();return {'scored_allele_records':len(g),'scored_maternal_shoots':len(mom),'mean_log_loss':avg.to_dict(),'equal_mother_mean_log_loss':mom.mean().to_dict(),'relative_reduction_vs_pooled':(1-avg/avg.pooled).to_dict(),'mother_wins_20':int((mom.mother_20<mom.pooled).sum())}
    return {'overall':summarize(v),'by_site':{str(site):summarize(g) for site,g in v.groupby('site')}}

def analyze(path):
    d,a,s=read_records(path);panels={}
    for prob in (.925,.99,1.):
        z=d[d.prob>=prob];q=a[a.prob>=prob]
        panels[str(prob)]={'informative_records':len(z),'seed_count_with_informative_alleles':len(z[['site','mom','rh','sp','seed']].drop_duplicates()),'compatible_count_audit':{k:int(q[k].sum()) for k in ('observed','unique','ambiguous','incompatible')},'rhipidium':evaluate(z,'rhipidium')}
        if prob in (.925,1.):panels[str(prob)]['spathe']=evaluate(z,'spathe')
    sens={k:evaluate(z,'rhipidium') for k,z in [('source_9_10_typed_loci',d[(d.prob>=.925)&(d.typed_loci>=9)]),('exclude_mother_locus_with_conflict',d[(d.prob>=.925)&d.clean])]}
    return {'status':'conditional_offspring_allele_diagnostic_not_spatial_or_paternity_refit','source_doi':'10.5061/dryad.dfn2z358x','paper_doi':'10.1002/ece3.11608','archive_sha256':ARCHIVE,'member_sha256':FILES,'seed_records':len(s),'maternal_shoots':26,'seed_typed_locus_histogram':{str(k):int(v) for k,v in s.typed_loci.value_counts().sort_index().items()},'panels':panels,'additional_sensitivities':sens,'limitations':['Maternal genotypes reconstructed from the same offspring, not independent tissue calls. Their held-out branch genotypes may therefore contribute to maternal reconstruction. Conditional cross-validation, not independent genotype prediction or validation of COLONY.','Only locus-level unique nonmaternal alleles; both offspring alleles absent from mother flagged as incompatible; both present ambiguous (not proof of selfing). Missing calls excluded. Different probability panels change locus/mother coverage, so differences cannot be attributed solely to error.','Pooled model conditions on mother-specific allowed alleles; otherwise differing maternal genotypes would create artificial site-pool heterogeneity. Locus vocabularies conditioned on all observed allele names, not test frequencies; fixed .5 pseudo count and shrinkage 5/20/50, not tuned.','Leave whole rhipidium or spathe out for each site/locus; scoring allele observations within nested maternal units, not independent biological samples. Aggregate log loss and equal-mother sensitivity only, no p-values.','Marginal paternal allele distribution does not identify actual sire sharing, distances, temporal overlap or pollen limitation. No new spatial evidence or refutation of prior sire-label result.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path);a=p.parse_args();v=json.dumps(analyze(a.source),indent=2,sort_keys=True,allow_nan=False)+'\n';a.out.write_text(v) if a.out else print(v,end='')
