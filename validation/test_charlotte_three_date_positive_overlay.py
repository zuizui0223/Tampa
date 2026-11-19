"""2016-positive-only three-date geometry claim-boundary synthetic tests."""
import importlib.util,unittest
from pathlib import Path
from shapely.geometry import box
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ch100",root/"analysis/100_charlotte_2016_2022_2024_positive_only_overlay.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TriplePositiveOnly(unittest.TestCase):
    def test_only_confirmed_2016_positive_area_enters_history(self):
        p16=box(0,0,10,10)
        a22=box(0,0,20,10)
        sea24=box(0,0,5,10)
        algae24=box(5,0,20,10)
        r=m.masked_overlap(p16,box(0,20,20,30),a22,sea24,algae24)
        self.assertEqual(r["2016_seagrass_positive_share_of_2022_algae_percent"],50)
        self.assertEqual(r["2016_positive_2022_algae_to_2024_class_fraction_percent"]["seagrass"],50)
        self.assertTrue(r["not_positive_2016_is_not_verified_2016_absence"])
    def test_unmapped_target_not_called_bare(self):
        r=m.masked_overlap(box(0,0,10,10),box(0,20,20,30),
                           box(0,0,20,10),box(0,0,2,10),
                           box(3,0,4,10))
        self.assertEqual(r["2016_positive_2022_algae_to_2024_class_fraction_percent"]["unmapped"],70)
    def test_no_2022_algae_fails(self):
        with self.assertRaisesRegex(m.M.GateStop,"2022_ALGAE_AREA_EMPTY"):
            m.masked_overlap(box(0,0,1,1),box(0,0,1,1),
                             box(0,0,0,0),box(0,0,1,1),box(0,0,1,1))
    def test_historical_only_positive_codes(self):
        self.assertEqual(m.EXPECTED_CLASS_COUNT,{"9113":954,"9116":428})
        self.assertTrue(m.BBOX_2022_2024["xmin"]<m.BBOX_2022_2024["xmax"])
if __name__=="__main__":unittest.main()
