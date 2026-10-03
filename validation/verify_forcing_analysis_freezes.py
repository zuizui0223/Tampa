#!/usr/bin/env python3
"""Verify frozen event/optical/forcing-family analysis metadata."""
from __future__ import annotations
import json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def blob(path):
    return subprocess.check_output(["git","hash-object",str(ROOT/path)],text=True).strip()

evf=json.loads((ROOT/"field/event_stress_primary_analysis_freeze.json").read_text())
opf=json.loads((ROOT/"field/optical_primary_analysis_freeze.json").read_text())
fam=json.loads((ROOT/"field/forcing_family_analysis_freeze.json").read_text())
evc=json.loads((ROOT/"results/event_stress_debt_prospective_v1_contract.json").read_text())
opc=json.loads((ROOT/"results/optical_microenvironment_prospective_v1_contract.json").read_text())
res=json.loads((ROOT/"field/integrated_campaign_resource_freeze.json").read_text())
ff=res["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]

assert evf["status"]=="FROZEN_BEFORE_TNC_INSPECTION"
assert opf["status"]=="FROZEN_BEFORE_TNC_INSPECTION"
assert fam["status"]=="FROZEN_BEFORE_TNC_INSPECTION"
assert blob(evf["script_path"])==evf["script_blob_sha1"]
assert blob(opf["script_path"])==opf["script_blob_sha1"]
assert blob(fam["script_path"])==fam["script_blob_sha1"]
assert evf["uncertainty"]["repetitions"]==10000 and evf["uncertainty"]["seed"]==20261004
assert opf["uncertainty"]["repetitions"]==10000 and opf["uncertainty"]["seed"]==20261005
assert "97.5%" in evf["uncertainty"]["forcing_family_interval"]
assert "97.5%" in opf["uncertainty"]["forcing_family_interval"]
assert fam["multiplicity"].startswith("Bonferroni two-test")
assert "Do not compare" in fam["no_ranking"]
assert evc["primary_analysis"]["analysis_freeze"]=="field/event_stress_primary_analysis_freeze.json"
assert opc["primary_analysis"]["analysis_freeze"]=="field/optical_primary_analysis_freeze.json"
assert ff["event_primary_analysis_code_frozen"] is True
assert ff["optical_primary_analysis_code_frozen"] is True
assert ff["forcing_family_analysis_code_frozen"] is True

print("Tampa event/optical/forcing-family analysis freezes: OK")
