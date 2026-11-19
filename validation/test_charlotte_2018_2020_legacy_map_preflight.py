"""Synthetic source-only tests for official 2018/2020 legacy seagrass mapping layers."""
import importlib.util,unittest
from pathlib import Path
S=importlib.util.spec_from_file_location("ch110",Path(__file__).resolve().parents[1]/"analysis/110_charlotte_2018_2020_legacy_map_preflight.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
BOUNDS={"xmin":-9159637.622929975,"ymin":3085497.118059525,"xmax":-9133636.733688185,"ymax":3115537.8056237204}
def pinned():return BOUNDS,"fixture_sha"
class API:
    def __init__(self,wrong=False,empty=False):self.wrong=wrong;self.empty=empty;self.calls=[]
    def __call__(self,url,params):
        self.calls.append((url,params))
        year="2018" if url.split("FeatureServer/")[1].split("/")[0]=="0" else "2020"
        if url.endswith("/query"):
            where=params["where"]
            if where=="1=1":return {"count":5}
            cls=int(where.split("=")[1])
            d={9113:3,9116:2,9121:0} if year=="2018" else {9113:2,9116:2,9121:1}
            if self.empty and year=="2020":d={9113:3,9116:2,9121:0}
            return {"count":d[cls]}
        return {"name":"Seagrass in "+("2022" if self.wrong else year),
            "type":"Feature Layer","geometryType":"esriGeometryPolygon",
            "objectIdField":"OBJECTID","fields":[
             {"name":"OBJECTID","type":"esriFieldTypeOID"},
             {"name":"FLUCCSCODE","type":"esriFieldTypeInteger"},
             {"name":"FLUCCSDESC","type":"esriFieldTypeString"},
             {"name":"Shape__Area","type":"esriFieldTypeDouble"}],
            "extent":{"spatialReference":{"wkid":2882}}}
class PreflightTest(unittest.TestCase):
    def test_independent_years_and_zero_class_preserved(self):
        api=API()
        out=M.collect(api,pinned)
        self.assertEqual(out["status"],"PASS_OFFICIAL_LEGACY_MAP_METADATA_AND_CLASS_COUNTS_ONLY")
        self.assertEqual(out["years"]["2018"]["n_by_focal_legacy_flucss_code"]["9121"],0)
        self.assertEqual(out["years"]["2020"]["n_by_focal_legacy_flucss_code"]["9121"],1)
        self.assertFalse(out["years"]["2018"]["algae_map_class_supported"])
        self.assertTrue(out["no_feature_geometries_opened"])
        self.assertTrue(all(p.get("returnGeometry")!="true" for _,p in api.calls))
    def test_both_years_zero_are_not_replaced(self):
        out=M.collect(API(empty=True),pinned)
        self.assertFalse(out["years"]["2020"]["algae_map_class_supported"])
    def test_date_mismatch_fails_closed(self):
        with self.assertRaisesRegex(M.Stop,"SOURCE_YEAR_OR_POLYGON_IDENTITY_DRIFT"):
            M.collect(API(wrong=True),pinned)
    def test_negative_other_count_refused(self):
        class Bad(API):
            def __call__(self,url,params):
                d=super().__call__(url,params)
                if url.endswith("/query") and params.get("where")=="1=1":return {"count":1}
                return d
        with self.assertRaisesRegex(M.Stop,"FOCAL_CLASS_COUNTS_EXCEED"):
            M.collect(Bad(),pinned)
    def test_spatial_envelope_stays_source_locked(self):
        self.assertEqual(M.LAYERS,{"2018":0,"2020":1})
        self.assertEqual(set(M.CLASSES),{9113,9116,9121})
if __name__=="__main__":unittest.main()
