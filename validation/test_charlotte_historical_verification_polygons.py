"""Synthetic tests for spatial field verification polygons, not site approval."""
import importlib.util,unittest
from pathlib import Path
from shapely.geometry import box,mapping
from shapely.ops import transform
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
    def test_export_is_actual_geojson_feature_collection(self):
        def feature(geom,cls,fid,area_field):
            geo=mapping(transform(m.REVERSE,geom))
            acres=geom.area/m.M.M.M2_PER_ACRE
            return {"type":"Feature","properties":{"FLUCCSCODE":cls,"FID":fid,area_field:acres},
                    "geometry":geo}
        old=box(cx,cy,cx+100,cy+100)
        sea=box(cx,cy,cx+50,cy+100)
        alg=box(cx+50,cy,cx+100,cy+100)
        d16={"features":[feature(old,9116,1,"ACRES")],"source_oids_sha256":"X"}
        d22={"features":[feature(old,9121,2,"Geodesic")],"oid_inventory_sha256":"Y"}
        d24={"features":[feature(sea,9116,3,"ACRES"),feature(alg,9121,4,"ACRES")],
             "oid_inventory_sha256":"Z"}
        r=m.analyze(d16,d22,d24)
        self.assertEqual(r["type"],"FeatureCollection")
        self.assertEqual(r["status"],"SOURCE_MAPPED_VERIFICATION_LOCATIONS_NOT_FIELDPERMITS")
        self.assertTrue(r["features"])
        self.assertTrue(all(f["type"]=="Feature" and f["geometry"]["type"] in ("Polygon","MultiPolygon")
                            for f in r["features"]))
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
