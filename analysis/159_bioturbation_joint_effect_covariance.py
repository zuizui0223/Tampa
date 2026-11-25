#!/usr/bin/env python3
"""Joint within-tank effect vectors and sampling covariance for meta readiness.

Single Laukaityte et al. 2025 study, not eight independent studies.
Use the author-selected rows and source integrity gates from analysis/158.
Retain shared-control covariance across fauna and endpoints; never infer
a cross-temperature covariance from separate water-bath groups.
"""
import argparse, importlib.util, json, math, statistics as st
from collections import defaultdict
from pathlib import Path
p=Path(__file__).with_name("158_bioturbation_burial_germination_stage_audit.py")
s=importlib.util.spec_from_file_location("source",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
FAUNA=m.FAUNA[1:]
LABELS=[f"{f}|{e}" for f in FAUNA for e in ("buried_fraction_of_counted","germinated_count_per_nominal_10")]
def covariance(x,y):
    a,b=st.mean(x),st.mean(y)
    return sum((u-a)*(v-b) for u,v in zip(x,y))/(len(x)-1)
def estimate(groups):
    # Equal weight per run, eight tank blocks per run and temperature.
    q=len(groups);k=len(groups[0][0])
    if q!=2 or any(len(g)!=8 or any(len(x)!=k for x in g) for g in groups):raise ValueError("unexpected run/block structure")
    avg=[st.mean(st.mean(x[i] for x in g) for g in groups) for i in range(k)]
    C=[[sum(covariance([x[i] for x in g],[x[j] for x in g])/len(g) for g in groups)/q**2 for j in range(k)] for i in range(k)]
    return avg,C
def analyze(raw):
    a=m.parse(raw);blocks=defaultdict(dict)
    for r in a:
        key=r["run"],r["temp"],r["block"];assert r["fauna"] not in blocks[key]
        blocks[key][r["fauna"]]=r
    assert len(blocks)==32 and all(set(v)==set(m.FAUNA) for v in blocks.values())
    out={}
    for temp in m.TEMPS:
        groups=[];detail=[]
        for run in (2,3):
            g=[]
            for key,v in sorted(blocks.items()):
                if key[:2]!=(run,temp):continue
                control=v["NO"]
                z=[]
                for f in FAUNA:
                    x=v[f]
                    z.extend((control["s"]/control["n"]-x["s"]/x["n"],(x["g"]-control["g"])/10))
                g.append(z);detail.append({"run":run,"block":key[2],"effect_vector":z})
            groups.append(g)
        avg,C=estimate(groups)
        se=[math.sqrt(C[i][i]) for i in range(len(avg))]
        corr=[[C[i][j]/(se[i]*se[j]) for j in range(len(avg))] for i in range(len(avg))]
        pairs=[{"fauna":f,"burial":avg[2*i],"burial_se":se[2*i],"germ_count_per_10":avg[2*i+1],"germ_count_per_10_se":se[2*i+1],"sampling_correlation":corr[2*i][2*i+1]} for i,f in enumerate(FAUNA)]
        out[temp]={"labels":LABELS,"effect_estimate":avg,"sampling_covariance":C,"sampling_correlation":corr,"pairs":pairs,"tank_vectors":detail}
    return {"status":"one_study_joint_effect_vector_candidate_not_pooled_meta_analysis","study_doi":"10.1007/s00442-025-05662-y","source_git_blob":m.SOURCE_BLOB,
      "temperature_strata":out,
      "boundaries":["Difference in equal-core fraction buried among counted seeds, and difference in germination count divided by nominal 10 introduced, not a verified probability or matched individual trajectory.",
        "Covariance is conditional on two runs, estimated from eight matched independent tank contrasts per run and temperature. Assumes independent tanks conditional on run; shared baths and only two runs limit temperature/general inference. No between-run or between-temperature covariance estimated.",
        "Shared control and shared endpoints make four treatment vectors dependent; retain full 8x8 covariance per temperature.",
        "No new pooled slope, causal mediation, equivalence or statistically independent studies. No combining arbitrary endpoint units. Source counts discrepancy remains documented in analysis/158."]}
def selftest():
    g=[[i,2*i] for i in range(8)]
    z,C=estimate([g,g])
    assert z==[3.5,7] and abs(C[0][0]-.375)<1e-12 and abs(C[0][1]-.75)<1e-12
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path);a=p.parse_args();selftest()
    print(json.dumps(analyze(a.input.read_bytes() if a.input else m.fetch()),indent=2,sort_keys=True,allow_nan=False))
