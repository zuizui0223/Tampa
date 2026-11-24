#!/usr/bin/env python3
"""Screen deposited diel-pollination extraction table for candidate paired stages.
Not the published meta-analysis dataset after modeling filters. Not individual matching.
"""
import argparse,base64,csv,hashlib,io,json,math,re,statistics as st,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
BLOB="39a82d966afcdde670603add1c881ace8791ffe9"
URL=f"https://api.github.com/repos/liamkendall/bumble-bat/git/blobs/{BLOB}"
KEY=["study_ID","plant_species","plant_cultivar","country","locality","Site_period","coordinates_lat","coordinates_lon","year_start","year_end","month_start","month_end","additional_treatment"]
DAY,NIGHT="day pollination","night pollination"
def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"Tampa-paired-pollination-audit/1.0","Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=45) as r:b=r.read(4_000_001)
    assert len(b)<=4_000_000
    a=json.loads(b);assert a["sha"]==BLOB and a["encoding"]=="base64"
    return base64.b64decode(a["content"])
def numeric(s):
    try:v=float(s)
    except (ValueError,TypeError):return None
    return v if math.isfinite(v) else None
def outcome(a,b):
    x,y=a["d"]-a["n"],b["d"]-b["n"]
    return "opposite" if x*y<0 else "tie" if x==0 or y==0 else "same"
def summarize(v):
    groups=defaultdict(list)
    for x in v:groups[x["context"]["study_ID"]].append(outcome(x["fruit"],x["seed"]))
    c=Counter(t for a in groups.values() for t in a)
    w=[a.count("opposite")/len(a) for a in groups.values()]
    return {"contexts":len(v),"study_ids":len(groups),"direction_counts":dict(c),
            "studies_with_any_opposite":sum("opposite" in a for a in groups.values()),
            "study_equal_mean_opposite_fraction":st.mean(w) if w else None,
            "study_equal_leave_one_out_range":[min(st.mean(w[:i]+w[i+1:]) for i in range(len(w))),max(st.mean(w[:i]+w[i+1:]) for i in range(len(w)))] if len(w)>1 else None}
def analyze(raw):
    assert hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==BLOB
    a=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    assert len(a)==1652 and len({r["study_ID"] for r in a})==140 and all(r["exclude"]=="n" for r in a)
    g=defaultdict(list)
    for r in a:
        if r["treatment_condition"] in (DAY,NIGHT):g[tuple(r[k] for k in KEY)].append(r)
    multi=[];ambiguous=0
    for k,rs in g.items():
        p={}
        for metric in sorted({r["treatment_effectiveness_metric"] for r in rs}):
            d,n=([r for r in rs if r["treatment_effectiveness_metric"]==metric and r["treatment_condition"]==t] for t in (DAY,NIGHT))
            if len(d)==len(n)==1 and d[0]["effectiveness_units"]==n[0]["effectiveness_units"]:
                x,y=d[0],n[0]
                p[metric]={"d":numeric(x["effectiveness_value"]),"n":numeric(y["effectiveness_value"]),"unit":x["effectiveness_units"],"source_rows":[x[""],y[""]],"sample_sizes":[x["sample_size"],y["sample_size"]]}
            elif d and n:ambiguous+=1
        if len(p)>1:multi.append({"context":dict(zip(KEY,k)),"metrics":p})
    both=[{"context":r["context"],"fruit":r["metrics"]["fruit set"],"seed":r["metrics"]["seed set"]} for r in multi if {"fruit set","seed set"}<=r["metrics"].keys()]
    complete=[x for x in both if all(v is not None and v>=0 for m in ("fruit","seed") for v in (x[m]["d"],x[m]["n"]))]
    strict=[x for x in complete if re.search(r"^proportion|^fruits?/flowers?$",x["fruit"]["unit"].lower()) and re.fullmatch(r"(?:mean )?(?:viable )?seeds?(?:/| per )(?:fruit|pod)",x["seed"]["unit"].lower()) and max(x["fruit"]["d"],x["fruit"]["n"])<=1 and min(x[m][t] for m in ("fruit","seed") for t in ("d","n"))>0]
    strict_2=[x for x in strict if "#" not in x["fruit"]["unit"] and min(x["seed"]["d"],x["seed"]["n"])>=1]
    for x in complete:
        x["direction"]=outcome(x["fruit"],x["seed"])
    for x in strict:
        x["day_over_night_ratios"]=[x[m]["d"]/x[m]["n"] for m in ("fruit","seed")]
        x["opposite_both_ratios_differ_by_factor_1p1"]=x["direction"]=="opposite" and all(abs(math.log(v))>=math.log(1.1) for v in x["day_over_night_ratios"])
    pollen={r["study_ID"] for r in a if r["treatment_effectiveness_metric"]=="pollen deposition"}
    pollen_and_seed=pollen & {r["study_ID"] for r in a if r["treatment_effectiveness_metric"]=="seed set"}
    return {"status":"screen_of_deposited_extraction_table_not_validated_meta_effect","source_doi":"10.1111/ele.70036","data_doi":"10.6084/m9.figshare.26004538.v1","source_blob":BLOB,"source_rows":len(a),"study_ids":140,"metric_counts":dict(Counter(r["treatment_effectiveness_metric"] for r in a)),"candidate_contexts":len(g),"ambiguous_metric_groups":ambiguous,"multi_endpoint_contexts":len(multi),"multi_endpoint_study_ids":len({x["context"]["study_ID"] for x in multi}),"pollen_studies":sorted(pollen),"pollen_and_seed_study_ids":sorted(pollen_and_seed),"pollen_and_seed_candidates":[x for x in multi if {"pollen deposition","seed set"}<=x["metrics"].keys()],"fruit_seed_candidates":len(both),"complete_summary":summarize(complete),"explicit_unit_positive_summary":summarize(strict),"sensitivity_excluding_converted_counts_and_seed_means_below_one":summarize(strict_2),"explicit_unit_strong_opposite":sum(x["opposite_both_ratios_differ_by_factor_1p1"] for x in strict),"candidate_records":complete,"strict_source_row_sets":[[x[m]["source_rows"] for m in ("fruit","seed")] for x in strict],"limitations":["Metadata keys are candidate context alignment only; missing or ambiguous metadata can hide different experiments or subgroups. No actual flower-level pairing or effect covariance; verify each original study before inclusion.","All deposited rows have exclude=n; 140 study IDs differ from 135 studies in published final model. No attempt to reproduce original paper filters.","Fruit and seed metrics have heterogeneous denominators; broad screening compares directions only. Explicit-unit positive subset is a posthoc sensitivity, not adjudicated eligible set. Some seed-per-fruit labels may be incorrect or normalized; sensitivity excludes seed means below one and converted counts but does not prove comparability.","Sign of a mean difference is not statistical significance or an established mechanism. No pooled prevalence estimate or independent treatment comparisons.","Martinell_2010 source text reports night seeds/fruit 43.7 vs deposited 47.3, flagged not corrected here. Elam_1988 subgroups need original-paper verification; no direct paired causal estimate."]}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path);a=p.parse_args()
    print(json.dumps(analyze(a.input.read_bytes() if a.input else fetch()),indent=2,sort_keys=True,allow_nan=False))
