"""Synthetic source-only tests for official mapped change products, not ecology."""
import importlib.util,unittest
from pathlib import Path
S=importlib.util.spec_from_file_location("ch112",Path(__file__).resolve().parents[1]/"analysis/112_charlotte_official_gain_loss_source_gate.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class Fixture:
    def __init__(self,wrong=False,zero=False):
        self.wrong=wrong;self.zero=zero;self.calls=[]
    def __call__(self,url,params):
        self.calls.append((url,params))
        if url.endswith("/FeatureServer"):
            return {"layers":[{"id":1}],"serviceDescription":"2022–2024 map interpretation"}
        if url.endswith("/query"):
            return {"count":0 if self.zero else 15}
        return {"name":"2022–2024 gain/loss map",
                "type":"Table" if self.wrong else "Feature Layer",
                "geometryType":"esriGeometryPolygon",
                "objectIdField":"FID",
                "fields":[{"name":"FID","type":"esriFieldTypeOID"},
                          {"name":"ChangeType","type":"esriFieldTypeString"}],
                "extent":{"xmin":-9150000,"ymin":3080000,"xmax":-9130000,"ymax":3110000,
                          "spatialReference":{"latestWkid":3857}},
                "description":"Mapped class difference"}

class SourceMapAudit(unittest.TestCase):
    def test_only_metadata_and_counts_are_used(self):
        fetch=Fixture()
        r=M.inspect(fetch)
        self.assertEqual(r["status"],"PASS_MAP_CHANGE_GIS_SOURCE_METADATA_COUNTS_ONLY")
        self.assertEqual(r["records"]["mapped_seagrass_gain"]["official_polygon_count"],15)
        self.assertFalse(r["records"]["mapped_seagrass_loss"]["source_class_semantics_directly_verified"])
        self.assertFalse(r["records"]["mapped_seagrass_gain"]["evidence_is_independent_of_2022_2024_seagrass_maps"])
        self.assertTrue(r["no_geometry_downloaded"])
        self.assertTrue(all(p.get("returnGeometry")!="true" for _,p in fetch.calls))
    def test_wrong_geometry_type_stops(self):
        with self.assertRaisesRegex(M.Stop,"NOT_POLYGON"):
            M.inspect(Fixture(wrong=True))
    def test_no_features_stops(self):
        with self.assertRaisesRegex(M.Stop,"EMPTY_OR_INACCESSIBLE"):
            M.inspect(Fixture(zero=True))
    def test_source_pairs_frozen(self):
        self.assertEqual(set(M.SERVICES),{"mapped_seagrass_gain","mapped_seagrass_loss"})
        self.assertEqual(len(M.SERVICES),2)
if __name__=="__main__":unittest.main()
