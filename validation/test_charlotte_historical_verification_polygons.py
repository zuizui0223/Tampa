"""Synthetic tests for spatial field verification polygons, not site approval."""
import importlib.util,unittest
from pathlib import Path
from shapely.geometry import box
from pyproj import Transformer
p=Path(__file__).resolve().parents[1]/"analysis/101_charlotte_historical_verification_polygons.py"
s=importlib.util.spec_from_file_location("c101",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
cx,cy=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True).transform(-82.3,26.7)

class VerificationPolygons(unittest.TestCase):
    def test_realistic_core_no_access_or_causal_score(self):
        origin=box(cx,cy,cx+100,cy+100)
        sea=box(cx,cy,cx+50,cy+100)
        algae=box(cx+50,cy,cx+100,cy+100)
        features,s=m.candidate_components(origin,origin,sea,algae,distances=(10.0,))
        self.assertEqual(len(features),2)
        self.assertEqual({f["properties"]["class"] for f in features},
            {"2024_mapped_seagrass","2024_mapped_attached_algae"})
        for f in features:
            pr=f["properties"]
            self.assertGreaterEqual(pr["area_acres"],0.25)
            self.assertTrue(pr["not_official_field_site"])
            self.assertTrue(pr["field_access_and_permits_not_verified"])
            self.assertTrue(pr["not_restoration_priority_score"])
            self.assertTrue(-83.5<pr["representative_point_lon"]<-81.0)
            self.assertTrue(25<pr["representative_point_lat"]<28)
    def test_slivers_explicitly_excluded(self):
        origin=box(cx,cy,cx+30,cy+30)
        f,s=m.candidate_components(origin,origin,origin,box(cx+100,cy,cx+200,cy+100),
                                   distances=(10.0,))
        self.assertEqual(f,[])
        self.assertGreater(s["10m::2024_mapped_seagrass"]["excluded_sliver_acres"],0)
    def test_threshold_cannot_undercut_mapping_minimum(self):
        with self.assertRaisesRegex(m.M.M.GateStop,"INVALID_FIXED_FIELD_TRAINING_CRITERION"):
            m.candidate_components(box(cx,cy,cx+100,cy+100),box(cx,cy,cx+100,cy+100),
                                    box(cx,cy,cx+100,cy+100),box(cx+100,cy,cx+200,cy+100),
                                    min_acres=0.1)
if __name__=="__main__":unittest.main()
