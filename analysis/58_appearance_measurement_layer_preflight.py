#!/usr/bin/env python3
"""Response-blind inventory of the unused Tampa seagrass Appearance field.

Reads only source metadata, species identity and Appearance. It does not read
SpeciesAbundance, blade length, shoot density, future retention/loss or any
derived Tampa response.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/data/trnsct.csv"
SIZE=17186023
BLOB="2a9ac04c300d4e209b1359656de6b581ad7ae138"
FOCAL={"Thalassia","Thalassia testudinum"}
VALID={"Poor":0,"Fair":1,"Good":2,"Very Good":3,"Excellent":3}

def sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch():
    req=Request(URL,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-appearance-preflight/1.0"})
    with urlopen(req,timeout=180) as r:
        data=r.read(SIZE+1)
    if len(data)!=SIZE or sha(data)!=BLOB:
        raise RuntimeError("pinned raw source identity drift")
    return data

def main(out:Path):
    out.mkdir(parents=True,exist_ok=True)
    rd=csv.DictReader(io.StringIO(fetch().decode("utf-8"),newline=""))
    req={"IDall","AssessmentYear","MonitoringAgency","Transect","BaySegment","Site","Species","Appearance"}
    if not req.issubset(set(rd.fieldnames or [])):
        raise RuntimeError("appearance source columns missing")
    counts=Counter(); by_bay=Counter(); by_agency=Counter(); by_year=Counter()
    points=set(); visits=set(); node_categories=defaultdict(set)
    unexpected=Counter()
    for row in rd:
        if (row["Species"] or "").strip() not in FOCAL:
            continue
        a=(row["Appearance"] or "").strip()
        if not a or a=="NA":
            continue
        if a=="BAD DATA":
            continue
        if a not in VALID:
            unexpected[a]+=1
            continue
        node=(row["Transect"] or "").strip()
        site=(row["Site"] or "").strip()
        year=(row["AssessmentYear"] or "").strip()
        visit=(row["IDall"] or "").strip()
        counts[a]+=1
        by_bay[(row["BaySegment"] or "").strip()]+=1
        by_agency[(row["MonitoringAgency"] or "UNKNOWN").strip() or "UNKNOWN"]+=1
        by_year[year]+=1
        points.add((node,site,year)); visits.add(visit); node_categories[node].add(a)
    result={
      "schema":"tampa.appearance_measurement_layer_preflight_v1",
      "status":"unused_general_condition_layer_has_substantial_focal_coverage",
      "response_blind":True,
      "source":{"commit":COMMIT,"size":SIZE,"blob":BLOB},
      "measurement":{
        "field":"Appearance",
        "protocol_meaning":"general rating of seagrass appearance / condition",
        "ordinal_mapping":VALID,
        "excluded_label":"BAD DATA"
      },
      "thalassia":{
        "valid_rows":sum(counts.values()),
        "unique_point_years":len(points),
        "unique_visits":len(visits),
        "unique_transects":len(node_categories),
        "transects_with_ge2_categories":sum(len(x)>=2 for x in node_categories.values()),
        "category_counts":dict(counts),
        "by_bay":dict(by_bay),
        "by_agency":dict(by_agency),
        "years":sorted(int(y) for y in by_year if y)
      },
      "unexpected_labels":dict(unexpected),
      "claim_boundary":[
        "Appearance is a trained but subjective field rating, not a physiological assay.",
        "Coverage was audited without reading abundance, blade length, shoot density or future state.",
        "Excellent and Very Good share the top ordinal score only because the field manual uses excellent while the raw database primarily uses Very Good; the raw labels remain reported.",
        "Coverage alone does not establish predictive or mechanistic value."
      ]
    }
    (out/"appearance_measurement_layer_preflight_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--out",type=Path,default=Path("results/generated_appearance_preflight"))
    a=p.parse_args(); main(a.out)
