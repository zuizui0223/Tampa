#!/usr/bin/env python3
"""Sample-standardized marker profiles and allele presence, not parentage."""
import argparse,csv,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
SHA="3081acdbd8b7bc330851ebf2057a4d4a7f279d8c3484e2c38f7c78494d6aca9d"
EXPECTED=[49,50,50,50,29,31,27,31,34,30]
LOCI=["PaA1","PaA105","PaA120","PaB6","PaB8","PaB112","PaD113"]
def parse(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("source drift")
    r=list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
    assert r[2][:7]==["Pop #","Sample site","Latitude (S)","Longitude (E)","Sample code","Year collected","Life stage"]
    assert r[2][7:21]==[f"Locus {l}-{a}" for l in LOCI for a in "ab"]
    groups=defaultdict(list);meta={};ids=set()
    for row in r[4:]:
        if not any(row):continue
        pop=int(row[0]);code=row[4];key=(row[1].split(",")[0],int(row[5]),row[6].lower())
        if code in ids or (pop in meta and key!=meta[pop]) or any(row[21:]):raise ValueError("sample or schema mismatch")
        ids.add(code);meta[pop]=key
        g=tuple(tuple(sorted(map(int,row[i:i+2]))) for i in range(7,21,2))
        if any(min(x)<0 or (0 in x and x!=(0,0)) for x in g):raise ValueError("invalid marker call")
        groups[pop].append(g)
    assert [len(groups[i]) for i in range(1,11)]==EXPECTED
    return groups,meta
def complete(g):return [x for x in g if all(0 not in p for p in x)]
def alleles(g):return {(i,a) for x in g for i,p in enumerate(x) for a in p if a!=0}
def richness(freq,N,n):
    assert 1<=n<=N and all(1<=v<=N for v in freq.values())
    den=math.comb(N,n)
    return sum(1-(math.comb(N-v,n)/den if N-v>=n else 0) for v in freq.values())
def afreq(g):return Counter(a for x in g for a in sorted(alleles([x])))
def summary(g,n):
    return {"n":len(g),"exact_marker_profiles":len(set(g)),"observed_marker_alleles":len(alleles(g)),
        "rarefied_profiles":richness(Counter(g),len(g),n),"rarefied_marker_alleles":richness(afreq(g),len(g),n)}
def contrast_curve(a,b):
    x,y=afreq(a),afreq(b)
    return {str(k):richness(y,len(b),k)-richness(x,len(a),k) for k in range(2,min(len(a),len(b))+1)}
def analyze(raw):
    groups,meta=parse(raw);c={i:complete(g) for i,g in groups.items()};uniq={i:list(dict.fromkeys(g)) for i,g in c.items()}
    n=min(map(len,c.values()));u=min(map(len,uniq.values()))
    adult_all=set().union(*(alleles(groups[i]) for i in range(1,5)))
    paired={5:1,6:1,7:3,8:3,9:4,10:4};out={}
    for i in groups:
        out[str(i)]={"site":meta[i][0],"year":meta[i][1],"stage":meta[i][2],"raw_n":len(groups[i]),"incomplete_n":len(groups[i])-len(c[i]),"complete":summary(c[i],n),"profile_equal":summary(uniq[i],u),"all_available_alleles":len(alleles(groups[i]))}
    comp={}
    for i,j in paired.items():
        a,b=c[j],c[i];aa,bb=alleles(groups[j]),alleles(groups[i]);sa,sb=out[str(j)],out[str(i)]
        comp[str(i)]={"adult_pop":j,"adult_year":meta[j][1],"seedling_year":meta[i][1],
            "delta_rarefied_profiles":sb["complete"]["rarefied_profiles"]-sa["complete"]["rarefied_profiles"],
            "delta_rarefied_alleles":sb["complete"]["rarefied_marker_alleles"]-sa["complete"]["rarefied_marker_alleles"],
            "delta_profile_equal_alleles":sb["profile_equal"]["rarefied_marker_alleles"]-sa["profile_equal"]["rarefied_marker_alleles"],
            "individual_allele_delta_curve":contrast_curve(a,b),"profile_equal_allele_delta_curve":contrast_curve(uniq[j],uniq[i]),
            "exact_seedling_profile_absent_from_complete_local_adults":sum(x not in set(a) for x in b),
            "seedling_alleles_absent_local_adult":sorted(bb-aa),
            "of_these_present_other_sampled_adults":sorted((bb-aa)&adult_all),
            "of_these_absent_all_sampled_adults":sorted(bb-adult_all),
            "adult_alleles_absent_seedling":sorted(aa-bb),
            "seedling_profiles_with_at_least_one_allele_unseen_locally":sum(bool(alleles([x])-aa) for x in b),
            "seedling_profiles_with_at_least_one_allele_unseen_all_adults":sum(bool(alleles([x])-adult_all) for x in b)}
    return {"status":"posthoc_marker_profile_and_allele_sample_comparison","source_sha256":SHA,"individual_rarefaction_n":n,"profile_equal_rarefaction_n":u,"populations":out,"matched_cohorts":comp,
      "cautions":["Only two allele columns per locus; README notes triploids without sample-level ploidy. No diploid frequencies, HWE, Ho, He, parentage or inferred actual genet identity. Exact complete recorded profiles only, not GenAlEx clone reconciliation.","Exact hypergeometric expectation for distinct profiles and locus-allele presence per individual or unique profile, not allelic richness per gene copy or confidence intervals.","Adults and seedlings noncontemporaneous; 3 sites x 2 cohorts share adults, not six independent sites or paired parents and offspring.","Unseen marker alleles do not establish immigration or new mutation. Incomplete adult coverage and marker error possible.","All available nonzero allele calls for presence/absence audit; complete individuals for rarefaction."]}
def selftest():
    assert richness(Counter({"a":2,"b":2}),4,2)==2*(1-1/6)
    assert richness(Counter({"a":4}),4,2)==1
    assert richness(Counter({"a":1,"b":1}),2,1)==1
    assert afreq([((1,1),(2,3))])==Counter({(0,1):1,(1,2):1,(1,3):1})
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=Path("external_reproductive/posidonia_adult_seedling/PaustralisRIpopgeneticsRawdata.csv"));a=ap.parse_args()
    selftest();print(json.dumps(analyze(a.input.read_bytes()),indent=2,sort_keys=True,allow_nan=False))
