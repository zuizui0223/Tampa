#!/usr/bin/env python3
"""Response-blind geographic linkage audit for the 2014/2015 ZEN2 cohorts.

This reads source original files, checks both published SHA256 checksums,
then *only* coordinates/site names/codes. Does not open 2015 Status or 2014
seagrass/consumer responses. It prevents joining unrelated different-year
meadows by a superficially shared site code.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics
from collections import defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

SOURCES={
    "2014":("https://datadocs.bco-dmo.org/dataset/712069/file/1VVMOrXtMO4KM1/ZEN2_survey_sorted.csv",
            "c2af785e48aa76f88834e6c96ab69f49f85feb0918a89f9ec0585680cb170034",150000),
    "2015":("https://datadocs.bco-dmo.org/dataset/724015/file/l880lRkF2gvLEO/crustacean_survival.csv",
            "3de12972e709f6a856e60e6d8cbf6fd81cf824edb7d907c453301e3e42d596fb",500000),
}
THRESHOLD_KM=25.0
AMBIGUOUS_CODE_FAMILIES={"KOA":"KO","KOB":"KO"}

def download(kind):
    url,sha,limit=SOURCES[kind]
    req=Request(url,headers={"User-Agent":"Tampa-ZEN2-geography-audit/1.0","Accept-Encoding":"identity"})
    with urlopen(req,timeout=90) as f:
        raw=f.read(limit+1)
    if len(raw)>limit or hashlib.sha256(raw).hexdigest()!=sha:
        raise ValueError("Original response-blind geographic source identity drift")
    return raw

def haversine(a,b):
    lat1,lon1=a;lat2,lon2=b
    if not all(math.isfinite(z) for z in (*a,*b)) or not all(-90<=x<=90 for x in (lat1,lat2)) or not all(-180<=x<=180 for x in (lon1,lon2)):
        raise ValueError("Invalid original geographic coordinate")
    p1,p2=math.radians(lat1),math.radians(lat2)
    dp=p2-p1;dl=math.radians(lon2-lon1)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(x)))

def get_rows(blob,kind,verify=True):
    if verify and hashlib.sha256(blob).hexdigest()!=SOURCES[kind][1]:
        raise ValueError("Source checksum failed")
    reader=csv.DictReader(io.StringIO(blob.decode("utf-8-sig")),delimiter=",")
    needed={
        "2014":{"Site_Code","Site","Subsite","Subsite_Name","Latitude","Longitude","Date_Collected"},
        "2015":{"Site","Latitude","Longitude"}
    }[kind]
    if reader.fieldnames is None or not needed.issubset(reader.fieldnames):
        raise ValueError("Required response-blind coordinate columns missing")
    items=[]
    for raw in reader:
        try:
            lat=float(raw["Latitude"]);lon=float(raw["Longitude"])
        except (ValueError,TypeError) as e:
            raise ValueError("Invalid source coordinate") from e
        if not -90<=lat<=90 or not -180<=lon<=180:
            raise ValueError("Source coordinate out of range")
        site=(raw["Site_Code"] if kind=="2014" else raw["Site"]).strip()
        if not site:raise ValueError("Missing source location label")
        if kind=="2014" and not str(raw["Date_Collected"]).startswith("2014"):
            raise ValueError("Unexpected 2014 survey date")
        items.append({
            "code":site,
            "id":raw["Site"].strip() if kind=="2014" else site,
            "name":raw.get("Subsite_Name","").strip(),
            "lat":lat,"lon":lon,
        })
    if (kind=="2014" and len(items)!=50) or (kind=="2015" and len(items)!=2666):
        raise ValueError("Original frame size drift")
    return items

def audit(old,new,threshold=THRESHOLD_KM):
    if not 0<threshold<500:raise ValueError("Unreasonable predeclared geographic threshold")
    groups_old=defaultdict(list)
    for r in old:groups_old[r["code"]].append(r)
    groups_new=defaultdict(list)
    for r in new:groups_new[r["code"]].append(r)
    if len(groups_old)!=25 or len(groups_new)!=17:
        raise ValueError("Unexpected sample-geography clusters")
    if any(len(g)!=2 for g in groups_old.values()):
        raise ValueError("2014 region code lacks exactly two subsite summaries")
    candidates=[]
    for code,study in sorted(groups_new.items()):
        # 2015 source rows are prey-level repeats of same original site geolocation:
        coords={(r["lat"],r["lon"]) for r in study}
        if len(coords)!=1:
            raise ValueError(f"Multiple 2015 site coordinates for {code}; manual review needed")
        match=AMBIGUOUS_CODE_FAMILIES.get(code,code)
        ambiguous=(code in AMBIGUOUS_CODE_FAMILIES)
        old_group=groups_old.get(match,[])
        loc=(study[0]["lat"],study[0]["lon"])
        distances=[haversine(loc,(r["lat"],r["lon"])) for r in old_group]
        min_distance=min(distances) if distances else None
        candidates.append({
            "source_2015_site":code,
            "source_2015_lat_lon":list(loc),
            "source_2014_region_code":match if old_group else None,
            "source_2014_subsite_ids":[r["id"] for r in old_group],
            "source_2014_subsite_names":[r["name"] for r in old_group],
            "source_2014_to_2015_distances_km":[round(z,3) for z in distances],
            "closest_subsite_id":(old_group[distances.index(min_distance)]["id"] if distances else None),
            "closest_distance_km":round(min_distance,3) if min_distance is not None else None,
            "code_mapping_ambiguous":ambiguous,
            "eligible_as_prior_site_context":(
                bool(old_group) and not ambiguous and min_distance<=threshold
            ),
            "prior_site_context_unit":"2014 source region-code with 2 subsites, not same permanent plot"
        })
    return {
        "schema":"tampa.zen2_2014_2015_source_geographic_link_audit_v1",
        "evidence_class":"response_blind_original_source_coordinate_audit",
        "source_shas":{k:v[1] for k,v in SOURCES.items()},
        "spatial_maximum_nearest_subsite_km":threshold,
        "source_2014_subsites":len(old),
        "source_2015_tether_trials":len(new),
        "distinct_2014_region_codes":len(groups_old),
        "distinct_2015_site_codes":len(groups_new),
        "eligible_site_codes":[r["source_2015_site"] for r in candidates if r["eligible_as_prior_site_context"]],
        "noneligible_site_codes":[r["source_2015_site"] for r in candidates if not r["eligible_as_prior_site_context"]],
        "candidates":candidates,
        "strict_limits":[
            "Same site code plus nearby coordinates is a candidate region-level context, not the same permanent quadrat.",
            "2014 A/B pair is region-level not 2015 edge-versus-interior orientation.",
            "No outcomes were accessed in this linkage audit; all 2015/status and 2014 biomass columns are ignored.",
            "KOA/KOB map ambiguously to 2014 KO and are excluded from direct one-to-one links.",
            "Do not tune nearest-neighbor distance threshold after seeing any 2015 risk outcome.",
            "Date difference does not identify mechanistic causation or out-of-sample validation.",
        ],
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,default=None)
    args=ap.parse_args()
    j=audit(get_rows(download("2014"),"2014"),get_rows(download("2015"),"2015"))
    s=json.dumps(j,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(s,encoding="utf8")
    else:print(s,end="")

if __name__=="__main__":main()
