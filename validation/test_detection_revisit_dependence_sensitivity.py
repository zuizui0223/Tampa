"""Exact sensitivity checks for a response-free Beta mixture detection effort table."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"112_detection_revisit_dependence_sensitivity.py"
SPEC=importlib.util.spec_from_file_location("detection_revisit_dependence",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class DetectionDependenceTests(unittest.TestCase):
    def test_independent_limit(self):
        self.assertAlmostEqual(M.miss_probability(3,.4,0),.6**3)
        self.assertEqual(M.required_visits(.4,0)["minimum_rounds"],6)

    def test_beta_mixture_exact_small_k(self):
        # Beta(2,3) => mean p=.4, rho=1/6
        self.assertAlmostEqual(M.miss_probability(2,.4,1/6),3*4/(5*6))
        self.assertAlmostEqual(M.miss_probability(3,.4,1/6),3*4*5/(5*6*7))

    def test_primary_grid_counts(self):
        expected={
            (.4,0.0):6,(.4,.1):9,(.4,.2):15,
            (.6,0.0):4,(.6,.1):5,(.6,.2):6,
            (.8,0.0):2,(.8,.1):3,(.8,.2):3,
        }
        self.assertEqual(len(M.report()["primary_grid"]),9)
        for (p,rho),k in expected.items():
            d=M.required_visits(p,rho)
            self.assertEqual(d["status"],"CONDITIONAL_MATHEMATICAL_TARGET_MET")
            self.assertEqual(d["minimum_rounds"],k)
            self.assertLessEqual(d["all_miss_at_minimum_rounds"],.05+1e-12)
            self.assertGreater(d["all_miss_at_one_fewer_round"],.05-1e-12)

    def test_same_average_detection_more_heterogeneity_requires_more_repeats(self):
        p=.4
        self.assertLess(M.required_visits(p,0)["minimum_rounds"],
                        M.required_visits(p,.1)["minimum_rounds"])
        self.assertLess(M.required_visits(p,.1)["minimum_rounds"],
                        M.required_visits(p,.2)["minimum_rounds"])

    def test_structural_zero_floor(self):
        d=M.required_visits(.6,.1,z=.08)
        self.assertEqual(d["status"],"NO_FINITE_ROUNDS_CAN_MEET_TARGET")
        self.assertIsNone(d["minimum_rounds"])
        self.assertAlmostEqual(d["asymptotic_miss_probability_floor"],.08)
        self.assertGreater(M.miss_probability(100,.6,.1,.08),.08)

    def test_maximum_budget_is_not_interpreted_as_impossible(self):
        d=M.required_visits(.4,.2,max_visits=10)
        self.assertEqual(d["status"],"NOT_MET_WITHIN_DECLARED_MAXIMUM")
        self.assertGreater(d["all_miss_at_declared_maximum"],.05)

    def test_invalid_parameters_rejected(self):
        cases=[
            lambda: M.required_visits(0,.1),lambda: M.required_visits(1,.1),
            lambda: M.required_visits(.4,-.1),lambda: M.required_visits(.4,1),
            lambda: M.required_visits(.4,.1,z=1),lambda: M.required_visits(.4,.1,z=-.1),
            lambda: M.required_visits(.4,.1,target_miss=0),
            lambda: M.required_visits(.4,.1,max_visits=0),
            lambda: M.miss_probability(-1,.4,.1),
            lambda: M.miss_probability(1.5,.4,.1),
        ]
        for f in cases:
            with self.assertRaises(ValueError):
                f()

    def test_no_field_data_or_fitted_parameters(self):
        r=M.report()
        self.assertEqual(r["evidence_class"],"response_free_illustrative_measurement_design_not_field_data")
        self.assertIn("not Tampa estimates",r["limitations"][0])
        self.assertIn("TNC",r["limitations"][-1])

if __name__=="__main__":
    unittest.main()
