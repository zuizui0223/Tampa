"""Site-level post-hoc environmental moderator screen tests."""
from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"analysis"/"125_zen_site_moderator_posthoc_robustness.py"
SPEC=importlib.util.spec_from_file_location("zenmoderator",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class ZENModeratorTests(unittest.TestCase):
    def test_ties_get_midrank(self):
        self.assertEqual(M.ranks([2,2,5,1]),[2.5,2.5,4,1])

    def test_pearson_exact(self):
        self.assertAlmostEqual(M.corr([1,2,3,4,5],[2,4,6,8,10]),1)
        self.assertAlmostEqual(M.corr([1,2,3,4,5],[10,8,6,4,2]),-1)
        self.assertIsNone(M.corr([1,1,1,1,1],[1,2,3,4,5]))

    def test_pinned_15site_effect_not_600_pseudoreplicates(self):
        source=json.loads(M.SOURCE.read_text())
        result=M.calculate(source)
        self.assertEqual(result["schema"],"tampa.zen_site_moderator_posthoc_robustness_v1")
        self.assertEqual(result["permutation"]["draws"],20000)
        for var in M.PREDICTORS:
            x=result["predictor_results"][var]
            self.assertEqual(x["n_sites"],15)
            self.assertGreaterEqual(x["three_predictor_familywise_maxT_permutation_p"],
                                    x["two_sided_unadjusted_site_label_permutation_p"])
            self.assertLessEqual(x["leave_one_site_out_pearson_min"],
                                 x["pearson_r"])
            self.assertGreaterEqual(x["leave_one_site_out_pearson_max"],
                                    x["pearson_r"])
        self.assertAlmostEqual(result["predictor_results"]["temp_avg"]["pearson_r"],
                                0.5294093965169012,places=8)

    def test_wrong_source_schema_fails(self):
        s=json.loads(M.SOURCE.read_text())
        s["schema"]="unknown"
        with self.assertRaises(ValueError):
            M.calculate(s)

    def test_reproducible_null_permutations(self):
        s=json.loads(M.SOURCE.read_text())
        a=M.calculate(s)
        b=M.calculate(s)
        self.assertEqual(a,b)

if __name__=="__main__":unittest.main()
