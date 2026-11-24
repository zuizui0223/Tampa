#!/usr/bin/env python3
"""Descriptive spatial genetic neighbourhoods in Yu et al. 2019.
DOI 10.1002/ece3.5106; data DOI 10.5061/dryad.sn1h87s.
One fragmented and one continuous plot, NOT replicated treatment.
Different MLG is not opposite sex, flowering, compatibility or gene flow.
"""
import collections
import hashlib
import io
import json
import math
from pathlib import Path
import numpy as np
import openpyxl

SOURCE=Path("reproductive_input/yu/Ramets For Two plots.xlsx")
SHA="10e1465ac9255ad2d873d6142386b5140320740ebc660196b4a9eb0e2251c959"
RADII=(1,2,4,8)
N_TARGET=271
SEED=20261124
B=2000

def parse(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Source member checksum mismatch")
    w=openpyxl.load_workbook(io.BytesIO(raw),data_only=True,read_only=True)
    if w.sheetnames!=["PLOTA","PLOTB"]:
        raise ValueError("Unexpected worksheet roster")
    result={}
    for s,n,G,pop in zip(w,[271,395],[214,255],["p1","p2"]):
        rows=list(s.values)
        if rows[2][0:2]!=("ind","pop") or rows[2][19:21]!=("x","y"):
            raise ValueError("Unexpected workbook layout")
        gen=[]; xy=[]; ids=set()
        for row in rows[3:]:
            if row[0] in ids or row[1]!=pop:
                raise ValueError("Duplicate individual ID or wrong population")
            ids.add(row[0])
            alleles=row[2:18]
            if len(alleles)!=16 or not all(isinstance(v,int) and v>0 for v in alleles):
                raise ValueError("Missing or nonpositive microsatellite alleles")
            gen.append(tuple(tuple(sorted(alleles[i:i+2])) for i in range(0,16,2)))
            coord=row[19:21]
            if not all(isinstance(v,int) and 0<=v<=20 for v in coord):
                raise ValueError("Unexpected coordinate")
            xy.append(coord)
        if len(gen)!=n or len(set(gen))!=G or len(set(xy))!=n:
            raise ValueError("Published sample/genet totals or coordinate uniqueness mismatch")
        labels={v:i for i,v in enumerate(dict.fromkeys(gen))}
        result[s.title]=(np.array([labels[v] for v in gen]),np.array(xy))
    return result

def inclusion(N,n,k):
    if not 0<=n<=N or not 1<=k<=N: raise ValueError("Invalid hypergeometric arguments")
    return 1-(math.comb(N-k,n)/math.comb(N,n) if N-k>=n else 0)

def distances2(xy):
    return np.sum((xy[:,None,:]-xy[None,:,:])**2,axis=2)

def describe(g,xy,d2):
    n=len(g); c=collections.Counter(g.tolist())
    diff=g[:,None]!=g[None,:]
    expected_same=sum(k*(k-1) for k in c.values())/(n*(n-1))
    out={"sampled_ramets":n,"exact_mlgs":len(c),"clonal_richness":(len(c)-1)/(n-1),
         "clone_size_histogram":dict(sorted(collections.Counter(c.values()).items())),
         "exact_expected_rarefied_mlg_count_n271":sum(inclusion(n,N_TARGET,k) for k in c.values()),
         "random_label_same_mlg_pair_probability":expected_same,"radii_m":{}}
    for r in RADII:
        m=(d2>0)&(d2<=r*r)
        tot=m.sum(axis=1); oth=(m&diff).sum(axis=1)
        near=[collections.Counter(g[row & diff[j]].tolist()) for j,row in enumerate(m)]
        unique=np.array([len(k) for k in near])
        interior=np.min(np.minimum(xy,20-xy),axis=1)>=r
        # Conditional on focal ramet retained, randomly choose n_target-1 from N-1.
        expected= [sum(inclusion(n-1,N_TARGET-1,k) for k in counts.values()) for counts in near]
        out["radii_m"][str(r)]={"mean_all_neighbour_ramets":float(tot.mean()),
            "mean_nonself_mlg_neighbour_ramets":float(oth.mean()),
            "mean_distinct_other_mlgs":float(unique.mean()),
            "fraction_without_other_mlg":float((unique==0).mean()),
            "pair_weighted_different_mlg_fraction":float(oth.sum()/tot.sum()),
            "undirected_neighbor_pairs":int(tot.sum()//2),
            "undirected_same_mlg_pairs":int((tot.sum()-oth.sum())//2),
            "interior_focal_count":int(interior.sum()),
            "interior_mean_distinct_other_mlgs":float(unique[interior].mean()),
            "exact_expected_mean_distinct_other_mlgs_rarefied_n271":float(np.mean(expected))}
    return out

def random_thinning(g,d2):
    rng=np.random.default_rng(SEED)
    rows=[]
    for _ in range(B):
        ix=np.sort(rng.choice(len(g),N_TARGET,replace=False)); a=g[ix]; d=d2[np.ix_(ix,ix)]
        diff=a[:,None]!=a[None,:]
        v=[len(set(a.tolist()))]
        for r in RADII:
            m=(d>0)&(d<=r*r)
            u=[len(set(a[row&diff[j]].tolist())) for j,row in enumerate(m)]
            v.append(float(np.mean(u)))
        rows.append(v)
    q=np.quantile(np.array(rows),[.025,.5,.975],axis=0).T.tolist()
    return {"draws":B,"seed":SEED,"quantiles":[.025,.5,.975],"total_mlgs":q[0],
            "mean_distinct_other_mlgs_by_radius":dict(zip(map(str,RADII),q[1:])),
            "interpretation":"Conditional descriptive random subsampling of observed plot B; not a sampling confidence interval or test of disturbance."}

def analyze(raw):
    parsed=parse(raw)
    results={s:describe(g,xy,distances2(xy)) for s,(g,xy) in parsed.items()}
    a,b=results["PLOTA"],results["PLOTB"]
    for r in map(str,RADII):
        p,q=a["radii_m"][r],b["radii_m"][r]
        assert p["mean_distinct_other_mlgs"]<q["mean_distinct_other_mlgs"]
        assert p["mean_distinct_other_mlgs"]>q["exact_expected_mean_distinct_other_mlgs_rarefied_n271"]
    assert abs(b["exact_expected_rarefied_mlg_count_n271"]-191.481689227847)<1e-9
    g,xy=parsed["PLOTB"]
    return {"status":"posthoc_original_data_two_plot_description","source_sha256":SHA,
       "plots":results,"plotB_thinning":random_thinning(g,distances2(xy)),
       "limitations":["Both plots 20x20 m, sample grid includes boundary points 0..20; raw observed point geometry only.",
       "One plot per habitat; spatially dependent ramets, pollution/disturbance/habitat confounded; no population-level treatment inference.",
       "MLGs are exact unphased eight-locus matches; no sex/flowering, effective pollen transport, compatibility or parentage linked.",
       "Rarefaction uniformly samples actual Plot B points without replacement, not a simulation of observed disturbance or mortality.",
       "Point-weighted observed genetic neighbourhood is not adult population density, genetic diversity of all shoots, or reproductive fitness."]}

if __name__=="__main__":
    assert inclusion(10,5,1)==.5 and inclusion(10,10,1)==1.
    print(json.dumps(analyze(SOURCE.read_bytes()),indent=2,sort_keys=True,allow_nan=False))
