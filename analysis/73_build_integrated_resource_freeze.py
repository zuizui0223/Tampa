#!/usr/bin/env python3
"""Build candidate integrated Tampa resource freezes from response-independent raw inputs.

This utility never overwrites authoritative freezes. It imports the already
validated four-bay TNC execution payload, combines it with a resource inventory
and a core-three forcing allocation/calendar manifest, and writes candidates
consumed by validate_integrated_campaign_readiness.py.

No TNC values or future ecological responses are permitted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

BAYS3=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
BAYS4=BAYS3+("Boca Ciega Bay",)
INTENTS={"confirmatory","disabled"}
TRUE={"true","1","yes","y"}
FALSE={"false","0","no","n",""}

REQUIRED_FORCING_COLUMNS=(
    "node_id","water_body","event_selected","optical_selected","optical_reference",
    "pre_visit_date","post_visit_date","logger_deployment_date","logger_retrieval_date",
)
FORBIDDEN_HEADER_TOKENS=("future","outcome","response","delta_frequency","next_year","tnc_value")

RESOURCE_TOP_KEYS={"schema","status","response_independent","module_intent","inventory","event_method","coring","secondary_optical_attribution","provenance"}
RESOURCE_SUBKEYS={
    "module_intent":{"event_stress","optical","optical_attribution"},
    "inventory":{
        "complete_temperature_salinity_node_systems_available",
        "within_canopy_par_node_systems_available",
        "above_canopy_par_reference_systems_available",
        "preservation_capacity_for_planned_core_samples",
        "hplc_primary_assay_capacity_for_planned_core_samples",
    },
    "event_method":{
        "temperature_salinity_sensor_model_and_calibration_rule",
        "event_sensor_geometry_pilot_complete",
    },
    "coring":{
        "pre_post_core_offset_geometry_frozen",
        "maximum_attempted_cores_per_node_across_pre_post_rounds",
        "minimum_pre_post_core_center_separation_cm",
        "maximum_cumulative_disturbed_area_cm2_per_node",
    },
    "secondary_optical_attribution":{"optical_attribution_analysis_code_frozen"},
    "provenance":{"inventory_date","prepared_by","equipment_inventory_source","field_access_or_permission_note"},
}

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path:Path):
    return json.loads(path.read_text())

def require_exact_object(obj,key,allowed,errors):
    x=obj.get(key)
    if not isinstance(x,dict):
        errors.append(f"{key} must be an object")
        return {}
    extra=set(x)-set(allowed)
    if extra:
        errors.append(f"{key} has unexpected keys: {sorted(extra)}")
    return x

def parse_bool(v,field,errors):
    s=str(v).strip().lower()
    if s in TRUE: return True
    if s in FALSE: return False
    errors.append(f"{field} must be boolean, got {v!r}")
    return False

def group_nodes(rows,key):
    by={b:[] for b in BAYS3}
    for r in rows:
        if r[key]:
            by[r["water_body"]].append(r["node_id"])
    return {b:sorted(v) for b,v in by.items()}

def selected_set(rows,key):
    return {r["node_id"] for r in rows if r[key]}

def date_payload(rows,nodes,col):
    return {r["node_id"]:r[col] for r in rows if r["node_id"] in nodes}

def validate_resource_inputs(x,errors):
    if x.get("schema")!="tampa.integrated_resource_inputs.v1":
        errors.append("resource input schema must be tampa.integrated_resource_inputs.v1")
    if x.get("response_independent") is not True:
        errors.append("resource inputs must explicitly set response_independent=true")
    extra=set(x)-RESOURCE_TOP_KEYS
    if extra:
        errors.append(f"resource inputs have unexpected top-level keys: {sorted(extra)}")
    objs={}
    for key,allowed in RESOURCE_SUBKEYS.items():
        objs[key]=require_exact_object(x,key,allowed,errors)

    intents=objs["module_intent"]
    for k in ("event_stress","optical","optical_attribution"):
        if intents.get(k) not in INTENTS:
            errors.append(f"module_intent.{k} must be confirmatory or disabled")
    if intents.get("optical")=="disabled" and intents.get("optical_attribution")=="confirmatory":
        errors.append("optical attribution cannot be confirmatory when optical primary is disabled")
    return objs

def read_forcing(path:Path,errors):
    with path.open(newline="") as f:
        r=csv.DictReader(f)
        cols=[c.strip() for c in (r.fieldnames or [])]
        bad=[c for c in cols if any(t in c.lower() for t in FORBIDDEN_HEADER_TOKENS)]
        if bad:
            errors.append(f"forcing manifest contains forbidden future/outcome columns: {bad}")
        miss=set(REQUIRED_FORCING_COLUMNS)-set(cols)
        if miss:
            errors.append(f"forcing manifest missing columns: {sorted(miss)}")
        extra=set(cols)-set(REQUIRED_FORCING_COLUMNS)
        if extra:
            errors.append(f"forcing manifest has unexpected columns: {sorted(extra)}")
        raw=list(r)

    rows=[]; seen=set()
    for i,row in enumerate(raw,2):
        node=row.get("node_id","").strip()
        bay=row.get("water_body","").strip()
        if not node:
            errors.append(f"forcing row {i}: blank node_id")
            continue
        if node in seen:
            errors.append(f"forcing manifest duplicate node_id: {node}")
        seen.add(node)
        if bay not in BAYS3:
            errors.append(f"{node}: forcing water_body must be one of core three bays")
            continue
        event=parse_bool(row.get("event_selected",""),f"{node}.event_selected",errors)
        optical=parse_bool(row.get("optical_selected",""),f"{node}.optical_selected",errors)
        ref=parse_bool(row.get("optical_reference",""),f"{node}.optical_reference",errors)
        if ref and not optical:
            errors.append(f"{node}: optical_reference=true requires optical_selected=true")
        d={k:row.get(k,"").strip() for k in REQUIRED_FORCING_COLUMNS}
        d.update({"node_id":node,"water_body":bay,"event_selected":event,"optical_selected":optical,"optical_reference":ref})
        if event or optical:
            for col in ("pre_visit_date","post_visit_date","logger_deployment_date","logger_retrieval_date"):
                if not d[col]:
                    errors.append(f"{node}: {col} required for selected forcing node")
        rows.append(d)
    return rows

def optical_rule(optical_freeze):
    if optical_freeze.get("status")!="READY":
        return None,False
    f=optical_freeze.get("fields_to_freeze_before_optical_confirmatory_deployment",{})
    model=f.get("par_sensor_model")
    manifest=f.get("sensor_specific_calibration_manifest")
    ok=f.get("all_outcome_bearing_channels_pass_calibration_gate") is True
    frac=f.get("selected_within_canopy_height_fraction")
    primary_class=f.get("primary_angular_response_class")
    reference_class=f.get("reference_angular_response_class")
    quantity_label=f.get("primary_light_quantity_reporting_label")
    if not (model and manifest and ok and frac is not None and primary_class and reference_class and quantity_label):
        return None,False
    if primary_class != reference_class:
        return None,False
    rule={
        "par_sensor_model":model,
        "primary_angular_response_class":primary_class,
        "reference_angular_response_class":reference_class,
        "primary_light_quantity_reporting_label":quantity_label,
        "sensor_specific_calibration_manifest":manifest,
        "selected_within_canopy_height_fraction":frac,
        "method_pilot_digest":f.get("pilot_artifact_or_manifest_digest"),
    }
    return json.dumps(rule,sort_keys=True),True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--resource-inputs",type=Path,required=True)
    ap.add_argument("--forcing-manifest",type=Path,required=True)
    ap.add_argument("--tnc-execution",type=Path,required=True)
    ap.add_argument("--resource-base",type=Path,default=Path("field/integrated_campaign_resource_freeze.json"))
    ap.add_argument("--tnc-base",type=Path,default=Path("field/tnc_v2_precollection_freeze.json"))
    ap.add_argument("--optical-freeze",type=Path,default=Path("field/optical_pilot_freeze.json"))
    ap.add_argument("--resource-out",type=Path,required=True)
    ap.add_argument("--tnc-out",type=Path,required=True)
    a=ap.parse_args()

    errors=[]
    inputs=load_json(a.resource_inputs)
    objs=validate_resource_inputs(inputs,errors)
    rows=read_forcing(a.forcing_manifest,errors)
    tnc_exec=load_json(a.tnc_execution)
    resource_base=load_json(a.resource_base)
    tnc_base=load_json(a.tnc_base)
    optical_freeze=load_json(a.optical_freeze)

    if tnc_exec.get("status")!="PASS_EXECUTION_MANIFEST":
        errors.append("TNC execution manifest must have status PASS_EXECUTION_MANIFEST")
    if tnc_exec.get("response_independent") is not True:
        errors.append("TNC execution manifest must be response_independent")
    payload=tnc_exec.get("resource_freeze_payload")
    if not isinstance(payload,dict):
        errors.append("TNC execution manifest lacks resource_freeze_payload")
        payload={}

    tnc_by=payload.get("final_four_bay_tnc_nodes_by_bay") or {}
    tnc_nodes={str(n) for b in BAYS4 for n in tnc_by.get(b,[])}
    for r in rows:
        if (r["event_selected"] or r["optical_selected"]) and r["node_id"] not in tnc_nodes:
            errors.append(f"{r['node_id']}: selected forcing node is absent from TNC-v2 registry")

    intents=objs.get("module_intent",{})
    event_intent=intents.get("event_stress")
    optical_intent=intents.get("optical")
    attr_intent=intents.get("optical_attribution")
    event_nodes=selected_set(rows,"event_selected")
    optical_nodes=selected_set(rows,"optical_selected")
    ref_nodes=selected_set(rows,"optical_reference")
    prepost=event_nodes|optical_nodes

    if event_intent=="disabled" and event_nodes:
        errors.append("event module is disabled but forcing manifest selects event nodes")
    if optical_intent=="disabled" and optical_nodes:
        errors.append("optical module is disabled but forcing manifest selects optical nodes")
    if attr_intent=="disabled" and ref_nodes:
        errors.append("optical attribution is disabled but forcing manifest selects reference nodes")
    if attr_intent=="confirmatory" and not ref_nodes:
        errors.append("optical attribution is confirmatory but no reference nodes are selected")

    if errors:
        raise SystemExit("\n".join(errors))

    resource=deepcopy(resource_base)
    rf=resource["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]
    resource["status"]="CANDIDATE_FROM_RESPONSE_INDEPENDENT_RAW_INPUTS"

    # Protected four-bay TNC registry and calendars come only from the validated execution manifest.
    for k in ("final_four_bay_tnc_nodes_by_bay","four_bay_authoritative_tnc_baseline_calendar","four_bay_baseline_transect_calendar"):
        rf[k]=payload[k]

    rf["event_module_intent"]=event_intent
    rf["optical_module_intent"]=optical_intent
    rf["optical_attribution_intent"]=attr_intent

    inv=objs["inventory"]
    rf["preservation_capacity_for_planned_core_samples"]=inv.get("preservation_capacity_for_planned_core_samples")
    rf["hplc_primary_assay_capacity_for_planned_core_samples"]=inv.get("hplc_primary_assay_capacity_for_planned_core_samples")

    # Optional forcing registries.
    rf["final_core_three_event_nodes_by_bay"]=group_nodes(rows,"event_selected") if event_intent=="confirmatory" else None
    rf["final_core_three_optical_nodes_by_bay"]=group_nodes(rows,"optical_selected") if optical_intent=="confirmatory" else None
    rf["optical_reference_nodes_by_bay"]=group_nodes(rows,"optical_reference") if attr_intent=="confirmatory" else None

    rf["complete_temperature_salinity_node_systems_available"]=inv.get("complete_temperature_salinity_node_systems_available") if event_intent=="confirmatory" else None
    rf["within_canopy_par_node_systems_available"]=inv.get("within_canopy_par_node_systems_available") if optical_intent=="confirmatory" else None
    rf["above_canopy_par_reference_systems_available"]=inv.get("above_canopy_par_reference_systems_available") if attr_intent=="confirmatory" else None

    ev=objs["event_method"]
    rf["temperature_salinity_sensor_model_and_calibration_rule"]=ev.get("temperature_salinity_sensor_model_and_calibration_rule") if event_intent=="confirmatory" else None
    rf["event_sensor_geometry_pilot_complete"]=ev.get("event_sensor_geometry_pilot_complete") if event_intent=="confirmatory" else None

    par_rule,optical_ready=optical_rule(optical_freeze)
    rf["par_sensor_model_and_calibration_rule"]=par_rule if optical_intent=="confirmatory" else None
    rf["optical_vertical_profile_pilot_complete"]=True if optical_intent=="confirmatory" and optical_ready else None

    cor=objs["coring"]
    if prepost:
        rf["pre_post_core_offset_geometry_frozen"]=cor.get("pre_post_core_offset_geometry_frozen")
        rf["maximum_attempted_cores_per_node_across_pre_post_rounds"]=cor.get("maximum_attempted_cores_per_node_across_pre_post_rounds")
        rf["minimum_pre_post_core_center_separation_cm"]=cor.get("minimum_pre_post_core_center_separation_cm")
        rf["maximum_cumulative_disturbed_area_cm2_per_node"]=cor.get("maximum_cumulative_disturbed_area_cm2_per_node")
        rf["core_three_pre_visit_route_calendar"]=date_payload(rows,prepost,"pre_visit_date")
        rf["core_three_post_visit_route_calendar"]=date_payload(rows,prepost,"post_visit_date")
        rf["core_three_logger_deployment_calendar"]=date_payload(rows,prepost,"logger_deployment_date")
        rf["core_three_logger_retrieval_calendar"]=date_payload(rows,prepost,"logger_retrieval_date")
    else:
        for k in (
            "pre_post_core_offset_geometry_frozen",
            "maximum_attempted_cores_per_node_across_pre_post_rounds",
            "minimum_pre_post_core_center_separation_cm",
            "maximum_cumulative_disturbed_area_cm2_per_node",
            "core_three_pre_visit_route_calendar",
            "core_three_post_visit_route_calendar",
            "core_three_logger_deployment_calendar",
            "core_three_logger_retrieval_calendar",
        ):
            rf[k]=None

    sec=objs["secondary_optical_attribution"]
    rf["optical_attribution_analysis_code_frozen"]=sec.get("optical_attribution_analysis_code_frozen") if attr_intent=="confirmatory" else None

    # Existing authoritative code-freeze booleans are preserved from the base resource skeleton.
    tnc=deepcopy(tnc_base)
    tnc["status"]="CANDIDATE_WITH_EXECUTION_CALENDAR"
    tf=tnc["fields_to_freeze_before_first_outcome_bearing_core"]
    tf["campaign_start_date"]=payload.get("tnc_v2_precollection_campaign_start_date")
    tf["campaign_end_date"]=payload.get("tnc_v2_precollection_campaign_end_date")

    provenance={
        "builder":"analysis/73_build_integrated_resource_freeze.py",
        "response_independent":True,
        "inputs":{
            "resource_inputs":{"path":str(a.resource_inputs),"sha256":sha256(a.resource_inputs)},
            "forcing_manifest":{"path":str(a.forcing_manifest),"sha256":sha256(a.forcing_manifest)},
            "tnc_execution":{"path":str(a.tnc_execution),"sha256":sha256(a.tnc_execution)},
            "resource_base":{"path":str(a.resource_base),"sha256":sha256(a.resource_base)},
            "tnc_base":{"path":str(a.tnc_base),"sha256":sha256(a.tnc_base)},
            "optical_freeze":{"path":str(a.optical_freeze),"sha256":sha256(a.optical_freeze)},
        },
        "module_intent":intents,
        "selected_counts":{
            "tnc_v2":len(tnc_nodes),
            "event":len(event_nodes),
            "optical":len(optical_nodes),
            "optical_reference":len(ref_nodes),
            "prepost_union":len(prepost),
        },
    }
    resource["build_provenance"]=provenance
    tnc["execution_build_provenance"]=provenance

    for out,obj in ((a.resource_out,resource),(a.tnc_out,tnc)):
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")

    print(json.dumps({
        "status":"CANDIDATES_WRITTEN",
        "resource_out":str(a.resource_out),
        "tnc_out":str(a.tnc_out),
        "selected_counts":provenance["selected_counts"],
        "module_intent":intents,
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
