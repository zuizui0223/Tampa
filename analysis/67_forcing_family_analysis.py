#!/usr/bin/env python3
"""Frozen paper-level two-test forcing-family summary for Tampa.

This script does not refit either mechanism. It consumes the separately frozen
event-stress and optical primary-analysis outputs and applies the predeclared
Bonferroni family rule using each member's two-sided 97.5% interval.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--event",required=True)
    ap.add_argument("--optical",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    ev=json.loads(Path(a.event).read_text())
    op=json.loads(Path(a.optical).read_text())

    errors=[]
    if ev.get("schema")!="tampa.event_stress_primary_analysis.v1":
        errors.append("unexpected event analysis schema")
    if op.get("schema")!="tampa.optical_primary_analysis.v1":
        errors.append("unexpected optical analysis schema")

    ev_estimable=ev.get("interpretation_status")!="nonestimable_or_pilot_gate_failed"
    op_estimable=op.get("interpretation_status")!="nonestimable_or_pilot_gate_failed"

    ev_ci=ev.get("family_level_ci97_5")
    op_ci=op.get("family_level_ci97_5")
    if not (isinstance(ev_ci,list) and len(ev_ci)==2): errors.append("event 97.5% CI missing")
    if not (isinstance(op_ci,list) and len(op_ci)==2): errors.append("optical 97.5% CI missing")

    members={}
    if not errors:
        ev_corr=bool(ev_estimable and float(ev_ci[1])<0)
        op_corr=bool(op_estimable and float(op_ci[0])>0)
        members={
          "event_stress":{
            "direction":"negative",
            "estimable":ev_estimable,
            "ci97_5":[float(ev_ci[0]),float(ev_ci[1])],
            "family_corrected_supported":ev_corr,
          },
          "optical":{
            "direction":"positive",
            "estimable":op_estimable,
            "ci97_5":[float(op_ci[0]),float(op_ci[1])],
            "family_corrected_supported":op_corr,
          }
        }
        status=(
          "FAMILY_NOT_JOINTLY_ESTIMABLE"
          if not (ev_estimable and op_estimable)
          else "FAMILY_CORRECTED_SUPPORT_PRESENT"
          if (ev_corr or op_corr)
          else "NO_MEMBER_PASSES_FAMILY_CORRECTION"
        )
    else:
        status="STOP_INVALID_MEMBER_OUTPUT"

    result={
      "schema":"tampa.forcing_family_analysis.v1",
      "status":status,
      "family":"event-stress + optical reserve-forcing primaries",
      "multiplicity":"Bonferroni two-test family; each member evaluated with two-sided 97.5% interval",
      "members":members,
      "errors":errors,
      "interpretation":[
        "Standalone event and optical 95% contract statuses remain unchanged.",
        "A family-corrected supported member may contribute to a paper-level statement that measured environmental forcing predicts reserve change.",
        "Do not rank event versus optical effects by coefficient, p-value or interval width.",
        "Because both tests share nodes, weather interval and TNC response, corrected support does not establish statistically independent causal effects.",
        "If either primary is non-estimable/pilot-only, do not make a joint confirmatory forcing-family claim."
      ]
    }
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
