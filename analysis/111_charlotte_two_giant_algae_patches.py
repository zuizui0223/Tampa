#!/usr/bin/env python3
"""Audit the two >=50-acre mapped algae source polygons driving class persistence.

Source: SHA256-locked prior successful SWFWMD 2016, 2022, 2024 GeoJSON
archive, NOT the intermittently unavailable live legacy source service.

Per-2022 algae polygon, compute independent original area, 2016 map-positive
seagrass overlap and 2024 mapped sea/algae/unmapped area (EPSG:6933).
An "unmapped" area is not biological death; "algae->sea" map class is not
proof of actual return or that an algae removal action restores seagrass.
"""
from __future__ import annotations
import argparse,importlib.util,json,math,sys
from pathlib import Path
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("class106",ROOT/"analysis/106_charlotte_archived_map_class_retention.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
G=M.G
REF=M.A
AC=G.M2_PER_ACRE
EXPECTED_SOURCE_ALGAE_POLYGONS=95
EXPECTED_LARGE_COUNT=2
LARGE_ACRES=50

class Stop(ValueError):pass

def summarize_patches(patches):
    if not patches:raise Stop("EMPTY_PATCH_SET")
    a=sum(x["source_algae_acres"] for x in patches)
    if a<=0:raise Stop("EMPTY_PATCH_AREA")
    same=sum(x["2024_same_attached_algae_acres"] for x in patches)
    sea=sum(x["2024_mapped_seagrass_acres"] for x in patches)
    unmapped=sum(x["2024_unmapped_area_acres"] for x in patches)
    historic=sum(x["2016_mapped_seagrass_positive_overlap_acres"] for x in patches)
    if abs((same+sea+unmapped)-a)>max(.01,.0001*a):
        raise Stop("PATCH_SUMMARY_AREA_NOT_CLOSED")
    if historic<0 or historic>a+.01:
        raise Stop("HISTORIC_OVERLAP_OUTSIDE_PATCH_SET")
    return {
       "source_algae_acres":round(a,3),
       "mapped_class_remains_algae_acres":round(same,3),
       "mapped_class_becomes_seagrass_acres":round(sea,3),
       "mapped_class_unmapped_acres":round(unmapped,3),
       "historical_2016_seagrass_positive_acres":round(historic,3),
       "2024_same_algae_percent_of_source_area":round(100*same/a,3)
    }

def audit(archive_root):
    old=REF.load_frozen_report()
    src,tgt,qc=M.get_locked_geometries(archive_root,old)
    positive16,_=REF.load_source_features(archive_root,"2016",
                   old["historical_source"]["source_raw_features_sha256"],1382)
    his,qc16=G.prepare(positive16,"ACRES")
    hist=unary_union([his[9113],his[9116]])
    sea24=unary_union([tgt[9113],tgt[9116]])
    algae24=tgt[9121]
    target_union24=unary_union([sea24,algae24])
    f22,_=REF.load_source_features(archive_root,"2022",
                   old["modern_source"]["2022"]["raw_geojson_canonical_sha256"],2303)
    patches=[]
    for f in f22:
        if f["properties"].get("FLUCCSCODE")!=9121:continue
        props=f["properties"];fid=props["FID"]
        rawgeom=G.shape(f["geometry"])
        if not rawgeom.is_valid:
            rawgeom=G.unary_union(G.polygon_parts(G.make_valid(rawgeom)))
        geom=G.transform(G.TRANSFORM,rawgeom)
        if not geom.is_valid or geom.area<=0:
            raise Stop("UNVERIFIED_ALGAE_SOURCE_GEOMETRY:"+str(fid))
        acres=geom.area/AC
        official=props.get("Geodesic")
        if not isinstance(official,(int,float)) or abs(official-acres)>max(0.005,0.002*official):
            raise Stop("OFFICIAL_SOURCE_ACRE_DISAGREES_WITH_ALGAE_FEATURE:"+str(fid))
        covered=geom.intersection(hist).area/AC
        a=geom.intersection(algae24).area/AC
        s=geom.intersection(sea24).area/AC
        unmapped=max(0.,acres-geom.intersection(target_union24).area/AC)
        if abs(a+s+unmapped-acres)>max(.0001,.001*acres):
            raise Stop("PER_PATCH_2024_CLASS_AREA_NONCLOSURE:"+str(fid))
        point=geom.representative_point()
        patches.append({
          "source_2022_FID":fid,
          "source_algae_acres":round(acres,6),
          "2016_mapped_seagrass_positive_overlap_acres":round(covered,6),
          "2024_same_attached_algae_acres":round(a,6),
          "2024_mapped_seagrass_acres":round(s,6),
          "2024_unmapped_area_acres":round(unmapped,6),
          "2024_same_algae_percent":round(100*a/acres,5),
          "2024_mapped_seagrass_percent":round(100*s/acres,5),
          "2016_history_positive_percent":round(100*covered/acres,5),
          "approximate_2022_representative_x_equal_area_m":round(point.x,1),
          "approximate_2022_representative_y_equal_area_m":round(point.y,1),
          "not_a_field_site_or_plant_individual":True,
        })
    if len(patches)!=EXPECTED_SOURCE_ALGAE_POLYGONS or len(set(p["source_2022_FID"] for p in patches))!=len(patches):
        raise Stop("ALGAE_SOURCE_IDENTITY_OR_FEATURE_COUNT_DRIFT")
    patches.sort(key=lambda x:(-x["source_algae_acres"],x["source_2022_FID"]))
    two=patches[:2];other=patches[2:]
    if not all(p["source_algae_acres"]>=LARGE_ACRES for p in two) or any(p["source_algae_acres"]>=LARGE_ACRES for p in other):
        raise Stop("FROZEN_TWO_LARGE_ALGAE_FEATURE_STRUCTURE_CHANGED")
    total=sum(x["source_algae_acres"] for x in patches)
    same=sum(x["2024_same_attached_algae_acres"] for x in patches)
    sea=sum(x["2024_mapped_seagrass_acres"] for x in patches)
    historic=sum(x["2016_mapped_seagrass_positive_overlap_acres"] for x in patches)
    stable=json.loads((ROOT/"results/charlotte_map_class_retention_source_verified_20261119.json").read_text(encoding="utf-8"))["report"]["results"]["classes"]["attached_macroalgae"]
    if (abs(total-674.188)>.01 or abs(same-245.158)>.01 or
        abs(sea-83.433)>.01 or abs(historic-626.854)>.01 or
        abs(stable["boundary_interior_m"]["0"]["same_class_overlap_acres"]-same)>.01):
        raise Stop("PER_PATCH_AREA_DOES_NOT_REPRODUCE_3DATE_SOURCE_MATRICES")
    large=summarize_patches(two);rest=summarize_patches(other)
    return {
       "schema":"tampa.charlotte_two_large_attached_algae_source_patch_audit_v1",
       "status":"ARCHIVED_SOURCE_AREA_VERIFIED_PATCH_DECOMPOSITION_NOT_BIOLOGICAL_TURNOVER",
       "source_archive":{
          "run_id":REF.ARCHIVE_RUN_ID,"artifact_id":REF.ARCHIVE_ID,
          "archive_zip_sha256":REF.ARCHIVE_ZIP_DIGEST,
          "source_2016_features_sha256":old["historical_source"]["source_raw_features_sha256"],
          "source_2022_features_sha256":old["modern_source"]["2022"]["raw_geojson_canonical_sha256"],
          "source_2024_features_sha256":old["modern_source"]["2024"]["raw_geojson_canonical_sha256"]
       },
       "two_largest_source_algae_patches":two,
       "two_largest_summary":large,
       "two_largest_pct_of_all_2022_algae_area":round(100*large["source_algae_acres"]/total,3),
       "remaining_93_patches_summary":rest,
       "all_95_patch_level_source_compositions":patches,
       "quality_control":{"2016":qc16,"2022":qc["2022"],"2024":qc["2024"]},
       "disallowed_inference":["2024 unmapped is bare/dead seagrass",
             "This identifies organismal longevity, causal algal suppression, or recovery",
             "Each of 95 mapped polygons is an independent biological replicate",
             "Land management or field access is authorized by candidate geometry"],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    try:result=audit(args.archive_root);rc=0
    except (Stop,REF.Stop,ValueError,KeyError,TypeError) as e:
        result={"schema":"tampa.charlotte_two_large_attached_algae_source_patch_audit_v1",
                "status":"STOP_SOURCE_IDENTITY_OR_AREA_GATE","reason":str(e),
                "biological_recovery_confirmed":False}
        rc=2
    d=Path(args.out);d.parent.mkdir(parents=True,exist_ok=True)
    d.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return rc

if __name__=="__main__":
    sys.exit(main())
