#!/usr/bin/env python3
"""Build response-independent optical pilot candidate summary from raw records."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from collections import defaultdict,Counter
from pathlib import Path

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")
FORBIDDEN=("future_frequency","future_delta","future_braun","future_shoot","future_blade","tnc_post","tnc_pre","ecological_outcome")
LEVELS=(0.25,0.50,0.75)
LEVEL_COL={0.25:"dli_25",0.50:"dli_50",0.75:"dli_75"}
TIE_ORDER={0.50:0,0.25:1,0.75:2}

def check_no_future(path:Path):
    txt=path.read_text(encoding="utf-8-sig").lower()
    bad=[x for x in FORBIDDEN if x in txt]
    if bad: raise RuntimeError(f"{path}: forbidden future-response token(s): {bad}")

def read_csv(path:Path):
    check_no_future(path)
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def as_bool(x):
    s=str(x).strip().lower()
    if s in {"1","true","yes","y"}: return True
    if s in {"0","false","no","n"}: return False
    raise ValueError(f"not boolean: {x!r}")

def quantile(xs,p):
    ys=sorted(xs)
    if not ys:return None
    pos=(len(ys)-1)*p; lo=math.floor(pos); hi=math.ceil(pos)
    if lo==hi:return ys[lo]
    return ys[lo]+(ys[hi]-ys[lo])*(pos-lo)

def linfit(xs,ys):
    if len(xs)<2: return None
    xm=statistics.mean(xs); ym=statistics.mean(ys)
    sxx=sum((x-xm)**2 for x in xs)
    if sxx<=0:return None
    b=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sxx
    a=ym-b*xm
    pred=[a+b*x for x in xs]
    sst=sum((y-ym)**2 for y in ys)
    sse=sum((y-p)**2 for y,p in zip(ys,pred))
    r2=1-sse/sst if sst>0 else 1.0
    return a,b,r2,pred

def cv(vals):
    if len(vals)<2:return 0.0
    m=statistics.mean(vals)
    return statistics.stdev(vals)/m if m else math.inf

def sha256(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

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

    paths=[Path(a.metadata),Path(a.calibration),Path(a.sideby),Path(a.profile),Path(a.placement),Path(a.fouling)]
    for p in paths: check_no_future(p)
    contract=json.loads(Path(a.contract).read_text())
    meta=json.loads(Path(a.metadata).read_text())
    if meta.get("outcome_response_accessed") is not False:
        raise SystemExit("outcome_response_accessed must be false")

    # Calibration.
    rows=read_csv(Path(a.calibration)); by=defaultdict(list)
    for r in rows:
        if not r.get("sensor_id","").strip(): continue
        by[r["sensor_id"].strip()].append(r)
    sensor_metrics={}
    for sid,rr in by.items():
        non_dark=[r for r in rr if r.get("dark","").strip() and not as_bool(r["dark"])]
        dark=[r for r in rr if r.get("dark","").strip() and as_bool(r["dark"])]
        xs=[float(r["sensor_raw_ppfd_umol_m2_s"]) for r in non_dark]
        ys=[float(r["reference_ppfd_umol_m2_s"]) for r in non_dark]
        fit=linfit(xs,ys)
        if fit is None: continue
        intercept,slope,r2,pred=fit
        rel=[abs(p-y)/y for p,y in zip(pred,ys) if abs(y)>1.0]
        dark_corr=[abs(intercept+slope*float(r["sensor_raw_ppfd_umol_m2_s"])) for r in dark]
        saturated=any(as_bool(r["saturated"]) for r in rr if r.get("saturated","").strip())
        sensor_metrics[sid]={
          "paired_n":len(non_dark),
          "irradiance_levels":len({r["irradiance_level_id"] for r in non_dark if r.get("irradiance_level_id","").strip()}),
          "intercept":intercept,"slope":slope,"r_squared":r2,
          "median_absolute_relative_error":statistics.median(rel) if rel else None,
          "p95_absolute_relative_error":quantile(rel,0.95) if rel else None,
          "dark_offset_abs_umol_m2_s":max(dark_corr) if dark_corr else None,
          "saturated":saturated
        }

    # Side-by-side integrated light agreement.
    side=read_csv(Path(a.sideby)); chk=defaultdict(list); side_hours=[]
    for r in side:
        if r.get("check_id","").strip():
            chk[r["check_id"].strip()].append(float(r["dli_mol_m2"]))
            if r.get("underwater_hours","").strip():
                side_hours.append(float(r["underwater_hours"]))
    check_cvs={k:cv(v) for k,v in chk.items()}
    max_side_cv=max(check_cvs.values()) if check_cvs else None
    min_side_hours=min(side_hours) if side_hours else None

    # Vertical profile.
    prof=read_csv(Path(a.profile))
    profile_rows=[]
    for r in prof:
        if not r.get("node_id","").strip(): continue
        vals={lev:float(r[LEVEL_COL[lev]]) for lev in LEVELS}
        ref=statistics.mean(vals.values())
        if ref<=0: continue
        profile_rows.append({
          "node_id":r["node_id"].strip(),"water_body":r["water_body"].strip(),"date":r["date"].strip(),
          "ref":ref,"vals":vals
        })
    level_metrics={}
    for lev in LEVELS:
        errs=[abs(z["vals"][lev]-z["ref"])/z["ref"] for z in profile_rows]
        signed=[(z["vals"][lev]-z["ref"])/z["ref"] for z in profile_rows]
        bybay={}
        for b in BAYS:
            zz=[(z["vals"][lev]-z["ref"])/z["ref"] for z in profile_rows if z["water_body"]==b]
            bybay[b]=statistics.median(zz) if zz else None
        level_metrics[str(lev)]={
          "median_absolute_relative_error":statistics.median(errs) if errs else None,
          "fraction_node_days_with_absolute_relative_error_lte_0_25":sum(e<=0.25 for e in errs)/len(errs) if errs else None,
          "bay_median_relative_bias":bybay,
          "max_absolute_bay_median_relative_bias":max((abs(v) for v in bybay.values() if v is not None),default=None)
        }
    valid_levels=[lev for lev in LEVELS if level_metrics[str(lev)]["median_absolute_relative_error"] is not None]
    selected=min(valid_levels,key=lambda lev:(level_metrics[str(lev)]["median_absolute_relative_error"],TIE_ORDER[lev])) if valid_levels else None
    node_days=Counter(z["node_id"] for z in profile_rows)
    profile_nodes=sorted(node_days)
    node_bay={z["node_id"]:z["water_body"] for z in profile_rows}
    profile_by_bay=Counter(node_bay[n] for n in profile_nodes)

    # Placement repeatability at selected level.
    placement=read_csv(Path(a.placement)); pass_flags=[]
    if selected is not None:
        for r in placement:
            if not r.get("node_id","").strip(): continue
            h=float(r["canopy_height_m"]); got=float(r["achieved_height_m"])
            target=selected*h
            tol=max(0.02,0.10*h)
            pass_flags.append(abs(got-target)<=tol)
    placement_fraction=sum(pass_flags)/len(pass_flags) if pass_flags else None

    # Fouling interval.
    fouling=read_csv(Path(a.fouling)); cells=defaultdict(list)
    for r in fouling:
        if not r.get("location_id","").strip(): continue
        post=float(r["post_clean_ppfd_umol_m2_s"]); pre=float(r["pre_clean_ppfd_umol_m2_s"])
        rel=abs(pre-post)/abs(post) if post else math.inf
        cells[int(float(r["service_interval_days"]))].append((r["location_id"].strip(),r["water_body"].strip(),rel))
    fouling_metrics={}
    selected_interval=None
    for interval in contract["fouling_maintenance_gate"]["candidate_service_intervals_days"]:
        vals=cells.get(interval,[])
        locs={x[0] for x in vals}; bybay=Counter(x[1] for x in vals); rel=[x[2] for x in vals]
        med=statistics.median(rel) if rel else None; p90=quantile(rel,0.90) if rel else None
        passed=bool(rel) and len(locs)>=contract["fouling_maintenance_gate"]["pilot_locations_min"] and all(bybay[b]>=contract["fouling_maintenance_gate"]["pilot_locations_min_per_bay"] for b in BAYS) and med<=contract["fouling_maintenance_gate"]["acceptance"]["median_absolute_relative_change_max"] and p90<=contract["fouling_maintenance_gate"]["acceptance"]["p90_absolute_relative_change_max"]
        fouling_metrics[str(interval)]={"locations":len(locs),"by_bay":dict(bybay),"median_absolute_relative_change":med,"p90_absolute_relative_change":p90,"pass":passed}
        if selected_interval is None and passed: selected_interval=interval

    cand={
      "schema":"tampa.optical_pilot_candidate.v1",
      "status":"RAW_PILOT_SUMMARY_CANDIDATE",
      "outcome_response_accessed":False,
      "metadata":meta,
      "calibration":{"sensor_metrics":sensor_metrics,"side_by_side_check_cv":check_cvs,"max_between_sensor_cv":max_side_cv,"minimum_underwater_hours":min_side_hours},
      "vertical_profile":{
        "pilot_nodes":len(profile_nodes),"nodes_by_bay":dict(profile_by_bay),
        "minimum_valid_daylight_days_per_node":min(node_days.values()) if node_days else None,
        "candidate_level_metrics":level_metrics,
        "selected_within_canopy_height_fraction":selected
      },
      "placement":{"fraction_within_tolerance":placement_fraction,"placements_n":len(pass_flags)},
      "fouling":{"candidate_interval_metrics":fouling_metrics,"selected_manual_service_interval_days":selected_interval},
      "raw_pilot_provenance":{str(p):sha256(p) for p in paths}
    }
    Path(a.out).write_text(json.dumps(cand,indent=2,sort_keys=True)+"\n")

    audit={"schema":"tampa.optical_raw_pilot_summary.v1","candidate":a.out,"raw_provenance":cand["raw_pilot_provenance"],"next_command":f"python validation/validate_optical_method_pilot.py --pilot {a.out}","boundary":"Response-independent measurement pilot only; TNC/future response prohibited."}
    Path(a.audit_out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.audit_out).write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    print(json.dumps(audit,indent=2,sort_keys=True))

if __name__=="__main__": main()
