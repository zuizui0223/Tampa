#!/usr/bin/env python3
"""Post-hoc ecological analysis of persistent Zostera state in NPS Tier-3 data.

This is NOT a rerun or rescue of the frozen NPS v2 external predictive endpoint.
That endpoint terminated non-estimable because it contained zero recorded-loss
transitions. Here the already-opened public dataset is used for a different,
explicitly exploratory ecological question:

    Can binary recorded presence remain saturated while quantitative Zostera
    frequency and cover vary substantially through time?

The parser and annual-state construction are kept identical to the frozen v2
contract wherever possible.
"""
from __future__ import annotations

import csv
import io
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "validation/nps_tier3_v2/final_outcome_contract.json").read_text())
FROZEN = json.loads((ROOT / "validation/nps_tier3_v2/terminal_outcome_result.json").read_text())

SEED = 20260927
BOOT = 5000


class ParseStop(RuntimeError):
    pass


def req_text(x, label):
    s = "" if x is None else str(x).strip()
    if not s:
        raise ParseStop(f"blank_required:{label}")
    return s


def parse_cover(x, rownum):
    s = "" if x is None else str(x).strip()
    if not s:
        raise ParseStop(f"blank_percent_cover:row{rownum}")
    if s == CONTRACT["parser"]["percent_cover_missing_token"]:
        return None
    try:
        v = float(s)
    except Exception as exc:
        raise ParseStop(f"nonnumeric_percent_cover:row{rownum}:{s!r}") from exc
    lo, hi = CONTRACT["parser"]["percent_cover_valid_range"]
    if not math.isfinite(v) or not (lo <= v <= hi):
        raise ParseStop(f"percent_cover_out_of_range:row{rownum}:{s}")
    return v


def download():
    req = Request(
        CONTRACT["source"]["response_url"],
        headers={"Accept-Encoding": "identity", "User-Agent": "Tampa-NPS-Posthoc-State/1.0"},
    )
    with urlopen(req, timeout=90) as r:
        if r.status != 200:
            raise ParseStop(f"response_http_{r.status}")
        data = r.read(int(CONTRACT["source"]["expected_bytes"]) + 1)
    if len(data) != int(CONTRACT["source"]["expected_bytes"]):
        raise ParseStop(f"response_size_drift:{len(data)}")
    return data


def parse_rows(data):
    text = data.decode(CONTRACT["parser"]["encoding"])
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=CONTRACT["parser"]["delimiter"])
    header = next(reader)
    if header != CONTRACT["source"]["expected_physical_header"]:
        raise ParseStop("header_drift")
    col = {h: i for i, h in enumerate(header)}
    out = []
    seen = set()
    for rownum, row in enumerate(reader, start=2):
        if len(row) != CONTRACT["parser"]["exact_row_width"]:
            raise ParseStop(f"row_width:{rownum}")
        rid = req_text(row[col["ID"]], f"ID row {rownum}")
        if rid in seen:
            raise ParseStop(f"duplicate_ID:{rid}")
        seen.add(rid)
        species = req_text(row[col["Species"]], f"Species row {rownum}")
        if species not in CONTRACT["parser"]["allowed_species_codes"]:
            raise ParseStop(f"unexpected_species:{species}")
        d = datetime.strptime(req_text(row[col["Date"]], f"Date row {rownum}"), CONTRACT["parser"]["date_format"]).date()
        q = float(req_text(row[col["Quadrat"]], f"Quadrat row {rownum}"))
        if not q.is_integer():
            raise ParseStop(f"quadrat_not_integer:{rownum}")
        q = int(q)
        out.append(
            {
                "ID": rid,
                "Location": req_text(row[col["Location"]], f"Location row {rownum}"),
                "SGNetCode": req_text(row[col["SGNetCode"]], f"SGNetCode row {rownum}"),
                "Transect": req_text(row[col["Transect"]], f"Transect row {rownum}"),
                "Quadrat": q,
                "Species": species,
                "Date": d,
                "Year": d.year,
                "PercentCover": parse_cover(row[col["Percent Cover"]], rownum),
            }
        )
    return out


def annualize(rows):
    cells = defaultdict(lambda: {"dates": set(), "species": defaultdict(list), "Location": set()})
    for r in rows:
        key = (r["SGNetCode"], r["Transect"], r["Quadrat"], r["Year"])
        rec = cells[key]
        rec["dates"].add(r["Date"].isoformat())
        rec["Location"].add(r["Location"])
        rec["species"][r["Species"]].append(r["PercentCover"])

    groups = defaultdict(list)
    for (site, tran, q, year), rec in cells.items():
        groups[(site, tran, year)].append((q, rec))

    states = []
    minobs = int(CONTRACT["annual_state"]["minimum_reobserved_quadrats"])
    minquant = int(CONTRACT["annual_state"]["minimum_quantitative_quadrats"])
    for (site, tran, year), items in groups.items():
        seen_q, zm_q, quant, dates, locations = set(), set(), [], set(), set()
        for q, rec in items:
            seen_q.add(q)
            dates.update(rec["dates"])
            locations.update(rec["Location"])
            spp = rec["species"]
            if "ZM" in spp:
                zm_q.add(q)
                vals = [v for v in spp["ZM"] if v is not None]
                if vals:
                    quant.append(float(np.mean(vals)))
            else:
                # Same frozen v2 semantics: an observed seagrass-bearing quadrat with
                # RM but no ZM is a focal quantitative zero, not a missing quadrat.
                quant.append(0.0)
        if len(locations) != 1:
            raise ParseStop(f"location_drift:{site}:{tran}:{year}")
        if len(seen_q) < minobs or len(quant) < minquant:
            continue
        states.append(
            {
                "node_id": f"{site}::{tran}",
                "SGNetCode": site,
                "Transect": tran,
                "Location": next(iter(locations)),
                "year": int(year),
                "observed_quadrat_count": len(seen_q),
                "quantitative_quadrat_count": len(quant),
                "survey_count": len(dates),
                "focal_frequency": len(zm_q) / len(seen_q),
                "focal_mean_cover": float(np.mean(quant)),
                "recorded_presence": len(zm_q) > 0,
            }
        )
    return pd.DataFrame(states).sort_values(["node_id", "year"]).reset_index(drop=True)


def consecutive(df):
    rows = []
    for node, g in df.groupby("node_id"):
        recs = g.sort_values("year").to_dict("records")
        for a, b in zip(recs[:-1], recs[1:]):
            if b["year"] != a["year"] + 1:
                continue
            rows.append(
                {
                    "node_id": node,
                    "Location": a["Location"],
                    "source_year": a["year"],
                    "target_year": b["year"],
                    "delta_frequency": b["focal_frequency"] - a["focal_frequency"],
                    "delta_cover": b["focal_mean_cover"] - a["focal_mean_cover"],
                    "abs_delta_frequency": abs(b["focal_frequency"] - a["focal_frequency"]),
                    "abs_delta_cover": abs(b["focal_mean_cover"] - a["focal_mean_cover"]),
                }
            )
    return pd.DataFrame(rows)


def node_sufficient(df, ycol):
    out = []
    for node, g in df.groupby("node_id"):
        if len(g) < 2:
            continue
        x = g["year"].to_numpy(float)
        y = g[ycol].to_numpy(float)
        xc = x - x.mean()
        yc = y - y.mean()
        sxx = float(np.dot(xc, xc))
        if sxx <= 0:
            continue
        out.append(
            {
                "node_id": node,
                "Location": str(g["Location"].iloc[0]),
                "n": len(g),
                "year_min": int(x.min()),
                "year_max": int(x.max()),
                "sxx": sxx,
                "sxy": float(np.dot(xc, yc)),
                "slope": float(np.dot(xc, yc) / sxx),
                "min": float(y.min()),
                "max": float(y.max()),
                "range": float(y.max() - y.min()),
            }
        )
    return pd.DataFrame(out)


def pooled_slope(node_stats):
    return float(node_stats["sxy"].sum() / node_stats["sxx"].sum())


def bootstrap_slope(node_stats, seed):
    rng = np.random.default_rng(seed)
    vals = []
    n = len(node_stats)
    sxx = node_stats["sxx"].to_numpy(float)
    sxy = node_stats["sxy"].to_numpy(float)
    for _ in range(BOOT):
        idx = rng.integers(0, n, n)
        den = sxx[idx].sum()
        vals.append(float(sxy[idx].sum() / den) if den > 0 else np.nan)
    a = np.asarray(vals)
    return [float(np.nanquantile(a, 0.025)), float(np.nanquantile(a, 0.975))]


def metric_summary(df, ycol, seed):
    ns = node_sufficient(df, ycol)
    overall = {
        "within_node_slope_per_year": pooled_slope(ns),
        "node_bootstrap_ci95": bootstrap_slope(ns, seed),
        "n_nodes": int(len(ns)),
        "negative_node_slopes": int((ns["slope"] < 0).sum()),
        "positive_node_slopes": int((ns["slope"] > 0).sum()),
        "median_within_node_range": float(ns["range"].median()),
        "q25_within_node_range": float(ns["range"].quantile(0.25)),
        "q75_within_node_range": float(ns["range"].quantile(0.75)),
    }
    locations = {}
    for i, (loc, g) in enumerate(ns.groupby("Location")):
        if len(g) < 2:
            continue
        locations[str(loc)] = {
            "n_nodes": int(len(g)),
            "within_node_slope_per_year": pooled_slope(g),
            "node_bootstrap_ci95": bootstrap_slope(g, seed + 100 + i),
            "negative_node_slopes": int((g["slope"] < 0).sum()),
            "positive_node_slopes": int((g["slope"] > 0).sum()),
            "median_within_node_range": float(g["range"].median()),
        }
    return overall, locations, ns


def main(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    data = download()
    raw = parse_rows(data)
    annual = annualize(raw)

    # Must reproduce the already-frozen non-estimable endpoint state exactly.
    expected = FROZEN["state_summary"]
    assert len(annual) == expected["annual_units"], (len(annual), expected)
    assert annual["node_id"].nunique() == expected["nodes"]
    assert int(annual["recorded_presence"].sum()) == expected["present_units"]
    assert bool(annual["recorded_presence"].all()) is True

    tr = consecutive(annual)
    assert len(tr) == FROZEN["estimability"]["source_positive_consecutive_transitions"]

    cover_overall, cover_locations, cover_nodes = metric_summary(annual, "focal_mean_cover", SEED)
    freq_overall, freq_locations, freq_nodes = metric_summary(annual, "focal_frequency", SEED + 1)

    abs_cover = tr["abs_delta_cover"].to_numpy(float)
    abs_freq = tr["abs_delta_frequency"].to_numpy(float)

    summary = {
        "schema": "tampa.nps_tier3_persistent_cover_v1",
        "status": "posthoc_external_ecological_analysis_not_predictive_validation",
        "source": {
            "nps_reference_id": "2316692",
            "years": [int(annual.year.min()), int(annual.year.max())],
            "annual_units": int(len(annual)),
            "nodes": int(annual.node_id.nunique()),
            "consecutive_year_pairs": int(len(tr)),
        },
        "binary_state": {
            "recorded_presence_units": int(annual.recorded_presence.sum()),
            "recorded_nonpresence_units": int((~annual.recorded_presence).sum()),
            "presence_fraction": float(annual.recorded_presence.mean()),
            "interpretation": "Binary recorded presence is saturated in every eligible annual unit."
        },
        "quantitative_state": {
            "frequency_observed_range": [float(annual.focal_frequency.min()), float(annual.focal_frequency.max())],
            "cover_observed_range": [float(annual.focal_mean_cover.min()), float(annual.focal_mean_cover.max())],
            "frequency": freq_overall,
            "cover": cover_overall,
            "location_frequency": freq_locations,
            "location_cover": cover_locations,
        },
        "year_to_year_instability": {
            "median_abs_delta_cover": float(np.median(abs_cover)),
            "q75_abs_delta_cover": float(np.quantile(abs_cover, 0.75)),
            "q90_abs_delta_cover": float(np.quantile(abs_cover, 0.90)),
            "median_abs_delta_frequency": float(np.median(abs_freq)),
            "q75_abs_delta_frequency": float(np.quantile(abs_freq, 0.75)),
            "q90_abs_delta_frequency": float(np.quantile(abs_freq, 0.90)),
        },
        "interpretation": (
            "This external NPS panel cannot validate next-year recorded loss because recorded Zostera presence never disappears "
            "from eligible annual transect units. It can, however, test the separate state-decoupling proposition: a saturated "
            "binary presence state can coexist with substantial quantitative cover/frequency dynamics. Trend direction is "
            "reported at pooled and location-specific within-transect scales and must not be interpreted as demographic loss."
        ),
        "claim_boundary": [
            "Post-hoc because the response was already opened by the frozen NPS v2 estimability test.",
            "Not counted as independent predictive confirmation of the Tampa early-warning endpoint.",
            "Recorded presence refers to observation in re-observed seagrass-bearing quadrats, not total meadow occupancy.",
            "Cover/frequency trends are observational; no nutrient or climate cause is identified.",
            "Location-specific slopes are descriptive external ecological replication and not a universal NPS-wide decline claim."
        ],
    }

    annual.to_csv(outdir / "nps_tier3_annual_state.csv", index=False)
    tr.to_csv(outdir / "nps_tier3_consecutive_changes.csv", index=False)
    cover_nodes.to_csv(outdir / "nps_tier3_cover_node_slopes.csv", index=False)
    freq_nodes.to_csv(outdir / "nps_tier3_frequency_node_slopes.csv", index=False)
    (outdir / "nps_persistent_cover_v1.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("results/generated_nps_posthoc"))
    args = p.parse_args()
    main(args.out)
