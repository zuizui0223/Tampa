"""Pure synthetic mapped-class stability checks: not a biological survival model."""
import importlib.util,unittest
from pathlib import Path
from shapely.geometry import box
p=Path(__file__).resolve().parents[1]/"analysis/106_charlotte_archived_map_class_retention.py"
s=importlib.util.spec_from_file_location("stability106",p)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)

class ClassStability(unittest.TestCase):
    def test_same_class_area_and_boundary_interiors(self):
        src={9113:box(0,0,100,100),9116:box(100,0,200,100),9121:box(200,0,300,100)}
        tgt={9113:box(0,0,90,100),9116:box(100,0,190,100),9121:box(210,0,290,100)}
        x=M.stability(src,tgt)
        self.assertEqual(x["classes"]["seagrass"]["boundary_interior_m"]["0"]["fixed_2022_source_area_retained_percent"],90)
        self.assertEqual(x["classes"]["attached_macroalgae"]["boundary_interior_m"]["0"]["fixed_2022_source_area_retained_percent"],80)
        self.assertEqual(x["seagrass_minus_algae_same_class_retention_percentage_points"],10)
        self.assertTrue(x["no_biological_survival_conclusion"])
        for cls in ("seagrass","attached_macroalgae"):
            d=x["classes"][cls]["boundary_interior_m"]
            self.assertGreater(d["0"]["same_class_overlap_acres"],d["10"]["same_class_overlap_acres"])
            self.assertGreaterEqual(d["10"]["same_class_overlap_acres"],d["25"]["same_class_overlap_acres"])
    def test_zero_area_for_algae_cannot_be_called_persistence(self):
        src={9113:box(0,0,100,100),9116:box(100,0,200,100),9121:box(0,0,0,0)}
        tgt={9113:box(0,0,100,100),9116:box(100,0,200,100),9121:box(210,0,290,100)}
        with self.assertRaisesRegex(M.Stop,"SOURCE_CLASS_EMPTY"):
            M.stability(src,tgt)
    def test_only_predeclared_distance_sensitivity(self):
        src={9113:box(0,0,100,100),9116:box(100,0,200,100),9121:box(200,0,300,100)}
        with self.assertRaisesRegex(M.Stop,"DISTANCES_CHANGED"):
            M.stability(src,src,distances=(0,8,10,25))
    def test_archive_is_immutable_and_not_external_prediction(self):
        self.assertEqual(M.FROZEN_SOURCE_ARCHIVE_RUN,44446913647)
        self.assertTrue(M.A.ARCHIVE_ZIP_DIGEST.startswith("sha256:fb22443b6d0"))
if __name__=="__main__":unittest.main()
