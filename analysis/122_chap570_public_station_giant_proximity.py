#!/usr/bin/env python3
"""Public CHAP (SEACAR Program 570) registered point proximity to mapped unknown habitat.

Registered CHAP station POINTS are neither actual annual 2016/22/24
quadrat responses nor proof that field survey visited the site in 2024.
The study asks only whether existing *registered* station midpoints are near
two 2022 attached-algae giant source polygons and their 2024 three-class
unmapped 25m/50m interior masks.

Polygons are original 2016/22/24 SHA-pinned SWFWMD source files in archived
artifact. Station layer is a separate public SEACAR MapServer, with exact
ProgramID=570 OID roster, source metadata SHA and lat/lon checks.
Distance is in EPSG:32617 (UTM 17N) metres. No user location is queried.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,sys
from pathlib import Path
from shapely.geometry import shape,Point
from shapely.ops import transform
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("ch118",ROOT/"analysis/118_charlotte_giant_unmapped_core_depth.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
G=M.G
PUB=ROOT/"results/charlotte_chap570_public_stations_source_verified_20261119.json"
OLD=ROOT/"results/charlotte_giant_unmapped_interior_source_verified_20261119.json"
SOURCE_MAP="https://gis.waterinstitute.usf.edu/arcgis/rest/services/Maps/SEACAR_Datazoom/MapServer/179"
OID="OBJECTID_1"
PROGRAM=570
EXPECTED_POINTS=63
P2D=Transformer.from_crs("EPSG:6933","EPSG:32617",always_xy=True).transform
WGS2D=Transformer.from_crs("EPSG:4326","EPSG:32617",always_xy=True).transform
RADII=(0,250,500,1000,2000,5000)
SCHEMA="tampa.chap_570_public_station_to_charlotte_giant_map_unknown_proximity_v1"
class Stop(ValueError):pass

def sha(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def release():
    public=json.loads(PUB.read_text(encoding="utf8"))
    if public.get("verified_ci",{}).get("run_id")!=44512764413 or public.get("report",{}).get("status")!="PASS_PUBLIC_CHAP_570_POINT_LAYER_AND_OID_INVENTORY_ONLY":
        raise Stop("UNVERIFIED_PUBLIC_FIELD_STATION_SOURCE")
    p=public["report"]
    if p.get("count_program570_point_features")!=EXPECTED_POINTS or p.get("object_id_field")!=OID or p.get("url")!=SOURCE_MAP:
        raise Stop("REGISTRY_METADATA_SOURCE_DRIFT")
    old=json.loads(OLD.read_text(encoding="utf8"))
    if old.get("verified_ci",{}).get("run_id")!=44509444813:
        raise Stop("UNVERIFIED_GIANT_UNMAPPED_3YEAR_SOURCE")
    return p,old

def download_station_points(preflight,query=None):
    if query is None:query=G.query
    meta=query(SOURCE_MAP,{"f":"json"})
    if sha(meta)!=preflight["layer_metadata_sha256"]:
        raise Stop("CHAP_PUBLIC_POINT_METADATA_SHA_CHANGED")
    idresp=query(SOURCE_MAP+"/query",{"f":"json","where":"ProgramID=570","returnIdsOnly":"true"})
    ids=idresp.get("objectIds")
    if (not isinstance(ids,list) or len(ids)!=EXPECTED_POINTS or
        len(set(ids))!=EXPECTED_POINTS or sha(sorted(ids))!=preflight["point_ids_sha256"]):
        raise Stop("REGISTERED_570_POINT_OID_SET_DRIFT")
    if idresp.get("objectIdFieldName",OID)!=OID:
        raise Stop("PUBLIC_POINT_QUERY_ID_FIELD_CHANGED")
    fs=[]
    for k in range(0,len(ids),100):
        batch=sorted(ids)[k:k+100]
        obj=query(SOURCE_MAP+"/query",{
            "objectIds":",".join(map(str,batch)),
            "outFields":"OBJECTID_1,ProgramID,ProgramLocationID,Latitude_DD,Longitude_DD,Start_Year,End_Year,ManagedAreaName",
            "returnGeometry":"true","outSR":"4326","f":"geojson"})
        chunk=obj.get("features")
        if obj.get("type")!="FeatureCollection" or not isinstance(chunk,list):
            raise Stop("PUBLIC_570_POINT_GEOJSON_NOT_AVAILABLE")
        have=[f.get("properties",{}).get(OID) for f in chunk]
        if len(chunk)!=len(batch) or len(have)!=len(set(have)) or set(have)!=set(batch):
            raise Stop("PUBLIC_570_POINT_BATCH_OIDS_NOT_EXACT")
        fs.extend(chunk)
    if len(fs)!=EXPECTED_POINTS:raise Stop("PUBLIC_570_POINT_RECORDS_INCOMPLETE")
    fs.sort(key=lambda x:x["properties"][OID])
    converted=[]
    mismatch=0;outside=0
    for f in fs:
        props=f["properties"]
        if props.get("ProgramID")!=PROGRAM:
            raise Stop("PUBLIC_POINT_WRONG_MONITORING_PROGRAM")
        geom=shape(f.get("geometry"))
        if geom.geom_type!="Point" or geom.is_empty:
            raise Stop("PUBLIC_STATION_GEOMETRY_NOT_POINT")
        lon,lat=geom.x,geom.y
        if not(-180<=lon<=180 and -90<=lat<=90):
            raise Stop("PUBLIC_STATION_NOT_LONGITUDE_LATITUDE")
        alon,alat=props.get("Longitude_DD"),props.get("Latitude_DD")
        if isinstance(alon,(float,int)) and isinstance(alat,(float,int)):
            if abs(alon-lon)>.01 or abs(alat-lat)>.01:mismatch+=1
        # Program 570 may include coordinates outside the two original
        # giant 2022 patches / Charlotte regional map. Never silently delete.
        if not(-83.5<lon<-81.0 and 25.0<lat<28.0):outside+=1
        x,y=WGS2D(lon,lat)
        converted.append({
          "oid":props[OID],"id":str(props.get("ProgramLocationID") or ""),
          "latitude":round(lat,7),"longitude":round(lon,7),
          "x_utm17n":x,"y_utm17n":y,
          "start_year":str(props.get("Start_Year") or ""),
          "end_year":str(props.get("End_Year") or ""),
          "managed_area":str(props.get("ManagedAreaName") or "")
        })
    return {
      "registry_records":converted,
      "public_geojson_feature_sha256":sha(fs),
      "metadata_attribute_coordinate_mismatches_over_point01deg":mismatch,
      "public_point_locations_outside_charlotte_regional_envelope":outside,
      "source_oids_verified":True
    }

def proximity(points,zones,radii=RADII):
    rows={}
    if not points or any("x_utm17n" not in p or "y_utm17n" not in p for p in points):
        raise Stop("NO_VERIFIED_PUBLIC_STATION_POINTS")
    if len({p["oid"] for p in points})!=len(points):
        raise Stop("DUPLICATE_PUBLIC_STATION_OIDS")
    for name,g in zones.items():
        if g.is_empty or not g.is_valid:raise Stop("MAPPED_UNKNOWN_ZONE_INVALID:"+name)
        dists=[]
        for p in points:
            d=Point(p["x_utm17n"],p["y_utm17n"]).distance(g)
            if not math.isfinite(d):raise Stop("NONFINITE_PUBLIC_STATION_DISTANCE")
            dists.append((d,p))
        dists.sort(key=lambda x:(x[0],x[1]["oid"]))
        rows[name]={
           "site_registry_points_total":len(points),
           "zone_area_utm17_square_metres":round(g.area,2),
           "min_distance_to_registered_public_station_metres":round(dists[0][0],2),
           "public_point_counts_within_radius_metres":{
              str(m):sum(d<=m+1e-8 for d,_ in dists) for m in radii
           },
           "nearest_public_station_point_ids":[
              {"public_registry_oid":p["oid"],"public_program_location_id":p["id"],
               "distance_metres":round(d,2),
               "station_point_not_a_verifed_2024_survey":True}
              for d,p in dists[:5]],
           "no_annual_field_visit_or_quadrat_measurement_retrieved":True,
        }
    return rows

def compute(archive):
    pinned,old=release()
    public=download_station_points(pinned)
    giants,target,history,summary,frozen,qc,q16=M.load_sources(archive)
    zones={}
    for fid in M.FIDS:
        g=giants[fid]
        unmapped=g.difference(target)
        if abs(unmapped.area/M.AC-summary["report"]["two_largest_source_algae_patches"][0 if fid==37 else 1]["2024_unmapped_area_acres"])>.005:
            raise Stop("SOURCE_FID_UNMAPPED_AREA_CHANGED")
        near=target.intersection(g.buffer(101))
        for d in (0,25,50):
            core=unmapped if d==0 else g.buffer(-d).difference(near.buffer(d))
            zones[f"FID{fid}_unknown_{d}m"]=transform(P2D,core)
    r=proximity(public["registry_records"],zones)
    return {
      "schema":SCHEMA,
      "status":"PUBLIC_REGISTRY_TO_SOURCE_PINNED_GIS_PROXIMITY_ONLY_NOT_BIOLOGICAL_VALIDATION",
      "n_public_program570_registry_points":len(public["registry_records"]),
      "public_source_registry_sha256":pinned["point_ids_sha256"],
      "public_station_point_geojson_sha256":public["public_geojson_feature_sha256"],
      "coordinate_discrepancies":public["metadata_attribute_coordinate_mismatches_over_point01deg"],
      "regional_outlier_public_point_count":public["public_point_locations_outside_charlotte_regional_envelope"],
      "spatial_distances_source":"EPSG:32617, original SWFWMD 2022/2024 mapped class masks",
      "zones":r,
      "registry_station_ids_not_actual_annual_quadrat_locations":True,
      "does_not_establish_no_historical_field_surveys_near_patches":True,
      "no_field_cover_shoot_density_or_algae_abundance_read":True,
      "no_true_2024_benthic_absence_concluded":True,
      "scientific_scope":"Registered CHAP sites (transect midpoints) are not a crosswalk to actual year-specific quadrat measurements; nearest registry site proximity alone cannot validate source mapping or infer biological recovery."
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive-root",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    try:r=compute(args.archive_root);code=0
    except (Stop,M.Stop,G.GateStop,M.M.REF.Stop,TypeError,KeyError,ValueError,FileNotFoundError) as e:
        r={"schema":SCHEMA,"status":"STOP_REGISTRY_OR_SOURCE_GIS_INTEGRITY","reason":str(e),
           "field_biology_claim_supported":False};code=2
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True))
    return code

if __name__=="__main__":sys.exit(main())
