#!/usr/bin/env python3
"""Prospective annual-state memory analysis for Tampa Bay Thalassia testudinum.

The source is pinned to the exact public Darwin Core conversion used by the earlier EOG
Tampa endpoint. This script verifies source identity, reconstructs eligible fixed-transect
visits, annualizes repeated visits, estimates year-to-year state transitions, and performs
strict walk-forward prediction using only earlier annual states.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

COMMIT = "6c567beff95ea04f0e397101befb49d5233ace8f"
BASE = f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
EVENT = {
    "url": f"{BASE}/event.csv",
    "size": 24654717,
    "blob": "583b4d4e328290ab065346579eb4f29f03ea0f99",
}
OCC = {
    "url": f"{BASE}/occurrence.csv",
    "size": 12508487,
    "blob": "d34aeb5aedb72459d1e04059629cb09450df929e",
}
FOCAL = "Thalassia testudinum"
EXPECTED = {"candidate_units": 1497, "nodes": 71, "positive_units": 927, "contexts": 29}
TAUS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 7.0, 10.0]

EVENT_HEADER = [
    "eventID", "parentEventID", "eventType", "eventDate", "year", "month", "day",
    "decimalLatitude", "decimalLongitude", "geodeticDatum", "minimumDepthInMeters",
    "maximumDepthInMeters", "country", "countryCode", "stateProvince", "waterBody",
    "locality", "locationID", "samplingProtocol", "institutionCode", "datasetName",
    "datasetID", "license", "locationRemarks",
]
OCC_HEADER = [
    "occurrenceID", "eventID", "basisOfRecord", "occurrenceStatus", "scientificName",
    "scientificNameID", "taxonRank", "kingdom", "phylum", "class", "order", "family",
    "genus", "collectionCode", "recordedBy", "identificationRemarks",
]


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def fetch(spec: dict[str, object]) -> bytes:
    req = Request(
        str(spec["url"]),
        headers={"Accept-Encoding": "identity", "User-Agent": "Tampa-memory-study/1.0"},
    )
    with urlopen(req, timeout=120) as response:
        data = response.read(int(spec["size"]) + 1)
    if len(data) != int(spec["size"]):
        raise RuntimeError(f"source-size drift: {spec['url']} -> {len(data)}")
    if git_blob_sha1(data) != spec["blob"]:
        raise RuntimeError(f"Git-blob drift: {spec['url']}")
    return data


def parse_event(data: bytes) -> tuple[list[dict[str, object]], dict[str, str]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if reader.fieldnames != EVENT_HEADER:
        raise RuntimeError("event header drift")

    parents: dict[str, dict[str, object]] = {}
    children: dict[str, list[str]] = defaultdict(list)
    seen_event_ids: set[str] = set()

    for row_number, row in enumerate(reader, start=2):
        event_id = (row["eventID"] or "").strip()
        if not event_id or event_id in seen_event_ids:
            raise RuntimeError(f"invalid/duplicate eventID at row {row_number}")
        seen_event_ids.add(event_id)
        event_type = (row["eventType"] or "").strip()
        if row["geodeticDatum"].strip() != "EPSG:4326":
            raise RuntimeError(f"datum drift at row {row_number}")

        if event_type == "Transect":
            date = datetime.strptime(row["eventDate"], "%Y-%m-%d").date()
            if (int(row["year"]), int(row["month"]), int(row["day"])) != (
                date.year, date.month, date.day
            ):
                raise RuntimeError(f"date-field disagreement at row {row_number}")
            parents[event_id] = {
                "unit_id": event_id,
                "node_id": row["locationID"].strip(),
                "year": date.year,
                "date": date.isoformat(),
                "longitude": float(row["decimalLongitude"]),
                "latitude": float(row["decimalLatitude"]),
                "water_body": row["waterBody"].strip(),
            }
        elif event_type == "Point":
            parent = (row["parentEventID"] or "").strip()
            children[parent].append(event_id)
        else:
            raise RuntimeError(f"unsupported eventType {event_type!r}")

    candidates: list[dict[str, object]] = []
    child_to_parent: dict[str, str] = {}
    node_coord: dict[str, tuple[float, float]] = {}
    node_water: dict[str, str] = {}
    candidate_keys: set[tuple[str, str]] = set()

    for parent_id, parent in sorted(parents.items()):
        child_ids = children.get(parent_id, [])
        if len(child_ids) < 3:
            continue
        key = (str(parent["node_id"]), str(parent["date"]))
        if key in candidate_keys:
            raise RuntimeError(f"duplicate candidate key {key}")
        candidate_keys.add(key)

        node = str(parent["node_id"])
        coord = (float(parent["longitude"]), float(parent["latitude"]))
        water = str(parent["water_body"])
        if node in node_coord and node_coord[node] != coord:
            raise RuntimeError(f"stable coordinate drift: {node}")
        if node in node_water and node_water[node] != water:
            raise RuntimeError(f"stable water-body drift: {node}")
        node_coord[node] = coord
        node_water[node] = water

        candidate = dict(parent)
        candidate["child_point_count"] = len(child_ids)
        candidates.append(candidate)
        for child_id in child_ids:
            child_to_parent[child_id] = parent_id

    return candidates, child_to_parent


def parse_occurrence(
    data: bytes,
    candidates: list[dict[str, object]],
    child_to_parent: dict[str, str],
) -> tuple[dict[str, int], dict[str, set[str]], int]:
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""))
    header = next(reader)
    if header != OCC_HEADER:
        raise RuntimeError("occurrence header drift")
    col = {name: i for i, name in enumerate(header)}
    labels = {str(row["unit_id"]): 0 for row in candidates}
    species_by_parent: dict[str, set[str]] = defaultdict(set)
    occurrence_ids: set[str] = set()
    focal_rows = 0

    for row_number, row in enumerate(reader, start=2):
        if len(row) != len(header):
            raise RuntimeError(f"occurrence width drift at row {row_number}")
        occurrence_id = row[col["occurrenceID"]]
        if not occurrence_id or occurrence_id in occurrence_ids:
            raise RuntimeError(f"invalid/duplicate occurrenceID at row {row_number}")
        occurrence_ids.add(occurrence_id)

        event_id = row[col["eventID"]]
        if event_id not in child_to_parent:
            raise RuntimeError(f"unknown child eventID at row {row_number}")
        parent = child_to_parent[event_id]

        if row[col["basisOfRecord"]] != "HumanObservation":
            raise RuntimeError(f"basisOfRecord drift at row {row_number}")
        status = row[col["occurrenceStatus"]]
        if status not in {"present", "absent"}:
            raise RuntimeError(f"status drift at row {row_number}")
        scientific_name = row[col["scientificName"]]

        if status == "present":
            species_by_parent[parent].add(scientific_name)
        if scientific_name == FOCAL:
            if status != "present":
                raise RuntimeError(f"focal row not present at row {row_number}")
            labels[parent] = 1
            focal_rows += 1

    return labels, species_by_parent, focal_rows


def annualize(
    candidates: list[dict[str, object]], labels: dict[str, int]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    visit = pd.DataFrame([{**row, "label": int(labels[row["unit_id"]])} for row in candidates])
    annual = (
        visit.groupby(["node_id", "year"], as_index=False)
        .agg(
            label=("label", "max"),
            visits=("label", "size"),
            positive_visits=("label", "sum"),
            longitude=("longitude", "first"),
            latitude=("latitude", "first"),
            water_body=("water_body", "first"),
        )
        .sort_values(["node_id", "year"])
        .reset_index(drop=True)
    )
    return visit, annual


def build_transitions(annual: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, group in annual.groupby("node_id"):
        records = group.sort_values("year").to_dict("records")
        for previous, current in zip(records[:-1], records[1:]):
            if int(current["year"]) != int(previous["year"]) + 1:
                continue
            rows.append(
                {
                    **current,
                    "prev_label": int(previous["label"]),
                    "transition": f"{int(previous['label'])}->{int(current['label'])}",
                }
            )
    return pd.DataFrame(rows)


def transition_summary(transitions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for year, group in transitions.groupby("year"):
        n11 = int(((group.prev_label == 1) & (group.label == 1)).sum())
        n10 = int(((group.prev_label == 1) & (group.label == 0)).sum())
        n01 = int(((group.prev_label == 0) & (group.label == 1)).sum())
        n00 = int(((group.prev_label == 0) & (group.label == 0)).sum())
        persistence = n11 / (n11 + n10) if n11 + n10 else np.nan
        colonization = n01 / (n01 + n00) if n01 + n00 else np.nan
        rows.append(
            {
                "year": int(year),
                "n": len(group),
                "n11": n11,
                "n10": n10,
                "n01": n01,
                "n00": n00,
                "persistence": persistence,
                "colonization": colonization,
                "memory_contrast": persistence - colonization,
            }
        )
    return pd.DataFrame(rows)


def add_memory_features(annual: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, group in annual.groupby("node_id"):
        history: list[tuple[int, int]] = []
        for _, row in group.sort_values("year").iterrows():
            year = int(row["year"])
            record = row.to_dict()
            for tau in TAUS:
                if history:
                    ages = np.asarray([year - old_year for old_year, _ in history], dtype=float)
                    weights = np.exp(-ages / tau)
                    states = np.asarray([state for _, state in history], dtype=float)
                    record[f"exp_{tau:g}"] = float(np.average(states, weights=weights))
                else:
                    record[f"exp_{tau:g}"] = np.nan
            rows.append(record)
            history.append((year, int(row["label"])))
    return pd.DataFrame(rows)


def fit_score(train: pd.DataFrame, test: pd.DataFrame, numeric: list[str]) -> float:
    columns = numeric + ["water_body"]
    preprocess = ColumnTransformer(
        [
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["water_body"]),
        ]
    )
    model = make_pipeline(preprocess, LogisticRegression(max_iter=1500, C=1.0))
    model.fit(train[columns], train.label)
    probability = model.predict_proba(test[columns])[:, 1]
    return float(log_loss(test.label, probability, labels=[0, 1]))


def walkforward_memory(feature_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    for tau in TAUS:
        memory = f"exp_{tau:g}"
        for target_year in sorted(feature_frame.year.unique()):
            if int(target_year) < 2004:
                continue
            train = feature_frame[
                (feature_frame.year < target_year) & feature_frame[memory].notna()
            ].copy()
            test = feature_frame[
                (feature_frame.year == target_year) & feature_frame[memory].notna()
            ].copy()
            if len(test) == 0 or train.label.nunique() < 2:
                continue

            baseline = fit_score(train, test, ["longitude", "latitude", "year"])
            augmented = fit_score(
                train, test, ["longitude", "latitude", "year", memory]
            )
            rows.append(
                {
                    "tau_years": tau,
                    "year": int(target_year),
                    "n": len(test),
                    "baseline_log_loss": baseline,
                    "memory_log_loss": augmented,
                    "delta": augmented - baseline,
                }
            )

    scores = pd.DataFrame(rows)
    summary = (
        scores.groupby("tau_years", as_index=False)
        .agg(
            years=("year", "nunique"),
            baseline_mean_log_loss=("baseline_log_loss", "mean"),
            memory_mean_log_loss=("memory_log_loss", "mean"),
            mean_delta=("delta", "mean"),
            median_delta=("delta", "median"),
            wins=("delta", lambda values: int((values < 0).sum())),
        )
        .sort_values(["memory_mean_log_loss", "tau_years"])
        .reset_index(drop=True)
    )
    return scores, summary



SEAGRASS_TAXA = {
    "Thalassia": "Thalassia testudinum",
    "Halodule": "Halodule wrightii",
    "Syringodium": "Syringodium filiforme",
    "Ruppia": "Ruppia maritima",
}


def community_turnover(
    candidates: list[dict[str, object]],
    species_by_parent: dict[str, set[str]],
) -> tuple[pd.DataFrame, dict]:
    visit_rows = []
    for row in candidates:
        present = species_by_parent.get(str(row["unit_id"]), set())
        visit_rows.append(
            {
                "node_id": row["node_id"],
                "year": int(row["year"]),
                "water_body": row["water_body"],
                **{
                    name: int(scientific in present)
                    for name, scientific in SEAGRASS_TAXA.items()
                },
            }
        )
    visit_species = pd.DataFrame(visit_rows)
    annual_species = (
        visit_species.groupby(["node_id", "year", "water_body"], as_index=False)
        [list(SEAGRASS_TAXA)]
        .max()
        .sort_values(["node_id", "year"])
        .reset_index(drop=True)
    )

    transitions = []
    for _, group in annual_species.groupby("node_id"):
        records = group.sort_values("year").to_dict("records")
        for left, right in zip(records[:-1], records[1:]):
            if int(right["year"]) != int(left["year"]) + 1:
                continue
            record = {
                "node_id": right["node_id"],
                "year": int(right["year"]),
                "water_body": right["water_body"],
            }
            for taxon in SEAGRASS_TAXA:
                record[f"{taxon}_prev"] = int(left[taxon])
                record[taxon] = int(right[taxon])
            transitions.append(record)
    tr = pd.DataFrame(transitions)

    thal_prev = tr[tr.Thalassia_prev == 1].copy()
    loss = thal_prev[thal_prev.Thalassia == 0].copy()
    persistence = thal_prev[thal_prev.Thalassia == 1].copy()

    cooccurrence = {}
    for taxon in ["Halodule", "Syringodium", "Ruppia"]:
        a = int(loss[taxon].sum())
        b = int(len(loss) - a)
        c = int(persistence[taxon].sum())
        d = int(len(persistence) - c)
        alternative = "less" if taxon == "Syringodium" else "two-sided"
        test = fisher_exact([[a, b], [c, d]], alternative=alternative)
        cooccurrence[taxon] = {
            "loss_present": a,
            "loss_absent": b,
            "persistence_present": c,
            "persistence_absent": d,
            "odds_ratio": float(test.statistic),
            "p": float(test.pvalue),
            "alternative": alternative,
        }

    loss_2016 = loss[loss.year == 2016]
    gain_2017 = tr[
        (tr.year == 2017)
        & (tr.Thalassia_prev == 0)
        & (tr.Thalassia == 1)
    ]
    pulse_nodes = sorted(set(loss_2016.node_id) & set(gain_2017.node_id))
    pulse_state = annual_species[
        annual_species.node_id.isin(pulse_nodes)
        & annual_species.year.isin([2015, 2016, 2017])
    ].sort_values(["node_id", "year"])

    usable_loss = []
    annual_index = {
        (str(row.node_id), int(row.year)): row
        for row in annual_species.itertuples(index=False)
    }
    for row in loss.itertuples(index=False):
        nxt = annual_index.get((str(row.node_id), int(row.year) + 1))
        if nxt is not None:
            usable_loss.append(
                {
                    "node_id": str(row.node_id),
                    "loss_year": int(row.year),
                    "recovered_next_year": int(nxt.Thalassia),
                }
            )
    recovery = pd.DataFrame(usable_loss)
    pulse_recovered = recovery[recovery.loss_year == 2016]
    other_recovered = recovery[recovery.loss_year != 2016]
    recovery_test = fisher_exact(
        [
            [
                int(pulse_recovered.recovered_next_year.sum()),
                int(len(pulse_recovered) - pulse_recovered.recovered_next_year.sum()),
            ],
            [
                int(other_recovered.recovered_next_year.sum()),
                int(len(other_recovered) - other_recovered.recovered_next_year.sum()),
            ],
        ],
        alternative="greater",
    )

    summary = {
        "annual_species_rows": int(len(annual_species)),
        "consecutive_species_transitions": int(len(tr)),
        "thalassia": {
            "loss_events": int(len(loss)),
            "persistence_events": int(len(persistence)),
            "cooccurrence_at_destination": cooccurrence,
            "usable_loss_events_with_next_year": int(len(recovery)),
            "next_year_recovery_events": int(recovery.recovered_next_year.sum()),
            "pulse_2016_loss_events": int(len(pulse_recovered)),
            "pulse_2016_next_year_recoveries": int(pulse_recovered.recovered_next_year.sum()),
            "non2016_loss_events_with_next_year": int(len(other_recovered)),
            "non2016_next_year_recoveries": int(other_recovered.recovered_next_year.sum()),
            "pulse_recovery_fisher": {
                "odds_ratio": (
                    "inf" if math.isinf(float(recovery_test.statistic))
                    else float(recovery_test.statistic)
                ),
                "p": float(recovery_test.pvalue),
                "alternative": "greater",
            },
        },
        "pulse_nodes": pulse_nodes,
        "pulse_state_2015_2017": pulse_state.to_dict("records"),
        "interpretation_boundary": (
            "Exploratory community-state analysis on the same frozen visit registry. "
            "Co-occurrence and recovery tests are data-derived and not confirmatory."
        ),
    }
    return annual_species, summary

def main(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    event_bytes = fetch(EVENT)
    occurrence_bytes = fetch(OCC)
    candidates, child_to_parent = parse_event(event_bytes)
    labels, species, focal_rows = parse_occurrence(
        occurrence_bytes, candidates, child_to_parent
    )

    observed = {
        "candidate_units": len(candidates),
        "nodes": len({row["node_id"] for row in candidates}),
        "positive_units": int(sum(labels.values())),
        "contexts": len({row["year"] for row in candidates}),
    }
    if observed != EXPECTED:
        raise RuntimeError(f"frozen endpoint count mismatch: {observed}")

    visit, annual = annualize(candidates, labels)
    transitions = build_transitions(annual)
    transition_by_year = transition_summary(transitions)
    annual_by_year = (
        annual.groupby("year", as_index=False)
        .agg(
            n_nodes=("label", "size"),
            positive_nodes=("label", "sum"),
            visits=("visits", "sum"),
        )
    )
    annual_by_year["prevalence"] = annual_by_year.positive_nodes / annual_by_year.n_nodes

    loss_2016 = transitions[
        (transitions.year == 2016)
        & (transitions.prev_label == 1)
        & (transitions.label == 0)
    ]
    gain_2017 = transitions[
        (transitions.year == 2017)
        & (transitions.prev_label == 0)
        & (transitions.label == 1)
    ]

    previous_positive_2016 = transitions[
        (transitions.year == 2016) & (transitions.prev_label == 1)
    ]
    prior_positive = transitions[
        (transitions.year >= 1999)
        & (transitions.year < 2016)
        & (transitions.prev_label == 1)
    ]
    loss_table = [
        [len(loss_2016), int((previous_positive_2016.label == 1).sum())],
        [int((prior_positive.label == 0).sum()), int((prior_positive.label == 1).sum())],
    ]
    loss_test = fisher_exact(loss_table, alternative="greater")

    previous_absent_2017 = transitions[
        (transitions.year == 2017) & (transitions.prev_label == 0)
    ]
    prior_absent = transitions[
        (transitions.year >= 1999)
        & (transitions.year < 2017)
        & (transitions.prev_label == 0)
    ]
    gain_table = [
        [len(gain_2017), int((previous_absent_2017.label == 0).sum())],
        [int((prior_absent.label == 1).sum()), int((prior_absent.label == 0).sum())],
    ]
    gain_test = fisher_exact(gain_table, alternative="greater")

    feature_frame = add_memory_features(annual)
    memory_scores, memory_summary = walkforward_memory(feature_frame)
    best = memory_summary.iloc[0].to_dict()
    annual_species, community_summary = community_turnover(candidates, species)

    pulse_species: dict[str, dict[str, object]] = {}
    for node in sorted(loss_2016.node_id):
        pulse_species[node] = {}
        for year in [2015, 2016, 2017]:
            units = [
                str(row["unit_id"])
                for row in candidates
                if row["node_id"] == node and int(row["year"]) == year
            ]
            present = sorted(set().union(*(species[unit] for unit in units))) if units else []
            pulse_species[node][str(year)] = {
                "candidate_units": units,
                "species_present": present,
                "thalassia_recorded": FOCAL in present,
            }

    summary = {
        "source_commit": COMMIT,
        "source_verified": True,
        "candidate_visits": len(visit),
        "annual_node_years": len(annual),
        "nodes": int(annual.node_id.nunique()),
        "years": [int(annual.year.min()), int(annual.year.max())],
        "positive_visits": int(visit.label.sum()),
        "focal_point_rows": int(focal_rows),
        "consecutive_year_transitions": len(transitions),
        "loss_2016": {
            "n": len(loss_2016),
            "nodes": sorted(loss_2016.node_id.tolist()),
            "fisher_vs_prior": {
                "table": loss_table,
                "odds_ratio": float(loss_test.statistic),
                "p": float(loss_test.pvalue),
            },
        },
        "gain_2017": {
            "n": len(gain_2017),
            "nodes": sorted(gain_2017.node_id.tolist()),
            "fisher_vs_prior": {
                "table": gain_table,
                "odds_ratio": float(gain_test.statistic),
                "p": float(gain_test.pvalue),
            },
        },
        "same_nodes_loss_2016_gain_2017": sorted(
            set(loss_2016.node_id) & set(gain_2017.node_id)
        ),
        "walkforward": {
            "best_tau_years": float(best["tau_years"]),
            "target_years": int(best["years"]),
            "matched_baseline_mean_log_loss": float(best["baseline_mean_log_loss"]),
            "memory_mean_log_loss": float(best["memory_mean_log_loss"]),
            "mean_delta": float(best["mean_delta"]),
            "wins": int(best["wins"]),
        },
        "interpretation_boundary": (
            "Exploratory annual recorded-detection/community-state memory. "
            "No climate-causal, demographic extinction/recolonization, or occupancy claim."
        ),
    }

    visit.to_csv(outdir / "visit_panel.csv", index=False)
    annual.to_csv(outdir / "annual_panel.csv", index=False)
    annual_by_year.to_csv(outdir / "year_summary.csv", index=False)
    transitions.to_csv(outdir / "transitions.csv", index=False)
    transition_by_year.to_csv(outdir / "transition_by_year.csv", index=False)
    memory_scores.to_csv(outdir / "memory_walkforward.csv", index=False)
    memory_summary.to_csv(outdir / "memory_summary.csv", index=False)
    annual_species.to_csv(outdir / "annual_species_panel.csv", index=False)
    with (outdir / "community_summary.json").open("w") as handle:
        json.dump(community_summary, handle, indent=2, sort_keys=True)
    with (outdir / "pulse_species_composition.json").open("w") as handle:
        json.dump(pulse_species, handle, indent=2, sort_keys=True)
    with (outdir / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/generated"))
    args = parser.parse_args()
    main(args.out)
