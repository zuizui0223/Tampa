#!/usr/bin/env python3
"""Replay the matched 2016-map-positive reference from a PINNED successful GIS archive.

No live ArcGIS request or new selection criteria. The aim is to challenge the
"92.979% of 2022 algae overlaps 2016 mapped seagrass" interpretation by asking
how much of *contemporaneous 2022 mapped seagrass* also overlaps the historical
mapped-seagrass mask, with exactly the same 2016 source footprint and CRS.

Counts and features are SHA-checked against previously successful, source-area
verified PR #164 artifacts and the existing committed outcome release.
This is post-hoc descriptive area context, not a hypothesis-blind test,
a spatial-independent p-value, evidence of algal competition, or a recovery rate.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("hist100",ROOT/"analysis/100_charlotte_2016_2022_2024_positive_only_overlay.py")
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

ARCHIVE_RUN_ID=44446913647
ARCHIVE_ID=14494425181
ARCHIVE_ZIP_DIGEST="sha256:fb22443b6d0b8bf1a86cf82670342adf18c6d76971074b65f7cbafbfe9db1bea"
PINNED_REPORT=ROOT/"results/charlotte_historical_positive_three_date_verified_20261119.json"
SOURCES={
  "2016":"charlotte_2016_positive_only_or_full.geojson",
  "2022":"charlotte_2022_positive_only_or_full.geojson",
}
METRIC="historic_positive_source_coverage_reference"

class Stop(RuntimeError):pass

def load_frozen_report(path=PINNED_REPORT):
    item=json.loads(Path(path).read_text(encoding="utf-8"))
    if item.get("schema")!="tampa.charlotte_three_date_positive_only_source_release_v1":
        raise Stop("UNVERIFIED_HISTORICAL_REFERENCE_REPORT")
    ci=item.get("verified_ci",{})
    if ci.get("run_id")!=44446322239 or ci.get("artifact_zip_sha256")!="sha256:954dc9c18859f4ffe0879530ef8e9e32a71225b25086b002670c2b0666a46e56":
        raise Stop("HISTORICAL_SOURCE_RELEASE_IDENTITY_MISMATCH")
    data=item["report"]
    if data.get("evidence")!="OUTCOME_CONTEXT_EXPOSED_DESCRIPTIVE_2016_POSITIVE_ONLY_GEOMETRY":
        raise Stop("INCORRECT_EVIDENCE_CLASS")
    if data.get("historical_source",{}).get("exact_source_ids")!=1382 or data.get("modern_source",{}).get("2022",{}).get("oid_count")!=2303:
        raise Stop("PREVIOUS_FIXED_SOURCE_UNIVERSE_MISMATCH")
    return data

def _one_archive_file(root, name):
    matches=list(Path(root).rglob(name))
    if len(matches)!=1 or not matches[0].is_file():raise Stop(f"ARCHIVE_FILE_NOT_UNIQUE:{name}:{len(matches)}")
    if matches[0].stat().st_size>50_000_000: raise Stop("ARCHIVE_SOURCE_FILE_OVERSIZE")
    return matches[0]

def load_source_features(archive_root,year,expected_sha,expected_count):
    p=_one_archive_file(archive_root,SOURCES[year])
    item=json.loads(p.read_text(encoding="utf-8"))
    if item.get("type")!="FeatureCollection" or not isinstance(item.get("features"),list):
        raise Stop("SOURCE_ARCHIVE_NOT_GEOJSON_FEATURE_COLLECTION")
    features=item["features"]
    if len(features)!=expected_count:raise Stop("ARCHIVED_FEATURE_COUNT_DRIFT:"+year)
    if M.M.sha(features)!=expected_sha:raise Stop("ARCHIVED_RAW_FEATURE_SHA_DRIFT:"+year)
    codefield="FLUCCSCODE"
    got=[f.get("properties",{}).get(codefield) for f in features]
    if year=="2016" and sorted(set(got))!=[9113,9116]:
        raise Stop("2016_FROZEN_POSITIVE_CODES_DRIFT")
    if year=="2022" and sorted(set(got))!=[9113,9116,9121]:
        raise Stop("2022_FROZEN_CODE_SET_DRIFT")
    return features,p

def replay(archive_root,release):
    h=release["historical_source"];cur=release["modern_source"]["2022"]
    f16,p16=load_source_features(archive_root,"2016",h["source_raw_features_sha256"],1382)
    f22,p22=load_source_features(archive_root,"2022",cur["raw_geojson_canonical_sha256"],2303)
    g16,q16=M.M.prepare(f16,"ACRES")
    g22,q22=M.M.prepare(f22,"Geodesic")
    for y,q,expected in (
        ("2016",q16,release["area_qc"]["2016"]),
        ("2022",q22,release["area_qc"]["2022"])):
        if not q["all_polygons_checked_against_original_area_field"]:
            raise Stop("OFFICIAL_SOURCE_AREA_NOT_VALIDATED:"+y)
        for cls in ("9113","9116","9121"):
            if abs(q["class_area_acres"][cls]-expected["class_area_acres"][cls])>.003:
                raise Stop("OFFICIAL_CLASS_ACRE_SUM_CHANGED:"+y+":"+cls)
    pos16=unary_union([g16[9113],g16[9116]])
    new=M.historic_positive_coverage_reference(pos16,g22)
    if abs(new["class_specific"]["9121"]["overlaps_2016_mapped_seagrass_acres"]-
           release["map_history"]["2016_seagrass_positive_within_2022_algae_acres"])>.005:
        raise Stop("NEW_REFERENCE_DOES_NOT_REPRODUCE_ORIGINAL_ALGAE_OVERLAP")
    if abs(new["class_specific"]["9121"]["overlaps_2016_mapped_seagrass_percent"]-
           release["map_history"]["2016_seagrass_positive_share_of_2022_algae_percent"])>.003:
        raise Stop("NEW_REFERENCE_RATE_DOES_NOT_REPRODUCE_ORIGINAL")
    return {
      "schema":"tampa.charlotte_historical_overlap_reference_v1",
      "status":"SOURCE_ARCHIVED_VERIFIED_POSTHOC_DESCRIPTIVE_REFERENCE_ONLY",
      "original_successful_feature_archive":{
        "run_id":ARCHIVE_RUN_ID,"artifact_id":ARCHIVE_ID,
        "artifact_zip_sha256":ARCHIVE_ZIP_DIGEST},
      "source_ids":{
        "2016":{"n_features":1382,"source_features_sha256":h["source_raw_features_sha256"],"original_revalidated_area_fields":True},
        "2022":{"n_features":2303,"source_features_sha256":cur["raw_geojson_canonical_sha256"],"original_revalidated_area_fields":True}},
      "reference":new,
      "falsification_interpretation":{
        "test":"Is historical seagrass-positive coverage of 2022 attached algae unusually high compared with 2022 mapped seagrass under the identical 2016 positive map?",
        "pre_specified_logic":"If contemporaneous mapped seagrass has similar or higher 2016 overlap, 92.979% alone cannot support a special historical seagrass-to-algae conversion preference.",
        "result_not_blind":True,"independent_estuaries":0,"spatially_independent_statistical_test":False,
        "no_source_2016_demographic_absence":True,"no_proven_algal_inhibition":True,
        "no_intervention_or_recovery_claim":True},
      "geometry_archive_input_names":{k:v for k,v in SOURCES.items()},
      "interpretation":"Descriptive geometric context only: denominator is each 2022 mapped class and background unmapped habitat is NOT observed bare ground. Comparisons may reflect the extent of historical vegetation/mapping rather than biological specialization."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    try:
        frozen=load_frozen_report()
        out=replay(args.archive_root,frozen);rc=0
    except (Stop,ValueError,TypeError,KeyError,FileNotFoundError) as e:
        out={"schema":"tampa.charlotte_historical_overlap_reference_v1",
             "status":"STOP_ARCHIVED_SOURCE_OR_GEOMETRY_QC","reason":str(e),
             "reference_computed":False};rc=2
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False))
    return rc
if __name__=="__main__":sys.exit(main())
