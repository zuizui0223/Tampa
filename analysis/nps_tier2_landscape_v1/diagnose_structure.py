#!/usr/bin/env python3
"""Diagnose row multiplicity in NPS Tier-2 CSV after parser failure.

No ecological trend is computed here. The goal is to determine what repeated
Event_Code x Quadrat_Ltr x Species rows represent before choosing any aggregation.
"""
from __future__ import annotations
import csv,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

HERE=Path(__file__).resolve().parent
C=json.loads((HERE/"analysis_contract.json").read_text())
OUT=HERE/"structure_diagnostic_result.json"

def cv(x):
    s=str(x).strip()
    if s==C["sample_semantics"]["missing_token"]: return None
    try: v=float(s)
    except: return "INVALID"
    return v

def main():
    req=Request(C["source"]["csv_url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier2-StructureDiag/1.0"})
    with urlopen(req,timeout=90) as r:
        data=r.read(20_000_001)
    rd=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    if rd.fieldnames!=C["source"]["expected_header"]: raise RuntimeError("header_drift")
    groups=defaultdict(list)
    id_seen=set(); duplicate_ids=[]
    for i,row in enumerate(rd,start=2):
        rid=str(row["QuadratData_ID"]).strip()
        if rid in id_seen: duplicate_ids.append(rid)
        id_seen.add(rid)
        key=(str(row["Event_Code"]).strip(),str(row["Quadrat_Ltr"]).strip(),str(row["Species"]).strip())
        groups[key].append({
          "row":i,"QuadratData_ID":rid,"cover":cv(row["Percent_Cover"]),
          "park":str(row["Park_Code"]).strip(),"hexagon":str(row["Hexagon"]).strip(),
          "station":str(row["Station"]).strip(),"date":str(row["Date"]).strip()
        })
    mult=Counter(len(v) for v in groups.values())
    repeated={k:v for k,v in groups.items() if len(v)>1}
    same_cover=0; different_cover=0; all_numeric=0; mixed_na=0
    examples=[]
    for k,v in sorted(repeated.items(), key=lambda kv:(-len(kv[1]),kv[0])):
        vals=[x["cover"] for x in v]
        numeric=[x for x in vals if isinstance(x,(int,float)) and math.isfinite(x)]
        if len(numeric)==len(vals):
            all_numeric+=1
            if len(set(numeric))==1: same_cover+=1
            else: different_cover+=1
        if any(x is None for x in vals) and numeric: mixed_na+=1
        if len(examples)<25:
            examples.append({"key":list(k),"rows":v})
    # Determine whether multiplicity is associated with distinct QuadratData_IDs.
    repeated_distinct_ids=sum(1 for v in repeated.values() if len({x["QuadratData_ID"] for x in v})==len(v))
    out={
      "schema":"tampa.nps_tier2_landscape_state_v1.structure_diagnostic",
      "csv_bytes":len(data),
      "row_count":sum(mult[k]*0 for k in []), 
      "unique_quadrat_data_ids":len(id_seen),
      "duplicate_quadrat_data_id_count":len(set(duplicate_ids)),
      "species_quadrat_group_count":len(groups),
      "multiplicity_distribution":{str(k):int(v) for k,v in sorted(mult.items())},
      "repeated_species_quadrat_group_count":len(repeated),
      "repeated_groups_all_numeric":all_numeric,
      "repeated_groups_same_numeric_cover":same_cover,
      "repeated_groups_different_numeric_cover":different_cover,
      "repeated_groups_mixed_numeric_and_na":mixed_na,
      "repeated_groups_with_distinct_quadrat_data_ids":repeated_distinct_ids,
      "examples":examples,
      "interpretation_rule":"No aggregation decision is made by this diagnostic."
    }
    # derive physical row count from total lengths
    out["row_count"]=int(sum(len(v) for v in groups.values()))
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
