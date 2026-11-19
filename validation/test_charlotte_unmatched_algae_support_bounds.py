"""Synthetic and locked-source tests for unmatched-map-support bounds.

Never interprets support sensitivity as a confidence interval or causal effect.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("ch108",ROOT/"analysis/108_charlotte_unmatched_algae_support_bounds.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
FROZEN=json.loads((ROOT/"results/charlotte_patch_size_spatial_support_verified_20261119.json").read_text(encoding="utf-8"))

class UnknownSupportBounds(unittest.TestCase):
    def test_real_source_reproduces_conditional_and_missing_ranges(self):
        result=M.evaluate(FROZEN)
        self.assertEqual(result["status"],"SOURCE_PINNED_PARTIAL_INFORMATION_SENSITIVITY_ONLY")
        self.assertTrue(result["no_pvalue_or_confidence_interval"])
        all_cases=result["results"]
        joint=all_cases["joint patch-size and 5km geography"]
        size=all_cases["2022 source patch-size bins"]
        self.assertAlmostEqual(joint["matched_algae_area_percent"],47.288,places=3)
        self.assertAlmostEqual(joint["conditional_original_matched_class_gap_points"],8.020,places=2)
        self.assertAlmostEqual(joint["full_algae_area_hypothetical_comparator_gap_lower_points"],-7.111,places=2)
        self.assertAlmostEqual(joint["full_algae_area_hypothetical_comparator_gap_upper_points"],45.601,places=2)
        self.assertTrue(joint["zero_inside_feasible_envelope"])
        self.assertFalse(joint["whole_area_adjusted_effect_is_estimable"])
        self.assertEqual(joint["reverse_direction_matched_strata_count"],3)
        self.assertAlmostEqual(joint["reverse_direction_algae_area_percent_of_matched"],31.248,places=2)
        self.assertAlmostEqual(joint["weighted_effective_n_matched_strata"],7.529,places=2)
        self.assertAlmostEqual(size["full_algae_area_hypothetical_comparator_gap_lower_points"],6.930,places=2)
        self.assertAlmostEqual(size["full_algae_area_hypothetical_comparator_gap_upper_points"],53.279,places=2)
        self.assertFalse(size["zero_inside_feasible_envelope"])

    def test_toy_unknown_sea_reference_exact_envelope(self):
        example={"cell_data":{
          "matched":{"in_common_support":True,
                     "seagrass":{"same_class_rate_percent":70,"patches":4},
                     "attached_macroalgae":{"same_class_rate_percent":50,"source_area_acres":40,
                         "retained_area_acres":20,"patches":4}},
          "unmatched":{"in_common_support":False,
                     "seagrass":{"patches":0},
                     "attached_macroalgae":{"source_area_acres":60,
                         "retained_area_acres":30,"patches":2}}},
          "matched_algae_area_acres":40,
          "weighted_seagrass_minus_algae_points":20,
          "algae_source_area_with_comparable_seagrass_percent":40,
          "can_generalize_to_full_algae_area":False}
        result=M.bounds(example,100,50)
        self.assertEqual(result["full_algae_area_hypothetical_comparator_gap_lower_points"],-22)
        self.assertEqual(result["full_algae_area_hypothetical_comparator_gap_upper_points"],38)
        self.assertEqual(result["unsupported_observed_algae_retained_acres"],30)
        self.assertTrue(result["not_a_confidence_interval"])

    def test_changed_source_digest_refused(self):
        bad=copy.deepcopy(FROZEN);bad["audited_ci"]["artifact_zip_sha256"]="sha256:not-the-verified-source"
        with self.assertRaisesRegex(M.Stop,"PROVENANCE_NOT_VERIFIED"):
            M.evaluate(bad)

    def test_missing_supported_class_reference_refused(self):
        bad=copy.deepcopy(FROZEN)
        bad["report"]["size_stratification"]["cell_data"]["10-50ac"]["seagrass"]["same_class_rate_percent"]=None
        with self.assertRaisesRegex(M.Stop,"INVALID_NUMERIC_FIELD"):
            M.evaluate(bad)

    def test_algae_area_nonclosure_refused(self):
        bad=copy.deepcopy(FROZEN)
        bad["report"]["size_stratification"]["cell_data"]["10-50ac"]["attached_macroalgae"]["source_area_acres"]+=2
        with self.assertRaisesRegex(M.Stop,"MASS_BALANCE_FAILED"):
            M.evaluate(bad)

    def test_no_posthoc_change_of_support_allowed(self):
        bad=copy.deepcopy(FROZEN)
        bad["report"]["size_by_grid_stratification"]["cell_data"]["10-50ac|-1584:660"]["in_common_support"]=False
        with self.assertRaisesRegex(M.Stop,"PREVIOUS_MATCHED_ALGAE_AREA_CHANGED"):
            M.evaluate(bad)

    def test_zero_denominator_and_nan_fail(self):
        base={"cell_data":{
           "matched":{"in_common_support":True,
               "seagrass":{"same_class_rate_percent":80,"patches":3},
               "attached_macroalgae":{"source_area_acres":float("nan"),
                   "retained_area_acres":1,"same_class_rate_percent":40,"patches":3}}},
           "matched_algae_area_acres":1,"weighted_seagrass_minus_algae_points":40,
           "algae_source_area_with_comparable_seagrass_percent":100}
        with self.assertRaisesRegex(M.Stop,"INVALID_NUMERIC_FIELD"):
            M.bounds(base,1,1)

if __name__=="__main__":
    unittest.main()
