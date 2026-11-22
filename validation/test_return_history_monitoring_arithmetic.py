"""No-network synthetic tests for descriptive return-history accounting."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'analysis' / '109_return_history_monitoring_arithmetic.py'
SPEC = importlib.util.spec_from_file_location('return_history_arithmetic', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    return {
        'schema': 'tampa.return_fragility_v1.canonical_summary',
        'status': 'return_fragility_supported',
        'registry': {
            'four_year_sequences': 580,
            'recovered_sequences': 83,
            'continuous_sequences': 497,
            'total_recorded_relosses': 94,
        },
        'secondary': {
            'recovered_reloss_fraction': 30 / 83,
            'continuous_reloss_fraction': 64 / 497,
        },
    }


class ReturnHistoryArithmeticTests(unittest.TestCase):
    def test_expected_risks_and_concentration(self):
        x = MODULE.derive(fixture())
        d = x['descriptive']
        self.assertAlmostEqual(d['relative_risk'], 2.806852409638554)
        self.assertAlmostEqual(d['absolute_risk_difference_percentage_points'], 23.267314731764078)
        self.assertAlmostEqual(d['event_concentration_ratio'], 2.230197385285824)
        self.assertEqual(x['denominators']['re_recorded_next_year_non_detections'], 30)
        self.assertEqual(x['denominators']['uninterrupted_next_year_non_detections'], 64)

    def test_incoherent_total_fails(self):
        x = fixture()
        x['registry']['total_recorded_relosses'] = 95
        with self.assertRaises(ValueError):
            MODULE.derive(x)

    def test_truncated_fractions_fail(self):
        x = fixture()
        x['secondary']['recovered_reloss_fraction'] = 0.36
        with self.assertRaises(ValueError):
            MODULE.derive(x)

    def test_status_and_schema_fail_closed(self):
        for key in ('status', 'schema'):
            x = fixture()
            x[key] = 'unexpected'
            with self.assertRaises(ValueError):
                MODULE.derive(x)


if __name__ == '__main__':
    unittest.main()
