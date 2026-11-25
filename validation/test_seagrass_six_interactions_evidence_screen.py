"""No-network, source-locked interaction registry and published-arithmetic tests."""
from __future__ import annotations
import importlib.util
import math
import tempfile
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"116_seagrass_six_interactions_evidence_screen.py"
SPEC=importlib.util.spec_from_file_location("six_interactions",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class TestSixInteractions(unittest.TestCase):
    def test_all_six_hypotheses_have_real_sources(self):
        rs=M.records_from_registry()
        self.assertGreaterEqual(len(rs),12)
        self.assertEqual({r["arm"] for r in rs},set(M.FAMILIES))
        self.assertEqual(len({r["study_id"] for r in rs}),len(rs))

    def test_report_is_descriptive_not_meta(self):
        x=M.report()
        self.assertEqual(x["status"],"bounded_exploratory_source_evidence_not_pooled_meta_analysis")
        self.assertEqual(len(x["family_inventory"]),6)
        self.assertEqual(len(x["published_numeric_rechecks"]),5)

    def test_chi_square_df2_published_caption_discrepancy(self):
        x=M.compare_chi2_from_original_paper()
        self.assertAlmostEqual(x["p_value_standard_chi_square_recomputed"],math.exp(-4.63))
        self.assertFalse(x["reported_p_matches_df_and_statistic"])
        self.assertTrue(x["qualitative_p_less_than_0_05_unchanged"])

    def test_rhodolith_sediment_arithmetic_without_pseudoreplication(self):
        x=M.original_rhodolith_report()
        self.assertAlmostEqual(x["outside_to_inside_mean_ratio"],4.182)
        self.assertAlmostEqual(x["outside_minus_inside_g"],.1591)

    def test_lucinid_published_meta_not_fresh_meta(self):
        x=M.published_lucinid_global()
        self.assertEqual(x["previous_meta_studies"],84)
        self.assertEqual(x["tropical_minus_temperate_percentage_points"],41)
        self.assertIsNone(x["new_95pct_ci"])

    def test_tampa_epiphyte_source_including_2016_is_null(self):
        x=M.tampa_existing_sensitivities()
        b=x["tampa_epiphyte"]
        self.assertAlmostEqual(b["unadjusted_grade3_minus_grade0_percentage_points"],100*(.8605769230769231-.7468354430379747))
        self.assertFalse(b["mechanism_supported"])
        self.assertLess(b["target_2016_included_adjusted_within_node_ci95"][0],0)

    def test_tampa_community_node_adjusted_interval_crosses_zero(self):
        x=M.tampa_existing_sensitivities()["tampa_seagrass_mixture"]
        self.assertFalse(x["mechanism_supported"])
        a,b=x["node_centered_binary_mixture_ci95"]
        self.assertLess(a,0)
        self.assertGreater(b,0)

    def test_bad_curation_fails_closed(self):
        rows=M.records_from_registry()
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"bad.csv"
            import csv
            with p.open("w",encoding="utf-8",newline="") as h:
                w=csv.DictWriter(h,fieldnames=M.REQUIRED)
                w.writeheader()
                for r in rows:
                    x=r.copy()
                    if x["study_id"]=="van_der_heide_2012":
                        x["arm"]="made_up_family"
                    w.writerow(x)
            with self.assertRaises(ValueError):
                M.records_from_registry(p)

if __name__=="__main__":
    unittest.main()
