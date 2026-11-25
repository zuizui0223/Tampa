#!/usr/bin/env python3
"""Measured geometry, hypothetical sex and flowering; not observed fertilization."""
import argparse, json, math, itertools, importlib.util
from pathlib import Path
from collections import Counter
import numpy as np
s=importlib.util.spec_from_file_location("spatial_null",Path(__file__).with_name("142_enhalus_spatial_null_decomposition.py"))
mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
RADII=(1,2,4,8)
FLOWERS=(.01,.05,.10,.25,.50,1.)
SEX=(.3,.5,.7)

def probability(counts,p,f,mode):
    qs=[p*(1-(1-f)**k if mode=="independent_ramets" else f) for k in counts]
    return 1-math.prod(1-q for q in qs),sum(qs)

def analyze(raw):
    out={}
    for name,(g,xy) in mod.parse(raw).items():
        d2=((xy[:,None,:]-xy[None,:,:])**2).sum(2)
        freq=Counter(g.tolist()); w=np.array([1/freq[i] for i in g]);w/=w.sum()
        plot={}
        for r in RADII:
            counts=[list(Counter(g[(d2[i]>0)&(d2[i]<=r*r)&(g!=g[i])].tolist()).values()) for i in range(len(g))]
            scenarios={}
            for p,f,mode in itertools.product(SEX,FLOWERS,("independent_ramets","synchronous_genet")):
                x=np.array([probability(c,p,f,mode) for c in counts])
                scenarios[f"{p:g}|{f:g}|{mode}"]={"ramet_weighted_probability":float(x[:,0].mean()),"genet_equal_probability":float(w@x[:,0]),"expected_distinct_active_donors":float(x[:,1].mean())}
            plot[str(r)]={"scenarios":scenarios}
        out[name]=plot
    summary={}
    for r in map(str,RADII):
        a,b=out["PLOTA"][r]["scenarios"],out["PLOTB"][r]["scenarios"]
        summary[r]={k:{metric:b[k][metric]-a[k][metric] for metric in a[k]} for k in a}
    return {"status":"observed_geometry_hypothetical_sex_flowering_sensitivity","source_sha256":mod.SHA,"plots":out,"B_minus_A":summary,"assumptions":["Condition on focal genet female and flowering; other genets have independent male probability p.","Exact marker MLG treated as genet proxy.","Equal flowering f across plots; independent sampled ramet activity within male genet or perfectly synchronous genet activity.","Fixed circular candidate reach, no transport direction, pollen dose, phenology, compatibility, outside-plot donors or actual fertilization.","One plot per habitat; probabilities are mathematical scenario expectations not field estimates or CIs."]}

def selftest():
    assert probability([], .5,.1,"independent_ramets")==(0,0)
    assert np.allclose(probability([2],.5,.1,"independent_ramets"),(.095,.095))
    assert np.allclose(probability([2],.5,.1,"synchronous_genet"),(.05,.05))
    assert np.allclose(probability([1,1],.5,1,"independent_ramets"),(.75,1))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=Path("reproductive_input/yu/Ramets For Two plots.xlsx"));a=p.parse_args();selftest()
    print(json.dumps(analyze(a.input.read_bytes()),sort_keys=True,indent=2,allow_nan=False))
