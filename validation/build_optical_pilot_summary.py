#!/usr/bin/env python3
"""Build a response-independent Tampa optical method-pilot candidate from standardized pilot records.

This script reads no TNC or future meadow response. It converts granular
measurement-pilot records into a machine-checkable candidate for
validation/validate_optical_method_pilot.py. It never overwrites the
authoritative field/optical_pilot_freeze.json.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
FORBIDDEN=(
    "future_frequency","future_delta","future_braun","future_shoot",
    "future_blade","tnc_post","tnc_pre","ecological_outcome"
)
LEVELS=(0.25,0.50,0.75)
LEVEL_COL={0.25:"dli_25",0.50:"dli_50",0.75:"dli_75"}
TIE_ORDER={0.50:0,0.25:1,0.75:2}


def check_no_future(path:Path):
    text=path.read_text(encoding="utf-8-sig").lower()
    bad=[x for x in FORBIDDEN if x in text]
    if bad:
        raise RuntimeError(f"{path}: forbidden future-response token(s): {bad}")


def read_csv(path:Path):
    check_no_future(path)
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def as_bool(x):
    s=str(x).strip().lower()
    if s in {"1","true","yes","y","pass","passed"}: return True
    if s in {"0","false","no","n","fail","failed"}: return False
    raise ValueError(f"not boolean: {x!r}")


def num(x):
    if x in (None,""): return None
    return float(x)


def quantile(xs,p):
    ys=sorted(float(x) for x in xs)
    if not ys: return None
    pos=(len(ys)-1)*p
    lo=math.floor(pos); hi=math.ceil(pos)
    if lo==hi: return ys[lo]
    return ys[lo]+(ys[hi]-ys[lo])*(pos-lo)


def linfit(xs,ys):
    if len(xs)<2: return None
    xm=statistics.mean(xs); ym=statistics.mean(ys)
    sxx=sum((x-xm)**2 for x in xs)
    if sxx<=0: return None
    slope=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sxx
    intercept=ym-slope*xm
    pred=[intercept+slope*x for x in xs]
    sst=sum((y-ym)**2 for y in ys)
    sse=sum((y-p)**2 for y,p in zip(ys,pred))
    r2=1-sse/sst if sst>0 else 1.0
    return intercept,slope,r2,pred


def sample_cv(vals):
    vals=[float(x) for x in vals]
    if len(vals)<2: return None
    mean=statistics.mean(vals)
    if mean==0: return math.inf
    return statistics.stdev(vals)/mean


def sha256(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calibration_summary(rows,meta,contract):
    by=defaultdict(list)
    for r in rows:
        sid=str(r.get("sensor_id","")).strip()
        if sid: by[sid].append(r)

    floor=float(contract["calibration_gate"]["relative_error_definition"]["denominator_floor_umol_m2_s"])
    dark_max=float(contract["calibration_gate"]["dark_reference_definition"]["reference_ppfd_max_umol_m2_s"])
    metrics={}
    for sid,rr in sorted(by.items()):
        complete=[]
        for r in rr:
            try:
                raw=float(r["sensor_raw_photon_rate_umol_m2_s"])
                ref=float(r["reference_photon_rate_umol_m2_s"])
                dark=as_bool(r["dark"])
                saturated=as_bool(r["saturated"])
            except Exception:
                continue
            complete.append((r,raw,ref,dark,saturated))
        if len(complete)<2:
            continue
        xs=[z[1] for z in complete]; ys=[z[2] for z in complete]
        fit=linfit(xs,ys)
        if fit is None: continue
        intercept,slope,r2,pred=fit
        rel=[abs(p-y)/max(abs(y),floor) for p,y in zip(pred,ys)]
        dark_corr=[
            abs(intercept+slope*raw)
            for _,raw,ref,dark,_ in complete
            if dark and ref<=dark_max
        ]
        non_dark_levels={
            str(r.get("irradiance_level_id","")).strip()
            for r,_,ref,dark,_ in complete
            if not dark and str(r.get("irradiance_level_id","")).strip()
        }
        metrics[sid]={
            "paired_n":len(complete),
            "irradiance_levels":len(non_dark_levels),
            "dark_observations":len(dark_corr),
            "maximum_reference_photon_rate_umol_m2_s":max(ys),
            "intercept":intercept,
            "slope":slope,
            "r_squared":r2,
            "median_absolute_relative_error":statistics.median(rel),
            "p95_absolute_relative_error":quantile(rel,0.95),
            "dark_offset_abs_umol_m2_s":max(dark_corr) if dark_corr else None,
            "saturated":any(z[4] for z in complete),
        }
    return metrics


def side_by_side_summary(rows,declared_sensors,contract):
    grouped=defaultdict(dict)
    hours=defaultdict(list)
    for r in rows:
        check=str(r.get("check_id","")).strip()
        sid=str(r.get("sensor_id","")).strip()
        if not check or not sid: continue
        try:
            dli=float(r["dli_mol_m2"])
            h=float(r["underwater_hours"])
        except Exception:
            continue
        grouped[check][sid]=dli
        hours[check].append(h)

    min_hours=float(contract["calibration_gate"]["side_by_side_dli_check"]["minimum_underwater_hours"])
    out={}
    eligible=[]
    declared=set(declared_sensors)
    for check,vals in sorted(grouped.items()):
        present=set(vals)
        complete=bool(declared) and declared.issubset(present)
        common_hours=min(hours[check]) if hours[check] else 0
        cv=sample_cv([vals[s] for s in declared_sensors]) if complete else None
        ok=bool(complete and common_hours>=min_hours and cv is not None)
        out[check]={
            "declared_sensors_present":complete,
            "minimum_underwater_hours":common_hours,
            "between_sensor_cv":cv,
            "eligible":ok,
        }
        if ok: eligible.append(check)
    max_cv=max((out[k]["between_sensor_cv"] for k in eligible),default=None)
    min_hrs=min((out[k]["minimum_underwater_hours"] for k in eligible),default=None)
    return {
        "check_metrics":out,
        "eligible_checks":eligible,
        "eligible_check_count":len(eligible),
        "max_between_sensor_cv":max_cv,
        "minimum_underwater_hours":min_hrs,
    }


def profile_summary(rows,contract):
    qc=contract["vertical_representativeness_gate"]["valid_day_input_rule"]
    min_cov=float(qc["minimum_daylight_coverage_fraction"])
    max_gap=float(qc["maximum_daylight_gap_minutes"])
    profile_rows=[]
    seen=set()
    for r in rows:
        node=str(r.get("node_id","")).strip()
        bay=str(r.get("water_body","")).strip()
        date=str(r.get("date","")).strip()
        if not node or bay not in BAYS or not date: continue
        key=(node,date)
        if key in seen:
            raise RuntimeError(f"duplicate vertical-profile node-day: {node} {date}")
        seen.add(key)
        try:
            cov=float(r["daylight_coverage_fraction"])
            gap=float(r["max_daylight_gap_minutes"])
            canopy_height=float(r["canopy_height_m"])
            canopy_class=str(r["canopy_height_class"]).strip().lower()
            vals={lev:float(r[LEVEL_COL[lev]]) for lev in LEVELS}
            above=float(r["dli_above"])
        except Exception:
            continue
        if cov<min_cov or gap>max_gap:
            continue
        ref=statistics.mean(vals.values())
        if ref<=0 or above<0: continue
        profile_rows.append({
            "node_id":node,"water_body":bay,"date":date,
            "ref":ref,"vals":vals,"above":above,
            "canopy_height_m":canopy_height,"canopy_height_class":canopy_class,
            "daylight_coverage_fraction":cov,"max_daylight_gap_minutes":gap,
        })

    metrics={}
    for lev in LEVELS:
        signed=[(z["vals"][lev]-z["ref"])/z["ref"] for z in profile_rows]
        absolute=[abs(v) for v in signed]
        bybay={}
        for b in BAYS:
            vv=[
                (z["vals"][lev]-z["ref"])/z["ref"]
                for z in profile_rows if z["water_body"]==b
            ]
            bybay[b]=statistics.median(vv) if vv else None
        metrics[str(lev)]={
            "median_absolute_relative_error":statistics.median(absolute) if absolute else None,
            "fraction_node_days_with_absolute_relative_error_lte_0_25":(
                sum(v<=0.25 for v in absolute)/len(absolute) if absolute else None
            ),
            "bay_median_relative_bias":bybay,
            "max_absolute_bay_median_relative_bias":max(
                (abs(v) for v in bybay.values() if v is not None),default=None
            ),
        }

    valid=[
        lev for lev in LEVELS
        if metrics[str(lev)]["median_absolute_relative_error"] is not None
    ]
    selected=min(
        valid,
        key=lambda lev:(metrics[str(lev)]["median_absolute_relative_error"],TIE_ORDER[lev])
    ) if valid else None
    days=Counter(z["node_id"] for z in profile_rows)
    node_bay={z["node_id"]:z["water_body"] for z in profile_rows}
    node_class={}
    for z in profile_rows:
        node=z["node_id"]; cls=z["canopy_height_class"]
        if node in node_class and node_class[node]!=cls:
            raise RuntimeError(f"canopy-height class drift within node {node}")
        node_class[node]=cls
    nodes=sorted(days)
    return {
        "pilot_nodes":len(nodes),
        "node_ids":nodes,
        "nodes_by_bay":dict(Counter(node_bay[n] for n in nodes)),
        "nodes_by_canopy_height_class":dict(Counter(node_class[n] for n in nodes)),
        "valid_daylight_node_days":len(profile_rows),
        "minimum_valid_daylight_days_per_node":min(days.values()) if days else None,
        "candidate_level_metrics":metrics,
        "selected_within_canopy_height_fraction":selected,
    }


def placement_summary(rows,selected,profile_nodes):
    bynode=defaultdict(list)
    nodebay={}
    flags=[]
    if selected is None:
        return {
            "pilot_nodes":0,"nodes_by_bay":{},"minimum_mock_deployments_per_node":None,
            "covers_vertical_profile_nodes":False,
            "fraction_within_tolerance":None,"placements_n":0
        }
    for r in rows:
        node=str(r.get("node_id","")).strip()
        bay=str(r.get("water_body","")).strip()
        if not node or bay not in BAYS: continue
        try:
            h=float(r["canopy_height_m"]); got=float(r["achieved_height_m"])
        except Exception:
            continue
        target=selected*h
        tolerance=max(0.02,0.10*h)
        ok=abs(got-target)<=tolerance
        bynode[node].append(ok); nodebay[node]=bay; flags.append(ok)
    nodes=sorted(bynode)
    return {
        "pilot_nodes":len(nodes),
        "nodes_by_bay":dict(Counter(nodebay[n] for n in nodes)),
        "minimum_mock_deployments_per_node":min((len(bynode[n]) for n in nodes),default=None),
        "covers_vertical_profile_nodes":set(profile_nodes).issubset(set(nodes)),
        "fraction_within_tolerance":sum(flags)/len(flags) if flags else None,
        "placements_n":len(flags),
    }


def fouling_cell(rows,mode,interval,contract):
    floor=float(contract["fouling_maintenance_gate"]["relative_change_definition"]["denominator_floor_umol_m2_s"])
    target=[]
    for r in rows:
        rmode=str(r.get("maintenance_mode","")).strip()
        if rmode!=mode: continue
        if mode=="manual":
            try:
                if int(float(r.get("service_interval_days","")))!=int(interval): continue
            except Exception:
                continue
        loc=str(r.get("location_id","")).strip()
        bay=str(r.get("water_body","")).strip()
        if not loc or bay not in BAYS: continue
        try:
            day=float(r["pilot_day"])
            pre=float(r["pre_clean_photon_rate_umol_m2_s"])
            post=float(r["post_clean_photon_rate_umol_m2_s"])
        except Exception:
            continue
        rel=abs(pre-post)/max(abs(post),floor)
        target.append((loc,bay,day,rel))

    locs={z[0] for z in target}
    bybay=Counter(z[1] for z in target)
    max_day_by_loc={loc:max(z[2] for z in target if z[0]==loc) for loc in locs}
    duration_ok=bool(locs) and all(v>=contract["fouling_maintenance_gate"]["minimum_submerged_pilot_days"] for v in max_day_by_loc.values())
    rel=[z[3] for z in target]
    med=statistics.median(rel) if rel else None
    p90=quantile(rel,0.90) if rel else None
    pass_gate=(
        bool(rel)
        and len(locs)>=contract["fouling_maintenance_gate"]["pilot_locations_min"]
        and all(bybay[b]>=contract["fouling_maintenance_gate"]["pilot_locations_min_per_bay"] for b in BAYS)
        and duration_ok
        and med<=contract["fouling_maintenance_gate"]["acceptance"]["median_absolute_relative_change_max"]
        and p90<=contract["fouling_maintenance_gate"]["acceptance"]["p90_absolute_relative_change_max"]
    )
    return {
        "locations":len(locs),
        "by_bay":dict(bybay),
        "minimum_location_submerged_days":min(max_day_by_loc.values()) if max_day_by_loc else None,
        "paired_checks":len(rel),
        "median_absolute_relative_change":med,
        "p90_absolute_relative_change":p90,
        "pass":bool(pass_gate),
    }


def fouling_summary(rows,contract):
    metrics={}
    selected_mode=None; selected_interval=None; selected_metrics=None
    for interval in contract["fouling_maintenance_gate"]["candidate_service_intervals_days"]:
        m=fouling_cell(rows,"manual",interval,contract)
        metrics[f"manual_{interval}"]=m
        if selected_mode is None and m["pass"]:
            selected_mode="manual"; selected_interval=int(interval); selected_metrics=m
    active=fouling_cell(rows,"active_antifouling",None,contract)
    metrics["active_antifouling"]=active
    if selected_mode is None and active["pass"]:
        selected_mode="active_antifouling"
        selected_interval="NOT_APPLICABLE_ACTIVE_ANTIFOULING"
        selected_metrics=active
    return {
        "candidate_metrics":metrics,
        "selected_maintenance_mode":selected_mode,
        "selected_manual_service_interval_days":selected_interval,
        "selected_metrics":selected_metrics,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",default="results/optical_pilot_acceptance_v1_contract.json")
    ap.add_argument("--metadata",default="field/optical_raw_pilot_metadata.json")
    ap.add_argument("--calibration",default="field/optical_calibration_pilot.csv")
    ap.add_argument("--sideby",default="field/optical_side_by_side_dli_pilot.csv")
    ap.add_argument("--profile",default="field/optical_vertical_profile_pilot.csv")
    ap.add_argument("--placement",default="field/optical_placement_pilot.csv")
    ap.add_argument("--fouling",default="field/optical_fouling_pilot.csv")
    ap.add_argument("--out",default="field/optical_pilot_candidate.json")
    ap.add_argument("--audit-out",default="results/optical_raw_pilot_summary.json")
    a=ap.parse_args()

    paths=[
        Path(a.metadata),Path(a.calibration),Path(a.sideby),
        Path(a.profile),Path(a.placement),Path(a.fouling)
    ]
    for p in paths: check_no_future(p)
    contract=json.loads(Path(a.contract).read_text(encoding="utf-8"))
    meta=json.loads(Path(a.metadata).read_text(encoding="utf-8"))
    if meta.get("outcome_response_accessed") is not False:
        raise SystemExit("outcome_response_accessed must be false")

    declared=[
        str(x).strip() for x in meta.get("outcome_bearing_sensor_ids",[])
        if str(x).strip()
    ]

    cal=calibration_summary(read_csv(Path(a.calibration)),meta,contract)
    side=side_by_side_summary(read_csv(Path(a.sideby)),declared,contract)
    profile=profile_summary(read_csv(Path(a.profile)),contract)
    placement=placement_summary(
        read_csv(Path(a.placement)),
        profile["selected_within_canopy_height_fraction"],
        profile["node_ids"],
    )
    fouling=fouling_summary(read_csv(Path(a.fouling)),contract)

    candidate={
        "schema":"tampa.optical_pilot_candidate.v2",
        "status":"RAW_PILOT_SUMMARY_CANDIDATE",
        "outcome_response_accessed":False,
        "metadata":meta,
        "calibration":{
            "declared_outcome_bearing_sensor_ids":declared,
            "sensor_metrics":cal,
            **side,
        },
        "vertical_profile":profile,
        "placement":placement,
        "fouling":fouling,
        "raw_pilot_provenance":{
            str(p):{"sha256":sha256(p),"bytes":p.stat().st_size}
            for p in paths
        },
        "source_artifact_manifest":meta.get("source_artifact_manifest",[]),
    }

    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(candidate,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    audit={
        "schema":"tampa.optical_raw_pilot_summary.v2",
        "candidate":a.out,
        "candidate_sha256":sha256(out),
        "raw_provenance":candidate["raw_pilot_provenance"],
        "next_command":f"python validation/validate_optical_method_pilot.py --pilot {a.out}",
        "boundary":"Response-independent measurement pilot only; TNC/future response prohibited.",
    }
    audit_out=Path(a.audit_out); audit_out.parent.mkdir(parents=True,exist_ok=True)
    audit_out.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
