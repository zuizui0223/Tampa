#!/usr/bin/env python3
"""Audit original TBEP transect source semantics behind the 2016/2017 pulse.

Uses the pinned pre-Darwin-Core trnsct.csv at the same commit as the EOG/Tampa
source. This checks whether 25-Dec dates were introduced by Darwin Core conversion
or already existed in the source table, and whether date patterns concentrate by
monitoring agency / multi-day IDall records.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

COMMIT = "6c567beff95ea04f0e397101befb49d5233ace8f"
RAW = {
    "url": f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/data/trnsct.csv",
    "size": 17186023,
    "blob": "2a9ac04c300d4e209b1359656de6b581ad7ae138",
}
PULSE = {"S1T1", "S3T12", "S3T3", "S3T4", "S3T5"}


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def fetch() -> bytes:
    req = Request(RAW["url"], headers={"Accept-Encoding": "identity", "User-Agent": "Tampa-source-protocol-audit/1.0"})
    with urlopen(req, timeout=180) as response:
        data = response.read(RAW["size"] + 1)
    if len(data) != RAW["size"]:
        raise RuntimeError(f"raw size drift: {len(data)}")
    if git_blob_sha1(data) != RAW["blob"]:
        raise RuntimeError("raw Git blob drift")
    return data


def main(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    data = fetch()
    frame = pd.read_csv(io.BytesIO(data), low_memory=False)
    required = {"IDall", "ObservationDate", "Transect", "MonitoringAgency", "Site"}
    missing = required - set(frame.columns)
    if missing:
        raise RuntimeError(f"missing required raw fields: {sorted(missing)}")

    frame["parsed_datetime"] = pd.to_datetime(frame["ObservationDate"], errors="coerce", utc=True)
    if frame["parsed_datetime"].isna().any():
        raise RuntimeError(f"unparseable ObservationDate rows: {int(frame.parsed_datetime.isna().sum())}")
    frame["parsed_date"] = frame["parsed_datetime"].dt.date

    group = (
        frame.groupby("IDall", as_index=False)
        .agg(
            Transect=("Transect", "first"),
            monitoring_agencies=("MonitoringAgency", lambda x: "|".join(sorted({str(v) for v in x.dropna()}))),
            raw_rows=("IDall", "size"),
            sampled_sites=("Site", "nunique"),
            unique_dates=("parsed_date", "nunique"),
            min_date=("parsed_date", "min"),
            max_date=("parsed_date", "max"),
        )
    )
    group["year_min"] = pd.to_datetime(group.min_date).dt.year
    group["year_max"] = pd.to_datetime(group.max_date).dt.year
    group["min_equals_max"] = group.min_date == group.max_date
    group["min_is_dec25"] = pd.to_datetime(group.min_date).dt.strftime("%m-%d") == "12-25"
    group["max_is_dec25"] = pd.to_datetime(group.max_date).dt.strftime("%m-%d") == "12-25"

    y2016 = group[group.year_min == 2016].copy()
    dec25 = y2016[y2016.min_is_dec25].copy()
    agency_dec25 = (
        dec25.groupby("monitoring_agencies", dropna=False)
        .size()
        .sort_values(ascending=False)
        .rename("groups")
        .reset_index()
    )
    agency_all = (
        y2016.groupby("monitoring_agencies", dropna=False)
        .size()
        .sort_values(ascending=False)
        .rename("groups")
        .reset_index()
    )

    pulse = group[
        group.Transect.astype(str).isin(PULSE)
        & group.year_min.between(2015, 2017)
    ].copy().sort_values(["Transect", "min_date"])

    summary = {
        "schema": "tampa.source_protocol_audit.v1",
        "source": {"commit": COMMIT, "size": RAW["size"], "blob": RAW["blob"]},
        "raw": {
            "rows": int(len(frame)),
            "idall_groups": int(len(group)),
            "multi_day_idall_groups": int((group.unique_dates > 1).sum()),
            "max_unique_dates_per_idall": int(group.unique_dates.max()),
        },
        "2016": {
            "idall_groups": int(len(y2016)),
            "min_date_dec25_groups": int(len(dec25)),
            "fraction_min_date_dec25": float(len(dec25) / len(y2016)) if len(y2016) else None,
            "dec25_groups_with_multiple_raw_dates": int((dec25.unique_dates > 1).sum()),
            "dec25_groups_min_equals_max": int(dec25.min_equals_max.sum()),
            "agency_all_groups": agency_all.to_dict("records"),
            "agency_dec25_groups": agency_dec25.to_dict("records"),
        },
        "pulse": {
            "rows": pulse.astype(str).to_dict("records"),
            "all_2016_pulse_min_dates_already_in_raw_source": bool(
                ((pulse.year_min != 2016) | pulse.min_is_dec25 | (pd.to_datetime(pulse.min_date).dt.strftime("%m-%d") == "11-12")).all()
            ),
        },
        "date_semantics": {
            "pinned_obis_conversion": "minimum parsed date within IDall",
            "current_tbeptools_read_formtransect": "maximum parsed date within IDall",
            "implication": "For multi-day IDall groups, parent-event dates depend on formatter choice. If min=max, that specific date is already present in the raw source and is not created by min/max selection."
        },
        "claim_boundary": "This is a source/protocol audit only. A raw 25-Dec value may still be an upstream entry/default convention; this audit cannot establish that it was the true biological field date."
    }
    group.to_csv(outdir / "source_idall_date_audit.csv", index=False)
    pulse.to_csv(outdir / "source_pulse_raw_audit.csv", index=False)
    (outdir / "source_protocol_audit.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/generated"))
    args = parser.parse_args()
    main(args.out)
