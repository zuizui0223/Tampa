"""Synthetic-only categorical and provenance contract test (no ArcGIS network)."""
import importlib.util
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"analysis"/"91_charlotte_arcgis_source_preflight.py"
S=importlib.util.spec_from_file_location("charlotte_gis91",P)
M=importlib.util.module_from_spec(S)
S.loader.exec_module(M)

def metadata(year,changes=None):
    d={"type":"Feature Layer","name":f"CH {year}",
       "geometryType":"esriGeometryPolygon","objectIdField":"FID",
       "maxRecordCount":2000,"editingInfo":{"lastEditDate":123},
       "extent":{"xmin":-9159637.0,"xmax":-9134080.0,"ymin":3085497.0,
                 "ymax":3115537.0,"spatialReference":{"wkid":102100}},
       "fields":[{"name":"FID","type":"esriFieldTypeOID"},
                 {"name":"FLUCCSCODE","type":"esriFieldTypeInteger"},
                 {"name":"FLUCCSDESC","type":"esriFieldTypeString"}]}
    if changes:d.update(changes)
    return d

def fake_fetch(url,params):
    year="2022" if "2022" in url else "2024"
    if url.endswith("/query"):
        v=params.get("where")
        return {"count":{ "1=1":8,"FLUCCSCODE=9113":3,
                          "FLUCCSCODE=9116":4,"FLUCCSCODE=9121":1}[v]}
    return metadata(year)

class SourcePreflightTest(unittest.TestCase):
    def test_pass_is_count_only(self):
        out=M.inventory(fake_fetch)
        self.assertEqual(out["access_status"],"PASS_METADATA_AND_COUNTS_ONLY")
        self.assertFalse(out["polygon_geometry_downloaded"])
        self.assertFalse(out["untouched_predictive_confirmation"])
        self.assertFalse(out["feature_counts_are_areas"])
        self.assertEqual(out["layers"]["2022"]["counts_by_code"]["9121"],1)
    def test_unexpected_class_stops(self):
        def bad(url,params):
            v=fake_fetch(url,params)
            if url.endswith("/query") and params["where"]=="1=1":
                return {"count":9}
            return v
        with self.assertRaisesRegex(M.SourceStop,"OTHER_CLASS_OR_NULL"):
            M.inventory(bad)
    def test_empty_algae_code_allowed_for_descriptive_feasibility(self):
        def noalgae(url,params):
            v=fake_fetch(url,params)
            if url.endswith("/query") and params["where"]=="FLUCCSCODE=9121":
                return {"count":0}
            if url.endswith("/query") and params["where"]=="1=1":
                return {"count":7}
            return v
        out=M.inventory(noalgae)
        self.assertEqual(out["layers"]["2022"]["counts_by_code"]["9121"],0)
    def test_wrong_type_stops(self):
        with self.assertRaisesRegex(M.SourceStop,"FLUCCSCODE_NOT_INTEGER"):
            M.inspect_layer(metadata("2022",{"fields":[
                {"name":"FID","type":"esriFieldTypeOID"},
                {"name":"FLUCCSCODE","type":"esriFieldTypeString"},
                {"name":"FLUCCSDESC","type":"esriFieldTypeString"}]}))
    def test_wrong_crs_stops(self):
        d=metadata("2022")
        d["extent"]["spatialReference"]={"wkid":26917}
        with self.assertRaisesRegex(M.SourceStop,"UNEXPECTED_LAYER_CRS"):
            M.inspect_layer(d)
    def test_service_error_stops(self):
        with self.assertRaisesRegex(M.SourceStop,"ARCGIS_SERVICE_ERROR"):
            M.arcgis_json("fake",{},opener=lambda req,timeout: BadResponse())

class BadResponse:
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return b'{"error":{"code":400,"message":"bad request"}}'

if __name__=="__main__":
    unittest.main()
