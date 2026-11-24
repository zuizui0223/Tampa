#!/usr/bin/env python3
"""Original 2014 ZEN2 50-subsite (25 region-code) observed state analysis.

Original BCO-DMO source DOI 10.26008/1912/bco-dmo.712069.1.
These are summary means for separate subsite A/B within 25 site codes.
A/B contrasts are observational **within-region differences**, not treatments
or longitudinal before-after ecological changes. Outcome is original 2014,
not the 2015 17-site experimental endpoint.

Inspect how independently measured seagrass biomass/shoot density and
mesograzer/epiphyton summary respond within pairs after reducing site-wide
context with paired contrasts. Correlations are descriptive, no causal effect.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

SRC_URL="https://datadocs.bco-dmo.org/dataset/712069/file/1VVMOrXtMO4KM1/ZEN2_survey_sorted.csv"
SRC_SHA256="c2af785e48aa76f88834e6c96ab69f49f85feb0918a89f9ec0585680cb170034"
VARS={
  "above":"Above_Zmarina_g",
  "below":"Below_Zmarina_g",
  "shoots":"Mean_Shoots_Zmarina_per_m2",
  "mesograzer_abundance":"Mean_Std_Total_Abund_Mesograzers",
  "mesograzer_count_unstandardized":"Mean_Total_Abund_Mesograzers",
  "mesograzer_richness":"Mean_Mesograzer_Richness",
  "epiphyton":"Mean_Site_Std_Periphyton",
  "temperature":"Temperature_C",
  "salinity":"Salinity_ppt",
}
KEYS=("Site_Code","Site","Subsite","Date_Collected")
YEAR=2014
BOOT=5000
SEED=2026112417

def source_bytes():
    req=Request(SRC_URL,headers={"User-Agent":"Tampa-zen2-50meadow-1.0",
                                 "Accept-Encoding":"identity"})
    with urlopen(req,timeout=90) as x:b=x.read(150000)
    if hashlib.sha256(b).hexdigest()!=SRC_SHA256:raise ValueError("2014 original source checksum changed")
    return b

def parse(raw,verify_digest=True):
    if verify_digest and hashlib.sha256(raw).hexdigest()!=SRC_SHA256:
        raise ValueError("Original source SHA mismatch")
    r=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if r.fieldnames is None or not set(KEYS).issubset(r.fieldnames) or not set(VARS.values()).issubset(r.fieldnames):
        raise ValueError("Unexpected original 2014 sample header")
    data=[]
    for i,x in enumerate(r):
        if not x["Site_Code"] or not x["Site"] or not x["Subsite"]:
            raise ValueError("Missing original site identity")
        if not x["Date_Collected"].startswith(str(YEAR)):
            raise ValueError("Unexpected sampling period")
        row={"region_code":x["Site_Code"].strip(),
             "subsite_id":x["Site"].strip(),"subsite":x["Subsite"].strip()}
        for k,col in VARS.items():
            s=str(x[col] or "").strip()
            if s.lower() in ("","na","n/a","null"):
                row[k]=None
                continue
            try:v=float(s)
            except ValueError as e:raise ValueError(f"Unrecognized numeric {col} in row {i}") from e
            if not math.isfinite(v) or (v<0 and k not in ("temperature",)):
                raise ValueError("Original negative/nonfinite site summary value")
            row[k]=v
        data.append(row)
    ids=[r["subsite_id"] for r in data]
    if len(ids)!=len(set(ids)):raise ValueError("Duplicate 2014 subsite")
    return data

def corr(x,y):
    if len(x)!=len(y) or len(x)<6:return None
    mx=statistics.mean(x);my=statistics.mean(y)
    xy=sum((a-mx)*(b-my) for a,b in zip(x,y))
    xx=sum((a-mx)**2 for a in x);yy=sum((b-my)**2 for b in y)
    return xy/math.sqrt(xx*yy) if xx>0 and yy>0 else None

def pair_differences(rows):
    groups=defaultdict(list)
    for r in rows:groups[r["region_code"]].append(r)
    if len(groups)!=25:
        raise ValueError("Expected 25 site codes from 50 subsite rows")
    pairs=[]
    for code,rs in sorted(groups.items()):
        if len(rs)!=2:
            raise ValueError("Each region code must have exactly two original independent subsite summaries")
        a,b=sorted(rs,key=lambda x:x["subsite_id"])
        item={"region_code":code,"subsite_A":a["subsite_id"],"subsite_B":b["subsite_id"]}
        for k in VARS:
            xa,xb=a[k],b[k]
            if xa is None or xb is None:
                item[k+"_dlog1p"]=None
            elif k in ("temperature",):
                item[k+"_dlog1p"]=xa-xb
            else:
                item[k+"_dlog1p"]=math.log1p(xa)-math.log1p(xb)
        pairs.append(item)
    return pairs

def summarize(rows):
    pair=pair_differences(rows)
    edges=[
        ("above","mesograzer_abundance"),
        ("below","mesograzer_abundance"),
        ("shoots","mesograzer_abundance"),
        ("above","mesograzer_count_unstandardized"),
        ("below","mesograzer_count_unstandardized"),
        ("shoots","mesograzer_count_unstandardized"),
        ("above","mesograzer_richness"),
        ("below","mesograzer_richness"),
        ("shoots","mesograzer_richness"),
        ("above","epiphyton"),
        ("below","epiphyton"),
        ("shoots","epiphyton"),
    ]
    res={}
    for k,y in edges:
        filtered=[
            (r[k+"_dlog1p"],r[y+"_dlog1p"])
            for r in pair if r[k+"_dlog1p"] is not None and r[y+"_dlog1p"] is not None
        ]
        x=[a for a,b in filtered];z=[b for a,b in filtered]
        n=len(x)
        observed=corr(x,z)
        bootvals=[]
        if observed is not None:
            rng=random.Random(SEED+len(k)*7+len(y)*13)
            for i in range(BOOT):
                ix=[rng.randrange(n) for j in range(n)]
                q=corr([x[j] for j in ix],[z[j] for j in ix])
                if q is not None:bootvals.append(q)
            bootvals.sort()
        res[k+"__"+y]={
            "pairs":n,"pearson_r_of_within_region_log1p_contrasts":observed,
            "site_code_pair_bootstrap_percentile_interval":[
                 bootvals[math.floor((len(bootvals)-1)*.025)],
                 bootvals[math.ceil((len(bootvals)-1)*.975)]
             ] if len(bootvals)>=100 else None,
        }
    missing={v:sum(x[v] is None for x in rows) for v in VARS}
    return {
       "schema":"tampa.zen2_2014_25paired_region_structure_consumer_v1",
       "evidence_class":"original_source_observational_cross_sectional_not_experiment",
       "source_doi":"10.26008/1912/bco-dmo.712069.1",
       "source_sha256":SRC_SHA256,
       "sample_subsites":len(rows),"paired_region_codes":len(pair),
       "measured_missing_subsite_counts":missing,
       "within_region_association_tests_descriptive":res,
       "individual_region_pair_log_contrasts":pair,
       "hard_limits":[
          "Two observational subsites share a region code, not randomized intervention assignment.",
          "2014 subsite data do not match 2015 factorial tether plots or 2011 grazer-deterrent plots.",
          "All models are post-hoc descriptive across at most 25 region-code pairs.",
          "Pairwise log1p difference is stable to the site-scale offset but does not block unmeasured within-code habitat confounding.",
          "The above/below biomass data were already part of published ZEN2 survey summaries.",
          "Mean_Std_Total_Abund_Mesograzers likely uses host-standardization. A correlation against host biomass may be mechanically induced by its denominator. The source also provides Mean_Total_Abund_Mesograzers without Std; compare both, and do not interpret the difference as causality.",
          "The unstandardized consumer outcome was added after seeing an unexpected negative association using the standardized consumer metric: post-hoc denominator diagnostic only.",
          "Within-region covariance is neither organism-specific interaction nor causally mediated change.",
          "This source cannot estimate future seagrass retention, TNC or biodiversity effects of consumer removal.",
       ]
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None);a=p.parse_args()
    rows=parse(source_bytes())
    if len(rows)!=50:raise ValueError("Original ZEN2 2014 source row count drift")
    j=summarize(rows)
    s=json.dumps(j,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
