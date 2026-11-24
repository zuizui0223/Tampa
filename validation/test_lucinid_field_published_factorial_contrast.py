"""Published experiment four-arm arithmetic checks (not new inferential tests)."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"analysis"/"122_lucinid_field_published_factorial_contrast.py"
SPEC=importlib.util.spec_from_file_location("lucinid_published2020",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class FieldFactorialTableTests(unittest.TestCase):
    def test_original_means_unchanged_and_source_documented(self):
        x=M.summary()
        self.assertEqual(x["replicate_plots_per_arm"],6)
        self.assertEqual(x["study_count"],1)
        self.assertIn("frontiersin.org",x["table1_original_source"])
        self.assertEqual(x["published_table"]["leaf_sulfide_derived_fraction_pct"]["reported_means_by_arm"],
                         {"C":20.3,"L":19.1,"OM":25.3,"L+OM":22.3})

    def test_intrusion_effects_under_both_organic_treatments(self):
        x=M.summary()["cross_endpoint_observations"]
        self.assertAlmostEqual(x["sulfide_intrusion_clam_reduction_no_organic_pp"],-1.2)
        self.assertAlmostEqual(x["sulfide_intrusion_clam_reduction_high_organic_pp"],-3.0)
        self.assertAlmostEqual(x["magnitude_ratio_of_intrusion_effect_organic_to_no_organic"],2.5)

    def test_rhizome_biomass_immediate_clam_effect_not_supported(self):
        x=M.summary()["published_table"]["rhizome_biomass_g_dw_m2"]
        self.assertAlmostEqual(x["published_mean_contrasts"]["lucinid_main_difference"],2.45)
        self.assertEqual(x["published_inference"]["reported_clam_main_p"],.8)
        self.assertFalse(x["is_new_experimental_evidence"])

    def test_porewater_absolute_effect_is_not_a_significant_result(self):
        x=M.summary()["published_table"]["porewater_sulfide_umol_L"]
        self.assertAlmostEqual(x["published_mean_contrasts"]["lucinid_addition_under_organic"],-454.5)
        self.assertEqual(x["published_inference"]["reported_om_vs_om_plus_clams_p"],.34)

    def test_additive_factorial_means(self):
        x=M.contrasts([1,2,3,4])
        self.assertEqual(x["lucinid_addition_under_no_organic"],1)
        self.assertEqual(x["lucinid_addition_under_organic"],1)
        self.assertEqual(x["lucinid_by_organic_difference_in_differences"],0)
        self.assertEqual(x["lucinid_main_difference"],1)
        self.assertEqual(x["organic_main_difference"],2)

    def test_invalid_four_cell_input_rejected(self):
        for x in ([1,2,3],[1,2,3,float("nan")]):
            with self.assertRaises(ValueError):
                M.contrasts(x)

if __name__=="__main__":unittest.main()
