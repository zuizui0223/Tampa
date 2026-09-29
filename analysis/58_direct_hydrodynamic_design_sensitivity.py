#!/usr/bin/env python3
"""Design sensitivity for the Tampa direct-hydrodynamic prospective test.

No ecological outcome data are read. The calculation asks what partial
correlation for the focal attenuation coefficient is required for 80% power in
a two-sided alpha=0.05 one-df test after four controls.
"""
from __future__ import annotations
import json
from pathlib import Path
from scipy.optimize import brentq
from scipy.stats import f, ncf

ALPHA=0.05
POWER=0.80
CONTROLS=4
NS=(18,24,30,36,42,47)

def threshold(n:int):
    df=n-CONTROLS-2
    crit=f.ppf(1-ALPHA,1,df)
    def pwr(r):
        lam=(r*r)*df/(1-r*r)
        return ncf.sf(crit,1,df,lam)
    r=brentq(lambda x:pwr(x)-POWER,1e-8,0.95)
    return {
        "n":n,
        "residual_df":df,
        "partial_r":r,
        "partial_R2":r*r
    }

def main(out:Path):
    result={
        "schema":"tampa.direct_hydrodynamic_design_sensitivity_v1",
        "response_data_used":False,
        "alpha_two_sided":ALPHA,
        "target_power":POWER,
        "controls":CONTROLS,
        "control_definition":"baseline frequency + ambient p90 + two bay indicators",
        "thresholds":[threshold(n) for n in NS],
        "decision":"Prefer 36 deployed nodes over the earlier 24-node target; repeated within-node velocity observations reduce measurement error but do not replace node-level replication."
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main(Path("results/direct_hydrodynamic_design_sensitivity_v1.json"))
