"""No-source synthetic tests for public GIS category-transition math."""
import importlib.util
import unittest
from pathlib import Path

from shapely.geometry import box,mapping

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("ch92",ROOT/"analysis"/"92_charlotte_public_gis_class_transitions.py")
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class SpatialTests(unittest.TestCase):
    def test_transition_matrix_and_unmapped_are_not_extinction(self):
        src={9113:box(0,0,10,10),9116:box(10,0,20,10),9121:box(20,0,30,10)}
        tgt={9113:box(20,0,25,10),9116:box(0,0,10,10),
             9121:box(10,0,15,10)}
        result=M.transitions(src,tgt)
        self.assertEqual(result["9121"]["target_fraction_percent"]["9113"],50)
        self.assertEqual(result["9121"]["target_fraction_percent"]["unmapped"],50)
        self.assertEqual(result["9116"]["target_fraction_percent"]["9121"],50)
        self.assertEqual(result["9113"]["target_fraction_percent"]["9116"],100)
        self.assertEqual(result["9113"]["target_fraction_percent"]["unmapped"],0)
    def test_transition_fails_overlapping_target_classes(self):
        src={9113:box(0,0,10,10),9116:box(10,0,20,10),9121:box(20,0,30,10)}
        tgt={9113:box(20,0,30,10),9116:box(20,0,30,10),
             9121:box(0,0,2,2)}
        with self.assertRaisesRegex(M.GateStop,"NOT_CLOSED"):
            M.transitions(src,tgt)
    def test_equal_area_prepare_does_not_confuse_polygon_count_with_area(self):
        polys=[
         {"properties":{"FLUCCSCODE":c},
          "geometry":mapping(box(-82.3+i*0.025,26.7,-82.3+i*0.025+0.01,26.71))}
         for i,c in enumerate((9113,9116,9121))]
        for poly in polys:
            poly["properties"]["ACRES"]=M.transform(M.TRANSFORM,M.shape(poly["geometry"])).area/M.M2_PER_ACRE
        union,qc=M.prepare(polys,"ACRES")
        self.assertEqual(qc["polygon_count"],3)
        self.assertEqual(qc["invalid_repaired"],0)
        self.assertEqual(qc["within_year_overlap_fraction"],0)
        self.assertTrue(all(v.area>0 for v in union.values()))
        self.assertGreater(qc["class_area_acres"]["9121"],0)
    def test_independent_original_acre_attribute_catches_wrong_hole_area(self):
        g=mapping(box(-82.3,26.7,-82.29,26.71))
        polys=[{"properties":{"FLUCCSCODE":9113,"FID":99,"ACRES":0.001},"geometry":g}]
        with self.assertRaisesRegex(M.GateStop,"VALIDATED_AREA_MISMATCH"):
            M.prepare(polys,"ACRES")
    def test_invalid_coordinates_stop(self):
        polys=[{"properties":{"FLUCCSCODE":9113},
                "geometry":mapping(box(-120,45,-119,46))}]
        with self.assertRaisesRegex(M.GateStop,"OUTSIDE_CHARLOTTE"):
            M.prepare(polys,"ACRES")
    def test_duplicate_id_inventory_rejected(self):
        def fetch(url,params):
            if url.endswith("/query"):
                if params.get("returnCountOnly"):return {"count":2}
                if params.get("returnIdsOnly"):return {"objectIds":[1,1]}
            return {"fields":[{"name":"FLUCCSCODE","type":"esriFieldTypeInteger"},
                              {"name":"Geodesic","type":"esriFieldTypeDouble"}],
                    "geometryType":"esriGeometryPolygon","objectIdField":"FID"}
        with self.assertRaisesRegex(M.GateStop,"BAD_OBJECTID_LIST"):
            M.download_year("2022",fetch)
    def test_unsupported_class_rejected(self):
        def fetch(url,params):
            if url.endswith("/query"):
                if params.get("returnCountOnly"):return {"count":3}
                if params.get("returnIdsOnly"):return {"objectIds":[1,2,3]}
                return {"type":"FeatureCollection","features":[
                  {"properties":{"FID":i,"FLUCCSCODE":c}, "geometry":mapping(box(-82.3,26.7,-82.29,26.71))}
                  for i,c in zip((1,2,3),(9113,9116,9900))]}
            return {"fields":[{"name":"FLUCCSCODE","type":"esriFieldTypeInteger"},
                              {"name":"Geodesic","type":"esriFieldTypeDouble"}],
                    "geometryType":"esriGeometryPolygon","objectIdField":"FID"}
        with self.assertRaisesRegex(M.GateStop,"UNAPPROVED_CLASS_CODE"):
            M.download_year("2022",fetch)

if __name__=="__main__":
    unittest.main()
