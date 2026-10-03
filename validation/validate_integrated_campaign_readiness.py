#!/usr/bin/env python3
"""Fail-closed readiness audit for the integrated Tampa prospective campaign.

This script reads only prospective design/resource information. It does not read
TNC values or future meadow responses.

Without --strict, an incomplete freeze is reported as STOP and exits 0 so the
repository may retain a deliberately pending pre-field state.
With --strict, any status other than READY_CONFIRMATORY_CAMPAIGN exits non-zero.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

BAYS3=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
BAYS4=BAYS3+("Boca Ciega Bay",)

def node_set(x, bays, field, errors):
    if not isinstance(x,dict):
        errors.append(f"{field} must be an object keyed by bay")
        return set(),{}
    out=set(); by={}
    for b in bays:
        vals=x.get(b)
        if not isinstance(vals,list):
            errors.append(f"{field}[{b}] must be a list of frozen node IDs")
            vals=[]
        vals=[str(v) for v in vals]
        if len(vals)!=len(set(vals)):
            errors.append(f"{field}[{b}] contains duplicate node IDs")
        by[b]=set(vals)
        overlap=out & by[b]
        if overlap:
            errors.append(f"{field} repeats nodes across bays: {sorted(overlap)}")
        out |= by[b]
    extra=set(x)-set(bays)
    if extra:
        errors.append(f"{field} has unexpected bay keys: {sorted(extra)}")
    return out,by

def pending_paths(obj,prefix=""):
    out=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            out.extend(pending_paths(v,f"{prefix}.{k}" if prefix else k))
    elif obj is None or obj=="" or obj=="PENDING":
        out.append(prefix)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--freeze",default="field/integrated_campaign_resource_freeze.json")
    ap.add_argument("--contract",default="results/integrated_field_campaign_v1_contract.json")
    ap.add_argument("--out",default="results/integrated_campaign_readiness_v1.json")
    ap.add_argument("--strict",action="store_true")
    a=ap.parse_args()

    freeze=json.loads(Path(a.freeze).read_text())
    contract=json.loads(Path(a.contract).read_text())
    fields=freeze["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]
    pending=pending_paths(fields)

    result={
      "schema":"tampa.integrated_campaign_readiness_v1",
      "status":None,
      "pending_fields":pending,
      "errors":[],
      "calculated":{},
      "claim_boundary":[
        "Resource readiness is not ecological evidence.",
        "This audit does not read TNC or future meadow responses.",
        "A mechanism may be pilot/non-confirmatory while the authoritative TNC v2 campaign remains confirmatory."
      ]
    }

    if pending:
        result["status"]="STOP_RESOURCE_FREEZE_INCOMPLETE"
    else:
        errors=[]
        event,event_by=node_set(fields["final_core_three_event_nodes_by_bay"],BAYS3,"event_nodes",errors)
        optical,opt_by=node_set(fields["final_core_three_optical_nodes_by_bay"],BAYS3,"optical_nodes",errors)
        tnc,tnc_by=node_set(fields["final_four_bay_tnc_nodes_by_bay"],BAYS4,"tnc_nodes",errors)
        ref,ref_by=node_set(fields["optical_reference_nodes_by_bay"],BAYS3,"optical_reference_nodes",errors)

        # Frozen sampling gates.
        if len(event)<30: errors.append(f"event total {len(event)} < 30")
        for b in BAYS3:
            if len(event_by[b])<8: errors.append(f"event {b} {len(event_by[b])} < 8")

        if len(optical)<30: errors.append(f"optical total {len(optical)} < 30")
        for b in BAYS3:
            if len(opt_by[b])<8: errors.append(f"optical {b} {len(opt_by[b])} < 8")

        if len(tnc)<36: errors.append(f"TNC v2 total {len(tnc)} < 36")
        for b in BAYS4:
            if len(tnc_by[b])<6: errors.append(f"TNC v2 {b} {len(tnc_by[b])} < 6")

        if len(ref)<12: errors.append(f"optical reference total {len(ref)} < 12")
        for b in BAYS3:
            if len(ref_by[b])<3: errors.append(f"optical reference {b} {len(ref_by[b])} < 3")

        if not event <= tnc:
            errors.append(f"event nodes missing from TNC baseline registry: {sorted(event-tnc)}")
        if not optical <= tnc:
            errors.append(f"optical nodes missing from TNC baseline registry: {sorted(optical-tnc)}")
        if not ref <= optical:
            errors.append(f"optical reference nodes are not a subset of optical primary nodes: {sorted(ref-optical)}")

        temp_sys=int(fields["complete_temperature_salinity_node_systems_available"])
        within_par=int(fields["within_canopy_par_node_systems_available"])
        above_par=int(fields["above_canopy_par_reference_systems_available"])
        if temp_sys < len(event):
            errors.append(f"temperature/salinity systems {temp_sys} < event nodes {len(event)}")
        if within_par < len(optical):
            errors.append(f"within-canopy PAR systems {within_par} < optical nodes {len(optical)}")
        if above_par < len(ref):
            errors.append(f"above-canopy PAR reference systems {above_par} < reference nodes {len(ref)}")

        prepost=event | optical
        baseline_only=tnc-prepost
        min_cores=6*len(prepost)+3*len(baseline_only)
        preserve=int(fields["preservation_capacity_for_planned_core_samples"])
        if preserve < min_cores:
            errors.append(f"preservation capacity {preserve} < minimum planned TNC cores {min_cores}")

        for key in (
          "event_sensor_geometry_pilot_complete",
          "optical_vertical_profile_pilot_complete",
          "pre_post_core_offset_geometry_frozen",
        ):
            if fields[key] is not True:
                errors.append(f"{key} must be true")

        result["calculated"]={
          "event_nodes":len(event),
          "optical_nodes":len(optical),
          "tnc_v2_nodes":len(tnc),
          "optical_reference_nodes":len(ref),
          "prepost_tnc_union_nodes":len(prepost),
          "baseline_only_tnc_nodes":len(baseline_only),
          "minimum_outcome_bearing_tnc_cores_before_replacements":min_cores,
          "temperature_salinity_node_systems_available":temp_sys,
          "within_canopy_par_node_systems_available":within_par,
          "above_canopy_par_reference_systems_available":above_par,
          "preservation_capacity_for_planned_core_samples":preserve,
        }
        result["errors"]=errors
        result["status"]="READY_CONFIRMATORY_CAMPAIGN" if not errors else "STOP_RESOURCE_GATE_FAILED"

    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if a.strict and result["status"]!="READY_CONFIRMATORY_CAMPAIGN":
        raise SystemExit(2)

if __name__=="__main__":
    main()
