"""Synthetic far-interior geometry tests; no fabricated ecological absence."""
import importlib.util,unittest
from pathlib import Path
from shapely.geometry import box,GeometryCollection
S=importlib.util.spec_from_file_location("ch118",Path(__file__).resolve().parents[1]/"analysis/118_charlotte_giant_unmapped_core_depth.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)

class FarUnmapped(unittest.TestCase):
    def test_no_2024_classes_leaves_deep_2022_interior(self):
        p=box(0,0,500,500)
        absent=GeometryCollection()
        historic=box(0,0,500,500)
        unknown,rows=M.classified_distance(p,absent,historic)
        self.assertEqual(unknown.area,250000)
        self.assertAlmostEqual(
            rows["25"]["unmapped_area_both_boundaries_interior_acres"],
            450*450/M.AC,places=3)
        self.assertAlmostEqual(
            rows["100"]["unmapped_area_both_boundaries_interior_acres"],
            300*300/M.AC,places=3)
        self.assertAlmostEqual(rows["0"]["fraction_interior_also_2016_seagrass_positive_percent"],100)
        self.assertGreater(rows["50"]["unmapped_area_both_boundaries_interior_acres"],
                           rows["100"]["unmapped_area_both_boundaries_interior_acres"])
    def test_same_year_2024_cover_produces_no_unmapped(self):
        with self.assertRaisesRegex(M.Stop,"UNMAPPED_AREA_MISSING"):
            M.classified_distance(box(0,0,500,500),box(0,0,500,500),box(0,0,500,500))
    def test_mapped_2024_patch_blocks_far_interior(self):
        p=box(0,0,300,300)
        mapped=box(150,0,200,300)
        original,rows=M.classified_distance(p,mapped,p)
        self.assertAlmostEqual(original.area,75000)
        self.assertLess(rows["25"]["unmapped_area_both_boundaries_interior_acres"],
                        rows["0"]["unmapped_area_both_boundaries_interior_acres"])
        self.assertLess(rows["50"]["unmapped_area_both_boundaries_interior_acres"],
                        rows["25"]["unmapped_area_both_boundaries_interior_acres"])
    def test_partial_historical_footprint_is_not_assumed_everywhere(self):
        p=box(0,0,400,400)
        historic=box(0,0,200,400)
        _,rows=M.classified_distance(p,GeometryCollection(),historic)
        self.assertAlmostEqual(rows["0"]["fraction_interior_also_2016_seagrass_positive_percent"],50,places=3)
    def test_thresholds_frozen(self):
        with self.assertRaisesRegex(M.Stop,"DISTANCES_CHANGED"):
            M.classified_distance(box(0,0,300,300),GeometryCollection(),box(0,0,300,300),distances=(0,10,20))
    def test_not_a_field_permit_or_recovery_measure(self):
        self.assertEqual(M.FIDS,(37,2166))
        self.assertEqual(M.MMU_AC,.25)
        self.assertEqual(M.THRESHOLDS,(0.,5.,10.,25.,50.,100.))
if __name__=="__main__":unittest.main()
