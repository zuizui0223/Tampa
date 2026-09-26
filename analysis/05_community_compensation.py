#!/usr/bin/env python3
"""Community-state compensation analysis for Tampa Bay seagrasses.

Reconstructs species-specific frequency occurrence and Braun-Blanquet abundance
for four seagrasses from the pinned Darwin Core source, then tests whether
post-2016 Thalassia state changes are accompanied by opposing changes in other
seagrasses at the same fixed transects.

This is an exploratory community-state analysis. Negative coupling is consistent
with replacement/compensation but does not by itself identify competition or causality.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

COMMIT = "6c567beff95ea04f0e397101befb49d5233ace8f"
BASE = f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FILES = {
    "event": {"url": f"{BASE}/event.csv", "size": 24654717, "blob": "583b4d4e328290ab065346579eb4f29f03ea0f99"},
    "occurrence": {"url": f"{BASE}/occurrence.csv", "size": 12508487, "blob": "d34aeb5aedb72459d1e04059629cb09450df929e"},
    "emof": {"url": f"{BASE}/emof.csv", "size": 16449353, "blob": "e463046726080334637824555309fd89c7c447da"},
}
SPECIES = {
    "Thalassia": "Thalassia testudinum",
    "Halodule": "Halodule wrightii",
    "Syringodium": "Syringodium filiforme",
    "Ruppia": "Ruppia maritima",
}
COVER_TYPE = "seagrass percent cover (Braun-Blanquet scale)"
BOOTSTRAPS = 2000
SEED = 20260926

EVENT_HEADER = [
    "eventID","parentEventID","eventType","eventDate","year","month","day",
    "decimalLatitude","decimalLongitude","geodeticDatum","minimumDepthInMeters",
    "maximumDepthInMeters","country","countryCode","stateProvince","waterBody",
    "locality","locationID","samplingProtocol","institutionCode","datasetName",
    "datasetID","license","locationRemarks",
]
OCC_HEADER = [
    "occurrenceID","eventID","basisOfRecord","occurrenceStatus","scientificName",
    "scientificNameID","taxonRank","kingdom","phylum","class","order","family",
    "genus","collectionCode","recordedBy","identificationRemarks",
]
EMOF_HEADER = [
    "eventID","occurrenceID","measurementType","measurementTypeID",
    "measurementValue","measurementUnit","measurementUnitID","measurementRemarks",
]


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def fetch(spec: dict) -> bytes:
    req = Request(spec["url"], headers={"Accept-Encoding": "identity", "User-Agent": "Tampa-community-state/1.0"})
    with urlopen(req, timeout=180) as response:
        data = response.read(spec["size"] + 1)
    if len(data) != spec["size"]:
        raise RuntimeError(f"source-size drift: {spec['url']} -> {len(data)}")
    if git_blob_sha1(data) != spec["blob"]:
        raise RuntimeError(f"Git-blob drift: {spec['url']}")
    return data


def parse_event(data: bytes):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if reader.fieldnames != EVENT_HEADER:
        raise RuntimeError("event header drift")
    parents, children = {}, defaultdict(list)
    for row in reader:
        typ = row["eventType"].strip()
        eid = row["eventID"].strip()
        if typ == "Transect":
            date = datetime.strptime(row["eventDate"], "%Y-%m-%d").date()
            parents[eid] = {
                "unit_id": eid,
                "node_id": row["locationID"].strip(),
                "year": date.year,
                "date": date.isoformat(),
                "water_body": row["waterBody"].strip(),
            }
        elif typ == "Point":
            children[row["parentEventID"].strip()].append(eid)
    candidates = {pid: p for pid, p in parents.items() if len(children.get(pid, [])) >= 3}
    child_to_parent = {child: pid for pid in candidates for child in children[pid]}
    return candidates, children, child_to_parent


def parse_occurrence(data: bytes, child_to_parent: dict[str, str]):
    reverse = {scientific: short for short, scientific in SPECIES.items()}
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if reader.fieldnames != OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    occurrence_species = {}
    by_child = defaultdict(lambda: defaultdict(list))
    for row in reader:
        child = row["eventID"]
        if child not in child_to_parent:
            continue
        sci = row["scientificName"]
        short = reverse.get(sci)
        if short is None:
            continue
        if row["occurrenceStatus"] != "present":
            raise RuntimeError(f"target seagrass row is not present: {sci}")
        oid = row["occurrenceID"]
        occurrence_species[oid] = short
        by_child[child][short].append(oid)
    return occurrence_species, by_child


def parse_cover(data: bytes, occurrence_species: dict[str, str]):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if reader.fieldnames != EMOF_HEADER:
        raise RuntimeError("emof header drift")
    cover = defaultdict(list)
    nonnumeric = defaultdict(int)
    for row in reader:
        oid = row["occurrenceID"]
        short = occurrence_species.get(oid)
        if short is None or row["measurementType"] != COVER_TYPE:
            continue
        try:
            value = float(row["measurementValue"].strip())
        except Exception:
            nonnumeric[short] += 1
            continue
        if math.isfinite(value):
            cover[oid].append(value)
    return cover, dict(nonnumeric)


def build_visit_panel(candidates, children, by_child, cover):
    rows = []
    for pid, parent in sorted(candidates.items()):
        child_ids = children[pid]
        record = dict(parent)
        record["child_point_count"] = len(child_ids)
        for short in SPECIES:
            present_points = 0
            all_point_cover = []
            for child in child_ids:
                oids = by_child[child].get(short, [])
                if not oids:
                    all_point_cover.append(0.0)
                    continue
                present_points += 1
                values = []
                for oid in oids:
                    values.extend(cover.get(oid, []))
                all_point_cover.append(float(np.mean(values)) if values else np.nan)
            record[f"{short}_frequency"] = present_points / len(child_ids)
            record[f"{short}_cover_index"] = (
                float(np.nanmean(all_point_cover))
                if np.isfinite(np.asarray(all_point_cover, dtype=float)).any()
                else np.nan
            )
        rows.append(record)
    return pd.DataFrame(rows)


def annualize(visit: pd.DataFrame):
    metric_cols = []
    for short in SPECIES:
        metric_cols += [f"{short}_frequency", f"{short}_cover_index"]
    aggregations = {metric: (metric, "mean") for metric in metric_cols}
    aggregations.update(
        water_body=("water_body", "first"),
        visits=("unit_id", "size"),
        child_point_count=("child_point_count", "mean"),
        date=("date", "first"),
    )
    annual = (
        visit.groupby(["node_id", "year"], as_index=False)
        .agg(**aggregations)
        .sort_values(["node_id", "year"])
        .reset_index(drop=True)
    )
    annual["date"] = pd.to_datetime(annual["date"])
    annual["doy"] = annual.date.dt.dayofyear
    annual["sin_doy"] = np.sin(2 * np.pi * (annual.doy - 1) / 365.2425)
    annual["cos_doy"] = np.cos(2 * np.pi * (annual.doy - 1) / 365.2425)
    annual["log_points"] = np.log(annual.child_point_count)
    return annual


def within_node_year_slope(frame: pd.DataFrame, metric: str, min_years: int = 5):
    d = frame[["node_id", "year", "sin_doy", "cos_doy", "log_points", metric]].dropna().copy()
    counts = d.groupby("node_id").size()
    nodes = sorted(counts[counts >= min_years].index.tolist())
    d = d[d.node_id.isin(nodes)]
    if len(nodes) < 3:
        return None
    variables = ["year", "sin_doy", "cos_doy", "log_points"]
    cross = {}
    for node, group in d.groupby("node_id"):
        x = group[variables].to_numpy(float)
        y = group[metric].to_numpy(float)
        x -= x.mean(axis=0)
        y -= y.mean()
        cross[node] = (x.T @ x, x.T @ y)

    def estimate(selected):
        xtx = np.sum([cross[node][0] for node in selected], axis=0)
        xty = np.sum([cross[node][1] for node in selected], axis=0)
        return np.linalg.pinv(xtx) @ xty

    beta = estimate(nodes)
    rng = np.random.default_rng(SEED)
    boot = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        selected = rng.choice(nodes, len(nodes), replace=True).tolist()
        boot[i] = estimate(selected)[0]
    ci = np.quantile(boot, [0.025, 0.975])
    return {
        "nodes": len(nodes),
        "rows": int(len(d)),
        "year_slope": float(beta[0]),
        "year_slope_ci95": [float(ci[0]), float(ci[1])],
    }


def consecutive_differences(annual: pd.DataFrame):
    rows = []
    metric_cols = [f"{s}_frequency" for s in SPECIES] + [f"{s}_cover_index" for s in SPECIES]
    for node, group in annual.groupby("node_id"):
        records = group.sort_values("year").to_dict("records")
        for left, right in zip(records[:-1], records[1:]):
            if int(right["year"]) != int(left["year"]) + 1:
                continue
            if not (2016 <= int(right["year"]) <= 2025):
                continue
            record = {
                "node_id": node,
                "year": int(right["year"]),
                "water_body": right["water_body"],
            }
            for metric in metric_cols:
                record[f"d_{metric}"] = float(right[metric]) - float(left[metric])
            rows.append(record)
    return pd.DataFrame(rows)


def compensation_correlations(diff: pd.DataFrame):
    out = {}
    for segment, group in diff.groupby("water_body"):
        out[segment] = {}
        for scale in ["frequency", "cover_index"]:
            target = f"d_Thalassia_{scale}"
            out[segment][scale] = {}
            for alt in ["Halodule", "Syringodium", "Ruppia"]:
                alt_col = f"d_{alt}_{scale}"
                pair = group[[target, alt_col]].dropna()
                if len(pair) < 10 or pair[target].nunique() < 2 or pair[alt_col].nunique() < 2:
                    out[segment][scale][alt] = None
                    continue
                test = spearmanr(pair[target], pair[alt_col])
                out[segment][scale][alt] = {
                    "n": int(len(pair)),
                    "spearman_rho": float(test.statistic),
                    "p": float(test.pvalue),
                }
    return out


def main(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    raw = {name: fetch(spec) for name, spec in FILES.items()}
    candidates, children, child_to_parent = parse_event(raw["event"])
    occurrence_species, by_child = parse_occurrence(raw["occurrence"], child_to_parent)
    cover, nonnumeric = parse_cover(raw["emof"], occurrence_species)
    visit = build_visit_panel(candidates, children, by_child, cover)
    annual = annualize(visit)

    post = annual[annual.year.between(2016, 2025)].copy()
    slopes = {}
    for segment in sorted(post.water_body.unique()):
        slopes[segment] = {}
        segment_frame = post[post.water_body == segment]
        for short in SPECIES:
            slopes[segment][short] = {}
            for scale in ["frequency", "cover_index"]:
                metric = f"{short}_{scale}"
                slopes[segment][short][scale] = within_node_year_slope(segment_frame, metric)

    diff = consecutive_differences(annual)
    coupling = compensation_correlations(diff)

    segment_year = (
        annual.groupby(["water_body", "year"], as_index=False)
        [[f"{s}_{scale}" for s in SPECIES for scale in ["frequency", "cover_index"]]]
        .mean()
    )

    summary = {
        "analysis": "seagrass_community_compensation_v1",
        "source_commit": COMMIT,
        "source_verified": True,
        "registry": {
            "candidate_visits": int(len(visit)),
            "annual_node_years": int(len(annual)),
            "nodes": int(annual.node_id.nunique()),
            "years": [int(annual.year.min()), int(annual.year.max())],
        },
        "nonnumeric_cover_rows": nonnumeric,
        "post2016_within_node_slopes": slopes,
        "year_to_year_coupling": coupling,
        "claim_boundary": [
            "Opposing species changes are descriptive evidence of community compensation/replacement, not proof of competition.",
            "Braun-Blanquet cover is an ordinal abundance index, not percentage cover.",
            "Survey-date and sampled-point-count controls are included in post-2016 slope models.",
        ],
    }
    visit.to_csv(outdir / "community_quant_visit.csv", index=False)
    annual.to_csv(outdir / "community_quant_annual.csv", index=False)
    segment_year.to_csv(outdir / "community_quant_segment_year.csv", index=False)
    diff.to_csv(outdir / "community_quant_differences.csv", index=False)
    (outdir / "community_compensation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/generated"))
    args = parser.parse_args()
    main(args.out)
