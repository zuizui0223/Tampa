#!/usr/bin/env python3
"""Post-hoc association between paired site treatment contrasts, not mediation."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/zen_15site_mesograzer_exploratory_verified_20261124.json"
BLOB = "ca992c835cf369f9a69689382f6969a06eadec16"
SOURCE = "5a97763735a22076eac25a86736c50cb12611a529c5e233941fbc3a73ad4c6ae"
KEY = "grazer_deterrent_main_difference"
N = 20000

def pearson(x, y):
    a = [v-sum(x)/len(x) for v in x]
    b = [v-sum(y)/len(y) for v in y]
    d = math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
    return sum(v*w for v,w in zip(a,b))/d if d else math.nan

def ranks(x):
    return [1+sum(w<v for w in x)+(sum(w==v for w in x)-1)/2 for v in x]

class RNG:
    def __init__(self): self.state = 20261124
    def index(self, n):
        self.state = (1664525*self.state+1013904223) % (2**32)
        return self.state*n//(2**32)

def load():
    raw = LEDGER.read_bytes()
    if hashlib.sha1(("blob "+str(len(raw))+"\0").encode()+raw).hexdigest()!=BLOB:
        raise ValueError("Unexpected frozen treatment-cell ledger Git blob")
    o = json.loads(raw)
    if o["source"]["sha256"]!=SOURCE:
        raise ValueError("Wrong original data source")
    a=[]
    for row in o["analysis"]["per_site_exploratory_contrasts"]:
        e=row["endpoints"]
        def contrast(name):
            item=e[name]
            if not item["eligible_for_four_arm_contrast"]:
                raise ValueError("Ineligible site")
            m=item["arm_means"]
            value=(math.log(m["D+N+"])+math.log(m["D+N-"])-math.log(m["D-N+"])-math.log(m["D-N-"]))/2
            if abs(value-item["posthoc_log_arm_mean_contrasts"][KEY])>1e-10:
                raise ValueError("Contrast drift")
            return item["posthoc_log_arm_mean_contrasts"][KEY]
        a.append({"site":row["site"],"grazer_reduction":-contrast("grazer_bmass_per_g"),
                  "epiphyte_increase":contrast("chla_per_Zostera")})
    if len(a)!=15 or len({v["site"] for v in a})!=15:
        raise ValueError("Expected 15 unique sites")
    return a

def analyze(a):
    x=[v["grazer_reduction"] for v in a]
    y=[v["epiphyte_increase"] for v in a]
    r=pearson(x,y)
    rho=pearson(ranks(x),ranks(y))
    rng=RNG()
    cp=cs=0
    boots=[]
    for _ in range(N):
        z=y[:]
        for k in range(len(z)-1,0,-1):
            j=rng.index(k+1)
            z[k],z[j]=z[j],z[k]
        cp+=abs(pearson(x,z))>=abs(r)-1e-12
        cs+=abs(pearson(ranks(x),ranks(z)))>=abs(rho)-1e-12
        ids=[rng.index(len(x)) for _ in x]
        b=pearson([x[j] for j in ids],[y[j] for j in ids])
        if math.isfinite(b): boots.append(b)
    boots.sort()
    loo=[pearson(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(x))]
    return {"status":"posthoc_site_contrast_association_not_mediation",
            "original_source_sha256":SOURCE,"input_git_blob":BLOB,
            "sites":len(a),"paired_site_effects":a,
            "pearson_r":r,"spearman_rho":rho,
            "two_sided_site_label_permutation_p":(cp+1)/(N+1),
            "spearman_permutation_sensitivity_p":(cs+1)/(N+1),
            "paired_site_bootstrap_descriptive_95pct_interval":[boots[int(.025*len(boots))],boots[int(.975*len(boots))]],
            "leave_one_site_out_pearson_range":[min(loo),max(loo)],
            "sign_table_reduction_positive_by_epiphyte_increase_positive":[
                sum(u>0 and v>0 for u,v in zip(x,y)),
                sum(u>0 and v<=0 for u,v in zip(x,y)),
                sum(u<=0 and v>0 for u,v in zip(x,y)),
                sum(u<=0 and v<=0 for u,v in zip(x,y))],
            "interpretation":"Positive exploratory tendency; primary permutation does not resolve association. Site exchangeability uncertain; bootstrap descriptive. No causal mediation or plant-state response measured."}

if __name__=="__main__":
    print(json.dumps(analyze(load()), indent=2, sort_keys=True))
