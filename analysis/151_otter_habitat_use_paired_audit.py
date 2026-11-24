#!/usr/bin/env python3
"""Eby et al. paired habitat-use observations, not plant response."""
import argparse,csv,datetime,hashlib,io,json,statistics as st
from collections import defaultdict
from pathlib import Path
SHA="99820885ece8398dd0a438b9329c65a00404b4a55ef88d492e533711f7e70b3d"
def analyze(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("source drift")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    assert len(rows)==59 and len({x["Date"] for x in rows})==59
    groups=defaultdict(list)
    for x in rows:
        d=datetime.datetime.strptime(x["Date"],"%d-%b-%y").date()
        e,w=float(x["Eelgrass_Density"]),float(x["Water_Density"])
        n,m=int(x["Eelgrass_Number"]),int(x["Water_Number"])
        assert min(e,w,n,m)>=0 and (n==0)==(e==0) and (m==0)==(w==0)
        groups[str(d.year)].append((e,w,n,m));groups["all"].append((e,w,n,m))
    out={}
    for k,v in groups.items():
        a,b=st.mean(x[0] for x in v),st.mean(x[1] for x in v)
        out[k]={"surveys":len(v),"mean_eelgrass_otters_per_ha":a,"mean_water_otters_per_ha":b,"ratio_of_mean_densities":a/b,
                "eelgrass_density_higher":sum(x[0]>x[1] for x in v),"equal":sum(x[0]==x[1] for x in v),
                "water_density_higher":sum(x[0]<x[1] for x in v),
                "summed_eelgrass_sightings":sum(x[2] for x in v),"summed_water_sightings":sum(x[3] for x in v)}
    assert {k:v["surveys"] for k,v in out.items()}=={"all":59,"2018":5,"2019":30,"2020":24}
    return {"status":"posthoc_paired_habitat_use_description","source_sha256":SHA,"source_doi":"10.7291/D1FX0Z","groups":out,
            "limitations":["Seal Bend only. Repeat counts not unique animals; no survey independence or selection-adjusted inference.","Original paper already compared otter habitat densities; not a new discovery of habitat preference.","Ratio of survey-average densities, not mean per-survey ratio; preserves zero counts.","No plant biomass, eelgrass area trend, genetic or reproductive response; no causal direction, feedback, or prey selection inference."]}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=Path("otter_sources/wasson/Elkhorn_Otter_Eelgrass.csv"));a=p.parse_args()
    print(json.dumps(analyze(a.input.read_bytes()),indent=2,sort_keys=True,allow_nan=False))
