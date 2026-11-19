#!/usr/bin/env python3
"""Full-area, shape-level audit: what are CHNEP 'Seagrass Gain/Loss' polygons?

Compare exact official agency change-map polygons (classes 9113,9116,9121)
with independently derived same-source set-difference masks for all classes:

  map_gain[c] = 2024-class-c polygons OUTSIDE ALL 2022 mapped classes.
  map_loss[c] = 2022-class-c polygons OUTSIDE ALL 2024 mapped classes.

This does NOT count 2022 attached algae -> 2024 seagrass as map *gain*
when there was mapped algae in 2022. Likewise no loss for such reclassification.

Primary 2022/2024 source GeoJSON is pinned by artifact SHA and independently
validated original source acres. 2022/24 agency gain/loss polygons are
independently source-area-validated with exact official OID, metadata and raw
geometry SHA, matching previously successful run #44478539061.

No independent biology, photo interpretation accuracy, ecological treatment,
plant mortality, colonization, or restored habitat is observed here.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys
from pathlib import Path
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "map114",ROOT/"analysis/114_charlotte_official_gain_loss_map_concordance.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
G=M.G
SOURCE_RELEASE=ROOT/"results/charlotte_official_change_map_giant_source_concordance_verified_20261119.json"
SCHEMA="tampa.charlotte_agency_change_set_difference_source_qc_v1"
CODES=(9113,9116,9121)
ROLES={
  "mapped_seagrass_gain":"gain",
  "mapped_seagrass_loss":"loss"
}
AC=G.M2_PER_ACRE
class Stop(ValueError):pass

def frozen_existing_source():
    r=json.loads(SOURCE_RELEASE.read_text(encoding="utf-8"))
    if r.get("schema")!="tampa.charlotte_original_source_versus_agency_change_layer_verified_release_v1":
        raise Stop("UNVERIFIED_ORIGINAL_AGENCY_CHANGE_SOURCE")
    a=r.get("verified_ci",{})
    if (a.get("run_id")!=44478539061 or
        a.get("artifact_zip_sha256")!="sha256:04a922966245301b375a958a0f5113037b2443150d23e6946995d368bacb3d76"):
        raise Stop("PREVIOUS_AGENCY_SOURCE_HASH_OR_RUN_MISMATCH")
    return r["report"]["official_gain_loss_sources"]

def change_pieces(src,target):
    all22=unary_union([src[c] for c in CODES])
    all24=unary_union([target[c] for c in CODES])
    if all22.is_empty or all24.is_empty:
        raise Stop("EMPTY_ORIGINAL_VEGETATION_CLASS_UNION")
    return {
      "gain":{c:target[c].difference(all22) for c in CODES},
      "loss":{c:src[c].difference(all24) for c in CODES}
    }

def compare_shapes(predicted,agency):
    out={}
    for role in ("gain","loss"):
        data=agency[role]
        class_ref=data["geometries_by_class"]
        cl={}
        for code in CODES:
            a=predicted[role][code]
            b=class_ref[code]
            if not a.is_valid or not b.is_valid:
                raise Stop("INVALID_SOURCE_DIFFERENCE_GEOMETRY:"+role+":"+str(code))
            predicted_area=a.area/AC
            agency_area=b.area/AC
            inter=a.intersection(b).area/AC
            union=a.union(b).area/AC
            omitted=max(0,predicted_area-inter)
            added=max(0,agency_area-inter)
            jaccard=inter/union if union>0 else None
            if inter>min(predicted_area,agency_area)+.001:
                raise Stop("INTERSECTION_EXCEEDS_CLASS_AREA")
            cl[str(code)]={
              "source_map_set_difference_acres":round(predicted_area,5),
              "agency_change_source_acres":round(agency_area,5),
              "source_agency_same_mapped_area_acres":round(inter,5),
              "source_map_not_in_agency_change_acres":round(omitted,5),
              "agency_change_not_in_source_map_acres":round(added,5),
              "source_agency_jaccard":round(jaccard,7) if jaccard is not None else None,
              "geometric_equivalence_within_0_02_acres":(omitted+added)<=.02,
              "no_organismal_gain_or_loss_inference":True
            }
        out[role]=cl
    return out

def audit(archive_root):
    frozen=frozen_existing_source()
    source_gate,_=M.source_docs()
    orig=M.M.REF.load_frozen_report()
    source,target,qc=M.M.M.get_locked_geometries(archive_root,orig)
    agency={}
    for role,short in ROLES.items():
        d=M.get_change(role,source_gate)
        required=frozen[short]
        for field in ("geojson_feature_sha256","oid_roster_sha256"):
            if d[field]!=required[field]:
                raise Stop("CHANGED_OFFICIAL_AGENCY_RAW_GEOMETRY:"+role+":"+field)
        if d["flucss_class_counts"]!=required["flucss_class_counts"]:
            raise Stop("CHANGED_OFFICIAL_MIXED_CLASSES:"+role)
        agency[short]=d
    comparisons=compare_shapes(change_pieces(source,target),agency)
    for role in ("gain","loss"):
        for cls in CODES:
            c=comparisons[role][str(cls)]
            if c["source_map_set_difference_acres"]<0 or c["agency_change_source_acres"]<0:
                raise Stop("NEGATIVE_AREA_CONCORDANCE")
    return {
      "schema":SCHEMA,
      "status":"VERIFIED_COMPLETE_SOURCE_SHAPE_DIFFERENCE_CONCORDANCE_OR_DISCORDANCE_REPORTED",
      "previous_official_source":str(SOURCE_RELEASE.relative_to(ROOT)),
      "source_acre_qc":qc,
      "source_original_2022_2024_sha256":{
        "2022":orig["modern_source"]["2022"]["raw_geojson_canonical_sha256"],
        "2024":orig["modern_source"]["2024"]["raw_geojson_canonical_sha256"]},
      "agency_source_raw_sha256":{
        role:agency[role]["geojson_feature_sha256"] for role in ("gain","loss")},
      "per_class_area_geometry_comparison":comparisons,
      "all_6_class_differences_within_0_02_acre":all(
        comparisons[r][str(c)]["geometric_equivalence_within_0_02_acres"]
        for r in ("gain","loss") for c in CODES),
      "source_years":[2022,2024],
      "not_independent_biological_observation":True,
      "loss_does_not_imply_bare_bottom":True,
      "map_class_swaps_are_not_map_gain_or_map_loss":True,
      "next_gate":"Complete mapped sampling footprint, every FLUCCS background class and/or independent quadrat field data for true 2024 benthic fate."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    try:
        output=audit(args.archive_root);rc=0
    except (Stop,M.Stop,M.M.Stop,M.M.REF.Stop,G.GateStop,ValueError,TypeError,KeyError,FileNotFoundError) as e:
        output={"schema":SCHEMA,"status":"STOP_COMPLETE_AGENCY_SET_DIFFERENCE_QC",
                "reason":str(e),"not_independent_biological_observation":True}
        rc=2
    f=Path(args.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":
    sys.exit(main())
