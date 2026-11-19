#!/usr/bin/env python3
"""Area-weighted, exploratory 2022->2024 mapped vegetation class transition.

Public SWFWMD Charlotte Harbor 2022/2024 FeatureServer layers only.
This describes *mapped categories*, not mortality, competition, or future
seagrass recovery risk. Read public polygons via auditable exact ID rosters.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

from shapely.geometry import shape, GeometryCollection
from shapely.ops import unary_union,transform
from shapely.validation import make_valid
from pyproj import Transformer

URL_ROOT="https://services2.arcgis.com/7XOSGW3VgfWJK7Ia/ArcGIS/rest/services"
LAYER_URLS={
"2022":URL_ROOT+"/Seagrass_in_2022_in_Charlotte_Harbor/FeatureServer/1",
"2024":URL_ROOT+"/Seagrass_in_2024_in_Charlotte_Harbor/FeatureServer/1",
}
CODES={9113:"patchy_seagrass",9116:"continuous_seagrass",9121:"attached_macroalgae"}
ALLOWED={*CODES}
M2_PER_ACRE=4046.8564224
UA="Ecological source-audited GIS descriptive reaggregation/1.0"
BATCH_SIZE=125
TRANSFORM=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True).transform

class GateStop(Exception):pass

def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                        ensure_ascii=False).encode("utf-8")).hexdigest()

def query(url,params):
    req=Request(url+"?"+urlencode(params),headers={"User-Agent":UA,"Accept":"application/json"})
    try:
        with urlopen(req,timeout=60) as response:
            body=response.read(25_000_001)
    except (OSError,HTTPError,URLError,TimeoutError) as e:
        raise GateStop("ARCGIS_NETWORK:"+type(e).__name__) from e
    if len(body)>25_000_000:
        raise GateStop("OVERSIZE_SERVER_RESPONSE")
    try: o=json.loads(body)
    except (ValueError,UnicodeDecodeError) as e:
        raise GateStop("NOT_JSON") from e
    if not isinstance(o,dict) or "error" in o:
        raise GateStop("ARCGIS_RETURNED_ERROR:"+str(o.get("error",o))[:250])
    return o

def download_year(year,query_fn=query):
    url=LAYER_URLS[year]
    meta=query_fn(url,{"f":"json"})
    names={f.get("name"):f.get("type") for f in meta.get("fields",[])}
    if meta.get("geometryType")!="esriGeometryPolygon" or names.get("FLUCCSCODE")!="esriFieldTypeInteger":
        raise GateStop(year+":METADATA_GEOMETRY_OR_CODE_DRIFT")
    if meta.get("objectIdField")!="FID":
        raise GateStop(year+":OBJECTID_FIELD_DRIFT")
    area_field="Geodesic" if year=="2022" else "ACRES"
    if names.get(area_field)!="esriFieldTypeDouble":
        raise GateStop(year+":SOURCE_ACRE_FIELD_MISSING")
    count=query_fn(url+"/query",{"where":"1=1","returnCountOnly":"true","f":"json"}).get("count")
    ids_resp=query_fn(url+"/query",{"where":"1=1","returnIdsOnly":"true","f":"json"})
    ids=ids_resp.get("objectIds")
    if not isinstance(ids,list) or not isinstance(count,int) or count<1 or len(ids)!=count:
        raise GateStop(year+":ID_INVENTORY_COUNT_MISMATCH")
    if len(set(ids))!=len(ids) or not all(isinstance(v,int) for v in ids):
        raise GateStop(year+":BAD_OBJECTID_LIST")
    ids=sorted(ids)
    features=[]
    batches=[]
    for i in range(0,len(ids),BATCH_SIZE):
        batch=ids[i:i+BATCH_SIZE]
        data=query_fn(url+"/query",{
            "objectIds":",".join(str(x) for x in batch),
            "outFields":"FID,FLUCCSCODE,FLUCCSDESC,"+area_field,
            "returnGeometry":"true",
            "outSR":"4326","f":"geojson"})
        feats=data.get("features")
        if data.get("type")!="FeatureCollection" or not isinstance(feats,list):
            raise GateStop(year+":BAD_GEOJSON_BATCH")
        have={f.get("properties",{}).get("FID") for f in feats}
        if have!=set(batch) or len(feats)!=len(batch):
            raise GateStop(year+":MISSING_OR_DUPLICATED_GEOJSON_FEATURES")
        features.extend(feats)
        batches.append({"first_oid":batch[0],"last_oid":batch[-1],
                        "n":len(feats),"geojson_sha256":sha(feats)})
    if len(features)!=len(ids):
        raise GateStop(year+":INCOMPLETE_GEOMETRY_DOWNLOAD")
    features.sort(key=lambda f:f["properties"]["FID"])
    codes=[f["properties"].get("FLUCCSCODE") for f in features]
    if set(codes)-ALLOWED:
        raise GateStop(year+":UNAPPROVED_CLASS_CODE:"+str(set(codes)-ALLOWED))
    if not any(c==9121 for c in codes):
        raise GateStop(year+":NO_ATTACHED_MACROALGAE_CLASS")
    return {
        "year":year,"url":url,"official_acre_field":area_field,"source_metadata_sha256":sha(meta),
        "oid_count":count,"oid_inventory_sha256":sha(ids),
        "raw_geojson_canonical_sha256":sha(features),
        "code_counts":{str(k):codes.count(k) for k in sorted(CODES)},
        "batch_checksums":batches,"features":features
    }

def geometry_repair_diagnostics(features):
    """Response-independent source-shape QC; no cross-year intersection."""
    from shapely.validation import explain_validity
    flagged=[]
    for f in features:
        p=f.get("properties",{})
        geom=shape(f["geometry"])
        if geom.is_valid:continue
        new=make_valid(geom)
        pieces=polygon_parts(new)
        if not pieces:
            flagged.append({"oid":p.get("FID"),"class":p.get("FLUCCSCODE"),
                            "reason":"no_polygonal_valid_repair"})
            continue
        fixed=unary_union(pieces)
        old_area=transform(TRANSFORM,geom).area
        new_area=transform(TRANSFORM,fixed).area
        relative=abs(new_area-old_area)/max(old_area,1e-8)
        flagged.append({
          "oid":p.get("FID"),"class":p.get("FLUCCSCODE"),
          "validity":explain_validity(geom)[:160],
          "original_projected_area_acres":round(old_area/M2_PER_ACRE,6),
          "valid_projected_area_acres":round(new_area/M2_PER_ACRE,6),
          "area_delta_acres":round((new_area-old_area)/M2_PER_ACRE,6),
          "relative_change":round(relative,7)})
    flagged.sort(key=lambda p:abs(p.get("area_delta_acres",0)),reverse=True)
    return {"invalid_source_features":len(flagged),
            "largest_absolute_area_repair_candidates":flagged[:15],
            "total_abs_delta_acres":round(sum(abs(p.get("area_delta_acres",0)) for p in flagged),3),
            "not_a_justification_to_relax_a_threshold":True}

def polygon_parts(g):
    if g.is_empty:return []
    if g.geom_type=="Polygon": return [g]
    if g.geom_type=="MultiPolygon":return list(g.geoms)
    if g.geom_type=="GeometryCollection":
        out=[]
        for v in g.geoms:out.extend(polygon_parts(v))
        return out
    return []

def prepare(features,area_field):
    groups={code:[] for code in CODES}
    invalid=0; repaired_area_delta_max=0.0
    max_source_diff_acres=0.0
    for f in features:
        p=f["properties"];g=f.get("geometry")
        if not g:raise GateStop("MISSING_GEOMETRY")
        geom=shape(g)
        if geom.is_empty or geom.geom_type not in ("Polygon","MultiPolygon"):
            raise GateStop("NOT_POLYGON_SOURCE_FEATURE")
        # WGS84 GeoJSON of Charlotte Harbor should be in the Gulf of Mexico.
        bounds=geom.bounds
        if not(-83.5<bounds[0]<-81.0 and -83.5<bounds[2]<-81.0
               and 25.0<bounds[1]<28.0 and 25.0<bounds[3]<28.0):
            raise GateStop("SOURCE_COORDINATES_OUTSIDE_CHARLOTTE_REGION")
        if not geom.is_valid:
            invalid+=1
            fixed=make_valid(geom)
            pieces=polygon_parts(fixed)
            if not pieces: raise GateStop("NONPOLYGONAL_INVALID_GEOMETRY")
            fixed=unary_union(pieces)
            rel=abs(fixed.area-geom.area)/max(geom.area,1e-18)
            repaired_area_delta_max=max(rel,repaired_area_delta_max)
            geom=fixed
        proj=transform(TRANSFORM,geom)
        if not proj.is_valid or proj.area<=0:
            raise GateStop("INVALID_PROJECTED_GEOMETRY")
        # Independent original source area fields test which ring/hole
        # interpretation is correct. This check is applied to EVERY polygon,
        # including syntactically valid input, before inspecting transitions.
        official=p.get(area_field)
        if isinstance(official,bool) or not isinstance(official,(int,float)) or not math.isfinite(official) or official<=0:
            raise GateStop("MISSING_OR_INVALID_SOURCE_ACRE_FIELD:"+str(p.get("FID")))
        computed=proj.area/M2_PER_ACRE
        diff=abs(computed-official)
        max_source_diff_acres=max(diff,max_source_diff_acres)
        if diff>max(0.005,0.002*official):
            raise GateStop("VALIDATED_AREA_MISMATCH:"+str(p.get("FID"))+":"+str(round(diff,4)))
        groups[p["FLUCCSCODE"]].append(proj)
    unioned={c:unary_union(geoms) for c,geoms in groups.items()}
    sums={c:sum(g.area for g in geoms) for c,geoms in groups.items()}
    union_areas={c:unioned[c].area for c in CODES}
    # Duplicate/overlapping features within a year: fail closed if >1% of area
    total_sum=sum(sums.values());total_union=unary_union(list(unioned.values())).area
    duplication=(total_sum-total_union)/max(total_union,1)
    if duplication>0.01:
        raise GateStop(f"EXCESSIVE_WITHIN_YEAR_OVERLAP:{duplication:.6f}")
    return unioned,{"polygon_count":len(features),"invalid_repaired":invalid,
                    "max_repair_relative_area_change":round(repaired_area_delta_max,8),
                    "independent_source_area_field":area_field,
                    "all_polygons_checked_against_original_area_field":True,
                    "maximum_source_area_absolute_difference_acres":round(max_source_diff_acres,4),
                    "within_year_overlap_fraction":round(duplication,8),
                    "class_area_acres":{str(c):round(union_areas[c]/M2_PER_ACRE,3) for c in CODES}}

def transitions(source,target):
    # Using the union of each 2024 mapped category; omissions are "unmapped"
    # not necessarily genuinely unoccupied seabed.
    tgt_union=unary_union(list(target.values()))
    out={}
    for code,s in source.items():
        denom=s.area
        if denom<=0:raise GateStop("EMPTY_SOURCE_CLASS:"+str(code))
        cells={}
        for tc,t in target.items():
            cells[str(tc)]=s.intersection(t).area
        unmapped=max(0.0,denom-s.intersection(tgt_union).area)
        cells["unmapped"]=unmapped
        closure=(sum(cells.values())-denom)/denom
        if abs(closure)>0.01:
            raise GateStop("TRANSITION_ROW_NOT_CLOSED:"+str(code))
        out[str(code)]={
            "source_mapped_acres":round(denom/M2_PER_ACRE,3),
            "target_area_acres":{k:round(v/M2_PER_ACRE,3) for k,v in cells.items()},
            "target_fraction_percent":{k:round(100*v/denom,3) for k,v in cells.items()},
            "sum_minus_source_area_relative":round(closure,7)}
    return out

def boundary_interior_sensitivity(source,target,distances=(5.0,10.0,25.0)):
    """Retain only class-overlap areas >= d metres inside both mapped classes."""
    src_seagrass=unary_union([source[9113],source[9116]])
    tgt_seagrass=unary_union([target[9113],target[9116]])
    raw={
        "algae_to_seagrass_acres":source[9121].intersection(tgt_seagrass).area/M2_PER_ACRE,
        "seagrass_to_algae_acres":src_seagrass.intersection(target[9121]).area/M2_PER_ACRE,
    }
    output={}
    for d in distances:
        if d<0:raise GateStop('NEGATIVE_BOUNDARY_DISTANCE')
        eroded_src_algae=source[9121].buffer(-d)
        eroded_tgt_seagrass=tgt_seagrass.buffer(-d)
        eroded_src_seagrass=src_seagrass.buffer(-d)
        eroded_tgt_algae=target[9121].buffer(-d)
        interior={
            "algae_to_seagrass_acres":eroded_src_algae.intersection(eroded_tgt_seagrass).area/M2_PER_ACRE,
            "seagrass_to_algae_acres":eroded_src_seagrass.intersection(eroded_tgt_algae).area/M2_PER_ACRE,
        }
        for name,v in interior.items():
            if v<0 or v>raw[name]+1e-8:
                raise GateStop("INTERIOR_BOUNDARY_SENSITIVITY_INCONSISTENT")
        output[str(int(d))]={
          "minimum_interior_distance_m_each_year":d,
          "interior_mapped_conversion_acres":{k:round(v,3) for k,v in interior.items()},
          "percent_of_original_mapped_conversion_relying_on_interior":{
             k:(round(100*v/raw[k],2) if raw[k]>0 else None) for k,v in interior.items()},
        }
    return {
      "original_mapped_conversion_acres":{k:round(v,3) for k,v in raw.items()},
      "boundary_sensitivity":output,
      "interpretation":"Geomorphological mapping-boundary sensitivity only, not a causal or detection-corrected biological change.",
    }
def calculate(record22,record24):
    groups22,qc22=prepare(record22["features"],"Geodesic")
    groups24,qc24=prepare(record24["features"],"ACRES")
    tab=transitions(groups22,groups24)
    interior=boundary_interior_sensitivity(groups22,groups24)
    ac=tab["9121"]
    return {
        "schema":"tampa.charlotte_public_gis_transition_v1",
        "evidence_class":"OUTCOME_CONTEXT_EXPOSED_DESCRIPTIVE_SPATIAL_CLASS_CONVERSION",
        "source_year":"2022","target_year":"2024",
        "source_metadata":{
          y:{k:v for k,v in record.items() if k not in ("features","batch_checksums")}
          for y,record in (("2022",record22),("2024",record24))
        },
        "quality_control":{"2022":qc22,"2024":qc24},
        "topology_repair_rule":"Use make_valid on invalid source shells ONLY if equal-area repaired polygon matches source's independent Geodesic or ACRES field within max(0.005 acre, 0.2%). Never accept NaN, missing official area, or major mismatch.",
        "source_area_to_target_class":tab,
        "mapped_boundary_interior_sensitivity":interior,
        "2022_attached_macroalgae_area_reclassified_as_2024_seagrass_acres":round(
            ac["target_area_acres"]["9113"]+ac["target_area_acres"]["9116"],3),
        "2022_attached_macroalgae_percent_reclassified_as_2024_seagrass":round(
            ac["target_fraction_percent"]["9113"]+ac["target_fraction_percent"]["9116"],3),
        "not_a_causal_effect":True,
        "not_true_bare_or_extinction":True,
        "not_seagrass_recovery_effect_with_control":True,
        "scope_warning":"Area transitions are confined to mapped 2022 class polygons, not the full seabed or necessarily the entire baywide published-area footprint. A 2024 unmapped polygon is NOT true biological absence.",
        "algae_definition":"Code 9121 attached macroalgae only; drifting or loose algae are not quantified.",
        "no_predictor_from_2025":True,
        "not_new_blind_confirmation":True,
        "mapping_minimum_unit_acres":0.25,
        "projected_equal_area_crs":"EPSG:6933",
        "disallowed_claims":["algae inhibits recolonization","seagrass mortality","universal recovery mechanism","independent cell-level replicates","causal proof of competition"]
    }

def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--output",required=True)
    a.add_argument("--raw-dir",default=None)
    x=a.parse_args(argv)
    try:
        data={}
        for year in ("2022","2024"):
            data[year]=download_year(year)
            if x.raw_dir:
                p=Path(x.raw_dir)/f"charlotte_{year}_public_layer.geojson"
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(json.dumps({"type":"FeatureCollection",
                     "features":data[year]["features"]},separators=(",",":"))+"\n",encoding="utf-8")
        diag={year:geometry_repair_diagnostics(data[year]["features"])
              for year in ("2022","2024")}
        report=calculate(data["2022"],data["2024"])
        report["source_geometry_repair_audit"]=diag
        rc=0
    except (GateStop,ValueError,TypeError) as e:
        report={"schema":"tampa.charlotte_public_gis_transition_v1",
                "status":"STOP_SOURCE_OR_TOPOLOGY_GATE",
                "reason":str(e),
                "source_geometry_repair_audit":locals().get("diag"),
                "raw_source_rosters_fetched":{y:len(v["features"]) for y,v in locals().get("data",{}).items()},
                "ecological_transition_estimated":False}
        rc=2
    p=Path(x.output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return rc

if __name__=="__main__":
    sys.exit(main())
