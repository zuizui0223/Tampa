#!/usr/bin/env python3
"""Apply PASS_OPTICAL_PILOT values to the optical pilot result freeze.

This script never chooses values. It copies only the payload emitted by
validation/validate_optical_method_pilot.py and refuses conflicts.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

KEYS=(
  "par_sensor_model",
  "reference_sensor_id_and_calibration_provenance",
  "sensor_specific_calibration_manifest",
  "all_outcome_bearing_channels_pass_calibration_gate",
  "selected_within_canopy_height_fraction",
  "vertical_profile_pilot_nodes",
  "vertical_profile_nodes_by_bay",
  "vertical_profile_median_absolute_relative_error",
  "vertical_profile_fraction_node_days_within_25pct",
  "vertical_profile_max_absolute_bay_median_relative_bias",
  "placement_repeatability_fraction_within_tolerance",
  "mounting_geometry_and_height_tolerance_rule",
  "maintenance_mode",
  "manual_service_interval_days",
  "fouling_median_absolute_relative_change",
  "fouling_p90_absolute_relative_change",
  "above_canopy_clearance_tolerance_rule",
  "pilot_artifact_or_manifest_digest",
)

def sha256(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--validation",type=Path,required=True)
    ap.add_argument("--freeze",type=Path,default=Path("field/optical_pilot_freeze.json"))
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    v=json.loads(a.validation.read_text())
    if v.get("status")!="PASS_OPTICAL_PILOT":
        raise SystemExit(f"refuse to apply optical pilot: status={v.get('status')}")
    copy=v.get("copy_to_optical_pilot_freeze")
    if not isinstance(copy,dict):
        raise SystemExit("PASS_OPTICAL_PILOT lacks copy_to_optical_pilot_freeze")
    missing=[k for k in KEYS if copy.get(k) in (None,"","PENDING")]
    if missing:
        raise SystemExit(f"optical pilot copy payload incomplete: {missing}")

    x=json.loads(a.freeze.read_text())
    fields=x["fields_to_freeze_before_optical_confirmatory_deployment"]
    conflicts={}
    for k in KEYS:
        old=fields.get(k)
        new=copy[k]
        if old not in (None,"","PENDING") and old!=new:
            conflicts[k]={"existing":old,"pilot":new}
    if conflicts:
        raise SystemExit("conflicting frozen optical-pilot values: "+json.dumps(conflicts,sort_keys=True))

    for k in KEYS:
        fields[k]=copy[k]

    x["method_pilot_provenance"]={
      "validation_schema":v.get("schema"),
      "validation_status":v.get("status"),
      "validation_file_sha256":sha256(a.validation),
      "candidate_source":v.get("pilot_source"),
      "candidate_sha256":v.get("pilot_candidate_sha256"),
      "raw_pilot_provenance":v.get("raw_pilot_provenance"),
      "source_artifact_manifest":v.get("source_artifact_manifest"),
      "copied_keys":list(KEYS),
      "rule":"Values copied mechanically from PASS_OPTICAL_PILOT; TNC/future response prohibited."
    }
    remaining=[k for k,val in fields.items() if val in (None,"","PENDING")]
    x["status"]="READY" if not remaining else "PILOT_PASS_FREEZE_INCOMPLETE"

    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":x["status"],
      "remaining_unfrozen_fields":remaining,
      "copied_keys":list(KEYS)
    },indent=2,sort_keys=True))

if __name__=="__main__": main()
