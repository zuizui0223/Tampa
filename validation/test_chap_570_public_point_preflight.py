"""Synthetics for independent SEACAR 570 monitoring station public point registry."""
import importlib.util,unittest
from pathlib import Path
S=importlib.util.spec_from_file_location("ch121",Path(__file__).resolve().parents[1]/"analysis/121_chap_570_public_point_preflight.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class Stub:
    def __init__(self,bad=False,no_geometry=False):
        self.bad=bad;self.no_geometry=no_geometry;self.calls=[]
    def __call__(self,url,params):
        self.calls.append((url,params))
        if not url.endswith("/query"):
            return {"geometryType":"esriGeometryPolygon" if self.no_geometry else "esriGeometryPoint",
               "objectIdField":"OBJECTID_1",
               "fields":[{"name":"OBJECTID_1","type":"esriFieldTypeOID"},
                         {"name":"ProgramID","type":"esriFieldTypeInteger"},
                         {"name":"ProgramLocationID","type":"esriFieldTypeString"}],
               "extent":{"spatialReference":{"latestWkid":3857}}}
        if params.get("returnCountOnly"):
            return {"count":12 if params["where"]=="1=1" else 5}
        if params.get("returnIdsOnly"):
            return {"objectIds":[1,2,3,4,4 if self.bad else 5]}
        raise AssertionError("unexpected request")
class Tests(unittest.TestCase):
    def test_complete_station_schema_and_oids(self):
        source=Stub();r=M.audit(source)
        self.assertEqual(r["status"],"PASS_PUBLIC_CHAP_570_POINT_LAYER_AND_OID_INVENTORY_ONLY")
        self.assertEqual(r["count_program570_point_features"],5)
        self.assertFalse(r["original_quadrat_data_opened"])
        self.assertFalse(r["points_confirmed_current_2024_survey"])
        self.assertTrue(all(x.get("returnGeometry")!="true" for _,x in source.calls))
    def test_duplicate_oid_hard_stops(self):
        with self.assertRaisesRegex(M.Stop,"BAD_STATION_OID_ROSTER"):
            M.audit(Stub(bad=True))
    def test_non_point_layer_refused(self):
        with self.assertRaisesRegex(M.Stop,"NOT_POINT_LAYER"):
            M.audit(Stub(no_geometry=True))
    def test_program_identifiers_frozen(self):
        self.assertEqual(M.PROGRAM,570)
        self.assertIn("SEACAR_Datazoom/MapServer/179",M.URL)
if __name__=="__main__":unittest.main()
