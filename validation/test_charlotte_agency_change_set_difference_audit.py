"""Original-source GIS set-difference versus agency change-map semantic tests."""
import importlib.util, unittest
from pathlib import Path
from shapely.geometry import box,GeometryCollection

ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location(
    "source116", ROOT/"analysis/116_charlotte_agency_change_set_difference_audit.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)

def blank():return GeometryCollection()

class ChangeSetDifference(unittest.TestCase):
    def test_source_class_swaps_are_neither_gain_nor_loss(self):
        # Same 0..10 space is patchy seagrass in 2022, continuous in 2024.
        # Pure classification swap is not map addition/removal.
        old={9113:box(0,0,10,10),9116:blank(),9121:box(20,0,30,10)}
        newer={9113:blank(),9116:box(0,0,10,10),9121:box(30,0,40,10)}
        r=M.change_pieces(old,newer)
        self.assertAlmostEqual(r["gain"][9116].area,0,places=8)
        self.assertAlmostEqual(r["loss"][9113].area,0,places=8)
        self.assertAlmostEqual(r["gain"][9121].area,100,places=8)
        self.assertAlmostEqual(r["loss"][9121].area,100,places=8)
    def test_exact_agency_shapes_match_all_class_differences(self):
        old={9113:box(0,0,10,10),9116:blank(),9121:box(20,0,30,10)}
        newer={9113:blank(),9116:box(0,0,10,10),9121:box(30,0,40,10)}
        derived=M.change_pieces(old,newer)
        agency={role:{"geometries_by_class":dict(derived[role])} for role in ("gain","loss")}
        r=M.compare_shapes(derived,agency)
        self.assertTrue(all(r[role][str(code)]["geometric_equivalence_within_0_02_acres"]
                        for role in ("gain","loss") for code in M.CODES))
        self.assertEqual(r["gain"]["9121"]["source_agency_jaccard"],1)
    def test_same_total_area_different_location_does_not_match(self):
        pred={"gain":{9113:box(0,0,100,100),9116:blank(),9121:blank()},
              "loss":{9113:blank(),9116:blank(),9121:blank()}}
        agency={"gain":{"geometries_by_class":{9113:box(100,0,200,100),9116:blank(),9121:blank()}},
                "loss":{"geometries_by_class":{9113:blank(),9116:blank(),9121:blank()}}}
        r=M.compare_shapes(pred,agency)
        self.assertEqual(r["gain"]["9113"]["source_map_set_difference_acres"],
                         r["gain"]["9113"]["agency_change_source_acres"])
        self.assertEqual(r["gain"]["9113"]["source_agency_jaccard"],0)
        self.assertFalse(r["gain"]["9113"]["geometric_equivalence_within_0_02_acres"])
    def test_source_pins_are_previous_successful_not_fabricated(self):
        r=M.frozen_existing_source()
        self.assertEqual(r["gain"]["count"],832)
        self.assertEqual(r["loss"]["count"],767)
        self.assertEqual(r["gain"]["flucss_class_counts"]["9121"],132)
        self.assertEqual(r["loss"]["flucss_class_counts"]["9121"],53)

if __name__=="__main__":unittest.main()
