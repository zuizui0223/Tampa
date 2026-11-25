#!/usr/bin/env python3
"""Source-locked posthoc matched-tank audit of Laukaityte et al. (2025).
Burial (among counted seeds) and germination count are different endpoints.
Not a new heatwave causal fit or genotype/seed-bank survival analysis.
"""
import argparse,csv,hashlib,io,itertools,json,math,statistics as st,urllib.request
from collections import defaultdict
from pathlib import Path
SOURCE_COMMIT="ea4679016e8bddcd083cd93fe2fd6f33b6b1025e"
SOURCE_BLOB="cb12f65a477078f3980a381b5251a635db312d53"
URL=f"https://raw.githubusercontent.com/SimonaLaukaityte/heatwave-on-animal-plant-interactions/{SOURCE_COMMIT}/data.txt"
FAUNA=("NO","COCKLE","SHRIMP","WORM","MIX")
TEMPS=("COLD","WARM")
def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"Tampa-bioturbation-source-audit/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=45) as r:raw=r.read(200001)
    if len(raw)>200000:raise ValueError("source size")
    return raw
def parse(raw):
    if hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()!=SOURCE_BLOB:raise ValueError("source blob drift")
    try:s=raw.decode("utf-8-sig")
    except UnicodeDecodeError:s=raw.decode("latin-1")
    rows=[];ids=set()
    for row in csv.DictReader(io.StringIO(s),delimiter="\t"):
        key=tuple(map(int,row["Sample ID"].split(".")));run,block,core=key
        assert key not in ids and run==int(row["run"]) and 1<=block<=16 and 1<=core<=5
        ids.add(key)
        n,g=int(row["seed_nb"]),int(row["germ_nb"])
        ns=[int(row[f"{i}_nb"]) for i in range(6)]
        gs=[int(row[f"{i}_germ_nb"]) for i in range(6)]
        assert sum(ns)==n>0 and sum(gs)==g and all(0<=b<=a for a,b in zip(ns,gs))
        f,t=row["fauna"],row["temp"]
        assert f in FAUNA and t in TEMPS
        rows.append(dict(key=key,run=run,block=block,fauna=f,temp=t,n=n,g=g,s=ns[0],sg=gs[0],reported_rate=float(row["germinated_perc"]) if row["germinated_perc"].strip() else None))
    assert len(rows)==240
    # Author R code explicitly selects rows 81:240 (runs 2 and 3 in deposit).
    a=rows[80:]
    assert [r["run"] for r in rows]==[1]*80+[2]*80+[3]*80
    assert all(r["reported_rate"] is not None for r in a)
    return a
def summary(a):
    N,G,S,SG=(sum(r[k] for r in a) for k in ("n","g","s","sg"))
    return dict(cores=len(a),counted_seeds=N,germinated=G,buried=N-S,buried_germinated=G-SG,surface=S,surface_germinated=SG,
      mean_core_buried_fraction=st.mean((r["n"]-r["s"])/r["n"] for r in a),pooled_buried_fraction=(N-S)/N,
      germinated_per_counted=G/N,mean_germinated_count=G/len(a),
      germinated_per_nominal_10_introduced=G/(10*len(a)),buried_germinated_per_counted=(G-SG)/(N-S),surface_germinated_per_counted=SG/S,
      counted_above_10=sum(r["n"]>10 for r in a),counted_below_10=sum(r["n"]<10 for r in a),
      deposited_rate_differs_from_g_over_n=sum(abs(r["reported_rate"]-r["g"]/r["n"])>1e-7 for r in a))
def exact_flip(d):
    obs=abs(sum(d));ge=0
    for signs in itertools.product((-1,1),repeat=len(d)):
        ge+=abs(sum(x*s for x,s in zip(d,signs)))>=obs-1e-10
    return ge/2**len(d)
def analyze(raw):
    a=parse(raw);blocks=defaultdict(dict)
    for r in a:
        k=(r["run"],r["temp"],r["block"]);assert r["fauna"] not in blocks[k]
        blocks[k][r["fauna"]]=r
    assert len(blocks)==32 and all(set(v)==set(FAUNA) for v in blocks.values())
    groups={f"{t}|{f}":summary([r for r in a if r["temp"]==t and r["fauna"]==f]) for t in TEMPS for f in FAUNA}
    assert all(v["cores"]==16 for v in groups.values())
    tests=[];accounting={}
    for t in TEMPS:
        bs=[(k,v) for k,v in sorted(blocks.items()) if k[1]==t]
        assert len(bs)==16 and all(sum(k[0]==run for k,v in bs)==8 for run in (2,3))
        for f in FAUNA[1:]:
            for name,fn in (("buried_fraction",lambda r:(r["n"]-r["s"])/r["n"]),("germinated_count",lambda r:r["g"])):
                d=[fn(v[f])-fn(v["NO"]) for k,v in bs]
                sens=[fn(v[f])-fn(v["NO"]) for k,v in bs if v[f]["n"]<=10 and v["NO"]["n"]<=10]
                tests.append(dict(temp=t,fauna=f,endpoint=name,paired_tanks=len(d),mean_difference=st.mean(d),
                    positive_tanks=sum(x>1e-10 for x in d),negative_tanks=sum(x<-1e-10 for x in d),exact_two_sided_swap_p=exact_flip(d),
                    run_means={str(run):st.mean(x for x,(k,v) in zip(d,bs) if k[0]==run) for run in (2,3)},
                    posthoc_exclude_overcount_pairs_n=len(sens),posthoc_exclude_overcount_pairs_mean=st.mean(sens)))
            x,y=groups[f"{t}|NO"],groups[f"{t}|{f}"]
            p,q=x["pooled_buried_fraction"],y["pooled_buried_fraction"]
            u,v=x["buried_germinated_per_counted"],y["buried_germinated_per_counted"]
            w,z=x["surface_germinated_per_counted"],y["surface_germinated_per_counted"]
            composition=(q-p)*(u+v-w-z)/2
            conditional=(p+q)/2*(v-u)+(1-(p+q)/2)*(z-w)
            delta=y["germinated_per_counted"]-x["germinated_per_counted"]
            assert math.isclose(composition+conditional,delta,abs_tol=1e-12)
            accounting[f"{t}|{f}"]=dict(pooled_germinated_per_counted_difference=delta,burial_composition_component=composition,conditional_rate_component=conditional)
    maximum=0.
    for i,r in enumerate(sorted(tests,key=lambda r:r["exact_two_sided_swap_p"])):
        maximum=max(maximum,(len(tests)-i)*r["exact_two_sided_swap_p"]);r["holm_p"]=min(1.,maximum)
    total=summary(a);assert total["counted_seeds"]==1529 and total["germinated"]==171
    assert total["counted_above_10"]==34 and total["counted_below_10"]==61 and total["deposited_rate_differs_from_g_over_n"]==75
    assert {(r["temp"],r["fauna"],r["endpoint"]) for r in tests if r["holm_p"]<.05}=={("COLD","COCKLE","buried_fraction"),("WARM","COCKLE","buried_fraction"),("WARM","MIX","buried_fraction")}
    return dict(status="posthoc_source_locked_bioturbation_stage_diagnostic",source_url=URL,source_git_blob=SOURCE_BLOB,
      paper_doi="10.1007/s00442-025-05662-y",source_code_commit="14286c76bf40a5416060b32e29c9e57f9ec51bd2",total=total,groups=groups,matched_tank_tests=tests,pooled_arithmetic_accounting=accounting,
      limits=["Use treatment assignment labels, not observed fauna counts. Two runs, 16 five-core tanks each; temperature treatments share larger water baths. No independent heatwave interaction test.",
      "Post-outcome 16 tests: two endpoints x four fauna contrasts x two temperatures; exact pairwise swaps conditional on within-tank random assignment, Holm correction. Not a refit of published model; no equivalence conclusion for nonsignificant germinated counts.",
      "Nominal ten introduced per core, but 34 counted totals >10 and 61 <10; cannot classify difference as seed loss or reconstruct true individual fate. Deposited germinated_perc differs from germinated/count total in 75 cores; may have different denominators, not silently repaired. Use counts and explicitly named denominators.",
      "Composition and conditional rate are descriptive algebra on end-of-experiment locations, not causal mediation, chronological seed trajectories, or germination probabilities conditional on initial burial. Non-germinated counts include unresolved viability; no genotype measurements.",
      "Excluding overcount pairs is a post-outcome sensitivity, not independent verification. Original study already established temperature-dependent non-trophic interactions."])
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path);a=p.parse_args()
    assert exact_flip([1,1])==.5 and exact_flip([0,0])==1.
    print(json.dumps(analyze(a.input.read_bytes() if a.input else fetch()),indent=2,sort_keys=True,allow_nan=False))
