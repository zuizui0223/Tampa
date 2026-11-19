#!/usr/bin/env python3
"""Far-interior 2024 unmapped source-area audit in 2 giant 2022 algae polygons.

Original authoritative 2016, 2022 and 2024 GeoJSON comes from sealed, checked
GitHub Actions archive (2026-11-19). No live ArcGIS and no unverifiable
photo-interpreter claims. We compute 2024 3-class-unmapped geometry INSIDE
source FIDs 37 and 2166, then require 5/10/25/50/100 metres distance from
BOTH original 2022 patch edge and 2024 three-class mapped footprint.

A far-interior 2024 'unmapped' polygon is still **NOT** true bare sediment,
algal death or sampling coverage. It may reflect missing classes, image
acquisition, detection or classification; only full original classes and
surveyed footprint/field observations distinguish those possibilities.
"""
from __future__ import annotations
import argparse,importlib.util,json,math,sys,hashlib
from pathlib import Path
from shapely.ops import unary_union,transform
from shapely.geometry import shape,mapping
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("two_giants111",ROOT/"analysis/111_charlotte_two_giant_algae_patches.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
G=M.G
AC=G.M2_PER_ACRE
REVERSE=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True).transform
FIDS=(37,2166)
THRESHOLDS=(0.,5.,10.,25.,50.,100.)
MAX_DIST=100
SOURCE_RELEASE=ROOT/"results/charlotte_giant_algae_patches_source_verified_20261119.json"
MMU_AC=.25
MAX_CORES=3000
SCHEMA="tampa.charlotte_giant_algae_unmapped_boundary_distance_v1"
class Stop(ValueError):pass

def load_sources(archive):
    summary=json.loads(SOURCE_RELEASE.read_text(encoding="utf8"))
    if summary.get("schema")!="tampa.charlotte_giant_algae_patches_source_verified_v1":
        raise Stop("ORIGINAL_GIANT_REPORT_NOT_SOURCE_VERIFIED")
    run=summary.get("verified_ci",{})
    if run.get("run_id")!=44464484860 or run.get("second_independent_execution",{}).get("numeric_output_identical_to_first_successful_execution") is not True:
        raise Stop("SOURCE_GIANT_REPORT_PROVENANCE_NOT_LOCKED")
    old=M.REF.load_frozen_report()
    source,target,qc=M.M.get_locked_geometries(archive,old)
    f22,_=M.REF.load_source_features(archive,"2022",
                    old["modern_source"]["2022"]["raw_geojson_canonical_sha256"],2303)
    f16,_=M.REF.load_source_features(archive,"2016",
                    old["historical_source"]["source_raw_features_sha256"],1382)
    oldmap,qc16=G.prepare(f16,"ACRES")
    history=unary_union([oldmap[9113],oldmap[9116]])
    t2024=unary_union([target[9113],target[9116],target[9121]])
    giant={}
    for f in f22:
        p=f.get("properties",{})
        fid=p.get("FID")
        if fid not in FIDS:continue
        if p.get("FLUCCSCODE")!=9121:raise Stop("GIANT_2022_SOURCE_NOT_ALGAE")
        geom=shape(f["geometry"])
        if not geom.is_valid:
            geom=unary_union(G.polygon_parts(G.make_valid(geom)))
        geom=transform(G.TRANSFORM,geom)
        acreage=geom.area/AC
        if abs(acreage-p["Geodesic"])>max(.005,.002*p["Geodesic"]):
            raise Stop("GIANT_2022_OFFICIAL_SOURCE_AREA_INVALID")
        giant[fid]=geom
    if set(giant)!=set(FIDS):
        raise Stop("TWO_GIANT_2022_IDS_NOT_EXACT")
    return giant,t2024,history,summary,old,qc,qc16

def area(x):return x.area/AC

def classified_distance(g,threeclasses,history, distances=THRESHOLDS):
    if tuple(distances)!=THRESHOLDS:
        raise Stop("DISTANCES_CHANGED_AFTER_SOURCE_OUTCOME")
    if not g.is_valid or not threeclasses.is_valid or not history.is_valid:
        raise Stop("GEOMETRY_INVALID")
    U=g.difference(threeclasses)
    if U.is_empty or U.area<=0: raise Stop("UNMAPPED_AREA_MISSING")
    # Limit far-side tests to 100m from the original class boundary.
    # This local clipping minimizes expensive buffer work without
    # excluding any 2024 class within 100m of a point inside g.
    near=threeclasses.intersection(g.buffer(MAX_DIST+1))
    oldac=area(U)
    hisac=area(U.intersection(history))
    result={}
    last=oldac+1
    for d in distances:
        if d<0:raise Stop("NEGATIVE_DISTANCE")
        if d:
            # strictly within source 2022 algae polygon AND >d from any
            # 2024 3-class polygon. This avoids calling narrow edge slivers
            # core disappeared habitat.
            core=g.buffer(-d).difference(near.buffer(d))
        else:
            core=U
        # Compute stable polygon pieces; empty or tiny shapes kept in totals,
        # but only >=0.25 acre pieces exported as field verification candidates.
        if not core.is_valid:raise Stop("INVALID_UNMAPPED_CORE")
        ca=area(core)
        if ca>last+.006:raise Stop("FAR_INTERIOR_AREA_INCREASES_WITH_DIST")
        if ca>oldac+.006:raise Stop("FAR_INTERIOR_EXCEEDS_UNMAPPED")
        histarea=area(core.intersection(history))
        if histarea>ca+.006:raise Stop("HISTORICAL_INTERSECTION_EXCEEDS_CORE")
        result[str(int(d))]={
          "unmapped_area_both_boundaries_interior_acres":round(ca,3),
          "unmapped_area_fraction_of_original_unmapped_percent":round(100*ca/oldac,3),
          "minimum_2016_seagrass_positive_overlap_acres_exact_geometry":round(histarea,3),
          "fraction_interior_also_2016_seagrass_positive_percent":round(100*histarea/ca,3) if ca>0 else None
        }
        last=ca
    return U,result

def build_candidates(giant,unions,history,pinned):
    report={};features=[]
    for fid in FIDS:
        g=giant[fid]
        # high-accuracy original map category overlaps were already audited;
        # check new 3-class union results against these pinned numbers.
        U,res=classified_distance(g,unions,history)
        expected=next(v for v in pinned["report"]["two_largest_source_algae_patches"] if v["source_2022_FID"]==fid)
        if abs(area(U)-expected["2024_unmapped_area_acres"])>.005:
            raise Stop("UNMAPPED_FID_AREA_NOT_REPRODUCED:"+str(fid))
        if abs(area(g)-expected["source_algae_acres"])>.005:
            raise Stop("SOURCE_FID_GIANT_AREA_DRIFT:"+str(fid))
        report[str(fid)]={
            "source_2022_giant_algae_acres":round(area(g),3),
            "2024_absent_from_three_class_map_acres":round(area(U),3),
            "2016_mapped_seagrass_positive_overlap_with_2024_unmapped_acres":round(area(U.intersection(history)),3),
            "fixed_distance_threshold_m":res,
            "not_field_absence_or_substrate_measure":True
        }
        near=unions.intersection(g.buffer(MAX_DIST+1))
        for d in (25.,50.,100.):
            core=g.buffer(-d).difference(near.buffer(d))
            pieces=G.polygon_parts(core)
            for poly in pieces:
                acres=area(poly)
                if acres<MMU_AC:continue
                rep=poly.representative_point()
                lon,lat=REVERSE(rep.x,rep.y)
                if not(-83.5<lon<-81 and 25<lat<28):
                    raise Stop("CORE_COORDS_OUTSIDE_CHARLOTTE")
                features.append({
                  "type":"Feature",
                  "properties":{
                    "source_2022_algae_FID":fid,
                    "distance_inside_2022_source_and_away_from_2024_mapped_classes_m":d,
                    "candidate_core_area_acres":round(acres,5),
                    "historic_2016_seagrass_positive_area_acres":round(area(poly.intersection(history)),5),
                    "candidate_lon":round(lon,7),"candidate_lat":round(lat,7),
                    "2024_true_habitat_class":"UNKNOWN_NOT_IN_9113_9116_9121",
                    "independent_field_survey_conducted":False,
                    "site_access_or_restoration_authorized":False
                  },
                  "geometry":mapping(transform(REVERSE,poly))
                })
                if len(features)>MAX_CORES:raise Stop("CANDIDATE_CORE_GEOMETRY_OVERFLOW")
    combined={}
    for d in THRESHOLDS:
        key=str(int(d))
        vals=[report[str(fid)]["fixed_distance_threshold_m"][key] for fid in FIDS]
        combined[key]={
          "combined_far_unmapped_acres":round(sum(v["unmapped_area_both_boundaries_interior_acres"] for v in vals),3),
          "combined_far_unmapped_also_2016_sea_positive_acres":round(sum(v["minimum_2016_seagrass_positive_overlap_acres_exact_geometry"] for v in vals),3)
        }
    total=sum(report[str(fid)]["2024_absent_from_three_class_map_acres"] for fid in FIDS)
    if abs(total-222.092455)>.01:
        raise Stop("PINNED_TWO_GIANT_TOTAL_UNMAPPED_DRIFT")
    return {
      "schema":SCHEMA,
      "status":"SOURCE_PINNED_THREE_CLASS_UNMAPPED_INTERIOR_GEOMETRY_ONLY",
      "source_years":[2016,2022,2024],
      "original_unmapped_2024_area_acres":round(total,3),
      "two_giant_fid_rows":report,
      "combined_boundary_sensitivity":combined,
      "mapped_core_min_area_acres":MMU_AC,
      "geojson_candidate_feature_count":len(features),
      "classification_scope":"2024 absent from codes 9113/9116/9121 only",
      "no_full_habitat_source_or_footprint_acquired":True,
      "not_plant_mortality_or_algal_disappearance":True,
      "not_true_bare_bottom":True,
      "not_independent_biological_detection":True,
      "not_authorized_field_site":True
    },{"type":"FeatureCollection","features":features}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--geojson-out",required=True)
    a=p.parse_args()
    try:
        original,all2024,hist,giantreport,frozen,qcs,qc16=load_sources(a.archive_root)
        r,geojson=build_candidates(original,all2024,hist,giantreport)
        r["source_qc"]={"2016":qc16,"2022":qcs["2022"],"2024":qcs["2024"]}
        r["source_original_sha256"]={
          "2016":frozen["historical_source"]["source_raw_features_sha256"],
          "2022":frozen["modern_source"]["2022"]["raw_geojson_canonical_sha256"],
          "2024":frozen["modern_source"]["2024"]["raw_geojson_canonical_sha256"]
        }
        rc=0
    except (Stop,M.Stop,M.REF.Stop,G.GateStop,ValueError,TypeError,KeyError,FileNotFoundError) as e:
        r={"schema":SCHEMA,"status":"STOP_ORIGINAL_SOURCE_OR_GEOMETRY_QC","reason":str(e),
            "biological_benthic_response_identified":False}
        geojson={"type":"FeatureCollection","features":[]}
        rc=2
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf8")
    g=Path(a.geojson_out);g.parent.mkdir(parents=True,exist_ok=True)
    g.write_text(json.dumps(geojson,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    print(json.dumps(r,indent=2,sort_keys=True))
    return rc

if __name__=="__main__":sys.exit(main())
