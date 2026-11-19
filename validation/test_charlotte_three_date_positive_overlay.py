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
    def test_historical_positive_coverage_must_be_compared_to_2022_seagrass(self):
        legacy=box(0,0,15,10)
        current={9113:box(0,0,10,10),9116:box(10,0,20,10),9121:box(10,0,20,10)}
        v=m.historic_positive_coverage_reference(legacy,current)
        self.assertEqual(v["class_specific"]["9113"]["overlaps_2016_mapped_seagrass_percent"],100)
        self.assertEqual(v["class_specific"]["9116"]["overlaps_2016_mapped_seagrass_percent"],50)
        self.assertEqual(v["class_specific"]["9121"]["overlaps_2016_mapped_seagrass_percent"],50)
        self.assertEqual(v["class_specific"]["2022_seagrass_combined"]["overlaps_2016_mapped_seagrass_percent"],75)
        self.assertEqual(v["algae_minus_seagrass_historical_positive_overlap_percentage_points"],-25)
        self.assertTrue(v["no_selection_or_legacy_significance_test"])
    def test_three_date_interior_overlap_monotonic(self):
        p16=box(0,0,100,100)
        a22=box(0,0,100,100)
        s24=box(0,0,50,100)
        a24=box(50,0,100,100)
        r=m.historical_interior_sensitivity(p16,a22,s24,a24)
        d=r["metre_inside_each_of_three_mapped_class_boundaries"]
        self.assertAlmostEqual(d["0"]["2024_seagrass_share_of_reduced_historical_algae_mask_percent"],50)
        self.assertGreater(d["0"]["2016_positive_and_2022_algae_interior_acres"],d["10"]["2016_positive_and_2022_algae_interior_acres"])
        self.assertGreater(d["10"]["2016_positive_and_2022_algae_interior_acres"],d["25"]["2016_positive_and_2022_algae_interior_acres"])
        self.assertTrue(r["not_positional_or_thematic_accuracy_correction"])
    def test_negative_interior_distance_fails(self):
        with self.assertRaisesRegex(m.M.GateStop,"NEGATIVE_BOUNDARY_DISTANCE"):
            m.historical_interior_sensitivity(box(0,0,100,100),box(0,0,100,100),box(0,0,100,100),box(0,0,0,0),distances=(-1,))
    def test_historical_only_positive_codes(self):
        self.assertEqual(m.EXPECTED_CLASS_COUNT,{"9113":954,"9116":428})
        self.assertTrue(m.BBOX_2022_2024["xmin"]<m.BBOX_2022_2024["xmax"])
if __name__=="__main__":unittest.main()
