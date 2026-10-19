#!/usr/bin/env python3
"""Validate candidate -> approved mark -> TNC core -> future same-mark BB.

This is only an identity/provenance gate. It does not authorize fieldwork,
certify genuine approvals, read a full survey census, or fit ecological effects.
"""
import argparse,csv,datetime as dt,hashlib,json,math
from pathlib import Path
from collections import Counter,defaultdict

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
ANCHORS=("q25","q50","q75")
CAND={"node_id","water_body","anchor_id","point_location_id","site_m","baseline_bb_anchor","baseline_survey_date","planned_tnc_date","current_eligibility_evidence","sampling_authority_status"}
APPR={"node_id","water_body","anchor_id","point_location_id","approval_reference_id","approved_before_collection","anchor_freeze_date"}
CORE={"node_id","water_body","anchor_id","point_location_id","core_id","core_collection_date","anchor_tnc","anchor_tnc_qc_pass"}
FUT={"node_id","water_body","point_location_id","future_survey_date","future_bb_anchor"}
PRIMARY=("node_id","water_body","anchor_id","baseline_bb_anchor","anchor_tnc","future_bb_anchor","anchor_tnc_qc_pass")

def check(r,expected,kind):
    if set(r)!=expected: raise ValueError(f"{kind}: missing/extra/forbidden fields")
def day(x,kind):
    try: return dt.date.fromisoformat(str(x))
    except (ValueError,TypeError) as e: raise ValueError(f"{kind}: invalid date") from e
def yes(x,kind):
    x=str(x).lower().strip()
    if x in ("true","1","yes"): return True
    if x in ("false","0","no"): return False
    raise ValueError(f"{kind}: not a boolean")
def num(x,low,high):
    try:
        v=float(x)
        return v if math.isfinite(v) and low<=v<=high else None
    except (ValueError,TypeError): return None

def build(candidates,approvals,cores,future):
    if not all((candidates,approvals,cores,future)):
        raise ValueError("all four externally supplied input registries required")
    selection,by_node,seen={},defaultdict(list),set()
    for row in candidates:
        check(row,CAND,"baseline candidate")
        node,bay,anchor,point=[str(row[k]).strip() for k in ("node_id","water_body","anchor_id","point_location_id")]
        key=node,anchor
        if not node or bay not in BAYS or anchor not in ANCHORS or not point or key in selection or point in seen:
            raise ValueError("duplicate or invalid candidate mark ID / anchor")
        if row["current_eligibility_evidence"]!="CURRENT_BASELINE_INPUT_ONLY" or row["sampling_authority_status"]!="NOT_AUTHORIZED":
            raise ValueError("candidate is not separate from sampling approval")
        site=num(row["site_m"],0,float("inf"))
        bb=num(row["baseline_bb_anchor"],0,5)
        if site is None or bb is None or bb<=0:
            raise ValueError("candidate requires positive numeric BB and site_m")
        baseline=day(row["baseline_survey_date"],"baseline")
        planned=day(row["planned_tnc_date"],"planned TNC")
        if abs((baseline-planned).days)>14: raise ValueError("frozen timing mismatch")
        item=dict(node_id=node,water_body=bay,anchor_id=anchor,point_location_id=point,
                  site_m=site,baseline_bb_anchor=bb,baseline=baseline,planned=planned)
        selection[key]=item;by_node[node].append(item);seen.add(point)
    for node,g in by_node.items():
        if len(g)!=3 or {v["anchor_id"] for v in g}!=set(ANCHORS):
            raise ValueError(f"{node}: noncanonical triplet")
        if len({v["water_body"] for v in g})!=1:
            raise ValueError(f"{node}: bay inconsistency")
        sites={v["anchor_id"]:v["site_m"] for v in g}
        if not sites["q25"]<sites["q50"]<sites["q75"]:
            raise ValueError(f"{node}: quartile site order mismatch")

    approved={}
    for row in approvals:
        check(row,APPR,"approval")
        key=row["node_id"],row["anchor_id"]
        if key not in selection or key in approved: raise ValueError("unknown/duplicate approved anchor")
        source=selection[key]
        if row["water_body"]!=source["water_body"] or row["point_location_id"]!=source["point_location_id"]:
            raise ValueError("approval point_location_id differs from frozen original anchor mark")
        if not yes(row["approved_before_collection"],"approval") or not str(row["approval_reference_id"]).strip():
            raise ValueError("missing external signed sampling approval reference")
        frozen=day(row["anchor_freeze_date"],"anchor freeze")
        if frozen>source["planned"]: raise ValueError("approval after TNC collection")
        approved[key]=frozen
    if set(approved)!=set(selection): raise ValueError("incomplete frozen approved triplet registry")

    measured,ids={},set()
    for row in cores:
        check(row,CORE,"TNC core")
        key=row["node_id"],row["anchor_id"]
        if key not in selection or key in measured: raise ValueError("unexpected/duplicated core anchor")
        source=selection[key]
        if row["water_body"]!=source["water_body"] or row["point_location_id"]!=source["point_location_id"]:
            raise ValueError("core point_location_id does not match frozen original anchor mark")
        cid=str(row["core_id"]).strip()
        if not cid or cid in ids: raise ValueError("core_id duplicate or blank")
        ids.add(cid)
        when=day(row["core_collection_date"],"TNC core collection")
        if when!=source["planned"] or when<approved[key]:
            raise ValueError("core collection or approval timing mismatch")
        measured[key]=(num(row["anchor_tnc"],0,float("inf")),yes(row["anchor_tnc_qc_pass"],"TNC QC"))
    # A missing or nonpassing core invalidates the original full triplet.

    point_to_key={source["point_location_id"]:key for key,source in selection.items()}
    outcomes={};observed_dates=defaultdict(set)
    for row in future:
        check(row,FUT,"future BB")
        key=point_to_key.get(str(row["point_location_id"]).strip())
        if key is None: raise ValueError("future location ID is not in the frozen candidate registry")
        if key in outcomes: raise ValueError("duplicate future mark; cannot choose/average post hoc")
        source=selection[key]
        if row["node_id"]!=source["node_id"] or row["water_body"]!=source["water_body"]:
            raise ValueError("future point ID linked to wrong node or bay")
        when=day(row["future_survey_date"],"future survey")
        if when<=source["baseline"] or when<=source["planned"]:
            raise ValueError("future mark survey must occur after baseline and TNC")
        observed_dates[key[0]].add(when)
        outcomes[key]=num(row["future_bb_anchor"],0,5)
    if any(len(dates)!=1 for dates in observed_dates.values()):
        raise ValueError("a node has multiple target visit dates; do not choose a favorable visit")

    complete,excluded,rows=Counter(),[],[]
    for node,g in sorted(by_node.items(),key=lambda item:(item[1][0]["water_body"],item[0])):
        bad=[]
        for v in g:
            key=node,v["anchor_id"]
            if key not in measured or measured[key][0] is None or not measured[key][1]:
                bad.append(f"{v['anchor_id']}:missing_or_failed_TNC_QC")
            if key not in outcomes or outcomes[key] is None:
                bad.append(f"{v['anchor_id']}:future_BB_missing_or_nonnumeric")
        if bad:
            excluded.append(dict(node_id=node,water_body=g[0]["water_body"],reasons=bad))
            continue
        for v in sorted(g,key=lambda x:ANCHORS.index(x["anchor_id"])):
            key=node,v["anchor_id"]
            rows.append(dict(node_id=node,water_body=v["water_body"],anchor_id=v["anchor_id"],
                             baseline_bb_anchor=v["baseline_bb_anchor"],anchor_tnc=measured[key][0],
                             future_bb_anchor=outcomes[key],anchor_tnc_qc_pass=True))
        complete[g[0]["water_body"]]+=1
    n=sum(complete.values())
    status=("PASS_LINEAGE_FOR_FROZEN_PRIMARY_INPUT" if n>=36 and all(complete[b]>=6 for b in BAYS)
            else "STOP_COMPLETE_TRIPLET_GATE")
    return {
       "schema":"tampa.anchor_TNC_original_mark_lineage_v1",
       "status":status,
       "evidence_class":"SYNTHETIC_OR_EXTERNALLY_SUPPLIED_UNVERIFIED_SOURCE_ONLY",
       "candidate_nodes":len(by_node),"complete_nodes":n,
       "complete_nodes_by_bay":{b:complete[b] for b in BAYS},
       "excluded_nodes":excluded,"primary_input_rows":rows,"primary_input_columns":list(PRIMARY),
       "boundaries":[
         "Passing lineage cannot authenticate survey or permit; human provenance must be independently reviewed.",
         "Identity is matched on official node and point-location ID before emitting the original frozen seven-column model input.",
         "Unmeasured/nonnumeric future BB is missing, not focal absence; sampled focal absence may be numeric zero.",
         "No TNC effect, demographic mortality, physiological mechanism or restoration benefit is inferred here.",
         "Do not impute/reassign anchors, relax 36/6 gates, or rescue the primary with a supportive model."
       ]
    }

def csv_rows(path,columns):
    with path.open(newline="",encoding="utf-8-sig") as h:
        rd=csv.DictReader(h)
        if len(rd.fieldnames or [])!=len(set(rd.fieldnames or [])) or set(rd.fieldnames or [])!=columns:
            raise ValueError(f"{path}: bad schema or prohibited extra columns")
        return list(rd)

def main():
    p=argparse.ArgumentParser()
    for flag in ("candidate","approval","tnc","future","report"):
        p.add_argument("--"+flag,type=Path,required=True)
    p.add_argument("--primary-input",type=Path)
    a=p.parse_args()
    files=((a.candidate,CAND),(a.approval,APPR),(a.tnc,CORE),(a.future,FUT))
    result=build(*(csv_rows(path,cols) for path,cols in files))
    public={k:v for k,v in result.items() if k!="primary_input_rows"}
    public["sha256_inputs"]={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path,_ in files}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(public,indent=2,sort_keys=True)+"\n")
    if result["status"]!="PASS_LINEAGE_FOR_FROZEN_PRIMARY_INPUT":
        print(json.dumps(public,indent=2));raise SystemExit(2)
    if a.primary_input:
        if a.primary_input.exists(): raise ValueError("do not overwrite model input; use a new versioned file path")
        a.primary_input.parent.mkdir(parents=True,exist_ok=True)
        with a.primary_input.open("w",newline="") as h:
            writer=csv.DictWriter(h,fieldnames=PRIMARY,lineterminator="\n")
            writer.writeheader()
            writer.writerows(result["primary_input_rows"])
    print(json.dumps(public,indent=2))

if __name__=="__main__":
    main()
