#!/usr/bin/env python3
"""Post-hoc, decision-facing audit of frozen Tampa walk-forward predictions.

No refits, threshold optimization or new ecological support rules. The purpose is
only to test whether higher AUC/log loss implies a useful capacity-limited
historical watchlist for next-year *recorded* Thalassia absence.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ARMS = ("space", "space_quant", "node", "node_quant")
CAPACITIES = (0.10, 0.20)


def load_predictions(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    expected = {"node_id", "target_year", "loss", *(f"p_{arm}" for arm in ARMS)}
    if not rows or not expected.issubset(rows[0]):
        raise ValueError("Missing required prediction columns")
    seen = set()
    for r in rows:
        r["target_year"] = int(r["target_year"])
        r["loss"] = int(r["loss"])
        key = (r["node_id"], r["target_year"])
        if not r["node_id"] or key in seen or r["loss"] not in (0, 1):
            raise ValueError("Duplicate/invalid node-year or loss label")
        seen.add(key)
        for arm in ARMS:
            val = float(r[f"p_{arm}"])
            if not math.isfinite(val) or not 0 <= val <= 1:
                raise ValueError("Invalid predicted probability")
            r[f"p_{arm}"] = val
    years = {r["target_year"] for r in rows}
    if (len(rows), sum(r["loss"] for r in rows), len(years)) != (570, 19, 23):
        raise ValueError("Not the frozen 570 / 19 / 23 scored cohort")
    if min(years) != 2003 or max(years) != 2025 or 2016 not in years:
        raise ValueError("Frozen year registry mismatch, including 2016")
    return rows


def watchlist(rows: list[dict], capacity: float, arm: str) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[r["target_year"]].append(r)
    alerts = events = total_n = 0
    per_year = []
    selections = set()
    for year, rs in sorted(groups.items()):
        # Floor maintains capacity for n>=1/capacity. At least one alert per year.
        take = max(1, math.floor(len(rs) * capacity))
        chosen = sorted(rs, key=lambda r: (-r[f"p_{arm}"], r["node_id"]))[:take]
        found = sum(r["loss"] for r in chosen)
        for r in chosen:
            selections.add((r["node_id"], year))
        alerts += take
        events += found
        total_n += len(rs)
        per_year.append({
            "target_year": year,
            "n": len(rs),
            "losses": sum(r["loss"] for r in rs),
            "alerts": take,
            "losses_captured": found,
        })
    total_losses = sum(r["loss"] for r in rows)
    return {
        "arm": arm,
        "nominal_capacity_fraction": capacity,
        "alerts": alerts,
        "realized_alert_fraction": alerts / total_n,
        "recorded_losses_captured": events,
        "event_recall": events / total_losses,
        "alert_precision": events / alerts,
        "prevalence": total_losses / total_n,
        "precision_lift_over_unstratified_prevalence": (events / alerts) / (total_losses / total_n),
        "by_year": per_year,
        "selection": selections,
    }


def audit(rows: list[dict]) -> dict:
    output = {
        "schema": "tampa.early_warning_monitoring_utility_v1",
        "evidence_class": "post_hoc_operational_diagnostic_not_a_new_prospective_validation",
        "cohort": {"scored_rows": len(rows), "recorded_losses": sum(r["loss"] for r in rows),
                   "target_years": len({r["target_year"] for r in rows}), "includes_2016": True},
        "capacity_audits": [],
        "claim_boundary": [
            "This evaluates targeting of *recorded absence*, not true seagrass mortality or conservation outcomes.",
            "The predictor comparison is post-hoc and cannot upgrade the existing ecological inference.",
            "Site-saturated node vs node+quant is the necessary operational comparator.",
            "Fixed 10% and 20% capacities are illustrations, not optimized treatment thresholds.",
            "Each year independently ranks only the nodes surveyed in that target year; no future labels inform ranking.",
            "Rare losses mean a small number of events can shift recall; report integer counts and the 2016 contribution.",
        ],
    }
    for cap in CAPACITIES:
        checks = {arm: watchlist(rows, cap, arm) for arm in ARMS}
        summary = {
            "nominal_capacity_fraction": cap,
            "arms": {arm: {k: v for k, v in d.items() if k != "selection"} for arm, d in checks.items()},
            "paired_node_quant_vs_node": {
                "net_additional_recorded_losses_captured": checks["node_quant"]["recorded_losses_captured"] - checks["node"]["recorded_losses_captured"],
                "watchlist_changes": len(checks["node_quant"]["selection"] ^ checks["node"]["selection"]) // 2,
                "target_2016": {
                    arm: next(y for y in checks[arm]["by_year"] if y["target_year"] == 2016)
                    for arm in ("node", "node_quant")
                },
            },
            "paired_space_quant_vs_space": {
                "net_additional_recorded_losses_captured": checks["space_quant"]["recorded_losses_captured"] - checks["space"]["recorded_losses_captured"],
            },
        }
        output["capacity_audits"].append(summary)
    return output


def self_test() -> None:
    toy = [
        {"node_id": "b", "target_year": 2016, "loss": 1, "p_node": .3},
        {"node_id": "a", "target_year": 2016, "loss": 0, "p_node": .3},
        {"node_id": "c", "target_year": 2016, "loss": 0, "p_node": .1},
    ]
    s = watchlist(toy, .5, "node")
    assert s["alerts"] == 1 and s["recorded_losses_captured"] == 0
    toy[0]["p_node"] = .4
    assert watchlist(toy, .5, "node")["recorded_losses_captured"] == 1
    assert watchlist(toy, 1, "node")["recorded_losses_captured"] == 1
    print("Self-tests passed: tie-breaking, capacity, event capture")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path,
                        default=Path("results/generated_site_warning/early_warning_site_identity_predictions.csv"))
    parser.add_argument("--out", type=Path,
                        default=Path("results/generated_site_warning/early_warning_monitoring_utility_v1.json"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = audit(load_predictions(args.predictions))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"cohort": result["cohort"], "capacity_audits": [
        {"fraction": d["nominal_capacity_fraction"],
         "node_net_events": d["paired_node_quant_vs_node"]["net_additional_recorded_losses_captured"]}
        for d in result["capacity_audits"]]}, indent=2))


if __name__ == "__main__":
    main()
