#!/usr/bin/env python3
"""Preflight 2018/2020 SWFWMD polygon-map category support in Charlotte Harbor.

Source (official District legacy MapServer):
https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental_Seagrass2018_sql/MapServer
layers 0 (2018) and 1 (2020).

The same official service family also has a FeatureServer on www25 whose
2018 layer returned status/messages instead of a layer schema in 2026-11-19
live CI; that endpoint is not treated as a valid source response. This is a
pre-outcome metadata-access-route correction, NOT another bay/time window.

No feature geometry, no area conversions and no ecological recovery outputs.
The spatial envelope is source-locked to a previously validated 2016/22/24
Charlotte GIS report. The District's open data site has a 06:00–22:00 America/New_York window; outside the official portal window mark SKIP, NOT source schema drift. During official hours, the service may still be unavailable; then stop
without substituting another year or interpreting zero mapped algae as absence.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

ROOT=Path(__file__).resolve().parents[1]
SOURCE_BASE="https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental_Seagrass2018_sql/MapServer"
LAYERS={"2018":0,"2020":1}
CLASSES={9113:"patchy_seagrass",9116:"continuous_seagrass",9121:"mapped_attached_macroalgae"}
LEGACY_CRS=2882
SPATIAL_CRS=3857
REFERENCE=ROOT/"results/charlotte_historical_positive_three_date_verified_20261119.json"
REFERENCE_SCHEMA="tampa.charlotte_three_date_positive_only_source_release_v1"
PREVIOUS_SOURCE_GIS_RUN=44446322239
USER_AGENT="Academic source class inventory, SWFWMD seagrass maps 2018-2020/1.0"
class Stop(ValueError):pass

OFFICIAL_SOURCE_HOURS_LOCAL=(6,22)
OFFICIAL_HOURS_REFERENCE="https://www.swfwmd.state.fl.us/resources/data-maps/gis-maps-survey"

def official_service_window(now_utc=None):
    """Distinguish SWFWMD declared REST office window from missing source data.

    The District GIS Open Data portal is available 06:00-22:00 local, but
    the exact MapServer's own per-service uptime may differ. Mark outside
    window as a *possible* source access block; do not claim source absent.
    """
    if now_utc is None:now_utc=datetime.now(timezone.utc)
    if now_utc.tzinfo is None:raise Stop("UTC_CLOCK_NOT_TZ_AWARE")
    local=now_utc.astimezone(ZoneInfo("America/New_York"))
    return {
      "local_date_time":local.isoformat(),
      "local_timezone":"America/New_York",
      "declared_portal_open_window_local":"06:00-22:00",
      "portal_open_time":OFFICIAL_SOURCE_HOURS_LOCAL[0]<=local.hour<OFFICIAL_SOURCE_HOURS_LOCAL[1],
      "official_portal_hours_reference":OFFICIAL_HOURS_REFERENCE,
      "service_specific_availability_not_guaranteed":True
    }

def request(url,params):
    uri=url+"?"+urlencode(params)
    r=Request(uri,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    try:
        with urlopen(r,timeout=45) as conn:
            body=conn.read(3_000_001)
    except (URLError,HTTPError,TimeoutError,OSError) as e:
        raise Stop("PUBLIC_SOURCE_UNREACHABLE:"+type(e).__name__) from e
    if len(body)>3_000_000:raise Stop("SOURCE_METADATA_TOO_BIG")
    try:x=json.loads(body)
    except (ValueError,UnicodeDecodeError) as e:raise Stop("ARCGIS_NOT_JSON") from e
    if not isinstance(x,dict) or "error" in x:
        raise Stop("ARCGIS_ERROR:"+str(x.get("error",x))[:250])
    return x

def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def get_reference(path=REFERENCE):
    x=json.loads(Path(path).read_text(encoding="utf-8"))
    if x.get("schema")!=REFERENCE_SCHEMA or x.get("verified_ci",{}).get("run_id")!=PREVIOUS_SOURCE_GIS_RUN:
        raise Stop("REFERENCE_IDENTITY_UNVERIFIED")
    h=x["report"]["historical_source"]
    if h.get("exact_source_ids")!=1382:
        raise Stop("REFERENCE_2016_COHORT_DRIFT")
    bbox=h.get("bounding_envelope_3857")
    if not isinstance(bbox,dict) or set(bbox)!={"xmin","ymin","xmax","ymax"} or not all(
            isinstance(v,(int,float)) and math.isfinite(v) for v in bbox.values()):
        raise Stop("REFERENCE_BOUNDS_NOT_FIXED")
    if not bbox["xmin"]<bbox["xmax"] or not bbox["ymin"]<bbox["ymax"]:
        raise Stop("REFERENCE_BOUNDS_INVALID")
    return bbox,sha(x)

def collect(fetch=request,ref=get_reference):
    bbox,reference_sha=ref()
    b=",".join(str(bbox[k]) for k in ("xmin","ymin","xmax","ymax"))
    geometry={"geometry":b,"geometryType":"esriGeometryEnvelope",
              "inSR":SPATIAL_CRS,"spatialRel":"esriSpatialRelIntersects","f":"json"}
    output={}
    for year,layerid in LAYERS.items():
        url=SOURCE_BASE+"/"+str(layerid)
        meta=fetch(url,{"f":"json"})
        if meta.get("name")!=f"Seagrass in {year}" or meta.get("geometryType")!="esriGeometryPolygon":
            raise Stop("SOURCE_YEAR_OR_POLYGON_IDENTITY_DRIFT:"+year+
                       ":name="+repr(meta.get("name"))+
                       ":geometry="+repr(meta.get("geometryType"))+
                       ":type="+repr(meta.get("type"))+
                       ":first_keys="+repr(sorted(meta.keys())[:18]))
        fields={f.get("name"):f.get("type") for f in meta.get("fields",[]) if isinstance(f,dict)}
        if (fields.get("FLUCCSCODE") not in ("esriFieldTypeInteger","esriFieldTypeSmallInteger") or
            fields.get("FLUCCSDESC")!="esriFieldTypeString"):
            raise Stop("SOURCE_CLASS_FIELDS_DRIFT:"+year)
        oid=meta.get("objectIdField")
        oid_candidates=[key for key,typ in fields.items() if typ=="esriFieldTypeOID"]
        oid_verified=bool(isinstance(oid,str) and fields.get(oid)=="esriFieldTypeOID")
        # A MapServer can expose classification/count queries but omit its
        # object-id advertisement. Preserve that distinction explicitly:
        # count-only research is allowed; feature-geometry acquisition is NOT.
        # Later exact OID inventories must validate unique source identities.
        crs=(meta.get("extent") or {}).get("spatialReference") or {}
        if crs.get("wkid")!=LEGACY_CRS:
            raise Stop("LEGACY_SOURCE_CRS_DRIFT:"+year)
        all_count=fetch(url+"/query",{**geometry,"where":"1=1","returnCountOnly":"true"}).get("count")
        if not isinstance(all_count,int) or all_count<1:raise Stop("NO_SPATIAL_SOURCE_RECORDS:"+year)
        per={}
        for k in CLASSES:
            n=fetch(url+"/query",{**geometry,"where":"FLUCCSCODE="+str(k),"returnCountOnly":"true"}).get("count")
            if not isinstance(n,int) or n<0:raise Stop("BAD_FOCAL_CLASS_QUERY:"+year+":"+str(k))
            per[str(k)]=n
        other=all_count-sum(per.values())
        if other<0:raise Stop("FOCAL_CLASS_COUNTS_EXCEED_SPATIAL_ALL:"+year)
        output[year]={
            "source_url":url,
            "metadata_sha256":sha(meta),
            "source_name":meta.get("name"),
            "declared_source_crs":crs,
            "object_id_field":oid,
            "object_id_field_is_esri_oid":oid_verified,
            "source_candidate_esri_oid_field_names":oid_candidates,
            "exact_feature_geometry_source_oid_gate_passed":oid_verified,
            "nonspatial_area_field_metadata":{
                name:fields.get(name) for name in ("Geodesic","ACRES","Shape__Area","Shape.STArea()")
                if name in fields},
            "map_extent_2016_2024_reference_envelope_3857":bbox,
            "n_legacy_source_features_intersecting_envelope":all_count,
            "n_by_focal_legacy_flucss_code":per,
            "n_other_classes_uninterpreted":other,
            "algae_map_class_supported":per["9121"]>0,
            "future_geometry_claim_authorized":False,
        }
    return {
        "schema":"tampa.charlotte_2018_2020_official_map_preflight_v1",
        "status":"PASS_OFFICIAL_LEGACY_MAP_METADATA_AND_CLASS_COUNTS_ONLY",
        "reference_pinned_release":str(REFERENCE.relative_to(ROOT)),
        "reference_sha256":reference_sha,
        "source_base":SOURCE_BASE,
        "years":output,
        "no_feature_geometries_opened":True,
        "no_areal_transitions_estimated":True,
        "no_temporary_algae_absence_inferred_from_zero_map_labels":True,
        "claim_boundary":"The original 2018/2020 district-wide legacy source has its own survey footprint and attributes. A count inside a common envelope is not a matched historical habitat area; do not assume a map area without source polygon/acreage QC.",
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    window=official_service_window()
    if not window["portal_open_time"]:
        # Do not query or label source 'schema drift' during documented
        # SWFWMD portal closure. This is a SKIP, not a passed data gate.
        out={"schema":"tampa.charlotte_2018_2020_official_map_preflight_v1",
             "status":"SKIP_OUTSIDE_DISTRICT_PUBLISHED_SOURCE_HOURS",
             "access_window":window,"years_checked":[],"source_class_results_unavailable":True,
             "no_areal_transitions_estimated":True}
        rc=0
    else:
        try:
            out=collect()
            out["access_window"]=window
            rc=0
        except (Stop,TypeError,KeyError,ValueError) as e:
            out={"schema":"tampa.charlotte_2018_2020_official_map_preflight_v1",
                 "status":"STOP_HISTORIC_SOURCE_PREFLIGHT_IN_PUBLISHED_HOURS",
                 "access_window":window,
                 "reason":str(e),"no_areal_transitions_estimated":True}
            rc=2
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True,indent=2))
    return rc
if __name__=="__main__":
    sys.exit(main())
