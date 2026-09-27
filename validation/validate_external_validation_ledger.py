#!/usr/bin/env python3
"""Validate the frozen Tampa external-validation closure ledger."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "validation" / "external_validation_ledger_v1.json"


def main() -> None:
    x = json.loads(LEDGER.read_text())
    assert x["schema"] == "tampa.external_validation_ledger_v1"

    attempts = x["attempts"]
    d = x["denominator"]

    assert len(attempts) == 10
    assert [a["index"] for a in attempts] == list(range(1, 11))
    assert len({(a["system"], a["version"]) for a in attempts}) == 10
    assert len({a["system"] for a in attempts}) == 5

    assert d["protocol_attempts"] == 10
    assert d["distinct_external_systems"] == 5
    assert d["scored_external_endpoints"] == 0
    assert d["favorable_external_endpoints"] == 0
    assert d["adverse_external_endpoints"] == 0
    assert d["null_or_no_confirmed_external_endpoints"] == 0
    assert d["candidate_hunting_hard_stop"] is True

    for attempt in attempts:
        assert attempt["model_fits"] == 0
        assert attempt["predictive_scores"] == 0
        assert attempt["counts_as_external_predictive_evidence"] is False
        assert attempt["untouched_retry_allowed"] is False
        record = ROOT / attempt["canonical_record"]
        assert record.is_file(), f"missing canonical record: {record}"

    assert x["discovery_hypothesis"]["external_status"] == "unconfirmed"

    readme = (ROOT / "README.md").read_text()
    assert "valid externally scored endpoints: **0**" in readme
    assert "candidate hunting: **hard-stopped**" in readme
    assert "externally unconfirmed" in readme

    spine = (ROOT / "manuscript" / "MANUSCRIPT_SPINE_V1.md").read_text()
    assert "valid externally scored endpoints: **0**" in spine
    assert "Do not add another public external dataset" in spine

    print("Tampa external-validation closure validated: 10 attempts, 5 systems, 0 scored external endpoints, candidate hunting hard-stopped.")


if __name__ == "__main__":
    main()
