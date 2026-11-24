#!/usr/bin/env python3
"""Reproduce published summary arithmetic; not a causal or fitted field model."""
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT/"data/seagrass_interactions_v1/seed_predation_burial_inputs.json").read_text())
p = d["infantes_2016"]
f = p["field_8_month_seedling_establishment"]
out = {"field_establishment_ratio": f["predator_exclosure"]/f["predator_access"],
       "depth_scenarios": [], "seed_supply_scenarios": []}
for x in p["reported_seed_loss_by_depth"]:
    q = x["predation"]
    assert 0 <= q < 1
    s = 1-q
    out["depth_scenarios"].append(dict(depth_cm=x["depth_cm"],observed_survival=s,
        half_hazard_survival=math.sqrt(s),half_hazard_gain_pp=100*(math.sqrt(s)-s),
        zero_hazard_survival=1,zero_hazard_gain_pp=100*q,zero_hazard_ratio=1/s))
r = d["li_2018"]["seed_rain_per_m2"]
for k,n in r.items():
    if k!="inside":
        out["seed_supply_scenarios"].append(dict(context=k,ratio_to_inside=n/r["inside"],
            break_even_later_recruitment_multiplier=r["inside"]/n))
assert math.isclose(out["field_establishment_ratio"],28)
assert out["depth_scenarios"][0]["half_hazard_gain_pp"] > out["depth_scenarios"][1]["half_hazard_gain_pp"] > out["depth_scenarios"][2]["half_hazard_gain_pp"]
print(json.dumps(out,indent=2))
