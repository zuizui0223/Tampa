#!/usr/bin/env python3
"""Response-open, source-audited global seagrass observation-grain feasibility analysis.

Strydom et al. (2021) PANGAEA 929968. Unlike frozen external Tampa
early-warning holdouts, this is an explicitly exploratory GLOBAL CROSS-SECTIONAL
database audit. Never treat literature records as independent permanent marks.

Source license: CC-BY-4.0, cite the original dataset DOI and ESSD 2023 paper.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from urllib.request import Request, urlopen

DATASET_URL="https://doi.org/10.1594/PANGAEA.929968"
DOI="10.1594/PANGAEA.929968"
ESSD_DOI="10.5194/essd-15-511-2023"
EXPECTED={
    "lat":"Latitude", "lon":"Longitude",
    "region":"Seagr bioregion", "habitat":"Habitat", "genus":"Genus",
    "year":"Year obs", "ag":"Seagr biom above dm",
    "bg":"Seagr biom below dm", "total":"Seagr biom tot dm",
    "shoot":"Seagr shoot dens", "cover":"Seagr cov",
    "ref":"Reference",
}
MEASURES=("ag","bg","total","shoot","cover")


def download()->bytes:
    req=Request(DATASET_URL,headers={
        "User-Agent":"Tampa-Global-Seagrass-Macro-Feasibility/1.0",
        "Accept":"text/tab-separated-values",
        "Accept-Encoding":"identity",
    })
    with urlopen(req,timeout=120) as resp:
        raw=resp.read(20_000_001)
    if len(raw)>20_000_000:
        raise RuntimeError("Unexpected data size >20MB")
    if b"Latitude\\tLongitude" not in raw and b"Latitude\tLongitude" not in raw:
        raise RuntimeError("PANGAEA DOI content negotiation did not return the required original tabular data")
    return raw


def tabular(raw:bytes):
    if raw[:2000].lstrip().lower().startswith((b"<!doctype",b"<html")):
        raise ValueError("HTML returned instead of PANGAEA tab-delimited data")
    text=raw.decode("utf-8-sig")
    lines=text.splitlines()
    headers=[i for i,line in enumerate(lines) if line.startswith("Latitude\t")]
    if len(headers)!=1:
        raise ValueError("Expected exactly one Latitude tab header after PANGAEA metadata")
    i=headers[0]
    r=csv.DictReader(io.StringIO("\n".join(lines[i:])),delimiter="\t")
    if not r.fieldnames or len(r.fieldnames)!=len(set(r.fieldnames)):
        raise ValueError("Invalid or duplicate raw headers")
    keys={}
    for symbol,prefix in EXPECTED.items():
        matches=[h for h in r.fieldnames if h==prefix or h.startswith(prefix+" [")]
        if len(matches)!=1:
            raise ValueError(f"Missing or ambiguous column {prefix}: {matches}")
        keys[symbol]=matches[0]
    rows=list(r)
    if any(None in x for x in rows):
        raise ValueError("Malformed raw tabular record")
    if len(rows)<100:
        raise ValueError("PANGAEA data prematurely truncated")
    return rows,keys,{"header_line":i+1,"header":r.fieldnames}


def parse_num(value:str):
    value=str(value or "").strip()
    if not value:
        return None
    try:
        x=float(value)
    except (ValueError,TypeError):
        return None
    return x if math.isfinite(x) else None


def quantile(arr,frac):
    x=sorted(arr)
    if not x:
        return None
    t=(len(x)-1)*frac
    i=math.floor(t)
    return x[i]*(1-(t-i))+x[min(i+1,len(x)-1)]*(t-i)


def audit(rows,keys):
    counts=Counter()
    invalid=Counter()
    study_years=defaultdict(set)
    siteyears=defaultdict(lambda:Counter())
    site_coords=defaultdict(set)
    bygenus=defaultdict(list)
    byregion=defaultdict(list)
    years=[]
    refs=set()
    exact_raw_row_counts=Counter(tuple(row[k] for k in rows[0].keys()) for row in rows)
    duplicated_member_rows=sum(c for c in exact_raw_row_counts.values() if c>1)
    duplicate_groups=sum(c>1 for c in exact_raw_row_counts.values())
    genera=set()
    regions=set()
    habitats=set()
    pair_studies=set()
    paired=[]
    nonzero_cover=0
    numeric_cover=0
    for row in rows:
        def f(k):return str(row[keys[k]] or "").strip()
        ref,genus,region,habitat=f("ref"),f("genus"),f("region"),f("habitat")
        if not all([ref,genus,region]):
            invalid["missing_required_reference_genus_or_bioregion"]+=1
            continue
        lat,lon=parse_num(f("lat")),parse_num(f("lon"))
        yr=parse_num(f("year"))
        if lat is None or lon is None or not -90<=lat<=90 or not -180<=lon<=180:
            invalid["invalid_geolocation"]+=1
            continue
        if yr is None or not 1900<=yr<=2025 or int(yr)!=yr:
            invalid["missing_or_noninteger_year"]+=1
        year=int(yr) if yr is not None and 1900<=yr<=2025 and int(yr)==yr else None
        refs.add(ref);genera.add(genus);regions.add(region);habitats.add(habitat)
        if year is not None:
            years.append(year)
            # literature/site-coordinate matches are candidate study repeat years only,
            # not verified same permanently sampled subplot or seasonal match.
            site=(ref,lat,lon,genus)
            siteyears[site][year]+=1
            site_coords[(ref,lat,lon)].add(genus)
            study_years[ref].add(year)
        measures={}
        for k in MEASURES:
            v=parse_num(f(k))
            if v is not None:
                counts[k]+=1
                if k=="cover":
                    numeric_cover+=1
                    nonzero_cover+=int(v>0)
                    if not 0<=v<=100:
                        invalid["cover_outside_0_100"]+=1
                if k in ("ag","bg","total","shoot") and v<0:
                    invalid[f"negative_{k}"]+=1
            elif f(k):
                invalid[f"nonnumeric_{k}"]+=1
            measures[k]=v
        for x,y,label in (("ag","bg","paired_ag_bg"),("bg","cover","paired_bg_cover"),
                          ("ag","cover","paired_ag_cover"),("shoot","cover","paired_shoot_cover")):
            if measures[x] is not None and measures[y] is not None:
                counts[label]+=1
        a,b=measures["ag"],measures["bg"]
        if a is not None and b is not None and a>0 and b>0:
            ratio=b/a
            paired.append(ratio)
            bygenus[genus].append((ratio,ref))
            byregion[region].append((ratio,ref))
            pair_studies.add(ref)
        if any(v is not None for v in measures.values()):
            counts["rows_with_target_measures"]+=1
    candidates=[
        {"reference":x[0],"latitude":x[1],"longitude":x[2],"genus":x[3],
         "n_years":len(y),"years":sorted(y),"rows":sum(y.values())}
        for x,y in siteyears.items() if len(y)>=2
    ]
    candidates.sort(key=lambda x:(-x["n_years"],-x["rows"],x["reference"],x["genus"]))
    def group_summary(groups):
        return sorted([
            {"group":key,"paired_rows":len(v),
             "distinct_references":len({ref for ratio,ref in v}),
             "median_below_to_above_biomass":median([z[0] for z in v]),
             "q25_ratio":quantile([z[0] for z in v],.25),
             "q75_ratio":quantile([z[0] for z in v],.75)}
            for key,v in groups.items()
        ],key=lambda x:-x["paired_rows"])
    return {
        "source_row_count":len(rows),
        "raw_reference_strings_not_independent_publications":len(refs),
        "exact_duplicate_member_rows_not_automatically_removed":duplicated_member_rows,
        "exact_duplicate_row_groups":duplicate_groups,
        "source_years_are_not_permanent_mark_revisits":True,
        "references":len(refs),
        "genera":len(genera),
        "bioregions":len(regions),
        "habitat_classes":sorted(habitats),
        "sampling_year_range":[min(years),max(years)] if years else None,
        "nonempty_measure_counts":dict(counts),
        "parse_and_domain_warnings":dict(invalid),
        "cover_values_with_positive_value":nonzero_cover,
        "total_numeric_cover_values":numeric_cover,
        "exact_same_row_paired_above_below_count":len(paired),
        "references_in_exact_same_row_biomass_pairs":len(pair_studies),
        "same_row_median_bg_to_ag_ratio":median(paired) if paired else None,
        "same_row_ratio_q25_q75":[quantile(paired,.25),quantile(paired,.75)] if paired else None,
        "paired_ratio_by_genus":group_summary(bygenus),
        "paired_ratio_by_bioregion":group_summary(byregion),
        "publication_geocoordinate_genus_candidates_with_two_or_more_years":len(candidates),
        "references_with_candidate_multiyear_groups":len({x["reference"] for x in candidates}),
        "candidate_multiyear_groups_top20":candidates[:20],
        "references_with_multiple_reported_years":sum(len(y)>=2 for y in study_years.values()),
        "note":(
            "Coordinates/genus/year within a publication are NOT verified fixed marks; "
            "all paired records are publication-extracted and can be correlated. "
            "No true absence or mapped extent is present in the dataset."
        ),
    }


def execute(raw:bytes):
    rows,keys,schema=tabular(raw)
    stats=audit(rows,keys)
    return {
        "schema":"tampa.global_seagrass_929968_feasibility_v1",
        "evidence_class":"exploratory_global_literature_reanalysis_not_longitudinal_validation",
        "source":{
            "original_dataset_doi":DOI,
            "related_essd_doi":ESSD_DOI,
            "url":DATASET_URL,
            "download_sha256":hashlib.sha256(raw).hexdigest(),
            "license":"CC BY 4.0",
            "schema":schema,
        },
        "audit":stats,
        "hard_stops":[
            "This global literature database is NOT a seagrass site-absence record.",
            "Observation year is not evidence that the same permanent quadrat was revisited.",
            "Repeated extracted values are not independent literature studies or sampling units.",
            "Raw Reference strings include known bibliographic corruption and can overcount independent articles; never use their count as n_studies.",
            "Exact duplicate rows are counted but not automatically removed because field replicate status is unresolved.",
            "Same-row biomass allocation ratio is a static cross-sectional measurement, not clonal carbon storage or TNC.",
            "Do not treat pooled genus/bioregion differences as ecological mechanism without study-cluster and location checks.",
            "The 2025 JBI global genus/life-history/temperature analysis already exists; this audit alone is not a novel macroecological discovery.",
            "Do not reuse the already-opened SeagrassNet external early-warning validation as untouched.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=None)
    p.add_argument("--raw-out",type=Path,default=None,help="Write exact downloaded CC-BY source for downstream same-run analysis")
    a=p.parse_args()
    raw=download()
    if a.raw_out:
        a.raw_out.parent.mkdir(parents=True,exist_ok=True)
        a.raw_out.write_bytes(raw)
    r=execute(raw)
    s=json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:
        print(s,end="")


if __name__=="__main__":
    main()
