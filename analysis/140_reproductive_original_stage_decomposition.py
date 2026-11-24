#!/usr/bin/env python3
"""Post-hoc original-data descriptive stage decomposition and survival bounds.
Run after analysis/138_reproductive_exact_source_members.py.
No causal mediation, no independent study replication; units are site-year and seedling.
"""
import csv, hashlib, io, json, math, statistics as st
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT=Path("reproductive_input")
def read(path,sha):
    raw=(ROOT/path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha: raise ValueError("source member drift: "+path)
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))

def parts(rows):
    # rows are log flower, log ratio, log fruit; identical scale and units.
    means=[st.mean(r[k] for r in rows) for k in range(3)]
    v=sum((r[2]-means[2])**2 for r in rows)
    if v<=0: raise ValueError("no log-fruit variability")
    return [sum((r[k]-means[k])*(r[2]-means[2]) for r in rows)/v for k in (0,1)]

def center(records):
    by=defaultdict(list)
    for r in records:by[r["location"]].append(r["log_values"])
    return [tuple(v[k]-st.mean(x[k] for x in group) for k in range(3))
            for group in by.values() for v in group]

def kendrick():
    f=read("kendrick/flower_Fruit_and_ratio_2013-2018.csv","249076a1ae7a0118020d3142a8fb2962b2eceb783caca861312b7c858e7d159b")
    i=read("kendrick/inflor_shoot_ReprodEffort_2013-2018.csv","405e75b888bef02df40c8746dc8db1a0a2afb41c7f2d7a55c9347ae39ed2f8cd")
    assert len(f)==416 and len(i)==180
    groups=defaultdict(list); keys=set(); mismatches=0
    for r in f:
        k=(r["location"],int(r["year"])); unique=(*k,r["rep"])
        if unique in keys:raise ValueError("duplicate flower replicate")
        keys.add(unique)
        F=float(r["Flowers m2"]);S=float(r["Fruit m2"])
        if F<=0 or not 0<=S<=F:raise ValueError("invalid count/density")
        mismatches+=abs(float(r["fr/fl"])-S/F)>.01
        groups[k].append((F,S))
    rows=[]
    for (loc,year),values in sorted(groups.items()):
        F=st.mean(x[0] for x in values);S=st.mean(x[1] for x in values)
        if S<=0:raise ValueError("zero site-year fruit: positive-log endpoint non-estimable")
        q=S/F
        rows.append(dict(location=loc,year=year,n=len(values),flower=F,fruit=S,ratio=q,
                         log_values=[math.log(F),math.log(q),math.log(S)]))
    idx={(r["location"],r["year"]):r["log_values"] for r in rows}
    changes=[tuple(v[k]-idx[(loc,y-1)][k] for k in range(3))
             for (loc,y),v in idx.items() if (loc,y-1) in idx]
    sites=sorted({r["location"] for r in rows})
    years=sorted({r["year"] for r in rows})
    missing=sorted({(r["location"],int(r["year"])) for r in i}-set(idx))
    assert len(rows)==35 and len(changes)==29 and missing==[("Nancy Cove",2013)]
    return dict(rows=rows,site_years=len(rows),adjacent_year_changes=len(changes),
         source_ratio_discrepancies_gt_0_01=mismatches,missing_site_years=missing,
         pooled_shares_flower_ratio=parts([r["log_values"] for r in rows]),
         within_site_shares_flower_ratio=parts(center(rows)),
         adjacent_change_shares_flower_ratio=parts(changes),
         leave_site_out={s:parts(center([r for r in rows if r["location"]!=s])) for s in sites},
         leave_year_out={y:parts(center([r for r in rows if r["year"]!=y])) for y in years},
         caution="Exact descriptive covariance allocation of identity log fruit=log flower+log ratio; equal site-year weight. Not explained variance from independent predictors, causality, pollination limitation, or a meta-analysis.")

def johnson():
    f=read("johnson/Seedling_Competition_Exp_MASTER.csv","97918fffb039b7111c7825cdaa331c8be38d3c7b1c2b1883e4b53a3330666385")
    assert len(f)==567
    dates=sorted({datetime.strptime(r["Date"],"%d-%b-%y").date() for r in f})
    groups=defaultdict(dict); arm={}
    for r in f:
        k=(r["Quadrant"],r["Seedling.Cell"]); d=datetime.strptime(r["Date"],"%d-%b-%y").date()
        if d in groups[k] or (k in arm and arm[k]!=r["Competition.Trt"]):raise ValueError("identity or treatment drift")
        groups[k][d]=int(r["Seedling.Survival"]);arm[k]=r["Competition.Trt"]
    assert len(groups)==21 and len(dates)==27
    for v in groups.values():
        assert set(v)==set(dates)
        seq=[v[d] for d in dates]
        assert set(seq)<={0,1} and seq[0]==1 and all(a>=b for a,b in zip(seq,seq[1:]))
    def estimate(start,condition):
        out={}
        for t in ("removed","left"):
            seq=[[v[d] for d in dates[start:]] for k,v in groups.items() if arm[k]==t and (not condition or v[dates[start]]==1)]
            gaps=[(b-a).days for a,b in zip(dates[start:],dates[start+1:])]
            lo=st.mean(sum(a*b for a,b in zip(s[1:],gaps)) for s in seq)
            hi=st.mean(sum(a*b for a,b in zip(s[:-1],gaps)) for s in seq)
            out[t]=dict(n=len(seq),end_alive=sum(s[-1] for s in seq),restricted_mean_alive_days_bounds=[lo,hi])
        return out
    return dict(assigned=estimate(0,False),conditional_on_15_may_alive=estimate(2,True),
        dates=[d.isoformat() for d in dates],initial_to_last_days=(dates[-1]-dates[0]).days,
        caution="Haphazard treatment assignment and close neighbours assigned controls per source metadata. One meadow, no independent sites; observed death interval bounds, not sampling CI. Conditional analysis selects post-treatment survivors. No causal universal estimate.")
if __name__=="__main__":
    print(json.dumps({"status":"posthoc_original_data_descriptive","kendrick":kendrick(),"johnson":johnson()},indent=2,sort_keys=True))
