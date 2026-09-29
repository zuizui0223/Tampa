#!/usr/bin/env python3
"""Verify the bounded Tampa qualitative-epiphyte mechanism audit."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

p=json.loads((ROOT/"results/epiphyte_measurement_layer_preflight_v1.json").read_text())
assert p["status"]=="unused_measurement_layer_has_substantial_focal_coverage"
assert p["response_blind"] is True
assert p["all_taxa"]["rows_with_density"]==31737
assert p["all_taxa"]["unique_transects"]==71
assert p["thalassia"]["rows_with_density"]==7590
assert p["thalassia"]["unique_points"]==7575
assert p["thalassia"]["unique_visits"]==901
assert p["thalassia"]["unique_transects"]==52
assert p["measurement"]["ordinal_mapping"]=={"Clean":0,"Light":1,"Moderate":2,"Heavy":3}

c=json.loads((ROOT/"results/epiphyte_retention_v1_contract.json").read_text())
assert c["status"]=="posthoc_followup_frozen_after_unadjusted_registry_opened"
assert c["primary_analysis"]["primary_coefficient"]=="epi_within_node"
assert c["transition_population"]["primary_target_year_exclusion"]==2016
assert c["primary_analysis"]["bootstrap"]["replicates"]==1000

r=json.loads((ROOT/"results/epiphyte_retention_v1.json").read_text())
assert r["status"]=="primary_positive_but_2016_sensitivity_not_supported"
pri=r["primary_exclude_target_2016"]
sen=r["sensitivity_include_target_2016"]
assert pri["complete_transitions"]==4189
assert pri["nodes"]==49
assert pri["recorded_losses"]==810
assert abs(pri["coefficient_epi_within_node"]-0.11777939835174929)<1e-12
assert pri["ci95"][0]>0 and pri["ci95"][1]>0
assert pri["classification"]=="within_node_positive_epiphyte_signal"
assert sen["complete_transitions"]==4279
assert sen["nodes"]==49
assert sen["recorded_losses"]==840
assert sen["ci95"][0]<0<sen["ci95"][1]
assert sen["classification"]=="within_node_epiphyte_signal_not_supported"
assert "does not support the simple hypothesis" in r["interpretation"]
assert "measure epiphyte biomass" in r["next_measurement_boundary"]
assert any("Do not retune" in x for x in r["claim_boundary"])

print("Tampa qualitative epiphyte layer: bounded result verified")
