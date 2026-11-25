#!/usr/bin/env python3
"""Source-locked, response-open diagnostics: realized paternity and local clone redundancy.
Different species/studies; no joint causal model, mating-distance fit, or independent treatment replication.
"""
import argparse,csv,hashlib,io,json,math,itertools
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import openpyxl

PATS={
 "unfiltered":("by_spathe_dataset.csv","d51472c95c184ce7e497151a78e29ee8a80609af31252d18c95bbd8477574c8d",212,972,36),
 "published":("by_spathe_dataset_slim.csv","ce02d8e5404a270177a82bc29910542406b2bbf25e4839dbc19ca0bc07746a14",162,844,26),
 "high_locus":("reduced_by_spathe.csv","15e34fc4483793a840ad20c35c898145a050b2f65d0512b10636b8fbb938a105",136,688,26),
}
SPATIAL_SHA="a5d01c36ceedf0772f2835fd4e45203cae01819b87fb46aff29da85c41560292"
def verified(p,sha):
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("source member drift "+str(p))
    return raw

def paternity(root):
    results={}; records={}
    for name,(file,sha,n,ng,nm) in PATS.items():
        rr=list(csv.DictReader(io.StringIO(verified(root/"zostera_paternity"/file,sha).decode("utf-8-sig"))))
        by={}
        for r in rr:
            key=tuple(int(r[k]) for k in ("Site","Maternal ID","Rhipidium","Spathe"))
            if key in by:raise ValueError("duplicate spathe")
            S,G,O,F=(int(r[k]) for k in ("Sires","Genotyped Seeds","Outcrossed Seeds","Selfed Seeds"))
            assert 1<=S<=G and O>=0 and F>=0 and O+F==G
            assert abs(float(r["Outcrossing Rate"])-O/G)<=.00501
            by[key]=(S,G,O,F)
        assert len(by)==n and sum(v[1] for v in by.values())==ng
        assert len({k[:2] for k in by})==nm
        q={k:v for k,v in by.items() if v[1]>=2 and v[3]==0}
        one={k:v for k,v in q.items() if v[0]==1}
        results[name]={"source_sha256":sha,"spathe_count":n,"genotyped_seed_count":ng,"maternal_shoots":nm,
            "all_outcross_min2":len(q),"all_outcross_single_sire":len(one),
            "single_sire_fraction":len(one)/len(q),
            "maternal_shoots_all_outcross_min2":len({k[:2] for k in q}),
            "maternal_shoots_single_sire_all_outcross_min2":len({k[:2] for k in one}),
            "sites":{s:{"eligible":sum(k[0]==s for k in q),"single_sire":sum(k[0]==s for k in one)} for s in (1,2,3)},
            "all_outcross_exactly5_sire_histogram":dict(sorted(Counter(v[0] for v in q.values() if v[1]==5).items()))}
        records[name]=by
    a,b=records["published"],records["high_locus"]
    common=a.keys()&b.keys();q=[k for k in common if all(t[k][1]>=2 and t[k][3]==0 for t in (a,b))]
    return {"source_doi":"10.5061/dryad.dfn2z358x","paper_doi":"10.1002/ece3.11608","datasets":results,
            "matched_published_high_locus":{"matched_spathes":len(common),"both_all_outcross_min2":len(q),
            "both_single_sire":sum(a[k][0]==b[k][0]==1 for k in q),
            "published_single_sire":sum(a[k][0]==1 for k in q),"high_locus_single_sire":sum(b[k][0]==1 for k in q),
            "both_same_genotyped_count":sum(a[k][1]==b[k][1] for k in q)},
            "limits":"Existing COLONY output, not a paternity refit; three overlapping cohorts, not three studies. All-outcross refers to genotyped seeds only. Sire number is observed/inferred richness, not effective sire number or measured pollen movement. Counts, not rounded rates. No cross-sheet pooling."}

def ranks(x):
    x=np.array(x);o=np.argsort(x,kind="stable");v=np.empty(len(x));i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[o[j]]==x[o[i]]:j+=1
        v[o[i:j]]=(i+j-1)/2
        i=j
    return v
def rho(x,y):return float(np.corrcoef(ranks(x),ranks(y))[0,1])
def exp_richness(sizes,n):
    N=sum(sizes);den=math.comb(N,n)
    return sum(1-(math.comb(N-k,n)/den if N-k>=n else 0) for k in sizes)

def spatial(root):
    raw=verified(root/"zostera_noltei_s004.xlsx",SPATIAL_SHA)
    w=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    assert w.sheetnames==["Zn RF msat data"]
    rows=list(w.active.values);w.close()
    assert rows[6][:4]==("Sample.ID","Genet","longitude","latitude")
    groups=defaultdict(list); coords={};ids=set();pool=[]
    for r in rows[7:]:
        id,g,lon,lat=r[:4]
        assert isinstance(id,str) and id[-1] in "ABCD" and id not in ids and isinstance(g,int)
        ids.add(id);p=id[:-1]
        assert -180<=lon<=180 and -90<=lat<=90
        if p in coords:assert coords[p]==(lon,lat)
        coords[p]=(lon,lat);groups[p].append(g);pool.append(g)
    sizes=list(Counter(pool).values());N=len(pool)
    assert N==3185 and len(sizes)==1999 and len(groups)==797 and len(set(coords.values()))==797
    assert Counter(map(len,groups.values()))=={4:794,3:3}
    complete=sorted(k for k,v in groups.items() if len(v)==4)
    x=np.array([groups[k] for k in complete]);loc=np.array([len(set(r)) for r in x])
    same=sum(sum(v*(v-1)//2 for v in Counter(g).values()) for g in groups.values())
    pairs=sum(len(g)*(len(g)-1)//2 for g in groups.values())
    p0=sum(k*(k-1) for k in sizes)/(N*(N-1))
    E=exp_richness(sizes,4)
    pair_idx=list(itertools.combinations(range(4),2))
    def sc(z):return sum(int(np.count_nonzero(z[:,i]==z[:,j])) for i,j in pair_idx)
    rng=np.random.default_rng(20261124);obs=sc(x);draws=[]
    for _ in range(4999):draws.append(sc(rng.permutation(pool)[:x.size].reshape(x.shape)))
    ll=np.radians(np.array([coords[k] for k in complete]));lon,lat=ll[:,0],ll[:,1]
    v=np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
    d=2*6371008.8*np.arcsin(np.clip(np.linalg.norm(v[:,None,:]-v[None,:,:],axis=2)/2,0,1))
    np.fill_diagonal(d,np.inf);order=np.argsort(d,axis=1,kind="stable");near={}
    for k in (1,5,10):
        G=[];V=[]
        for i,ix in enumerate(order[:,:k]):
            other=set(x[ix].ravel());here=set(x[i])
            G.append(len(other));V.append(len(other-here))
        near[k]={"median_farthest_selected_quadrat_m":float(np.median(d[np.arange(len(x)),order[:,k-1]])),
                 "mean_external_distinct_genets":float(np.mean(G)),"mean_external_genets_not_in_focal":float(np.mean(V)),
                 "spearman_local_richness_vs_external_richness":rho(loc,G),
                 "spearman_local_richness_vs_external_novel_genets":rho(loc,V),
                 "mean_external_richness_by_local_count":{n:float(np.mean(np.array(G)[loc==n])) for n in (1,2,3,4)}}
    return {"paper_doi":"10.1371/journal.pone.0199275","source_sha256":SPATIAL_SHA,"sample_units":N,"published_genet_labels":len(sizes),
        "observed_quadrat_ids":len(groups),"complete_quadrats":len(complete),"three_sample_quadrats":3,
        "complete_quadrat_genet_count_histogram":dict(Counter(map(int,loc))),
        "mean_genets_complete_quadrat":float(loc.mean()),"random_label_expected_genets_complete_quadrat":E,
        "mean_distinct_other_genets_per_focal":float(loc.mean()-1),"random_label_expected_other_genets":E-1,
        "relative_deficit_other_genets":1-(float(loc.mean())-1)/(E-1),
        "all_quadrat_same_genet_pairs":same,"all_quadrat_pairs":pairs,"same_genet_fraction":same/pairs,
        "random_label_same_genet_pair_fraction":p0,"expected_same_genet_pairs":pairs*p0,
        "complete_quadrat_permutation":{"observed_same_pairs":obs,"draws":4999,"seed":20261124,
        "quantiles":np.quantile(draws,[.025,.5,.975]).tolist(),"one_sided_p":(1+sum(z>=obs for z in draws))/5000},
        "genets_at_multiple_sampled_quadrats":len({g for g,n in Counter(g for q in groups.values() for g in set(q)).items() if n>1}),
        "nearest_complete_quadrats":near,
        "limits":"4 ramet sample units per 4m2 quadrat, each may contain 3-4 shoots; quadrat coordinates not individual coordinates. 797 genotyped quadrats in workbook, original 803 occupied. Global fixed-label shuffling is not a local demographic or dispersal model. Nearest K selected occupied quadrats have equal sampled effort, not equal radius or abundance; overlapping spatial neighborhoods, no inferential p for rank correlations. No verified flowering/mates/pollen flow."}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("external_reproductive"));a=p.parse_args()
    result={"status":"posthoc_original_source_descriptive_cross_species_diagnostics","paternity":paternity(a.root),"spatial":spatial(a.root)}
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
