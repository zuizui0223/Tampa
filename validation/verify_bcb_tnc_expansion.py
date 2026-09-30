#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
x=json.loads((ROOT/"results/bcb_tnc_expansion_preflight_v1.json").read_text())
assert x["status"]=="four_bay_tnc_expansion_feasible"
assert x["current_three_bay"]["recent_thalassia_positive_nodes"]==33
assert x["candidate_four_bay"]["recent_thalassia_positive_nodes"]==41
assert x["candidate_four_bay"]["minimum_nodes_per_bay"]==8
assert x["candidate_four_bay"]["by_water_body"]["Boca Ciega Bay"]["thalassia_positive_nodes"]==8
assert x["candidate_four_bay"]["by_water_body"]["Boca Ciega Bay"]["nodes_with_ge3_positive_marks"]==8
assert x["candidate_four_bay"]["by_water_body"]["Boca Ciega Bay"]["nodes_with_lt3_positive_marks"]==0
assert x["boca_ciega_design_value"]["all_nodes_have_ge3_positive_marks"] is True
assert x["candidate_four_bay"]["approximate_80pct_detectable_partial_r"] < x["current_three_bay"]["approximate_80pct_detectable_partial_r"]
print("Boca Ciega TNC expansion preflight: OK")
