#!/usr/bin/env python3
"""Public mapped-vegetation field-verification candidate polygons.

Derived from certified source-overlap geometry, NOT biological extinction,
restoration authorization or field access. Every shape is 2016 seagrass-
positive ∩ 2022 attached algae ∩ its explicit 2024 classification. Export
only polygonal cores 10 and 25 m inside all relevant mapped class boundaries
and >=0.25 acres (the official minimum mapping unit).
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from shapely.geometry import mapping
from shapely.ops import unary_union,transform
from pyproj import Transformer

BASE=Path(__file__).resolve().parents[1]
SRC=BASE/"analysis/100_charlotte_2016_2022_2024_positive_only_overlay.py"
S=importlib.util.spec_from_file_location("ch100",SRC)
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
REVERSE=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True).transform
CLASS_LABELS={
   "2024_mapped_seagrass":"Previously mapped seagrass; algae in 2022; mapped seagrass in 2024",
   "2024_mapped_attached_algae":"Previously mapped seagrass; algae in 2022 and 2024",
   "2024_unmapped":"Previously mapped seagrass; algae in 2022; 2024 target class unrecorded"}
MIN_ACRES=0.25
DISTANCES=(10.0,25.0)
MAX_FEATURES=10000

def polygon_parts(g):
    return M.M.polygon_parts(g)

def candidate_components(pos16,algae22,sea24,algae24,distances=DISTANCES,
                         min_acres=MIN_ACRES):
    if not distances or min_acres<.25:
        raise M.M.GateStop("INVALID_FIXED_FIELD_TRAINING_CRITERION")
    features=[]
    summaries={}
    for d in distances:
        if d<0:raise M.M.GateStop("NEGATIVE_INTERIOR_DISTANCE")
        hist=pos16.buffer(-d).intersection(algae22.buffer(-d))
        classes={
         "2024_mapped_seagrass":hist.intersection(sea24.buffer(-d)),
         "2024_mapped_attached_algae":hist.intersection(algae24.buffer(-d)),
         # Unknown target mapping: do not infer bare bottom. Require distance
         # from ANY mapped 2024 class polygon, hence positive buffer.
         "2024_unmapped":hist.difference(unary_union([sea24,algae24]).buffer(d))
        }
        for cl,g in classes.items():
            if not g.is_valid:raise M.M.GateStop("CORE_OVERLAY_INVALID")
            parts=[p for p in polygon_parts(g) if p.area>0]
            valid=[p for p in parts if p.area/M.M.M2_PER_ACRE>=min_acres]
            total=sum(p.area for p in valid)/M.M.M2_PER_ACRE
            whole=sum(p.area for p in parts)/M.M.M2_PER_ACRE
            summaries[f"{int(d)}m::{cl}"]={
               "mapped_core_acres_all_fragments":round(whole,3),
               "eligible_core_acres_ge_0_25_acre":round(total,3),
               "candidate_polygon_count":len(valid),
               "excluded_sliver_acres":round(whole-total,3)
            }
            for p in valid:
                rep=p.representative_point()
                core_geojson=mapping(transform(REVERSE,p))
                lon,lat=REVERSE(rep.x,rep.y)
                if not(-83.5<lon<-81.0 and 25.0<lat<28.0):
                    raise M.M.GateStop("SUGGESTED_VERIFICATION_POINT_OUTSIDE_CHARLOTTE")
                features.append({"type":"Feature",
                    "properties":{
                     "class":cl,"classification":CLASS_LABELS[cl],
                     "all_three_year_source_mapped_only":True,
                     "years":[2016,2022,2024],
                     "metres_inside_mapped_boundaries":d,
                     "area_acres":round(p.area/M.M.M2_PER_ACRE,5),
                     "representative_point_lon":round(lon,7),
                     "representative_point_lat":round(lat,7),
                     "not_official_field_site":True,
                     "field_access_and_permits_not_verified":True,
                     "not_restoration_priority_score":True},
                    "geometry":core_geojson})
                if len(features)>MAX_FEATURES:
                    raise M.M.GateStop("OUTPUT_CANDIDATE_LIMIT_EXCEEDED")
    features.sort(key=lambda f:(
        f["properties"]["metres_inside_mapped_boundaries"],
        f["properties"]["class"],-f["properties"]["area_acres"]))
    for i,f in enumerate(features):
        f["properties"]["candidate_id"]=f"MAPVERIFY_{i+1:05d}"
    return features,summaries

def analyze(d16,d22,d24):
    a16,q16=M.M.prepare(d16["features"],"ACRES")
    a22,q22=M.M.prepare(d22["features"],"Geodesic")
    a24,q24=M.M.prepare(d24["features"],"ACRES")
    pos16=unary_union([a16[9113],a16[9116]])
    sea24=unary_union([a24[9113],a24[9116]])
    features,summary=candidate_components(pos16,a22[9121],sea24,a24[9121])
    return {
     "schema":"tampa.charlotte_historical_map_field_verification_candidates_v1",
     "status":"SOURCE_MAPPED_VERIFICATION_LOCATIONS_NOT_FIELDPERMITS",
     "evidence_class":"POSTHOC_PUBLIC_GIS_MAP_CORES_ONLY",
     "source_oids_sha256":{
       "2016":d16["source_oids_sha256"],
       "2022":d22["oid_inventory_sha256"],
       "2024":d24["oid_inventory_sha256"]},
     "candidate_area_summaries":summary,
     "feature_count":len(features),
     "source_quality":{"2016":q16,"2022":q22,"2024":q24},
     "geometry_type":"EPSG:4326 GeoJSON Polygon or MultiPolygon",
     "min_candidate_area_acres":MIN_ACRES,
     "interior_metre_thresholds":list(DISTANCES),
     "field_confirmation_required":[
        "2024 field revisit status, physical quadrat/point identity and complete sample effort",
        "focal Thalassia, Halodule and attached/detached algal abundance measured independently",
        "benthic light, epiphyte load, depth, sediment and field accessibility",
        "vegetated vs bare/undetected fate of 2024 unmapped categories"],
     "interpretation":"GIS-mapped verification areas only; classes cannot prove true death, recolonization, competition or suitability for restoration.",
     "no_permits_or_site_approval":True,
     "features":features}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    try:
        d16=M.source16();d22=M.M.download_year("2022");d24=M.M.download_year("2024")
        res=analyze(d16,d22,d24)
        rc=0
    except (M.M.GateStop,ValueError,TypeError,KeyError) as e:
        res={"schema":"tampa.charlotte_historical_map_field_verification_candidates_v1",
             "status":"STOP_MAP_SOURCE_OR_QC_GATE","reason":str(e),
             "no_permits_or_site_approval":True}
        rc=2
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(res,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in res.items() if k!="features"},ensure_ascii=False,sort_keys=True,indent=2))
    return rc
if __name__=="__main__":sys.exit(main())
