#!/usr/bin/env python3
"""Reverse-aggregate the VERIFIED 2022->2024 public mapped class transition.

No new GIS downloads, models or inferential tests. The derived 2024-class
source fractions explicitly preserve the "unmapped in 2022" residual;
this must NEVER be equated to true bare bottom, colonization or new algae.
"""
import argparse,hashlib,json,math
from pathlib import Path

REPORT="tampa.charlotte_public_gis_transition_verified_release_v1"
CODES=("9113","9116","9121")
SOURCE_RUN=44431639618
ZIP_DIGEST="sha256:d712335ef03178de292d643efa7eb580ecd6e9c65990cd8273d5e5b6b73eb4c7"

def backward(report):
    if report.get("schema")!=REPORT or report.get("verified_workflow",{}).get("run_id")!=SOURCE_RUN:
        raise ValueError("WRONG_VERIFIED_SOURCE")
    if report["verified_workflow"].get("artifact_zip_sha256")!=ZIP_DIGEST:
        raise ValueError("WORKFLOW_ARTIFACT_DIGEST_MISMATCH")
    r=report["result"]
    if r.get("not_new_blind_confirmation") is not True or r.get("not_a_causal_effect") is not True:
        raise ValueError("SCIENTIFIC_BOUNDARY_NOT_ENFORCED")
    start=r["source_area_to_target_class"]
    end=r["quality_control"]["2024"]["class_area_acres"]
    results={}
    for tgt in CODES:
        total=end[tgt]
        if not isinstance(total,(int,float)) or total<=0:
            raise ValueError("BAD_TARGET_ACREAGE")
        sources={s:float(start[s]["target_area_acres"][tgt]) for s in CODES}
        for s,v in sources.items():
            if not math.isfinite(v) or v<0:raise ValueError("INVALID_SOURCE_TRANSITION")
        unmapped=total-sum(sources.values())
        if unmapped<-.04:raise ValueError("NONCLOSED_TARGET_AREA")
        if unmapped<0:unmapped=0.0
        sources["unmapped_in_2022"]=unmapped
        if abs(sum(sources.values())-total)>.04:
            raise ValueError("TARGET_SUM_NOT_CLOSED")
        results[tgt]={
            "target_area_acres":round(total,3),
            "source_2022_area_acres":{k:round(v,3) for k,v in sources.items()},
            "source_2022_fraction_percent":{k:round(100*v/total,3) for k,v in sources.items()},
        }
    target_algae=results["9121"]
    target_seagrass_total=end["9113"]+end["9116"]
    former_seagrass_to_algae=(start["9113"]["target_area_acres"]["9121"]
                              +start["9116"]["target_area_acres"]["9121"])
    formerly_unmapped_to_algae=target_algae["source_2022_area_acres"]["unmapped_in_2022"]
    remaining_algae=start["9121"]["target_area_acres"]["9121"]
    if abs(former_seagrass_to_algae+formerly_unmapped_to_algae+remaining_algae-end["9121"])>.05:
        raise ValueError("ALGAE_ORIGIN_MASS_BALANCE_FAIL")
    algae_to_seagrass=start["9121"]["target_area_acres"]["9113"]+start["9121"]["target_area_acres"]["9116"]
    return {
      "schema":"tampa.charlotte_2024_mapped_origin_decomposition_v1",
      "source_verification_run":SOURCE_RUN,
      "source_verification_artifact_digest":ZIP_DIGEST,
      "evidence_class":"POST_HOC_DETERMINISTIC_REAGGREGATION_OF_VERIFIED_MAPPED_CLASSES",
      "2024_targets_with_2022_class_provenance":results,
      "2024_attached_algae_of_2022_mapped_seagrass_origin_acres":round(former_seagrass_to_algae,3),
      "2024_attached_algae_of_2022_mapped_seagrass_origin_percent":round(
          100*former_seagrass_to_algae/end["9121"],3),
      "2024_attached_algae_outside_2022_mapped_classes_acres":round(formerly_unmapped_to_algae,3),
      "2024_attached_algae_outside_2022_mapped_classes_percent":round(
          100*formerly_unmapped_to_algae/end["9121"],3),
      "2024_attached_algae_on_2022_algae_area_acres":round(remaining_algae,3),
      "2022_algae_to_2024_seagrass_acres":round(algae_to_seagrass,3),
      "2024_mapped_seagrass_total_acres":round(target_seagrass_total,3),
      "explicit_no_recovery_effect_inference":True,
      "warning":"A 2024 class mapped on area outside 2022 class polygons is NOT proven newly established vegetation; the 2022 no-polygon classification, full survey footprint and observation process are unknown. Areas are not comparable with broader district baywide mapped acreage without footprint crosswalk."
    }

def main():
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",default=str(root/"results/charlotte_public_gis_transition_verified_20261119.json"))
    p.add_argument("--output",required=True)
    args=p.parse_args()
    raw=Path(args.source).read_bytes()
    source=json.loads(raw)
    r=backward(source)
    r["source_report_sha256"]=hashlib.sha256(raw).hexdigest()
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
if __name__=="__main__":main()
