"""Geometry-only synthetic verification of CHAP public station proximity, not data on visits."""
from pathlib import Path
import importlib.util,unittest
from shapely.geometry import box,GeometryCollection
s=importlib.util.spec_from_file_location("ch122",Path(__file__).resolve().parents[1]/"analysis/122_chap570_public_station_giant_proximity.py")
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
class Tests(unittest.TestCase):
    def test_point_on_source_and_near_distance(self):
        p=[{"oid":1,"id":"a","x_utm17n":0,"y_utm17n":0},
           {"oid":2,"id":"b","x_utm17n":1000,"y_utm17n":0},
           {"oid":3,"id":"c","x_utm17n":2000,"y_utm17n":0}]
        r=M.proximity(p,{"target":box(0,0,10,10)})
        x=r["target"]
        self.assertEqual(x["min_distance_to_registered_public_station_metres"],0)
        self.assertEqual(x["public_point_counts_within_radius_metres"]["250"],1)
        self.assertEqual(x["public_point_counts_within_radius_metres"]["1000"],2)
        self.assertEqual(x["public_point_counts_within_radius_metres"]["2000"],3)
        self.assertTrue(x["no_annual_field_visit_or_quadrat_measurement_retrieved"])
    def test_closest_ever_public_point_not_an_annual_visit(self):
        r=M.proximity([{"oid":5,"id":"public","x_utm17n":0,"y_utm17n":0}],
                      {"missing":box(100,0,200,100)})
        q=r["missing"]["nearest_public_station_point_ids"][0]
        self.assertTrue(q["station_point_not_a_verifed_2024_survey"])
        self.assertEqual(q["distance_metres"],100)
    def test_empty_mask_or_station_gate(self):
        with self.assertRaisesRegex(M.Stop,"NO_VERIFIED_PUBLIC_STATION_POINTS"):
            M.proximity([],{"target":box(0,0,10,10)})
        with self.assertRaisesRegex(M.Stop,"MAPPED_UNKNOWN_ZONE_INVALID"):
            M.proximity([{"oid":1,"x_utm17n":0,"y_utm17n":0}],{"empty":GeometryCollection()})
    def test_duplicate_registry_oid_hard_stops(self):
        points=[{"oid":1,"x_utm17n":0,"y_utm17n":0},
                {"oid":1,"x_utm17n":30,"y_utm17n":30}]
        with self.assertRaisesRegex(M.Stop,"DUPLICATE_PUBLIC_STATION_OIDS"):
            M.proximity(points,{"zone":box(0,0,10,10)})
    def test_fixed_public_source_program_and_distance_thresholds(self):
        self.assertEqual(M.EXPECTED_POINTS,63)
        self.assertEqual(M.PROGRAM,570)
        self.assertEqual(M.RADII,(0,250,500,1000,2000,5000))
        self.assertEqual(M.OID,"OBJECTID_1")
if __name__=="__main__":unittest.main()
