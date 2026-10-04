#!/usr/bin/env python3
"""Build the frozen one-row-per-node input for Tampa optical primary analysis.

This script joins:
- response-independent optical exposure/QC produced by
  analysis/73_build_optical_dli_exposure.py
- node-level pre/post TNC summaries produced under the separately frozen TNC
  laboratory/sampling workflow.

It performs no model fitting and no exposure selection.
"""
from __future__ import annotations
import argparse,csv,json
from datetime import date
from pathlib import Path

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay")


def truth(v):
    return str(v).strip().lower() in {"1","true","yes","y","pass","passed"}


def parse_date(s):
    return date.fromisoformat(str(s).strip()[:10])


def read_unique(path:Path,key):
    rows=list(csv.DictReader(path.open("r",encoding="utf-8-sig",newline="")))
    out={}
    for r in rows:
        k=str(r.get(key,"")).strip()
        if not k:
            continue
        if k in out:
            raise RuntimeError(f"{path}: duplicate {key}={k}")
        out[k]=r
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--exposure",required=True)
    ap.add_argument("--tnc",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--audit-out",required=True)
    a=ap.parse_args()

    exp=read_unique(Path(a.exposure),"node_id")
    tnc=read_unique(Path(a.tnc),"node_id")
    nodes=sorted(set(exp)|set(tnc))
    if set(exp)!=set(tnc):
        missing_exp=sorted(set(tnc)-set(exp))
        missing_tnc=sorted(set(exp)-set(tnc))
        raise RuntimeError(f"optical/TNC node registry mismatch: missing exposure={missing_exp}, missing TNC={missing_tnc}")

    rows=[]
    mismatch=[]
    for node in nodes:
        e=exp[node]; t=tnc[node]
        bay_e=str(e["water_body"]).strip(); bay_t=str(t["water_body"]).strip()
        if bay_e!=bay_t or bay_e not in BAYS:
            mismatch.append(node); continue
        try:
            pre=float(t["tnc_pre_mg_g"]); post=float(t["tnc_post_mg_g"])
            dli=float(e["mean_daily_within_canopy_dli"])
            coverage=float(e["par_coverage_fraction"])
            valid_days=int(float(e["valid_daily_dli_count"]))
            common_days=int(float(e["common_overlap_days"]))
            dpre=parse_date(t["tnc_pre_date"]); dpost=parse_date(t["tnc_post_date"])
        except Exception as exc:
            raise RuntimeError(f"{node}: invalid numeric/date field: {exc}")
        interval=(dpost-dpre).days
        daily_pass=truth(e["daily_dli_qc_pass"])
        optical_pass=truth(e["optical_exposure_qc_pass"])
        tnc_pass=truth(t["tnc_pair_qc_pass"])
        interval_pass=39<=interval<=45
        primary=bool(optical_pass and tnc_pass and interval_pass)
        rows.append({
          "node_id":node,
          "water_body":bay_e,
          "tnc_pre_mg_g":pre,
          "tnc_post_mg_g":post,
          "mean_daily_within_canopy_dli":dli,
          "par_coverage_fraction":coverage,
          "valid_daily_dli_count":valid_days,
          "common_overlap_days":common_days,
          "pre_post_tnc_interval_days":interval,
          "daily_dli_qc_pass":daily_pass,
          "primary_qc_pass":primary,
        })
    if mismatch:
        raise RuntimeError(f"water-body mismatch for nodes: {mismatch}")

    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    audit={
      "schema":"tampa.optical_primary_input_builder.v1",
      "nodes":len(rows),
      "primary_qc_pass_nodes":sum(bool(r["primary_qc_pass"]) for r in rows),
      "nodes_by_water_body":{
        b:sum(r["water_body"]==b for r in rows) for b in BAYS
      },
      "primary_qc_pass_by_water_body":{
        b:sum(r["water_body"]==b and bool(r["primary_qc_pass"]) for r in rows) for b in BAYS
      },
      "rule":"primary_qc_pass = optical_exposure_qc_pass AND tnc_pair_qc_pass AND pre/post TNC interval 39-45 days",
      "claim_boundary":[
        "The join does not fit or choose an optical model.",
        "A TNC pair that fails its frozen laboratory/sampling QC cannot be restored by good PAR coverage.",
        "A PAR node that fails optical QC cannot be restored by a favorable TNC value."
      ]
    }
    apath=Path(a.audit_out); apath.parent.mkdir(parents=True,exist_ok=True)
    apath.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
