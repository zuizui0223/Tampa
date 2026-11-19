"""Source-only tests of original District 2024 MapServer all-class dictionary gate."""
import importlib.util, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"analysis/125_charlotte_2024_district_original_full_class_preflight.py"
sp=importlib.util.spec_from_file_location("ch125",P)
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
BBOX={"xmin":-9159637.622929975,"ymin":3085497.118059525,
      "xmax":-9133636.733688185,"ymax":3115537.8056237204}
CODES={"9113":7,"9116":3,"9121":2,"0":4,"5400":5,"6510":1}
def reference():
    return BBOX, "pinned-original-envelope-sha"

class Stub:
    def __init__(self,bad_year=False,bad_closure=False):
        self.bad_year=bad_year;self.bad_closure=bad_closure;self.calls=[]
    def __call__(self,url,params):
        self.calls.append((url,params))
        if url==M.LAYER:
            return {
              "name":"Seagrass in 2022" if self.bad_year else "Seagrass in 2024",
              "geometryType":"esriGeometryPolygon",
              "objectIdField":None,
              "fields":[
                {"name":"OBJECTID","type":"esriFieldTypeOID"},
                {"name":"FLUCCSCODE","type":"esriFieldTypeInteger"},
                {"name":"FLUCCSDESC","type":"esriFieldTypeString"},
                {"name":"ACRES","type":"esriFieldTypeDouble"}],
              "extent":{"spatialReference":{"wkid":2882}}}
        if url.endswith("/query"):
            if params.get("groupByFieldsForStatistics"):
                counts=dict(CODES)
                if self.bad_closure:counts["0"]+=1
                return {"features":[
                  {"attributes":{"FLUCCSCODE":int(k),"n":v}}
                  for k,v in counts.items()]}
            if params.get("returnCountOnly"):
                where=params["where"]
                if where=="1=1":return {"count":sum(CODES.values())}
                return {"count":CODES.get(where.split("=")[-1],0)}
        raise AssertionError("Unexpected original source request")

class OriginalFullClass(unittest.TestCase):
    def test_all_background_codes_reported_without_geometry(self):
        stub=Stub();r=M.inspect(stub,reference)
        self.assertEqual(r["status"],"PASS_OFFICIAL_2024_ORIGINAL_DISTRICT_YEAR_CODE_DICTIONARY_ONLY")
        self.assertTrue(r["contains_background_benthic_map_categories"])
        self.assertEqual(r["n_source_polygons_of_other_classes"],10)
        self.assertEqual(r["exhaustive_original_source_code_counts"]["5400"],5)
        self.assertEqual(r["source_oid_field_typed"],"OBJECTID")
        self.assertIsNone(r["source_oid_field_advertised"])
        self.assertFalse(r["giant_unmapped_habitat_state_identified"])
        self.assertFalse(r["source_2024_full_survey_footprint_confirmed"])
        self.assertTrue(r["no_geometry_downloaded"])
        self.assertTrue(all(p.get("returnGeometry")!="true" for _,p in stub.calls))
    def test_changed_layer_year_hard_stop(self):
        with self.assertRaisesRegex(M.Stop,"NOT_2024_ORIGINAL_DISTRICT_POLYGON_LAYER"):
            M.inspect(Stub(bad_year=True),reference)
    def test_category_count_nonclosure_hard_stop(self):
        with self.assertRaisesRegex(M.Stop,"CLASS_COUNT_MASS_NONCLOSURE"):
            M.inspect(Stub(bad_closure=True),reference)
    def test_live_class_code_is_not_assumed_bare(self):
        self.assertIn("5400",M.KNOWN)
        self.assertEqual(M.HOSTED,{"9113":2087,"9116":912,"9121":210})
        self.assertTrue(M.LAYER.endswith("/3"))
if __name__=="__main__":unittest.main()
