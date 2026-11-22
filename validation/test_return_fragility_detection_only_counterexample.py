"""No-network checks of analytic detection-only return-fragility counterexample."""
from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "analysis" / "110_return_fragility_detection_only_counterexample.py"
SPEC = importlib.util.spec_from_file_location("detection_only_counterexample", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def fixture():
    return {
        "schema": "tampa.return_fragility_v1.canonical_summary",
        "status": "return_fragility_supported",
        "registry": {
            "four_year_sequences": 580,
            "recovered_sequences": 83,
            "continuous_sequences": 497,
            "total_recorded_relosses": 94,
        },
        "secondary": {
            "recovered_reloss_fraction": 30 / 83,
            "continuous_reloss_fraction": 64 / 497,
        },
    }


class CounterexampleTests(unittest.TestCase):
    def test_beta_round_parameters_reproduce_a_large_gap_without_true_loss(self):
        x = MOD.beta_counterexample(1.0, 0.5)
        self.assertEqual(x["true_occupancy_trajectory"], [1, 1, 1, 1])
        self.assertAlmostEqual(x["fraction_gap_group"], 1 / 7)
        self.assertAlmostEqual(x["later_non_detection_given_gap"], 1 / 3)
        self.assertAlmostEqual(x["later_non_detection_given_continuous"], 1 / 9)
        self.assertAlmostEqual(x["risk_difference_percentage_points"], 100 * 2 / 9)
        self.assertAlmostEqual(x["risk_ratio"], 3)
        self.assertAlmostEqual(x["gap_group_fraction_of_later_non_detections"], 1 / 3)

    def test_no_mark_heterogeneity_means_no_selection_gap(self):
        x = MOD.discrete_selection_identity([0.7, 0.7], [0.4, 0.6])
        self.assertAlmostEqual(x["gap_minus_continuous_probability"], 0, places=12)
        self.assertAlmostEqual(x["later_non_detection_given_gap"], 0.3, places=12)

    def test_static_mark_heterogeneity_creates_selection_gap(self):
        x = MOD.discrete_selection_identity([0.95, 0.5], [0.5, 0.5])
        self.assertGreater(x["gap_minus_continuous_probability"], 0)
        self.assertAlmostEqual(
            x["gap_minus_continuous_probability"],
            x["variance_identity_rhs"],
            places=12,
        )

    def test_original_counts_are_not_reinterpreted_as_independent_sites(self):
        x = MOD.derive(fixture())
        o = x["observed_frozen_reaggregation"]
        self.assertEqual(o["gap_group_sequences"], 83)
        self.assertEqual(o["later_non_detections_gap_group"], 30)
        self.assertEqual(o["later_non_detections_uninterrupted"], 64)
        self.assertAlmostEqual(o["risk_ratio"], (30 / 83) / (64 / 497))
        self.assertIn("post", x["limits"][0].lower())

    def test_bad_source_fails_closed(self):
        for mutation in ("schema", "status", "events", "rounding"):
            x = fixture()
            if mutation == "schema":
                x["schema"] = "unknown"
            elif mutation == "status":
                x["status"] = "non_estimable"
            elif mutation == "events":
                x["registry"]["total_recorded_relosses"] = 95
            else:
                x["secondary"]["recovered_reloss_fraction"] = 0.36
            with self.assertRaises(ValueError):
                MOD.derive(x)

    def test_invalid_prior_fails(self):
        for a, b in ((0, 1), (-1, 1), (1, float("nan"))):
            with self.assertRaises(ValueError):
                MOD.beta_counterexample(a, b)


if __name__ == "__main__":
    unittest.main()
