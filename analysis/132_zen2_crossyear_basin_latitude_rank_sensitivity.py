#!/usr/bin/env python3
"""Post-hoc ocean-basin/latitude robustness of ZEN2 2014->2015 shoot ranks.

The original 2014/2015 sources and crossyear geography/site contrasts were
previously SHA-verified and frozen in PR171. This is a post-outcome
SENSITIVITY added after discovering a strong 14-site crossyear rank
correlation; not an independent replication, predeclared primary, causality
test or globally general phenomenon.
"""
from __future__ import annotations
import argparse,importlib.util,json,math,random,statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"results/zen2_2014_prior_state_2015_trophic_risk_verified_20261124.json"
GEO=ROOT/"results/zen2_2014_2015_geographic_link_verified_20261124.json"
SEED=202611241432
PERM=20000

def rank(vals):
    inds=sorted(range(len(vals)),key=lambda i:vals[i])
    out=[0.]*len(vals);i=0
    while i<len(inds):
        j=i+1
        while j<len(inds) and vals[inds[j]]==vals[inds[i]]:j+=1
        mid=(i+1+j)/2
        for k in inds[i:j]:out[k]=mid
        i=j
    return out

def pearson(a,b):
    if len(a)!=len(b) or len(a)<4:raise ValueError("Insufficient observation pairs")
    mx=statistics.mean(a);my=statistics.mean(b)
    c=sum((x-mx)*(y-my) for x,y in zip(a,b))
    v=sum((x-mx)**2 for x in a);w=sum((y-my)**2 for y in b)
    if v<=0 or w<=0:raise ValueError("Zero variance")
    return c/math.sqrt(v*w)

def ocean(lon):
    # Broad geographies in the original 2021 comparative experiment:
    # Western + Eastern Pacific vs Atlantic + Mediterranean.
    if lon <= -100 or lon >= 100:return "Pacific"
    if -100 < lon < 100:return "Atlantic_Mediterranean"
    raise ValueError("Undefined ocean basin")

def analyze(pinned,geo,perm=PERM,seed=SEED):
    if pinned.get("schema")!="tampa.zen2_nearest_subsite_2014_prior_state_2015_interaction_exploratory_v1":
        raise ValueError("Unexpected crossyear ecological source")
    if geo.get("schema")!="tampa.zen2_2014_2015_source_geographic_link_audit_v1":
        raise ValueError("Unexpected response-blind geography")
    if pinned.get("source_shas")!=geo.get("source_shas"):
        raise ValueError("Two source SHA registries differ")
    if len(pinned.get("candidate_sites",[]))!=14:
        raise ValueError("14-site biological frame was revised")
    loc={
        x["source_2015_site"]:x["source_2015_lat_lon"]
        for x in geo["candidates"] if x["eligible_as_prior_site_context"]
    }
    if set(loc)!={x["site_code"] for x in pinned["candidate_sites"]}:
        raise ValueError("Outcome site and geography link cohorts disagree")
    records=[]
    for x in pinned["candidate_sites"]:
        s=x["site_code"];lat,lon=loc[s]
        if not math.isfinite(lat) or not math.isfinite(lon):
            raise ValueError("Bad source lat/lon")
        records.append({"site":s,"ocean":ocean(lon),"latitude":lat,
                        "shoots2014":x["year2014_shoot_density"],
                        "shoots2015":x["year2015_ambient_shoot_density"]})
    groups=defaultdict(list)
    for i,z in enumerate(records):groups[z["ocean"]].append(i)
    if {k:len(v) for k,v in groups.items()}!={"Pacific":8,"Atlantic_Mediterranean":6}:
        raise ValueError("Unexpected 8/6-basin layout")
    x=rank([r["shoots2014"] for r in records])
    y=rank([r["shoots2015"] for r in records])
    lat=rank([r["latitude"] for r in records])
    observed=pearson(x,y)
    past_lat=pearson(x,lat);future_lat=pearson(y,lat)
    partial=(observed-past_lat*future_lat)/math.sqrt((1-past_lat**2)*(1-future_lat**2))
    rng=random.Random(seed);exceed=0
    for _ in range(perm):
        y_null=y.copy()
        for indices in groups.values():
            permuted=[y_null[i] for i in indices]
            rng.shuffle(permuted)
            for i,value in zip(indices,permuted):y_null[i]=value
        exceed+=abs(pearson(x,y_null))>=abs(observed)
    ocean_stats={}
    for key,indices in groups.items():
        a=[records[i]["shoots2014"] for i in indices]
        b=[records[i]["shoots2015"] for i in indices]
        ocean_stats[key]={
          "n_source_nearest_subsites":len(indices),
          "site_codes":[records[i]["site"] for i in indices],
          "within_basin_spearman_r":pearson(rank(a),rank(b))
        }
    return {
        "schema":"tampa.zen2_crossyear_basin_latitude_rank_sensitivity_v1",
        "evidence_class":"response_open_posthoc_basin_and_latitude_reanalysis",
        "source_ledger_files":[str(DATA.relative_to(ROOT)),str(GEO.relative_to(ROOT))],
        "same_14_sites_original_spearman_r":observed,
        "latitude_rank_r2014":past_lat,
        "latitude_rank_r2015":future_lat,
        "partial_spearman_rank_correlation_given_latitude":partial,
        "basin_stratified_2015_label_permutation_two_sided_p":(exceed+1)/(perm+1),
        "basin_stratified_permutations":perm,
        "permutation_seed":seed,
        "ocean_category_counts":{k:len(v) for k,v in groups.items()},
        "within_basin_results":ocean_stats,
        "source_site_geographies":records,
        "strict_limits":[
            "Basin categorization follows prior 2021 Atlantic/Mediterranean versus Pacific framing; it is derived here from original coordinates.",
            "This sensitivity was selected after the strong overall r was seen: it is not an independent confirmatory p value.",
            "Basin-stratified random pairing preserves large basin differences but not spatial autocorrelation or independent-environment gradients within basins.",
            "Partial rank correlation controlling latitude is descriptive; with fourteen sites it cannot rule out coastline, habitat, climate or lab-method confounding.",
            "The 2014/2015 surveys are geographically nearby but not same permanent meadow quadrats.",
            "Spatial rank stability cannot be called biological persistence/resilience, causal time memory or new evidence that trophic interactions are intrinsically variable.",
        ]
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,default=None)
    args=ap.parse_args()
    data=analyze(json.loads(DATA.read_text()),json.loads(GEO.read_text()))
    txt=json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(txt,encoding="utf8")
    else:print(txt,end="")

if __name__=="__main__":
    main()
