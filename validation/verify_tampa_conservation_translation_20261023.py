#!/usr/bin/env python3
"""Tampa source-backed conservation translation integrity for author review.

Only audits existing results and operational prose, no new forecast fitting,
threshold tuning, field observations or management intervention results.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NOTE=ROOT/"manuscript/TAMPA_CONSERVATION_TRANSLATION_V1.md"
MET=ROOT/"results/warning_reporting_metrics_v1.json"
MARK=ROOT/"results/early_warning_fixed_mark_overlap_verified_v1.json"
CAS=ROOT/"results/condition_leads_thinning_v1.json"
OUT=ROOT/"results/tampa_conservation_translation_qc_20261023.json"

def verify():
    text=NOTE.read_text(encoding="utf-8")
    p=json.loads(MET.read_text(encoding="utf-8"))
    marks=json.loads(MARK.read_text(encoding="utf-8"))
    seq=json.loads(CAS.read_text(encoding="utf-8"))
    registry=marks["registry"]
    checks={}
    checks["original_source_qc"]=(
        p["schema"]=="tampa.warning_reporting_metrics_v1" and
        marks["status"]=="COMPLETED_OBSERVATION_PROCESS_AUDIT" and
        seq["status"]=="condition_leading_information_not_supported")
    checks["source_cohort"]=all(x in text for x in ("570","19","23","2016"))
    node=p["metrics"]["node"]
    enhanced=p["metrics"]["node_quant"]
    checks["node_reference_auc"]=(
        f"{node['auc']:.3f}" in text and f"{enhanced['auc']:.3f}" in text)
    checks["annual_log_loss_displays"]=(
        f"{node['macro_log_loss']:.5f}" in text and
        f"{enhanced['macro_log_loss']:.5f}" in text)
    checks["measured_gain_not_exaggerated"]=all(x in text for x in (
        "approximately **0.7%**","L2-regularized node identity",
        "no untouched future-year validation"))
    cap=marks["capacity_decomposition"]
    for x in cap:
        percent=int(100*x["nominal_capacity"])
        checks[f"capacity_{percent}"]=all(t in text for t in (
            f"{percent}% per scored year", str(x["alerts_per_arm"]),
            f"{x['captured_all_node']}/{registry['scored_losses']}",
            f"{x['captured_all_node_quant']}/{registry['scored_losses']}",
        ))
    all_losses=marks["loss_partitions"]["all_losses"]
    scored=marks["loss_partitions"]["scored_losses"]
    checks["mark_revisit_total"]=all(
        x in text for x in (
            f"{all_losses['at_least_one_revisited']} of {all_losses['events']}",
            f"{all_losses['no_positive_mark_revisited']} of {all_losses['events']}",
            f"{scored['at_least_one_revisited']} revisited at least one positive mark",
            f"{scored['no_positive_mark_revisited']} revisited none",
        ))
    checks["no_unmeasured_slow_memory"]=(
        "slow, site-anchored occupancy/abundance component" not in text
        and "do **not** measure biological memory duration" in text)
    checks["no_false_cascade"]=(
        not seq["primary_frequency"]["supported"]
        and "does not support a single serial pathway" in text)
    checks["careful_management_scope"]=all(
        x in text for x in (
            "confirmation-sampling priority list",
            "an unvisited mark must not be coded as sampled absence",
            "Do **not** trigger a restoration treatment",
            "not a collapse forecast",
        ))
    checks["no_external_management_claim"]=(
        "management intervention" in text and
        not bool(re.search(r"validated (?:restoration|treatment) threshold",text,re.I)))
    return {
      "schema":"tampa.conservation_monitoring_translation_source_qc.v1",
      "status":"PASS_SOURCE_NUMERIC_OPERATIONAL_TRANSLATION" if all(checks.values()) else "STOP_SOURCE_NUMERIC_OR_MANAGEMENT_OVERCLAIM",
      "checks":checks,
      "failed":[k for k,v in checks.items() if not v],
      "author_boundary":"Only source reaggregation of retrospective observed non-detections; not a tested restoration policy or source-causal mechanism."
    }

if __name__=="__main__":
    a=verify()
    OUT.write_text(json.dumps(a,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(a,indent=2,ensure_ascii=False))
    sys.exit(0 if a["status"].startswith("PASS") else 2)
