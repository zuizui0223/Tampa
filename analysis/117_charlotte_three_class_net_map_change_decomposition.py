#!/usr/bin/env python3
"""Reconcile ALL three 2022->2024 vegetation classes without assuming biology.

Two source-verified durable inputs:
- original per-class 2022/24 GIS areas and polygon intersection matrix
- separately downloaded, independently source-area-validated agency change-map
  layers, which misleadingly use names "Seagrass Gain" and "Seagrass Loss"
  despite including code 9121 attached macroalgae.

Partition the published 2022->2024 map net class area change into:
 (1) 2024 mapped area not in any 2022 three class polygons ("gain" map)
 (2) 2022 mapped area not in any 2024 three class polygons ("loss" map)
 (3) within covered footprints, SEA->ALGAE and ALGAE->SEA classification.
Crucially, patchy<->continuous sea category flips remain *within* sea.

Do not equate mapped new/unmapped with new vegetation/death, and this is
not independent biological validation. Bounds account for 0.001 ac rounding.
"""
from __future__ import annotations
import argparse,json,math,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"results/charlotte_public_gis_transition_verified_20261119.json"
OFFICIAL=ROOT/"results/charlotte_official_change_map_giant_source_concordance_verified_20261119.json"
SEA=("9113","9116")
ALGAE="9121"
CODES=(*SEA,ALGAE)
GEO_TOL=.025
SOURCE_GIS_RUN=44431639618
SOURCE_AGENCY_RUN=44478539061

class Stop(ValueError):pass

def n(value,path):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise Stop("MISSING_FINITE_SOURCE_VALUE:"+path)
    if value<0: raise Stop("NEGATIVE_SOURCE_AREA:"+path)
    return float(value)

def inputs():
    original=json.loads(ORIGINAL.read_text(encoding="utf-8"))
    official=json.loads(OFFICIAL.read_text(encoding="utf-8"))
    if original.get("schema")!="tampa.charlotte_public_gis_transition_verified_release_v1":
        raise Stop("UNVERIFIED_PRIMARY_SOURCE_GIS_REPORT")
    if original.get("verified_workflow",{}).get("run_id")!=SOURCE_GIS_RUN:
        raise Stop("PRIMARY_SOURCE_RUN_ID_MISMATCH")
    if official.get("schema")!="tampa.charlotte_original_source_versus_agency_change_layer_verified_release_v1":
        raise Stop("UNVERIFIED_OFFICIAL_CHANGE_SOURCE")
    if official.get("verified_ci",{}).get("run_id")!=SOURCE_AGENCY_RUN:
        raise Stop("OFFICIAL_SOURCE_RUN_ID_MISMATCH")
    return original,official

def compute(primary,official):
    r=primary["result"]
    matrix=r["source_area_to_target_class"]
    year22=r["quality_control"]["2022"]["class_area_acres"]
    year24=r["quality_control"]["2024"]["class_area_acres"]
    derived_gain={}
    derived_loss={}
    for c in CODES:
        target=n(year24[c],"2024."+c)
        mapped_prior=sum(n(matrix[src]["target_area_acres"][c],src+"->"+c) for src in CODES)
        derived_gain[c]=target-mapped_prior
        derived_loss[c]=n(matrix[c]["target_area_acres"]["unmapped"],"2022."+c+"->unmapped")
        if derived_gain[c]<-.001:raise Stop("NEGATIVE_GEOMETRIC_GAIN_SOURCE:"+c)
    s=official["report"]["official_gain_loss_sources"]
    gain={c:n(s["gain"]["mapped_class_areas_acres"][c],"official_gain."+c) for c in CODES}
    loss={c:n(s["loss"]["mapped_class_areas_acres"][c],"official_loss."+c) for c in CODES}
    if s["gain"]["flucss_class_counts"]!={"9113":513,"9116":187,"9121":132} or s["loss"]["flucss_class_counts"]!={"9113":496,"9116":218,"9121":53}:
        raise Stop("OFFICIAL_CHANGE_CLASS_COUNT_LEDGER_DRIFT")
    discrepancies={f"gain_{c}":round(gain[c]-derived_gain[c],5) for c in CODES}
    discrepancies.update({f"loss_{c}":round(loss[c]-derived_loss[c],5) for c in CODES})
    if max(abs(v) for v in discrepancies.values())>GEO_TOL:
        raise Stop("AGENCY_GAIN_LOSS_AREA_INCONSISTENT_WITH_ORIGINAL_MAP:"+str(discrepancies))
    # Same-year seagrass category flips are still seagrass cover, not sea-area loss.
    sea_to_algae=sum(n(matrix[c]["target_area_acres"][ALGAE],"sea->algae."+c) for c in SEA)
    algae_to_sea=sum(n(matrix[ALGAE]["target_area_acres"][c],"algae->sea."+c) for c in SEA)
    sea22=sum(n(year22[c],"sea22."+c) for c in SEA)
    sea24=sum(n(year24[c],"sea24."+c) for c in SEA)
    algae22=n(year22[ALGAE],"algae22")
    algae24=n(year24[ALGAE],"algae24")
    sea_net=sea24-sea22
    algae_net=algae24-algae22
    # Use original GIS matrix-derived gains/losses for the exact mass-balance
    # derivation; official mapped change areas serve as independent source QC
    # on the *same imagery*, NOT separate plant biology.
    sea_footprint=sum(derived_gain[c]-derived_loss[c] for c in SEA)
    algae_footprint=derived_gain[ALGAE]-derived_loss[ALGAE]
    cross_sea=algae_to_sea-sea_to_algae
    cross_algae=-cross_sea
    residuals={
        "seagrass_actual_minus_decomposition_acres":round(sea_net-(sea_footprint+cross_sea),5),
        "algae_actual_minus_decomposition_acres":round(algae_net-(algae_footprint+cross_algae),5),
        "three_classes_actual_minus_decomposition_acres":round((sea_net+algae_net)-(sea_footprint+algae_footprint),5)
    }
    if max(abs(v) for v in residuals.values())>GEO_TOL:
        raise Stop("CATEGORY_AREA_DECOMPOSITION_FAILED:"+str(residuals))
    return {
      "schema":"tampa.charlotte_three_class_mapped_net_change_decomposition_v1",
      "status":"SUCCESS_VERIFIED_TWO_SOURCE_GIS_AREA_MASS_BALANCE_NOT_CAUSAL",
      "source_original_gis_run":SOURCE_GIS_RUN,
      "official_change_gis_source_run":SOURCE_AGENCY_RUN,
      "source_validation_type":"Originally independent source acreage/geometries but shared SWFWMD remote sensing; not independent ecological studies",
      "source_years":[2022,2024],
      "mapped_area_acres":{
        "2022_seagrass":round(sea22,3),"2024_seagrass":round(sea24,3),
        "seagrass_net_change":round(sea_net,3),
        "2022_attached_algae":round(algae22,3),"2024_attached_algae":round(algae24,3),
        "attached_algae_net_change":round(algae_net,3),
        "three_class_net_change":round(sea_net+algae_net,3)},
      "official_gain_area_per_class_acres":gain,
      "official_loss_area_per_class_acres":loss,
      "independently_derived_map_gain_area_per_class_acres":{c:round(derived_gain[c],3) for c in CODES},
      "independently_derived_map_loss_area_per_class_acres":{c:round(derived_loss[c],3) for c in CODES},
      "official_minus_derived_source_area_residual_acres":discrepancies,
      "cross_class_mapped_area_acres":{
          "2022_seagrass_to_2024_attached_algae":round(sea_to_algae,3),
          "2022_attached_algae_to_2024_seagrass":round(algae_to_sea,3),
          "net_seagrass_from_class_reclassification":round(cross_sea,3),
          "net_attached_algae_from_class_reclassification":round(cross_algae,3)},
      "source_map_coverage_change_acres":{
          "mapped_seagrass_new_source_coverage":round(sum(derived_gain[c] for c in SEA),3),
          "mapped_seagrass_source_coverage_removed":round(sum(derived_loss[c] for c in SEA),3),
          "mapped_seagrass_net_coverage_component":round(sea_footprint,3),
          "mapped_algae_new_source_coverage":round(derived_gain[ALGAE],3),
          "mapped_algae_source_coverage_removed":round(derived_loss[ALGAE],3),
          "mapped_algae_net_coverage_component":round(algae_footprint,3)},
      "mass_balance_residual_acres":residuals,
      "not_independent_field_validation":True,
      "unmapped_is_not_bare_or_unvegetated":True,
      "code_9121_in_nominal_seagrass_change_layers_is_attached_macroalgae":True,
      "not_true_establishment_mortality_or_algae_inhibition":True,
      "interpretation":"Agency gain/loss maps reflect year-to-year mapped-coverage set differences, while class swaps between seagrass and algae are separate. Both are remote-sensing map labels, not independent biological recovery or plant mortality.",
      "precision":"Source values rounded to 0.001 acres; absolute source residual tolerance 0.025 acre."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    try:
        original,official=inputs()
        result=compute(original,official)
        result["input_file_sha256"]={
           "original":hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
           "official":hashlib.sha256(OFFICIAL.read_bytes()).hexdigest()}
        rc=0
    except (Stop,ValueError,TypeError,KeyError,FileNotFoundError) as e:
        result={"schema":"tampa.charlotte_three_class_mapped_net_change_decomposition_v1",
           "status":"STOP_SOURCE_CHANGE_MASS_BALANCE","reason":str(e),
           "biological_effect_not_estimated":True}
        rc=2
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False))
    return rc

if __name__=="__main__":main()
