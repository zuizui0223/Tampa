"""Synthetic, original-source-free ZEN2 manipulation and ceiling safeguards."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"129_zen2_predation_manipulation_ceiling_audit.py"
SPEC=importlib.util.spec_from_file_location("zen2_dose_ceiling",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def sample():
    rows=[]
    sites=("AA","BB","CC","DD","EE","FF")
    for site in sites:
        for loc in M.ORIGINAL.LOCATIONS:
            for treatment in M.ORIGINAL.TREATMENTS:
                for i in range(6):
                    eaten=1 if site=="CC" else int(i>=3)
                    rows.append({
                        "site":site,"location":loc,"treatment":treatment,
                        "recorded_eaten":eaten,
                        "taxon":"Isopod" if site in ("EE","FF") else "Amphipod",
                        "density_initial":100.,
                        "density_actual":{"Amb":100.,"Fifty":50.,"Eighty":20.}[treatment],
                        "size_mm":8. if eaten else 5.,
                        "epibiont":1.,"crust_biomass":0.5,
                        "tether":str(i),
                    })
    primary=M.ORIGINAL.analyze(rows)
    return rows,primary

class AuditTests(unittest.TestCase):
    def test_non_original_fixture_requires_explicit_override(self):
        rows,primary=sample()
        with self.assertRaises(ValueError):
            M.summarize(rows,primary)

    def test_exact_dose_and_ceiling_identified(self):
        rows,primary=sample()
        j=M.summarize(rows,primary,require_original_frame=False)
        self.assertEqual(j["site_count"],6)
        self.assertEqual(j["original_tethered_prey_trials"],216)
        self.assertEqual(j["sites_with_100pct_consumption"],["CC"])
        self.assertEqual(j["number_sites_other"],5)
        doses=j["manipulation_fidelity_source_count_diagnostic"]["site_mean_post_pre_ratios"]
        for treatment,value in (("Amb",1),("Fifty",.5),("Eighty",.2)):
            self.assertAlmostEqual(doses[treatment]["median"],value)
            self.assertAlmostEqual(doses[treatment]["maximum_absolute_deviation_from_nominal"],0)

    def test_preyspecies_is_site_confounded_not_within_site(self):
        rows,primary=sample()
        j=M.summarize(rows,primary,require_original_frame=False)
        self.assertEqual(j["taxon_by_site_not_an_independent_species_experiment"]["Isopod"]["n_sites"],2)
        self.assertEqual(j["taxon_by_site_not_an_independent_species_experiment"]["Amphipod"]["n_sites"],4)

    def test_size_protection_is_observational_and_matched(self):
        rows,primary=sample()
        j=M.summarize(rows,primary,require_original_frame=False)
        for key in ("prey_size_eaten_minus_alive_within_site_mm",
                    "prey_size_eaten_minus_alive_within_site_treatment_cells_mm"):
            r=j["size_diagnostic_posthoc_no_causal_prey_selection"][key]
            self.assertEqual(r["sites_with_estimate"],5)
            self.assertAlmostEqual(r["site_equal_mean_mm"],3)
            self.assertEqual(r["site_bootstrap_95pct_percentile"],[3,3])

    def test_tether_labels_repeat_and_are_not_216_independent_sites(self):
        rows,primary=sample()
        j=M.summarize(rows,primary,require_original_frame=False)
        self.assertEqual(j["tether_id_uniqueness"]["sum_within_site_unique_tether_labels"],36)
        self.assertEqual(j["tether_id_uniqueness"]["sum_within_site_reused_labels"],180)
        self.assertEqual(j["site_count"],6)

    def test_one_site_with_mixed_taxa_fails_falsifiability_gate(self):
        rows,primary=sample()
        rows[0]["taxon"]="Isopod"
        with self.assertRaises(ValueError):
            M.summarize(rows,primary,require_original_frame=False)

if __name__=="__main__":
    unittest.main()
