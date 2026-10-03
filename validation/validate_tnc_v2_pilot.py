#!/usr/bin/env python3
"""DEPRECATED legacy TNC-v2 pilot validator.

This earlier single-manifest pipeline is superseded by the authoritative
raw-record method-pilot pipeline:

  validation/build_tnc_v2_method_pilot_summary.py
    -> field/tnc_v2_method_pilot_candidate.json
    -> validation/validate_tnc_v2_method_pilot.py
    -> analysis/69_apply_tnc_v2_method_pilot.py

The canonical raw inputs are:
  field/tnc_v2_raw_pilot_metadata.json
  field/tnc_v2_hplc_matrix_pilot.json
  field/tnc_v2_tissue_class_pilot.csv
  field/tnc_v2_core_geometry_pilot.csv
  field/tnc_v2_offset_pilot.csv
  field/tnc_v2_preservation_pilot.csv

Do not use field/tnc_v2_pilot_freeze.json or field/tnc_v2_pilot_manifest.csv
for outcome-bearing protocol decisions.
"""
raise SystemExit(
    "DEPRECATED: run validation/build_tnc_v2_method_pilot_summary.py, then "
    "validation/validate_tnc_v2_method_pilot.py"
)
