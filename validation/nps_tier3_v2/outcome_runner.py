#!/usr/bin/env python3
"""Once-only NPS Tier-3 Zostera quantitative early-warning validation v2."""
from __future__ import annotations

import csv, io, json, math, re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"final_outcome_contract.json").read_text())
AUTH=ROOT/"OUTCOME_AUTHORIZED_ONCE"
OUT=ROOT/"terminal_outcome_result.json"

class TerminalStop(RuntimeError): pass

AUDIT={"response_gets":0,"response_bytes_opened":0,"response_rows_opened":0,"response_values_opened":False,
       "model_fits":0,"predictive_scores":0}

def req_text(x,label):
    s="" if x is None else str(x).strip()
    if not s: raise TerminalStop(f"blank_required:{label}")
    return s

def parse_cover(x,rownum):
    s="" if x is None else str(x).strip()
    if not s: raise TerminalStop(f"blank_percent_cover:row{rownum}")
    if s==C["parser"]["percent_cover_missing_token"]:
        return None
    try: v=float(s)
    except Exception as exc: raise TerminalStop(f"nonnumeric_percent_cover:row{rownum}:{s!r}") from exc
    if not math.isfinite(v): raise TerminalStop(f"nonfinite_percent_cover:row{rownum}")
    lo,hi=C["parser"]["percent_cover_valid_range"]
    if not (lo<=v<=hi): raise TerminalStop(f"percent_cover_out_of_range:row{rownum}:{v}")
    return float(v)

def parse_date(x,rownum):
    s=req_text(x,f"Date row {rownum}")
    try: return datetime.strptime(s,C["parser"]["date_format"]).date()
    except ValueError as exc: raise TerminalStop(f"date_parse_failure:row{rownum}:{s}") from exc

def parse_quadrat(x,rownum):
    s=req_text(x,f"Quadrat row {rownum}")
    try: v=float(s)
    except Exception as exc: raise TerminalStop(f"quadrat_nonnumeric:row{rownum}:{s}") from exc
    if not math.isfinite(v) or not v.is_integer(): raise TerminalStop(f"quadrat_not_integer:row{rownum}:{s}")
    v=int(v); lo,hi=C["parser"]["quadrat_integer_range"]
    if not (lo<=v<=hi): raise TerminalStop(f"quadrat_out_of_range:row{rownum}:{v}")
    return v

def download_once():
    req=Request(C["source"]["response_url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier3-v2/1.0"})
    with urlopen(req,timeout=90) as r:
        if r.status!=200: raise TerminalStop(f"response_http_{r.status}")
        data=r.read(int(C["source"]["expected_bytes"])+1)
    AUDIT["response_gets"]+=1; AUDIT["response_bytes_opened"]+=len(data); AUDIT["response_values_opened"]=True
    if len(data)!=int(C["source"]["expected_bytes"]):
        raise TerminalStop(f"response_size_drift:{len(data)}")
    return data

def parse_rows(data):
    try: text=data.decode(C["parser"]["encoding"])
    except UnicodeDecodeError as exc: raise TerminalStop("response_encoding_failure") from exc
    reader=csv.reader(io.StringIO(text,newline=""),delimiter=C["parser"]["delimiter"])
    try: header=next(reader)
    except StopIteration as exc: raise TerminalStop("empty_response") from exc
    if header!=C["source"]["expected_physical_header"]:
        raise TerminalStop(f"header_drift:{header!r}")
    col={h:i for i,h in enumerate(header)}
    out=[]
    seen_ids=set()
    for rownum,row in enumerate(reader,start=2):
        AUDIT["response_rows_opened"]+=1
        if len(row)!=int(C["parser"]["exact_row_width"]):
            raise TerminalStop(f"row_width:{rownum}:{len(row)}")
        for field in C["parser"]["required_nonblank"]:
            req_text(row[col[field]],f"{field} row {rownum}")
        rid=req_text(row[col["ID"]],f"ID row {rownum}")
        if rid in seen_ids: raise TerminalStop(f"duplicate_ID:{rid}")
        seen_ids.add(rid)
        species=req_text(row[col["Species"]],f"Species row {rownum}")
        if species not in C["parser"]["allowed_species_codes"]:
            raise TerminalStop(f"unexpected_species_code:row{rownum}:{species}")
        d=parse_date(row[col["Date"]],rownum)
        q=parse_quadrat(row[col["Quadrat"]],rownum)
        cover=parse_cover(row[col["Percent Cover"]],rownum)
        out.append({
            "ID":rid,
            "EventID":req_text(row[col["EventID"]],f"EventID row {rownum}"),
            "Location":req_text(row[col["Location"]],f"Location row {rownum}"),
            "SGNetCode":req_text(row[col["SGNetCode"]],f"SGNetCode row {rownum}"),
            "Transect":req_text(row[col["Transect"]],f"Transect row {rownum}"),
            "Quadrat":q,
            "Species":species,
            "Date":d,
            "Year":d.year,
            "PercentCover":cover,
        })
    if not out: raise TerminalStop("no_data_rows")
    return out

def annualize(rows):
    # one species row per permanent quadrat/event is expected; multiple dates within a
    # year are pooled without inventing bare-quadrat observations.
    cells=defaultdict(lambda:{"dates":set(),"species":defaultdict(list),"Location":set()})
    for r in rows:
        key=(r["SGNetCode"],r["Transect"],r["Quadrat"],r["Year"])
        rec=cells[key]
        rec["dates"].add(r["Date"].isoformat())
        rec["Location"].add(r["Location"])
        rec["species"][r["Species"]].append(r["PercentCover"])
    for key,rec in cells.items():
        if len(rec["Location"])!=1: raise TerminalStop(f"location_drift_within_quadrat_year:{key}")
        for sp,vals in rec["species"].items():
            # more than one row per species/date is not allowed; repeated dates can occur
            # only if separate events but are annualized by mean.
            pass

    groups=defaultdict(list)
    for (site,tran,q,year),rec in cells.items():
        groups[(site,tran,year)].append((q,rec))

    states=[]
    minobs=int(C["annual_state"]["minimum_reobserved_quadrats"])
    minquant=int(C["annual_state"]["minimum_quantitative_quadrats"])
    for (site,tran,year),items in groups.items():
        quadrat_seen=set()
        zm_seen=set()
        quantitative=[]
        dates=set()
        locations=set()
        for q,rec in items:
            quadrat_seen.add(q); dates.update(rec["dates"]); locations.update(rec["Location"])
            species=rec["species"]
            if "ZM" in species:
                zm_seen.add(q)
                vals=[v for v in species["ZM"] if v is not None]
                if vals:
                    quantitative.append(float(np.mean(vals)))
                # if ZM was observed but cover was only NA, quantitative cover for this
                # quadrat is missing, not zero.
            else:
                # Quadrat has at least one observed seagrass species but no ZM row.
                # Under the EML 'Species of seagrass observed' semantics this is a
                # re-observed vegetated quadrat with ZM not observed, represented as 0
                # only for the focal cover state.
                quantitative.append(0.0)
        if len(locations)!=1: raise TerminalStop(f"location_drift_within_transect_year:{site}:{tran}:{year}")
        if len(quadrat_seen)<minobs or len(quantitative)<minquant:
            continue
        frequency=len(zm_seen)/len(quadrat_seen)
        states.append({
            "node_id":f"{site}::{tran}",
            "SGNetCode":site,
            "Transect":tran,
            "Location":next(iter(locations)),
            "year":int(year),
            "observed_quadrat_count":int(len(quadrat_seen)),
            "quantitative_quadrat_count":int(len(quantitative)),
            "survey_count":int(len(dates)),
            "focal_frequency":float(frequency),
            "focal_mean_cover":float(np.mean(quantitative)),
            "recorded_presence":bool(len(zm_seen)>0),
            "recorded_loss_state":bool(len(zm_seen)==0),
        })
    # uniqueness
    seen=set()
    for s in states:
        k=(s["node_id"],s["year"])
        if k in seen: raise TerminalStop(f"duplicate_annual_state:{k}")
        seen.add(k)
    return states

def transitions(states):
    by=defaultdict(dict)
    for s in states: by[s["node_id"]][s["year"]]=s
    rows=[]
    for node,ys in by.items():
        for y,src in sorted(ys.items()):
            if not src["recorded_presence"]: continue
            tgt=ys.get(y+1)
            if tgt is None: continue
            if tgt["recorded_presence"]: lab=0
            elif tgt["recorded_loss_state"]: lab=1
            else: continue
            rows.append({
                "node_id":node,"SGNetCode":src["SGNetCode"],"Transect":src["Transect"],"Location":src["Location"],
                "source_year":int(y),"target_year":int(y+1),
                "log_observed_quadrat_count":float(math.log1p(src["observed_quadrat_count"])),
                "log_survey_count":float(math.log1p(src["survey_count"])),
                "focal_frequency":float(src["focal_frequency"]),"focal_mean_cover":float(src["focal_mean_cover"]),
                "recorded_loss":int(lab),
            })
    return pd.DataFrame(rows)

def count_gate(states,tr):
    g=C["estimability_gate"]
    s={
      "annual_units":len(states),
      "source_positive_consecutive_transitions":len(tr),
      "recorded_losses":int(tr.recorded_loss.sum()) if len(tr) else 0,
      "recorded_persistence":int((1-tr.recorded_loss).sum()) if len(tr) else 0,
    }
    ok=(s["annual_units"]>=g["minimum_annual_units"] and
        s["source_positive_consecutive_transitions"]>=g["minimum_source_positive_consecutive_transitions"] and
        s["recorded_losses"]>=g["minimum_recorded_losses"] and
        s["recorded_persistence"]>=g["minimum_recorded_persistence"])
    yrs=[]
    if len(tr):
        for y in sorted(tr.target_year.unique()):
            train=tr[tr.target_year<y]
            if int(train.recorded_loss.sum())>=g["per_target_year_training_min_prior_losses"] and int((1-train.recorded_loss).sum())>=g["per_target_year_training_min_prior_persistence"]:
                yrs.append(int(y))
    s["prospectively_scorable_target_years"]=yrs
    s["prospectively_scorable_target_year_count"]=len(yrs)
    s["passed"]=bool(ok and len(yrs)>=g["minimum_scored_target_years"])
    return s

def model(num,cat):
    hp=C["model"]["hyperparameters"]
    prep=ColumnTransformer([("num",StandardScaler(),num),("cat",OneHotEncoder(handle_unknown="ignore"),cat)])
    return Pipeline([("prep",prep),("clf",LogisticRegression(C=hp["C"],max_iter=hp["max_iter"],solver=hp["solver"]))])

def score(tr,years):
    bn=C["model"]["baseline_numeric"]; cat=C["model"]["baseline_categorical"]; an=bn+C["model"]["augmentation"]
    rows=[]; py=[]; pb=[]; pa=[]
    eps=C["scoring"]["probability_clip"]
    for y in years:
        train=tr[tr.target_year<y].copy(); test=tr[tr.target_year==y].copy()
        if test.empty: raise TerminalStop(f"empty_test_year:{y}")
        mb=model(bn,cat); ma=model(an,cat)
        mb.fit(train[bn+cat],train.recorded_loss); AUDIT["model_fits"]+=1
        ma.fit(train[an+cat],train.recorded_loss); AUDIT["model_fits"]+=1
        b=np.clip(mb.predict_proba(test[bn+cat])[:,1],eps,1-eps)
        a=np.clip(ma.predict_proba(test[an+cat])[:,1],eps,1-eps)
        yy=test.recorded_loss.to_numpy(int)
        lb=float(log_loss(yy,b,labels=[0,1])); la=float(log_loss(yy,a,labels=[0,1])); AUDIT["predictive_scores"]+=2
        rows.append({"target_year":int(y),"n":len(test),"losses":int(yy.sum()),"persistence":int(len(yy)-yy.sum()),
                     "baseline_log_loss":lb,"augmented_log_loss":la,"augmented_minus_baseline":la-lb,
                     "winner":"augmented" if la<lb else ("baseline" if lb<la else "tie")})
        py.extend(yy.tolist());pb.extend(b.tolist());pa.extend(a.tolist())
    bm=float(np.mean([r["baseline_log_loss"] for r in rows])); am=float(np.mean([r["augmented_log_loss"] for r in rows]))
    aw=sum(r["winner"]=="augmented" for r in rows); bw=sum(r["winner"]=="baseline" for r in rows)
    need=math.ceil(0.60*len(rows))
    if am<bm and aw>=need: status="favorable_external_early_warning"
    elif bm<am and bw>=need: status="adverse_external_early_warning"
    else: status="no_confirmed_external_early_warning"
    sec={"pooled_baseline_brier":float(brier_score_loss(py,pb)),"pooled_augmented_brier":float(brier_score_loss(py,pa))}
    if len(set(py))==2:
        sec["pooled_baseline_auc"]=float(roc_auc_score(py,pb));sec["pooled_augmented_auc"]=float(roc_auc_score(py,pa))
    return {"status":status,"baseline_macro_log_loss":bm,"augmented_macro_log_loss":am,"augmented_minus_baseline":am-bm,
            "augmented_year_wins":aw,"baseline_year_wins":bw,"tie_years":len(rows)-aw-bw,"required_win_count":need,
            "year_scores":rows,"secondary":sec}

def terminal(status,reason=None,extra=None):
    out={"schema":"tampa.nps_tier3_external_early_warning_v2.terminal_outcome_result",
         "attempt_id":C["attempt_id"],"terminal_status":status,"reason":reason,
         "response_access_audit":dict(AUDIT),
         "counts_as_external_predictive_evidence":status in {"favorable_external_early_warning","adverse_external_early_warning","no_confirmed_external_early_warning"}}
    if extra: out.update(extra)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))

def main():
    if not AUTH.exists(): raise RuntimeError("authorization marker missing")
    a=json.loads(AUTH.read_text())
    if a.get("authorized") is not True or a.get("attempt_id")!=C["attempt_id"]: raise RuntimeError("authorization marker mismatch")
    try:
        data=download_once()
        raw=parse_rows(data)
        states=annualize(raw)
        tr=transitions(states)
        cg=count_gate(states,tr)
        if not cg["passed"]:
            terminal(C["estimability_gate"]["failure_status"],"frozen_estimability_gate_failed",{
                "estimability":cg,
                "state_summary":{"annual_units":len(states),"nodes":len(set(s["node_id"] for s in states)),
                                 "years":sorted(set(s["year"] for s in states)),
                                 "present_units":sum(s["recorded_presence"] for s in states),
                                 "loss_state_units":sum(s["recorded_loss_state"] for s in states)}
            });return
        res=score(tr,cg["prospectively_scorable_target_years"])
        terminal(res["status"],None,{
            "estimability":cg,"primary_result":res,
            "state_summary":{"annual_units":len(states),"nodes":len(set(s["node_id"] for s in states)),
                             "years":sorted(set(s["year"] for s in states)),
                             "present_units":sum(s["recorded_presence"] for s in states),
                             "loss_state_units":sum(s["recorded_loss_state"] for s in states)},
            "scientific_boundary":{
                "endpoint":"next-year loss of recorded Zostera from re-observed seagrass-bearing permanent quadrats",
                "not_claimed":["demographic extinction","bare-habitat loss","causal nutrient mechanism","universal early-warning effect"]
            }
        })
    except TerminalStop as exc:
        terminal("terminal_protocol_or_schema_stop",str(exc))
    except Exception as exc:
        terminal("terminal_execution_stop",f"{type(exc).__name__}:{exc}")

if __name__=="__main__":main()
