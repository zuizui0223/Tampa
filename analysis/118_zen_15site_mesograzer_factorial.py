#!/usr/bin/env python3
"""Exploratory site-level reaggregation of ZEN's original 600-plot experiment.

DOI 10.1111/ele.12448; 2016 BCO-DMO dataset 659737, official CC BY 4.0 CSV.
The 15 sites and 4 randomized combinations are original published experiment,
not 600 independent estuaries or a new globally general causal discovery.

D+ = grazer deterrent (reduced grazers), N+ = nutrient addition.
The CSV directly measures epiphyte chlorophyll per Zostera and grazer biomass,
NOT Zostera shoot density, cover, production or rhizome TNC.

Source checksum was verified in the preceding independent source gate.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import random
import statistics
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

URL="https://datadocs.bco-dmo.org/dataset/659737/file/2GGXP4qs6jo9x0/ZEN.csv"
SOURCE_SHA256="5a97763735a22076eac25a86736c50cb12611a529c5e233941fbc3a73ad4c6ae"
TREATMENTS=("D+N+","D+N-","D-N+","D-N-")
OUTCOMES=("chla_per_Zostera","grazer_bmass_per_g")
MIN_VALID_PER_SITE_CELL=5
BOOT=5000
SEED=2026112401

def raw_file()->bytes:
    req=Request(URL,headers={"User-Agent":"Tampa-interaction-zen-reaggregation/1.0",
                             "Accept-Encoding":"identity"})
    with urlopen(req,timeout=90) as r:
        raw=r.read(1000001)
    if len(raw)>1000000 or hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise RuntimeError("ZEN original-source checksum mismatch or over-size")
    return raw

def numeric(value,allow_negative=False):
    t=str(value or "").strip()
    if t.lower() in ("","na","n/a","nan","null","."):
        return None
    try:x=float(t)
    except ValueError:raise ValueError(f"Unexpected nonnumeric value {t[:50]}")
    if not math.isfinite(x) or (x<0 and not allow_negative):
        raise ValueError("Invalid negative/non-finite measured biomass or Chla")
    return x

def parse(raw):
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        # For non-network synthetic unit tests use parse_core directly.
        raise ValueError("Original ZEN source sha256 mismatch")
    return parse_core(raw)

def parse_core(raw):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")),delimiter=",")
    fields=reader.fieldnames
    required={"site_code","plot","unique_plot_id","treatment",*OUTCOMES,
              "grazer_richness_site","temp_avg","sal"}
    if fields is None or not required.issubset(fields):
        raise ValueError(f"Original ZEN required fields missing {sorted(required-set(fields or []))}")
    rows=list(reader)
    if any(None in r for r in rows):
        raise ValueError("Malformed ZEN CSV")
    sites=defaultdict(list)
    ids=set()
    for i,r in enumerate(rows):
        t=r["treatment"].strip()
        site=r["site_code"].strip()
        uid=r["unique_plot_id"].strip()
        if t not in TREATMENTS or not site or not uid:
            raise ValueError(f"Unexpected treatment/site/plot id at row {i}")
        if uid in ids:raise ValueError("Duplicate unique_plot_id")
        ids.add(uid)
        parsed={
            "site":site,"uid":uid,"treatment":t,
            "nutrient_added":int("N+" in t),
            "deterrent_added":int("D+" in t),
        }
        for target in OUTCOMES:
            parsed[target]=numeric(r[target])
        for k in ("grazer_richness_site","temp_avg","sal"):
            parsed[k]=numeric(r[k],allow_negative=(k=="temp_avg"))
        sites[site].append(parsed)
    return sites

def contrast(cells:dict):
    m=lambda t:cells[t]
    # Equal weight to both N states (and conversely both D states).
    d=((m("D+N+")+m("D+N-"))-(m("D-N+")+m("D-N-")))/2
    n=((m("D+N+")+m("D-N+"))-(m("D+N-")+m("D-N-")))/2
    dn=m("D+N+")-m("D+N-")-m("D-N+")+m("D-N-")
    return {"grazer_deterrent_main_difference":d,
            "nutrient_addition_main_difference":n,
            "grazer_deterrent_x_nutrient_difference_in_differences":dn}

def by_site(sites:dict):
    reports=[]
    for site,rows in sorted(sites.items()):
        by_t=defaultdict(list)
        for r in rows:by_t[r["treatment"]].append(r)
        if set(by_t)!=set(TREATMENTS):
            raise ValueError(f"Missing assigned factorial treatment at site {site}")
        record={
            "site":site,"row_count":len(rows),
            "arm_allocation":{t:len(by_t[t]) for t in TREATMENTS},
            "cross_site_predictors":{
                k:statistics.median(v) if v else None
                for k in ("grazer_richness_site","temp_avg","sal")
                for v in [[x[k] for x in rows if x[k] is not None]]
            },
            "endpoints":{}
        }
        for target in OUTCOMES:
            measured={t:[x[target] for x in by_t[t] if x[target] is not None] for t in TREATMENTS}
            eligible=all(len(x)>=MIN_VALID_PER_SITE_CELL for x in measured.values())
            a={"n_valid_per_arm":{t:len(measured[t]) for t in TREATMENTS},
               "eligible_for_four_arm_contrast":eligible,
               "arm_means":{t:statistics.mean(measured[t]) if measured[t] else None for t in TREATMENTS}}
            if eligible:
                a["contrasts"]=contrast(a["arm_means"])
                # Exploratory scale-invariant check added after a very high raw
                # site contrast was observed. NOT a frozen original primary.
                if all(x>0 for x in a["arm_means"].values()):
                    logs={t:math.log(x) for t,x in a["arm_means"].items()}
                    a["posthoc_log_arm_mean_contrasts"]=contrast(logs)
                else:
                    a["posthoc_log_arm_mean_contrasts"]=None
            record["endpoints"][target]=a
        reports.append(record)
    return reports

def cluster_bootstrapped_mean(x:list[float],seed=SEED):
    if len(x)<4:return {"estimable":False}
    point=statistics.mean(x)
    rng=random.Random(seed)
    draws=[statistics.mean([x[rng.randrange(len(x))] for _ in x]) for i in range(BOOT)]
    draws.sort()
    i=math.floor((BOOT-1)*.025);j=math.ceil((BOOT-1)*.975)
    positives=sum(a>0 for a in x);negatives=sum(a<0 for a in x)
    return {"estimable":True,"sites":len(x),"mean_site_equal":point,
            "site_bootstrap_95pct_percentile_ci":[draws[i],draws[j]],
            "positive_site_contrasts":positives,"negative_site_contrasts":negatives,
            "zeros":len(x)-positives-negatives,
            "summary_only_no_new_randomization_test":True}

def pearson(xs,ys):
    if len(xs)<5:return None
    mx=statistics.mean(xs);my=statistics.mean(ys)
    a=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    b=sum((x-mx)**2 for x in xs)
    c=sum((y-my)**2 for y in ys)
    return a/math.sqrt(b*c) if b>0 and c>0 else None

def analysis(sites):
    site_data=by_site(sites)
    result={"sites_total":len(site_data),"plots_total":sum(x["row_count"] for x in site_data),
            "unique_plot_counts_by_site":{x["site"]:x["row_count"] for x in site_data},
            "endpoints":{}}
    for response in OUTCOMES:
        eligible=[x for x in site_data if x["endpoints"][response]["eligible_for_four_arm_contrast"]]
        ckeys=("grazer_deterrent_main_difference","nutrient_addition_main_difference",
               "grazer_deterrent_x_nutrient_difference_in_differences")
        contrasts={}
        for label in ckeys:
            v=[x["endpoints"][response]["contrasts"][label] for x in eligible]
            contrasts[label]=cluster_bootstrapped_mean(v,seed=SEED+len(label)+len(response))
        moderators={}
        for key in ("grazer_richness_site","temp_avg","sal"):
            v=[(x["cross_site_predictors"][key],
                x["endpoints"][response]["contrasts"]["grazer_deterrent_main_difference"])
               for x in eligible if x["cross_site_predictors"][key] is not None]
            moderators[key]={"site_count":len(v),
                             "unadjusted_pearson_of_site_deterrent_effect":(
                                pearson([a for a,b in v],[b for a,b in v]))}
        log_eligible=[
            x for x in eligible
            if x["endpoints"][response]["posthoc_log_arm_mean_contrasts"] is not None
        ]
        log_contrasts={}
        for label in ckeys:
            vals=[
                x["endpoints"][response]["posthoc_log_arm_mean_contrasts"][label]
                for x in log_eligible
            ]
            res=cluster_bootstrapped_mean(vals,seed=SEED+100+len(label)+len(response))
            if res.get("estimable"):
                res["site_equal_geometric_effect_ratio"]=math.exp(res["mean_site_equal"])
                res["geometric_ratio_ci95"]=[
                    math.exp(v) for v in res["site_bootstrap_95pct_percentile_ci"]
                ]
                res["median_site_specific_ratio"]=math.exp(statistics.median(vals))
                loo=[
                    {"omitted_site":x["site"],
                     "site_equal_geometric_effect_ratio_without_site":
                        math.exp(statistics.mean([
                            y["endpoints"][response]["posthoc_log_arm_mean_contrasts"][label]
                            for y in log_eligible if y["site"]!=x["site"]
                        ]))}
                    for x in log_eligible
                ] if len(log_eligible)>=5 else []
                if loo:
                    res["site_omission_geometric_ratio_min"]=min(
                        z["site_equal_geometric_effect_ratio_without_site"] for z in loo
                    )
                    res["site_omission_geometric_ratio_max"]=max(
                        z["site_equal_geometric_effect_ratio_without_site"] for z in loo
                    )
                    res["most_influential_site_omission_by_ratio"]={
                        "min_ratio":min(loo,key=lambda z:z["site_equal_geometric_effect_ratio_without_site"]),
                        "max_ratio":max(loo,key=lambda z:z["site_equal_geometric_effect_ratio_without_site"]),
                    }
            log_contrasts[label]=res
        raw_d=[x["endpoints"][response]["contrasts"]["grazer_deterrent_main_difference"] for x in eligible]
        raw_loo=[{"omitted_site":x["site"],
                  "mean_raw_contrast_without_site":statistics.mean([
                      y["endpoints"][response]["contrasts"]["grazer_deterrent_main_difference"]
                      for y in eligible if y["site"]!=x["site"]])}
                for x in eligible] if len(eligible)>=5 else []
        result["endpoints"][response]={
            "posthoc_scale_invariant_log_of_arm_means":log_contrasts,
            "raw_deterrent_site_omission_min_max":[
                min(z["mean_raw_contrast_without_site"] for z in raw_loo),
                max(z["mean_raw_contrast_without_site"] for z in raw_loo),
            ] if raw_loo else None,
            "raw_deterrent_effect_site_median":statistics.median(raw_d) if raw_d else None,
            "sites_eligible":len(eligible),
            "not_eligible_sites":sorted(x["site"] for x in site_data if x not in eligible),
            "contrasts":contrasts,
            "posthoc_site_level_moderator_descriptors":moderators,
            "expected_main_sign_if_effective_grazer_reduction":(
               "positive" if response=="chla_per_Zostera" else "negative")
        }
    result["per_site_exploratory_contrasts"]=site_data
    return result

def execute(raw):
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError("Original original ZEN source bytes do not match frozen digest")
    sites=parse_core(raw)
    result=analysis(sites)
    if result["sites_total"]!=15 or result["plots_total"]!=600:
        raise ValueError("Published 15-site/600-plot factorial frame drift")
    if any(count!=40 for count in result["unique_plot_counts_by_site"].values()):
        raise ValueError("Expected exactly 40 original plot rows per site")
    return {
        "schema":"tampa.zen_global_mesograzer_15site_exploratory_v1",
        "status":"response_open_exploratory_comparative_experiment",
        "source":{"dataset_url":URL,"data_doi":None,"paper_doi":"10.1111/ele.12448",
                  "sha256":hashlib.sha256(raw).hexdigest(),"original_dataset_sites":15},
        "analysis":result,
        "strict_boundaries":[
            "Only 15 field sites provide geographic replication; 600 plots are not independent ecosystems.",
            "D+ = deterrent treatment and N+ = fertilization from published ZEN design.",
            "Only original measured chlorophyll-a per Zostera and grazer biomass endpoints are analyzed; no plant shoot, cover, TNC, or true persistence response is in source.",
            "Missing NA measurements are never coded zero. At least five numerical observations per site per arm are required, predeclared before source outcomes.",
            "Site-equal bootstrap intervals are exploratory; published 2015 work already modeled these effects.",
            "Scale-invariant log-of-arm-means contrasts and leave-one-site-out diagnostics were added after observing a large Virginia raw-scale site effect; they are expressly post-hoc robustness checks.",
            "Posthoc moderator correlations are observational across 15 sites and not externally predictive or mechanistically isolated.",
            "The BCO-DMO dataset landing page mentions 16 sites but the actual CSV has 15 site codes and 600 original factorial plots.",
        ]
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    r=execute(raw_file())
    s=json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
