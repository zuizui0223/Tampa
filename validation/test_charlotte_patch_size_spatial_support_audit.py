"""Synthetic, response-free regression tests of map class patch area common-support."""
import importlib.util, unittest
from pathlib import Path
from shapely.geometry import box,mapping

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("ch107",ROOT/"analysis/107_charlotte_patch_size_spatial_support_audit.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def row(i, group, area, retain, size, grid, code=9116):
    return {"fid":i,"code":code,"source_acres":area,
            "same_group_retained_acres":area*retain,
            "exact_code_retained_acres":area*retain,
            "size_bin":size,"grid_id":grid}

class MapPatchSupport(unittest.TestCase):
    def test_size_reference_uses_algae_area_weight_without_optimizing(self):
        groups={
         "seagrass":[row(i,"seagrass",2,.8,"2-10ac","A") for i in range(3)],
         "attached_macroalgae":[row(i+10,"attached_macroalgae",2,.2,"2-10ac","A",9121) for i in range(3)]
        }
        r=M._matched(groups,lambda x:x["size_bin"],3,1.)
        self.assertEqual(r["matched_n_cells"],1)
        self.assertEqual(r["algae_source_area_with_comparable_seagrass_percent"],100)
        self.assertEqual(r["weighted_mapped_same_class_persistence_percent"]["seagrass"],80)
        self.assertEqual(r["weighted_mapped_same_class_persistence_percent"]["attached_macroalgae"],20)
        self.assertEqual(r["weighted_seagrass_minus_algae_points"],60)
        self.assertTrue(r["can_generalize_to_full_algae_area"])

    def test_sparse_common_support_is_reported_not_rescued(self):
        groups={
         "seagrass":[row(i,"seagrass",5,.9,"2-10ac","A") for i in range(10)],
         "attached_macroalgae":[row(i+100,"attached_macroalgae",.2,.1,"lt0.5ac","B",9121) for i in range(4)]
        }
        r=M._matched(groups,lambda x:x["size_bin"],3,1.)
        self.assertEqual(r["matched_n_cells"],0)
        self.assertIsNone(r["weighted_seagrass_minus_algae_points"])
        self.assertEqual(r["algae_source_area_with_comparable_seagrass_percent"],0)
        self.assertFalse(r["can_generalize_to_full_algae_area"])

    def test_partial_coverage_not_extrapolated(self):
        groups={
          "seagrass":[row(i,"seagrass",2,.8,"2-10ac","A") for i in range(4)],
          "attached_macroalgae":(
              [row(i+50,"attached_macroalgae",2,.5,"2-10ac","A",9121) for i in range(3)]+
              [row(i+70,"attached_macroalgae",10,.1,"10-50ac","B",9121) for i in range(3)])
        }
        r=M._matched(groups,lambda x:x["size_bin"],3,1.)
        self.assertEqual(r["matched_n_cells"],1)
        self.assertAlmostEqual(r["algae_source_area_with_comparable_seagrass_percent"],16.667,places=2)
        self.assertEqual(r["weighted_seagrass_minus_algae_points"],30)
        self.assertFalse(r["can_generalize_to_full_algae_area"])

    def test_official_source_area_wins_over_visual_shape(self):
        g=box(-82.3,26.7,-82.29,26.71)
        area=M.G.transform(M.G.TRANSFORM,g).area/M.G.M2_PER_ACRE
        feature={"type":"Feature","properties":{"FID":5,"FLUCCSCODE":9116,
            "Geodesic":area},"geometry":mapping(g)}
        p,projected,a=M._props_geom(feature)
        self.assertEqual(p["FID"],5)
        self.assertAlmostEqual(a,area)
        feature["properties"]["Geodesic"]=area*2
        with self.assertRaisesRegex(M.Stop,"ORIGINAL_ACRE_FIELD_FAILED_INDEPENDENT_REVALIDATION"):
            M._props_geom(feature)

    def test_strict_original_seagrass_code_retention_is_also_reported(self):
        self.assertEqual(M.BINS[0],(0.,.5,"lt0.5ac"))
        self.assertEqual(M.GRID_M,5000)
        self.assertEqual(M.MIN_COVERAGE,.8)
        self.assertEqual(M.MIN_SIZE_N,3)
        self.assertEqual(M.MIN_CELL_N,2)

if __name__=="__main__":
    unittest.main()
