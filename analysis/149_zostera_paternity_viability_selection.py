#!/usr/bin/env python3
"""Post-hoc audit of viability-dependent coverage of realized paternity.
Original published data 10.5061/dryad.dfn2z358x. No biological causal fit.
"""
import argparse,csv,hashlib,io,json,statistics
from pathlib import Path
from collections import defaultdict
FILES={
 "viability":("Slim_viability_by_spathe.csv","a673af844fb2bf14282734f6848b0038dfab6657503dcd62237c18aaaf9f55b3"),
 "published":("by_spathe_dataset_slim.csv","ce02d8e5404a270177a82bc29910542406b2bbf25e4839dbc19ca0bc07746a14"),
 "high_locus":("reduced_by_spathe.csv","15e34fc4483793a840ad20c35c898145a050b2f65d0512b10636b8fbb938a105")}
KEY=("Site","Maternal ID","Rhipidium","Spathe")
def load(root,which):
    name,sha=FILES[which];raw=(root/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("Source member checksum changed: "+name)
    out={}
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        k=tuple(int(row[x]) for x in KEY);n=int(row["Seeds"]);v=int(row["Viable Seeds"])
        if k in out or not 0<=v<=n or n<=0:raise ValueError("Unexpected key/count")
        out[k]=(n,v) if which=="viability" else (n,v,int(row["Genotyped Seeds"]),int(row["Sires"]))
        if which!="viability":
            assert 1<=out[k][3]<=out[k][2]<=n
    return out
def summarize(rows):
    return dict(spathes=len(rows),seeds=sum(n for n,v in rows),
        viable=sum(v for n,v in rows),nonviable=sum(n-v for n,v in rows),
        all_nonviable=sum(v==0 for n,v in rows),
        mean_spathe_viability=statistics.mean(v/n for n,v in rows) if rows else None)
def compare(v,p):
    if not p.keys()<=v.keys():raise ValueError("Nonmatching paternity keys")
    if any(p[k][0]!=v[k][0] for k in p):raise ValueError("Total seed denominator disagreement")
    inside=set(p);outside=set(v)-inside
    def subset(keys):return summarize([v[k] for k in sorted(keys)])
    def strata(idx):
        return {str(z):{name:subset({k for k in group if k[idx]==z}) for name,group in [("included",inside),("excluded",outside)]} for z in sorted({k[idx] for k in v})}
    moms=defaultdict(lambda:[[],[]])
    for k,(n,s) in v.items():moms[k[:2]][int(k in inside)].append(s/n)
    diff=[statistics.mean(b)-statistics.mean(a) for a,b in moms.values() if a and b]
    bands=[]
    for lo,hi,label in [(-1,0,"zero"),(0,.25,"0_to_25"),(.25,.5,"25_to_50"),(.5,.75,"50_to_75"),(.75,1,"75_to_100_exclusive"),(1,1,"all_viable")]:
        eligible={k for k,(n,s) in v.items() if ((s/n==1) if lo==hi==1 else (lo<s/n<=hi and (label!="75_to_100_exclusive" or s<n)))}
        bands.append(dict(band=label,n=len(eligible),included=len(eligible&inside)))
    return dict(included=subset(inside),excluded=subset(outside),
        source_viable_count_disagreements=sum(p[k][1]!=v[k][1] for k in p),
        genotyped_gt_viable_in_viability_table=sum(p[k][2]>v[k][1] for k in p),
        genotyped_gt_viable_in_paternity_table=sum(p[k][2]>p[k][1] for k in p),
        concordant_included=subset({k for k in p if p[k][1]==v[k][1]}),
        same_mother_with_both_groups=len(diff),same_mother_positive=sum(d>0 for d in diff),
        same_mother_equal_weight_mean_difference=statistics.mean(diff) if diff else None,
        same_mother_equal_weight_median_difference=statistics.median(diff) if diff else None,
        by_site=strata(0),by_spathe_position=strata(3),by_viability_band=bands)
def analyze(root):
    v=load(root,"viability");a=load(root,"published");b=load(root,"high_locus")
    assert (len(v),len(a),len(b))==(219,162,136)
    assert len({k[:2] for k in v})==26
    x=compare(v,a);y=compare(v,b)
    assert x["included"]["nonviable"]==53 and x["excluded"]["nonviable"]==338
    assert x["excluded"]["all_nonviable"]==23 and x["same_mother_positive"]==x["same_mother_with_both_groups"]==22
    assert x["source_viable_count_disagreements"]==22 and y["source_viable_count_disagreements"]==17
    return {"status":"posthoc_observation_selection_audit_not_causal","source_doi":"10.5061/dryad.dfn2z358x",
        "source_sha256":{k:s for k,(n,s) in FILES.items()},"viability_frame":summarize(list(v.values())),
        "published":x,"high_locus":y,
        "limitations":["All viability outcomes use the dedicated viability table; 22/162 and 17/136 matched viability count discrepancies are not silently reconciled.",
            "Published paternity cohort intentionally filters genotyping coverage. High-locus cohort is overlapping, not independent replication.",
            "Selection on viability/genotyping makes sire richness conditional on observed genotyped seeds. Nonviable seed paternity cannot be inferred; absence of a record is not zero sires.",
            "No model of causal effect of paternal diversity on viability, no inferred parentage for nonviable seeds, no independent population-level inference."]}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("external_reproductive/zostera_paternity"));a=p.parse_args()
    print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
