#!/usr/bin/env python3
"""Source-concordance of official 2022–2024 gain/loss maps at two 2022 algae FIDs.

The CHNEP/SWFWMD 'Seagrass Gain/Loss' GIS source is *derived from the same
aerial seagrass mapping family*. This script checks whether its polygons
agree with an independently coded exact-polygon overlay, NOT whether seagrass
plants recruited, died or algae competed with them.

Input primary class polygons: original SHA256-pinned successful source archive.
Official gain/loss class geometry is fetched via exact OID inventories.
Original area attributes are compared to EPSG:6933 equal-area geometry.
Any source class drift, incomplete fetch or area mismatch is terminal STOP.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, sys
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("large111",ROOT/"analysis/111_charlotte_two_giant_algae_patches.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
G=M.G
AREA=G.M2_PER_ACRE
SRC=ROOT/"results/charlotte_official_gain_loss_source_verified_20261119.json"
GIANT=ROOT/"results/charlotte_giant_algae_patches_source_verified_20261119.json"
ROLES=("mapped_seagrass_gain","mapped_seagrass_loss")
SOURCE_CODES=(9113,9116)
SMALL_BATCH=100

class Stop(ValueError):pass

def source_docs():
    src=json.loads(SRC.read_text(encoding="utf-8"))
    if src.get("schema")!="tampa.charlotte_official_gain_loss_source_verified_release_v1":
        raise Stop("UNVERIFIED_GAIN_LOSS_SOURCE_RELEASE")
    if src.get("verified_run",{}).get("run_id")!=44475344451:
        raise Stop("UNEXPECTED_GAIN_LOSS_SOURCE_RUN")
    p=src["report"]
    if p.get("status")!="PASS_MAP_CHANGE_GIS_SOURCE_METADATA_COUNTS_ONLY":
        raise Stop("INVALID_CHANGE_SOURCE_PREFLIGHT")
    giant=json.loads(GIANT.read_text(encoding="utf-8"))
    if giant.get("status")!="SUCCESS_SOURCE_LOCKED_POSTHOC_MAPPED_PATCH_INFLUENCE_ONLY":
        raise Stop("UNVERIFIED_GIANT_SOURCE_REPORT")
    ids=[p["source_2022_FID"] for p in giant["report"]["two_largest_source_algae_patches"]]
    if ids!=[37,2166]:raise Stop("GIANT_OID_SOURCE_CHANGED")
    return p,giant

def polygon_only(g):
    if g.is_empty:return []
    if g.geom_type=="Polygon":return [g]
    if g.geom_type=="MultiPolygon":return list(g.geoms)
    if g.geom_type=="GeometryCollection":
        r=[]
        for x in g.geoms:r.extend(polygon_only(x))
        return r
    return []

def get_change(role, pinned, fetch=None):
    if fetch is None:fetch=G.query
    prior=pinned["records"][role]
    url=prior["layer_url"]
    meta=fetch(url,{"f":"json"})
    # Use the exact same canonical source metadata rule from the preflight.
    sh=__import__("hashlib").sha256(
        json.dumps(meta,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    if sh!=prior["layer_metadata_sha256"]:
        raise Stop("OFFICIAL_CHANGE_MAP_METADATA_DRIFT:"+role)
    fields={f["name"]:f["type"] for f in meta.get("fields",[])}
    oid=prior["oid_field"]
    area_field="ACRES" if role=="mapped_seagrass_gain" else "Geodesic"
    if (meta.get("geometryType")!="esriGeometryPolygon" or
        fields.get(oid)!="esriFieldTypeOID" or
        fields.get("FLUCCSCODE")!="esriFieldTypeDouble" or
        fields.get(area_field)!="esriFieldTypeDouble"):
        raise Stop("CHANGE_MAP_SCHEMA_OR_AREA_DRIFT:"+role)
    count=fetch(url+"/query",{"f":"json","where":"1=1","returnCountOnly":"true"}).get("count")
    roster=fetch(url+"/query",{"f":"json","where":"1=1","returnIdsOnly":"true"}).get("objectIds")
    if not isinstance(count,int) or count!=prior["official_polygon_count"]:
        raise Stop("CHANGE_MAP_SOURCE_COUNT_DRIFT:"+role)
    if not isinstance(roster,list) or len(roster)!=count or len(set(roster))!=count:
        raise Stop("CHANGE_MAP_FID_ROSTER_MISSING_OR_DUPLICATED:"+role)
    if not all(isinstance(v,int) for v in roster):
        raise Stop("NONINTEGER_ORIGINAL_CHANGE_FID")
    features=[];digests=[]
    for i in range(0,len(roster),SMALL_BATCH):
        chunk=sorted(roster)[i:i+SMALL_BATCH]
        raw=fetch(url+"/query",{
            "objectIds":",".join(str(v) for v in chunk),
            "outFields":",".join((oid,"FLUCCSCODE","FLUCCSDESC",area_field)),
            "returnGeometry":"true","outSR":"4326","f":"geojson"})
        fs=raw.get("features")
        if raw.get("type")!="FeatureCollection" or not isinstance(fs,list):
            raise Stop("BAD_GEOJSON_CHANGE_FEATURE_RESPONSE:"+role)
        actual=[f.get("properties",{}).get(oid) for f in fs]
        if len(fs)!=len(chunk) or len(set(actual))!=len(fs) or set(actual)!=set(chunk):
            raise Stop("UNRECONCILED_CHANGE_MAP_OIDS:"+role)
        features.extend(fs)
        digests.append(G.sha(fs))
    classes={9113:0,9116:0}
    geoms=[]
    max_error=0;repair=0
    for f in features:
        props=f["properties"]
        code=props.get("FLUCCSCODE")
        if code not in SOURCE_CODES:
            raise Stop("CHANGE_MAP_HAS_NON_SEAGRASS_CODE:"+role+":"+str(code))
        official=props.get(area_field)
        if isinstance(official,bool) or not isinstance(official,(int,float)) or not math.isfinite(official) or official<=0:
            raise Stop("CHANGE_MAP_OFFICIAL_ACRES_INVALID")
        sh=shape(f["geometry"])
        if sh.geom_type not in ("Polygon","MultiPolygon") or sh.is_empty:
            raise Stop("CHANGE_MAP_GEOMETRY_INVALID_TYPE")
        b=sh.bounds
        if not(-83.5<b[0]<-81 and -83.5<b[2]<-81 and 25<b[1]<28 and 25<b[3]<28):
            raise Stop("CHANGE_MAP_SOURCE_COORDINATES_OUTSIDE_BAY")
        if not sh.is_valid:
            repair+=1
            sh=G.unary_union(polygon_only(G.make_valid(sh)))
        p=G.transform(G.TRANSFORM,sh)
        if p.is_empty or not p.is_valid or p.area<=0:raise Stop("INVALID_CHANGE_PROJECTED_SHAPE")
        diff=abs(p.area/AREA-official)
        max_error=max(max_error,diff)
        if diff>max(0.005,0.002*official):
            raise Stop("CHANGE_MAP_INDEPENDENT_AREA_MISMATCH:"+role)
        geoms.append(p)
        classes[int(code)]+=1
    merged=unary_union(geoms)
    total=sum(p.area for p in geoms)
    if (total-merged.area)/max(1,merged.area)>.01:
        raise Stop("EXCESSIVE_CHANGE_LAYER_POLYGON_OVERLAP")
    return {
       "url":url,
       "count":count,"oid_roster_sha256":G.sha(sorted(roster)),
       "geojson_feature_sha256":G.sha(sorted(features,key=lambda x:x["properties"][oid])),
       "batch_hashes":digests,"original_area_field":area_field,
       "max_source_area_error_acres":round(max_error,5),
       "n_repaired_features":repair,
       "flucss_seagrass_code_counts":{str(k):v for k,v in classes.items()},
       "mapped_acres":round(merged.area/AREA,3),
       "geometry":merged
    }

def source_giant_shapes(root):
    old=M.REF.load_frozen_report()
    originals,_=M.REF.load_source_features(root,"2022",
        old["modern_source"]["2022"]["raw_geojson_canonical_sha256"],2303)
    selected=[f for f in originals if f.get("properties",{}).get("FID") in (37,2166)]
    if len(selected)!=2 or {f["properties"]["FID"] for f in selected}!={37,2166}:
        raise Stop("GIANT_ORIGINAL_SOURCE_GIS_IDS_MISSING")
    raw={}
    for f in selected:
        props=f["properties"];g=shape(f["geometry"])
        if not g.is_valid:g=G.unary_union(polygon_only(G.make_valid(g)))
        geom=G.transform(G.TRANSFORM,g)
        expected=props["Geodesic"]
        if abs(geom.area/AREA-expected)>max(0.005,.002*expected):
            raise Stop("GIANT_ORIGINAL_ACRE_REVALIDATION_FAILED")
        raw[str(props["FID"])]=geom
    return raw

def compare(giants,gain,loss,pinned_giant):
    out={}
    for fid,geometry in giants.items():
        original=next(f for f in pinned_giant["report"]["two_largest_source_algae_patches"]
                      if str(f["source_2022_FID"])==fid)
        gain_area=geometry.intersection(gain["geometry"]).area/AREA
        loss_area=geometry.intersection(loss["geometry"]).area/AREA
        expected_sea=original["2024_mapped_seagrass_acres"]
        # Never require an overlap to match by convenience. If sources differ,
        # report disagreement as source-map discordance, not a scientific result.
        out[fid]={
            "source_2022_algae_acres":original["source_algae_acres"],
            "2024_our_own_seagrass_overlap_acres":expected_sea,
            "official_gain_map_overlap_acres":round(gain_area,5),
            "official_loss_map_overlap_acres":round(loss_area,5),
            "gain_minus_our_seagrass_overlap_acres":round(gain_area-expected_sea,5),
            "gain_source_concordance_fraction_of_our_reclassified_sea":
                round(min(gain_area,expected_sea)/expected_sea,5) if expected_sea>0 else None,
            "same_original_imagery_not_independent_ecology":True,
        }
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--raw-dir")
    a=p.parse_args()
    try:
        previous,pinned_giant=source_docs()
        giant=source_giant_shapes(a.archive_root)
        gain=get_change("mapped_seagrass_gain",previous)
        loss=get_change("mapped_seagrass_loss",previous)
        comparison=compare(giant,gain,loss,pinned_giant)
        # Add no source geometry to the JSON summary and do not expose
        # FID OIDs as real-world biological study-site identifiers.
        out={
          "schema":"tampa.charlotte_source_gain_loss_map_concordance_v1",
          "status":"SOURCE_VERIFIED_SAME_MAP_FAMILY_CONCORDANCE_ONLY",
          "giant_2022_attached_algae_fid_comparisons":comparison,
          "official_gain_loss_sources":{
            role:{k:v for k,v in data.items() if k!="geometry"}
            for role,data in [("gain",gain),("loss",loss)]},
          "source_2022_fids":[37,2166],
          "original_giant_report_source":"results/charlotte_giant_algae_patches_source_verified_20261119.json",
          "no_survey_footprint_or_extra_benthic_classes_observed":True,
          "not_biological_or_independent_field_validation":True,
          "not_inference_on_2024_unmapped_benthic_state":True,
          "source_role_not_an_independent_replicate":True
        }
        rc=0
    except (Stop,M.Stop,M.REF.Stop,G.GateStop,TypeError,ValueError,KeyError,OSError) as e:
        out={"schema":"tampa.charlotte_source_gain_loss_map_concordance_v1",
             "status":"STOP_OFFICIAL_MAP_CHANGE_SOURCE_OR_AREA",
             "reason":str(e),"not_biological_or_independent_field_validation":True}
        rc=2
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True))
    return rc

if __name__=="__main__":
    sys.exit(main())
