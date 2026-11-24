"""Descriptive audit of published flower-visitor specimens, no inferential claims."""
import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/seagrass_interactions_v1/flower_visitor_peracarid_2012.csv"
EXPECTED = {"Mysida": (1, 8), "Amphipoda": (8, 56), "Isopoda": (11, 17),
            "Cumacea": (10, 35), "Tanaidacea": (4, 12)}

def audit(path=SOURCE):
    groups = defaultdict(Counter)
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len({(r["order"], r["source_taxon"]) for r in rows}) == len(rows)
    for r in rows:
        n = int(r["specimens"])
        assert n > 0 and r["diet_bin"] in {"H", "O", "other", "unknown"}
        g = groups[r["order"]]
        g["taxa"] += 1
        g["specimens"] += n
        g[r["diet_bin"]] += n
    assert set(groups) == set(EXPECTED)
    for g, (nt, n) in EXPECTED.items():
        assert (groups[g]["taxa"], groups[g]["specimens"]) == (nt, n)
    totals = sum(groups.values(), Counter())
    assert totals["specimens"] == 128 and totals["taxa"] == 34
    n = totals["specimens"]
    candidate = totals["H"] + totals["O"]
    return {
        "status": "published aggregate descriptive audit; no causal or inferential claim",
        "source": "10.3354/meps10072 Supplement 2 and Table 2",
        "orders": {g: dict(c) for g,c in groups.items()},
        "totals": dict(totals),
        "fraction_all_flower_specimens": n / 312,
        "fraction_crustacean_flower_specimens": n / 252,
        "H_or_O_fraction_all_peracarids": candidate / n,
        "H_or_O_fraction_known_peracarids": candidate / (n - totals["unknown"]),
        "H_or_O_fraction_upper_if_all_unknown_H_or_O": (candidate + totals["unknown"]) / n,
        "largest_taxon_fraction_peracarids": max(int(r["specimens"]) for r in rows) / n,
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
