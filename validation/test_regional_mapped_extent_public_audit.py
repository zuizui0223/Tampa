"""Source-bound deterministic mapped-acreage audit tests. No field/water chemistry data."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("extent90",ROOT/"analysis/90_regional_mapped_extent_public_audit.py")
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
CSV=(ROOT/"results/regional_extent_public_sources_v1.csv").read_text(encoding="utf-8")
REGISTRY=json.loads((ROOT/"results/regional_extent_public_sources_v1_registry.json").read_text(encoding="utf-8"))

class SourceAudit(unittest.TestCase):
    def test_reproduces_same_source_decline_and_divergence(self):
        r=M.evaluate(CSV,REGISTRY)
        self.assertTrue(r["shared_2018_to_2020_decline"])
        self.assertEqual(r["2022_to_2024_recovery_direction"],{
            "Tampa Bay":"increase", "Charlotte Harbor":"decline",
            "Sarasota Bay":"increase"})
        self.assertEqual(r["primary"]["Charlotte Harbor"]["2016_to_2024"]["delta_acres"],-6260)
        self.assertEqual(r["primary"]["Tampa Bay"]["2018_to_2020"]["delta_acres"],-6355)
        self.assertEqual(r["primary"]["Sarasota Bay"]["2022_to_2024"]["delta_acres"],1913)
        self.assertEqual(r["alternate_chnep_distinct_spatial_scope"]["swfwmd_minus_chnep_acres_same_year"]["2016"],2951)
        self.assertEqual(r["alternate_chnep_distinct_spatial_scope"]["text_minus_chart_loss_acres"],65)
        self.assertTrue(r["not_untouched_prediction"])

    def test_source_anchor_tamper_fails(self):
        bad=CSV.replace('SWFWMD_2026,"Charlotte Harbor",2024,14020', 'SWFWMD_2026,"Charlotte Harbor",2024,14021')
        self.assertNotEqual(CSV,bad)
        with self.assertRaisesRegex(ValueError,"source anchor drift"): M.evaluate(bad,REGISTRY)

    def test_duplicate_year_fails(self):
        bad=CSV+"SWFWMD_2026,Tampa Bay,2024,31562,SWFWMD_2026\n"
        with self.assertRaisesRegex(ValueError,"duplicated year"): M.evaluate(bad,REGISTRY)

    def test_unverified_source_id_fails(self):
        bad=CSV.replace('SWFWMD_2026,"Tampa Bay",2016,41655,SWFWMD_2026',
                        'SWFWMD_2026,"Tampa Bay",2016,41655,CHNEP_FACTSHEET_2023')
        with self.assertRaisesRegex(ValueError,"mixed series"): M.evaluate(bad,REGISTRY)

    def test_missing_registry_source_fails(self):
        bad=dict(REGISTRY)
        bad["sources"]={"SWFWMD_2026":REGISTRY["sources"]["SWFWMD_2026"]}
        with self.assertRaisesRegex(ValueError,"registry not exact"):M.evaluate(CSV,bad)

    def test_missing_required_2024_fails(self):
        bad="\n".join(x for x in CSV.splitlines()
                     if '"Charlotte Harbor",2024,14020' not in x)+"\n"
        with self.assertRaisesRegex(ValueError,"source anchor drift"):M.evaluate(bad,REGISTRY)

if __name__=="__main__":
    unittest.main()
