#!/usr/bin/env python3
"""Once-only Texas seagrass external early-warning validation v2.

The scientific contract is frozen before this runner is authorized. Each yearly ZIP
is accessed only for the predeclared QuadratPercentCover member using exact HTTP Range
requests. No other archive member is decompressed or parsed.
"""
from __future__ import annotations

import binascii
import csv
import io
import json
import math
import re
import struct
import zlib
import zipfile
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
CONTRACT = json.loads((ROOT / "final_outcome_contract.json").read_text())
AUTH = ROOT / "OUTCOME_AUTHORIZED_ONCE"
OUT = ROOT / "terminal_outcome_result.json"

class TerminalStop(RuntimeError):
    pass

AUDIT = {
    "archive_full_downloads": 0,
    "selected_entry_local_header_requests": 0,
    "selected_entry_payload_requests": 0,
    "selected_entry_compressed_bytes_opened": 0,
    "selected_entry_uncompressed_bytes_parsed": 0,
    "unselected_entry_payload_requests": 0,
    "model_fits": 0,
    "predictive_scores": 0,
}

def norm_header(x):
    s = "" if x is None else str(x).strip().lower()
    s = s.replace("%", " percent ")
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")

def canon_id(x):
    if x is None:
        return ""
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, (float, np.floating)) and math.isfinite(float(x)):
        y = float(x)
        if y.is_integer():
            return str(int(y))
        return ("%.12g" % y).strip()
    return re.sub(r"\s+", " ", str(x).strip())

def alias_match(label, alias):
    return label == alias or label.startswith(alias + "_") or label.endswith("_" + alias)

def one_by_priority(headers, groups, required=True):
    for group in groups:
        idx = [i for i,h in enumerate(headers) if any(alias_match(h,a) for a in group)]
        if len(idx) == 1:
            return idx[0]
        if len(idx) > 1:
            raise TerminalStop(f"ambiguous_header_alias:{group}:{[headers[i] for i in idx]}")
    if required:
        raise TerminalStop(f"required_header_not_found:{groups}")
    return None

def optional_one(headers, aliases):
    idx = [i for i,h in enumerate(headers) if any(alias_match(h,a) for a in aliases)]
    if len(idx) == 1:
        return idx[0]
    return None

def resolve_header(values):
    H = [norm_header(x) for x in values]
    station_groups = [CONTRACT["parser"]["station_alias_priority"][0],
                      CONTRACT["parser"]["station_alias_priority"][1]]
    station = one_by_priority(H, station_groups, True)
    quadrat = one_by_priority(H, [CONTRACT["parser"]["quadrat_aliases"]], True)
    region = optional_one(H, CONTRACT["parser"]["region_aliases"])

    focal_wide = [i for i,h in enumerate(H) if "thalassia" in h]
    if len(focal_wide) == 1:
        return {
            "layout": "wide_species_columns",
            "station": station,
            "quadrat": quadrat,
            "region": region,
            "focal_cover": focal_wide[0],
            "headers": H,
        }
    if len(focal_wide) > 1:
        raise TerminalStop(f"multiple_thalassia_columns:{[H[i] for i in focal_wide]}")

    species = optional_one(H, CONTRACT["parser"]["long_species_aliases"])
    cover = optional_one(H, CONTRACT["parser"]["long_cover_aliases"])
    if species is not None and cover is not None:
        return {
            "layout": "long_species_cover",
            "station": station,
            "quadrat": quadrat,
            "region": region,
            "species": species,
            "cover": cover,
            "headers": H,
        }
    raise TerminalStop("no_unambiguous_focal_cover_layout")

def combine_header_rows(a, b):
    n = max(len(a), len(b))
    out = []
    for i in range(n):
        x = "" if i >= len(a) or a[i] is None else str(a[i]).strip()
        y = "" if i >= len(b) or b[i] is None else str(b[i]).strip()
        if x and y and norm_header(x) != norm_header(y):
            out.append(x + " " + y)
        else:
            out.append(y or x)
    return out

def find_header(rows):
    maxr = min(int(CONTRACT["parser"]["header_search_max_rows"]), len(rows))
    found = []
    for r in range(maxr):
        candidates = [(1, list(rows[r]))]
        if r + 1 < maxr:
            candidates.append((2, combine_header_rows(list(rows[r]), list(rows[r+1]))))
        for depth, vals in candidates:
            try:
                mapping = resolve_header(vals)
            except TerminalStop:
                continue
            found.append((r, depth, mapping))
    if not found:
        raise TerminalStop("no_valid_header_mapping_first_25_rows")
    # First mapping in row order, preferring a single-row header over a two-row
    # header at the same row. If the same earliest row/depth produces >1 mapping
    # that cannot occur because resolve_header is deterministic.
    found.sort(key=lambda x: (x[0], x[1]))
    first = found[0]
    # A later alternative with a different semantic layout is treated as ambiguity
    # only if it starts on the same earliest row.
    same = [x for x in found if x[0] == first[0] and x[1] == first[1]]
    if len(same) != 1:
        raise TerminalStop("ambiguous_earliest_header_mapping")
    return first

def range_get(spec, start, end):
    req = Request(
        spec["url"],
        headers={
            "Range": f"bytes={start}-{end}",
            "Accept-Encoding": "identity",
            "User-Agent": "Tampa-Texas-EarlyWarning-v2/1.0",
        },
    )
    with urlopen(req, timeout=60) as r:
        if r.status != 206:
            raise TerminalStop(f"range_http_{r.status}:{spec['year']}:{start}-{end}")
        expected = f"bytes {start}-{end}/{spec['archive_size']}"
        if str(r.headers.get("Content-Range", "")) != expected:
            raise TerminalStop(f"content_range_drift:{spec['year']}")
        etag = str(r.headers.get("ETag", ""))
        if spec.get("etag") and etag and etag != spec["etag"]:
            raise TerminalStop(f"etag_drift:{spec['year']}:{etag}")
        b = r.read(end - start + 2)
    if len(b) != end - start + 1:
        raise TerminalStop(f"range_length_drift:{spec['year']}")
    return b

def fetch_selected_entry(spec):
    off = int(spec["offset"])
    h = range_get(spec, off, off + 29)
    AUDIT["selected_entry_local_header_requests"] += 1
    if h[:4] != b"PK\x03\x04":
        raise TerminalStop(f"local_header_signature:{spec['year']}")
    method = struct.unpack_from("<H", h, 8)[0]
    fnlen = struct.unpack_from("<H", h, 26)[0]
    xlen = struct.unpack_from("<H", h, 28)[0]
    if method != int(spec["method"]):
        raise TerminalStop(f"compression_method_drift:{spec['year']}")
    extra = b""
    if fnlen + xlen:
        extra = range_get(spec, off + 30, off + 30 + fnlen + xlen - 1)
        AUDIT["selected_entry_local_header_requests"] += 1
    name = extra[:fnlen].decode("utf-8")
    if name != spec["entry"]:
        raise TerminalStop(f"entry_name_drift:{spec['year']}:{name}")
    start = off + 30 + fnlen + xlen
    end = start + int(spec["csize"]) - 1
    raw = range_get(spec, start, end)
    AUDIT["selected_entry_payload_requests"] += 1
    AUDIT["selected_entry_compressed_bytes_opened"] += len(raw)
    if method == 0:
        data = raw
    elif method == 8:
        try:
            data = zlib.decompress(raw, -15)
        except zlib.error as exc:
            raise TerminalStop(f"deflate_failure:{spec['year']}") from exc
    else:
        raise TerminalStop(f"unsupported_compression:{spec['year']}:{method}")
    if len(data) != int(spec["usize"]):
        raise TerminalStop(f"uncompressed_size_drift:{spec['year']}")
    if f"{binascii.crc32(data)&0xffffffff:08x}" != spec["crc32"]:
        raise TerminalStop(f"crc_drift:{spec['year']}")
    AUDIT["selected_entry_uncompressed_bytes_parsed"] += len(data)
    return data

def rows_from_csv(data):
    try:
        text = data.decode(CONTRACT["parser"]["csv_encoding"])
    except UnicodeDecodeError as exc:
        raise TerminalStop("csv_encoding_failure") from exc
    return [row for row in csv.reader(io.StringIO(text, newline=""))]

def rows_from_xlsx(data):
    try:
        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception as exc:
        raise TerminalStop("xlsx_open_failure") from exc
    candidates = []
    for ws in wb.worksheets:
        rows = [list(row) for row in ws.iter_rows(values_only=True)]
        if not rows:
            continue
        try:
            hr, depth, mapping = find_header(rows)
        except TerminalStop:
            continue
        candidates.append((ws.title, hr, depth, mapping, rows))
    if len(candidates) != 1:
        raise TerminalStop(f"xlsx_valid_sheet_count:{len(candidates)}")
    return candidates[0]

def parse_cover(value, year, rowno):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        v = float(str(value).strip())
    except Exception as exc:
        raise TerminalStop(f"nonnumeric_focal_cover:{year}:row{rowno}:{value!r}") from exc
    if not math.isfinite(v):
        raise TerminalStop(f"nonfinite_focal_cover:{year}:row{rowno}")
    if v == float(CONTRACT["response_semantics"]["missing_sentinel"]):
        return None
    lo, hi = CONTRACT["response_semantics"]["valid_cover_range"]
    if not (float(lo) <= v <= float(hi)):
        raise TerminalStop(f"focal_cover_out_of_range:{year}:row{rowno}:{v}")
    return float(v)

def focal_long_match(x):
    s = re.sub(r"\s+", " ", canon_id(x).lower())
    return s in set(CONTRACT["parser"]["focal_long_values"])

def parse_year(spec, data):
    if spec["format"] == "csv":
        rows = rows_from_csv(data)
        hr, depth, mapping = find_header(rows)
        sheet = "__CSV__"
    else:
        sheet, hr, depth, mapping, rows = rows_from_xlsx(data)
    start = hr + depth
    seen = {}
    station_regions = defaultdict(set)
    physical_data_rows = 0
    focal_rows = 0
    for idx in range(start, len(rows)):
        row = list(rows[idx])
        if not any(v is not None and str(v).strip() for v in row):
            continue
        physical_data_rows += 1
        need = max(v for k,v in mapping.items() if k not in {"layout","headers","region"} and isinstance(v,int))
        if len(row) <= need:
            raise TerminalStop(f"short_row:{spec['year']}:{idx+1}")
        station = canon_id(row[mapping["station"]])
        quad = canon_id(row[mapping["quadrat"]])
        if not station or not quad:
            raise TerminalStop(f"blank_station_or_quadrat:{spec['year']}:{idx+1}")
        region = "__UNKNOWN__"
        if mapping.get("region") is not None and mapping["region"] < len(row):
            r = canon_id(row[mapping["region"]])
            if r:
                region = r
        node = f"{region}::{station}" if region != "__UNKNOWN__" else station
        station_regions[node].add(region)

        cover = None
        if mapping["layout"] == "wide_species_columns":
            if mapping["focal_cover"] >= len(row):
                raise TerminalStop(f"missing_focal_column_cell:{spec['year']}:{idx+1}")
            cover = parse_cover(row[mapping["focal_cover"]], spec["year"], idx+1)
            focal_rows += 1
        else:
            if mapping["species"] >= len(row) or mapping["cover"] >= len(row):
                raise TerminalStop(f"long_row_missing_cells:{spec['year']}:{idx+1}")
            if not focal_long_match(row[mapping["species"]]):
                continue
            cover = parse_cover(row[mapping["cover"]], spec["year"], idx+1)
            focal_rows += 1

        key = (node, quad)
        if key in seen and cover is not None and seen[key] is not None:
            raise TerminalStop(f"duplicate_valid_focal_station_quadrat:{spec['year']}:{node}:{quad}")
        if key not in seen or (seen[key] is None and cover is not None):
            seen[key] = cover

    bynode = defaultdict(list)
    for (node, quad), cover in seen.items():
        if cover is not None:
            bynode[node].append((quad, cover))
    annual = []
    minq = int(CONTRACT["parser"]["annual_min_valid_focal_quadrats"])
    for node, vals in bynode.items():
        if len(vals) < minq:
            continue
        covers = np.asarray([v for _,v in vals], dtype=float)
        region = next(iter(station_regions[node])) if station_regions[node] else "__UNKNOWN__"
        annual.append({
            "node_id": node,
            "region": region,
            "year": int(spec["year"]),
            "valid_quadrat_count": int(len(covers)),
            "focal_frequency": float(np.mean(covers > 0.0)),
            "focal_mean_cover": float(np.mean(covers)),
            "recorded_presence": bool(np.any(covers > 0.0)),
            "recorded_zero_cover": bool(np.all(covers == 0.0)),
        })
    audit = {
        "year": int(spec["year"]),
        "entry": spec["entry"],
        "format": spec["format"],
        "sheet": sheet,
        "header_row_1based": int(hr + 1),
        "header_depth": int(depth),
        "layout": mapping["layout"],
        "normalized_headers": mapping["headers"],
        "physical_nonblank_data_rows": int(physical_data_rows),
        "focal_rows_seen": int(focal_rows),
        "eligible_annual_station_years": int(len(annual)),
    }
    return annual, audit

def build_transitions(states):
    by = defaultdict(dict)
    for s in states:
        key = (s["node_id"], int(s["year"]))
        if key in by[s["node_id"]]:
            raise TerminalStop(f"duplicate_annual_state:{key}")
        by[s["node_id"]][int(s["year"])] = s
    out = []
    for node, ys in by.items():
        for y, src in sorted(ys.items()):
            if not src["recorded_presence"]:
                continue
            tgt = ys.get(y + 1)
            if tgt is None:
                continue
            if tgt["recorded_presence"]:
                loss = 0
            elif tgt["recorded_zero_cover"]:
                loss = 1
            else:
                continue
            out.append({
                "node_id": node,
                "region": src["region"],
                "source_year": int(y),
                "target_year": int(y+1),
                "log_valid_quadrat_count": float(math.log1p(src["valid_quadrat_count"])),
                "focal_frequency": float(src["focal_frequency"]),
                "focal_mean_cover": float(src["focal_mean_cover"]),
                "recorded_loss": int(loss),
            })
    return pd.DataFrame(out)

def preprocessor(num, cat):
    return ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ])

def make_model(num, cat):
    hp = CONTRACT["model"]["hyperparameters"]
    return Pipeline([
        ("prep", preprocessor(num, cat)),
        ("clf", LogisticRegression(C=float(hp["C"]), max_iter=int(hp["max_iter"]), solver=str(hp["solver"]))),
    ])

def count_gate(states, tr):
    eg = CONTRACT["estimability_gate"]
    summary = {
        "annual_station_years": int(len(states)),
        "source_positive_consecutive_transitions": int(len(tr)),
        "recorded_losses": int(tr["recorded_loss"].sum()) if len(tr) else 0,
        "recorded_persistence": int((1-tr["recorded_loss"]).sum()) if len(tr) else 0,
    }
    checks = [
        summary["annual_station_years"] >= int(eg["minimum_annual_station_years"]),
        summary["source_positive_consecutive_transitions"] >= int(eg["minimum_source_positive_consecutive_transitions"]),
        summary["recorded_losses"] >= int(eg["minimum_recorded_losses"]),
        summary["recorded_persistence"] >= int(eg["minimum_recorded_persistence"]),
    ]
    years = []
    for y in sorted(tr["target_year"].unique()) if len(tr) else []:
        train = tr[tr.target_year < y]
        if int(train.recorded_loss.sum()) >= int(eg["per_target_year_training_min_prior_losses"]) and int((1-train.recorded_loss).sum()) >= int(eg["per_target_year_training_min_prior_persistence"]):
            years.append(int(y))
    summary["prospectively_scorable_target_years"] = years
    summary["prospectively_scorable_target_year_count"] = len(years)
    checks.append(len(years) >= int(eg["minimum_scored_target_years"]))
    summary["passed"] = bool(all(checks))
    return summary

def fit_and_score(tr, years):
    base_num = CONTRACT["model"]["baseline_numeric"]
    cat = CONTRACT["model"]["baseline_categorical"]
    aug_num = base_num + CONTRACT["model"]["augmentation"]
    scores = []
    pooled_y=[]; pooled_b=[]; pooled_a=[]
    for y in years:
        train = tr[tr.target_year < y].copy()
        test = tr[tr.target_year == y].copy()
        if test.empty:
            raise TerminalStop(f"empty_test_year:{y}")
        mb = make_model(base_num, cat)
        ma = make_model(aug_num, cat)
        mb.fit(train[base_num+cat], train.recorded_loss)
        AUDIT["model_fits"] += 1
        ma.fit(train[aug_num+cat], train.recorded_loss)
        AUDIT["model_fits"] += 1
        pb = np.clip(mb.predict_proba(test[base_num+cat])[:,1], CONTRACT["scoring"]["probability_clip"], 1-CONTRACT["scoring"]["probability_clip"])
        pa = np.clip(ma.predict_proba(test[aug_num+cat])[:,1], CONTRACT["scoring"]["probability_clip"], 1-CONTRACT["scoring"]["probability_clip"])
        yv = test.recorded_loss.to_numpy(dtype=int)
        lb = float(log_loss(yv,pb,labels=[0,1]))
        la = float(log_loss(yv,pa,labels=[0,1]))
        AUDIT["predictive_scores"] += 2
        scores.append({
            "target_year":int(y),"n":int(len(test)),"losses":int(yv.sum()),"persistence":int(len(yv)-yv.sum()),
            "baseline_log_loss":lb,"augmented_log_loss":la,"augmented_minus_baseline":la-lb,
            "winner":"augmented" if la<lb else ("baseline" if lb<la else "tie")
        })
        pooled_y.extend(yv.tolist()); pooled_b.extend(pb.tolist()); pooled_a.extend(pa.tolist())
    bmacro=float(np.mean([x["baseline_log_loss"] for x in scores]))
    amacro=float(np.mean([x["augmented_log_loss"] for x in scores]))
    aw=sum(x["winner"]=="augmented" for x in scores)
    bw=sum(x["winner"]=="baseline" for x in scores)
    threshold=math.ceil(0.60*len(scores))
    if amacro < bmacro and aw >= threshold:
        status="favorable_external_early_warning"
    elif bmacro < amacro and bw >= threshold:
        status="adverse_external_early_warning"
    else:
        status="no_confirmed_external_early_warning"
    sec = {
        "pooled_baseline_brier":float(brier_score_loss(pooled_y,pooled_b)),
        "pooled_augmented_brier":float(brier_score_loss(pooled_y,pooled_a)),
    }
    if len(set(pooled_y))==2:
        sec["pooled_baseline_auc"]=float(roc_auc_score(pooled_y,pooled_b))
        sec["pooled_augmented_auc"]=float(roc_auc_score(pooled_y,pooled_a))
    return {
        "status":status,"baseline_macro_log_loss":bmacro,"augmented_macro_log_loss":amacro,
        "augmented_minus_baseline":amacro-bmacro,"augmented_year_wins":aw,"baseline_year_wins":bw,
        "tie_years":len(scores)-aw-bw,"required_win_count":threshold,"year_scores":scores,"secondary":sec
    }

def write_terminal(status, reason=None, extra=None):
    out = {
        "schema":"tampa.texas_seagrass_external_early_warning_v2.terminal_outcome_result",
        "attempt_id":CONTRACT["attempt_id"],
        "terminal_status":status,
        "reason":reason,
        "response_access_audit":dict(AUDIT),
        "counts_as_external_predictive_evidence": status in {
            "favorable_external_early_warning","adverse_external_early_warning","no_confirmed_external_early_warning"
        },
    }
    if extra:
        out.update(extra)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

def main():
    if not AUTH.exists():
        raise RuntimeError("OUTCOME_AUTHORIZED_ONCE marker missing")
    marker = json.loads(AUTH.read_text())
    if marker.get("attempt_id") != CONTRACT["attempt_id"] or marker.get("authorized") is not True:
        raise RuntimeError("authorization marker mismatch")
    try:
        states=[]; parser_audit=[]
        for spec in CONTRACT["source"]["selected_cover_entries"]:
            data=fetch_selected_entry(spec)
            annual,audit=parse_year(spec,data)
            states.extend(annual); parser_audit.append(audit)
        if AUDIT["selected_entry_payload_requests"] != int(CONTRACT["one_shot_access"]["selected_entry_payload_count"]):
            raise TerminalStop("selected_entry_payload_count_drift")
        tr=build_transitions(states)
        cg=count_gate(states,tr)
        if not cg["passed"]:
            write_terminal(
                CONTRACT["estimability_gate"]["failure_status"],
                "frozen_estimability_gate_failed",
                {"parser_audit":parser_audit,"estimability":cg}
            )
            return
        result=fit_and_score(tr,cg["prospectively_scorable_target_years"])
        write_terminal(
            result["status"],
            None,
            {
                "parser_audit":parser_audit,
                "estimability":cg,
                "primary_result":result,
                "annual_state_summary":{
                    "annual_station_years":len(states),
                    "recorded_present_station_years":sum(bool(x["recorded_presence"]) for x in states),
                    "recorded_zero_cover_station_years":sum(bool(x["recorded_zero_cover"]) for x in states),
                    "nodes":len(set(x["node_id"] for x in states)),
                    "years":sorted(set(int(x["year"]) for x in states)),
                },
                "scientific_interpretation":{
                    "endpoint":"next-year explicitly recorded zero-cover state",
                    "favorable_meaning":"source-year Thalassia quadrat frequency and mean percent cover add independent out-of-time information beyond station identity, year and effort in this Texas monitoring system",
                    "adverse_meaning":"the frozen quantitative state does not generalize as a useful complement in this Texas monitoring system",
                    "boundary":"recorded cover-state instability is not demographic extinction; the external result does not identify a causal stress mechanism"
                }
            }
        )
    except TerminalStop as exc:
        write_terminal("terminal_protocol_or_schema_stop",str(exc),{"counts_as_external_predictive_evidence":False})
    except Exception as exc:
        write_terminal("terminal_execution_stop",f"{type(exc).__name__}:{exc}",{"counts_as_external_predictive_evidence":False})

if __name__=="__main__":
    main()
