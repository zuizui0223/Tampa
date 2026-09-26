#!/usr/bin/env python3
"""Exploratory Tampa Bay scale-decoupling analysis.

Tests whether changes in bay-wide mapped seagrass extent are mirrored by fixed-transect
seagrass frequency, and whether Thalassia-specific local state behaves differently.

No EOG features are used here. The analysis is an independent ecological follow-up.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

SPECIES_COLUMNS = {
    "Thalassia": "Thalassia_frequency",
    "Halodule": "Halodule_frequency",
    "Syringodium": "Syringodium_frequency",
    "Ruppia": "Ruppia_frequency",
    "Halophila": "Halophila_frequency",
}


def pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else math.nan


def slope(xs: list[float], ys: list[float]) -> float:
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den > 0 else math.nan


def quantile(values: list[float], q: float) -> float:
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


def permutation_p(xs: list[float], ys: list[float], observed: float, reps: int = 10000) -> float:
    rng = random.Random(20260926)
    work = list(ys)
    exceed = 0
    for _ in range(reps):
        rng.shuffle(work)
        if abs(pearson(xs, work)) >= abs(observed):
            exceed += 1
    return (exceed + 1) / (reps + 1)


def transition_summary(rows: list[dict]) -> dict:
    counts = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 0}
    for row in rows:
        counts[(row["p0"], row["p1"])] += 1
    absent_n = counts[(0, 0)] + counts[(0, 1)]
    present_n = counts[(1, 0)] + counts[(1, 1)]
    return {
        "n": len(rows),
        "00": counts[(0, 0)],
        "01": counts[(0, 1)],
        "10": counts[(1, 0)],
        "11": counts[(1, 1)],
        "persistence": counts[(1, 1)] / present_n if present_n else None,
        "loss": counts[(1, 0)] / present_n if present_n else None,
        "recolonization": counts[(0, 1)] / absent_n if absent_n else None,
    }


def load_annual(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = []
        for row in csv.DictReader(fh):
            out = {
                "transect": row["transect"],
                "year": int(row["year"]),
                "bay_segment": row["bay_segment"],
                "n_visits": int(row["n_visits"]),
                "total_seagrass": float(row["total_seagrass_frequency"]),
            }
            for label, column in SPECIES_COLUMNS.items():
                out[label] = float(row[column])
            rows.append(out)
        return rows


def load_coverage(path: Path) -> dict[int, float]:
    with path.open(newline="", encoding="utf-8") as fh:
        return {int(r["year"]): float(r["acres"]) for r in csv.DictReader(fh)}


def analyze(annual_rows: list[dict], coverage: dict[int, float]) -> dict:
    by_year: dict[int, list[dict]] = defaultdict(list)
    by_key = {}
    for row in annual_rows:
        by_year[row["year"]].append(row)
        by_key[(row["transect"], row["year"])] = row

    annual_mean = {}
    variables = ["total_seagrass", *SPECIES_COLUMNS]
    for year, rows in by_year.items():
        annual_mean[year] = {
            "n": len(rows),
            **{v: sum(r[v] for r in rows) / len(rows) for v in variables},
        }

    matched = []
    for year in sorted(set(coverage) & set(annual_mean)):
        matched.append({"year": year, "acres": coverage[year], **annual_mean[year]})

    level_corr = {
        v: pearson([r["acres"] for r in matched], [r[v] for r in matched])
        for v in variables
    }

    intervals = []
    for left, right in zip(matched, matched[1:]):
        dt = right["year"] - left["year"]
        row = {
            "from": left["year"],
            "to": right["year"],
            "annualized_acres_change": (right["acres"] - left["acres"]) / dt,
        }
        for v in variables:
            row[f"annualized_{v}_change"] = (right[v] - left[v]) / dt
        intervals.append(row)

    x_change = [r["annualized_acres_change"] for r in intervals]
    change_corr = {}
    change_perm_p = {}
    for v in variables:
        y_change = [r[f"annualized_{v}_change"] for r in intervals]
        observed = pearson(x_change, y_change)
        change_corr[v] = observed
        change_perm_p[v] = permutation_p(x_change, y_change, observed)

    pairs = []
    for row in annual_rows:
        nxt = by_key.get((row["transect"], row["year"] + 1))
        if nxt is None:
            continue
        pairs.append(
            {
                "transect": row["transect"],
                "destination_year": row["year"] + 1,
                "p0": int(row["Thalassia"] > 0),
                "p1": int(nxt["Thalassia"] > 0),
                "f0": row["Thalassia"],
                "f1": nxt["Thalassia"],
            }
        )
    pre = [p for p in pairs if p["destination_year"] <= 2016]
    post = [p for p in pairs if p["destination_year"] >= 2017]
    pre_t, post_t = transition_summary(pre), transition_summary(post)

    grouped: dict[str, list[dict]] = defaultdict(list)
    for p in pairs:
        grouped[p["transect"]].append(p)
    transects = sorted(grouped)
    rng = random.Random(20260926)
    b_persist, b_recol, b_slope = [], [], []
    for _ in range(3000):
        sample = []
        for _j in transects:
            sample.extend(grouped[rng.choice(transects)])
        a = [p for p in sample if p["destination_year"] <= 2016]
        z = [p for p in sample if p["destination_year"] >= 2017]
        at, zt = transition_summary(a), transition_summary(z)
        if at["persistence"] is not None and zt["persistence"] is not None:
            b_persist.append(zt["persistence"] - at["persistence"])
        if at["recolonization"] is not None and zt["recolonization"] is not None:
            b_recol.append(zt["recolonization"] - at["recolonization"])
        sa = slope([p["f0"] for p in a], [p["f1"] for p in a])
        sz = slope([p["f0"] for p in z], [p["f1"] for p in z])
        if math.isfinite(sa) and math.isfinite(sz):
            b_slope.append(sz - sa)

    return {
        "design": {
            "analysis_status": "exploratory_v1",
            "breakpoint": 2016,
            "breakpoint_reason": "literature/management-defined peak in mapped bay-wide seagrass coverage; not estimated from the transect response",
            "mapping_year_count": len(matched),
            "annual_transect_rows": len(annual_rows),
        },
        "extent_frequency": {
            "level_correlation": level_corr,
            "annualized_change_correlation": change_corr,
            "annualized_change_permutation_p": change_perm_p,
            "change_2016_2022_pct": {
                "acres": 100 * (coverage[2022] / coverage[2016] - 1),
                "total_seagrass": 100 * (annual_mean[2022]["total_seagrass"] / annual_mean[2016]["total_seagrass"] - 1),
                "Thalassia": 100 * (annual_mean[2022]["Thalassia"] / annual_mean[2016]["Thalassia"] - 1),
            },
            "change_2016_2024_pct": {
                "acres": 100 * (coverage[2024] / coverage[2016] - 1),
                "total_seagrass": 100 * (annual_mean[2024]["total_seagrass"] / annual_mean[2016]["total_seagrass"] - 1),
                "Thalassia": 100 * (annual_mean[2024]["Thalassia"] / annual_mean[2016]["Thalassia"] - 1),
            },
            "matched_mapping_years": matched,
            "interval_changes": intervals,
        },
        "thalassia_memory": {
            "all": transition_summary(pairs),
            "through_2016": pre_t,
            "2017_2025": post_t,
            "frequency_lag_slope": {
                "through_2016": slope([p["f0"] for p in pre], [p["f1"] for p in pre]),
                "2017_2025": slope([p["f0"] for p in post], [p["f1"] for p in post]),
            },
            "post_minus_pre": {
                "persistence": post_t["persistence"] - pre_t["persistence"],
                "recolonization": post_t["recolonization"] - pre_t["recolonization"],
                "frequency_lag_slope": slope([p["f0"] for p in post], [p["f1"] for p in post]) - slope([p["f0"] for p in pre], [p["f1"] for p in pre]),
            },
            "cluster_bootstrap_95pct_post_minus_pre": {
                "persistence": [quantile(b_persist, 0.025), quantile(b_persist, 0.975)],
                "recolonization": [quantile(b_recol, 0.025), quantile(b_recol, 0.975)],
                "frequency_lag_slope": [quantile(b_slope, 0.025), quantile(b_slope, 0.975)],
            },
        },
        "claim_boundary": {
            "supported_exploratory": [
                "Fixed-transect Thalassia occurrence is strongly persistent year-to-year.",
                "The data do not support a post-2016 weakening of Thalassia local-state memory.",
                "Bay-wide mapped seagrass extent covaries strongly with total seagrass frequency at fixed transects, including in first differences.",
                "Thalassia-specific frequency is decoupled from bay-wide extent at this scale.",
            ],
            "requires_next_test": [
                "Whether mapped areal losses are concentrated at meadow edges while monitored core transects persist.",
                "Whether the decoupling is caused by temperature, salinity, nutrients, storms, or another environmental mechanism.",
                "Whether the original EOG adverse result was caused by this scale mismatch.",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annual", default="data/annual_transect_frequency.csv")
    parser.add_argument("--coverage", default="data/seagrass_coverage_tbep.csv")
    parser.add_argument("--output", default="results/exploratory_v1.json")
    args = parser.parse_args()
    result = analyze(load_annual(Path(args.annual)), load_coverage(Path(args.coverage)))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
