"""Synthetic noncausal two giant-algae source polygon decomposition tests."""
import importlib.util,unittest
from pathlib import Path
S=importlib.util.spec_from_file_location("giants111",Path(__file__).resolve().parents[1]/"analysis/111_charlotte_two_giant_algae_patches.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)

def p(fid,area,algae,sea,unknown,historic):
    return {"source_2022_FID":fid,"source_algae_acres":area,
            "2024_same_attached_algae_acres":algae,
            "2024_mapped_seagrass_acres":sea,
            "2024_unmapped_area_acres":unknown,
            "2016_mapped_seagrass_positive_overlap_acres":historic}
class SourcePatchAudit(unittest.TestCase):
    def test_two_large_source_patches_area_closure(self):
        rows=[p(1,100,20,10,70,90),p(2,80,10,20,50,70)]
        a=M.summarize_patches(rows)
        self.assertEqual(a["source_algae_acres"],180)
        self.assertEqual(a["mapped_class_remains_algae_acres"],30)
        self.assertEqual(a["mapped_class_becomes_seagrass_acres"],30)
        self.assertEqual(a["mapped_class_unmapped_acres"],120)
        self.assertEqual(a["historical_2016_seagrass_positive_acres"],160)
        self.assertAlmostEqual(a["2024_same_algae_percent_of_source_area"],16.667,places=3)
    def test_classification_missing_not_forced_to_zero(self):
        x=M.summarize_patches([p(1,1,.1,0,.9,.5)])
        self.assertEqual(x["mapped_class_unmapped_acres"],.9)
    def test_nonclosed_row_rejected(self):
        with self.assertRaisesRegex(M.Stop,"PATCH_SUMMARY_AREA_NOT_CLOSED"):
            M.summarize_patches([p(3,10,1,1,1,5)])
    def test_historical_overlap_outside_source_rejected(self):
        with self.assertRaisesRegex(M.Stop,"HISTORIC_OVERLAP_OUTSIDE_PATCH_SET"):
            M.summarize_patches([p(3,10,1,1,8,11)])
    def test_no_patches_stops(self):
        with self.assertRaisesRegex(M.Stop,"EMPTY_PATCH_SET"):
            M.summarize_patches([])
    def test_source_and_large_patch_threshold_frozen(self):
        self.assertEqual(M.EXPECTED_SOURCE_ALGAE_POLYGONS,95)
        self.assertEqual(M.EXPECTED_LARGE_COUNT,2)
        self.assertEqual(M.LARGE_ACRES,50)
if __name__=="__main__":
    unittest.main()
