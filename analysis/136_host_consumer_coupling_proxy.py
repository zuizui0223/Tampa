"""Exploratory local host–consumer coupling; reproduce archived-pair calculations."""
import csv, json
from pathlib import Path
from math import isfinite

ROOT = Path(__file__).resolve().parents[1]
X = ["shoots_dlog1p", "above_dlog1p", "below_dlog1p"]
Y = ["mesograzer_count_unstandardized_dlog1p", "mesograzer_abundance_dlog1p", "mesograzer_richness_dlog1p"]

def fit(rows, x, y):
    den = sum(r[x] ** 2 for r in rows)
    if den == 0:
        raise ValueError("zero predictor variation")
    return sum(r[x] * r[y] for r in rows) / den

def analyze():
    with open(ROOT / "data/seagrass_interactions_v1/zen2_2014_pair_contrasts_reproductive_proxy.csv", newline="") as f:
        rows = [{k: (v if k == "region_code" else float(v)) for k,v in r.items()} for r in csv.DictReader(f)]
    assert len(rows) == len({r["region_code"] for r in rows}) == 25
    state = 712069
    def rand():
        nonlocal state
        state = (1664525 * state + 1013904223) % 2**32
        return state / 2**32
    out = []
    for x in X:
        for y in Y:
            rs = [r for r in rows if isfinite(r[x]) and isfinite(r[y])]
            n = len(rs)
            b = fit(rs,x,y)
            boot = sorted(fit([rs[int(rand()*n)] for _ in range(n)],x,y) for _ in range(20000))
            loo = [fit(rs[:i]+rs[i+1:],x,y) for i in range(n)]
            sse = sum((a[y]-loo[i]*a[x])**2 for i,a in enumerate(rs))
            sse0 = sum(a[y]**2 for a in rs)
            sse1 = sum((a[y]-a[x])**2 for a in rs)
            out.append(dict(x=x,y=y,n=n,b=b,ci=[boot[500],boot[19499]],
                loo=[min(loo),max(loo)],skill=1-sse/sse0,proportional_skill=1-sse1/sse0,
                sign_agreement=sum(a[x]*a[y]>0 for a in rs)))
    return out

if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2))
