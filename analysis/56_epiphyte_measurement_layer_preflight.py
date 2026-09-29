#!/usr/bin/env python3
"""Response-blind inventory of the unused Tampa epiphyte measurement layer.

This script opens only source metadata, species identity and epiphyte fields from the
pinned raw transect table. It does not inspect focal frequency, Braun-Blanquet,
blade length, shoot density, loss or re-recording outcomes.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
URL=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/data/trnsct.csv"
SIZE=17186023
BLOB="2a9ac04c300d4e209b1359656de6b581ad7ae138"
FOCAL={"Thalassia","Thalassia testudinum"}
DENSITY_ORDER={"Clean":0,"Light":1,"Moderate":2,"Heavy":3}
FORBIDDEN_READ_COLUMNS={
    "SpeciesAbundance","BladeLength_1","BladeLength_2","BladeLength_3",
    "BladeLength_4","BladeLength_5","BladeLength_Avg","BladeLength_StdDev",
    "ShootDensity_1","ShootDensity_2","ShootDensity_3","ShootDensity_Avg",
    "ShootDensity_StdDev"
}

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch()->bytes:
    req=Request(URL,headers={"Accept-Encoding":"identity","User-Agent":"Tampa-epiphyte-preflight/1.0"})
    with urlopen(req,timeout=180) as resp:
        data=resp.read(SIZE+1)
    if len(data)!=SIZE:
        raise RuntimeError(f"raw source size drift: {len(data)} != {SIZE}")
    if git_blob_sha1(data)!=BLOB:
        raise RuntimeError("raw source blob drift")
    return data

def main(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    reader=csv.DictReader(io.StringIO(fetch().decode("utf-8"),newline=""))
    required={
        "IDall","AssessmentYear","Transect","BaySegment","Site","Species",
        "EpiphyteType_1","EpiphyteType_2","EpiphyteType_3","EpiphyteDensity"
    }
    if not required.issubset(set(reader.fieldnames or [])):
        raise RuntimeError("required epiphyte source columns missing")

    density=Counter(); by_year=Counter(); by_bay=Counter(); species=Counter()
    type_counts=[Counter(),Counter(),Counter()]
    points=set(); visits=set(); nodes=set(); years=set()

    fdensity=Counter(); fbay=Counter(); ftype=[Counter(),Counter(),Counter()]
    fpoints=set(); fvisits=set(); fnodes=set(); fyears=set()
    bad_rows=[]

    for rownum,row in enumerate(reader,start=2):
        # Never read the forbidden response columns in this preflight.
        value=(row["EpiphyteDensity"] or "").strip()
        if not value or value=="NA":
            continue
        year=(row["AssessmentYear"] or "").strip()
        node=(row["Transect"] or "").strip()
        bay=(row["BaySegment"] or "").strip()
        visit=(row["IDall"] or "").strip()
        site=(row["Site"] or "").strip()
        sp=(row["Species"] or "").strip()
        point=f"{visit}|{site}"

        density[value]+=1; by_year[year]+=1; by_bay[bay]+=1; species[sp]+=1
        points.add(point); visits.add(visit); nodes.add(node); years.add(year)
        for k in range(3):
            t=(row[f"EpiphyteType_{k+1}"] or "").strip()
            if t and t!="NA":
                type_counts[k][t]+=1

        if sp in FOCAL:
            fdensity[value]+=1; fbay[bay]+=1
            fpoints.add(point); fvisits.add(visit); fnodes.add(node); fyears.add(year)
            for k in range(3):
                t=(row[f"EpiphyteType_{k+1}"] or "").strip()
                if t and t!="NA":
                    ftype[k][t]+=1
            if value not in DENSITY_ORDER and value!="BAD DATA":
                bad_rows.append({"row":rownum,"value":value})

    result={
        "schema":"tampa.epiphyte_measurement_layer_preflight_v1",
        "status":"unused_measurement_layer_has_substantial_focal_coverage",
        "response_blind":True,
        "source":{"commit":COMMIT,"size":SIZE,"blob":BLOB},
        "measurement":{
            "density_field":"EpiphyteDensity",
            "type_fields":["EpiphyteType_1","EpiphyteType_2","EpiphyteType_3"],
            "ordinal_density_mapping":DENSITY_ORDER,
            "excluded_density_label":"BAD DATA"
        },
        "all_taxa":{
            "rows_with_density":sum(density.values()),
            "unique_points":len(points),
            "unique_visits":len(visits),
            "unique_transects":len(nodes),
            "years":sorted(years),
            "density_counts":dict(density),
            "by_bay":dict(by_bay),
            "top_species":species.most_common(20),
            "top_epiphyte_types":[x.most_common(30) for x in type_counts]
        },
        "thalassia":{
            "rows_with_density":sum(fdensity.values()),
            "unique_points":len(fpoints),
            "unique_visits":len(fvisits),
            "unique_transects":len(fnodes),
            "years":sorted(fyears),
            "density_counts":dict(fdensity),
            "by_bay":dict(fbay),
            "top_epiphyte_types":[x.most_common(30) for x in ftype]
        },
        "unexpected_focal_density_rows":bad_rows[:20],
        "claim_boundary":[
            "Coverage was audited before any epiphyte-to-Tampa-response association was fit.",
            "This source contains a substantial epiphyte layer that the current annual-state manuscript does not analyze.",
            "EpiphyteDensity is an ordinal qualitative field, not percent epiphyte cover or biomass.",
            "BAD DATA is excluded, not recoded.",
            "Epiphyte association with future meadow state remains untested at this preflight stage."
        ]
    }
    (outdir/"epiphyte_measurement_layer_preflight_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps({
        "status":result["status"],
        "all_taxa":{k:result["all_taxa"][k] for k in ("rows_with_density","unique_points","unique_visits","unique_transects")},
        "thalassia":{k:result["thalassia"][k] for k in ("rows_with_density","unique_points","unique_visits","unique_transects","density_counts","by_bay")},
    },indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/generated_epiphyte_preflight"))
    a=p.parse_args(); main(a.out)
