#!/usr/bin/env python3
"""Build Tampa ecology Supplementary Tables S1-S9.

This script does not fit new models. It converts already-generated analysis outputs
and committed canonical result records into manuscript-facing CSV tables.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text())


def table_s1(primary: Path, out: Path):
    x=load_json(primary/"state_change_validation.json")
    rows=[]
    for segment,metrics in x["trend_audit"]["models"].items():
        for metric,variants in metrics.items():
            z=variants.get("season_effort_adjusted")
            if z is None:
                continue
            rows.append({
                "water_body":segment,
                "state":metric,
                "nodes":z["nodes"],
                "rows":z["rows"],
                "year_slope":z["year_slope"],
                "ci95_low":z["year_slope_ci95"][0],
                "ci95_high":z["year_slope_ci95"][1],
                "adjusted_for":";".join(z["adjusted_for"]),
            })
    pd.DataFrame(rows).to_csv(out/"Table_S1_post2016_state_slopes.csv",index=False)


def table_s2(nps: Path, out: Path):
    nodes=pd.read_csv(nps/"nps_tier3_cover_node_slopes.csv")
    node_rows=nodes.copy()
    node_rows.insert(0,"level","node")
    canon=load_json(ROOT/"results/nps_persistent_cover_v1.json")
    loc_rows=[]
    for loc,z in canon["quantitative_state"]["location_cover_slopes"].items():
        loc_rows.append({
            "level":"location",
            "node_id":"",
            "Location":loc,
            "n":z["nodes"],
            "year_min":"",
            "year_max":"",
            "sxx":"",
            "sxy":"",
            "slope":z["slope"],
            "min":"",
            "max":"",
            "range":"",
            "ci95_low":z["ci95"][0],
            "ci95_high":z["ci95"][1],
        })
    for col in ["ci95_low","ci95_high"]:
        if col not in node_rows.columns:
            node_rows[col]=""
    cols=list(pd.DataFrame(loc_rows).columns)
    for col in cols:
        if col not in node_rows.columns:
            node_rows[col]=""
    pd.concat([node_rows[cols],pd.DataFrame(loc_rows)[cols]],ignore_index=True).to_csv(
        out/"Table_S2_nps_cover_slopes.csv",index=False
    )


def table_s3(primary: Path, out: Path):
    y=pd.read_csv(primary/"early_warning_year_scores.csv")
    p=y.pivot(index=["target_year","n","losses","train_n","train_losses"],
              columns="arm",values=["log_loss","brier"]).reset_index()
    p.columns=["_".join([str(v) for v in c if str(v)!=""]).rstrip("_") if isinstance(c,tuple) else str(c) for c in p.columns]
    p["quantitative_minus_baseline_log_loss"]=p["log_loss_quantitative"]-p["log_loss_baseline"]
    p.to_csv(out/"Table_S3_early_warning_target_years.csv",index=False)


def table_s4(site: Path, out: Path):
    rows=[]
    files=[
        ("binary_detected","without_node_id","site_identity_binary_detected_without_node_grid.csv"),
        ("binary_detected","with_node_id","site_identity_binary_detected_with_node_grid.csv"),
        ("focal_frequency","without_node_id","site_identity_frequency_without_node_grid.csv"),
        ("focal_frequency","with_node_id","site_identity_frequency_with_node_grid.csv"),
        ("braun_blanquet","without_node_id","site_identity_cover_index_without_node_grid.csv"),
        ("braun_blanquet","with_node_id","site_identity_cover_index_with_node_grid.csv"),
    ]
    for outcome,reference,name in files:
        d=pd.read_csv(site/name)
        d.insert(0,"reference",reference)
        d.insert(0,"outcome",outcome)
        rows.append(d)
    pd.concat(rows,ignore_index=True).to_csv(out/"Table_S4_memory_tau_grid.csv",index=False)


def table_s5(out: Path):
    cv=load_json(ROOT/"results/current_validation_v2.json")
    rows=[]
    t=cv["threshold_induced_memory_known_truth"]
    rows.append({
        "family":"thresholding_only",
        "cells":t["cells"],"total_replicates":t["total_replicates"],
        "supporting_cells":t["supporting_cells"],"required_supporting_cells":t["required_supporting_cells"],
        "global_pattern_fraction":t["global_positive_amplification_fraction"],
        "required_global_fraction":t["required_global_positive_fraction"],
        "robust_levels":t["robust_phi_levels"],"required_robust_levels":t["required_robust_phi_levels"],
        "global_median_amplification":t["global_median_amplification"],
        "support_rule_passed":t["support_rule_passed"],
    })
    t=cv["two_timescale_hidden_state_memory_known_truth"]
    rows.append({
        "family":"slow_suitability_plus_fast_condition",
        "cells":t["cells"],"total_replicates":t["total_replicates"],
        "supporting_cells":t["supporting_cells"],"required_supporting_cells":t["required_supporting_cells"],
        "global_pattern_fraction":t["global_target_pattern_fraction"],
        "required_global_fraction":t["required_global_target_pattern_fraction"],
        "robust_levels":t["robust_phi_slow_levels"],"required_robust_levels":t["required_robust_phi_slow_levels"],
        "global_median_amplification":t["global_median_amplification"],
        "support_rule_passed":t["support_rule_passed"],
    })
    t=cv["latent_occupancy_detection_memory_known_truth"]
    rows.append({
        "family":"latent_occupancy_imperfect_detection",
        "cells":t["cells"],"total_replicates":t["total_replicates"],
        "supporting_cells":t["supporting_cells"],"required_supporting_cells":t["required_supporting_cells"],
        "global_pattern_fraction":t["global_target_pattern_fraction"],
        "required_global_fraction":t["required_global_target_pattern_fraction"],
        "robust_levels":t["robust_p11_levels"],"required_robust_levels":t["required_robust_p11_levels"],
        "global_median_amplification":t["global_median_amplification"],
        "support_rule_passed":t["support_rule_passed"],
    })
    pd.DataFrame(rows).to_csv(out/"Table_S5_known_truth_mechanism_decisions.csv",index=False)


def table_s6(out: Path):
    x=load_json(ROOT/"results/site_template_outcome_v1.json")
    rows=[]
    for outcome,z in x["primary"].items():
        rows.append({
            "outcome":outcome,
            "eligible_nodes":z["eligible_nodes"],
            "spatial_reference_mae":z["spatial_reference"]["mae"],
            "spatial_reference_r2":z["spatial_reference"]["heldout_r2"],
            "measured_template_mae":z["measured_template"]["mae"],
            "measured_template_r2":z["measured_template"]["heldout_r2"],
            "template_wins":z["increment"]["wins"],
            "signflip_p":z["increment"]["signflip_p"],
            "supported":z["increment"]["supported"],
        })
    pd.DataFrame(rows).to_csv(out/"Table_S6_site_template_scores.csv",index=False)


def table_s7(out: Path):
    x=load_json(ROOT/"results/benthic_light_condition_v1.json")
    rows=[]
    for outcome,z in x["primary_6m"].items():
        rows.append({
            "outcome":outcome,
            "eligible_rows":z.get("eligible_rows",""),
            "eligible_nodes":z.get("eligible_nodes",""),
            "target_years":z.get("scored_target_years",""),
            "baseline_mae":z["baseline_mae"],
            "light_mae":z["light_mae"],
            "wins":z["wins"],
            "signflip_p":z["signflip_p"],
            "supported":z["supported"],
            "sensitivity_3m_p":x["sensitivity_3m"].get(
                {"blade_length_mean_mm":"blade_length_p",
                 "shoot_density_mean_m2":"shoot_density_p",
                 "focal_frequency":"focal_frequency_p",
                 "bb_cover_mean_all_points":"bb_cover_p"}[outcome],""
            )
        })
    pd.DataFrame(rows).to_csv(out/"Table_S7_benthic_light_scores.csv",index=False)


def table_s8(out: Path):
    x=load_json(ROOT/"results/compound_hotfresh_condition_v1.json")
    rows=[]
    for outcome,z in x["primary"].items():
        rows.append({
            "evidence_class":"primary","outcome":outcome,
            "transition_rows":z["transition_rows"],"nodes":z["nodes"],"target_years":z["target_years"],
            "baseline_mae":z["baseline_mae"],"compound_mae":z["compound_mae"],
            "wins":z["wins"],"signflip_p":z["signflip_p"],"supported":z["supported"]
        })
    for outcome,z in x["secondary"].items():
        rows.append({
            "evidence_class":"secondary","outcome":outcome,
            "transition_rows":"","nodes":"","target_years":"",
            "baseline_mae":z["baseline_mae"],"compound_mae":z["compound_mae"],
            "wins":z["wins"],"signflip_p":z["signflip_p"],"supported":z["supported"]
        })
    pd.DataFrame(rows).to_csv(out/"Table_S8_compound_hotfresh_scores.csv",index=False)


def table_s9(out: Path):
    car=load_json(ROOT/"validation/caribbean_early_warning_v1/terminal_result.json")
    nps=load_json(ROOT/"validation/nps_tier3_v2/terminal_outcome_result.json")
    rows=[
        {
            "attempt":"Caribbean SeagrassNet v1",
            "focal_taxon":"Thalassia testudinum",
            "response_opened":car["response_opened"],
            "terminal_status":car["status"],
            "reason":car["reason"],
            "eligible_annual_units":"",
            "source_positive_transitions":"",
            "recorded_losses":"",
            "model_fits":car["predictive_model_fits"],
            "predictive_scores":car["predictive_scores"],
            "counts_as_external_predictive_evidence":car["counts_as_external_predictive_evidence"],
        },
        {
            "attempt":"NPS Tier-3 v2",
            "focal_taxon":"Zostera marina",
            "response_opened":nps["response_access_audit"]["response_values_opened"],
            "terminal_status":nps["terminal_status"],
            "reason":nps["reason"],
            "eligible_annual_units":nps["estimability"]["annual_units"],
            "source_positive_transitions":nps["estimability"]["source_positive_consecutive_transitions"],
            "recorded_losses":nps["estimability"]["recorded_losses"],
            "model_fits":nps["response_access_audit"]["model_fits"],
            "predictive_scores":nps["response_access_audit"]["predictive_scores"],
            "counts_as_external_predictive_evidence":nps["counts_as_external_predictive_evidence"],
        },
    ]
    pd.DataFrame(rows).to_csv(out/"Table_S9_external_validation_ledger.csv",index=False)


def main(primary: Path, nps: Path, site: Path, out: Path):
    out.mkdir(parents=True,exist_ok=True)
    table_s1(primary,out)
    table_s2(nps,out)
    table_s3(primary,out)
    table_s4(site,out)
    table_s5(out)
    table_s6(out)
    table_s7(out)
    table_s8(out)
    table_s9(out)
    manifest={
        "schema":"tampa.supplement_tables_v1",
        "tables":[f"Table_S{i}_" for i in range(1,10)],
        "status":"built_from_existing_analysis_and_canonical_results"
    }
    (out/"supplement_tables_manifest_v1.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--primary",type=Path,default=Path("results/generated_supplement"))
    p.add_argument("--nps",type=Path,default=Path("results/generated_nps_supplement"))
    p.add_argument("--site",type=Path,default=Path("results/generated_site_identity_supplement"))
    p.add_argument("--out",type=Path,default=Path("results/generated_supplement_tables"))
    a=p.parse_args()
    main(a.primary,a.nps,a.site,a.out)
