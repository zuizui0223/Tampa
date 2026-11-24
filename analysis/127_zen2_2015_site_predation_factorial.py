#!/usr/bin/env python3
"""Original 2015 ZEN2 global eelgrass manipulation, site-equal faunal predation.

Pre-source hypothesis defined in docs/ZEN2_FOUNDATION_CONSUMER_EXPERIMENT_20261124.md
and exact response/treatment semantics confirmed in the original BCO-DMO source
dataset DOI 10.26008/1912/bco-dmo.724015.2.

Each tethered small crustacean is ONE prey trial, *not* an independent habitat.
Observations are nested in site, location, experimental plot and four rounds,
but the public source does NOT expose an unambiguous trial/plot key: global
inference is at the 17-site level, and no variance estimate for a single site
claims to account for all round/plot dependence.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

SOURCE_URL="https://datadocs.bco-dmo.org/dataset/724015/file/l880lRkF2gvLEO/crustacean_survival.csv"
SOURCE_SHA256="3de12972e709f6a856e60e6d8cbf6fd81cf824edb7d907c453301e3e42d596fb"
EXPECTED_SITES=17
EXPECTED_ROWS=2666
TARGET_COLUMNS=("Site","Taxon","Basin","Latitude","Longitude","Patch_location",
                "Shoot_reduction","Tether_no","Size_mm","Crust_biomass","Other_biomass",
                "Total_biomass","Epiphyte_biomass","Starting_shoot_dens","Calc_shoot_dens","Status")
LOCATIONS=("Edge","Interior")
TREATMENTS=("Amb","Fifty","Eighty")
SEED=2026112416
BOOT=5000

def load_source():
    req=Request(SOURCE_URL,headers={"User-Agent":"Tampa-ZEN2-original-17site/1.0",
                                    "Accept-Encoding":"identity"})
    with urlopen(req,timeout=90) as f:
        blob=f.read(500001)
    if len(blob)>500000 or hashlib.sha256(blob).hexdigest()!=SOURCE_SHA256:
        raise RuntimeError("2015 original ZEN2 CSV byte identity differs from source-verified source")
    return blob

def parse_rows(blob,verify_digest=True):
    if verify_digest and hashlib.sha256(blob).hexdigest()!=SOURCE_SHA256:
        raise ValueError("Original source checksum drift")
    reader=csv.DictReader(io.StringIO(blob.decode("utf-8-sig")))
    if reader.fieldnames!=list(TARGET_COLUMNS):
        raise ValueError("Unexpected original source header")
    rows=list(reader)
    if any(None in r for r in rows):raise ValueError("Malformed CSV row")
    result=[]
    for i,r in enumerate(rows,2):
        site=r["Site"].strip();loc=r["Patch_location"].strip();treatment=r["Shoot_reduction"].strip()
        status=r["Status"].strip()
        if not site or loc not in LOCATIONS or treatment not in TREATMENTS or status not in ("0","1"):
            raise ValueError(f"Unexpected factor or outcome at line {i}")
        def numeric(key,allow_na=True):
            val=r[key].strip()
            if val.upper() in ("","NA","N/A"):
                if allow_na:return None
                raise ValueError(f"Missing essential {key} at line {i}")
            try:v=float(val)
            except ValueError as e:raise ValueError(f"Invalid numeric {key} at line {i}") from e
            if not math.isfinite(v) or v<0:raise ValueError(f"Negative/nonfinite {key} at line {i}")
            return v
        density=numeric("Calc_shoot_dens",False)
        initial=numeric("Starting_shoot_dens",False)
        result.append({"site":site,"location":loc,"treatment":treatment,
                       "recorded_eaten":int(status),"taxon":r["Taxon"].strip(),
                       "density_actual":density,"density_initial":initial,
                       "size_mm":numeric("Size_mm"),
                       "epibiont":numeric("Epiphyte_biomass"),
                       "crust_biomass":numeric("Crust_biomass"),
                       "tether":r["Tether_no"].strip()})
    return result

def mean(x):return statistics.mean(x)

def pearson(x,y):
    if len(x)!=len(y) or len(x)<5:return None
    a=mean(x);b=mean(y);xx=sum((v-a)**2 for v in x);yy=sum((v-b)**2 for v in y)
    return sum((u-a)*(v-b) for u,v in zip(x,y))/math.sqrt(xx*yy) if xx>0 and yy>0 else None

def contrast(cells):
    m=lambda loc,tr:cells[(loc,tr)]
    edge=mean([m("Edge",t)-m("Interior",t) for t in TREATMENTS])
    fifty=mean([m(loc,"Fifty")-m(loc,"Amb") for loc in LOCATIONS])
    eighty=mean([m(loc,"Eighty")-m(loc,"Amb") for loc in LOCATIONS])
    interaction_80=(m("Edge","Eighty")-m("Interior","Eighty"))-(m("Edge","Amb")-m("Interior","Amb"))
    return {"edge_minus_interior_risk":edge,"fifty_minus_ambient_risk":fifty,
            "eighty_minus_ambient_risk":eighty,
            "edge_by_eighty_thinning_difference_in_differences":interaction_80}

def site_table(rows):
    bysite=defaultdict(list)
    for r in rows:bysite[r["site"]].append(r)
    out=[]
    for site,rs in sorted(bysite.items()):
        cells=defaultdict(list)
        for r in rs:cells[(r["location"],r["treatment"])].append(r)
        if set(cells)!={(loc,tr) for loc in LOCATIONS for tr in TREATMENTS}:
            raise ValueError(f"Site lacks a predeclared factorial cell: {site}")
        if any(len(x)<5 for x in cells.values()):
            raise ValueError(f"Site has fewer than five tethered prey trials per cell: {site}")
        means={(loc,tr):mean([x["recorded_eaten"] for x in cell])
               for (loc,tr),cell in cells.items()}
        out.append({
            "site":site,"trials":len(rs),
            "site_recorded_predation_fraction":mean([x["recorded_eaten"] for x in rs]),
            "n_by_location_thinning":{f"{loc}|{tr}":len(cells[(loc,tr)])
                                       for loc in LOCATIONS for tr in TREATMENTS},
            "eaten_by_location_thinning":{f"{loc}|{tr}":sum(x["recorded_eaten"] for x in cells[(loc,tr)])
                                          for loc in LOCATIONS for tr in TREATMENTS},
            "risk_by_location_thinning":{f"{loc}|{tr}":means[(loc,tr)]
                                         for loc in LOCATIONS for tr in TREATMENTS},
            "site_average_initial_shoot_density":mean([x["density_initial"] for x in rs]),
            "site_average_calculated_shoot_density":mean([x["density_actual"] for x in rs]),
            "contrasts":contrast(means),
            "taxa":dict(Counter(x["taxon"] for x in rs)),
            "source_tether_number_uniques":len({x["tether"] for x in rs}),
        })
    return out

def bootstrap_site_mean(xs,seed=SEED):
    if len(xs)<5:raise ValueError("Fewer than five sites")
    rng=random.Random(seed);n=len(xs)
    draws=sorted(mean([xs[rng.randrange(n)] for _ in range(n)]) for i in range(BOOT))
    return {"mean_site_equal":mean(xs),
            "median_site":statistics.median(xs),
            "site_bootstrap_95pct_percentile":[draws[math.floor((BOOT-1)*.025)],
                                               draws[math.ceil((BOOT-1)*.975)]],
            "positive_sites":sum(x>0 for x in xs),"negative_sites":sum(x<0 for x in xs),
            "zero_sites":sum(x==0 for x in xs),
            "leave_one_site_out_mean_range":[
                min(mean(xs[:i]+xs[i+1:]) for i in range(n)),
                max(mean(xs[:i]+xs[i+1:]) for i in range(n))
            ],
            "sites":n,"bootstrap_resamples":BOOT}

def analyze(rows):
    sites=site_table(rows)
    names=("edge_minus_interior_risk","fifty_minus_ambient_risk",
           "eighty_minus_ambient_risk","edge_by_eighty_thinning_difference_in_differences")
    return {
        "schema":"tampa.zen2_2015_original_site_equal_predation_v1",
        "evidence_class":"reanalysis_of_Hovel_et_al_2021_original_public_experiment",
        "source_doi":"10.26008/1912/bco-dmo.724015.2",
        "source_paper_doi":"10.1002/ecy.3316",
        "source_sha256":SOURCE_SHA256,
        "site_count":len(sites),
        "tethered_prey_count":sum(x["trials"] for x in sites),
        "recorded_eaten_count":sum(sum(x["eaten_by_location_thinning"].values()) for x in sites),
        "recorded_alive_count":sum(x["trials"] for x in sites)-sum(sum(x["eaten_by_location_thinning"].values()) for x in sites),
        "source_cell_coverage":sites,
        "site_equal_contrasts":{
            name:bootstrap_site_mean([x["contrasts"][name] for x in sites],seed=SEED+i)
            for i,name in enumerate(names)
        },
        "physical_density_aggregate": {
            "mean_site_average_initial_shoot_density":mean([x["site_average_initial_shoot_density"] for x in sites]),
            "mean_site_average_calculated_shoot_density":mean([x["site_average_calculated_shoot_density"] for x in sites]),
        },
        "limits":[
            "The global 17-site patch edge and shoot-thinning test was already published by Hovel et al. 2021.",
            "Status=1 is recorded consumed; 0 alive. Tethered predation is not natural population survival.",
            "Site means, not individual tether records or repeated trials, are geographic replicates.",
            "Site bootstrap is exploratory and does not account for all unrecorded plot/trial dependence.",
            "Habitat edge is a spatial context, not randomized intervention; thinning levels were manipulated.",
            "No plant growth, TNC, meadow annual retention, predator abundance, or consumer-mediated grazer benefit is measured in this experimental endpoint.",
            "Do not treat 2011 grazer-deterrent 15-site results as an intervention performed on the 2015 tethered organisms.",
        ]
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None);args=p.parse_args()
    b=load_source();rows=parse_rows(b);out=analyze(rows)
    if out["site_count"]!=EXPECTED_SITES or out["tethered_prey_count"]!=EXPECTED_ROWS:
        raise ValueError("Original site and tether frame drift")
    s=json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
