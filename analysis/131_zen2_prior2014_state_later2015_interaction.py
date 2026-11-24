#!/usr/bin/env python3
"""Exploratory ZEN2 2014->2015 nearest-subsite structural-state transport.

SOURCES: original SHA-frozen 2014 survey and 2015 tethered experiment.
2015 outcomes were ALREADY OPENED during PR171, therefore this is a
response-exposed *post hoc cross-year ecological context analysis*, NOT a
prospective prediction or independent confirmation of Hovel et al. 2021.

Source geography is screened first; same region code alone is not enough.
The 2014 A/B subsite nearer to the 2015 experimental site is selected
WITHOUT inspecting any 2014/2015 biological response. Korea KOA/KOB remain
excluded because the original source code mapping was not one-to-one.
"""
from __future__ import annotations
import argparse,importlib.util,json,math,random,statistics
from collections import defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
SEED=202611241404
PERMS=20000
ALLOWED_PREDICTORS=("year2014_shoot_density","year2014_epiphyton")
ALLOWED_RESPONSES=("year2015_edge_minus_interior_risk","year2015_eighty_minus_ambient_risk")
MIN_COMPLETE_SITES=10

def load_script(name,path):
    sp=importlib.util.spec_from_file_location(name,BASE/"analysis"/path)
    mod=importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod

GEO=load_script("zen2_geo_gate","130_zen2_2014_2015_geographic_link_gate.py")
OLD=load_script("zen2_2014_state","128_zen2_2014_50meadow_state_consumer.py")
NEW=load_script("zen2_2015_risk","127_zen2_2015_site_predation_factorial.py")

def rank(x):
    vals=sorted(range(len(x)),key=lambda i:x[i])
    out=[None]*len(x);i=0
    while i<len(vals):
        j=i+1
        while j<len(vals) and x[vals[i]]==x[vals[j]]:j+=1
        rr=(i+1+j)/2.0
        for k in vals[i:j]:out[k]=rr
        i=j
    return out

def corr(x,y):
    if len(x)!=len(y) or len(x)<5:return None
    if not all(math.isfinite(z) for z in list(x)+list(y)):
        raise ValueError("Nonfinite data")
    ma=statistics.mean(x);mb=statistics.mean(y)
    ax=sum((v-ma)**2 for v in x);by=sum((v-mb)**2 for v in y)
    if ax<=0 or by<=0:return None
    return sum((a-ma)*(b-mb) for a,b in zip(x,y))/math.sqrt(ax*by)

def spearman(x,y):
    return corr(rank(x),rank(y))

def source_matched_records(raw14,raw15):
    link=GEO.audit(GEO.get_rows(raw14,"2014"),
                   GEO.get_rows(raw15,"2015"),threshold=25.0)
    gate={x["source_2015_site"]:x for x in link["candidates"] if x["eligible_as_prior_site_context"]}
    if len(gate)!=14 or len(set(gate))!=14:
        raise ValueError("Source-only original 14 eligible code+geography matches changed")
    old=OLD.parse(raw14)
    site2014={r["subsite_id"]:r for r in old}
    original2015=NEW.parse_rows(raw15)
    first2015=NEW.analyze(original2015)
    summary2015={z["site"]:z for z in first2015["source_cell_coverage"]}
    by2015=defaultdict(list)
    for item in original2015:by2015[item["site"]].append(item)
    matched=[]
    for site in sorted(gate):
        info=gate[site]
        former=site2014.get(info["closest_subsite_id"])
        if former is None:raise ValueError("Source-only nearest 2014 subsite not found")
        if former["region_code"]!=info["source_2014_region_code"]:
            raise ValueError("Nearest-site region code drift")
        newer=by2015[site]
        ambient={}
        for location in NEW.LOCATIONS:
            cell=[x for x in newer if x["location"]==location and x["treatment"]=="Amb"]
            if len(cell)<5:raise ValueError("Not enough original ambient trials")
            ambient[location]=cell
        baseline_shoots=statistics.mean([
            statistics.mean(x["density_initial"] for x in ambient[location])
            for location in NEW.LOCATIONS
        ])
        epa=[
            statistics.mean([x["epibiont"] for x in ambient[location]
                             if x["epibiont"] is not None])
            for location in NEW.LOCATIONS
            if sum(x["epibiont"] is not None for x in ambient[location])>=5
        ]
        baseline_epi=statistics.mean(epa) if len(epa)==2 else None
        outcome=summary2015[site]["contrasts"]
        matched.append({
            "site_code":site,
            "nearest_2014_source_subsite":former["subsite_id"],
            "nearest_distance_km":info["closest_distance_km"],
            "year2014_shoot_density":former["shoots"],
            "year2014_epiphyton":former["epiphyton"],
            "year2014_above_biomass":former["above"],
            "year2014_below_biomass":former["below"],
            "year2015_ambient_shoot_density":baseline_shoots,
            "year2015_ambient_epibiont":baseline_epi,
            "year2015_edge_minus_interior_risk":outcome["edge_minus_interior_risk"],
            "year2015_eighty_minus_ambient_risk":outcome["eighty_minus_ambient_risk"],
            "year2015_original_site_overall_predation":summary2015[site]["site_recorded_predation_fraction"],
            "year2015_prey_taxa":summary2015[site]["taxa"],
        })
    return link,matched

def permutation_screen(records,perms=PERMS,seed=SEED):
    # Fix complete-case membership by PAST survey predictors only, never by
    # next-year risk. The old epibiont field has one source NA in 50 subsites.
    valid=[
      r for r in records
      if all(r.get(p) is not None for p in ALLOWED_PREDICTORS)
      and all(r.get(o) is not None for o in ALLOWED_RESPONSES)
    ]
    if len(valid)<MIN_COMPLETE_SITES:raise ValueError("Insufficient temporal site context")
    names=[(p,o) for p in ALLOWED_PREDICTORS for o in ALLOWED_RESPONSES]
    x={p:[math.log1p(r[p]) for r in valid] for p in ALLOWED_PREDICTORS}
    if any(v<0 for r in valid for p in ALLOWED_PREDICTORS for v in [r[p]]):
        raise ValueError("Negative habitat baseline predictor")
    y={o:[r[o] for r in valid] for o in ALLOWED_RESPONSES}
    rx={p:rank(vals) for p,vals in x.items()}
    ry={o:rank(vals) for o,vals in y.items()}
    observed={(p,o):corr(rx[p],ry[o]) for p,o in names}
    if any(v is None for v in observed.values()):
        raise ValueError("Zero-variance spatial predictor or outcome")
    count={k:0 for k in names}
    family={k:0 for k in names}
    rng=random.Random(seed)
    n=len(valid)
    for _ in range(perms):
        indices=list(range(n));rng.shuffle(indices)
        test={(p,o):abs(corr(rx[p],[ry[o][i] for i in indices])) for p,o in names}
        maxT=max(test.values())
        for k in names:
            threshold=abs(observed[k])
            count[k]+=test[k]>=threshold
            family[k]+=maxT>=threshold
    stats=[]
    for p,o in names:
        k=(p,o)
        all_loo=[]
        for i,r in enumerate(valid):
            xx=[v for j,v in enumerate(x[p]) if j!=i]
            yy=[v for j,v in enumerate(y[o]) if j!=i]
            all_loo.append({"omitted_site":r["site_code"],
                            "spearman_r":spearman(xx,yy)})
        stats.append({
            "prior_predictor":p,"later_risk_outcome":o,
            "n_site_code_geography_matched_complete":n,
            "spearman_r":observed[k],
            "site_label_two_sided_posthoc_permutation_p":(count[k]+1)/(perms+1),
            "four_comparison_maxT_FWER_permutation_p":(family[k]+1)/(perms+1),
            "leave_one_site_out_spearman_min":min(x["spearman_r"] for x in all_loo),
            "leave_one_site_out_spearman_max":max(x["spearman_r"] for x in all_loo),
            "sign_interpretation":"Exploratory temporal across-site association only, not a causal or prospectively frozen prediction"
        })
    return {
        "complete_case_sites":[r["site_code"] for r in valid],
        "n_complete_case_sites":n,
        "permutation_draws":perms,
        "permutation_seed":seed,
        "maxT_scope":"four posthoc 2014 vegetation predictors x 2015 observed risk effects",
        "associations":stats
    }

def stability(records,perms=PERMS,seed=SEED+5):
    src=[r for r in records if r["year2014_shoot_density"] is not None and r["year2015_ambient_shoot_density"] is not None]
    if len(src)<MIN_COMPLETE_SITES:raise ValueError("Not enough matched shoot density sites")
    x=[math.log1p(r["year2014_shoot_density"]) for r in src]
    y=[math.log1p(r["year2015_ambient_shoot_density"]) for r in src]
    obs=spearman(x,y)
    if obs is None:raise ValueError("Zero variance earlier or later density")
    rng=random.Random(seed);exceed=0
    for _ in range(perms):
        copy=y.copy();rng.shuffle(copy)
        exceed+=abs(spearman(x,copy))>=abs(obs)
    oneout=[spearman(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(src))]
    return {
        "source_2014_nearest_subsite_shoot_density_vs_2015_ambient_shoot_density":{
            "n_geographically_nearby_sites":len(src),
            "spearman_r":obs,
            "within_source_year_independent_site_label_permutation_p":(exceed+1)/(perms+1),
            "leave_one_site_out_spearman_min":min(oneout),
            "leave_one_site_out_spearman_max":max(oneout),
            "unit":"source shoots per m2 in both years, different local transects and years",
        }
    }

def execute(raw14,raw15):
    link,sites=source_matched_records(raw14,raw15)
    if len(sites)!=14:raise ValueError("14-site eligibility gate changed")
    screen=permutation_screen(sites)
    return {
      "schema":"tampa.zen2_nearest_subsite_2014_prior_state_2015_interaction_exploratory_v1",
      "evidence_class":"posthoc_external_crossyear_geographic_context_not_longitudinal_fixed_plots",
      "source_shas":{k:v[1] for k,v in GEO.SOURCES.items()},
      "geographic_gate_rule":"Same 2014 region code and <=25km nearest of 2014 A/B subsite to 2015 site; KOA/KOB explicitly excluded; 5km strict sensitivity predeclared before viewing crossyear result",
      "candidate_sites":sites,
      "n_match":len(sites),
      "distance_summary":{
         "min_nearest_km":min(x["nearest_distance_km"] for x in sites),
         "max_nearest_km":max(x["nearest_distance_km"] for x in sites),
         "median_nearest_km":statistics.median(x["nearest_distance_km"] for x in sites)
      },
      "temporal_structural_stability":stability(sites),
      "site_equal_prior_predictor_later_risk_screen":screen,
      "strict_five_km_sensitivity":{
          "included_site_codes":[s["site_code"] for s in sites if s["nearest_distance_km"]<=5],
          "structural_stability":stability(
              [s for s in sites if s["nearest_distance_km"]<=5],perms=perms5()
          )
      },
      "hard_limits":[
        "2014 and 2015 source sites are geographically nearby, NOT identical permanent sampling points.",
        "Nearest subsite selected exclusively by source coordinates; averaging far-away A/B subsites would be invalid.",
        "2015 risk outcomes and 2014 site survey outcomes were already opened before this cross-year test: no untouched holdout.",
        "Original Hovel et al. 2021 already linked same-year structural features to predation edge effects.",
        "Only 14 sites eligible by exact code and <=25km; KOA/KOB excluded despite likely geographic match, GA has no 2014 source code.",
        "Cross-year association may reflect shared environment and researcher/site identity; not experimental temporal causality.",
        "2014 epiphyton and 2015 epibiont can use different sampling and normalization and should not be compared as absolute rates.",
        "No TNC, actual host survival, fish predator identification or validated conservation decision threshold.",
        "Four comparisons are jointly corrected only within this selected posthoc family, not all analyses in the research program.",
      ]
    }

def perms5():
    # Limit secondary site-distance check to a fixed 5000 randomizations.
    return 5000

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,default=None);args=ap.parse_args()
    j=execute(GEO.download("2014"),GEO.download("2015"))
    txt=json.dumps(j,sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(txt,encoding="utf8")
    else:print(txt,end="")

if __name__=="__main__":
    main()
