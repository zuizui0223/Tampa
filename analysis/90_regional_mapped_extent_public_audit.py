#!/usr/bin/env python3
"""Reproduce source-reported mapped seagrass acreage contrasts, descriptive only.

Input is an auditable, hand-transcribed table from two *public reports*, not
raw species/plot observations. Never pool across scope-specific mapping series.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from pathlib import Path
from collections import defaultdict

EXPECTED_SWFWMD = {
    "Tampa Bay": {2016:41655, 2018:40652, 2020:34297, 2022:30135, 2024:31562},
    "Charlotte Harbor": {2016:20280, 2018:19715, 2020:15273, 2022:14913, 2024:14020},
    "Sarasota Bay": {2016:13469, 2018:12853, 2020:10540, 2022:9963, 2024:11876},
}
EXPECTED_CHNEP = {2016:17329,2018:16938,2020:13355,2022:13098}
PRIMARY_ID = "SWFWMD_2026"
CHNEP_ID = "CHNEP_FACTSHEET_2023"
REQUIRED_HEADERS = {"series_id","estuary","year","acres","source_id"}
ALLOWED_SERIES = {
    (PRIMARY_ID,"Tampa Bay"), (PRIMARY_ID,"Charlotte Harbor"),
    (PRIMARY_ID,"Sarasota Bay"),
    (CHNEP_ID,"Charlotte Harbor (CHNEP distinct scope)"),
}
ECOLOGICAL_BOUNDARY = (
    "Mapped acreage is spatial habitat extent. It is not species-specific "
    "cover, shoot density, blade condition, shoot mortality, or resilience. "
    "Three estuaries and five mapping years cannot identify general causal "
    "stress or prove prediction. Published 2016-2017 local monitoring declines "
    "preceding 2018-2020 mapped loss are qualitative retrospective evidence, "
    "not a validated site-level leading indicator."
)

def change(a,b):
    return {"start_acres":a, "end_acres":b, "delta_acres":b-a,
            "percent_change":round(100*(b/a-1),4)}

def evaluate(csv_text, registry):
    if registry.get("schema") != "tampa.regional_mapped_extent_source_registry_v1":
        raise ValueError("Unverified registry schema")
    sources=registry.get("sources",{})
    if set(sources)!={PRIMARY_ID, CHNEP_ID}:
        raise ValueError("Source registry not exact")
    if not all(v.get("url","").startswith("https://") for v in sources.values()):
        raise ValueError("Source URLs invalid")
    data=defaultdict(dict)
    reader=csv.DictReader(csv_text.splitlines())
    if not reader.fieldnames or set(reader.fieldnames)!=REQUIRED_HEADERS:
        raise ValueError("Source table field drift")
    for row in reader:
        key=(row["series_id"],row["estuary"])
        if key not in ALLOWED_SERIES or row["source_id"]!=row["series_id"]:
            raise ValueError("Unapproved estuary/source or mixed series")
        year=int(row["year"]); acres=int(row["acres"])
        if year<1980 or year>2024 or acres<0 or year in data[key]:
            raise ValueError("Invalid or duplicated year/area")
        data[key][year]=acres
    if set(data)!=ALLOWED_SERIES: raise ValueError("Missing or extra mapping series")
    for estuary,anchors in EXPECTED_SWFWMD.items():
        observed=data[(PRIMARY_ID,estuary)]
        for y,v in anchors.items():
            if observed.get(y)!=v: raise ValueError(f"SWFWMD source anchor drift: {estuary}/{y}")
    chnep=data[(CHNEP_ID,"Charlotte Harbor (CHNEP distinct scope)")]
    for y,v in EXPECTED_CHNEP.items():
        if chnep.get(y)!=v: raise ValueError(f"CHNEP source anchor drift: {y}")

    primary={}
    for estuary in EXPECTED_SWFWMD:
        ser=data[(PRIMARY_ID,estuary)]
        primary[estuary]={
            "2016_to_2024":change(ser[2016],ser[2024]),
            "2016_to_2022":change(ser[2016],ser[2022]),
            "2018_to_2020":change(ser[2018],ser[2020]),
            "2022_to_2024":change(ser[2022],ser[2024]),
            "2016_index_100":{str(y):round(100*ser[y]/ser[2016],4)
                                    for y in (2016,2018,2020,2022,2024)},
        }
    if not all(x["2018_to_2020"]["delta_acres"]<0 for x in primary.values()):
        raise ValueError("Expected simultaneous 2018-2020 negative period not found")
    signs={k:("increase" if v["2022_to_2024"]["delta_acres"]>0 else
               "decline" if v["2022_to_2024"]["delta_acres"]<0 else "unchanged")
           for k,v in primary.items()}
    if set(signs.values())!={"increase","decline"}:
        raise ValueError("Expected directional divergence not reproduced")

    indexed_spread = {}
    for year in (2022, 2024):
        values = [primary[estuary]["2016_index_100"][str(year)] for estuary in EXPECTED_SWFWMD]
        indexed_spread[str(year)] = round(max(values) - min(values),4)
    # Descriptive cross-estuary dispersion at two time points, not independent inference.
    chdiff={str(y):data[(PRIMARY_ID,"Charlotte Harbor")][y]-chnep[y]
            for y in (2016,2018,2020,2022)}
    return {
        "schema":"tampa.regional_mapped_extent_context_v1",
        "evidence_status":"PUBLIC_AGENCY_REPORT_DESCRIPTIVE_REAGGREGATION",
        "not_untouched_prediction":True,
        "source_table_sha256":hashlib.sha256(csv_text.encode("utf-8")).hexdigest(),
        "primary_same_agency":PRIMARY_ID,
        "primary":primary,
        "shared_2018_to_2020_decline":True,
        "2022_to_2024_recovery_direction":signs,
        "regional_2016_index_spread_points":indexed_spread,
        "alternate_chnep_distinct_spatial_scope":{
            "2018_to_2020":change(chnep[2018],chnep[2020]),
            "2016_to_2022":change(chnep[2016],chnep[2022]),
            "swfwmd_minus_chnep_acres_same_year":chdiff,
            "chnep_text_2018_2020_loss_acres":3648,
            "chnep_chart_2018_2020_loss_acres":3583,
            "text_minus_chart_loss_acres":65,
            "scope_equivalence":"UNKNOWN_NOT_HARMONIZED",
        },
        "published_local_decline_note":{
            "source":"CHNEP Seagrass in Charlotte Harbor Fact Sheet, 2023",
            "reported_pattern":"Thalassia and Halodule abundance declines at multiple monitoring locations during 2016-2017 preceded 2018-2020 mapped acreage loss",
            "ecological_inference":"Retrospective chronology only; underlying repeat-transect responses, spatial match, detection, and statistical forecast are unavailable"
        },
        "inference_boundary":ECOLOGICAL_BOUNDARY,
    }

def main():
    root=Path(__file__).resolve().parents[1]
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument("--source-csv",default=str(root/"results/regional_extent_public_sources_v1.csv"))
    pa.add_argument("--registry",default=str(root/"results/regional_extent_public_sources_v1_registry.json"))
    pa.add_argument("--output",default=None)
    x=pa.parse_args()
    csv_text=Path(x.source_csv).read_text(encoding="utf-8")
    registry=json.loads(Path(x.registry).read_text(encoding="utf-8"))
    report=evaluate(csv_text,registry)
    output=json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if x.output:
        Path(x.output).parent.mkdir(parents=True,exist_ok=True)
        Path(x.output).write_text(output,encoding="utf-8")
    print(output,end="")
    return 0

if __name__=="__main__":
    sys.exit(main())
