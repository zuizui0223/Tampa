#!/usr/bin/env python3
"""Exploratory seagrass interaction evidence and outcome-grain audit.

This does NOT meta-analyze incompatible reported endpoints or silently fit
experimental effects from paper abstracts. It verifies the hand-curated
publication inventory, reaggregates existing Tampa canonical ledgers, and
computes only published, directly comparable arithmetic quantities.

Report source URLs/DOIs precisely; full methods and tables are in the cited
original papers. Results from the six families cannot be pooled as a common
causal 'interaction benefit' at present.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data/seagrass_interactions_v1/study_evidence_registry.csv"
FAMILIES={
 "animal_pollination":"visitation or stigma pollen deposition under fauna x flow",
 "lucinid_sulfide":"sediment sulfide and plant biomass under bivalves or sulfur oxidizers",
 "grazer_epiphyte":"algal load and plant growth under grazers x nutrients or temperature",
 "algae_turtle":"rhodolith or seaweed effects under turtle herbivory",
 "nitrogen_symbiosis":"15N2 fixation and host translocation under nutrients and light",
 "predator_cascade":"predator -> intermediate grazer -> algal load -> seagrass state",
}
REQUIRED=("study_id","arm","year","publication_doi","public_data_url","evidence_type",
          "endpoint_family","data_status","unit_of_replication","interpretation_limit")

def records_from_registry(path=REGISTRY):
    with open(path,encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != list(REQUIRED):
            raise ValueError("Unexpected registry header")
        rows=list(reader)
    ids=set()
    for i,row in enumerate(rows,start=2):
        if None in row or any(row[k] is None for k in REQUIRED):
            raise ValueError(f"Row {i}: malformed CSV")
        if not row["study_id"] or row["study_id"] in ids:
            raise ValueError(f"Row {i}: missing or duplicated study ID")
        ids.add(row["study_id"])
        if row["arm"] not in FAMILIES:
            raise ValueError(f"Row {i}: unexpected interaction family")
        if not (1900 <= int(row["year"]) <= 2026):
            raise ValueError(f"Row {i}: unexpected year")
        if row["publication_doi"] and not re.match(r"^10\.\d{4,9}/\S+$",row["publication_doi"]):
            raise ValueError(f"Row {i}: invalid DOI string")
        if not row["public_data_url"].startswith("https://"):
            raise ValueError(f"Row {i}: missing public source URL")
        if not row["unit_of_replication"] or not row["interpretation_limit"]:
            raise ValueError(f"Row {i}: missing causal/independence guard")
    missing=set(FAMILIES)-{r["arm"] for r in rows}
    if missing:
        raise ValueError(f"Missing interaction families: {sorted(missing)}")
    return rows

def compare_chi2_from_original_paper():
    # Nature Communications 2016, Figure 4 caption reports chi^2=9.26 df=2
    # with P=.001. Under standard chi-square df=2, survival=exp(-x/2).
    chi2,df,p_reported = 9.26,2,0.001
    p_recomputed=math.exp(-chi2/2)
    return {
      "source":"10.1038/ncomms12980 Figure 4 caption",
      "test":"fauna female flower versus leaf visits in water movement",
      "chi_square_reported":chi2,"degrees_freedom":df,
      "p_value_reported":p_reported,
      "p_value_standard_chi_square_recomputed":p_recomputed,
      "reported_p_matches_df_and_statistic":math.isclose(p_reported,p_recomputed,rel_tol=.05),
      "qualitative_p_less_than_0_05_unchanged":p_recomputed<.05,
      "interpretation":"Published caption arithmetic inconsistency (or unreported alternate test), not a new biological effect; seek authors' raw visit counts before effect-size analysis."
    }

def original_rhodolith_report():
    # 2024 Ecosystems, Experiment 3: sediment retained in collectors outside
    # natural dense rhodolith bed vs within natural dense bed.
    outside,inside=.2091,.05
    return {
       "source":"10.1007/s10021-024-00909-w Experiment 3",
       "endpoint":"sediment_accumulation_dry_grams_in_sampling_tubes",
       "outside_natural_bed_mean_g":outside,
       "outside_natural_bed_sd_g":.1017,
       "inside_natural_bed_mean_g":inside,
       "inside_natural_bed_sd_g":.02,
       "outside_to_inside_mean_ratio":outside/inside,
       "outside_minus_inside_g":outside-inside,
       "published_t":-7.0,"published_t_df":16,
       "effect_status":"published_mean_arithmetic_only_no_new_causal_effect_or_valid_study_weight",
       "interpretation":"Denser rhodolith beds had reduced sediment resuspension relative to manipulated sparse-seagrass plot context; not direct Thalassia growth or evidence of a general sign switch."
    }

def published_lucinid_global():
    return {
      "source":"10.1126/science.1219973",
      "previous_meta_studies":84,
      "previous_meta_site_count":83,
      "published_lucinid_presence_percent":{"tropical":97,"subtropical":90,"temperate":56},
      "tropical_minus_temperate_percentage_points":41,
      "new_95pct_ci":None,
      "effect_status":"previous_published_meta_result_no_raw_category_denominators_here",
      "interpretation":"Association frequency, not trial-level experimental benefit, and not novel macroecological meta-analysis."
    }

def tampa_existing_sensitivities(root=ROOT):
    f=json.loads((root/"results/epiphyte_retention_v1.json").read_text(encoding="utf-8"))
    c=json.loads((root/"results/community_insurance_node_audit_v1.json").read_text(encoding="utf-8"))
    if f.get("schema")!="tampa.epiphyte_retention_v1.canonical_summary" or c.get("schema")!="tampa.community_insurance_node_audit_v1.canonical_summary":
        raise ValueError("Canonical Tampa result schema mismatch")
    fr=f["unadjusted_retention_primary"]
    if [int(x["epiphyte_ordinal"]) for x in fr]!=[0,1,2,3]:
        raise ValueError("Epiphyte ordinal class drift")
    y0,y3=fr[0]["retention_fraction"],fr[-1]["retention_fraction"]
    b=f["sensitivity_include_target_2016"]["ci95"]
    ci=c["primary"]["bootstrap_ci95"]
    if not b[0]<0<b[1] or not ci[0]<0<ci[1]:
        raise ValueError("A formerly unsupported model changed; re-review before interpretation")
    return {
        "tampa_epiphyte":{
          "source":"results/epiphyte_retention_v1.json",
          "unadjusted_grade0_retention":y0,
          "unadjusted_grade3_retention":y3,
          "unadjusted_grade3_minus_grade0_percentage_points":100*(y3-y0),
          "target_2016_included_adjusted_within_node_ci95":b,
          "mechanism_supported":False,
          "interpretation":"Higher ordinal epiphyte score is not evidence of epiphyte facilitation: the year-inclusive adjusted interval contains zero and leaf-age/site quality/detection are unresolved."
        },
        "tampa_seagrass_mixture":{
          "source":"results/community_insurance_node_audit_v1.json",
          "node_centered_binary_mixture_ci95":ci,
          "mechanism_supported":False,
          "interpretation":"Pooled community vegetation retention does not survive node-saturated support rule; cannot infer competitive replacement or facilitation."
        },
    }

def report(registry=REGISTRY,root=ROOT):
    rows=records_from_registry(registry)
    family_count=Counter(x["arm"] for x in rows)
    data_types=defaultdict(Counter)
    for x in rows:
        data_types[x["arm"]][x["data_status"]]+=1
    return {
       "schema":"tampa.seagrass_six_interactions_exploratory_registry_v1",
       "status":"bounded_exploratory_source_evidence_not_pooled_meta_analysis",
       "registry_total_records":len(rows),
       "family_inventory":[{"family":k,"reviewed_records":family_count[k],
             "testable_question":v,"source_availability":dict(data_types[k])} for k,v in FAMILIES.items()],
       "published_numeric_rechecks":{
          "animal_pollination_caption":compare_chi2_from_original_paper(),
          "rhodolith_sediment":original_rhodolith_report(),
          "existing_lucinid_meta":published_lucinid_global(),
          **tampa_existing_sensitivities(root),
       },
       "highest_priority_testable_cross_family_hypothesis":(
          "Effect of an interaction partner on seagrass quantitative state changes sign "
          "when herbivory, nutrient shortage, sulfide stress or physical exposure changes "
          "the partner's net benefit relative to its resource/shading cost."
       ),
       "no_pooling_reasons":[
         "Multiple tested arms use different outcome organisms, directions and units.",
         "Published meta-analyses already cover mean grazer/nutrient and seaweed impacts.",
         "Counts of sites/plots/replicates cannot substitute for treatment mean, SD and replicate identity.",
         "Mechanism is not inferred from co-occurrence or an unadjusted association.",
         "A single site or paper cannot be promoted to global interaction-sign generality.",
         "No new detection of causal root microbe substitution, pelagic pollinator dependence or N2-fixation cost.",
       ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=None)
    a=p.parse_args()
    s=json.dumps(report(),indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if a.out is None:print(s,end="")
    else:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")

if __name__=="__main__":main()
