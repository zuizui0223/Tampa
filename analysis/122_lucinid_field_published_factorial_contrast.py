#!/usr/bin/env python3
"""Exploratory four-cell contrast of van der Geest et al. 2020 published Table 1.

These are PAPER-REPORTED means and SEs (n=6 plots per treatment), not original
2020 plot-level observations and not an independent cross-study replication.
Their published factorial analysis is authoritative for inference. This code
provides explicit dimensional and contrast arithmetic only and never pools
with the 2012 laboratory experiment as an independent mechanism estimate.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

PAPER="https://doi.org/10.3389/fmars.2020.00011"
TABLE="https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2020.00011/full"
CELL_NAMES=("C","L","OM","L+OM")
N_PER_CELL=6
# Data extracted from published Table 1; order: C, L, OM, L+OM.
TABLE_MEANS_SE={
    "leaf_sulfide_derived_fraction_pct":{
        "unit":"percent_sediment_derived_leaf_sulfur",
        "mean":[20.3,19.1,25.3,22.3],
        "se":[1.5,.6,1.0,.4],
        "reported_clam_main_p":.048,
        "reported_organic_main_p":"<0.001",
        "reported_no_interactions":True,
    },
    "porewater_sulfide_umol_L":{
        "unit":"umol_L",
        "mean":[.1,.4,1170.9,716.4],
        "se":[0,.3,272.0,266.3],
        "reported_om_vs_om_plus_clams_p":.34,
        "reported_no_interactions":True,
    },
    "rhizome_biomass_g_dw_m2":{
        "unit":"g_dry_weight_m2",
        "mean":[65.9,70.4,48.4,48.8],
        "se":[11.6,10.0,4.6,9.3],
        "reported_clam_main_p":.80,
        "reported_organic_main_p":.048,
        "reported_no_interactions":True,
    },
    "leaf_biomass_g_dw_m2":{
        "unit":"g_dry_weight_m2",
        "mean":[76.7,85.2,91.5,64.8],
        "se":[14.3,10.9,22.0,11.0],
        "reported_clam_main_p":.56,
        "reported_no_interactions":True,
    },
    "shoot_density_count_m2":{
        "unit":"shoots_m2",
        "mean":[1210.,1592.,1274.,1189.],
        "se":[261.,160.,211.,167.],
        "reported_clam_main_p":.47,
        "reported_no_interactions":True,
    },
}

def contrasts(values):
    if len(values)!=4 or any(not math.isfinite(float(x)) for x in values):
        raise ValueError("Expected four finite treatment means in C,L,OM,L+OM order")
    c,l,om,olm=map(float,values)
    return {
        "lucinid_addition_under_no_organic":l-c,
        "lucinid_addition_under_organic":olm-om,
        "lucinid_main_difference":((l-c)+(olm-om))/2,
        "organic_main_difference":((om-c)+(olm-l))/2,
        "lucinid_by_organic_difference_in_differences":(olm-om)-(l-c),
    }

def summary():
    results={}
    for k,v in TABLE_MEANS_SE.items():
        means=v["mean"];ses=v["se"]
        if len(means)!=4 or len(ses)!=4:
            raise AssertionError("Publication table schema drift")
        calc=contrasts(means)
        # Do not use this as exact ANOVA inferential variance: paper randomized
        # in blocks and some outcomes were non-Gaussian.
        derived_se_approx=math.sqrt(sum(x*x for x in ses))/2
        results[k]={
            "unit":v["unit"],
            "reported_means_by_arm":dict(zip(CELL_NAMES,means)),
            "reported_standard_errors_by_arm":dict(zip(CELL_NAMES,ses)),
            "published_inference":{
                x:y for x,y in v.items() if x.startswith("reported_")
            },
            "published_mean_contrasts":calc,
            "independent_cell_mean_approx_SE_of_main_difference_noninferential":derived_se_approx,
            "is_new_experimental_evidence":False,
        }
    stress=results["leaf_sulfide_derived_fraction_pct"]["published_mean_contrasts"]
    eps=results["porewater_sulfide_umol_L"]["published_mean_contrasts"]
    bg=results["rhizome_biomass_g_dw_m2"]["published_mean_contrasts"]
    return {
        "schema":"tampa.lucinid_2020_four_group_published_table_reaggregation_v1",
        "evidence_class":"posthoc_published_mean_arithmetic_no_new_trial_effect",
        "publication":PAPER,
        "table1_original_source":TABLE,
        "replicate_plots_per_arm":N_PER_CELL,
        "study_count":1,
        "published_table":results,
        "cross_endpoint_observations":{
            "sulfide_intrusion_clam_reduction_no_organic_pp":stress["lucinid_addition_under_no_organic"],
            "sulfide_intrusion_clam_reduction_high_organic_pp":stress["lucinid_addition_under_organic"],
            "magnitude_ratio_of_intrusion_effect_organic_to_no_organic":abs(stress["lucinid_addition_under_organic"])/abs(stress["lucinid_addition_under_no_organic"]),
            "porewater_sulfide_clam_difference_under_high_organic_umol_L":eps["lucinid_addition_under_organic"],
            "rhizome_biomass_lucinid_main_difference_g_dw_m2":bg["lucinid_main_difference"],
            "biological_interpretation":(
                "Clam addition reduced leaf sulfide intrusion under both organic "
                "conditions; its immediate rhizome biomass main effect was not "
                "supported by the paper's original ANOVA (P=0.80). The more "
                "negative stress-context absolute intrusion difference has no "
                "published supported factorial interaction. Sulfide defense "
                "and instantaneous biomass response are distinct measured state axes."
            ),
        },
        "limits":[
            "All 4-cell means and SEs are reprinted from one already published 2020 paper.",
            "n=6 randomized field plots per treatment in the original study, not six independent estuaries.",
            "The manuscript's F/chi-square analyses are authoritative; no normal-approximation p-value calculated here.",
            "Absolute effect change 1.2 to 3.0 percentage points does not establish effect moderation: original paper reported no significant interaction.",
            "Porewater sulfide mean difference is non-significant in original report; it is not a proven independent sulfide reduction effect.",
            "A reduced leaf sulfide intrusion fraction is not sufficient proof of increased shoot or rhizome biomass.",
            "No microbial clade substitution, global macroecological distribution, or future TNC resilience measured.",
        ],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    s=json.dumps(summary(),ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    else:print(s,end="")

if __name__=="__main__":main()
