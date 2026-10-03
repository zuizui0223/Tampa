#!/usr/bin/env python3
"""Baseline-only feasibility audit for within-transect anchor-level TNC diagnostics.

Uses already-open 2023-2025 monitoring state only to ask whether the three
predeclared distinct TNC anchors can be linked to quantitative point-level
Thalassia Braun-Blanquet state.

No TNC values and no future response are available or used.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES={
 "event":{"url":f"{BASE}/event.csv","size":24654717,"blob":"583b4d4e328290ab065346579eb4f29f03ea0f99"},
 "occurrence":{"url":f"{BASE}/occurrence.csv","size":12508487,"blob":"d34aeb5aedb72459d1e04059629cb09450df929e"},
 "emof":{"url":f"{BASE}/emof.csv","size":16449353,"blob":"e463046726080334637824555309fd89c7c447da"},
}
CORE=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
YEARS=(2023,2024,2025)
FOCAL="Thalassia testudinum"
BB_TYPE="seagrass percent cover (Braun-Blanquet scale)"

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def fetch(spec):
    req=Request(spec["url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-anchor-BB-preflight/1.0"})
    with urlopen(req,timeout=240) as r:
        data=r.read(spec["size"]+1)
    if len(data)!=spec["size"]:
        raise RuntimeError(f"source size drift: {len(data)} != {spec['size']}")
    if git_blob_sha1(data)!=spec["blob"]:
        raise RuntimeError("source blob drift")
    return data

def parse_site(location_id:str):
    try: return float(location_id.rsplit(":",1)[-1])
    except Exception: return None

def nearest_unique(vals,target,used):
    cand=sorted((abs(x-target),x) for x in vals if x not in used)
    return cand[0][1] if cand else None

def parse_numeric(v):
    try: return float(v)
    except Exception: return None

def main(out:Path):
    event=fetch(FILES["event"])
    occ=fetch(FILES["occurrence"])
    emof=fetch(FILES["emof"])

    # Recent eligible visits and child point geometry.
    parents={}
    children=defaultdict(list)
    point_meta={}
    rd=csv.DictReader(io.StringIO(event.decode("utf-8"),newline=""))
    for row in rd:
        typ=row["eventType"].strip()
        if typ=="Transect":
            year=int(row["year"] or row["eventDate"][:4])
            wb=row["waterBody"].strip()
            if year in YEARS and wb in CORE:
                eid=row["eventID"].strip()
                parents[eid]={
                    "node_id":row["locationID"].strip(),
                    "year":year,
                    "water_body":wb,
                    "date":row["eventDate"][:10],
                }
        elif typ=="Point":
            pid=row["parentEventID"].strip()
            if pid in parents:
                eid=row["eventID"].strip()
                site=parse_site(row["locationID"].strip())
                if site is None: continue
                children[pid].append(eid)
                point_meta[eid]={"pid":pid,"site_m":site}

    eligible={p for p in parents if len(children.get(p,[]))>=3}

    # Focal occurrence IDs.
    focal_occ={}
    rd=csv.DictReader(io.StringIO(occ.decode("utf-8"),newline=""))
    for row in rd:
        eid=row["eventID"].strip()
        if eid not in point_meta or point_meta[eid]["pid"] not in eligible:
            continue
        if row["scientificName"].strip()==FOCAL and row["occurrenceStatus"].strip()=="present":
            focal_occ[eid]=row["occurrenceID"].strip()

    # Quantitative BB by occurrence ID.
    bb_by_occ={}
    rd=csv.DictReader(io.StringIO(emof.decode("utf-8"),newline=""))
    for row in rd:
        oid=row["occurrenceID"].strip()
        if oid and row["measurementType"].strip()==BB_TYPE:
            bb_by_occ[oid]=row["measurementValue"].strip()

    # Annualize visit-level focal frequency, preserve all pids in latest year.
    annual=defaultdict(lambda:{"visits":0,"freq":0.0,"water_body":None,"pids":[]})
    for pid in eligible:
        p=parents[pid]; pts=children[pid]
        f=sum(eid in focal_occ for eid in pts)/len(pts)
        k=(p["node_id"],p["year"])
        z=annual[k]
        z["visits"]+=1; z["freq"]+=f; z["water_body"]=p["water_body"]; z["pids"].append(pid)

    latest={}
    for (node,year),z in annual.items():
        x={
            "node_id":node,"year":year,"water_body":z["water_body"],
            "focal_frequency":z["freq"]/z["visits"],"pids":z["pids"]
        }
        if node not in latest or year>latest[node]["year"]:
            latest[node]=x

    latest_pos=[x for x in latest.values() if x["focal_frequency"]>0]
    if len(latest_pos)!=41:
        raise RuntimeError(f"recent four-bay positive node drift: {len(latest_pos)} != 41")

    rows=[]
    anchor_rows=[]
    for n in latest_pos:
        # Mark is focal-positive if it was positive in >=1 eligible visit of latest year.
        by_site=defaultdict(list)
        for pid in n["pids"]:
            for eid in children[pid]:
                by_site[point_meta[eid]["site_m"]].append(eid)

        positive_sites=sorted(
            site for site,eids in by_site.items()
            if any(eid in focal_occ for eid in eids)
        )

        if len(positive_sites)<3:
            rows.append({
                "node_id":n["node_id"],"water_body":n["water_body"],"year":n["year"],
                "positive_meter_marks":len(positive_sites),
                "three_distinct_anchor_design":False,
                "anchors_all_quantitative_bb":False,
                "anchor_site_m":[]
            })
            continue

        q=np.quantile(np.asarray(positive_sites,float),[.25,.5,.75])
        used=set(); anchors=[]
        for target in q:
            hit=nearest_unique(positive_sites,float(target),used)
            if hit is None: raise RuntimeError("unique anchor assignment failed")
            anchors.append(hit); used.add(hit)

        node_ok=True
        for site in anchors:
            vals=[]; invalid=[]
            for eid in by_site[site]:
                if eid in focal_occ:
                    raw=bb_by_occ.get(focal_occ[eid])
                    val=parse_numeric(raw) if raw is not None else None
                    if val is None:
                        invalid.append(raw if raw is not None else "MISSING_BB")
                    else:
                        vals.append(val)
                else:
                    # The point was sampled but focal Thalassia was not recorded.
                    vals.append(0.0)
            ok=bool(vals) and not invalid
            node_ok=node_ok and ok
            anchor_rows.append({
                "node_id":n["node_id"],"water_body":n["water_body"],"year":n["year"],
                "site_m":site,"baseline_visit_values":vals,
                "invalid_present_bb_values":invalid,
                "baseline_bb_mean":float(np.mean(vals)) if ok else None,
                "quantitative_baseline_ok":ok
            })

        rows.append({
            "node_id":n["node_id"],"water_body":n["water_body"],"year":n["year"],
            "positive_meter_marks":len(positive_sites),
            "three_distinct_anchor_design":True,
            "anchors_all_quantitative_bb":bool(node_ok),
            "anchor_site_m":anchors
        })

    ge3=[x for x in rows if x["three_distinct_anchor_design"]]
    ok=[x for x in rows if x["anchors_all_quantitative_bb"]]
    by={}
    for wb in CORE:
        d=[x for x in rows if x["water_body"]==wb]
        by[wb]={
            "recent_positive_nodes":len(d),
            "three_distinct_anchor_nodes":sum(x["three_distinct_anchor_design"] for x in d),
            "three_anchor_quantitative_bb_nodes":sum(x["anchors_all_quantitative_bb"] for x in d),
        }

    minimum_in_bay=min(by[x]["three_anchor_quantitative_bb_nodes"] for x in CORE)
    passed=(len(ok)>=36 and minimum_in_bay>=6)

    result={
      "schema":"tampa.tnc_anchor_bb_four_bay_preflight_v1",
      "status":"anchor_level_quantitative_diagnostic_feasible" if passed else "anchor_level_quantitative_diagnostic_not_supported",
      "evidence_class":"response-open baseline design feasibility only; no TNC and no future response",
      "source":{"repository":"tbep-tech/obis-example","commit":COMMIT,"years":list(YEARS)},
      "frozen_gate":{
        "minimum_nodes_with_three_distinct_quantitative_anchors":36,
        "minimum_nodes_per_bay":6,
        "nodes_with_three_distinct_positive_anchors":len(ge3),
        "nodes_with_three_distinct_quantitative_bb_anchors":len(ok),
        "minimum_quantitative_nodes_in_any_bay":minimum_in_bay,
        "passed":passed,
        "by_water_body":by
      },
      "bb_semantics":{
        "present_numeric":"Use numeric Braun-Blanquet measurementValue.",
        "sampled_focal_absent":"Code as 0 for the baseline visit.",
        "present_but_reported_without_numeric_cover":"Quantitative anchor invalid; do not convert 'Reported' to a numeric cover score.",
        "annual_anchor_summary":"Mean across eligible visits in the latest node-year only when every focal-present visit has numeric BB."
      },
      "prospective_diagnostic":{
        "eligible_nodes":"Only nodes with three distinct frozen q25/q50/q75 Thalassia-positive anchors and quantitative baseline BB at all three anchors.",
        "future_outcome":"Same permanent meter-mark Thalassia Braun-Blanquet score at the next fixed-transect survey; sampled focal absence may be coded 0, present nonnumeric 'Reported' is quantitatively missing.",
        "predictor":"anchor-level rhizome TNC centered within node: anchor_TNC - mean(anchor_TNC across the three anchors)",
        "candidate_model":"future_BB_anchor ~ baseline_BB_anchor + within_node_centered_anchor_TNC + node_fixed_effect",
        "uncertainty":"cluster/bootstrap or permutation at stable-node level, frozen before future outcome access",
        "purpose":"Test whether local reserve differences within the same transect predict local future quantitative state after stable node identity is removed."
      },
      "intervention_boundary":[
        "This diagnostic is allowed only if the field protocol freezes a core offset judged not to disturb the permanent meter-mark monitoring footprint.",
        "Core anchor position may not move after TNC assay or preliminary PAR/hydrodynamic results.",
        "If coring may plausibly alter the paired permanent meter mark, the anchor-level future diagnostic is invalid for that anchor rather than interpreted ecologically."
      ],
      "claim_boundary":[
        "This is a prospective secondary diagnostic, not a replacement for the node-level primary TNC test.",
        "Within-node centering and node fixed effects weaken stable transect-level site-template confounding but do not remove persistent meter-mark microhabitat differences or time-varying local causes.",
        "Braun-Blanquet is an ordinal cover score; effect size is interpreted as association on the frozen score scale, not exact percent-cover change.",
        "Do not use binary re-recording as recovery."
      ],
      "nodes":sorted(rows,key=lambda x:(x["water_body"],x["node_id"])),
      "anchors":sorted(anchor_rows,key=lambda x:(x["water_body"],x["node_id"],x["site_m"]))
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","frozen_gate","bb_semantics","prospective_diagnostic")},indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("results/generated_tnc_anchor_bb_four_bay/tnc_anchor_bb_four_bay_preflight_v1.json"))
    a=ap.parse_args(); main(a.out)
