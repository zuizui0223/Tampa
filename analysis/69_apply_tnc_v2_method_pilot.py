#!/usr/bin/env python3
"""Apply a PASS_METHOD_PILOT result to a copy of the TNC-v2 precollection freeze.

This is a transcription-safety bridge. It never chooses method values itself.
It copies only the six values already emitted by the response-independent
method-pilot validator, and refuses to run unless that validator passed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

KEYS=(
  "horizontal_rhizome_tissue_class",
  "minimum_perpendicular_transect_offset_m",
  "core_diameter_cm",
  "core_depth_cm",
  "maximum_collection_to_preservation_minutes",
  "preservation_method",
)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--validation",type=Path,required=True)
    ap.add_argument("--freeze",type=Path,default=Path("field/tnc_v2_precollection_freeze.json"))
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    v=json.loads(a.validation.read_text())
    if v.get("status")!="PASS_METHOD_PILOT":
        raise SystemExit(f"refuse to apply pilot: status={v.get('status')}")
    copy=v.get("copy_to_precollection_freeze")
    if not isinstance(copy,dict):
        raise SystemExit("PASS_METHOD_PILOT lacks copy_to_precollection_freeze")

    missing=[k for k in KEYS if copy.get(k) in (None,"","PENDING")]
    if missing:
        raise SystemExit(f"pilot copy payload incomplete: {missing}")

    freeze=json.loads(a.freeze.read_text())
    fields=freeze["fields_to_freeze_before_first_outcome_bearing_core"]

    # Fail closed if a human has already frozen a conflicting non-null value.
    conflicts={}
    for k in KEYS:
        old=fields.get(k)
        new=copy[k]
        if old not in (None,"","PENDING") and old!=new:
            conflicts[k]={"existing":old,"pilot":new}
    if conflicts:
        raise SystemExit("conflicting frozen method values: "+json.dumps(conflicts,sort_keys=True))

    for k in KEYS:
        fields[k]=copy[k]

    freeze["method_pilot_provenance"]={
      "validation_schema":v.get("schema"),
      "validation_status":v.get("status"),
      "source_pilot":v.get("pilot_source","field/tnc_v2_method_pilot.json"),
      "raw_pilot_provenance":v.get("raw_pilot_provenance"),
      "analytical_qc_count_freeze":v.get("analytical_qc_count_freeze"),
      "raw_hplc_counts":v.get("raw_hplc_counts"),
      "copied_keys":list(KEYS),
      "rule":"Values copied mechanically from PASS_METHOD_PILOT; no ecological outcome used."
    }

    remaining=[
      k for k,val in fields.items()
      if val in (None,"","PENDING")
    ]
    freeze["status"]=(
      "METHOD_PILOT_PASS_LOGISTICS_PENDING"
      if remaining else
      "FROZEN_BEFORE_FIRST_OUTCOME_BEARING_CORE"
    )

    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(freeze,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":freeze["status"],
      "copied":{k:fields[k] for k in KEYS},
      "remaining_unfrozen_fields":remaining
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
