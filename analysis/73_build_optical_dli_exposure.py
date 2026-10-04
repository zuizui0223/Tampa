#!/usr/bin/env python3
"""Build frozen Tampa optical DLI exposures from outcome-bearing raw PAR logger records.

This preprocessing layer reads PAR/logger metadata and the response-independent
READY optical method freeze. It does NOT read TNC or future meadow responses.

Pipeline:
  raw sensor PPFD
    -> frozen sensor-specific calibration
    -> frozen schedule alignment / range QC
    -> astronomical daylight QC
    -> <=30 min interpolation only
    -> trapezoidal daily light integral (DLI)
    -> node-level mean within-canopy DLI over one predeclared common window

The common exposure window is fixed from the complete predeclared optical node
manifest before PAR/TNC-based node exclusion. Sensor failures therefore cannot
be used to expand or shift the exposure window.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
LOCAL_TZ=ZoneInfo("America/New_York")
UTC=timezone.utc
FIXED_START=(7,24)
FIXED_END_EXCLUSIVE=(9,4)  # includes all of Sep 3
MAX_INTERVAL_MIN=15.0
TIMESTAMP_TOLERANCE_SECONDS=120.0
MIN_DAYLIGHT_COVERAGE=0.90
MAX_DAYLIGHT_GAP_MIN=30.0
MIN_VALID_DLI_DAYS=30
MIN_OVERALL_COVERAGE=0.85
MIN_COMMON_OVERLAP_DAYS=35
SOLAR_ZENITH_DEG=90.833
FORBIDDEN=(
    "tnc_pre","tnc_post","future_frequency","future_delta",
    "future_braun","future_shoot","future_blade","ecological_outcome"
)


def check_no_response(path:Path):
    txt=path.read_text(encoding="utf-8-sig").lower()
    bad=[x for x in FORBIDDEN if x in txt]
    if bad:
        raise RuntimeError(f"{path}: forbidden biological-response token(s): {bad}")


def parse_utc(s:str)->datetime:
    v=str(s).strip()
    if not v:
        raise ValueError("empty UTC timestamp")
    if v.endswith("Z"):
        v=v[:-1]+"+00:00"
    x=datetime.fromisoformat(v)
    if x.tzinfo is None:
        raise ValueError(f"timestamp lacks UTC offset: {s}")
    x=x.astimezone(UTC)
    return x


def iso_utc(x:datetime)->str:
    return x.astimezone(UTC).isoformat().replace("+00:00","Z")


def truth(v)->bool:
    return str(v).strip().lower() in {"1","true","yes","y","pass","passed"}


def normalize_deg(x:float)->float:
    return x%360.0


def sunrise_sunset_utc(local_day:date,lat:float,lon:float):
    """NOAA-style sunrise/sunset approximation for zenith 90.833 degrees."""
    n=local_day.timetuple().tm_yday
    lng_hour=lon/15.0

    def calc(sunrise:bool):
        t=n+(((6.0 if sunrise else 18.0)-lng_hour)/24.0)
        m=(0.9856*t)-3.289
        mr=math.radians(m)
        l=m+1.916*math.sin(mr)+0.020*math.sin(2*mr)+282.634
        l=normalize_deg(l)
        lr=math.radians(l)
        ra=math.degrees(math.atan(0.91764*math.tan(lr)))
        ra=normalize_deg(ra)
        lq=math.floor(l/90.0)*90.0
        raq=math.floor(ra/90.0)*90.0
        ra=(ra+(lq-raq))/15.0
        sin_dec=0.39782*math.sin(lr)
        cos_dec=math.cos(math.asin(sin_dec))
        cos_h=(
            math.cos(math.radians(SOLAR_ZENITH_DEG))
            - sin_dec*math.sin(math.radians(lat))
        )/(cos_dec*math.cos(math.radians(lat)))
        if cos_h>1 or cos_h<-1:
            raise RuntimeError("sunrise/sunset undefined for node/date")
        h=(360.0-math.degrees(math.acos(cos_h))) if sunrise else math.degrees(math.acos(cos_h))
        h/=15.0
        local_mean=h+ra-(0.06571*t)-6.622
        ut=(local_mean-lng_hour)%24.0
        return ut

    sr_h=calc(True)
    ss_h=calc(False)
    base=datetime.combine(local_day,time(0,0),tzinfo=UTC)
    sunrise=base+timedelta(hours=sr_h)
    sunset=base+timedelta(hours=ss_h)
    if sunset<=sunrise:
        sunset+=timedelta(days=1)
    return sunrise,sunset


def ceil_div_timedelta(delta:timedelta,step:timedelta)->int:
    return math.ceil(delta.total_seconds()/step.total_seconds()-1e-12)


def floor_div_timedelta(delta:timedelta,step:timedelta)->int:
    return math.floor(delta.total_seconds()/step.total_seconds()+1e-12)


def expected_grid(anchor:datetime,start:datetime,end:datetime,interval_min:float):
    step=timedelta(minutes=interval_min)
    k0=ceil_div_timedelta(start-anchor,step)
    k1=floor_div_timedelta((end-timedelta(microseconds=1))-anchor,step)
    if k1<k0:
        return []
    return [anchor+k*step for k in range(k0,k1+1)]


def local_dates(start:datetime,end:datetime):
    if end<=start:
        return []
    d0=start.astimezone(LOCAL_TZ).date()
    d1=(end-timedelta(microseconds=1)).astimezone(LOCAL_TZ).date()
    out=[]; d=d0
    while d<=d1:
        out.append(d); d+=timedelta(days=1)
    return out


def interpolate_value(t:datetime,known_times,known_values):
    i=bisect.bisect_left(known_times,t)
    if i<len(known_times) and known_times[i]==t:
        return known_values[i]
    if i==0 or i==len(known_times):
        return None
    t0,t1=known_times[i-1],known_times[i]
    v0,v1=known_values[i-1],known_values[i]
    span=(t1-t0).total_seconds()
    if span<=0:
        return None
    frac=(t-t0).total_seconds()/span
    return v0+(v1-v0)*frac


def trapz_dli(times,values):
    area=0.0
    for i in range(1,len(times)):
        dt=(times[i]-times[i-1]).total_seconds()
        area+=0.5*(values[i-1]+values[i])*dt
    return area/1e6


def load_manifest(path:Path):
    check_no_response(path)
    rows=list(csv.DictReader(path.open("r",encoding="utf-8-sig",newline="")))
    if not rows:
        raise RuntimeError("empty optical deployment manifest")
    out=[]
    seen_nodes=set(); seen_sensors=set()
    for r in rows:
        node=r["node_id"].strip(); sensor=r["sensor_id"].strip(); bay=r["water_body"].strip()
        if not node or not sensor or bay not in BAYS:
            raise RuntimeError(f"invalid manifest identity: {r}")
        if node in seen_nodes:
            raise RuntimeError(f"one outcome-bearing sensor per node required: duplicate node {node}")
        if sensor in seen_sensors:
            raise RuntimeError(f"sensor reused across simultaneous nodes: {sensor}")
        seen_nodes.add(node); seen_sensors.add(sensor)
        interval=float(r["sampling_interval_minutes"])
        if interval<=0 or interval>MAX_INTERVAL_MIN:
            raise RuntimeError(f"{node}: sampling interval {interval} outside (0,{MAX_INTERVAL_MIN}] min")
        dep=parse_utc(r["deployment_utc"]); ret=parse_utc(r["retrieval_utc"])
        anchor=parse_utc(r["schedule_anchor_utc"])
        if ret<=dep:
            raise RuntimeError(f"{node}: retrieval <= deployment")
        lat=float(r["latitude"]); lon=float(r["longitude"])
        if not (24<=lat<=31 and -88<=lon<=-79):
            raise RuntimeError(f"{node}: coordinates outside broad Florida audit bound")
        if not truth(r.get("primary_confirmatory","true")):
            raise RuntimeError(f"{node}: manifest may contain only predeclared primary optical nodes")
        out.append({
            "node_id":node,"sensor_id":sensor,"water_body":bay,
            "latitude":lat,"longitude":lon,
            "deployment_utc":dep,"retrieval_utc":ret,
            "schedule_anchor_utc":anchor,"sampling_interval_minutes":interval,
        })
    return out


def calibration_map(freeze:dict,manifest):
    if freeze.get("status")!="READY":
        raise RuntimeError("field/optical_pilot_freeze.json is not READY")
    prov=freeze.get("method_pilot_provenance",{})
    if prov.get("validation_status")!="PASS_OPTICAL_PILOT":
        raise RuntimeError("READY optical freeze lacks PASS_OPTICAL_PILOT provenance")
    fields=freeze["fields_to_freeze_before_optical_confirmatory_deployment"]
    if fields.get("all_outcome_bearing_channels_pass_calibration_gate") is not True:
        raise RuntimeError("optical freeze does not certify all outcome-bearing channels")
    cm=fields.get("sensor_specific_calibration_manifest")
    if not isinstance(cm,dict):
        raise RuntimeError("sensor-specific calibration manifest missing")
    out={}
    for m in manifest:
        sid=m["sensor_id"]
        if sid not in cm:
            raise RuntimeError(f"{sid}: no frozen calibration")
        z=cm[sid]
        trans=z.get("reference_from_raw_to_ppfd",{})
        try:
            intercept=float(trans["intercept"]); slope=float(trans["slope"])
            max_ref=float(z["maximum_reference_ppfd_umol_m2_s"])
        except Exception as e:
            raise RuntimeError(f"{sid}: incomplete calibration manifest: {e}")
        if slope<=0 or max_ref<=0:
            raise RuntimeError(f"{sid}: invalid calibration slope/range")
        out[sid]={"intercept":intercept,"slope":slope,"maximum_reference_ppfd_umol_m2_s":max_ref}
    return out


def load_raw(path:Path,manifest,cal,common_start,common_end):
    check_no_response(path)
    rows=list(csv.DictReader(path.open("r",encoding="utf-8-sig",newline="")))
    sensor_to_node={m["sensor_id"]:m for m in manifest}
    mapped={m["node_id"]:{} for m in manifest}
    row_audit=defaultdict(lambda:Counter())
    for r in rows:
        sid=str(r.get("sensor_id","")).strip()
        if sid not in sensor_to_node:
            continue
        m=sensor_to_node[sid]; node=m["node_id"]
        row_audit[node]["rows_seen"]+=1
        try:
            ts=parse_utc(r["timestamp_utc"])
            raw=float(r["raw_ppfd"])
        except Exception:
            row_audit[node]["invalid_parse"]+=1
            continue
        if not (common_start<=ts<common_end):
            row_audit[node]["outside_common_window"]+=1
            continue
        if not truth(r.get("instrument_qc_pass","true")):
            row_audit[node]["instrument_qc_fail"]+=1
            continue
        interval=timedelta(minutes=m["sampling_interval_minutes"])
        k=round((ts-m["schedule_anchor_utc"]).total_seconds()/interval.total_seconds())
        target=m["schedule_anchor_utc"]+k*interval
        err=abs((ts-target).total_seconds())
        if err>TIMESTAMP_TOLERANCE_SECONDS:
            row_audit[node]["off_schedule"]+=1
            continue
        z=cal[sid]
        ppfd=z["intercept"]+z["slope"]*raw
        if ppfd>z["maximum_reference_ppfd_umol_m2_s"]+1e-9:
            row_audit[node]["outside_calibration_range"]+=1
            continue
        ppfd=max(0.0,ppfd)
        if target in mapped[node]:
            raise RuntimeError(f"{node}: multiple valid raw rows map to schedule time {target}")
        mapped[node][target]=ppfd
        row_audit[node]["valid_mapped"]+=1
    return mapped,row_audit


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--raw",required=True)
    ap.add_argument("--optical-freeze",default="field/optical_pilot_freeze.json")
    ap.add_argument("--daily-out",required=True)
    ap.add_argument("--node-out",required=True)
    ap.add_argument("--audit-out",required=True)
    a=ap.parse_args()

    manifest=load_manifest(Path(a.manifest))
    years={m["deployment_utc"].astimezone(LOCAL_TZ).year for m in manifest} | {
        m["retrieval_utc"].astimezone(LOCAL_TZ).year for m in manifest
    }
    if len(years)!=1:
        raise RuntimeError(f"optical manifest spans multiple campaign years: {years}")
    year=next(iter(years))
    fixed_start=datetime(year,*FIXED_START,0,0,tzinfo=LOCAL_TZ).astimezone(UTC)
    fixed_end=datetime(year,*FIXED_END_EXCLUSIVE,0,0,tzinfo=LOCAL_TZ).astimezone(UTC)

    # Freeze the common window from every predeclared node BEFORE data-quality exclusions.
    common_start=max([fixed_start]+[m["deployment_utc"] for m in manifest])
    common_end=min([fixed_end]+[m["retrieval_utc"] for m in manifest])
    if common_end<=common_start:
        raise RuntimeError("no common optical exposure window")
    dates=local_dates(common_start,common_end)
    common_days=len(dates)

    freeze=json.loads(Path(a.optical_freeze).read_text(encoding="utf-8"))
    cal=calibration_map(freeze,manifest)
    mapped,row_audit=load_raw(Path(a.raw),manifest,cal,common_start,common_end)

    daily=[]
    nodes=[]
    for m in manifest:
        node=m["node_id"]; obs=mapped[node]
        all_expected=expected_grid(
            m["schedule_anchor_utc"],common_start,common_end,m["sampling_interval_minutes"]
        )
        overall_obs=sum(t in obs for t in all_expected)
        overall_cov=overall_obs/len(all_expected) if all_expected else 0.0
        valid_dlis=[]
        invalid_reasons=Counter()

        for d in dates:
            sr,ss=sunrise_sunset_utc(d,m["latitude"],m["longitude"])
            day_start=max(sr,common_start)
            day_end=min(ss,common_end)
            if day_end<=day_start:
                continue
            expected=expected_grid(
                m["schedule_anchor_utc"],day_start,day_end,m["sampling_interval_minutes"]
            )
            observed_times=[t for t in expected if t in obs]
            coverage=len(observed_times)/len(expected) if expected else 0.0

            known_times=[day_start]+observed_times+[day_end]
            known_values=[0.0]+[obs[t] for t in observed_times]+[0.0]
            # known_times are normally sorted, but explicit sort protects clipped boundaries.
            pairs=sorted(zip(known_times,known_values),key=lambda z:z[0])
            known_times=[z[0] for z in pairs]; known_values=[z[1] for z in pairs]
            max_gap=max(
                ((known_times[i]-known_times[i-1]).total_seconds()/60.0 for i in range(1,len(known_times))),
                default=math.inf,
            )
            coverage_ok=coverage>=MIN_DAYLIGHT_COVERAGE
            gap_ok=max_gap<=MAX_DAYLIGHT_GAP_MIN+1e-9
            valid=bool(expected and coverage_ok and gap_ok)
            dli=None
            if valid:
                vals=[]
                for t in expected:
                    if t in obs:
                        vals.append(obs[t])
                    else:
                        v=interpolate_value(t,known_times,known_values)
                        if v is None:
                            raise RuntimeError(f"{node} {d}: valid-day interpolation failed")
                        vals.append(v)
                series_times=[day_start]+expected+[day_end]
                series_vals=[0.0]+vals+[0.0]
                dli=trapz_dli(series_times,series_vals)
                valid_dlis.append(dli)
            else:
                if not coverage_ok: invalid_reasons["daylight_coverage"]+=1
                if not gap_ok: invalid_reasons["daylight_gap"]+=1

            daily.append({
                "node_id":node,"water_body":m["water_body"],"sensor_id":m["sensor_id"],
                "local_date":d.isoformat(),
                "sunrise_utc":iso_utc(sr),"sunset_utc":iso_utc(ss),
                "expected_daylight_observations":len(expected),
                "observed_daylight_observations":len(observed_times),
                "daylight_coverage_fraction":coverage,
                "maximum_continuous_daylight_gap_minutes":max_gap,
                "valid_daily_dli":valid,
                "dli_mol_m2":dli,
            })

        valid_count=len(valid_dlis)
        daily_pass=valid_count>=MIN_VALID_DLI_DAYS
        overall_pass=overall_cov>=MIN_OVERALL_COVERAGE
        common_pass=common_days>=MIN_COMMON_OVERLAP_DAYS
        optical_qc=bool(daily_pass and overall_pass and common_pass)
        nodes.append({
            "node_id":node,"water_body":m["water_body"],"sensor_id":m["sensor_id"],
            "mean_daily_within_canopy_dli":(
                statistics_mean(valid_dlis) if valid_dlis else None
            ),
            "par_coverage_fraction":overall_cov,
            "valid_daily_dli_count":valid_count,
            "common_overlap_days":common_days,
            "daily_dli_qc_pass":daily_pass,
            "optical_exposure_qc_pass":optical_qc,
            "common_window_start_utc":iso_utc(common_start),
            "common_window_end_utc":iso_utc(common_end),
            "invalid_daylight_coverage_days":invalid_reasons["daylight_coverage"],
            "invalid_daylight_gap_days":invalid_reasons["daylight_gap"],
        })

    daily_path=Path(a.daily_out); daily_path.parent.mkdir(parents=True,exist_ok=True)
    with daily_path.open("w",newline="",encoding="utf-8") as f:
        fields=list(daily[0].keys()) if daily else []
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(daily)
    node_path=Path(a.node_out); node_path.parent.mkdir(parents=True,exist_ok=True)
    with node_path.open("w",newline="",encoding="utf-8") as f:
        fields=list(nodes[0].keys()) if nodes else []
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(nodes)

    audit={
        "schema":"tampa.optical_dli_exposure_builder.v1",
        "response_independent":True,
        "nodes":len(nodes),
        "nodes_by_water_body":dict(sorted(Counter_simple(m["water_body"] for m in manifest).items())),
        "fixed_calendar":{"start_month_day":"07-24","end_month_day":"09-03"},
        "common_window_start_utc":iso_utc(common_start),
        "common_window_end_utc":iso_utc(common_end),
        "common_overlap_local_dates":common_days,
        "node_optical_qc_pass":sum(bool(x["optical_exposure_qc_pass"]) for x in nodes),
        "row_qc":{k:dict(v) for k,v in row_audit.items()},
        "algorithm":{
            "timezone":"America/New_York",
            "solar_zenith_deg":SOLAR_ZENITH_DEG,
            "timestamp_match_tolerance_seconds":TIMESTAMP_TOLERANCE_SECONDS,
            "negative_calibrated_ppfd":"truncate_to_zero",
            "above_calibration_range":"treat_as_missing",
            "daily_integration":"trapezoidal over scheduled daylight grid with PPFD=0 at astronomical sunrise/sunset",
            "daylight_interpolation":"linear only when longest known-point daylight gap <=30 min",
            "daylight_coverage_min":MIN_DAYLIGHT_COVERAGE,
            "valid_daily_dli_min":MIN_VALID_DLI_DAYS,
            "overall_schedule_coverage_min":MIN_OVERALL_COVERAGE,
            "common_overlap_days_min":MIN_COMMON_OVERLAP_DAYS,
        },
        "claim_boundary":[
            "This preprocessing uses PAR and response-independent calibration only; it does not read TNC or future meadow outcome.",
            "The common window is frozen from every predeclared optical node before raw-data QC exclusions.",
            "Nodes failing optical QC remain reported and are not used to shift or expand the common exposure window."
        ],
    }
    audit_path=Path(a.audit_out); audit_path.parent.mkdir(parents=True,exist_ok=True)
    audit_path.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,sort_keys=True))


def statistics_mean(xs):
    return sum(xs)/len(xs)


def Counter_simple(xs):
    out=defaultdict(int)
    for x in xs: out[x]+=1
    return out


if __name__=="__main__":
    main()
