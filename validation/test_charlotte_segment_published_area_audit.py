"""Synthetic and source-locked tests of official eight-subregion acreage labels."""
import importlib.util
from pathlib import Path
import unittest
root=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location("cs93",root/"analysis"/"93_charlotte_segment_published_area_audit.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
SRC=(root/"results/charlotte_segments_2022_2024_official_v1.csv").read_text()

class SegmentAudit(unittest.TestCase):
    def test_reported_real_values_and_rounding_disclosure(self):
        r=m.audit(SRC)
        self.assertEqual(r["source_rounded_total"]["reported_net_delta"],-893)
        self.assertEqual(r["sum_of_displayed_segment_2022"],14912)
        self.assertEqual(r["sum_of_displayed_segment_2024"],14020)
        self.assertEqual(r["sum_of_reported_segment_deltas"],-894)
        self.assertEqual(r["east_wall_north_decline_acres"],-270)
        self.assertEqual(r["myakka_river_reported_gain_acres"],12)
        self.assertEqual(r["top_three_reported_absolute_decline_segments"],
                         [("East Wall North",270),("Southern Charlotte",211),("West Wall",130)])
        self.assertAlmostEqual(r["share_of_reported_bay_net_loss_attributable_to_top_three_negative_deltas_percent"],68.42,places=2)
        self.assertTrue(r["one_acre_rounding_inconsistency_disclosed"])
    def test_source_value_change_refused(self):
        with self.assertRaisesRegex(ValueError,"PERCENT_CHANGE_SOURCE_DRIFT"):
            m.audit(SRC.replace("East Wall North,1593,1323,-270,-17",
                                "East Wall North,1593,1323,-270,-42"))
    def test_extra_segment_refused(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_SEGMENT_REGISTRY_DRIFT"):
            m.audit(SRC+SRC.splitlines()[1]+"\n")
    def test_scope_change_refused(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_ID_DRIFT"):
            m.audit(SRC.replace("SWFWMD_CHFI_20260311","OTHER_AGENCY",1))
if __name__=="__main__":unittest.main()
