#!/usr/bin/env python3
"""Mapped-class two-year stability vs instability in Charlotte Harbor.

Archive-only: reuses exactly the previously source-verified 2022 and 2024
GeoJSON polygon vectors and independent original acreage audit. NO live GIS,
field plant data or species-level mortality. This is POST-HOC descriptive
class persistence, not a test of ecological longevity or causal competition.
"""
from __future__ import annotations
import argparse,importlib.util,json,sys
from pathlib import Path
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("archive102",ROOT/"analysis/102_charlotte_historical_overlap_archived_reference.py")
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)
G=A.M.M # previously verified two-year 92 public GIS source toolkit
FROZEN_SOURCE_ARCHIVE_RUN=A.ARCHIVE_RUN_ID
EXPECTED_2024_FILE="charlotte_2024_positive_only_or_full.geojson"

class Stop(RuntimeError): pass

def get_locked_geometries(archive_root,original):
    original22=original["modern_source"]["2022"]
    original24=original["modern_source"]["2024"]
    f22,_=A.load_source_features(archive_root,"2022",original22["raw_geojson_canonical_sha256"],2303)
    f24_path=A._one_archive_file(archive_root,EXPECTED_2024_FILE)
    blob=json.loads(f24_path.read_text(encoding="utf-8"))
    f24=blob.get("features")
    if blob.get("type")!="FeatureCollection" or not isinstance(f24,list) or len(f24)!=3209:
        raise Stop("FROZEN_2024_GEOJSON_FORMAT_OR_COUNT_CHANGED")
    if G.sha(f24)!=original24["raw_geojson_canonical_sha256"]:
        raise Stop("FROZEN_2024_GEOJSON_SOURCE_SHA_CHANGED")
    if set(f["properties"].get("FLUCCSCODE") for f in f24)!={9113,9116,9121}:
        raise Stop("FROZEN_2024_CLASS_DICTIONARY_CHANGED")
    source,qc22=G.prepare(f22,"Geodesic")
    target,qc24=G.prepare(f24,"ACRES")
    for year,actual in (("2022",qc22),("2024",qc24)):
        expected=original["area_qc"][year]
        if not actual["all_polygons_checked_against_original_area_field"]:
            raise Stop("OFFICIAL_SOURCE_AREA_NOT_VERIFIED:"+year)
        for code in ("9113","9116","9121"):
            if abs(actual["class_area_acres"][code]-expected["class_area_acres"][code])>.003:
                raise Stop("FROZEN_CLASS_ACREAGE_CHANGED:"+year+":"+code)
    return source,target,{"2022":qc22,"2024":qc24}

def stability(source,target, distances=(0.,5.,10.,25.)):
    if list(distances)!=[0.,5.,10.,25.]:
        raise Stop("PRIMARY_BOUNDARY_DISTANCES_CHANGED")
    sea22=unary_union([source[9113],source[9116]])
    sea24=unary_union([target[9113],target[9116]])
    alg22=source[9121];alg24=target[9121]
    classes={"seagrass":(sea22,sea24),"attached_macroalgae":(alg22,alg24)}
    result={}
    for name,(src,tgt) in classes.items():
        original=src.area
        if original<=0:raise Stop("FROZEN_ORIGINAL_SOURCE_CLASS_EMPTY:"+name)
        vals={};prev=None
        for d in distances:
            eroded_src=src if d==0 else src.buffer(-d)
            eroded_target=tgt if d==0 else tgt.buffer(-d)
            retained=eroded_src.intersection(eroded_target).area
            if retained<-1e-5 or retained>original+1e-5:
                raise Stop("IMPOSSIBLE_2YEAR_STABILITY_AREA")
            if prev is not None and retained>prev+1e-5:
                raise Stop("INTERIOR_STABILITY_NONMONOTONIC")
            prev=retained
            vals[str(int(d))]={
              "same_class_overlap_acres":round(retained/G.M2_PER_ACRE,3),
              "fixed_2022_source_area_retained_percent":round(100*retained/original,3),
              "area_within_2022_class_interior_acres":round(eroded_src.area/G.M2_PER_ACRE,3),
              "area_fraction_of_eroded_2022_class_percent":round(
                  100*retained/eroded_src.area,3) if eroded_src.area>0 else None
            }
        result[name]={
            "2022_class_area_acres":round(original/G.M2_PER_ACRE,3),
            "boundary_interior_m":vals}
    return {
      "classes":result,
      "seagrass_minus_algae_same_class_retention_percentage_points":round(
          result["seagrass"]["boundary_interior_m"]["0"]["fixed_2022_source_area_retained_percent"]-
          result["attached_macroalgae"]["boundary_interior_m"]["0"]["fixed_2022_source_area_retained_percent"],3),
      "no_biological_survival_conclusion":True,
      "no_independent_polygon_sample_size":True,
      "no_equivalence_of_detection_or_mapping":True,
      "interpretation":"The two mapped classes differ in how much of their 2022 *area* retains the same class in 2024. This may reflect morphology, thematic accuracy, observation timing, or genuine cover change; it is not evidence of differential lifespans."
    }

def run(archive_root):
    old=A.load_frozen_report()
    src,tgt,qc=get_locked_geometries(archive_root,old)
    out=stability(src,tgt)
    a=old["map_history"]
    expected_algae=a["2022_algae_total_acres"]
    if abs(out["classes"]["attached_macroalgae"]["2022_class_area_acres"]-expected_algae)>.005:
        raise Stop("ALGAE_AREA_DOES_NOT_MATCH_HISTORICAL_VERIFIED_RELEASE")
    # Independent primary source matrix reproduces same-class bare values:
    primary=json.loads((ROOT/"results/charlotte_public_gis_transition_verified_20261119.json").read_text(encoding="utf-8"))["result"]["source_area_to_target_class"]
    old_algae=primary["9121"]["target_area_acres"]["9121"]
    old_sea=sum(primary[str(s)]["target_area_acres"][str(t)] for s in (9113,9116) for t in (9113,9116))
    if abs(out["classes"]["attached_macroalgae"]["boundary_interior_m"]["0"]["same_class_overlap_acres"]-old_algae)>.004:
        raise Stop("ALGAE_SAME_CLASS_MATRIX_REPRODUCTION_FAIL")
    if abs(out["classes"]["seagrass"]["boundary_interior_m"]["0"]["same_class_overlap_acres"]-old_sea)>.004:
        raise Stop("SEAGRASS_SAME_CLASS_MATRIX_REPRODUCTION_FAIL")
    return {
      "schema":"tampa.charlotte_same_mapped_class_area_retention_v1",
      "status":"SUCCESS_ARCHIVED_SOURCE_DESCRIPTIVE_CLASS_STABILITY_ONLY",
      "source":{"archive_run_id":A.ARCHIVE_RUN_ID,"archive_artifact_id":A.ARCHIVE_ID,
                "archive_sha256":A.ARCHIVE_ZIP_DIGEST,
                "original_2022_sha256":old["modern_source"]["2022"]["raw_geojson_canonical_sha256"],
                "original_2024_sha256":old["modern_source"]["2024"]["raw_geojson_canonical_sha256"]},
      "qcs":qc,
      "results":out,
      "evidence_limits":["Mapped classes, not individual plants or lifespans",
                         "2024 missing class means unrecorded, not verified bare bottom",
                         "No control for mapping effort/season, water clarity, photo interpretation, or hydrodynamics",
                         "Fragmented polygons are spatially dependent, not independent samples",
                         "This is outcome-exposed descriptive within Charlotte; not transportability or causal proof"]}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive-root",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    try:report=run(a.archive_root);rc=0
    except (A.Stop,Stop,ValueError,TypeError,KeyError,FileNotFoundError) as e:
        report={"schema":"tampa.charlotte_same_mapped_class_area_retention_v1",
                "status":"STOP_ARCHIVED_SOURCE_OR_GEOMETRY_GATE",
                "reason":str(e),"ecological_conclusion_supported":False}
        rc=2
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))
    return rc
if __name__=="__main__":sys.exit(main())
