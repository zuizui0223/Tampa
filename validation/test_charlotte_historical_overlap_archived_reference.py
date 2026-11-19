"""Response-free tests for the source-archived 2016 overlap reference replay."""
import importlib.util, json, tempfile, unittest
from pathlib import Path
from shapely.geometry import box

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("ch102",ROOT/"analysis/102_charlotte_historical_overlap_archived_reference.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

class HistoricalSourceReference(unittest.TestCase):
    def test_committed_authoritative_source_pin(self):
        r=M.load_frozen_report()
        self.assertEqual(r["historical_source"]["exact_source_ids"],1382)
        self.assertEqual(r["modern_source"]["2022"]["oid_count"],2303)
        self.assertEqual(r["map_history"]["2016_seagrass_positive_share_of_2022_algae_percent"],92.979)
    def test_no_archive_file_stops(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(M.Stop,"ARCHIVE_FILE_NOT_UNIQUE"):
                M.load_source_features(td,"2016","0"*64,1382)
    def test_unverified_features_hash_stops(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/M.SOURCES["2022"]
            f={"type":"FeatureCollection","features":[{"properties":{"FID":1,"FLUCCSCODE":9113},
              "type":"Feature","geometry":{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}}]}
            file.write_text(json.dumps(f),encoding="utf-8")
            with self.assertRaisesRegex(M.Stop,"ARCHIVED_RAW_FEATURE_SHA_DRIFT"):
                M.load_source_features(td,"2022","0"*64,1)
    def test_wrong_count_hard_stop_before_calculation(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/M.SOURCES["2016"]
            file.write_text(json.dumps({"type":"FeatureCollection","features":[]}))
            with self.assertRaisesRegex(M.Stop,"ARCHIVED_FEATURE_COUNT_DRIFT"):
                M.load_source_features(td,"2016","0"*64,1382)
    def test_baseline_prevents_automatic_special_history_claim(self):
        s=box(0,0,100,100)
        pools={9113:s,9116:box(100,0,200,100),9121:box(0,0,100,100)}
        old=s
        r=M.M.historic_positive_coverage_reference(old,pools)
        self.assertEqual(r["class_specific"]["9121"]["overlaps_2016_mapped_seagrass_percent"],100)
        self.assertEqual(r["class_specific"]["2022_seagrass_combined"]["overlaps_2016_mapped_seagrass_percent"],50)
        self.assertFalse(r["no_selection_or_legacy_significance_test"] is False)
    def test_pinned_archive_not_user_supplied(self):
        self.assertEqual(M.ARCHIVE_RUN_ID,44446913647)
        self.assertEqual(M.ARCHIVE_ID,14494425181)
        self.assertTrue(M.ARCHIVE_ZIP_DIGEST.startswith("sha256:fb22443b6d0b8bf1a"))
if __name__=="__main__":unittest.main()
