"""Reproduce published-summary arithmetic, no raw data fit."""
import json
from pathlib import Path
s=[('COP',.03,1.90,6),('DEV',.36,7.65,100),('HD',.97,1.62,100),('MM',15.80,16.30,136),('LP',8.58,12.60,78),('TC',15.20,18.40,106),('CB',0,6.37,2)]
p=[(2.5,57,14,9.6,2.3),(5,16,6,3.7,2.7),(10,34,13,5.7,3.7),(20,20,6,7.4,3.1)]
sites=[dict(site=k,male=m,female=f,total=m+f,males_per_female=m/f,male_fraction=m/(m+f),common_garden_collected=n,extreme_male_rarity=m<.3,in_reported_germination_comparison=k not in ('COP','CB')) for k,m,f,n in s]
patches=[dict(nominal_area_m2=a,viable_m2=v,nonviable_m2=u,ratio_of_means_viable_fraction=v/(v+u),nominal_total_viable=a*v,flowering_shoots_m2_2012=r,viable_per_reproductive_shoot_2012=t) for a,v,u,r,t in p]
assert sum(x['common_garden_collected'] for x in sites if x['in_reported_germination_comparison'])==520
assert sum(x['common_garden_collected'] for x in sites)==528
print(json.dumps(dict(sites=sites,patches=patches,CB_HD_total=6.37/2.59,DEV_HD_total=8.01/2.59,DEV_HD_male_female=(.36/7.65)/(.97/1.62),density_ratio=57/20,nominal_total_ratio=400/142.5,mass_flowering_ratio=97/5),indent=2))
