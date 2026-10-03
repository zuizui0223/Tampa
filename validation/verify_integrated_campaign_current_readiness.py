#!/usr/bin/env python3
"""Verify the committed current integrated-campaign readiness snapshot.

The canonical snapshot is logistics/design state only. Re-run the authoritative
readiness validator against the current freeze files and require exact agreement
on status and pending-field set.
"""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/"validation/validate_integrated_campaign_readiness.py"
CANON=ROOT/"results/integrated_campaign_readiness_v1.json"

canon=json.loads(CANON.read_text())
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/"readiness.json"
    cp=subprocess.run(
        [sys.executable,str(VALIDATOR),"--out",str(out)],
        cwd=ROOT,text=True,capture_output=True
    )
    if cp.returncode!=0:
        raise RuntimeError(f"readiness validator crashed\nSTDOUT={cp.stdout}\nSTDERR={cp.stderr}")
    current=json.loads(out.read_text())

assert canon["status"]==current["status"]=="STOP_RESOURCE_FREEZE_INCOMPLETE"
assert canon["pending_count"]==len(current["pending_fields"])
assert set(canon["pending_fields"])==set(current["pending_fields"])
assert canon["protected_primary"]["confirmatory_minimum_total"]==36
assert canon["protected_primary"]["confirmatory_minimum_per_bay"]==6
assert "No outcome-bearing field collection is authorized yet" in canon["current_decision"]

tnc_freeze=json.loads((ROOT/"field/tnc_v2_precollection_freeze.json").read_text())
batch_rule=tnc_freeze["fields_to_freeze_before_first_outcome_bearing_core"]["assay_batch_randomization_rule"]
assert "joint batch manifest" in batch_rule
assert "not perfectly confounded with HPLC batch" in batch_rule
assert "dynamic reserve-trajectory diagnostic is non-estimable" in batch_rule

print("Tampa current integrated readiness snapshot: OK")
