"""Source-summary-only exact tests for return-history exchangeability audit."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"111_return_fragility_exchangeability_audit.py"
SPEC=importlib.util.spec_from_file_location("exchangeability_audit",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def fixture():
    return {"schema":"tampa.return_fragility_v1.canonical_summary",
            "status":"return_fragility_supported",
            "registry":{"four_year_sequences":580,"recovered_sequences":83,
                        "continuous_sequences":497,"total_recorded_relosses":94},
            "secondary":{"recovered_reloss_fraction":30/83,
                         "continuous_reloss_fraction":64/497}}

class TestExchangeabilityAudit(unittest.TestCase):
    def test_canonical_table_exact(self):
        r=M.analyze(M.cells_from_frozen(fixture()))
        self.assertEqual(r["cells"],{
            "middle_missing_next_missing":30,"middle_missing_next_present":53,
            "middle_present_next_missing":64,"middle_present_next_present":433})
        self.assertEqual(r["observed_offdiagonal_asymmetry_count"],11)
        self.assertEqual(r["middle_missing_count"],83)
        self.assertEqual(r["future_missing_count"],94)
        self.assertTrue(r["not_a_valid_unclustered_mcnemar_test"])

    def test_exchangeable_symmetrized_moment_is_feasible(self):
        m=M.analyze(M.cells_from_frozen(fixture()))["symmetrized_compatibility_example_not_actual_observations"]
        self.assertTrue(m["feasible_stationary_heterogeneous_q"])
        self.assertGreater(m["variance_q"],0)
        self.assertAlmostEqual(m["mean_q"],177/1160)
        self.assertAlmostEqual(m["second_moment_q"],30/580)
        x=m["one_exact_two_point_conditional_mixture"]
        self.assertAlmostEqual(x["reconstructed_first_moment"],m["mean_q"])
        self.assertAlmostEqual(x["reconstructed_second_moment"],m["second_moment_q"])
        self.assertEqual(x["true_occupancy_all_years"],"present")

    def test_infeasible_second_moment_detected(self):
        x=M.analyze({"middle_missing_next_missing":0,"middle_missing_next_present":50,
                     "middle_present_next_missing":50,"middle_present_next_present":0})
        self.assertFalse(x["symmetrized_compatibility_example_not_actual_observations"]["feasible_stationary_heterogeneous_q"])

    def test_independent_repeats_require_enough_visits(self):
        expected={.3:9,.4:6,.5:5,.6:4,.7:3,.8:2}
        for p,k in expected.items():
            r=M.repeats_for_detection(p)
            self.assertEqual(r["repeat_visits"],k)
            self.assertLessEqual(r["all_miss_probability_given_presence"],.05+1e-14)
            self.assertGreater((1-p)**(k-1),.05-1e-12)

    def test_bad_source_rejected(self):
        for mutation in ("status","schema","total","fraction"):
            s=fixture()
            if mutation=="status":s["status"]="unsupported"
            elif mutation=="schema":s["schema"]="unexpected"
            elif mutation=="total":s["registry"]["total_recorded_relosses"]=95
            else:s["secondary"]["recovered_reloss_fraction"]=.36
            with self.assertRaises(ValueError):
                M.derive(s)

    def test_invalid_independent_visit_p_rejected(self):
        for p in (-.1,0,1,float("nan")):
            with self.assertRaises(ValueError):
                M.repeats_for_detection(p)

if __name__=="__main__":
    unittest.main()
