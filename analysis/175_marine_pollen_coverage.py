#!/usr/bin/env python3
"""Published Table 2 totals, NOT reconstructed trap-level raw data."""
import json, math, csv
from pathlib import Path
ROWS=[('Back-Reef','2006-04-26',120,16,67),('Back-Reef','2006-05-10',120,17,57),('Mid-Lagoon','2006-05-25',100,23,71)]
def run():
    result=[]
    for site,date,n,k,m in ROWS:
        e=n*(1-(1-1/n)**m)
        a,b=divmod(m,k)
        pairs_min=(k-b)*math.comb(a,2)+b*math.comb(a+1,2)
        pairs_max=math.comb(m-k+1,2)
        qmin=pairs_min/math.comb(m,2)
        qmax=pairs_max/math.comb(m,2)
        result.append(dict(site=site,date=date,traps=n,positive=k,grains=m,zero_fraction=1-k/n,expected_positive_equal_probability=e,expected_zero_fraction=1-e/n,observed_to_expected_positive=k/e,mean_grains_all=m/n,mean_grains_positive=m/k,pair_concentration_lower=qmin,pair_concentration_upper=qmax,equal_probability_pair=1/n,pair_concentration_lower_relative=qmin*n))
    fruit=[]
    for name,p0,p1 in [('2008 male flower removal',.86,.60),('2009 pollen addition',.65,.91)]:
        fruit.append(dict(comparison=name,fruit_set_reference=p0,fruit_set_treatment=p1,zero_reference=1-p0,zero_treatment=1-p1,zero_RD=p0-p1,zero_RR=(1-p1)/(1-p0)))
    return dict(status='published aggregate calculation only',source_doi='10.1002/ece3.2309',trap_table=2,trap_results=result,fruit_source_doi='10.3354/meps08870',fruit_failure=fruit,limits=['Three trials; equal-probability allocation is only a descriptive benchmark. Trap distances, hydrodynamics, and mucilage clusters differ. No significance test or identification of animal transport.','Pair concentration bounds are combinatorial bounds conditional on published counts, not population confidence intervals.','No trap coordinates or raw counts; cannot control for distance or infer female flower receipt.','Fruit-set from rounded reported means; distinct years/treatments; no pooled effects or animal exclusion.'])
if __name__=='__main__':
    r=run();p=Path(__file__).parent;(p/'results.json').write_text(json.dumps(r,indent=2)+'\n')
    with (p/'trap_summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=r['trap_results'][0]);w.writeheader();w.writerows(r['trap_results'])
    print(json.dumps(r,indent=2))
