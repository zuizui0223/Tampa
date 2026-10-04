#!/usr/bin/env python3
"""Fail-closed readiness audit for the integrated Tampa prospective campaign.

This audit reads design/resource files only. It never reads TNC values or
future meadow responses.

Key logic:
- four-bay TNC v2 is the protected decisive outcome-bearing primary;
- event and optical modules must be frozen as confirmatory or disabled;
- disabled optional modules do not trigger destructive pre/post TNC sampling;
- paired above-canopy PAR is secondary attribution and can be disabled while
  the optical primary remains confirmatory;
- node-level calendars are checked against the frozen exposure/TNC windows.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path

BAYS3=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
BAYS4=BAYS3+("Boca Ciega Bay",)
INTENTS={"confirmatory","disabled"}

def parse_date(v, field, errors):
    if not isinstance(v,str) or not v.strip():
        errors.append(f"{field} must be YYYY-MM-DD")
        return None
    try:
        return dt.date.fromisoformat(v.strip())
    except Exception:
        errors.append(f"{field} is not ISO date: {v!r}")
        return None

def node_set(x,bays,field,errors,allow_null=False):
    if x is None and allow_null:
        return set(),{b:set() for b in bays}
    if not isinstance(x,dict):
        errors.append(f"{field} must be an object keyed by bay")
        return set(),{b:set() for b in bays}
    out=set(); by={}
    for b in bays:
        vals=x.get(b)
        if not isinstance(vals,list):
            errors.append(f"{field}[{b}] must be a list")
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

def date_map(x, expected_nodes, field, errors):
    if not isinstance(x,dict):
        errors.append(f"{field} must be an object node_id -> YYYY-MM-DD")
        return {}
    keys={str(k) for k in x}
    miss=expected_nodes-keys
    extra=keys-expected_nodes
    if miss: errors.append(f"{field} missing nodes: {sorted(miss)}")
    if extra: errors.append(f"{field} has unexpected nodes: {sorted(extra)}")
    out={}
    for k,v in x.items():
        d=parse_date(v,f"{field}[{k}]",errors)
        if d is not None: out[str(k)]=d
    return out

def bool_true(v,field,errors):
    if v is not True:
        errors.append(f"{field} must be true before outcome-bearing deployment")

def pending_tnc_freeze(tnc_freeze):
    fields=tnc_freeze.get("fields_to_freeze_before_first_outcome_bearing_core",{})
    return [k for k,v in fields.items() if v in (None,"","PENDING")]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--freeze",default="field/integrated_campaign_resource_freeze.json")
    ap.add_argument("--contract",default="results/integrated_field_campaign_v1_contract.json")
    ap.add_argument("--tnc-freeze",default="field/tnc_v2_precollection_freeze.json")
    ap.add_argument("--optical-pilot-freeze",default="field/optical_pilot_freeze.json")
    ap.add_argument("--out",default="results/integrated_campaign_readiness_v1.json")
    ap.add_argument("--strict",action="store_true")
    a=ap.parse_args()

    freeze=json.loads(Path(a.freeze).read_text())
    contract=json.loads(Path(a.contract).read_text())
    tnc_freeze=json.loads(Path(a.tnc_freeze).read_text())
    optical_pilot_freeze=json.loads(Path(a.optical_pilot_freeze).read_text())
    fields=freeze["fields_to_freeze_before_first_outcome_bearing_pre_tnc_core_or_logger"]

    errors=[]
    notes=[]
    calculated={}

    # Deliberately incomplete pre-field freezes are a valid repository state:
    # report STOP_RESOURCE_FREEZE_INCOMPLETE without pretending the design failed.
    tnc_pending=pending_tnc_freeze(tnc_freeze)
    unconditional=[
        "event_module_intent",
        "optical_module_intent",
        "optical_attribution_intent",
        "final_four_bay_tnc_nodes_by_bay",
        "tnc_v2_primary_analysis_code_frozen",
        "node_level_uncertainty_code_frozen",
        "preservation_capacity_for_planned_core_samples",
        "hplc_primary_assay_capacity_for_planned_core_samples",
        "four_bay_baseline_transect_calendar",
        "four_bay_authoritative_tnc_baseline_calendar",
    ]
    pending=[k for k in unconditional if fields.get(k) in (None,"","PENDING")]

    event_intent=fields.get("event_module_intent")
    optical_intent=fields.get("optical_module_intent")
    attr_intent=fields.get("optical_attribution_intent")

    if event_intent=="confirmatory":
        for k in (
            "final_core_three_event_nodes_by_bay",
            "complete_temperature_salinity_node_systems_available",
            "temperature_salinity_sensor_model_and_calibration_rule",
            "event_sensor_geometry_pilot_complete",
            "event_primary_analysis_code_frozen",
            "pre_post_core_offset_geometry_frozen",
            "maximum_attempted_cores_per_node_across_pre_post_rounds",
            "maximum_cumulative_disturbed_area_cm2_per_node",
            "minimum_pre_post_core_center_separation_cm",
            "core_three_pre_visit_route_calendar",
            "core_three_post_visit_route_calendar",
            "core_three_logger_deployment_calendar",
            "core_three_logger_retrieval_calendar",
        ):
            if fields.get(k) in (None,"","PENDING"): pending.append(k)
    if optical_intent=="confirmatory":
        if optical_pilot_freeze.get("status")!="READY":
            pending.append("optical_pilot_freeze.READY")
        for k in (
            "final_core_three_optical_nodes_by_bay",
            "within_canopy_par_node_systems_available",
            "par_sensor_model_and_calibration_rule",
            "optical_vertical_profile_pilot_complete",
            "optical_primary_analysis_code_frozen",
            "pre_post_core_offset_geometry_frozen",
            "maximum_attempted_cores_per_node_across_pre_post_rounds",
            "maximum_cumulative_disturbed_area_cm2_per_node",
            "minimum_pre_post_core_center_separation_cm",
            "core_three_pre_visit_route_calendar",
            "core_three_post_visit_route_calendar",
            "core_three_logger_deployment_calendar",
            "core_three_logger_retrieval_calendar",
        ):
            if fields.get(k) in (None,"","PENDING"): pending.append(k)
    if attr_intent=="confirmatory":
        for k in (
            "optical_reference_nodes_by_bay",
            "above_canopy_par_reference_systems_available",
            "optical_attribution_analysis_code_frozen",
        ):
            if fields.get(k) in (None,"","PENDING"): pending.append(k)
    if event_intent=="confirmatory" and optical_intent=="confirmatory":
        if fields.get("forcing_family_analysis_code_frozen") in (None,"","PENDING"):
            pending.append("forcing_family_analysis_code_frozen")

    pending=sorted(set(pending))
    if tnc_pending:
        pending.extend("tnc_v2_precollection."+k for k in sorted(tnc_pending))
    if pending:
        result={
          "schema":"tampa.integrated_campaign_readiness_v2",
          "status":"STOP_RESOURCE_FREEZE_INCOMPLETE",
          "pending_fields":pending,
          "module_status":{
            "tnc_v2":"PENDING",
            "event_stress":"PENDING" if event_intent is None else event_intent.upper(),
            "optical":"PENDING" if optical_intent is None else optical_intent.upper(),
            "optical_attribution":"PENDING" if attr_intent is None else attr_intent.upper(),
          },
          "errors":[],
          "notes":["No outcome-bearing collection is authorized while this freeze is incomplete."],
          "calculated":{},
          "claim_boundary":[
            "Resource readiness is not ecological evidence.",
            "This audit does not read TNC values or future meadow responses.",
            "A pending fail-closed state is expected before response-independent logistics/pilots are frozen."
          ]
        }
        out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps(result,indent=2,sort_keys=True))
        if a.strict:
            raise SystemExit(2)
        return

    # Authoritative TNC precollection system is mandatory.
    if tnc_freeze.get("contract")!="results/clonal_state_prospective_v2_contract.json":
        errors.append("TNC-v2 precollection freeze does not point to authoritative v2 contract")

    # Freeze mechanism intent before sampling.
    event_intent=fields.get("event_module_intent")
    optical_intent=fields.get("optical_module_intent")
    attr_intent=fields.get("optical_attribution_intent")
    for name,val in (
        ("event_module_intent",event_intent),
        ("optical_module_intent",optical_intent),
        ("optical_attribution_intent",attr_intent),
    ):
        if val not in INTENTS:
            errors.append(f"{name} must be one of {sorted(INTENTS)}, got {val!r}")
    if optical_intent=="disabled" and attr_intent=="confirmatory":
        errors.append("optical attribution cannot be confirmatory when optical primary is disabled")

    # TNC-v2 registry is always required.
    tnc,tnc_by=node_set(fields.get("final_four_bay_tnc_nodes_by_bay"),BAYS4,"tnc_nodes",errors)
    if len(tnc)<36: errors.append(f"TNC v2 total {len(tnc)} < 36")
    for b in BAYS4:
        if len(tnc_by[b])<6: errors.append(f"TNC v2 {b} {len(tnc_by[b])} < 6")

    bool_true(fields.get("tnc_v2_primary_analysis_code_frozen"),"tnc_v2_primary_analysis_code_frozen",errors)
    bool_true(fields.get("node_level_uncertainty_code_frozen"),"node_level_uncertainty_code_frozen",errors)

    # Authoritative four-bay baseline calendars are mandatory.
    tnc_cal=date_map(fields.get("four_bay_authoritative_tnc_baseline_calendar"),tnc,
                     "four_bay_authoritative_tnc_baseline_calendar",errors)
    baseline_cal=date_map(fields.get("four_bay_baseline_transect_calendar"),tnc,
                          "four_bay_baseline_transect_calendar",errors)

    if tnc_cal:
        span=(max(tnc_cal.values())-min(tnc_cal.values())).days
        calculated["authoritative_tnc_baseline_span_days"]=span
        if span>28:
            errors.append(f"authoritative four-bay TNC baseline span {span} d > 28 d")
    for node in sorted(tnc & set(tnc_cal) & set(baseline_cal)):
        dd=abs((tnc_cal[node]-baseline_cal[node]).days)
        if dd>14:
            errors.append(f"{node}: fixed-transect baseline is {dd} d from authoritative TNC baseline (>14)")

    # Integrated TNC dates must also lie inside the independent v2 precollection campaign.
    if not tnc_pending:
        tf=tnc_freeze["fields_to_freeze_before_first_outcome_bearing_core"]
        ts=parse_date(tf.get("campaign_start_date"),"tnc_v2 campaign_start_date",errors)
        te=parse_date(tf.get("campaign_end_date"),"tnc_v2 campaign_end_date",errors)
        if ts and te:
            if te<ts: errors.append("TNC-v2 campaign end precedes start")
            if (te-ts).days>28: errors.append("TNC-v2 frozen campaign exceeds 28 days")
            for node,d in tnc_cal.items():
                if d<ts or d>te:
                    errors.append(f"{node}: authoritative TNC baseline date {d} outside TNC-v2 frozen campaign {ts}..{te}")

    # Optional module registries.
    event,event_by=node_set(fields.get("final_core_three_event_nodes_by_bay"),BAYS3,
                            "event_nodes",errors,allow_null=(event_intent=="disabled"))
    optical,opt_by=node_set(fields.get("final_core_three_optical_nodes_by_bay"),BAYS3,
                            "optical_nodes",errors,allow_null=(optical_intent=="disabled"))

    if event_intent=="confirmatory":
        if len(event)<30: errors.append(f"event total {len(event)} < 30")
        for b in BAYS3:
            if len(event_by[b])<8: errors.append(f"event {b} {len(event_by[b])} < 8")
        if not event<=tnc: errors.append(f"event nodes missing from TNC-v2 registry: {sorted(event-tnc)}")
        bool_true(fields.get("event_sensor_geometry_pilot_complete"),"event_sensor_geometry_pilot_complete",errors)
        bool_true(fields.get("event_primary_analysis_code_frozen"),"event_primary_analysis_code_frozen",errors)
        try:
            temp_sys=int(fields.get("complete_temperature_salinity_node_systems_available"))
            if temp_sys<len(event): errors.append(f"temperature/salinity systems {temp_sys} < event nodes {len(event)}")
        except Exception:
            errors.append("complete_temperature_salinity_node_systems_available must be integer when event is confirmatory")
    else:
        notes.append("event-stress outcome-bearing module disabled; no event-specific pre/post TNC is authorized")

    if optical_intent=="confirmatory":
        if optical_pilot_freeze.get("contract")!="results/optical_pilot_acceptance_v1_contract.json":
            errors.append("optical pilot freeze does not point to frozen optical acceptance contract")
        if optical_pilot_freeze.get("status")!="READY":
            errors.append("optical pilot freeze is not READY")
        opp=optical_pilot_freeze.get("method_pilot_provenance",{})
        if opp.get("validation_status")!="PASS_OPTICAL_PILOT":
            errors.append("optical pilot freeze lacks PASS_OPTICAL_PILOT provenance")
        if not opp.get("candidate_sha256") or not opp.get("raw_pilot_provenance"):
            errors.append("optical pilot freeze lacks raw-pilot provenance/digest")
        opf=optical_pilot_freeze.get("fields_to_freeze_before_optical_confirmatory_deployment",{})
        clearance=opf.get("above_canopy_clearance_tolerance_rule")
        if attr_intent=="confirmatory" and clearance=="NOT_APPLICABLE_ATTRIBUTION_DISABLED":
            errors.append("optical attribution is confirmatory but optical pilot freeze marks above-canopy clearance not applicable")
        if len(optical)<30: errors.append(f"optical total {len(optical)} < 30")
        for b in BAYS3:
            if len(opt_by[b])<8: errors.append(f"optical {b} {len(opt_by[b])} < 8")
        if not optical<=tnc: errors.append(f"optical nodes missing from TNC-v2 registry: {sorted(optical-tnc)}")
        bool_true(fields.get("optical_vertical_profile_pilot_complete"),"optical_vertical_profile_pilot_complete",errors)
        bool_true(fields.get("optical_primary_analysis_code_frozen"),"optical_primary_analysis_code_frozen",errors)
        try:
            n=int(fields.get("within_canopy_par_node_systems_available"))
            if n<len(optical): errors.append(f"within-canopy PAR systems {n} < optical nodes {len(optical)}")
        except Exception:
            errors.append("within_canopy_par_node_systems_available must be integer when optical is confirmatory")
    else:
        notes.append("optical outcome-bearing module disabled; no optical-specific pre/post TNC is authorized")

    # Secondary optical attribution never blocks the optical primary.
    ref,ref_by=node_set(fields.get("optical_reference_nodes_by_bay"),BAYS3,
                        "optical_reference_nodes",errors,allow_null=(attr_intent=="disabled"))
    optical_attribution_status="DISABLED"
    if attr_intent=="confirmatory":
        if optical_intent!="confirmatory":
            errors.append("optical attribution requires confirmatory optical primary")
        if not ref<=optical:
            errors.append(f"optical reference nodes not subset of optical primary: {sorted(ref-optical)}")
        if len(ref)<12:
            errors.append(f"optical reference total {len(ref)} < 12 while attribution is labeled confirmatory")
        for b in BAYS3:
            if len(ref_by[b])<3:
                errors.append(f"optical reference {b} {len(ref_by[b])} < 3 while attribution is confirmatory")
        try:
            n=int(fields.get("above_canopy_par_reference_systems_available"))
            if n<len(ref): errors.append(f"above-canopy PAR systems {n} < reference nodes {len(ref)}")
        except Exception:
            errors.append("above_canopy_par_reference_systems_available must be integer when attribution is confirmatory")
        bool_true(fields.get("optical_attribution_analysis_code_frozen"),"optical_attribution_analysis_code_frozen",errors)
        optical_attribution_status="CONFIRMATORY" if not any("optical reference" in e or "above-canopy" in e for e in errors) else "STOP"
    else:
        notes.append("paired above-canopy attribution disabled; this does not invalidate a confirmatory optical primary")

    # If both environmental forcing modules are confirmatory, freeze family-level code.
    if event_intent=="confirmatory" and optical_intent=="confirmatory":
        bool_true(fields.get("forcing_family_analysis_code_frozen"),"forcing_family_analysis_code_frozen",errors)

    # Shared pre/post sampling applies only to confirmatory event/optical nodes.
    prepost=event|optical
    if prepost:
        bool_true(fields.get("pre_post_core_offset_geometry_frozen"),"pre_post_core_offset_geometry_frozen",errors)
        try:
            max_attempt=int(fields.get("maximum_attempted_cores_per_node_across_pre_post_rounds"))
            if max_attempt<6:
                errors.append("maximum_attempted_cores_per_node_across_pre_post_rounds must be >=6")
        except Exception:
            max_attempt=None
            errors.append("maximum_attempted_cores_per_node_across_pre_post_rounds must be integer")

        try:
            sep=float(fields.get("minimum_pre_post_core_center_separation_cm"))
            max_area=float(fields.get("maximum_cumulative_disturbed_area_cm2_per_node"))
            frozen_d=float(tnc_freeze["fields_to_freeze_before_first_outcome_bearing_core"]["core_diameter_cm"])
            if sep < frozen_d:
                errors.append(
                    f"minimum pre/post core-center separation {sep} cm < frozen core diameter {frozen_d} cm; core footprints could overlap"
                )
            if max_attempt is not None:
                import math
                implied=max_attempt*math.pi*(frozen_d/2.0)**2
                if max_area+1e-9 < implied:
                    errors.append(
                        f"maximum cumulative disturbed area {max_area:.2f} cm2 < area implied by {max_attempt} attempted {frozen_d} cm cores ({implied:.2f} cm2)"
                    )
            calculated["minimum_pre_post_core_center_separation_cm"]=sep
            calculated["maximum_cumulative_disturbed_area_cm2_per_node"]=max_area
        except Exception:
            errors.append("pre/post core separation and cumulative disturbed area must be numeric and consistent with frozen TNC core diameter")

        deploy=date_map(fields.get("core_three_logger_deployment_calendar"),prepost,
                        "core_three_logger_deployment_calendar",errors)
        retrieve=date_map(fields.get("core_three_logger_retrieval_calendar"),prepost,
                          "core_three_logger_retrieval_calendar",errors)
        pre=date_map(fields.get("core_three_pre_visit_route_calendar"),prepost,
                     "core_three_pre_visit_route_calendar",errors)
        post=date_map(fields.get("core_three_post_visit_route_calendar"),prepost,
                      "core_three_post_visit_route_calendar",errors)

        start0=dt.date(2001,7,24); end0=dt.date(2001,9,3)
        # Compare by month/day on a common non-leap template year.
        def md2001(d):
            return dt.date(2001,d.month,d.day)

        for node in sorted(prepost & set(deploy) & set(retrieve) & set(pre) & set(post)):
            ds,dr,dp,dq=deploy[node],retrieve[node],pre[node],post[node]
            dm=md2001(ds); rm=md2001(dr)
            if dm<start0 or dm>start0+dt.timedelta(days=7):
                errors.append(f"{node}: logger deployment {ds} outside July 24-31 window")
            if rm<end0 or rm>end0+dt.timedelta(days=7):
                errors.append(f"{node}: logger retrieval {dr} outside September 3-10 window")
            if abs((dp-ds).days)>3:
                errors.append(f"{node}: pre-TNC is >3 d from logger deployment")
            if abs((dq-dr).days)>3:
                errors.append(f"{node}: post-TNC is >3 d from logger retrieval")
            interval=(dq-dp).days
            if interval<39 or interval>45:
                errors.append(f"{node}: pre/post TNC interval {interval} d outside 39-45")
            if node in tnc_cal and tnc_cal[node]!=dq:
                errors.append(f"{node}: authoritative core-three TNC baseline must equal post-exposure TNC date; third TNC round is prohibited")

        # Common exposure overlap is evaluated separately for each confirmatory module.
        for label,nodes in (("event",event if event_intent=="confirmatory" else set()),
                            ("optical",optical if optical_intent=="confirmatory" else set())):
            if nodes and nodes<=set(deploy) and nodes<=set(retrieve):
                common_start=max(deploy[n] for n in nodes)
                common_end=min(retrieve[n] for n in nodes)
                overlap=(common_end-common_start).days
                calculated[f"{label}_common_overlap_days"]=overlap
                if overlap<35:
                    errors.append(f"{label} common logger overlap {overlap} d < 35 d")
    else:
        # No optional forcing module -> no extra destructive pre-TNC round.
        if event_intent=="disabled" and optical_intent=="disabled":
            notes.append("No outcome-bearing pre-exposure TNC round is authorized; campaign is TNC-v2 baseline only")

    baseline_only=tnc-prepost
    min_cores=6*len(prepost)+3*len(baseline_only)
    calculated.update({
        "tnc_v2_nodes":len(tnc),
        "event_nodes":len(event),
        "optical_nodes":len(optical),
        "optical_reference_nodes":len(ref),
        "prepost_tnc_union_nodes":len(prepost),
        "baseline_only_tnc_nodes":len(baseline_only),
        "minimum_outcome_bearing_tnc_cores_before_replacements":min_cores,
    })
    try:
        preserve=int(fields.get("preservation_capacity_for_planned_core_samples"))
        calculated["preservation_capacity_for_planned_core_samples"]=preserve
        if preserve<min_cores:
            errors.append(f"preservation capacity {preserve} < minimum planned TNC cores {min_cores}")
    except Exception:
        errors.append("preservation_capacity_for_planned_core_samples must be integer")

    try:
        hplc_cap=int(fields.get("hplc_primary_assay_capacity_for_planned_core_samples"))
        calculated["hplc_primary_assay_capacity_for_planned_core_samples"]=hplc_cap
        if hplc_cap<min_cores:
            errors.append(f"HPLC primary assay capacity {hplc_cap} < minimum planned TNC cores {min_cores}")
    except Exception:
        errors.append("hplc_primary_assay_capacity_for_planned_core_samples must be integer")

    # Determine per-module labels.
    tnc_errors=[e for e in errors if (
        e.startswith("TNC v2") or "authoritative TNC" in e or "TNC-v2" in e
        or "four-bay" in e or "baseline is" in e or "preservation capacity" in e
        or "tnc_v2_primary_analysis" in e or "node_level_uncertainty" in e
    )]
    event_errors=[e for e in errors if "event" in e.lower() or "temperature/salinity" in e]
    optical_errors=[e for e in errors if "optical" in e.lower() or "within-canopy PAR" in e]

    module_status={
        "tnc_v2":"CONFIRMATORY_READY" if not tnc_errors else "STOP",
        "event_stress":(
            "DISABLED" if event_intent=="disabled"
            else "CONFIRMATORY_READY" if not event_errors else "STOP"
        ),
        "optical":(
            "DISABLED" if optical_intent=="disabled"
            else "CONFIRMATORY_READY" if not optical_errors else "STOP"
        ),
        "optical_attribution":optical_attribution_status,
    }

    if tnc_errors:
        status="STOP_TNC_V2_GATE_FAILED"
    elif errors:
        # Complete freezes fail closed on any remaining rule violation. Do not
        # allow an unclassified calendar/QC error to slip through as READY.
        status="STOP_MODULE_INTENT_MISMATCH"
    else:
        status="READY_TNC_CONFIRMATORY_CAMPAIGN"

    result={
      "schema":"tampa.integrated_campaign_readiness_v2",
      "status":status,
      "module_status":module_status,
      "errors":errors,
      "notes":notes,
      "calculated":calculated,
      "claim_boundary":[
        "Resource readiness is not ecological evidence.",
        "This audit does not read TNC values or future meadow responses.",
        "Four-bay TNC v2 is protected as the decisive outcome-bearing primary.",
        "Optional forcing modules must be confirmatory-ready or disabled before outcome-bearing pre-TNC sampling.",
        "Paired above-canopy PAR attribution is secondary and may be disabled without invalidating the optical primary.",
      ]
    }

    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if a.strict and not status.startswith("READY_"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
