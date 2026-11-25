#!/usr/bin/env python3
"""Exact finite-pool adult reference/test comparison; not migration inference."""
import argparse, importlib.util, json, math
from pathlib import Path
p=Path(__file__).with_name("146_posidonia_stage_marker_diversity.py")
s=importlib.util.spec_from_file_location("stage",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def miss(N,k,n):
    if not (0<=k<=N and 0<=n<=N):raise ValueError("invalid hypergeometric inputs")
    return math.comb(N-k,n)/math.comb(N,n) if N-k>=n else 0.

def compare(a,b,r,t):
    N,M=len(a),len(b)
    if r+t>N or t>M:raise ValueError("insufficient samples")
    ac,bc=m.afreq(a),m.afreq(b);x=y=z=0.
    for k in sorted(ac.keys()|bc.keys()):
        u,v=ac[k],bc[k]
        ref=miss(N,u,r)
        x+=ref-miss(N,u,r+t)
        term=ref*(1-miss(M,v,t));y+=term
        if u==0:z+=term
    return {"adult_reference":r,"test_size":t,"adult_withheld_expected_new_alleles":x,
            "seedling_expected_new_alleles":y,"difference":y-x,
            "seedling_new_expected_absent_full_adult_pool":z,
            "seedling_new_expected_present_full_adult_pool":y-z}

def analyze(raw):
    groups,meta=m.parse(raw);c={i:m.complete(g) for i,g in groups.items()}
    u={i:list(dict.fromkeys(g)) for i,g in c.items()};out={}
    for stage,data in [("complete_individual",c),("unique_profile",u)]:
        results={}
        for i,j in {5:1,6:1,7:3,8:3,9:4,10:4}.items():
            a,b=data[j],data[i]
            vals={str(r):compare(a,b,r,5) for r in (2,3,4,5,6)}
            results[str(i)]={"site":meta[i][0],"year":meta[i][1],"adult_year":meta[j][1],
                "adult_pool":len(a),"seedling_pool":len(b),"primary":vals["6"],
                "sensitivity_reference_size":vals}
        out[stage]=results
    return {"status":"posthoc_finite_pool_coverage_diagnostic","source_sha256":m.SHA,"results":out,
        "limits":["Adult reference 6 and disjoint adult test 5 compared with 5 independently sampled seedling records sharing adult reference. Exact finite-pool expectations, not p-values.",
        "Observed pools only; unique complete marker profiles not validated genets, two allele columns and ambiguous ploidy.",
        "Adults noncontemporaneous; no inference of immigration, parentage, or causal process.",
        "3 meadows, two cohorts per meadow sharing adults. Reference size 2..6 sensitivity with fixed test size 5."]}

def selftest():
    a=[((1,1),),((1,1),),((2,2),)];b=[((3,3),),((3,3),)]
    v=compare(a,b,1,1)
    assert abs(v["adult_withheld_expected_new_alleles"]-2/3)<1e-12
    assert v["seedling_expected_new_alleles"]==1 and v["seedling_new_expected_absent_full_adult_pool"]==1

if __name__=="__main__":
    q=argparse.ArgumentParser()
    q.add_argument("--input",type=Path,default=Path("external_reproductive/posidonia_adult_seedling/PaustralisRIpopgeneticsRawdata.csv"))
    a=q.parse_args();selftest()
    print(json.dumps(analyze(a.input.read_bytes()),indent=2,sort_keys=True,allow_nan=False))
