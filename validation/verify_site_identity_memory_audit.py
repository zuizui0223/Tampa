#!/usr/bin/env python3
"""Verify the canonical site-identity audit summary against a fresh rerun."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

NAME_MAP = {
    "binary_detected": "binary_detected",
    "frequency": "focal_frequency",
    "cover_index": "cover_index",
}


def close(a, b, tol=1e-4):
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def main(generated: Path, canonical: Path) -> None:
    g = json.loads(generated.read_text())
    c = json.loads(canonical.read_text())

    assert g["status"] == "stable_site_reference_absorbs_older_history"
    assert g["primary_proxy_pattern_passed"] is True
    assert close(g["primary_tau_years"], c["primary_tau_years"])

    expected_counts = c["full_grid"]
    for gname, cname in NAME_MAP.items():
        gr = g["results"][gname]
        cr = c[cname]
        for ref, count_key in [
            ("without_node_id", "supported_tau_counts_without_node"),
            ("with_node_id", "supported_tau_counts_with_node"),
        ]:
            assert gr[ref]["grid_support_count"] == expected_counts[count_key][cname]
            gp = gr[ref]["primary_tau10"]
            cp = cr[ref]
            assert gp["support_rule_passed"] == cp["supported"]
            assert gp["history_wins"] == cp["history_wins"]
            assert close(gp["signflip_p"], cp["signflip_p"], tol=0.005)
            if gname == "binary_detected":
                assert close(gp["lag1_mean_score"], cp["lag1_log_loss"])
                assert close(gp["history_mean_score"], cp["history_log_loss"])
            else:
                assert close(gp["lag1_mean_score"], cp["lag1_mae"])
                assert close(gp["history_mean_score"], cp["history_mae"])

    print("site-identity memory audit canonical summary: OK")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--generated",
        type=Path,
        default=Path("results/generated_site_identity/tampa_site_identity_memory_audit_v1.json"),
    )
    p.add_argument(
        "--canonical",
        type=Path,
        default=Path("results/site_identity_memory_audit_v1.json"),
    )
    a = p.parse_args()
    main(a.generated, a.canonical)
