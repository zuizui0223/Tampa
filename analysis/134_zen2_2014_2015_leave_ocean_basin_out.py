#!/usr/bin/env python3
"""Post-outcome leave-one-BASIN-out ZEN2 2014->2015 ecological transport.

The entire 2014 and 2015 source outcome cohort was previously opened.
Two coarse original geographic groups (Pacific n=8; Atlantic/Mediterranean
n=6) are swapped as calibration versus evaluation domains. This is NOT
independent external validation across numerous ecosystems, because there
are only two basin groups and one coordinated published ZEN2 program.

Compare held-out basin prediction error against training-basin mean of the
SAME outcome in each fold. No target-site data is used to learn a coefficient.
This design was proposed AFTER earlier site-LOOCV success and is exploratory.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE2014=ROOT/"results/zen2_2014_prior_state_2015_trophic_risk_verified_20261124.json"
FILEGEO=ROOT/"results/zen2_2014_2015_geographic_link_verified_20261124.json"
OUTCOMES=(
    ("year2014_shoot_density","year2015_ambient_shoot_density","log1p_response"),
    ("year2014_shoot_density","year2015_edge_minus_interior_risk","risk_difference"),
    ("year2014_shoot_density","year2015_eighty_minus_ambient_risk","risk_difference"),
)

def module(name,filename):
    s=importlib.util.spec_from_file_location(name,ROOT/"analysis"/filename)
    m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

BASIN=module("source_geography_132","132_zen2_crossyear_basin_latitude_rank_sensitivity.py")
CV=module("crossyear_site_cv_133","133_zen2_crossyear_structure_vs_trophic_site_cv.py")
BASINS=("Pacific","Atlantic_Mediterranean")

def execute(data,geo,restrict_km=25.0):
    if data.get("schema")!="tampa.zen2_nearest_subsite_2014_prior_state_2015_interaction_exploratory_v1":
        raise ValueError("Unexpected 2014–2015 source original ecological schema")
    if geo.get("schema")!="tampa.zen2_2014_2015_source_geographic_link_audit_v1":
        raise ValueError("Wrong source geographic gate")
    if data.get("source_shas")!=geo.get("source_shas"):
        raise ValueError("Source identity mismatch")
    if restrict_km not in (5.0,25.0):
        raise ValueError("Postoutcome arbitrary geographic threshold forbidden")
    loc={
        x["source_2015_site"]:x["source_2015_lat_lon"]
        for x in geo["candidates"] if x["eligible_as_prior_site_context"]
    }
    by=[]
    for row in data["candidate_sites"]:
        site=row["site_code"]
        if site not in loc:raise ValueError("2015 ecological outcome missing a source-geography match")
        if row["nearest_distance_km"]>restrict_km:
            continue
        b=BASIN.ocean(loc[site][1])
        by.append({**row,"ocean":b})
    n=len(by)
    if (restrict_km==25 and n!=14) or (restrict_km==5 and n!=13):
        raise ValueError("Unexpected fixed geographic analysis cohort")
    groups={k:[v for v in by if v["ocean"]==k] for k in BASINS}
    if restrict_km==25 and [len(groups[k]) for k in BASINS]!=[8,6]:
        raise ValueError("Incorrect 8+6 basin frame")
    if restrict_km==5 and [len(groups[k]) for k in BASINS]!=[7,6]:
        raise ValueError("Incorrect 7+6 basin frame")
    result=[]
    for pred,outcome,target_scale in OUTCOMES:
        details=[]
        for basin in BASINS:
            train=[r for r in by if r["ocean"]!=basin]
            test=groups[basin]
            x_train=[CV.transformed(r[pred],"log1p_predictor") for r in train]
            y_train=[CV.transformed(r[outcome],target_scale) for r in train]
            fitted=CV.fit_ols(x_train,y_train)
            baseline=statistics.mean(y_train)
            entries=[]
            for site in test:
                yy=CV.transformed(site[outcome],target_scale)
                predx=CV.transformed(site[pred],"log1p_predictor")
                entries.append({
                    "site":site["site_code"],"test_domain":basin,
                    "observed":yy,
                    "prediction":fitted["intercept"]+fitted["slope"]*predx,
                    "reference_prediction":baseline,
                })
            model_sse=sum((z["observed"]-z["prediction"])**2 for z in entries)
            ref_sse=sum((z["observed"]-z["reference_prediction"])**2 for z in entries)
            if ref_sse<=1e-14:raise ValueError("No baseline variance in out-of-basin evaluation")
            details.append({
                "held_out_basin":basin,
                "n_test_site_codes":len(test),
                "n_train_site_codes":len(train),
                "training_only_predictor_slope":fitted["slope"],
                "predictive_r2_over_training_basin_mean":1-model_sse/ref_sse,
                "rmse_prediction":math.sqrt(model_sse/len(entries)),
                "rmse_baseline":math.sqrt(ref_sse/len(entries)),
                "model_sse":model_sse,
                "baseline_sse":ref_sse,
                "site_level_predictions":entries,
            })
        total_model=sum(z["model_sse"] for z in details)
        total_reference=sum(z["baseline_sse"] for z in details)
        result.append({
            "prior_predictor":pred,
            "subsequent_target":outcome,
            "outcome_scale":target_scale,
            "n_test_sites_combined":n,
            "leave_one_basin_out_r2_against_training_basin_mean":1-total_model/total_reference,
            "two_held_out_basin_evaluations":details,
        })
    return {
        "schema":"tampa.zen2_leave_one_ocean_basin_out_2014_2015_exploratory_v1",
        "evidence_class":"response_exposed_posthoc_geographic_transport_not_external_prospective_validation",
        "source_shas":data["source_shas"],
        "distance_gate_km":restrict_km,
        "site_count":n,
        "basin_site_counts":{k:len(v) for k,v in groups.items()},
        "cv_method":"train on 2014->2015 data in one basin, evaluate on all geographical sites in other basin; each basin once",
        "models":result,
        "hard_limits":[
            "Two broad ocean categories do not constitute independent continental validation trials.",
            "Model choice and this domain-swap audit were selected after inspecting 14-site overall structure-vs-risk CV.",
            "One coordinated published ZEN2 program, not a meta-analysis and not another unseen field study.",
            "The source biodiversity/function outcome is a tethered 24-h predation contrast subject to ceiling at many sites.",
            "Observed stability of relative site shoot density need not indicate same-meadow shoot survival or plant physiology.",
            "A domain-transfer R2 compares to the OTHER basin's training mean and is sensitive to between-basin mean shifts.",
            "Risk results may differ by which tether endpoint is selected; report all three fixed endpoints, not only positive ones.",
            "No causal mechanistic feedback, long-term survival or cross-species universal restoration threshold is established.",
        ]
    }

def report():
    first=json.loads(FILE2014.read_text())
    geo=json.loads(FILEGEO.read_text())
    return {
        "schema":"tampa.zen2_cross_basin_transport_pair_v1",
        "source_original_result":str(FILE2014.relative_to(ROOT)),
        "source_geo_result":str(FILEGEO.relative_to(ROOT)),
        "source_outcomes_already_opened":True,
        "all_25km":execute(first,geo,restrict_km=25),
        "strict_5km":execute(first,geo,restrict_km=5),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    out=json.dumps(report(),ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(out,encoding="utf-8")
    else:print(out,end="")

if __name__=="__main__":
    main()
