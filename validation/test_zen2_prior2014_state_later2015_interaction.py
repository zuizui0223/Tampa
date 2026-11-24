"""No-web, independent-unit tests for the response-open ZEN2 cross-year screen."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/"analysis"/"131_zen2_prior2014_state_later2015_interaction.py"
SPEC=importlib.util.spec_from_file_location("zen2_crossyear",FILE)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def rows(n=14):
    return [
      {
        "site_code":f"S{i:02d}",
        "year2014_shoot_density":5.0+i,
        "year2014_epiphyton":1.0+i%5,
        "year2015_ambient_shoot_density":10.0+2*i,
        "year2015_ambient_epibiont":1.0+i%5,
        "year2015_edge_minus_interior_risk":i*.02-.2,
        "year2015_eighty_minus_ambient_risk":.25-i*.01,
        "nearest_distance_km":.5,
      } for i in range(n)
    ]

class CrossyearTests(unittest.TestCase):
    def test_rank_ties_and_identical_correlation(self):
        self.assertEqual(M.rank([2.,2.,1.,3.]),[2.5,2.5,1.,4.])
        self.assertAlmostEqual(M.spearman([1.,2.,3.,4.,5.],[5.,4.,3.,2.,1.]),-1.)
        self.assertIsNone(M.corr([2.]*6,[1.,2.,3.,4.,5.,6.]))

    def test_synthetic_temporal_stability_and_frozen_n(self):
        j=M.stability(rows(),perms=100,seed=11)
        x=j["source_2014_nearest_subsite_shoot_density_vs_2015_ambient_shoot_density"]
        self.assertEqual(x["n_geographically_nearby_sites"],14)
        self.assertAlmostEqual(x["spearman_r"],1.)
        self.assertAlmostEqual(x["leave_one_site_out_spearman_min"],1.)

    def test_site_permutation_preserves_two_outcome_correlation(self):
        j=M.permutation_screen(rows(),perms=100,seed=11)
        self.assertEqual(j["n_complete_case_sites"],14)
        self.assertEqual(len(j["associations"]),4)
        for row in j["associations"]:
            self.assertGreaterEqual(row["four_comparison_maxT_FWER_permutation_p"],
                                    row["site_label_two_sided_posthoc_permutation_p"])
            self.assertGreaterEqual(row["four_comparison_maxT_FWER_permutation_p"],1/101)
            self.assertLessEqual(row["four_comparison_maxT_FWER_permutation_p"],1)

    def test_missing_prior_epiphyton_is_not_zero(self):
        xs=rows()
        xs[0]["year2014_epiphyton"]=None
        j=M.permutation_screen(xs,perms=100,seed=11)
        self.assertEqual(j["n_complete_case_sites"],13)
        self.assertNotIn("S00",j["complete_case_sites"])

    def test_less_than_ten_sites_blocks_screen(self):
        with self.assertRaises(ValueError):
            M.permutation_screen(rows(8),perms=100)
        with self.assertRaises(ValueError):
            M.stability(rows(8),perms=100)

    def test_reproducibility(self):
        one=M.permutation_screen(rows(),perms=250,seed=123)
        two=M.permutation_screen(rows(),perms=250,seed=123)
        self.assertEqual(one,two)

    def test_no_invalid_nanor_negative_predictors(self):
        xs=rows()
        xs[0]["year2014_shoot_density"]=-2.
        with self.assertRaises(ValueError):
            M.permutation_screen(xs,perms=100)

if __name__=="__main__":
    unittest.main()
