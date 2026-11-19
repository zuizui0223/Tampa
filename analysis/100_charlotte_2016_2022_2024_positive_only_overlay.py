#!/usr/bin/env python3
"""Three-date public GIS overlap for *verified 2016 mapped seagrass* only.

No attempt to call 2016 "unknown / code 0 / 5400" absent. Only positive
2016 codes 9113 + 9116 are used as a prior seagrass-recorded mask.
2022 attached-algae -> 2024 seagrass is MAP RECLASSIFICATION, not verified
plant recruitment or a causal recovery estimate. Outcomes are context-exposed.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path

from shapely.ops import unary_union
from shapely.geometry import GeometryCollection

ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("gis92",ROOT/"analysis/92_charlotte_public_gis_class_transitions.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
LEGACY="https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental/MapServer/20"
BBOX_2022_2024={
 "xmin":-9159637.622929975,"ymin":3085497.118059525,
 "xmax":-9133636.733688185,"ymax":3115537.8056237204
}
EXPECTED_CLASS_COUNT={"9113":954,"9116":428}
SOURCE_YEAR="2016"
ALGAE_CODE=9121
SEAGRASS=(9113,9116)
SOURCE_AREA_TOLERANCE="max(0.005 acres, 0.002 * official ACRES) per original feature"
UA="Historical 2016 mapped positive-only spatial audit/1.0"

def query(url,params):
    return M.query(url,params)

def source16(query_fn=query):
    meta=query_fn(LEGACY,{"f":"json"})
    fields={f.get("name"):f.get("type") for f in meta.get("fields",[])}
    if (meta.get("geometryType")!="esriGeometryPolygon" or
        fields.get("FLUCCS_CODE")!="esriFieldTypeString" or
        fields.get("ACRES")!="esriFieldTypeDouble" or
        (meta.get("extent",{}).get("spatialReference") or {}).get("wkid")!=2882):
        raise M.GateStop("LEGACY_2016_IDENTITY_UNVERIFIED")
    modern={}
    for year,url in M.LAYER_URLS.items():
        g=query_fn(url,{"f":"json"})
        extent=g.get("extent") or {}
        if not all(isinstance(extent.get(k),(int,float)) for k in BBOX_2022_2024):
            raise M.GateStop("MODERN_BOUNDING_BOX_UNAVAILABLE")
        modern[year]={k:extent[k] for k in BBOX_2022_2024}
    union={
      k:(min(modern[y][k] for y in modern) if k in ("xmin","ymin")
         else max(modern[y][k] for y in modern)) for k in BBOX_2022_2024
    }
    if any(abs(union[k]-v)>1.0 for k,v in BBOX_2022_2024.items()):
        raise M.GateStop("HISTORICAL_FILTER_ENVELOPE_DRIFT")
    envelope=",".join(str(BBOX_2022_2024[k]) for k in ("xmin","ymin","xmax","ymax"))
    common={"geometry":envelope,"geometryType":"esriGeometryEnvelope",
            "inSR":3857,"spatialRel":"esriSpatialRelIntersects","f":"json"}
    ids_all=[]
    counts={}
    for code,n_expected in EXPECTED_CLASS_COUNT.items():
        where="FLUCCS_CODE='"+code+"'"
        count=query_fn(LEGACY+"/query",{**common,"where":where,"returnCountOnly":"true"}).get("count")
        if count!=n_expected:
            raise M.GateStop("2016_CLASS_COUNT_DRIFT:"+code+":"+str(count))
        res=query_fn(LEGACY+"/query",{**common,"where":where,"returnIdsOnly":"true"})
        ids=res.get("objectIds")
        if not isinstance(ids,list) or len(ids)!=count or len(ids)!=len(set(ids)):
            raise M.GateStop("LEGACY_2016_EXACT_ID_INVENTORY_FAIL:"+code)
        ids_all.extend(ids);counts[code]=count
    if len(ids_all)!=len(set(ids_all)):raise M.GateStop("2016_CROSS_CLASS_DUPLICATE_OBJECT_ID")
    ids_all.sort()
    feats=[];checks=[]
    for i in range(0,len(ids_all),M.BATCH_SIZE):
        batch=ids_all[i:i+M.BATCH_SIZE]
        res=query_fn(LEGACY+"/query",{
            "objectIds":",".join(map(str,batch)),
            "outFields":"OBJECTID,FLUCCS_CODE,ACRES",
            "returnGeometry":"true","outSR":"4326","f":"geojson"})
        batch_feats=res.get("features")
        if res.get("type")!="FeatureCollection" or not isinstance(batch_feats,list):
            raise M.GateStop("2016_GEOJSON_BATCH_UNAVAILABLE")
        observed={f.get("properties",{}).get("OBJECTID") for f in batch_feats}
        if observed!=set(batch) or len(batch_feats)!=len(batch):
            raise M.GateStop("2016_GEOJSON_EXACT_ID_MISMATCH")
        for f in batch_feats:
            props=f["properties"]
            code=props.get("FLUCCS_CODE")
            if code not in EXPECTED_CLASS_COUNT:raise M.GateStop("2016_UNEXPECTED_CODE_IN_POSITIVE_BATCH")
            if props.get("ACRES") is None:raise M.GateStop("2016_SOURCE_ACRES_MISSING")
            # Safe internal canonical mapping to the verified 2022/24 preparation.
            props["FID"]=props["OBJECTID"]
            props["FLUCCSCODE"]=int(code)
        feats.extend(batch_feats)
        checks.append({"count":len(batch),"first_oid":batch[0],"last_oid":batch[-1],
                       "source_geojson_sha256":M.sha(batch_feats)})
    if len(feats)!=len(ids_all):raise M.GateStop("2016_INCOMPLETE_RESPONSE")
    feats.sort(key=lambda f:f["properties"]["OBJECTID"])
    return {"features":feats,"exact_source_ids":len(ids_all),
            "2016_source_class_counts":counts,
            "legacy_metadata_sha256":M.sha(meta),
            "source_raw_features_sha256":M.sha(feats),
            "source_oids_sha256":M.sha(ids_all),
            "batch_checksums":checks,"bounding_envelope_3857":BBOX_2022_2024}

def masked_overlap(positive_2016,sea22,algae22,sea24,algae24):
    area=algae22.area
    if area<=0:raise M.GateStop("2022_ALGAE_AREA_EMPTY")
    historical=algae22.intersection(positive_2016)
    h=historical.area
    h_to_sea=historical.intersection(sea24).area
    h_to_algae=historical.intersection(algae24).area
    h_mapped=historical.intersection(unary_union([sea24,algae24])).area
    h_unmapped=max(0.0,h-h_mapped)
    if abs(h_to_sea+h_to_algae+h_unmapped-h)>max(5.0,0.001*h):
        raise M.GateStop("THREE_DATE_ROW_CLOSURE_FAIL")
    out={
        "2022_algae_total_acres":round(area/M.M2_PER_ACRE,3),
        "2016_seagrass_positive_within_2022_algae_acres":round(h/M.M2_PER_ACRE,3),
        "2016_seagrass_positive_share_of_2022_algae_percent":round(100*h/area,3),
        "2016_positive_2022_algae_to_2024_class_acres":{
            "seagrass":round(h_to_sea/M.M2_PER_ACRE,3),
            "attached_macroalgae":round(h_to_algae/M.M2_PER_ACRE,3),
            "unmapped":round(h_unmapped/M.M2_PER_ACRE,3)},
        "2016_positive_2022_algae_to_2024_class_fraction_percent":{
            "seagrass":round(100*h_to_sea/h,3) if h else None,
            "attached_macroalgae":round(100*h_to_algae/h,3) if h else None,
            "unmapped":round(100*h_unmapped/h,3) if h else None},
        "non_2016_positive_2022_algae_acres":round((area-h)/M.M2_PER_ACRE,3),
        "not_positive_2016_is_not_verified_2016_absence":True
    }
    return out

def historic_positive_coverage_reference(pos16,modern22):
    """Descriptive reference for how widespread 2016 mapped-seagrass overlap is.

    Matched area denominator within each 2022 positive class. No unobserved
    substrate is labeled negative; this is NOT a spatially independent null.
    """
    out={}
    for cls in (9113,9116,9121):
        g=modern22[cls]
        total=g.area
        if total<=0:raise M.GateStop("EMPTY_2022_REFERENCE_CLASS:"+str(cls))
        overlap=g.intersection(pos16).area
        if overlap<0 or overlap>total+1e-4:raise M.GateStop("BAD_HISTORIC_COVERAGE")
        out[str(cls)]={
            "2022_source_class_area_acres":round(total/M.M2_PER_ACRE,3),
            "overlaps_2016_mapped_seagrass_acres":round(overlap/M.M2_PER_ACRE,3),
            "overlaps_2016_mapped_seagrass_percent":round(100*overlap/total,3),
        }
    seagrass_total=sum(modern22[cls].area for cls in (9113,9116))
    seagrass_overlap=sum(modern22[cls].intersection(pos16).area for cls in (9113,9116))
    out["2022_seagrass_combined"]={
       "2022_source_class_area_acres":round(seagrass_total/M.M2_PER_ACRE,3),
       "overlaps_2016_mapped_seagrass_acres":round(seagrass_overlap/M.M2_PER_ACRE,3),
       "overlaps_2016_mapped_seagrass_percent":round(100*seagrass_overlap/seagrass_total,3)
    }
    # Difference measured on the map only. No ecological preference test
    # without equivalent sampling universe and spatial independence.
    algae_percent=100*modern22[9121].intersection(pos16).area/modern22[9121].area
    sea_percent=100*seagrass_overlap/seagrass_total
    return {
       "class_specific":out,
       "algae_minus_seagrass_historical_positive_overlap_percentage_points":round(algae_percent-sea_percent,3),
       "no_selection_or_legacy_significance_test":True,
       "interpretation":"Area fractions of 2016 map-positive source within each 2022 mapped class; no causal history effect, no known full sampling background or independent units."
    }
def historical_interior_sensitivity(pos16,algae22,sea24,algae24,distances=(0.0,5.0,10.0,25.0)):
    """3-date class overlap with every mapped class eroded inside by d metres."""
    results={}
    previous=None
    for d in distances:
        if d<0: raise M.GateStop("NEGATIVE_BOUNDARY_DISTANCE")
        h16=pos16.buffer(-d) if d else pos16
        a22=algae22.buffer(-d) if d else algae22
        s24=sea24.buffer(-d) if d else sea24
        a24=algae24.buffer(-d) if d else algae24
        hist=h16.intersection(a22)
        histarea=hist.area
        sea=hist.intersection(s24).area
        algae=hist.intersection(a24).area
        uncovered=max(0.0,histarea-hist.intersection(unary_union([s24,a24])).area)
        if abs(sea+algae+uncovered-histarea)>max(5.0,0.001*histarea):
            raise M.GateStop("HISTORICAL_INTERIOR_ROW_NOT_CLOSED")
        val={"2016_positive_and_2022_algae_interior_acres":round(histarea/M.M2_PER_ACRE,3),
             "2024_mapped_seagrass_interior_acres":round(sea/M.M2_PER_ACRE,3),
             "2024_mapped_algae_interior_acres":round(algae/M.M2_PER_ACRE,3),
             "2024_unmapped_interior_acres":round(uncovered/M.M2_PER_ACRE,3),
             "2024_seagrass_share_of_reduced_historical_algae_mask_percent":(round(100*sea/histarea,3) if histarea else None)}
        if previous is not None:
            for k in ("2016_positive_and_2022_algae_interior_acres","2024_mapped_seagrass_interior_acres","2024_mapped_algae_interior_acres"):
                if val[k]>previous[k]+0.003:raise M.GateStop("EROSION_INCREASES_OVERLAP")
        results[str(int(d))]=val;previous=val
    return {
      "metre_inside_each_of_three_mapped_class_boundaries":results,
      "not_positional_or_thematic_accuracy_correction":True,
      "scope":"Each erosion changes the denominator; interior shares are not treatment effects or evidence of true recolonization."
    }
def calc(dat16,dat22,dat24):
    historic,qc16=M.prepare(dat16["features"],"ACRES")
    s22,qc22=M.prepare(dat22["features"],"Geodesic")
    s24,qc24=M.prepare(dat24["features"],"ACRES")
    src16_positive=unary_union([historic[9113],historic[9116]])
    sea22=unary_union([s22[9113],s22[9116]])
    sea24=unary_union([s24[9113],s24[9116]])
    reference=historic_positive_coverage_reference(src16_positive,s22)
    result=masked_overlap(src16_positive,sea22,s22[9121],sea24,s24[9121])
    sensitivity=historical_interior_sensitivity(src16_positive,s22[9121],sea24,s24[9121])
    if abs(sensitivity["metre_inside_each_of_three_mapped_class_boundaries"]["0"]["2016_positive_and_2022_algae_interior_acres"]-result["2016_seagrass_positive_within_2022_algae_acres"])>.005:
        raise M.GateStop("SENSITIVITY_DOES_NOT_MATCH_FROZEN_PRIMARY")
    return {
        "schema":"tampa.charlotte_three_date_positive_only_map_overlap_v1",
        "evidence":"OUTCOME_CONTEXT_EXPOSED_DESCRIPTIVE_2016_POSITIVE_ONLY_GEOMETRY",
        "source_years":[2016,2022,2024],
        "historical_source":{
            k:v for k,v in dat16.items() if k not in ("features","batch_checksums")},
        "modern_source":{
            yr:{k:v for k,v in dat.items() if k not in ("features","batch_checksums")}
            for yr,dat in (("2022",dat22),("2024",dat24))},
        "area_qc":{"2016":qc16,"2022":qc22,"2024":qc24},
        "map_history":result,
        "historic_positive_source_coverage_reference":reference,
        "historical_map_boundary_interior_sensitivity":sensitivity,
        "biological_recolonization_confirmed":False,
        "absence_or_survey_footprint_confirmed":False,
        "causal_macroalgae_inhibition_estimated":False,
        "2016_legacy_undefined_codes_excluded_from_positive_mask":["0","5400"],
        "2016_9121_zero_count_does_not_prove_algal_absence":True,
        "conclusion_boundary":"The 2016-mapped seagrass-positive footprint is a historical map state, not a longitudinal demographic observation or eligibility of all unclassified area. 2022 attached algae mapping does not imply plant death. 2024 seagrass mapping is a class return, not proven clonal/seed recovery."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--raw-dir")
    a=ap.parse_args()
    try:
        d16=source16()
        d22=M.download_year("2022")
        d24=M.download_year("2024")
        if a.raw_dir:
            p=Path(a.raw_dir);p.mkdir(parents=True,exist_ok=True)
            for y,d in [("2016",d16),("2022",d22),("2024",d24)]:
                (p/f"charlotte_{y}_positive_only_or_full.geojson").write_text(json.dumps(
                    {"type":"FeatureCollection","features":d["features"]},
                    ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
        output=calc(d16,d22,d24)
        rc=0
    except (M.GateStop,ValueError,TypeError,KeyError) as e:
        output={"schema":"tampa.charlotte_three_date_positive_only_map_overlap_v1",
                "status":"STOP_SOURCE_OR_GEOMETRY_GATE","reason":str(e),
                "biological_recolonization_confirmed":False,
                "three_date_overlap_computed":False}
        rc=2
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(output,indent=2,sort_keys=True))
    return rc

if __name__=="__main__":sys.exit(main())
