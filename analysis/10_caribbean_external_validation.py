#!/usr/bin/env python3
"""Frozen v1 external validation of the Tampa quantitative early-warning hypothesis.

IMPORTANT: scientific choices are read from the committed frozen contract. This script
must not be edited after the PANGAEA response payload is opened and still be called v1.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class TerminalStop(RuntimeError):
    pass


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).lower()


def read_contract(path: Path) -> dict:
    return json.loads(path.read_text())


def fetch_payload(contract: dict) -> tuple[bytes, str]:
    url = "https://doi.org/" + contract["source"]["doi"]
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "text/tab-separated-values",
            "User-Agent": "Tampa-Caribbean-Early-Warning-v1/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            payload = response.read()
            final_url = response.geturl()
    except Exception as exc:
        raise TerminalStop(f"transport_failure:{type(exc).__name__}:{exc}") from exc
    if not payload:
        raise TerminalStop("empty_response_payload")
    return payload, final_url


def find_header(lines: list[str], contract: dict) -> tuple[int, list[str]]:
    required = contract["parser_contract"]["data_header_detection"]["required_position_prefixes"]
    min_cols = int(contract["parser_contract"]["data_header_detection"]["minimum_columns"])
    for i, line in enumerate(lines):
        row = next(csv.reader([line], delimiter="\t"))
        if len(row) < min_cols:
            continue
        ok = True
        for pos_str, prefix in required.items():
            pos = int(pos_str)
            if pos >= len(row) or not norm(row[pos]).startswith(norm(prefix)):
                ok = False
                break
        if ok:
            return i, row
    raise TerminalStop("declared_data_header_not_found")


def parse_datetime(value: str) -> pd.Timestamp:
    try:
        ts = pd.to_datetime(value.strip(), utc=True, errors="raise")
    except Exception as exc:
        raise TerminalStop(f"invalid_datetime:{value}") from exc
    if pd.isna(ts):
        raise TerminalStop(f"missing_datetime:{value}")
    return ts


def parse_float(value: str, label: str) -> float:
    try:
        x = float(value.strip())
    except Exception as exc:
        raise TerminalStop(f"invalid_numeric:{label}:{value}") from exc
    if not math.isfinite(x):
        raise TerminalStop(f"nonfinite_numeric:{label}:{value}")
    return x


def parse_dataset(payload: bytes, contract: dict) -> tuple[pd.DataFrame, dict]:
    try:
        text = payload.decode(contract["parser_contract"]["encoding"])
    except UnicodeDecodeError as exc:
        raise TerminalStop("payload_utf8_decode_failure") from exc

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    header_idx, header = find_header(lines, contract)
    expected_min = int(contract["parser_contract"]["expected_minimum_columns"])

    sample_meta: dict[tuple[str, str, str], dict] = {}
    focal_cover: dict[tuple[str, str, str], float] = {}
    node_meta: dict[str, dict[str, list]] = defaultdict(
        lambda: {"country": [], "location": [], "lat": [], "lon": []}
    )

    physical_rows = 0
    focal_rows = 0

    for raw_line in lines[header_idx + 1 :]:
        if not raw_line.strip() or raw_line.lstrip().startswith("/*") or raw_line.strip() == "*/":
            continue
        row = next(csv.reader([raw_line], delimiter="\t"))
        if len(row) < expected_min:
            raise TerminalStop(f"short_data_row:{len(row)}")
        physical_rows += 1

        country = row[1].strip()
        location = row[2].strip()
        loc_id = row[5].strip()
        stat_id = row[7].strip()
        if not country or not location or not loc_id or not stat_id:
            raise TerminalStop("missing_country_location_or_station_identity")

        latitude = parse_float(row[3], "latitude")
        longitude = parse_float(row[4], "longitude")
        dt = parse_datetime(row[8])

        qid = row[9].strip() or row[10].strip()
        if not qid:
            raise TerminalStop("missing_quadrat_identity")

        node = f"{loc_id}::{stat_id}"
        date_key = dt.isoformat()
        sample_key = (node, date_key, qid)

        if sample_key not in sample_meta:
            sample_meta[sample_key] = {
                "node_id": node,
                "country": country,
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "datetime": dt,
                "year": int(dt.year),
                "quadrat_id": qid,
            }
        else:
            prev = sample_meta[sample_key]
            if (
                prev["country"] != country
                or prev["location"] != location
                or abs(prev["latitude"] - latitude) > 1e-9
                or abs(prev["longitude"] - longitude) > 1e-9
            ):
                raise TerminalStop("quadrat_sample_metadata_inconsistency")

        node_meta[node]["country"].append(country)
        node_meta[node]["location"].append(location)
        node_meta[node]["lat"].append(latitude)
        node_meta[node]["lon"].append(longitude)

        taxon_fields = " ".join(row[11:14])
        taxon_norm = norm(taxon_fields)
        focal = (
            "thalassia testudinum" in taxon_norm
            or "374720" in taxon_norm
            or "taxname:374720" in taxon_norm
        )
        if focal:
            focal_rows += 1
            if sample_key in focal_cover:
                raise TerminalStop("duplicate_focal_row_for_quadrat_sample")
            cover = parse_float(row[14], "focal_percent_cover")
            if cover < 0 or cover > 100:
                raise TerminalStop(f"focal_percent_cover_out_of_range:{cover}")
            focal_cover[sample_key] = cover

    if physical_rows == 0:
        raise TerminalStop("zero_physical_data_rows")
    if focal_rows == 0:
        raise TerminalStop("zero_focal_taxon_rows_under_frozen_identity")

    # Validate node identity and derive one stable coordinate per node.
    node_summary: dict[str, dict] = {}
    for node, meta in node_meta.items():
        countries = set(meta["country"])
        locations = set(meta["location"])
        if len(countries) != 1 or len(locations) != 1:
            raise TerminalStop(f"node_identity_drift:{node}")
        lat_span = max(meta["lat"]) - min(meta["lat"])
        lon_span = max(meta["lon"]) - min(meta["lon"])
        if lat_span > 0.01 or lon_span > 0.01:
            raise TerminalStop(f"node_coordinate_drift_gt_0.01_degree:{node}")
        node_summary[node] = {
            "country": next(iter(countries)),
            "location": next(iter(locations)),
            "latitude": float(np.median(meta["lat"])),
            "longitude": float(np.median(meta["lon"])),
        }

    annual_samples: dict[tuple[str, int], list[tuple[str, str, str]]] = defaultdict(list)
    for key, meta in sample_meta.items():
        annual_samples[(meta["node_id"], meta["year"])].append(key)

    rows = []
    minimum_samples = int(contract["parser_contract"]["annual_candidate_min_quadrat_samples"])
    for (node, year), keys in sorted(annual_samples.items()):
        unique_keys = sorted(set(keys))
        if len(unique_keys) < minimum_samples:
            continue
        dates = sorted({sample_meta[k]["datetime"] for k in unique_keys})
        positive_keys = [k for k in unique_keys if focal_cover.get(k, 0.0) > 0]
        total_cover = float(sum(focal_cover.get(k, 0.0) for k in unique_keys))
        day_angles = np.asarray(
            [2.0 * np.pi * (int(d.dayofyear) - 1) / 365.2425 for d in dates],
            dtype=float,
        )
        meta = node_summary[node]
        rows.append(
            {
                "node_id": node,
                "year": int(year),
                "country": meta["country"],
                "location": meta["location"],
                "latitude": meta["latitude"],
                "longitude": meta["longitude"],
                "recorded_presence": int(len(positive_keys) > 0),
                "focal_frequency": float(len(positive_keys) / len(unique_keys)),
                "focal_cover_mean_all_quadrats": float(total_cover / len(unique_keys)),
                "survey_count": int(len(dates)),
                "quadrat_count": int(len(unique_keys)),
                "survey_sin_mean": float(np.sin(day_angles).mean()),
                "survey_cos_mean": float(np.cos(day_angles).mean()),
                "log_survey_count": float(np.log1p(len(dates))),
                "log_quadrat_count": float(np.log1p(len(unique_keys))),
            }
        )

    annual = pd.DataFrame(rows)
    audit = {
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "payload_bytes": len(payload),
        "header_columns": len(header),
        "physical_data_rows": physical_rows,
        "focal_rows": focal_rows,
        "unique_quadrat_samples": len(sample_meta),
        "unique_nodes": len(node_summary),
        "annual_station_years_after_min_quadrat_gate": int(len(annual)),
        "annual_positive_station_years": int(annual["recorded_presence"].sum()) if len(annual) else 0,
    }
    return annual, audit


def build_transitions(annual: pd.DataFrame) -> pd.DataFrame:
    transitions = []
    for node, group in annual.sort_values(["node_id", "year"]).groupby("node_id"):
        records = group.to_dict("records")
        for source, target in zip(records[:-1], records[1:]):
            if int(target["year"]) != int(source["year"]) + 1:
                continue
            if int(source["recorded_presence"]) != 1:
                continue
            transitions.append(
                {
                    "node_id": node,
                    "source_year": int(source["year"]),
                    "target_year": int(target["year"]),
                    "loss": int(1 - int(target["recorded_presence"])),
                    "country": source["country"],
                    "latitude": float(source["latitude"]),
                    "longitude": float(source["longitude"]),
                    "survey_sin_mean": float(source["survey_sin_mean"]),
                    "survey_cos_mean": float(source["survey_cos_mean"]),
                    "log_survey_count": float(source["log_survey_count"]),
                    "log_quadrat_count": float(source["log_quadrat_count"]),
                    "focal_frequency": float(source["focal_frequency"]),
                    "focal_cover_mean_all_quadrats": float(source["focal_cover_mean_all_quadrats"]),
                }
            )
    return pd.DataFrame(transitions)


def estimability(annual: pd.DataFrame, transitions: pd.DataFrame, contract: dict) -> tuple[bool, list[str]]:
    gate = contract["estimability_gate"]
    reasons = []
    if len(annual) < gate["minimum_annual_station_years"]:
        reasons.append("annual_station_years")
    if len(transitions) < gate["minimum_source_positive_consecutive_transitions"]:
        reasons.append("source_positive_consecutive_transitions")
    if len(transitions):
        losses = int(transitions["loss"].sum())
        persistence = int(len(transitions) - losses)
    else:
        losses = persistence = 0
    if losses < gate["minimum_recorded_losses"]:
        reasons.append("recorded_losses")
    if persistence < gate["minimum_recorded_persistence"]:
        reasons.append("recorded_persistence")
    return len(reasons) == 0, reasons


def make_model(contract: dict, augmented: bool) -> tuple[Pipeline, list[str]]:
    m = contract["model"]
    numeric = list(m["baseline_numeric"])
    if augmented:
        numeric += list(m["augmentation"])
    categorical = list(m["baseline_categorical"])
    pre = ColumnTransformer(
        [
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ],
        remainder="drop",
    )
    hp = m["hyperparameters"]
    model = LogisticRegression(
        C=float(hp["C"]),
        max_iter=int(hp["max_iter"]),
        solver=str(hp["solver"]),
    )
    return Pipeline([("preprocess", pre), ("model", model)]), numeric + categorical


def run_walkforward(transitions: pd.DataFrame, contract: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    gate = contract["estimability_gate"]
    yearly = []
    predictions = []

    for target_year in sorted(int(x) for x in transitions["target_year"].unique()):
        train = transitions[transitions["target_year"] < target_year].copy()
        test = transitions[transitions["target_year"] == target_year].copy()
        prior_losses = int(train["loss"].sum())
        prior_persistence = int(len(train) - prior_losses)
        if (
            prior_losses < gate["per_target_year_training_min_prior_losses"]
            or prior_persistence < gate["per_target_year_training_min_prior_persistence"]
        ):
            continue
        if len(test) == 0 or train["loss"].nunique() < 2:
            continue

        arm_probs = {}
        for arm, augmented in [("baseline", False), ("augmented", True)]:
            pipe, cols = make_model(contract, augmented)
            pipe.fit(train[cols], train["loss"])
            prob = pipe.predict_proba(test[cols])[:, 1]
            arm_probs[arm] = prob
            yearly.append(
                {
                    "target_year": target_year,
                    "arm": arm,
                    "n": int(len(test)),
                    "losses": int(test["loss"].sum()),
                    "train_n": int(len(train)),
                    "train_losses": prior_losses,
                    "log_loss": float(log_loss(test["loss"], prob, labels=[0, 1])),
                    "brier": float(brier_score_loss(test["loss"], prob)),
                }
            )

        for i, (_, row) in enumerate(test.iterrows()):
            predictions.append(
                {
                    "node_id": row["node_id"],
                    "target_year": target_year,
                    "loss": int(row["loss"]),
                    "p_baseline": float(arm_probs["baseline"][i]),
                    "p_augmented": float(arm_probs["augmented"][i]),
                }
            )

    return pd.DataFrame(yearly), pd.DataFrame(predictions)


def summarize(yearly: pd.DataFrame, predictions: pd.DataFrame, contract: dict) -> dict:
    min_years = int(contract["estimability_gate"]["minimum_scored_target_years"])
    if yearly.empty:
        return {"status": "terminal_non_estimable_external_validation", "reason": "zero_scored_target_years"}

    pivot = yearly.pivot(index="target_year", columns="arm", values="log_loss").dropna()
    if len(pivot) < min_years:
        return {
            "status": "terminal_non_estimable_external_validation",
            "reason": "fewer_than_minimum_scored_target_years",
            "scored_target_years": int(len(pivot)),
        }

    delta = pivot["augmented"] - pivot["baseline"]
    aug_wins = int((delta < 0).sum())
    base_wins = int((delta > 0).sum())
    required_wins = int(math.ceil(0.60 * len(pivot)))
    macro_baseline = float(pivot["baseline"].mean())
    macro_augmented = float(pivot["augmented"].mean())

    if macro_augmented < macro_baseline and aug_wins >= required_wins:
        terminal = "favorable_external_early_warning"
    elif macro_baseline < macro_augmented and base_wins >= required_wins:
        terminal = "adverse_external_early_warning"
    else:
        terminal = "no_confirmed_external_early_warning"

    pred = predictions[predictions["target_year"].isin(pivot.index)].copy()
    pooled = {
        "rows": int(len(pred)),
        "losses": int(pred["loss"].sum()),
        "baseline_log_loss": float(log_loss(pred["loss"], pred["p_baseline"], labels=[0, 1])),
        "augmented_log_loss": float(log_loss(pred["loss"], pred["p_augmented"], labels=[0, 1])),
        "baseline_brier": float(brier_score_loss(pred["loss"], pred["p_baseline"])),
        "augmented_brier": float(brier_score_loss(pred["loss"], pred["p_augmented"])),
    }
    if pred["loss"].nunique() == 2:
        pooled["baseline_auc"] = float(roc_auc_score(pred["loss"], pred["p_baseline"]))
        pooled["augmented_auc"] = float(roc_auc_score(pred["loss"], pred["p_augmented"]))

    return {
        "status": terminal,
        "scored_target_years": int(len(pivot)),
        "target_year_range": [int(pivot.index.min()), int(pivot.index.max())],
        "required_wins_for_directional_terminal": required_wins,
        "augmented_wins": aug_wins,
        "baseline_wins": base_wins,
        "ties": int((delta == 0).sum()),
        "macro_baseline_log_loss": macro_baseline,
        "macro_augmented_log_loss": macro_augmented,
        "macro_augmented_minus_baseline": float(macro_augmented - macro_baseline),
        "median_year_delta": float(delta.median()),
        "pooled": pooled,
    }


def main(contract_path: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    contract = read_contract(contract_path)
    result: dict = {
        "schema": "tampa.caribbean_external_early_warning_v1.result",
        "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        "source_doi": contract["source"]["doi"],
        "focal_taxon": contract["source"]["focal_taxon"],
    }

    try:
        payload, final_url = fetch_payload(contract)
        annual, audit = parse_dataset(payload, contract)
        transitions = build_transitions(annual)
        result["response_access"] = {
            "full_payload_requests": 1,
            "payload_bytes": audit["payload_bytes"],
            "payload_sha256": audit["payload_sha256"],
            "resolved_url": final_url,
            "raw_payload_persisted": False,
        }
        result["parse_audit"] = audit
        result["transition_registry"] = {
            "source_positive_consecutive_transitions": int(len(transitions)),
            "recorded_losses": int(transitions["loss"].sum()) if len(transitions) else 0,
            "recorded_persistence": int((transitions["loss"] == 0).sum()) if len(transitions) else 0,
            "target_years": sorted(int(x) for x in transitions["target_year"].unique()) if len(transitions) else [],
        }

        ok, reasons = estimability(annual, transitions, contract)
        if not ok:
            result["terminal"] = {
                "status": "terminal_non_estimable_external_validation",
                "failed_minima": reasons,
            }
        else:
            yearly, predictions = run_walkforward(transitions, contract)
            result["terminal"] = summarize(yearly, predictions, contract)
            annual.to_csv(outdir / "caribbean_annual_station_state.csv", index=False)
            transitions.to_csv(outdir / "caribbean_external_transitions.csv", index=False)
            yearly.to_csv(outdir / "caribbean_external_year_scores.csv", index=False)
            predictions.to_csv(outdir / "caribbean_external_predictions.csv", index=False)

    except TerminalStop as exc:
        result["terminal"] = {
            "status": "terminal_protocol_or_schema_stop",
            "reason": str(exc),
        }

    result["claim_boundary"] = [
        "Recorded loss is not demographic extinction.",
        "A favorable result is external predictive replication, not proof that low cover causes loss.",
        "An adverse or null result is retained without retuning predictors, annualization, or decision rules.",
        "Parser/schema failure after response access terminates v1 and is not repaired in place.",
    ]
    (outdir / "caribbean_external_early_warning_v1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True)
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("validation/caribbean_early_warning_v1/frozen_contract.json"),
    )
    parser.add_argument("--out", type=Path, default=Path("results/caribbean_external_v1"))
    args = parser.parse_args()
    main(args.contract, args.out)
