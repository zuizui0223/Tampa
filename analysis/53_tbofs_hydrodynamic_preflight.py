#!/usr/bin/env python3
"""Response-blind physical preflight for NOAA TBOFS hydrodynamic exposure.

This script deliberately does NOT read any Tampa biological response columns.
It derives the 71 stable transect coordinates from the pinned Event table only,
downloads one pinned TBOFS gridded fields NetCDF, audits ROMS grid/current
metadata, and maps transect coordinates to the nearest valid wet rho cell.

The result is a source-usability gate, not an ecological association test.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

import netCDF4
import numpy as np

EVENT_COMMIT = "6c567beff95ea04f0e397101befb49d5233ace8f"
EVENT_URL = f"https://raw.githubusercontent.com/tbep-tech/obis-example/{EVENT_COMMIT}/dwc/event.csv"
EVENT_SIZE = 24654717
EVENT_BLOB = "583b4d4e328290ab065346579eb4f29f03ea0f99"

DEFAULT_TBOFS_URL = (
    "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nosofs/prod/"
    "tbofs.20260928/tbofs.t06z.20260928.fields.n006.nc"
)

REQUIRED_WATER_BODIES = {"Old Tampa Bay", "Middle Tampa Bay", "Lower Tampa Bay"}


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def download(url: str, timeout: int = 240) -> bytes:
    req = Request(url, headers={"Accept-Encoding": "identity", "User-Agent": "Tampa-TBOFS-preflight/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def stable_nodes_from_event(data: bytes):
    if len(data) != EVENT_SIZE:
        raise RuntimeError(f"event.csv size drift: {len(data)} != {EVENT_SIZE}")
    if git_blob_sha1(data) != EVENT_BLOB:
        raise RuntimeError("event.csv blob drift")

    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    parents = {}
    child_counts = defaultdict(int)
    for row in reader:
        typ = row["eventType"].strip()
        if typ == "Transect":
            parents[row["eventID"].strip()] = {
                "node_id": row["locationID"].strip(),
                "water_body": row["waterBody"].strip(),
                "longitude": float(row["decimalLongitude"]),
                "latitude": float(row["decimalLatitude"]),
            }
        elif typ == "Point":
            child_counts[row["parentEventID"].strip()] += 1

    nodes = {}
    for event_id, p in parents.items():
        if child_counts.get(event_id, 0) < 3:
            continue
        node = p["node_id"]
        if node in nodes:
            old = nodes[node]
            if not (
                old["water_body"] == p["water_body"]
                and abs(old["longitude"] - p["longitude"]) < 1e-9
                and abs(old["latitude"] - p["latitude"]) < 1e-9
            ):
                raise RuntimeError(f"coordinate drift within stable node {node}")
        else:
            nodes[node] = p

    out = sorted(nodes.values(), key=lambda x: x["node_id"])
    if len(out) != 71:
        raise RuntimeError(f"stable-node registry drift: {len(out)} != 71")
    return out


def attrs(v):
    out = {}
    for k in v.ncattrs():
        val = getattr(v, k)
        if isinstance(val, np.ndarray):
            val = val.tolist()
        elif isinstance(val, np.generic):
            val = val.item()
        try:
            json.dumps(val)
            out[k] = val
        except TypeError:
            out[k] = str(val)
    return out


def find_var(ds, exact=(), attr_needles=()):
    for name in exact:
        if name in ds.variables:
            return name
    for name, v in ds.variables.items():
        text = " ".join(
            str(getattr(v, a, "")) for a in ("standard_name", "long_name", "description")
        ).lower()
        if any(n.lower() in text for n in attr_needles):
            return name
    return None


def find_lonlat_rho(ds):
    exact_pairs = [
        ("lon_rho", "lat_rho"),
        ("longitude", "latitude"),
        ("lon", "lat"),
    ]
    for lon_name, lat_name in exact_pairs:
        if lon_name in ds.variables and lat_name in ds.variables:
            lon = np.asarray(ds.variables[lon_name][:]).squeeze()
            lat = np.asarray(ds.variables[lat_name][:]).squeeze()
            if lon.shape == lat.shape and lon.ndim == 2:
                return lon_name, lat_name, lon, lat
    raise RuntimeError("No matching 2-D rho/grid longitude-latitude pair found")


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1 = np.deg2rad(lat1)
    p2 = np.deg2rad(lat2)
    dp = p2 - p1
    dl = np.deg2rad(lon2 - lon1)
    a = np.sin(dp / 2.0) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0) ** 2
    return 2.0 * r * np.arcsin(np.minimum(1.0, np.sqrt(a)))


def finite_array(v):
    a = np.ma.asarray(v[:])
    if np.ma.isMaskedArray(a):
        return np.asarray(a.filled(np.nan), dtype=float)
    return np.asarray(a, dtype=float)


def pick_wet_mask(ds, grid_shape):
    if "mask_rho" in ds.variables:
        m = finite_array(ds.variables["mask_rho"]).squeeze()
        if m.shape == grid_shape:
            return "mask_rho", np.isfinite(m) & (m > 0.5)

    if "h" in ds.variables:
        h = finite_array(ds.variables["h"]).squeeze()
        if h.shape == grid_shape:
            return "h_finite_positive", np.isfinite(h) & (h > 0)

    return "lonlat_finite_only", None


def current_candidates(ds):
    east = find_var(
        ds,
        exact=("u", "water_u", "u_velocity", "eastward_velocity"),
        attr_needles=("eastward sea water velocity", "eastward current", "u-momentum", "u velocity"),
    )
    north = find_var(
        ds,
        exact=("v", "water_v", "v_velocity", "northward_velocity"),
        attr_needles=("northward sea water velocity", "northward current", "v-momentum", "v velocity"),
    )
    return east, north


def vertical_audit(ds, u_name, v_name):
    dims = set()
    for name in (u_name, v_name):
        if name:
            dims.update(ds.variables[name].dimensions)

    candidates = []
    for d in dims:
        if d in ds.variables:
            v = ds.variables[d]
            arr = finite_array(v).squeeze()
            if arr.ndim == 1 and 2 <= arr.size <= 100:
                at = attrs(v)
                text = " ".join([d, str(at.get("standard_name", "")), str(at.get("long_name", ""))]).lower()
                if "s_" in d.lower() or "sigma" in text or "vertical" in text:
                    candidates.append((d, arr, at))

    if not candidates and "s_rho" in ds.variables:
        v = ds.variables["s_rho"]
        candidates.append(("s_rho", finite_array(v).squeeze(), attrs(v)))

    if not candidates:
        return {
            "supported": False,
            "reason": "no explicit current vertical coordinate found",
        }

    d, arr, at = candidates[0]
    vals = np.asarray(arr, dtype=float)
    finite = vals[np.isfinite(vals)]
    if finite.size == 0:
        return {"supported": False, "dimension": d, "reason": "vertical coordinate all missing"}

    bottom_index = int(np.nanargmin(vals))
    top_index = int(np.nanargmax(vals))
    roms_like = bool(np.nanmin(finite) >= -1.5 and np.nanmax(finite) <= 0.5 and np.nanmin(finite) < np.nanmax(finite))

    return {
        "supported": bool(roms_like and finite.size == 11),
        "dimension": d,
        "size": int(finite.size),
        "min": float(np.nanmin(finite)),
        "max": float(np.nanmax(finite)),
        "bottom_index_by_most_negative_sigma": bottom_index,
        "surface_index_by_least_negative_sigma": top_index,
        "roms_sigma_like": roms_like,
        "attributes": at,
        "interpretation": (
            "Near-bed layer reproducibly defined as the most-negative ROMS-like sigma coordinate."
            if roms_like
            else "Vertical coordinate is not safely interpretable as ROMS-like sigma."
        ),
    }


def main(tbofs_url: str, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)

    event = download(EVENT_URL)
    nodes = stable_nodes_from_event(event)

    tbofs_bytes = download(tbofs_url)
    nc_path = outdir / "tbofs_preflight_source.nc"
    nc_path.write_bytes(tbofs_bytes)
    file_sha256 = hashlib.sha256(tbofs_bytes).hexdigest()

    ds = netCDF4.Dataset(nc_path, "r")
    try:
        lon_name, lat_name, lon, lat = find_lonlat_rho(ds)
        mask_rule, mask = pick_wet_mask(ds, lon.shape)
        if mask is None:
            mask = np.isfinite(lon) & np.isfinite(lat)
        else:
            mask = mask & np.isfinite(lon) & np.isfinite(lat)

        wet_lat = lat[mask]
        wet_lon = lon[mask]
        wet_flat_indices = np.flatnonzero(mask.ravel())
        if wet_lat.size == 0:
            raise RuntimeError("No valid wet cells under frozen rule")

        mappings = []
        for p in nodes:
            d = haversine_km(p["latitude"], p["longitude"], wet_lat, wet_lon)
            j = int(np.nanargmin(d))
            flat = int(wet_flat_indices[j])
            iy, ix = np.unravel_index(flat, lon.shape)
            mappings.append({
                **p,
                "grid_y": int(iy),
                "grid_x": int(ix),
                "grid_longitude": float(lon[iy, ix]),
                "grid_latitude": float(lat[iy, ix]),
                "distance_km": float(d[j]),
            })

        east, north = current_candidates(ds)
        vertical = vertical_audit(ds, east, north)

        distances = np.array([x["distance_km"] for x in mappings], dtype=float)
        wb = Counter(x["water_body"] for x in mappings)
        mapped_required = REQUIRED_WATER_BODIES.issubset(wb)

        spatial_gate = bool(
            len(mappings) >= 30
            and mapped_required
            and float(np.median(distances)) <= 1.0
            and float(np.max(distances)) <= 2.0
        )
        gate_pass = bool(spatial_gate and vertical.get("supported", False) and east and north)

        variable_inventory = {}
        for name, v in ds.variables.items():
            if name in {lon_name, lat_name, "mask_rho", "h", east, north, vertical.get("dimension")}:
                variable_inventory[name] = {
                    "dimensions": list(v.dimensions),
                    "shape": list(v.shape),
                    "dtype": str(v.dtype),
                    "attributes": attrs(v),
                }

        summary = {
            "schema": "tampa.tbofs_hydrodynamic_preflight_v1",
            "status": "gate_pass" if gate_pass else "gate_fail",
            "response_blind": True,
            "biological_response_columns_read": [],
            "source": {
                "tbofs_url": tbofs_url,
                "download_bytes": len(tbofs_bytes),
                "sha256": file_sha256,
                "event_commit": EVENT_COMMIT,
                "event_blob": EVENT_BLOB,
            },
            "grid": {
                "longitude_variable": lon_name,
                "latitude_variable": lat_name,
                "shape": list(lon.shape),
                "wet_cell_rule": mask_rule,
                "wet_cells": int(mask.sum()),
            },
            "currents": {
                "eastward_candidate": east,
                "northward_candidate": north,
                "vertical": vertical,
            },
            "mapping": {
                "stable_nodes": len(mappings),
                "water_body_counts": dict(sorted(wb.items())),
                "required_water_bodies_present": mapped_required,
                "distance_km": {
                    "min": float(np.min(distances)),
                    "median": float(np.median(distances)),
                    "p90": float(np.quantile(distances, 0.90)),
                    "max": float(np.max(distances)),
                    "n_gt_1km": int(np.sum(distances > 1.0)),
                    "n_gt_2km": int(np.sum(distances > 2.0)),
                },
            },
            "gate": {
                "minimum_valid_nodes": 30,
                "required_water_bodies": sorted(REQUIRED_WATER_BODIES),
                "maximum_median_mapping_distance_km": 1.0,
                "maximum_primary_node_mapping_distance_km": 2.0,
                "spatial_gate_pass": spatial_gate,
                "vertical_gate_pass": bool(vertical.get("supported", False)),
                "current_pair_identified": bool(east and north),
                "overall_pass": gate_pass,
            },
            "audited_variables": variable_inventory,
            "claim_boundary": [
                "This is a physical-source usability gate only.",
                "No seagrass response was used to choose grid cell, vertical layer, or current variables.",
                "Passing does not establish an ecological hydrodynamic effect.",
            ],
        }

        with (outdir / "tbofs_hydrodynamic_preflight_v1.json").open("w") as f:
            json.dump(summary, f, indent=2, sort_keys=True)

        fieldnames = [
            "node_id", "water_body", "longitude", "latitude",
            "grid_y", "grid_x", "grid_longitude", "grid_latitude", "distance_km",
        ]
        with (outdir / "tbofs_node_mapping_coordinates_only.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(mappings)

        print(json.dumps(summary, indent=2, sort_keys=True))

    finally:
        ds.close()
        nc_path.unlink(missing_ok=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tbofs-url", default=DEFAULT_TBOFS_URL)
    ap.add_argument("--out", type=Path, default=Path("results/generated_tbofs_preflight"))
    args = ap.parse_args()
    main(args.tbofs_url, args.out)
