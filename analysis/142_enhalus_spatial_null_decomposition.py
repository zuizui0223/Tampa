#!/usr/bin/env python3
"""Post-hoc exact random-label neighbourhood diagnostic, not a disturbance test."""
import collections, hashlib, io, json, math, itertools, argparse
from pathlib import Path
import numpy as np
import openpyxl
SHA='10e1465ac9255ad2d873d6142386b5140320740ebc660196b4a9eb0e2251c959'
RADII=(1,2,4,8)
B=4999
SEED=2026112402

def parse(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA: raise ValueError('source hash drift')
    w=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    if w.sheetnames!=['PLOTA','PLOTB']:raise ValueError('sheet roster')
    result={}
    for s,n,G,pop in zip(w,[271,395],[214,255],['p1','p2']):
        rows=list(s.values)
        if rows[2][:2]!=('ind','pop') or rows[2][19:21]!=('x','y'):raise ValueError('header')
        gen=[];xy=[];ids=set()
        for r in rows[3:]:
            if r[0] in ids or r[1]!=pop:raise ValueError('id or population')
            ids.add(r[0]); a=r[2:18]; q=r[19:21]
            if len(a)!=16 or not all(isinstance(v,int) and v>0 for v in a):raise ValueError('alleles')
            if not all(isinstance(v,int) and 0<=v<=20 for v in q):raise ValueError('coordinates')
            gen.append(tuple(tuple(sorted(a[i:i+2])) for i in range(0,16,2)));xy.append(q)
        if len(gen)!=n or len(set(gen))!=G or len(set(xy))!=n:raise ValueError('counts')
        ids={g:i for i,g in enumerate(dict.fromkeys(gen))}
        result[s.title]=(np.array([ids[g] for g in gen]),np.array(xy))
    return result

def null_expected_unique(sizes,m):
    # Uniformly permute fixed genotype labels over fixed coordinates. Focal label
    # is drawn from N individuals, and m neighbours are selected from N-1.
    N=sum(sizes); den=math.comb(N-1,m)
    return sum((1-k/N)*(1-(math.comb(N-1-k,m)/den if N-1-k>=m else 0)) for k in sizes)

def describe(g,xy,seed):
    n=len(g); sizes=list(collections.Counter(g.tolist()).values()); same_p=sum(k*(k-1) for k in sizes)/(n*(n-1))
    d2=np.sum((xy[:,None,:]-xy[None,:,:])**2,axis=2)
    edges=np.where(np.triu((d2>0)&(d2<=max(RADII)**2),1)); ed2=d2[edges]
    edge_masks=np.array([ed2<=r*r for r in RADII]); obs=(g[edges[0]]==g[edges[1]])
    pair_counts=edge_masks@obs.astype(int); expected_pairs=edge_masks.sum(axis=1)*same_p
    rng=np.random.default_rng(seed); draws=np.empty((B,len(RADII)),int)
    for i in range(B):
        p=rng.permutation(g); same=(p[edges[0]]==p[edges[1]])
        draws[i]=edge_masks@same.astype(int)
    out={}
    for j,r in enumerate(RADII):
        m=(d2>0)&(d2<=r*r); degree=m.sum(axis=1); mean_deg=float(degree.mean());
        u=np.array([len(set(g[row & (g!=g[i])].tolist())) for i,row in enumerate(m)])
        expectation={k:null_expected_unique(sizes,k) for k in set(degree.tolist())}
        null=np.array([expectation[k] for k in degree]); U=float(u.mean()); E=float(null.mean())
        out[str(r)]={'mean_degree':mean_deg,'observed_distinct_other_mlgs':U,'random_label_expected_distinct_other_mlgs':E,
            'composition_penalty':mean_deg-E,'spatial_arrangement_penalty':E-U,
            'spatial_deficit_fraction_of_null':1-U/E,
            'observed_same_mlg_pairs':int(pair_counts[j]),'random_label_expected_same_mlg_pairs':float(expected_pairs[j]),
            'same_pair_observed_expected_ratio':float(pair_counts[j]/expected_pairs[j]),
            'same_pair_permutation_p_one_sided_unadjusted':float((1+np.count_nonzero(draws[:,j]>=pair_counts[j]))/(B+1)),
            'same_pair_random_label_quantiles':np.quantile(draws[:,j],[.025,.5,.975]).tolist()}
    return out

def analyze(raw):
    parsed=parse(raw); p={s:describe(g,xy,SEED+i) for i,(s,(g,xy)) in enumerate(parsed.items())}; a,b=p['PLOTA'],p['PLOTB']; gap={}
    for r in map(str,RADII):
        x,y=a[r],b[r]; D=y['mean_degree']-x['mean_degree']; C=y['composition_penalty']-x['composition_penalty']; S=y['spatial_arrangement_penalty']-x['spatial_arrangement_penalty']; U=y['observed_distinct_other_mlgs']-x['observed_distinct_other_mlgs']
        assert abs(U-(D-C-S))<1e-10
        gap[r]={'observed_B_minus_A':U,'neighbour_degree_gap':D,'global_clone_composition_penalty_gap':C,'spatial_arrangement_penalty_gap':S,'fraction_degree_gap_offset_by_total_redundancy_gap':(C+S)/D}
    return {'status':'posthoc_two_plot_random_label_diagnostic','source_sha256':SHA,'permutation_draws_per_plot':B,'seed_base':SEED,'plots':p,'B_minus_A_accounting':gap,'boundaries':['Each habitat represented by one plot; no disturbance treatment inference.','Uniform label shuffling conditions on sampled coordinates and global clone counts; intentionally breaks spatial autocorrelation; not a realistic demographic null.','Composition and arrangement penalties are arithmetic relative to specified reference, not causal independent effects.','Other MLGs are not verified flowering opposite-sex mates.','Permutation p values are unadjusted plot-specific spatial association diagnostics, not across-meadow tests.']}

def selftest():
    g=[0,0,1,2]; N=len(g)
    for m in range(N):
        actual=[len(set(p[1:m+1])-{p[0]}) for p in itertools.permutations(g)]
        assert abs(np.mean(actual)-null_expected_unique([2,1,1],m))<1e-12
    for m in range(4):assert abs(null_expected_unique([1]*4,m)-m)<1e-12
    assert null_expected_unique([4],3)==0

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path('reproductive_input/yu/Ramets For Two plots.xlsx'));args=ap.parse_args();selftest();print(json.dumps(analyze(args.input.read_bytes()),indent=2,sort_keys=True,allow_nan=False))
