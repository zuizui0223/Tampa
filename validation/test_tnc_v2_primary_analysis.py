#!/usr/bin/env python3
"""Synthetic checks for the frozen four-bay TNC v2 primary analysis."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"analysis/64_tnc_v2_primary_analysis.py"

spec=importlib.util.spec_from_file_location("tnc_primary",SCRIPT)
m=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

# Keep CI fast while testing the same stratified-bootstrap implementation.
m.BOOTSTRAP_REPS=1200
m.BOOTSTRAP_SEED=20261003

def make(effect:float,n_by_bay=(10,10,10,10)):
    rows=[]; fut=[]
    k=0
    for bay,n in zip(m.BAYS,n_by_bay):
        for i in range(n):
            k+=1
            tnc=80 + 2.5*i + 4*m.BAYS.index(bay)
            base=0.25 + 0.025*((i+2*m.BAYS.index(bay))%10)
            bb=0.5 + 0.2*((i+1)%5)
            rows.append({
                "node_id":f"N{k:03d}","water_body":bay,
                "baseline_frequency":base,
                "baseline_braun_blanquet":bb,
                "rhizome_tnc_mg_g":tnc,
            })
    b=pd.DataFrame(rows)
    z=(b["rhizome_tnc_mg_g"]-b["rhizome_tnc_mg_g"].mean())/b["rhizome_tnc_mg_g"].std(ddof=1)
    # Deterministic small noise orthogonal enough to avoid a perfect fit.
    noise=np.array([0.004*np.sin(i*1.7) for i in range(len(b))])
    delta=effect*z.to_numpy()+noise
    for node,y0,d in zip(b["node_id"],b["baseline_frequency"],delta):
        fut.append({"node_id":node,"future_frequency":float(y0+d)})
    return b,pd.DataFrame(fut)

# Positive-direction case.
b,f=make(0.06)
x,_,_=m.prepare(b,f)
assert len(x)==40
assert m.fit_tnc_coef(x)>0
boot=m.bootstrap_ci(x)
assert boot["ci95"][0]>0, boot

# Opposite-direction case.
b,f=make(-0.06)
x,_,_=m.prepare(b,f)
boot=m.bootstrap_ci(x)
assert boot["ci95"][1]<0, boot

# Replication gate logic: five Boca Ciega nodes is below the frozen six-per-bay floor.
b,f=make(0.06,(10,10,10,5))
x,_,_=m.prepare(b,f)
counts={bay:int((x["water_body"]==bay).sum()) for bay in m.BAYS}
confirmatory=(len(x)>=m.MIN_TOTAL and all(counts[bay]>=m.MIN_PER_BAY for bay in m.BAYS))
assert confirmatory is False
assert counts["Boca Ciega Bay"]==5

print("Tampa TNC v2 frozen primary analysis synthetic checks: OK")
