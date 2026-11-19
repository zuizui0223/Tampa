#!/usr/bin/env python3
"""Test if the original SWFWMD 2024 legacy district map has OTHER bottom classes.

The Charlotte Harbor 2024 *hosted* FeatureServer only contains 9113,9116,9121.
But older district-year MapServers have additional codes such as 0,5400,
6510,6540,7210. The original 2024 district-wide MapServer might retain
these classes and thereby resolve some of the 222 acres absent from the
hosted three-class vegetation map. MUST verify rather than assume.

Source-only grouped code frequencies inside a FIXED Charlotte Harbor map
envelope. No polygons, no true bottom coverage or ecological survival.
Requires SWFWMD 6am–10pm America/New_York access window.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("old110",ROOT/"analysis/110_charlotte_2018_2020_legacy_map_preflight.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
LAYER=M.SOURCE_BASE+"/3"
SOURCE="tampa.charlotte_2024_district_full_original_legend_preflight_v1"
EXPECTED="Seagrass in 2024"
HOSTED={"9113":2087,"9116":912,"9121":210}
KNOWN={"0":"land","5400":"open_water_or_unvegetated_as_defined_by_original_key",
       "6510":"tidal_flat","6540":"oyster_reef","7210":"submerged_nonvegetated_sand_per_2016_SWFWMD_mapping_class_key_check_2024_descriptor",
       "9113":"patchy_seagrass","9116":"continuous_seagrass",
       "9121":"attached_macroalgae","9122":"composite_colonized_algae"}
class Stop(ValueError):pass

def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def inspect(query=M.request,ref=M.get_reference):
    bbox,ref_sha=ref()
    layer=query(LAYER,{"f":"json"})
    fields={x.get("name"):x.get("type") for x in layer.get("fields",[]) if isinstance(x,dict)}
    if layer.get("name")!=EXPECTED or layer.get("geometryType")!="esriGeometryPolygon":
        raise Stop("NOT_2024_ORIGINAL_DISTRICT_POLYGON_LAYER")
    if fields.get("FLUCCSCODE") not in ("esriFieldTypeInteger","esriFieldTypeSmallInteger"):
        raise Stop("ORIGINAL_2024_MAPPED_CATEGORY_CODE_MISSING")
    if (layer.get("extent") or {}).get("spatialReference",{}).get("wkid")!=2882:
        raise Stop("ORIGINAL_2024_CRS_UNVERIFIED")
    oid=[name for name,typ in fields.items() if typ=="esriFieldTypeOID"]
    if len(oid)!=1:raise Stop("ORIGINAL_2024_OID_TYPE_AMBIGUOUS")
    geomstr=",".join(str(bbox[k]) for k in ("xmin","ymin","xmax","ymax"))
    spatial={"f":"json","geometry":geomstr,"geometryType":"esriGeometryEnvelope",
             "inSR":3857,"spatialRel":"esriSpatialRelIntersects"}
    total=query(LAYER+"/query",{**spatial,"where":"1=1","returnCountOnly":"true"}).get("count")
    if not isinstance(total,int) or total<1:raise Stop("ORIGINAL_2024_BBOX_COUNT_UNAVAILABLE")
    grouped=query(LAYER+"/query",{
        **spatial,"where":"1=1","returnGeometry":"false",
        "groupByFieldsForStatistics":"FLUCCSCODE",
        "outStatistics":json.dumps([{"statisticType":"count","onStatisticField":oid[0],
              "outStatisticFieldName":"n"}]),
        "orderByFields":"FLUCCSCODE"})
    fs=grouped.get("features")
    if not isinstance(fs,list) or grouped.get("exceededTransferLimit"):
        raise Stop("ORIGINAL_2024_GROUPED_CLASSES_INCOMPLETE")
    counts={}
    for f in fs:
        a=f.get("attributes",{})
        raw=a.get("FLUCCSCODE")
        if isinstance(raw,(int,float)) and int(raw)==raw:code=str(int(raw))
        elif raw is None:code="NULL"
        else:code=str(raw)
        number=a.get("n")
        if code in counts or not isinstance(number,int) or number<0:
            raise Stop("ORIGINAL_2024_DUPLICATE_OR_INVALID_GROUPED_CLASS")
        counts[code]=number
    if sum(counts.values())!=total:
        raise Stop("ORIGINAL_2024_MAP_CLASS_COUNT_MASS_NONCLOSURE")
    for code in ("9113","9116","9121"):
        n=query(LAYER+"/query",{**spatial,"where":"FLUCCSCODE="+code,
            "returnCountOnly":"true"}).get("count")
        if n!=counts.get(code,0):
            raise Stop("ORIGINAL_2024_FOCAL_CODE_CROSSQUERY_DISAGREES:"+code)
    non3={k:v for k,v in counts.items() if k not in HOSTED}
    return {
      "schema":SOURCE,
      "status":"PASS_OFFICIAL_2024_ORIGINAL_DISTRICT_YEAR_CODE_DICTIONARY_ONLY",
      "source":LAYER,
      "source_metadata_sha256":sha(layer),
      "reference_2016_2022_2024_map_envelope_sha256":ref_sha,
      "source_extent_3857":bbox,
      "source_oid_field_typed":oid[0],
      "source_oid_field_advertised":layer.get("objectIdField"),
      "original_independent_area_field_candidates":[k for k in fields if any(
          t in k.upper() for t in ("ACRE","AREA","GEODESIC"))],
      "all_original_features_intersecting_fixed_Charlotte_envelope":total,
      "exhaustive_original_source_code_counts":counts,
      "original_mapped_code_names_are_from_provisional_external_legend_only":KNOWN,
      "original_categories_other_than_9113_9116_9121":non3,
      "n_source_polygons_of_other_classes":sum(non3.values()),
      "contains_background_benthic_map_categories":bool(non3),
      "source_classes_overlapping_hosted_2024_count_nocrosswalk":{
          c:counts.get(c,0) for c in HOSTED},
      "hosted_2024_three_code_counts_from_previous_verified_source":HOSTED,
      "source_2024_full_survey_footprint_confirmed":False,
      "source_2024_all_original_code_semantics_verified":False,
      "giant_unmapped_habitat_state_identified":False,
      "no_geometry_downloaded":True,
      "claim_boundary":"The official original district map may include extra classes, but their exact biological meaning, mapping footprint, and overlap with FID37/2166 2024 three-class-unmapped areas need exact original source geometry verification. Counts cannot establish 2024 benthic fate."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    window=M.official_service_window()
    if not window["portal_open_time"]:
        out={"schema":SOURCE,"status":"SKIP_OFFICIAL_SOURCE_OUTSIDE_PORTAL_HOURS",
             "source_access_window":window,"no_benthic_fate_inferred":True};rc=0
    else:
        try:out=inspect();out["source_access_window"]=window;rc=0
        except (Stop,M.Stop,ValueError,KeyError,TypeError) as e:
            out={"schema":SOURCE,"status":"STOP_2024_ORIGINAL_CATEGORY_SOURCE_GATE",
                 "reason":str(e),"source_access_window":window,
                 "no_benthic_fate_inferred":True};rc=2
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":sys.exit(main())
