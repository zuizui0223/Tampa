#!/usr/bin/env python3
"""Aggregate 2016 FLUCCS_CODE categories inside Charlotte 2022/24 envelope.

Public-source category/record counts only. No polygons, area or 2016 history
transition result. Unrecognized codes remain uninterpreted (not zeros).
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path

SRC=Path(__file__).resolve().parent/"97_charlotte_2016_spatial_source_inventory.py"
S=importlib.util.spec_from_file_location("ch2016_97",SRC)
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
KNOWNS=("6510","6540","7210","9113","9116","9121")

def audit(req=None):
    if req is None:req=M.request
    metas={y:req(url,{"f":"json"}) for y,url in M.CURRENT.items()}
    bb={k:(min(v["extent"][k] for v in metas.values()) if k in ("xmin","ymin")
           else max(v["extent"][k] for v in metas.values()))
        for k in ("xmin","ymin","xmax","ymax")}
    env=",".join(str(bb[k]) for k in ("xmin","ymin","xmax","ymax"))
    spatial={"geometry":env,"geometryType":"esriGeometryEnvelope",
             "inSR":3857,"spatialRel":"esriSpatialRelIntersects","f":"json"}
    count=req(M.HIST+"/query",{**spatial,"where":"1=1","returnCountOnly":"true"}).get("count")
    if not isinstance(count,int) or count<1:raise M.GateStop("BAD_SPATIAL_COUNT")
    opts={**spatial,"where":"1=1","returnGeometry":"false",
          "groupByFieldsForStatistics":"FLUCCS_CODE",
          "outStatistics":json.dumps([{"statisticType":"count","onStatisticField":"OBJECTID",
                                       "outStatisticFieldName":"n"}]),
          "orderByFields":"FLUCCS_CODE"}
    groups=req(M.HIST+"/query",opts)
    features=groups.get("features")
    if not isinstance(features,list) or groups.get("exceededTransferLimit"):
        raise M.GateStop("GROUPED_CODE_COUNTS_NOT_COMPLETE")
    counts={}
    for f in features:
        a=f.get("attributes",{})
        key=str(a.get("FLUCCS_CODE"))
        n=a.get("n")
        if key in counts or not isinstance(n,int) or n<0:
            raise M.GateStop("INVALID_GROUPED_CODE_RECORD")
        counts[key]=n
    if sum(counts.values())!=count:
        raise M.GateStop("GROUPED_CODE_COUNTS_DO_NOT_SUM_TO_SPATIAL_TOTAL")
    for k in KNOWNS:
        query_count=req(M.HIST+"/query",{**spatial,"where":"FLUCCS_CODE='"+k+"'",
                                           "returnCountOnly":"true"}).get("count")
        if not isinstance(query_count,int) or query_count!=counts.get(k,0):
            raise M.GateStop("EXPECTED_CLASS_COUNT_NOT_REPRODUCED:"+k)
    extra={k:v for k,v in counts.items() if k not in KNOWNS}
    return {
      "schema":"tampa.charlotte_2016_historical_code_dictionary_diagnostic_v1",
      "status":"PASS_CATEGORY_SOURCE_DIAGNOSTIC_ONLY",
      "source":M.HIST,
      "spatial_envelope_3857":bb,
      "all_class_feature_count":count,
      "category_counts":counts,
      "unmapped_to_known_six_classes":extra,
      "unrecognized_count":sum(extra.values()),
      "known_codes":list(KNOWNS),
      "source_class_metadata_only":True,
      "polygon_geometries_downloaded":False,
      "2016_2022_2024_transitions_computed":False,
      "unrecognized_classes_are_not_absence":True,
      "interpretation":"Class inventory only. Before analyzing 2016 history, unknown classes must be assigned a documented treatment, likely exclusion as other substrate, not silently seagrass or absence.",
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",required=True)
    x=a.parse_args()
    try:result=audit();rc=0
    except (M.GateStop,ValueError,TypeError) as e:
        result={"schema":"tampa.charlotte_2016_historical_code_dictionary_diagnostic_v1",
                "status":"STOP_CLASS_SOURCE_DIAGNOSTIC","reason":str(e),
                "2016_2022_2024_transitions_computed":False};rc=2
    p=Path(x.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return rc
if __name__=="__main__":sys.exit(main())
