#!/usr/bin/env python3
"""Auditable 2015 ZEN2 manipulation fidelity, predation ceiling and prey identity.

Uses the frozen original BCO-DMO CSV SHA verified by analysis/127.
All diagnostics were decided AFTER the 17-site unadjusted outcomes were
seen. No new causal effect is claimed and no favorable subgroup replaces
the original all-17-site primary exploratory contrasts.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "zen2_2015_primary",ROOT/"analysis"/"127_zen2_2015_site_predation_factorial.py"
)
ORIGINAL=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORIGINAL)
EXPECTED={"Amb":1.0,"Fifty":.5,"Eighty":.2}
CONTRASTS=(
 "edge_minus_interior_risk",
 "fifty_minus_ambient_risk",
 "eighty_minus_ambient_risk",
 "edge_by_eighty_thinning_difference_in_differences"
)

def group_label(site):
    # KOA/KOB are the sole pair with shared two-character site family.
    # This is a purely conservative geography-sensitivity grouping, not
    # evidence of same randomization/independence clusters.
    return "KO" if site in ("KOA","KOB") else site

def safeavg(values):
    return statistics.mean(values) if values else None

def summarize(rows,primary,require_original_frame=True):
    if primary["schema"]!="tampa.zen2_2015_original_site_equal_predation_v1":
        raise ValueError("Unexpected original site-contrast schema")
    if require_original_frame and (len(rows)!=2666 or primary["site_count"]!=17):
        raise ValueError("Original source cohort drift")
    if set(x["taxon"] for x in rows)!={"Amphipod","Isopod"}:
        raise ValueError("Unexpected original prey taxon roster")
    by=defaultdict(list)
    for x in rows:by[x["site"]].append(x)
    if set(by)!={x["site"] for x in primary["source_cell_coverage"]}:
        raise ValueError("Original source sites disagree with pinned primary")
    sites=[]
    for site,items in sorted(by.items()):
        cell=defaultdict(list)
        for x in items:
            if x["density_initial"]<=0:
                raise ValueError("Cannot evaluate achieved:initial shoot density for a zero baseline")
            cell[(x["location"],x["treatment"])].append(x)
        classes={x["taxon"] for x in items}
        if len(classes)!=1:
            # This is the only available possibility for a within-site
            # taxon contrast, so treat it as a separate audit gate.
            raise ValueError("Unexpected within-site prey classes: new design review needed")
        effects=next(x["contrasts"] for x in primary["source_cell_coverage"] if x["site"]==site)
        sizes={
          status:[x["size_mm"] for x in items if x["recorded_eaten"]==status and x["size_mm"] is not None]
          for status in (0,1)
        }
        within_cell_size=[]
        for key,cell_items in cell.items():
            alive=[x["size_mm"] for x in cell_items if x["recorded_eaten"]==0 and x["size_mm"] is not None]
            eaten=[x["size_mm"] for x in cell_items if x["recorded_eaten"]==1 and x["size_mm"] is not None]
            if len(alive)>=2 and len(eaten)>=2:
                within_cell_size.append(statistics.mean(eaten)-statistics.mean(alive))
        ratios={}
        risks={}
        for location in ORIGINAL.LOCATIONS:
            for tr in ORIGINAL.TREATMENTS:
                v=cell[(location,tr)]
                if len(v)<5:raise ValueError("Unbalanced original plot cell")
                label=f"{location}|{tr}"
                ratios[label]=safeavg([x["density_actual"]/x["density_initial"] for x in v])
                risks[label]=safeavg([x["recorded_eaten"] for x in v])
        ratios_by_treatment={tr:safeavg([x["density_actual"]/x["density_initial"]
                                         for x in items if x["treatment"]==tr])
                             for tr in ORIGINAL.TREATMENTS}
        n_tethers=len({x["tether"] for x in items})
        sites.append({
          "site":site,
          "taxon":next(iter(classes)),
          "n_original_tether_trials":len(items),
          "tether_id_distinct_within_site":n_tethers,
          "original_tether_id_reuse_count_beyond_first":len(items)-n_tethers,
          "all_tethered_prey_consumed":all(x["recorded_eaten"]==1 for x in items),
          "site_overall_consumed_fraction":safeavg([x["recorded_eaten"] for x in items]),
          "ambient_only_consumed_fraction":safeavg([x["recorded_eaten"] for x in items if x["treatment"]=="Amb"]),
          "prey_size_mm_n":sum(x["size_mm"] is not None for x in items),
          "prey_size_mm_missing":sum(x["size_mm"] is None for x in items),
          "prey_size_eaten_minus_alive_within_site_mm":(
              statistics.mean(sizes[1])-statistics.mean(sizes[0])
              if len(sizes[1])>=5 and len(sizes[0])>=5 else None
          ),
          "prey_size_eaten_minus_alive_within_site_treatment_cells_mm":(
              statistics.mean(within_cell_size) if len(within_cell_size)>=2 else None
          ),
          "site_six_cells_with_measurable_size_and_both_outcomes":len(within_cell_size),
          "achieved_to_initial_density_ratio_by_treatment":ratios_by_treatment,
          "achieved_to_initial_density_ratio_by_cell":ratios,
          "predation_by_cell":risks,
          "original_site_risk_contrasts":effects,
        })
    taxonomy=defaultdict(set)
    for r in sites:taxonomy[r["taxon"]].add(r["site"])
    if (require_original_frame and len(sites)!=17) or set(taxonomy)!={"Amphipod","Isopod"}:
        raise ValueError("Incorrect 17-site source or taxonomy classes")
    all17={k:[r["original_site_risk_contrasts"][k] for r in sites] for k in CONTRASTS}
    non_saturated=[r for r in sites if not r["all_tethered_prey_consumed"]]
    noceil={k:[r["original_site_risk_contrasts"][k] for r in non_saturated] for k in CONTRASTS}
    ratios_all={t:[r["achieved_to_initial_density_ratio_by_treatment"][t] for r in sites]
                for t in ORIGINAL.TREATMENTS}
    grouped=defaultdict(list)
    for r in sites:grouped[group_label(r["site"])].append(r)
    region_summary={}
    for k in CONTRASTS:
        group_means=[statistics.mean([x["original_site_risk_contrasts"][k] for x in group])
                     for group in grouped.values()]
        region_summary[k]={
            "n_conservative_site_families":len(group_means),
            "site_family_equal_mean":statistics.mean(group_means),
            "original_17_site_equal_mean":statistics.mean(all17[k]),
        }
    size_gates={}
    for label in ("prey_size_eaten_minus_alive_within_site_mm",
                  "prey_size_eaten_minus_alive_within_site_treatment_cells_mm"):
        sample=[x[label] for x in sites if x[label] is not None]
        size_gates[label]={
          "sites_with_estimate":len(sample),
          "site_equal_mean_mm":statistics.mean(sample) if sample else None,
          "site_equal_median_mm":statistics.median(sample) if sample else None,
          "positive_site_differences":sum(v>0 for v in sample),
          "negative_site_differences":sum(v<0 for v in sample),
          "no_effect_sized_test_if_n_below_5":len(sample)<5,
        }
        if len(sample)>=5:
            size_gates[label]["site_bootstrap_95pct_percentile"]=(
                ORIGINAL.bootstrap_site_mean(sample,seed=2026112425)["site_bootstrap_95pct_percentile"]
            )
            site_pairs=[(x["site"],x["taxon"],x[label]) for x in sites if x[label] is not None]
            size_gates[label]["leave_one_site_out_mean_range"]=[
                min(statistics.mean([z[2] for z in site_pairs if z[0]!=site]) for site,_,_ in site_pairs),
                max(statistics.mean([z[2] for z in site_pairs if z[0]!=site]) for site,_,_ in site_pairs),
            ]
            amph=[p[2] for p in site_pairs if p[1]=="Amphipod"]
            size_gates[label]["amphipod_only_posthoc_check"]={
                "sites":len(amph),
                "site_equal_mean_mm":statistics.mean(amph) if amph else None,
                "site_bootstrap_95pct_percentile":(
                    ORIGINAL.bootstrap_site_mean(amph,seed=2026112488)["site_bootstrap_95pct_percentile"]
                    if len(amph)>=5 else None
                ),
                "warning":"Dropping isopod sites selects distinct geographies and cannot identify an independent prey-taxon effect.",
            }
    return {
      "schema":"tampa.zen2_2015_predation_manipulation_ceiling_taxon_audit_v1",
      "status":"response_exposed_posthoc_sensitivity_not_new_original_experimental_claim",
      "source_file_sha256":ORIGINAL.SOURCE_SHA256,
      "source_paper":"10.1002/ecy.3316",
      "site_count":len(sites),
      "size_diagnostic_posthoc_no_causal_prey_selection":size_gates,
      "measured_prey_size_count":sum(x["prey_size_mm_n"] for x in sites),
      "missing_prey_size_count":sum(x["prey_size_mm_missing"] for x in sites),
      "sites_without_any_prey_size_measurement":[x["site"] for x in sites if x["prey_size_mm_n"]==0],
      "sites_with_more_than_half_prey_size_missing":[
          x["site"] for x in sites if x["prey_size_mm_missing"]>x["n_original_tether_trials"]/2
      ],
      "original_tethered_prey_trials":sum(x["n_original_tether_trials"] for x in sites),
      "taxon_by_site_not_an_independent_species_experiment":{
          k:{"sites":sorted(v),"n_sites":len(v),
             "original_tethered_prey_trials":sum(x["n_original_tether_trials"] for x in sites if x["taxon"]==k)}
          for k,v in taxonomy.items()
      },
      "sites_with_100pct_consumption":[x["site"] for x in sites if x["all_tethered_prey_consumed"]],
      "count_100pct_consumed_sites":sum(x["all_tethered_prey_consumed"] for x in sites),
      "other_sites_in_sensitivity":[x["site"] for x in non_saturated],
      "number_sites_other":len(non_saturated),
      "tether_id_uniqueness":{
          "total_original_trials":sum(x["n_original_tether_trials"] for x in sites),
          "sum_within_site_unique_tether_labels":sum(x["tether_id_distinct_within_site"] for x in sites),
          "sum_within_site_reused_labels":sum(x["original_tether_id_reuse_count_beyond_first"] for x in sites),
          "warnings":"Tether_no is not a globally unique trial/plot/round identifier. Four deployment rounds may reuse labels.",
      },
      "manipulation_fidelity_source_count_diagnostic":{
          "treatment_expected_post_pre_ratio":EXPECTED,
          "site_mean_post_pre_ratios":{
             tr:{"median":statistics.median(v),"min":min(v),"max":max(v),
                 "site_count":len(v),"mean":statistics.mean(v),
                 "maximum_absolute_deviation_from_nominal":max(abs(x-EXPECTED[tr]) for x in v)}
             for tr,v in ratios_all.items()
          },
          "warning":"Calculated shoot density is recorded after manipulation, not an independent canopy-architecture/leaf-height measurement.",
      },
      "original_all_sites_and_posthoc_nonsaturated_summary":{
          k:{
            "all_17_site_equal_mean":statistics.mean(all17[k]),
            "non_saturated_site_equal_mean":statistics.mean(noceil[k]),
            "non_saturated_site_count":len(noceil[k]),
            "all_site_bootstrap_ci95_from_frozen_primary":
                primary["site_equal_contrasts"][k]["site_bootstrap_95pct_percentile"],
            "original_full_data_status":"AUTHORITATIVE_DESCRIPTIVE",
            "nonsaturated_status":"POSTHOC_CONDITIONING_ON_OBSERVED_OUTCOME_NOT_VALID_CAUSAL_REPLACEMENT",
          } for k in CONTRASTS
      },
      "same_region_KO_pair_sensitivity":region_summary,
      "site_diagnostics":sites,
      "interpretation_stops":[
          "Amphipod-versus-isopod prey taxon is completely confounded by site: 15 versus 2 sites, with no within-site taxon comparison.",
          "Three sites at 100% eaten limit estimability of upward risk changes but removing them post hoc selects on the outcome.",
          "Tether label is reused over repeated deployment rounds; don't count distinct IDs as independent habitat blocks.",
          "Original Hovel 2021 already studied patch-edge risk and shoot thinning and found adjusted edges could be safer.",
          "Prey size was assessed after the global null and original site-roster review: even within original factorial cells it is observational and can reflect tethering and survival bias.",
          "Actual measured patch architecture, prey size, epibiont biomass and predator community are not identified as causal mediators here.",
          "A calibrated longer-term survival probability and reciprocal seagrass-grazer demographic feedback are not observed.",
      ]
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None);a=p.parse_args()
    raw=ORIGINAL.load_source()
    rows=ORIGINAL.parse_rows(raw)
    primary=ORIGINAL.analyze(rows)
    data=summarize(rows,primary)
    s=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
